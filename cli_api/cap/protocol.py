"""CAP Protocol — CLI-First Universal Protocol core data types and helpers."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CAPVersion(str, Enum):
    """Supported CAP protocol versions."""

    V1 = "1.0"


class ActionStatus(str, Enum):
    """Result status codes for a CAP response."""

    OK = "ok"
    ERROR = "error"
    PENDING = "pending"
    STREAMING = "streaming"


@dataclass
class CAPRequest:
    """A structured CAP request envelope."""

    service: str
    action: str
    args: list[str] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    session_id: str | None = None
    agent_role: str | None = None
    chain_id: str | None = None
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    protocol_version: str = CAPVersion.V1

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": "CAP",
            "version": self.protocol_version,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "service": self.service,
            "action": self.action,
            "args": self.args,
            "kwargs": self.kwargs,
            "session_id": self.session_id,
            "agent_role": self.agent_role,
            "chain_id": self.chain_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CAPRequest:
        return cls(
            service=data["service"],
            action=data["action"],
            args=data.get("args", []),
            kwargs=data.get("kwargs", {}),
            session_id=data.get("session_id"),
            agent_role=data.get("agent_role"),
            chain_id=data.get("chain_id"),
            request_id=data.get("request_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", time.time()),
            protocol_version=data.get("version", CAPVersion.V1),
        )


@dataclass
class CAPResponse:
    """A structured CAP response envelope."""

    request_id: str
    service: str
    action: str
    status: ActionStatus = ActionStatus.OK
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    protocol_version: str = CAPVersion.V1

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol": "CAP",
            "version": self.protocol_version,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "service": self.service,
            "action": self.action,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CAPResponse:
        return cls(
            request_id=data.get("request_id", str(uuid.uuid4())),
            service=data["service"],
            action=data["action"],
            status=ActionStatus(data.get("status", ActionStatus.OK)),
            result=data.get("result"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", time.time()),
            protocol_version=data.get("version", CAPVersion.V1),
        )

    @classmethod
    def error_response(
        cls, request: CAPRequest, error: str, metadata: dict[str, Any] | None = None
    ) -> CAPResponse:
        return cls(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.ERROR,
            error=error,
            metadata=metadata or {},
        )
