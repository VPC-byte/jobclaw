"""LLM abstraction layer + re-exported domain models for backward compat."""

# --- LLM layer -----------------------------------------------------------
from jobclaw.models.streaming import (
    StreamContext,
    StreamOptions,
    UnifiedStreamer,
    is_oauth_token,
)
from jobclaw.models.claude_api import ClaudeClient

# --- Domain models (moved to jobclaw.domain, re-exported here) -----------
from jobclaw.domain import (
    Application,
    ApplicationStatus,
    Job,
    JobSource,
    Match,
    Profile,
    SalaryRange,
)

__all__ = [
    # LLM
    "ClaudeClient",
    "StreamContext",
    "StreamOptions",
    "UnifiedStreamer",
    "is_oauth_token",
    # Domain
    "Application",
    "ApplicationStatus",
    "Job",
    "JobSource",
    "Match",
    "Profile",
    "SalaryRange",
]
