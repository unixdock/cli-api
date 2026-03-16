"""Tests for the agent chain executor."""

from __future__ import annotations

import pytest

from cli_api.adapters.base import AdapterInfo, BaseAdapter
from cli_api.adapters.registry import AdapterRegistry, ServiceEntry
from cli_api.broker.broker import CAPBroker
from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse
from cli_api.chain.executor import ChainExecutor, parse_pipeline
from cli_api.usage.tracker import UsageTracker


class _StepAdapter(BaseAdapter):
    """Prefixes its service name to the input for easy chaining verification."""

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def info(self) -> AdapterInfo:
        return AdapterInfo(name=self._name, description="step adapter")

    async def execute(self, request: CAPRequest) -> CAPResponse:
        text = " ".join(request.args)
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=f"[{self._name}] {text}",
        )


class _FailAdapter(BaseAdapter):
    @property
    def info(self) -> AdapterInfo:
        return AdapterInfo(name="fail", description="always fails")

    async def execute(self, request: CAPRequest) -> CAPResponse:
        return CAPResponse.error_response(request, "intentional failure")


def _make_broker(*names: str) -> CAPBroker:
    reg = object.__new__(AdapterRegistry)
    reg._adapters = {}
    reg._entries = {}
    for name in names:
        if name == "fail":
            adapter: BaseAdapter = _FailAdapter()
        else:
            adapter = _StepAdapter(name)
        reg._adapters[name] = adapter
        reg._entries[name] = ServiceEntry(name=name, adapter_type="custom")
    tracker = UsageTracker.__new__(UsageTracker)
    tracker._records = []
    return CAPBroker(registry=reg, tracker=tracker)


class TestParsePipeline:
    def test_simple(self):
        assert parse_pipeline("a -> b -> c") == ["a", "b", "c"]

    def test_single(self):
        assert parse_pipeline("only") == ["only"]

    def test_empty(self):
        assert parse_pipeline("") == []

    def test_extra_spaces(self):
        assert parse_pipeline("  a  ->  b  ") == ["a", "b"]


class TestChainExecutor:
    @pytest.mark.anyio
    async def test_two_step_chain(self):
        broker = _make_broker("step1", "step2")
        executor = ChainExecutor(broker=broker)
        result = await executor.execute(["step1", "step2"], initial_input="hello")
        assert result.success
        assert "[step2]" in result.final_result
        assert "[step1]" in result.final_result

    @pytest.mark.anyio
    async def test_single_step(self):
        broker = _make_broker("only")
        executor = ChainExecutor(broker=broker)
        result = await executor.execute(["only"], initial_input="ping")
        assert result.success
        assert result.final_result == "[only] ping"

    @pytest.mark.anyio
    async def test_step_failure_stops_chain(self):
        broker = _make_broker("step1", "fail", "step3")
        executor = ChainExecutor(broker=broker)
        result = await executor.execute(["step1", "fail", "step3"], initial_input="hi")
        assert not result.success
        assert "fail" in (result.error or "")
        # Only 2 steps attempted (step1 ok, fail errors)
        assert len(result.steps) == 2

    @pytest.mark.anyio
    async def test_monitor_callback_called(self):
        broker = _make_broker("a", "b")
        executor = ChainExecutor(broker=broker)
        events: list[dict] = []

        async def cb(ev: dict) -> None:
            events.append(ev)

        await executor.execute(["a", "b"], initial_input="x", monitor_callback=cb)
        event_types = [e["event"] for e in events]
        assert "chain_step_start" in event_types
        assert "chain_step_done" in event_types

    @pytest.mark.anyio
    async def test_chain_id_propagated(self):
        broker = _make_broker("svc")
        executor = ChainExecutor(broker=broker)
        result = await executor.execute(["svc"], initial_input="test")
        assert result.chain_id
        assert len(result.steps) == 1
