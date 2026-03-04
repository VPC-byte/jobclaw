"""Extract Claude OAuth token from the locally installed Claude Code CLI."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

_DEFAULT_CREDENTIALS_PATH = Path.home() / ".claude" / ".credentials.json"


class ClaudeToken(BaseModel):
    """Parsed Claude OAuth credentials."""

    access_token: str
    refresh_token: str
    expires_at: int
    scopes: list[str]
    subscription_type: str | None = None
    rate_limit_tier: str | None = None


def get_claude_token(
    credentials_path: Path | None = None,
) -> ClaudeToken:
    """Read *~/.claude/.credentials.json* and return a :class:`ClaudeToken`.

    Parameters
    ----------
    credentials_path:
        Override path for testing / non-default installs.

    Raises
    ------
    FileNotFoundError
        Credentials file does not exist.
    ValueError
        File exists but has unexpected structure.
    """
    path = credentials_path or _DEFAULT_CREDENTIALS_PATH

    if not path.exists():
        raise FileNotFoundError(f"Claude credentials file not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))

    oauth = raw.get("claudeAiOauth")
    if not isinstance(oauth, dict):
        raise ValueError(
            f"Expected 'claudeAiOauth' object in {path}, got {type(oauth).__name__}"
        )

    access_token = oauth.get("accessToken")
    if not access_token:
        raise ValueError("Missing 'accessToken' in claudeAiOauth")

    return ClaudeToken(
        access_token=access_token,
        refresh_token=oauth.get("refreshToken", ""),
        expires_at=int(oauth.get("expiresAt", 0)),
        scopes=oauth.get("scopes", []),
        subscription_type=oauth.get("subscriptionType"),
        rate_limit_tier=oauth.get("rateLimitTier"),
    )
