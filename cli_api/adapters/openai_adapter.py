"""OpenAI adapter for the CAP protocol."""

from __future__ import annotations

import os
from typing import Any

import httpx

from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse

from .base import AdapterInfo, BaseAdapter

_OPENAI_BASE = "https://api.openai.com/v1"


class OpenAIAdapter(BaseAdapter):
    """Adapter that wraps the OpenAI Chat Completions API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
        base_url: str = _OPENAI_BASE,
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._model = model
        self._base_url = base_url

    @property
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="openai",
            description="OpenAI Chat Completions (GPT-4o / GPT-4 / GPT-3.5-turbo)",
            supported_actions=["chat", "complete", "embed", "list-models"],
            requires_api_key=True,
            base_url=self._base_url,
            capabilities={"streaming": True, "function_calling": True},
        )

    async def execute(self, request: CAPRequest) -> CAPResponse:
        action = request.action.lower()
        if action in ("chat", "complete"):
            return await self._chat(request)
        if action == "list-models":
            return await self._list_models(request)
        return CAPResponse.error_response(
            request, f"OpenAI adapter does not support action '{action}'."
        )

    async def _chat(self, request: CAPRequest) -> CAPResponse:
        prompt = " ".join(request.args) or request.kwargs.get("prompt", "")
        messages = request.kwargs.get("messages") or [{"role": "user", "content": prompt}]
        if request.agent_role:
            messages = [
                {"role": "system", "content": f"You are a {request.agent_role}."},
                *messages,
            ]
        payload: dict[str, Any] = {
            "model": request.kwargs.get("model", self._model),
            "messages": messages,
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            return CAPResponse.error_response(request, str(exc))
        except httpx.RequestError as exc:
            return CAPResponse.error_response(request, f"Network error: {exc}")

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=content,
            metadata={"usage": usage, "model": data.get("model")},
        )

    async def _list_models(self, request: CAPRequest) -> CAPResponse:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self._base_url}/models",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            return CAPResponse.error_response(request, str(exc))
        models = [m["id"] for m in data.get("data", [])]
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=models,
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(
                    f"{self._base_url}/models",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                )
                return resp.status_code == 200
        except Exception:
            return False
