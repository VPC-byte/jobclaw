"""Core domain models used across scraping, matching, and applying."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl, model_validator


class JobSource(str, Enum):
    """Supported job sources."""

    BOSS = "boss"
    LINKEDIN = "linkedin"
    LAGOU = "lagou"


class ApplicationStatus(str, Enum):
    """Application lifecycle states."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"
    FAILED = "failed"
    CAPTCHA_BLOCKED = "captcha_blocked"


class SalaryRange(BaseModel):
    """Represents a salary range with currency."""

    min_annual: int | None = Field(default=None, ge=0)
    max_annual: int | None = Field(default=None, ge=0)
    currency: str = Field(default="CNY", min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_range(self) -> "SalaryRange":
        """Ensure max salary is not lower than min salary."""

        if self.min_annual is not None and self.max_annual is not None:
            if self.max_annual < self.min_annual:
                raise ValueError("max_annual must be greater than or equal to min_annual")
        return self


class Job(BaseModel):
    """A normalized job listing from any source platform."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    source: JobSource
    title: str
    company: str
    location: str
    url: HttpUrl
    description: str
    salary: SalaryRange | None = None
    tags: list[str] = Field(default_factory=list)
    posted_at: datetime | None = None
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class Profile(BaseModel):
    """Candidate profile loaded from local config files."""

    name: str
    email: str | None = None
    years_experience: float = Field(default=0.0, ge=0.0)
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    desired_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    salary_expectation: SalaryRange | None = None
    remote_ok: bool = True
    links: dict[str, HttpUrl] = Field(default_factory=dict)


class Match(BaseModel):
    """Match result between a profile and a job listing."""

    job_id: str
    score: float = Field(ge=0.0, le=1.0)
    reasoning: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Application(BaseModel):
    """Tracks application submission and follow-up details."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    job_id: str
    source: JobSource
    status: ApplicationStatus = ApplicationStatus.DRAFT
    message: str = ""
    applied_at: datetime | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extra: dict[str, Any] = Field(default_factory=dict)
    # Common extra keys:
    #   "reason": str — failure/skip reason (e.g. "captcha", "already_applied",
    #                    "daily_limit", "button_not_found", "inactive_hr")
    #   "greeting_sent": str — the actual greeting message sent
    #   "hr_name": str — recruiter name if available
    #   "response_time": float — seconds taken for the apply action
