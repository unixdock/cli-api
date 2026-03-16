"""Tests for the CAP broker routing layer."""

from __future__ import annotations

import pytest

from cli_api.adapters.base import AdapterInfo, BaseAdapter
from cli_api.adapters.registry import AdapterRegistry, ServiceEntry
from cli_api.broker.broker import CAPBroker, RoutingHint
from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse
from cli_api.usage.tracker import UsageTracker


class _DummyAdapter(BaseAdapter):
    def __init__(self, name: str, local: bool = False) -> None:
        self._name = name
        self._local = local

    @property
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name=self._name,
            description="dummy",
            supported_actions=["chat"],
            local_only=self._local,
        )

    async def execute(self, request: CAPRequest) -> CAPResponse:
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=f"reply from {self._name}",
            metadata={"usage": {"prompt_tokens": 5, "completion_tokens": 10}},
        )


def _make_broker(adapters: dict) -> CAPBroker:
    reg = object.__new__(AdapterRegistry)
    reg._adapters = {}
    reg._entries = {}
    for name, adapter in adapters.items():
        reg._adapters[name] = adapter
        local = getattr(adapter, "_local", False)
        reg._entries[name] = ServiceEntry(name=name, adapter_type="custom", local_only=local)
    tracker = UsageTracker.__new__(UsageTracker)
    tracker._records = []
    return CAPBroker(registry=reg, tracker=tracker)


class TestCAPBroker:
    @pytest.mark.anyio
    async def test_dispatch_ok(self):
        broker = _make_broker({"openai": _DummyAdapter("openai")})
        req = CAPRequest(service="openai", action="chat", args=["hi"])
        resp = await broker.dispatch(req)
        assert resp.status == ActionStatus.OK
        assert "openai" in resp.result

    @pytest.mark.anyio
    async def test_unknown_service_returns_error(self):
        broker = _make_broker({})
        req = CAPRequest(service="ghost", action="chat")
        resp = await broker.dispatch(req)
        assert resp.status == ActionStatus.ERROR
        assert "ghost" in (resp.error or "")

    @pytest.mark.anyio
    async def test_unsupported_action_returns_error(self):
        class _LimitedAdapter(_DummyAdapter):
            @property
            def info(self) -> AdapterInfo:
                return AdapterInfo(
                    name="limited", description="limited", supported_actions=["chat"]
                )

        broker = _make_broker({"limited": _LimitedAdapter("limited")})
        req = CAPRequest(service="limited", action="fly")
        resp = await broker.dispatch(req)
        assert resp.status == ActionStatus.ERROR

    @pytest.mark.anyio
    async def test_latency_recorded_in_metadata(self):
        broker = _make_broker({"svc": _DummyAdapter("svc")})
        req = CAPRequest(service="svc", action="chat")
        resp = await broker.dispatch(req)
        assert "latency_ms" in resp.metadata
        assert resp.metadata["latency_ms"] >= 0

    @pytest.mark.anyio
    async def test_usage_tracked(self):
        broker = _make_broker({"svc": _DummyAdapter("svc")})
        req = CAPRequest(service="svc", action="chat")
        await broker.dispatch(req)
        assert len(broker._tracker._records) == 1
        rec = broker._tracker._records[0]
        assert rec.service == "svc"
        assert rec.tokens_in == 5
        assert rec.tokens_out == 10

    @pytest.mark.anyio
    async def test_prefer_local_routing(self):
        broker = _make_broker({
            "cloud": _DummyAdapter("cloud", local=False),
            "local": _DummyAdapter("local", local=True),
        })
        req = CAPRequest(service="cloud", action="chat")
        resp = await broker.dispatch(req, hint=RoutingHint(prefer_local=True))
        # Should be routed to the local adapter
        assert resp.status == ActionStatus.OK
        assert "local" in resp.result

    @pytest.mark.anyio
    async def test_health_check_all(self):
        broker = _make_broker({"a": _DummyAdapter("a"), "b": _DummyAdapter("b")})
        health = await broker.health_check_all()
        assert health["a"] is True
        assert health["b"] is True
