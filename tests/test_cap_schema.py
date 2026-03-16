"""Tests for the CAP JSON Schema / capability manifest."""

from __future__ import annotations

from cli_api.cap.schema import build_capability_manifest


class TestCapabilityManifest:
    def test_protocol_field(self):
        m = build_capability_manifest()
        assert m["protocol"] == "CAP"
        assert m["version"] == "1.0"

    def test_schemas_present(self):
        m = build_capability_manifest()
        assert "schemas" in m
        assert "request" in m["schemas"]
        assert "response" in m["schemas"]

    def test_request_schema_required_fields(self):
        schema = build_capability_manifest()["schemas"]["request"]
        assert "service" in schema["required"]
        assert "action" in schema["required"]

    def test_common_flags(self):
        m = build_capability_manifest()
        flags = m["common_flags"]
        assert "--json" in flags
        assert "--session" in flags
        assert "--agent-role" in flags
        assert "--chain" in flags
        assert "--monitor" in flags

    def test_built_in_actions(self):
        m = build_capability_manifest()
        names = [a["name"] for a in m["built_in_actions"]]
        assert "chain" in names
        assert "register" in names
        assert "usage" in names
        assert "repl" in names
        assert "bridge" in names

    def test_supported_adapters(self):
        m = build_capability_manifest()
        assert "openai" in m["supported_adapters"]
        assert "ollama" in m["supported_adapters"]

    def test_supported_bridges(self):
        m = build_capability_manifest()
        assert "mcp" in m["supported_bridges"]
        assert "a2a" in m["supported_bridges"]
        assert "acp" in m["supported_bridges"]

    def test_service_specific_manifest(self):
        m = build_capability_manifest(service="openai")
        assert m.get("service") == "openai"

    def test_extra_actions_merged(self):
        extra = [{"name": "custom-action", "description": "test"}]
        m = build_capability_manifest(extra_actions=extra)
        names = [a["name"] for a in m["built_in_actions"]]
        assert "custom-action" in names
