"""Tests for the adapter base + registry."""

from __future__ import annotations

import pytest

from cli_api.adapters.base import AdapterInfo, BaseAdapter
from cli_api.adapters.registry import AdapterRegistry, ServiceEntry
from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse


class _EchoAdapter(BaseAdapter):
    """Test double that echoes its input back."""

    @property
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="echo",
            description="Echo adapter for tests",
            supported_actions=["echo", "chat"],
        )

    async def execute(self, request: CAPRequest) -> CAPResponse:
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=" ".join(request.args),
        )


class TestBaseAdapter:
    def test_supports_action_listed(self):
        adapter = _EchoAdapter()
        assert adapter.supports_action("echo")
        assert adapter.supports_action("chat")

    def test_does_not_support_unknown_action(self):
        adapter = _EchoAdapter()
        assert not adapter.supports_action("fly")

    @pytest.mark.anyio
    async def test_health_check_default_true(self):
        adapter = _EchoAdapter()
        assert await adapter.health_check() is True

    @pytest.mark.anyio
    async def test_execute_returns_response(self):
        adapter = _EchoAdapter()
        req = CAPRequest(service="echo", action="echo", args=["hello", "world"])
        resp = await adapter.execute(req)
        assert resp.status == ActionStatus.OK
        assert resp.result == "hello world"


class TestAdapterRegistry:
    def _fresh_registry(self) -> AdapterRegistry:
        """Return a new registry without touching disk."""
        reg = object.__new__(AdapterRegistry)
        reg._adapters = {}
        reg._entries = {}
        return reg

    def test_register_and_get(self):
        reg = self._fresh_registry()
        adapter = _EchoAdapter()
        entry = ServiceEntry(name="echo", adapter_type="custom", description="echo svc")
        reg.register(entry, adapter)
        assert reg.has("echo")
        assert reg.get("echo") is adapter

    def test_list_services(self):
        reg = self._fresh_registry()
        reg.register(ServiceEntry(name="svc1", adapter_type="custom"), _EchoAdapter())
        reg.register(ServiceEntry(name="svc2", adapter_type="custom"), _EchoAdapter())
        names = [e.name for e in reg.list_services()]
        assert "svc1" in names
        assert "svc2" in names

    def test_get_unknown_returns_none(self):
        reg = self._fresh_registry()
        assert reg.get("nonexistent") is None

    def test_has_returns_false_for_unknown(self):
        reg = self._fresh_registry()
        assert not reg.has("ghost")
