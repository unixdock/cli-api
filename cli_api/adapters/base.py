"""Base adapter interface for CAP-compatible backend agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from cli_api.cap.protocol import CAPRequest, CAPResponse


@dataclass
class AdapterInfo:
    """Static metadata about an adapter."""

    name: str
    description: str
    supported_actions: list[str] = field(default_factory=list)
    requires_api_key: bool = False
    local_only: bool = False
    base_url: str | None = None
    capabilities: dict[str, Any] = field(default_factory=dict)


class BaseAdapter(ABC):
    """Abstract base class every CAP adapter must implement."""

    @property
    @abstractmethod
    def info(self) -> AdapterInfo:
        """Return static metadata for this adapter."""

    @abstractmethod
    async def execute(self, request: CAPRequest) -> CAPResponse:
        """Execute a CAP request and return a structured response."""

    async def health_check(self) -> bool:
        """Return ``True`` if the backend is reachable."""
        return True

    def supports_action(self, action: str) -> bool:
        return not self.info.supported_actions or action in self.info.supported_actions
