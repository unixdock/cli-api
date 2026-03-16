"""Ollama / LM Studio adapter — local-first, zero-config."""

from __future__ import annotations

from typing import Any

import httpx

from cli_api.cap.protocol import ActionStatus, CAPRequest, CAPResponse

from .base import AdapterInfo, BaseAdapter

_OLLAMA_BASE = "http://localhost:11434"
_LM_STUDIO_BASE = "http://localhost:1234/v1"


class OllamaAdapter(BaseAdapter):
    """Adapter for local Ollama instances (OpenAI-compatible API)."""

    def __init__(
        self,
        base_url: str = _OLLAMA_BASE,
        model: str = "llama3",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    @property
    def info(self) -> AdapterInfo:
        return AdapterInfo(
            name="ollama",
            description="Local Ollama LLM server (llama3, mistral, gemma, …)",
            supported_actions=["chat", "complete", "list-models"],
            requires_api_key=False,
            local_only=True,
            base_url=self._base_url,
            capabilities={"streaming": True, "local": True},
        )

    async def execute(self, request: CAPRequest) -> CAPResponse:
        action = request.action.lower()
        if action in ("chat", "complete"):
            return await self._chat(request)
        if action == "list-models":
            return await self._list_models(request)
        return CAPResponse.error_response(
            request, f"Ollama adapter does not support action '{action}'."
        )

    async def _chat(self, request: CAPRequest) -> CAPResponse:
        prompt = " ".join(request.args) or request.kwargs.get("prompt", "")
        messages: list[dict[str, Any]] = request.kwargs.get("messages") or []
        if request.agent_role and not any(m["role"] == "system" for m in messages):
            messages = [{"role": "system", "content": f"You are a {request.agent_role}."}] + messages
        if not messages:
            messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": request.kwargs.get("model", self._model),
            "messages": messages,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self._base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            return CAPResponse.error_response(request, str(exc))
        except httpx.RequestError as exc:
            return CAPResponse.error_response(request, f"Cannot reach Ollama at {self._base_url}: {exc}")

        content = data.get("message", {}).get("content", "")
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=content,
            metadata={"model": data.get("model"), "done": data.get("done")},
        )

    async def _list_models(self, request: CAPRequest) -> CAPResponse:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            return CAPResponse.error_response(request, str(exc))
        models = [m["name"] for m in data.get("models", [])]
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=models,
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                resp = await client.get(f"{self._base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


class LMStudioAdapter(OllamaAdapter):
    """Adapter for LM Studio (OpenAI-compatible local server)."""

    def __init__(
        self,
        base_url: str = _LM_STUDIO_BASE,
        model: str = "local-model",
    ) -> None:
        super().__init__(base_url=base_url, model=model)

    @property
    def info(self) -> AdapterInfo:
        base = super().info
        return AdapterInfo(
            name="lm-studio",
            description="Local LM Studio server (OpenAI-compatible)",
            supported_actions=base.supported_actions,
            requires_api_key=False,
            local_only=True,
            base_url=self._base_url,
            capabilities=base.capabilities,
        )

    async def _chat(self, request: CAPRequest) -> CAPResponse:
        """LM Studio uses an OpenAI-compatible endpoint."""
        prompt = " ".join(request.args) or request.kwargs.get("prompt", "")
        messages: list[dict[str, Any]] = request.kwargs.get("messages") or [
            {"role": "user", "content": prompt}
        ]
        if request.agent_role:
            messages = [
                {"role": "system", "content": f"You are a {request.agent_role}."},
                *messages,
            ]
        payload = {
            "model": request.kwargs.get("model", self._model),
            "messages": messages,
        }
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self._base_url}/chat/completions", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.RequestError as exc:
            return CAPResponse.error_response(
                request, f"Cannot reach LM Studio at {self._base_url}: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            return CAPResponse.error_response(request, str(exc))
        content = data["choices"][0]["message"]["content"]
        return CAPResponse(
            request_id=request.request_id,
            service=request.service,
            action=request.action,
            status=ActionStatus.OK,
            result=content,
            metadata={"model": data.get("model")},
        )
