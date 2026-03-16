"""Anthropic adapter for the CAP protocol."""

from __future__ import annotations

import os
from typing import Any

import httpx

from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse

from .base import AdapterInfo, BaseAdapter

_ANTHROPIC_BASE = "https://api.anthropic.com/v1"
_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


class AnthropicAdapter(BaseAdapter):
    """Adapter that wraps the Anthropic Messages API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
        base_url: str = _ANTHROPIC_BASE,
    ) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._model = model
        self._base_url = base_url

    @property
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="anthropic",
            description="Anthropic Claude (claude-3-5-sonnet / claude-3-opus / haiku)",
            supported_actions=["chat", "complete"],
            requires_api_key=True,
            base_url=self._base_url,
            capabilities={"streaming": True, "vision": True},
        )

    async def execute(self, request: CAPRequest) -> CAPResponse:
        action = request.action.lower()
        if action in ("chat", "complete"):
            return await self._messages(request)
        return CAPResponse.error_response(
            request, f"Anthropic adapter does not support action '{action}'."
        )

    async def _messages(self, request: CAPRequest) -> CAPResponse:
        prompt = " ".join(request.args) or request.kwargs.get("prompt", "")
        messages = request.kwargs.get("messages") or [{"role": "user", "content": prompt}]
        system = None
        if request.agent_role:
            system = f"You are a {request.agent_role}."

        payload: dict[str, Any] = {
            "model": request.kwargs.get("model", self._model),
            "max_tokens": request.kwargs.get("max_tokens", 4096),
            "messages": messages,
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self._base_url}/messages",
                    json=payload,
                    headers={
                        "x-api-key": self._api_key,
                        "anthropic-version": "2023-06-01",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            return CAPResponse.error_response(request, str(exc))
        except httpx.RequestError as exc:
            return CAPResponse.error_response(request, f"Network error: {exc}")

        content = data["content"][0]["text"]
        usage = data.get("usage", {})
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=content,
            metadata={"usage": usage, "model": data.get("model")},
        )
