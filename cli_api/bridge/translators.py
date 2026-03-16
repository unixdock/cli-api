"""Protocol bridges — translate MCP / A2A / ACP payloads into CAP requests."""

from __future__ import annotations

import json
from typing import Any

from cli_api.cap.protocol import CAPRequest


class MCPBridge:
    """Model Context Protocol → CAP translator.

    MCP JSON-RPC shape::

        {"jsonrpc": "2.0", "method": "tool/call", "params": {"name": "...", "arguments": {...}}}
    """

    @staticmethod
    def to_cap(payload: dict[str, Any], service: str = "mcp") -> CAPRequest:
        method: str = payload.get("method", "")
        params: dict[str, Any] = payload.get("params", {})

        # tool/call → <service> <tool-name> with arguments as kwargs
        if method == "tool/call":
            action = params.get("name", "call")
            kwargs = dict(params.get("arguments", {}))
        elif method == "sampling/createMessage":
            action = "chat"
            messages = params.get("messages", [])
            kwargs = {"messages": messages}
        else:
            action = method.replace("/", "-")
            kwargs = dict(params)

        return CAPRequest(service=service, action=action, kwargs=kwargs)

    @staticmethod
    def from_cap_response(response: Any) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": str(response.result or "")}]},
            "id": response.request_id,
        }


class A2ABridge:
    """Google Agent-to-Agent (A2A) → CAP translator.

    A2A task shape::

        {"id": "...", "message": {"role": "user", "parts": [{"text": "..."}]}}
    """

    @staticmethod
    def to_cap(payload: dict[str, Any], service: str = "a2a") -> CAPRequest:
        task_id = payload.get("id", "")
        message = payload.get("message", {})
        parts = message.get("parts", [])
        text = " ".join(p.get("text", "") for p in parts if "text" in p)
        return CAPRequest(
            service=service,
            action="chat",
            args=[text],
            kwargs={"task_id": task_id},
        )

    @staticmethod
    def from_cap_response(response: Any) -> dict[str, Any]:
        return {
            "id": response.request_id,
            "status": {"state": "completed" if response.status.value == "ok" else "failed"},
            "artifacts": [
                {"parts": [{"type": "text", "text": str(response.result or "")}]}
            ],
        }


class ACPBridge:
    """Agent Communication Protocol (ACP) → CAP translator.

    ACP message shape::

        {"agent": "...", "action": "...", "input": {...}}
    """

    @staticmethod
    def to_cap(payload: dict[str, Any]) -> CAPRequest:
        service = payload.get("agent", "acp")
        action = payload.get("action", "chat")
        input_data = payload.get("input", {})
        if isinstance(input_data, str):
            args = [input_data]
            kwargs: dict[str, Any] = {}
        else:
            args = []
            kwargs = dict(input_data)
        return CAPRequest(service=service, action=action, args=args, kwargs=kwargs)

    @staticmethod
    def from_cap_response(response: Any) -> dict[str, Any]:
        return {
            "agent": response.service,
            "action": response.action,
            "status": response.status.value,
            "output": response.result,
        }


def translate_to_cap(protocol: str, payload_str: str, service: str | None = None) -> CAPRequest:
    """Top-level translation entry point used by the CLI bridge command."""
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON payload: {exc}") from exc

    protocol = protocol.lower()
    if protocol == "mcp":
        return MCPBridge.to_cap(payload, service or "mcp")
    if protocol == "a2a":
        return A2ABridge.to_cap(payload, service or "a2a")
    if protocol == "acp":
        return ACPBridge.to_cap(payload)
    raise ValueError(f"Unknown protocol '{protocol}'. Supported: mcp, a2a, acp")
