"""Tests for jobclaw.models.streaming — SSE streaming layer."""

from __future__ import annotations

import pytest

from jobclaw.models.streaming import (
    StreamContext,
    StreamOptions,
    UnifiedStreamer,
    _OAUTH_BETAS,
    is_oauth_token,
)


def test_is_oauth_token_positive() -> None:
    assert is_oauth_token("sk-ant-oat01-abc123") is True


def test_is_oauth_token_regular_api_key() -> None:
    assert is_oauth_token("sk-ant-api03-something") is False


def test_is_oauth_token_empty() -> None:
    assert is_oauth_token("") is False


def test_oauth_betas_not_empty() -> None:
    assert len(_OAUTH_BETAS) >= 2
    assert any("oauth" in b for b in _OAUTH_BETAS)


def test_stream_context_creation() -> None:
    ctx = StreamContext(user_message="hello", system="be helpful")
    assert ctx.user_message == "hello"
    assert ctx.system == "be helpful"


def test_stream_options_defaults() -> None:
    opts = StreamOptions(access_token="tok", model="claude-sonnet-4-6")
    assert opts.max_tokens == 4096
    assert opts.temperature == 0.0
    assert opts.max_retries == 3


def test_unified_streamer_instantiation() -> None:
    streamer = UnifiedStreamer()
    assert streamer is not None


@pytest.mark.asyncio
async def test_stream_non_retryable_raises() -> None:
    """A non-retryable error should propagate immediately."""
    streamer = UnifiedStreamer()
    ctx = StreamContext(user_message="test")
    opts = StreamOptions(
        access_token="invalid",
        model="claude-sonnet-4-6",
        max_retries=1,
    )

    with pytest.raises(Exception):
        await streamer.stream(ctx, opts)
