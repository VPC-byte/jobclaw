"""Async Claude wrapper built on the unified streaming layer."""

from __future__ import annotations

from jobclaw.auth import ClaudeToken, get_claude_token
from jobclaw.models.streaming import (
    StreamContext,
    StreamOptions,
    UnifiedStreamer,
)

_DEFAULT_MODEL = "claude-sonnet-4-6"


class ClaudeClient:
    """Thin async wrapper around Anthropic Messages streaming API.

    Supports both OAuth tokens (from Claude Code CLI) and regular API keys.
    """

    def __init__(
        self,
        token: ClaudeToken | None = None,
        *,
        api_key: str | None = None,
        model: str = _DEFAULT_MODEL,
        timeout: float = 120.0,
        streamer: UnifiedStreamer | None = None,
    ) -> None:
        if token is not None:
            self._access_token = token.access_token
        elif api_key is not None:
            self._access_token = api_key
        else:
            # Auto-detect: try OAuth credentials first
            self._access_token = get_claude_token().access_token

        self.model = model
        self.timeout = timeout
        self.streamer = streamer or UnifiedStreamer()

    async def chat(
        self,
        user_message: str,
        *,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str:
        """Send a message to Claude and return the full response text."""
        context = StreamContext(user_message=user_message, system=system)
        options = StreamOptions(
            access_token=self._access_token,
            model=self.model,
            timeout=self.timeout,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return await self.streamer.stream(context, options)
