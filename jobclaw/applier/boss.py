"""Boss直聘 auto-apply adapter — 打招呼 (chat greeting) flow."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from datetime import datetime, timezone
from string import Template
from typing import Self

from playwright.async_api import Browser, Page, Playwright, async_playwright

from jobclaw.applier.base import BaseApplier
from jobclaw.applier.captcha import detect_captcha, notify_captcha
from jobclaw.applier.history import ApplyHistory
from jobclaw.config import Settings
from jobclaw.models import Application, ApplicationStatus, Job, JobSource, Profile

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Selectors — multiple fallbacks for resilience
# ---------------------------------------------------------------------------

_BTN_START_CHAT = [
    "a.btn-startchat",                          # primary CTA
    ".job-detail-box .btn-startchat",
    "a[ka='job_detail_chat']",
    "a:has-text('立即沟通')",
    "div.job-op a.btn",                          # broad fallback
]

_BTN_CONTINUE_CHAT = [
    "a:has-text('继续沟通')",
    "a.btn-startchat:has-text('继续沟通')",
]

_CHAT_INPUT = [
    "#chat-input",
    ".chat-input textarea",
    "div.chat-editor textarea",
    "[contenteditable='true'].chat-input",
    "div.edit-area [contenteditable='true']",
    "textarea[name='msg']",
]

_BTN_SEND = [
    "button.btn-send",
    "button:has-text('发送')",
    ".chat-op button[type='submit']",
    "div.message-controls button.btn-v2",
]

_DAILY_LIMIT_TEXT = [
    "今日沟通人数已达上限",
    "今日投递次数已用完",
    "今天的机会已用完",
]


class BossApplier(BaseApplier):
    """Auto-apply to jobs on Boss直聘 via the 打招呼 chat flow.

    Usage::

        async with BossApplier(settings) as applier:
            result = await applier.apply(job, profile)

    The applier manages its own Playwright browser lifecycle and
    cookie-based authentication (same mechanism as BossScraper).
    """

    def __init__(
        self,
        settings: Settings,
        *,
        notifier: object | None = None,
        history: ApplyHistory | None = None,
    ) -> None:
        self._settings = settings
        self._notifier = notifier
        self._history = history or ApplyHistory()
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    # -- lifecycle ----------------------------------------------------------

    async def __aenter__(self) -> Self:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self._settings.jobclaw_headless,
        )
        logger.info("BossApplier browser launched (headless=%s)", self._settings.jobclaw_headless)
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("BossApplier browser closed")

    # -- public API ---------------------------------------------------------

    async def apply(self, job: Job, profile: Profile) -> Application:  # noqa: C901
        """Send a greeting to the recruiter on Boss直聘.

        Returns an Application with appropriate status:
          - SUBMITTED  — greeting sent (or already chatting)
          - FAILED     — unrecoverable error (captcha, limit, etc.)
          - CAPTCHA_BLOCKED — captcha detected, manual intervention needed
        """
        t0 = time.monotonic()
        logger.info("Boss apply START: %s @ %s [%s]", job.title, job.company, job.url)

        # --- pre-flight checks ------------------------------------------------
        if self._history.is_applied(job.id):
            logger.info("Skipped (already applied): %s", job.id)
            return self._make_app(
                job, ApplicationStatus.SUBMITTED,
                extra={"reason": "already_applied"},
            )

        if self._history.today_count() >= self._settings.boss_daily_limit:
            logger.warning("Daily limit reached (%d)", self._settings.boss_daily_limit)
            return self._make_app(
                job, ApplicationStatus.FAILED,
                extra={"reason": "daily_limit"},
            )

        if not self._browser:
            raise RuntimeError("BossApplier not initialised — use 'async with'.")

        # --- browser context --------------------------------------------------
        context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        cookie = self._settings.boss_cookie
        if cookie:
            await context.add_cookies([
                {"name": "wt2", "value": cookie, "domain": ".zhipin.com", "path": "/"},
            ])

        page = await context.new_page()

        try:
            return await self._do_apply(page, job, profile, t0)
        except Exception as exc:
            logger.exception("Unexpected error during Boss apply: %s", exc)
            return self._make_app(
                job, ApplicationStatus.FAILED,
                extra={"reason": "unexpected_error", "error": str(exc)},
            )
        finally:
            await context.close()

    # -- internal flow ------------------------------------------------------

    async def _do_apply(  # noqa: C901
        self,
        page: Page,
        job: Job,
        profile: Profile,
        t0: float,
    ) -> Application:
        """Core apply flow inside a browser page."""

        # 1. Navigate to job detail page
        logger.info("Navigating to %s", job.url)
        await page.goto(str(job.url), wait_until="domcontentloaded", timeout=30_000)
        await self._human_delay(0.5, 1.5)

        # 2. Captcha check
        if await detect_captcha(page):
            if self._notifier:
                await notify_captcha(self._notifier, str(job.url))
            return self._make_app(
                job, ApplicationStatus.CAPTCHA_BLOCKED,
                extra={"reason": "captcha"},
            )

        # 3. Check daily limit text on page
        body = await page.inner_text("body")
        for limit_text in _DAILY_LIMIT_TEXT:
            if limit_text in body:
                logger.warning("Daily limit detected on page: %s", limit_text)
                return self._make_app(
                    job, ApplicationStatus.FAILED,
                    extra={"reason": "daily_limit"},
                )

        # 4. Check if already chatting (继续沟通)
        continue_btn = await self._find_element(page, _BTN_CONTINUE_CHAT)
        if continue_btn:
            logger.info("Already in conversation for %s", job.id)
            self._history.mark_applied(job.id, "submitted")
            return self._make_app(
                job, ApplicationStatus.SUBMITTED,
                extra={"reason": "already_applied"},
            )

        # 5. Find and click 立即沟通
        start_btn = await self._find_element(page, _BTN_START_CHAT)
        if not start_btn:
            logger.error("Cannot find '立即沟通' button for %s", job.url)
            return self._make_app(
                job, ApplicationStatus.FAILED,
                extra={"reason": "button_not_found"},
            )

        logger.info("Clicking '立即沟通'")
        await start_btn.click()
        await self._human_delay(1.5, 3.0)

        # 6. Post-click captcha check
        if await detect_captcha(page):
            if self._notifier:
                await notify_captcha(self._notifier, str(job.url))
            return self._make_app(
                job, ApplicationStatus.CAPTCHA_BLOCKED,
                extra={"reason": "captcha"},
            )

        # 7. Compose greeting
        greeting = self._build_greeting(job, profile)

        if greeting:
            # 8. Find chat input and type greeting
            chat_input = await self._find_element(page, _CHAT_INPUT)
            if not chat_input:
                # Might have auto-sent the default greeting from Boss backend
                logger.info("No chat input found — default greeting may have been sent")
                self._history.mark_applied(job.id, "submitted")
                elapsed = time.monotonic() - t0
                return self._make_app(
                    job, ApplicationStatus.SUBMITTED,
                    extra={"reason": "default_greeting", "response_time": round(elapsed, 2)},
                )

            logger.info("Typing greeting: %s", greeting[:60])
            await chat_input.click()
            await self._human_delay(0.3, 0.8)

            # Type slowly to mimic human input
            await chat_input.fill("")
            await page.keyboard.type(greeting, delay=random.randint(30, 80))
            await self._human_delay(0.5, 1.0)

            # 9. Send
            send_btn = await self._find_element(page, _BTN_SEND)
            if send_btn:
                await send_btn.click()
                logger.info("Send button clicked")
            else:
                # Fallback: press Enter
                await page.keyboard.press("Enter")
                logger.info("Sent via Enter key")

            await self._human_delay(1.0, 2.0)
        else:
            # No custom greeting — boss will use the pre-configured default
            logger.info("No custom greeting; relying on Boss default greeting")

        # 10. Verify success — check for sent message or conversation state
        # After sending, Boss typically shows the message in the chat window
        # We consider it successful if no error dialog appeared
        if await detect_captcha(page):
            if self._notifier:
                await notify_captcha(self._notifier, str(job.url))
            return self._make_app(
                job, ApplicationStatus.CAPTCHA_BLOCKED,
                extra={"reason": "captcha"},
            )

        # Mark in history
        self._history.mark_applied(job.id, "submitted")
        elapsed = time.monotonic() - t0
        logger.info(
            "Boss apply SUCCESS: %s @ %s (%.1fs)",
            job.title, job.company, elapsed,
        )

        # Inter-apply delay (human-like pacing)
        delay = random.uniform(
            self._settings.boss_apply_delay_min,
            self._settings.boss_apply_delay_max,
        )
        logger.debug("Waiting %.1fs before next apply", delay)
        await asyncio.sleep(delay)

        return self._make_app(
            job, ApplicationStatus.SUBMITTED,
            extra={
                "greeting_sent": greeting or "(default)",
                "response_time": round(elapsed, 2),
            },
        )

    # -- helpers ------------------------------------------------------------

    def _build_greeting(self, job: Job, profile: Profile) -> str | None:
        """Build a greeting message from template, or return None for default."""
        template = self._settings.boss_greeting
        if not template:
            return None

        # Support $-style substitution: $company, $title, $name
        try:
            return Template(template).safe_substitute(
                company=job.company,
                title=job.title,
                name=profile.name,
            )
        except Exception as e:
            logger.warning("Greeting template error: %s — using raw template", e)
            return template

    @staticmethod
    async def _find_element(page: Page, selectors: list[str]):
        """Try multiple selectors and return the first visible match."""
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    visible = await el.is_visible()
                    if visible:
                        return el
            except Exception:
                continue
        return None

    @staticmethod
    async def _human_delay(lo: float = 0.5, hi: float = 1.5) -> None:
        """Sleep for a random duration to mimic human interaction."""
        await asyncio.sleep(random.uniform(lo, hi))

    @staticmethod
    def _make_app(
        job: Job,
        status: ApplicationStatus,
        *,
        extra: dict | None = None,
    ) -> Application:
        """Create an Application result."""
        return Application(
            job_id=job.id,
            source=JobSource.BOSS,
            status=status,
            message=f"{job.title} @ {job.company}",
            applied_at=datetime.now(timezone.utc) if status == ApplicationStatus.SUBMITTED else None,
            extra=extra or {},
        )
