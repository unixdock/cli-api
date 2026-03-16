"""CAP Broker — intelligent routing + execution engine."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from cli_api.adapters.registry import AdapterRegistry, get_registry
from cli_api.cap.protocol import CAPRequest, CAPResponse
from cli_api.usage.tracker import UsageTracker, get_tracker


@dataclass
class RoutingHint:
    """Hints that influence the broker routing decision."""

    prefer_local: bool = False
    max_latency_ms: int | None = None
    max_cost_units: float | None = None
    require_capabilities: list[str] = field(default_factory=list)


class CAPBroker:
    """Routes CAPRequests to the appropriate adapter, tracks usage, emits events."""

    def __init__(
        self,
        registry: AdapterRegistry | None = None,
        tracker: UsageTracker | None = None,
    ) -> None:
        self._registry = registry or get_registry()
        self._tracker = tracker or get_tracker()

    async def dispatch(
        self,
        request: CAPRequest,
        hint: RoutingHint | None = None,
    ) -> CAPResponse:
        """Resolve the correct adapter and execute the request."""
        hint = hint or RoutingHint()

        # Prefer local adapters when requested
        service = request.service
        if hint.prefer_local:
            service = self._resolve_local(service) or service

        adapter = self._registry.get(service)
        if adapter is None:
            return CAPResponse.error_response(
                request,
                f"Unknown service '{service}'. Use 'cli-api list' to see available services.",
            )

        if not adapter.supports_action(request.action):
            return CAPResponse.error_response(
                request,
                f"Service '{service}' does not support action '{request.action}'.",
            )

        t0 = time.monotonic()
        response = await adapter.execute(request)
        latency_ms = int((time.monotonic() - t0) * 1000)
        response.metadata.setdefault("latency_ms", latency_ms)

        # Track usage
        usage = response.metadata.get("usage", {})
        self._tracker.record(
            service=service,
            action=request.action,
            tokens_in=usage.get("prompt_tokens", 0),
            tokens_out=usage.get("completion_tokens", 0),
            latency_ms=latency_ms,
            status=response.status.value,
        )

        return response

    def _resolve_local(self, service: str) -> str | None:
        """Return a local alternative for the requested service, if available."""
        local_services = [
            e.name
            for e in self._registry.list_services()
            if e.local_only
        ]
        if service in local_services:
            return service
        if local_services:
            return local_services[0]
        return None

    async def health_check_all(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for entry in self._registry.list_services():
            adapter = self._registry.get(entry.name)
            if adapter:
                results[entry.name] = await adapter.health_check()
        return results


# Singleton broker
_broker: CAPBroker | None = None


def get_broker() -> CAPBroker:
    global _broker
    if _broker is None:
        _broker = CAPBroker()
    return _broker
