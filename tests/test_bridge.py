"""Tests for the protocol bridge translators (MCP / A2A / ACP)."""

from __future__ import annotations

import json

import pytest

from cli_api.bridge.translators import (
    A2ABridge,
    ACPBridge,
    MCPBridge,
    translate_to_cap,
)


class TestMCPBridge:
    def test_tool_call(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "tool/call",
            "params": {"name": "search", "arguments": {"query": "AI agents"}},
        }
        req = MCPBridge.to_cap(payload)
        assert req.service == "mcp"
        assert req.action == "search"
        assert req.kwargs["query"] == "AI agents"

    def test_sampling_create_message(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "sampling/createMessage",
            "params": {"messages": [{"role": "user", "content": "hello"}]},
        }
        req = MCPBridge.to_cap(payload)
        assert req.action == "chat"
        assert req.kwargs["messages"][0]["role"] == "user"

    def test_from_cap_response(self):
        from cli_api.cap.protocol import ActionStatus, CAPResponse

        resp = CAPResponse(
            request_id="r1", service="mcp", action="search",
            status=ActionStatus.OK, result="found it",
        )
        out = MCPBridge.from_cap_response(resp)
        assert out["jsonrpc"] == "2.0"
        assert out["result"]["content"][0]["text"] == "found it"

    def test_custom_service(self):
        payload = {"method": "tool/call", "params": {"name": "x"}}
        req = MCPBridge.to_cap(payload, service="my-mcp")
        assert req.service == "my-mcp"


class TestA2ABridge:
    def test_basic(self):
        payload = {
            "id": "task-1",
            "message": {
                "role": "user",
                "parts": [{"text": "research quantum computing"}],
            },
        }
        req = A2ABridge.to_cap(payload)
        assert req.action == "chat"
        assert "quantum computing" in req.args[0]
        assert req.kwargs["task_id"] == "task-1"

    def test_from_cap_response(self):
        from cli_api.cap.protocol import ActionStatus, CAPResponse

        resp = CAPResponse(
            request_id="r1", service="a2a", action="chat",
            status=ActionStatus.OK, result="done",
        )
        out = A2ABridge.from_cap_response(resp)
        assert out["status"]["state"] == "completed"
        assert out["artifacts"][0]["parts"][0]["text"] == "done"


class TestACPBridge:
    def test_string_input(self):
        payload = {"agent": "claude", "action": "write", "input": "write a poem"}
        req = ACPBridge.to_cap(payload)
        assert req.service == "claude"
        assert req.action == "write"
        assert "write a poem" in req.args

    def test_dict_input(self):
        payload = {"agent": "gpt", "action": "chat", "input": {"prompt": "hello"}}
        req = ACPBridge.to_cap(payload)
        assert req.kwargs["prompt"] == "hello"

    def test_from_cap_response(self):
        from cli_api.cap.protocol import ActionStatus, CAPResponse

        resp = CAPResponse(
            request_id="r1", service="claude", action="write",
            status=ActionStatus.OK, result="poem here",
        )
        out = ACPBridge.from_cap_response(resp)
        assert out["agent"] == "claude"
        assert out["output"] == "poem here"


class TestTranslateToCap:
    def test_mcp(self):
        payload = json.dumps({"method": "tool/call", "params": {"name": "fn"}})
        req = translate_to_cap("mcp", payload)
        assert req.action == "fn"

    def test_a2a(self):
        payload = json.dumps({
            "id": "t1",
            "message": {"parts": [{"text": "hi"}]},
        })
        req = translate_to_cap("a2a", payload)
        assert req.action == "chat"

    def test_acp(self):
        payload = json.dumps({"agent": "bot", "action": "chat", "input": "go"})
        req = translate_to_cap("acp", payload)
        assert req.service == "bot"

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            translate_to_cap("mcp", "not-json")

    def test_unknown_protocol_raises(self):
        with pytest.raises(ValueError, match="Unknown protocol"):
            translate_to_cap("xyz", "{}")
