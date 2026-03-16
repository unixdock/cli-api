"""CAP Schema — JSON Schema + capability manifest generation for `--help`."""

from __future__ import annotations

from typing import Any

from .protocol import CAPRequest, CAPResponse


def _json_schema_for_type(python_type: str) -> dict[str, Any]:
    """Map simple Python type names to JSON Schema primitives."""
    mapping = {
        "str": {"type": "string"},
        "int": {"type": "integer"},
        "float": {"type": "number"},
        "bool": {"type": "boolean"},
        "list": {"type": "array"},
        "dict": {"type": "object"},
        "Any": {},
    }
    return mapping.get(python_type, {"type": "string"})


# ------------------------------------------------------------------
# Static capability manifest used at `--help` time.
# Adapters can enrich this by contributing their own capabilities.
# ------------------------------------------------------------------

CAP_COMMON_FLAGS: dict[str, dict[str, Any]] = {
    "--json": {
        "type": "boolean",
        "description": "Return structured JSON output instead of plain text.",
        "default": False,
    },
    "--session": {
        "type": "string",
        "description": "Session ID for stateful conversations (auto-generated if omitted).",
        "default": None,
    },
    "--agent-role": {
        "type": "string",
        "description": "Semantic role hint for the target agent (e.g. researcher, writer, reviewer).",
        "default": None,
    },
    "--chain": {
        "type": "string",
        "description": "Execute a pipeline: 'svc1 -> svc2 -> svc3'.",
        "default": None,
    },
    "--monitor": {
        "type": "boolean",
        "description": "Stream real-time monitoring events to stdout.",
        "default": False,
    },
}


def build_capability_manifest(
    service: str | None = None,
    extra_actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a JSON-Schema-compatible capability manifest.

    When *service* is ``None`` the global manifest is returned, otherwise the
    service-specific manifest is merged in.
    """
    request_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CAPRequest",
        "description": "A CLI-First Universal Protocol (CAP) request envelope.",
        "type": "object",
        "properties": {
            "protocol": {"type": "string", "const": "CAP"},
            "version": {"type": "string", "enum": ["1.0"]},
            "request_id": {"type": "string", "format": "uuid"},
            "timestamp": {"type": "number"},
            "service": {"type": "string"},
            "action": {"type": "string"},
            "args": {"type": "array", "items": {"type": "string"}},
            "kwargs": {"type": "object"},
            "session_id": {"type": ["string", "null"]},
            "agent_role": {"type": ["string", "null"]},
            "chain_id": {"type": ["string", "null"]},
        },
        "required": ["service", "action"],
    }

    response_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CAPResponse",
        "description": "A CLI-First Universal Protocol (CAP) response envelope.",
        "type": "object",
        "properties": {
            "protocol": {"type": "string", "const": "CAP"},
            "version": {"type": "string", "enum": ["1.0"]},
            "request_id": {"type": "string", "format": "uuid"},
            "timestamp": {"type": "number"},
            "service": {"type": "string"},
            "action": {"type": "string"},
            "status": {"type": "string", "enum": ["ok", "error", "pending", "streaming"]},
            "result": {},
            "error": {"type": ["string", "null"]},
            "metadata": {"type": "object"},
        },
        "required": ["request_id", "service", "action", "status"],
    }

    built_in_actions = [
        {
            "name": "register",
            "description": "Register a new agent service in the local registry.",
            "args": [{"name": "service_name", "type": "string", "required": True}],
        },
        {
            "name": "list",
            "description": "List all registered agent services.",
            "args": [],
        },
        {
            "name": "chain",
            "description": "Execute an ordered pipeline of agent services.",
            "args": [
                {
                    "name": "pipeline",
                    "type": "string",
                    "description": "Pipeline spec: 'svc1 -> svc2 -> svc3'",
                    "required": True,
                }
            ],
        },
        {
            "name": "usage",
            "description": "Display real-time cross-service token/credit consumption.",
            "args": [],
        },
        {
            "name": "repl",
            "description": "Launch interactive REPL with undo/redo support.",
            "args": [{"name": "service", "type": "string", "required": False}],
        },
        {
            "name": "monitor",
            "description": "Stream live monitoring events from all active agents.",
            "args": [],
        },
        {
            "name": "bridge",
            "description": "Translate an external protocol request (MCP/A2A/ACP) into CAP.",
            "args": [
                {
                    "name": "protocol",
                    "type": "string",
                    "enum": ["mcp", "a2a", "acp"],
                    "required": True,
                },
                {"name": "payload", "type": "string", "required": True},
            ],
        },
    ]

    manifest: dict[str, Any] = {
        "protocol": "CAP",
        "version": "1.0",
        "description": (
            "CLI-First Universal Protocol — one command to unify AI agents.\n"
            "Usage: cli-api <service> <action> [args] [--json] [--session ID] "
            "[--agent-role ROLE] [--chain PIPELINE] [--monitor]"
        ),
        "common_flags": CAP_COMMON_FLAGS,
        "built_in_actions": built_in_actions + (extra_actions or []),
        "schemas": {
            "request": request_schema,
            "response": response_schema,
        },
        "supported_adapters": [
            "openai",
            "anthropic",
            "ollama",
            "lm-studio",
            "custom",
        ],
        "supported_bridges": ["mcp", "a2a", "acp"],
    }

    if service:
        manifest["service"] = service

    return manifest


def dataclass_to_jsonschema(cls: type) -> dict[str, Any]:
    """Minimal JSON Schema derivation for our protocol dataclasses."""
    if cls is CAPRequest:
        return build_capability_manifest()["schemas"]["request"]
    if cls is CAPResponse:
        return build_capability_manifest()["schemas"]["response"]
    return {}
