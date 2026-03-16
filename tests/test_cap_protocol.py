"""Tests for the CAP protocol data types."""

from __future__ import annotations

import json

from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse


class TestCAPRequest:
    def test_defaults(self):
        req = CAPRequest(service="openai", action="chat")
        assert req.service == "openai"
        assert req.action == "chat"
        assert req.args == []
        assert req.kwargs == {}
        assert req.session_id is None
        assert req.agent_role is None
        assert req.chain_id is None
        assert req.protocol_version == "1.0"

    def test_to_dict(self):
        req = CAPRequest(service="ollama", action="chat", args=["hello"])
        d = req.to_dict()
        assert d["protocol"] == "CAP"
        assert d["version"] == "1.0"
        assert d["service"] == "ollama"
        assert d["action"] == "chat"
        assert d["args"] == ["hello"]

    def test_to_json_roundtrip(self):
        req = CAPRequest(service="openai", action="chat", args=["test"], agent_role="writer")
        raw = req.to_json()
        data = json.loads(raw)
        assert data["service"] == "openai"
        assert data["agent_role"] == "writer"

    def test_from_dict(self):
        d = {
            "service": "anthropic",
            "action": "complete",
            "args": ["prompt"],
            "kwargs": {"model": "claude-3"},
            "session_id": "sess-1",
        }
        req = CAPRequest.from_dict(d)
        assert req.service == "anthropic"
        assert req.action == "complete"
        assert req.session_id == "sess-1"
        assert req.kwargs == {"model": "claude-3"}


class TestCAPResponse:
    def test_ok_response(self):
        req = CAPRequest(service="openai", action="chat")
        resp = CAPResponse(
            request_id=req.request_id,
            service=req.service,
            action=req.action,
            status=ActionStatus.OK,
            result="Hello!",
        )
        assert resp.status == ActionStatus.OK
        assert resp.result == "Hello!"
        assert resp.error is None

    def test_error_response(self):
        req = CAPRequest(service="openai", action="chat")
        resp = CAPResponse.error_response(req, "Connection refused")
        assert resp.status == ActionStatus.ERROR
        assert resp.error == "Connection refused"
        assert resp.result is None

    def test_to_dict(self):
        req = CAPRequest(service="openai", action="chat")
        resp = CAPResponse(
            request_id=req.request_id,
            service="openai",
            action="chat",
            status=ActionStatus.OK,
            result="ok",
        )
        d = resp.to_dict()
        assert d["protocol"] == "CAP"
        assert d["status"] == "ok"

    def test_to_json_roundtrip(self):
        req = CAPRequest(service="openai", action="chat")
        resp = CAPResponse(
            request_id=req.request_id,
            service="openai",
            action="chat",
            result={"answer": 42},
        )
        raw = resp.to_json()
        data = json.loads(raw)
        assert data["result"] == {"answer": 42}

    def test_from_dict(self):
        d = {
            "request_id": "req-1",
            "service": "openai",
            "action": "chat",
            "status": "ok",
            "result": "hello",
        }
        resp = CAPResponse.from_dict(d)
        assert resp.status == ActionStatus.OK
        assert resp.result == "hello"
