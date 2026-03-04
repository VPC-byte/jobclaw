"""Tests for core data models."""

import pytest
from pydantic import ValidationError

from jobclaw.models import (
    Application,
    ApplicationStatus,
    Job,
    JobSource,
    Match,
    Profile,
    SalaryRange,
)


class TestSalaryRange:
    def test_valid_range(self) -> None:
        s = SalaryRange(min_annual=300000, max_annual=600000)
        assert s.min_annual == 300000
        assert s.currency == "CNY"

    def test_invalid_range(self) -> None:
        with pytest.raises(ValidationError):
            SalaryRange(min_annual=600000, max_annual=300000)

    def test_none_values(self) -> None:
        s = SalaryRange()
        assert s.min_annual is None
        assert s.max_annual is None


class TestJob:
    def test_create_job(self) -> None:
        job = Job(
            source=JobSource.BOSS,
            title="Python Developer",
            company="Test Corp",
            location="深圳",
            url="https://www.zhipin.com/job/123",
            description="Build cool stuff",
        )
        assert job.source == JobSource.BOSS
        assert job.title == "Python Developer"
        assert job.id  # UUID auto-generated

    def test_job_with_salary(self) -> None:
        job = Job(
            source=JobSource.LINKEDIN,
            title="AI Engineer",
            company="AI Corp",
            location="Remote",
            url="https://linkedin.com/jobs/123",
            description="Work on agents",
            salary=SalaryRange(min_annual=400000, max_annual=800000),
            tags=["Python", "LLM", "Agent"],
        )
        assert job.salary is not None
        assert job.salary.min_annual == 400000
        assert len(job.tags) == 3


class TestProfile:
    def test_create_profile(self) -> None:
        p = Profile(
            name="Joe",
            years_experience=3,
            skills=["Python", "K8s", "LLM"],
        )
        assert p.name == "Joe"
        assert p.remote_ok is True  # default
        assert len(p.skills) == 3


class TestMatch:
    def test_valid_score(self) -> None:
        m = Match(job_id="abc", score=0.85, reasoning=["Good fit"])
        assert m.score == 0.85

    def test_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            Match(job_id="abc", score=1.5)
        with pytest.raises(ValidationError):
            Match(job_id="abc", score=-0.1)


class TestApplication:
    def test_default_status(self) -> None:
        app = Application(job_id="abc", source=JobSource.BOSS)
        assert app.status == ApplicationStatus.DRAFT
