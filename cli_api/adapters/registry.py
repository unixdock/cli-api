"""CAP adapter registry — service discovery and registration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from cli_api.adapters.base import BaseAdapter

_REGISTRY_PATH = Path.home() / ".cli-api" / "registry.json"


@dataclass
class ServiceEntry:
    """A record in the CAP service registry."""

    name: str
    adapter_type: str  # "openai" | "anthropic" | "ollama" | "lm-studio" | "custom"
    description: str = ""
    base_url: str | None = None
    model: str | None = None
    api_key_env: str | None = None  # env-var name (never stored directly)
    capabilities: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    local_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AdapterRegistry:
    """In-process registry mapping service names → adapter instances."""

    def __init__(self) -> None:
        self._adapters: dict[str, BaseAdapter] = {}
        self._entries: dict[str, ServiceEntry] = {}
        self._load_persistent()
        self._register_defaults()

    # ------------------------------------------------------------------
    # Default built-in adapters
    # ------------------------------------------------------------------

    def _register_defaults(self) -> None:
        from cli_api.adapters.anthropic_adapter import AnthropicAdapter
        from cli_api.adapters.ollama_adapter import LMStudioAdapter, OllamaAdapter
        from cli_api.adapters.openai_adapter import OpenAIAdapter

        defaults: list[tuple[str, BaseAdapter]] = [
            ("openai", OpenAIAdapter()),
            ("anthropic", AnthropicAdapter()),
            ("ollama", OllamaAdapter()),
            ("lm-studio", LMStudioAdapter()),
        ]
        for name, adapter in defaults:
            if name not in self._adapters:
                self._adapters[name] = adapter
                if name not in self._entries:
                    info = adapter.info
                    self._entries[name] = ServiceEntry(
                        name=name,
                        adapter_type=name,
                        description=info.description,
                        base_url=info.base_url,
                        capabilities=info.capabilities,
                        local_only=info.local_only,
                    )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, entry: ServiceEntry, adapter: BaseAdapter | None = None) -> None:
        """Register a service. If *adapter* is None a default adapter is built."""
        if adapter is None:
            adapter = self._build_adapter(entry)
        self._adapters[entry.name] = adapter
        self._entries[entry.name] = entry
        self._save_persistent()

    def get(self, name: str) -> BaseAdapter | None:
        return self._adapters.get(name)

    def list_services(self) -> list[ServiceEntry]:
        return list(self._entries.values())

    def has(self, name: str) -> bool:
        return name in self._adapters

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load_persistent(self) -> None:
        if not _REGISTRY_PATH.exists():
            return
        try:
            raw = json.loads(_REGISTRY_PATH.read_text())
            for item in raw:
                entry = ServiceEntry(**item)
                self._entries[entry.name] = entry
                # Adapters are re-built lazily when first used
        except Exception:
            pass

    def _save_persistent(self) -> None:
        _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = [e.to_dict() for e in self._entries.values()]
        _REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def _build_adapter(self, entry: ServiceEntry) -> BaseAdapter:
        """Construct a concrete adapter from a ServiceEntry."""
        import os

        from cli_api.adapters.anthropic_adapter import AnthropicAdapter
        from cli_api.adapters.ollama_adapter import LMStudioAdapter, OllamaAdapter
        from cli_api.adapters.openai_adapter import OpenAIAdapter

        api_key = os.environ.get(entry.api_key_env or "", None)
        kwargs: dict[str, Any] = {}
        if entry.base_url:
            kwargs["base_url"] = entry.base_url
        if entry.model:
            kwargs["model"] = entry.model
        if api_key:
            kwargs["api_key"] = api_key

        adapter_map = {
            "openai": OpenAIAdapter,
            "anthropic": AnthropicAdapter,
            "ollama": OllamaAdapter,
            "lm-studio": LMStudioAdapter,
        }
        cls = adapter_map.get(entry.adapter_type, OllamaAdapter)
        return cls(**kwargs)


# Singleton registry instance
_registry: AdapterRegistry | None = None


def get_registry() -> AdapterRegistry:
    global _registry
    if _registry is None:
        _registry = AdapterRegistry()
    return _registry
