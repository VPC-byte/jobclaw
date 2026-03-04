"""Tests for BossApplier — mock Playwright-based apply flow."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jobclaw.applier.boss import BossApplier
from jobclaw.applier.history import ApplyHistory
from jobclaw.config import Settings
from jobclaw.models import ApplicationStatus, Job, JobSource, Profile


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        boss_cookie="test-cookie",
        boss_greeting="你好，我对$title职位很感兴趣，希望进一步了解！",
        boss_apply_delay_min=0.5,
        boss_apply_delay_max=1.0,
        boss_daily_limit=100,
        jobclaw_headless=True,
    )


@pytest.fixture()
def profile() -> Profile:
    return Profile(name="Joe", email="joe@test.com", skills=["Python"])


@pytest.fixture()
def job() -> Job:
    return Job(
        id="boss-job-123",
        source=JobSource.BOSS,
        title="大模型工程师",
        company="TestCorp",
        location="深圳",
        url="https://www.zhipin.com/job_detail/abc123.html",
        description="AI/ML role",
    )


@pytest.fixture()
def history(tmp_path: Path) -> ApplyHistory:
    return ApplyHistory(path=tmp_path / "history.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_page(
    *,
    has_start_btn: bool = True,
    has_continue_btn: bool = False,
    has_chat_input: bool = True,
    has_send_btn: bool = True,
    has_captcha: bool = False,
    body_text: str = "",
) -> AsyncMock:
    """Create a mock Page with configurable elements."""
    page = AsyncMock()
    page.goto = AsyncMock()
    page.inner_text = AsyncMock(return_value=body_text)
    page.keyboard = AsyncMock()
    page.keyboard.type = AsyncMock()
    page.keyboard.press = AsyncMock()

    def make_el(visible: bool = True):
        el = AsyncMock()
        el.is_visible = AsyncMock(return_value=visible)
        el.click = AsyncMock()
        el.fill = AsyncMock()
        return el

    async def query_selector(sel: str):
        # Captcha selectors
        if has_captcha and ("captcha" in sel or "verify" in sel):
            return make_el(True)
        # 继续沟通 must match before 立即沟通 — check text precisely
        if "继续沟通" in sel:
            return make_el(True) if has_continue_btn else None
        if ("立即沟通" in sel or "startchat" in sel or "job_detail_chat" in sel or "job-op" in sel) and has_start_btn:
            return make_el(True)
        if ("chat-input" in sel or "chat-editor" in sel or "edit-area" in sel or "msg" in sel) and has_chat_input:
            return make_el(True)
        if ("btn-send" in sel or "发送" in sel or "submit" in sel or "btn-v2" in sel) and has_send_btn:
            return make_el(True)
        return None

    page.query_selector = AsyncMock(side_effect=query_selector)
    return page


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBossApplier:
    """Test BossApplier core logic by mocking Playwright."""

    @pytest.mark.asyncio
    async def test_successful_apply(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """Happy path: navigate → click 立即沟通 → type greeting → send."""
        page = _make_mock_page()
        applier = BossApplier(settings, history=history)

        with patch("jobclaw.applier.boss.asyncio.sleep", new=AsyncMock()):
            result = await applier._do_apply(page, job, profile, 0.0)

        assert result.status == ApplicationStatus.SUBMITTED
        assert history.is_applied(job.id)
        assert result.extra.get("greeting_sent")

    @pytest.mark.asyncio
    async def test_already_applied_in_history(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """If job is in history, skip without opening browser."""
        history.mark_applied(job.id, "submitted")
        applier = BossApplier(settings, history=history)
        # We call apply() but mock the browser so it doesn't launch
        applier._browser = MagicMock()

        mock_ctx = AsyncMock()
        mock_page = _make_mock_page()
        mock_ctx.new_page = AsyncMock(return_value=mock_page)
        applier._browser.new_context = AsyncMock(return_value=mock_ctx)

        result = await applier.apply(job, profile)
        assert result.status == ApplicationStatus.SUBMITTED
        assert result.extra["reason"] == "already_applied"

    @pytest.mark.asyncio
    async def test_continue_chat_detected(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """If 继续沟通 button found, treat as already applied."""
        page = _make_mock_page(has_continue_btn=True, has_start_btn=False)
        applier = BossApplier(settings, history=history)

        with patch("jobclaw.applier.boss.asyncio.sleep", new=AsyncMock()):
            result = await applier._do_apply(page, job, profile, 0.0)

        assert result.status == ApplicationStatus.SUBMITTED
        assert result.extra["reason"] == "already_applied"

    @pytest.mark.asyncio
    async def test_captcha_detected(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """If captcha appears, return CAPTCHA_BLOCKED."""
        page = _make_mock_page(has_captcha=True)
        applier = BossApplier(settings, history=history)

        with patch("jobclaw.applier.boss.asyncio.sleep", new=AsyncMock()):
            result = await applier._do_apply(page, job, profile, 0.0)

        assert result.status == ApplicationStatus.CAPTCHA_BLOCKED
        assert result.extra["reason"] == "captcha"

    @pytest.mark.asyncio
    async def test_daily_limit_from_history(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """If daily limit reached in history, return FAILED."""
        settings.boss_daily_limit = 3
        for i in range(3):
            history.mark_applied(f"prev-{i}", "submitted")

        applier = BossApplier(settings, history=history)
        applier._browser = MagicMock()

        result = await applier.apply(job, profile)
        assert result.status == ApplicationStatus.FAILED
        assert result.extra["reason"] == "daily_limit"

    @pytest.mark.asyncio
    async def test_daily_limit_from_page(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """If page shows daily limit text, return FAILED."""
        page = _make_mock_page(body_text="今日沟通人数已达上限，明天再来")
        applier = BossApplier(settings, history=history)

        with patch("jobclaw.applier.boss.asyncio.sleep", new=AsyncMock()):
            result = await applier._do_apply(page, job, profile, 0.0)
        assert result.status == ApplicationStatus.FAILED
        assert result.extra["reason"] == "daily_limit"

    @pytest.mark.asyncio
    async def test_button_not_found(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """If 立即沟通 button missing, return FAILED."""
        page = _make_mock_page(has_start_btn=False)
        applier = BossApplier(settings, history=history)

        with patch("jobclaw.applier.boss.asyncio.sleep", new=AsyncMock()):
            result = await applier._do_apply(page, job, profile, 0.0)
        assert result.status == ApplicationStatus.FAILED
        assert result.extra["reason"] == "button_not_found"

    @pytest.mark.asyncio
    async def test_no_greeting_uses_default(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """When boss_greeting is None, rely on Boss default greeting."""
        settings.boss_greeting = None
        page = _make_mock_page()
        applier = BossApplier(settings, history=history)

        with patch("jobclaw.applier.boss.asyncio.sleep", new=AsyncMock()):
            result = await applier._do_apply(page, job, profile, 0.0)
        assert result.status == ApplicationStatus.SUBMITTED

    @pytest.mark.asyncio
    async def test_greeting_template_substitution(
        self, settings: Settings, job: Job, profile: Profile, history: ApplyHistory,
    ) -> None:
        """Greeting template variables are substituted."""
        settings.boss_greeting = "Hi, I'm $name. Interested in $title at $company."
        applier = BossApplier(settings, history=history)
        greeting = applier._build_greeting(job, profile)
        assert greeting == "Hi, I'm Joe. Interested in 大模型工程师 at TestCorp."
