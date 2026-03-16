"""Agent chain executor — runs `svc1 -> svc2 -> svc3` pipelines."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from cli_api.broker.broker import CAPBroker, get_broker
from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse


def parse_pipeline(spec: str) -> list[str]:
    """Parse 'svc1 -> svc2 -> svc3' into ['svc1', 'svc2', 'svc3']."""
    return [s.strip() for s in spec.split("->") if s.strip()]


@dataclass
class ChainResult:
    """Aggregated output of a multi-stage pipeline."""

    chain_id: str
    pipeline: list[str]
    steps: list[CAPResponse] = field(default_factory=list)
    final_result: Any = None
    success: bool = True
    error: str | None = None


class ChainExecutor:
    """Executes an ordered pipeline of CAP services.

    Each step receives the *result* of the previous step as its prompt/input,
    allowing a researcher → writer → reviewer pattern.
    """

    def __init__(self, broker: CAPBroker | None = None) -> None:
        self._broker = broker or get_broker()

    async def execute(
        self,
        pipeline: list[str],
        initial_input: str,
        action: str = "chat",
        session_id: str | None = None,
        agent_roles: list[str] | None = None,
        extra_kwargs: dict[str, Any] | None = None,
        monitor_callback: Any | None = None,
    ) -> ChainResult:
        """Run *pipeline* with *initial_input*, passing each output as the next input."""
        chain_id = str(uuid.uuid4())
        chain_result = ChainResult(chain_id=chain_id, pipeline=pipeline)
        current_input = initial_input

        for idx, service in enumerate(pipeline):
            role = (agent_roles[idx] if agent_roles and idx < len(agent_roles) else None)
            request = CAPRequest(
                service=service,
                action=action,
                args=[current_input],
                kwargs=extra_kwargs or {},
                session_id=session_id,
                agent_role=role,
                chain_id=chain_id,
            )

            if monitor_callback:
                await monitor_callback(
                    {
                        "event": "chain_step_start",
                        "chain_id": chain_id,
                        "step": idx + 1,
                        "total": len(pipeline),
                        "service": service,
                    }
                )

            response = await self._broker.dispatch(request)
            chain_result.steps.append(response)

            if monitor_callback:
                await monitor_callback(
                    {
                        "event": "chain_step_done",
                        "chain_id": chain_id,
                        "step": idx + 1,
                        "service": service,
                        "status": response.status.value,
                    }
                )

            if response.status == ActionStatus.ERROR:
                chain_result.success = False
                chain_result.error = (
                    f"Step {idx + 1} ({service}) failed: {response.error}"
                )
                break

            current_input = str(response.result or "")

        chain_result.final_result = current_input if chain_result.success else None
        return chain_result
