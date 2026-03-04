"""Tests for jobclaw.auth.claude_auth — Claude OAuth credential loading."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jobclaw.auth.claude_auth import ClaudeToken, get_claude_token


_VALID_CREDENTIALS = {
    "claudeAiOauth": {
        "accessToken": "sk-ant-oat01-test-token-abc123",
        "refreshToken": "refresh-xyz",
        "expiresAt": 1999999999,
        "scopes": ["user:inference", "user:profile"],
        "subscriptionType": "pro",
        "rateLimitTier": "tier1",
    }
}


@pytest.fixture()
def creds_file(tmp_path: Path) -> Path:
    """Write valid credentials to a temp file and return the path."""
    path = tmp_path / ".credentials.json"
    path.write_text(json.dumps(_VALID_CREDENTIALS), encoding="utf-8")
    return path


def test_get_claude_token_happy_path(creds_file: Path) -> None:
    token = get_claude_token(creds_file)
    assert isinstance(token, ClaudeToken)
    assert token.access_token == "sk-ant-oat01-test-token-abc123"
    assert token.refresh_token == "refresh-xyz"
    assert token.expires_at == 1999999999
    assert token.subscription_type == "pro"
    assert token.rate_limit_tier == "tier1"
    assert "user:inference" in token.scopes


def test_get_claude_token_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        get_claude_token(tmp_path / "nonexistent.json")


def test_get_claude_token_bad_structure(tmp_path: Path) -> None:
    path = tmp_path / ".credentials.json"
    path.write_text(json.dumps({"something": "else"}), encoding="utf-8")
    with pytest.raises(ValueError, match="claudeAiOauth"):
        get_claude_token(path)


def test_get_claude_token_missing_access_token(tmp_path: Path) -> None:
    data = {"claudeAiOauth": {"refreshToken": "x"}}
    path = tmp_path / ".credentials.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="accessToken"):
        get_claude_token(path)
