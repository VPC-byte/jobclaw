"""Async SSE streaming layer for Anthropic Claude Messages API."""

from __future__ import annotations

import asyncio
import json
import random
from dataclasses import dataclass

import httpx

_API_VERSION = "2023-06-01"
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_OAUTH_BETAS = [
    "claude-code-20250219",
    "oauth-2025-04-20",
    "fine-grained-tool-streaming-2025-05-14",
    "interleaved-thinking-2025-05-14",
]
_CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"


def is_oauth_token(token: str) -> bool:
    """Return whether the Claude token is an OAuth token (vs regular API key)."""
    return "sk-ant-oat" in token


@dataclass(frozen=True)
class StreamContext:
    """What to send to the model."""

    user_message: str
    system: str | None = None


@dataclass(frozen=True)
class StreamOptions:
    """How to call the API."""

    access_token: str
    model: str
    timeout: float = 120.0
    max_retries: int = 3
    base_delay: float = 1.0
    anthropic_version: str = _API_VERSION
    max_tokens: int = 4096
    temperature: float = 0.0


class UnifiedStreamer:
    """Claude Messages SSE streaming client with retry/backoff."""

    async def stream(self, context: StreamContext, options: StreamOptions) -> str:
        """Stream a Claude Messages request and return the full text."""
        backoff = options.base_delay
        last_exc: Exception | None = None

        for attempt in range(1, options.max_retries + 1):
            try:
                return await self._stream_once(context, options)
            except Exception as exc:
                if not self._is_retryable(exc) or attempt >= options.max_retries:
                    raise
                last_exc = exc
                jittered_backoff = backoff * (0.5 + random.random())
                await asyncio.sleep(jittered_backoff)
                backoff *= 2

        if last_exc:  # pragma: no cover
            raise last_exc
        raise RuntimeError("Streaming failed")  # pragma: no cover

    async def _stream_once(
        self, context: StreamContext, options: StreamOptions
    ) -> str:
        headers: dict[str, str] = {
            "content-type": "application/json",
            "accept": "text/event-stream",
        }

        if is_oauth_token(options.access_token):
            # OAuth token — use Bearer auth + beta headers
            headers["Authorization"] = f"Bearer {options.access_token}"
            headers["anthropic-beta"] = ",".join(_OAUTH_BETAS)
        else:
            # Regular API key — use x-api-key header
            headers["x-api-key"] = options.access_token

        headers["anthropic-version"] = options.anthropic_version

        body: dict[str, object] = {
            "model": options.model,
            "max_tokens": options.max_tokens,
            "temperature": options.temperature,
            "stream": True,
            "messages": [{"role": "user", "content": context.user_message}],
        }
        if context.system:
            body["system"] = context.system

        parts: list[str] = []
        async with httpx.AsyncClient(timeout=options.timeout) as client:
            async with client.stream(
                "POST", _CLAUDE_API_URL, headers=headers, json=body
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue

                    event_type = event.get("type")
                    if event_type == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            parts.append(delta.get("text", ""))
                    elif event_type == "error":
                        message = (
                            event.get("error", {}).get("message")
                            or event.get("message")
                            or "unknown error"
                        )
                        raise RuntimeError(f"Claude stream error: {message}")

        return "".join(parts)

    def _is_retryable(self, exc: Exception) -> bool:
        if isinstance(exc, (httpx.TimeoutException, httpx.TransportError)):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code in _RETRYABLE_STATUS_CODES
        return False


__all__ = [
    "StreamContext",
    "StreamOptions",
    "UnifiedStreamer",
    "is_oauth_token",
    "_OAUTH_BETAS",
]
