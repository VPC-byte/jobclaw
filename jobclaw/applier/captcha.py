"""Captcha detection and notification for Boss直聘."""

from __future__ import annotations

import logging

from playwright.async_api import Page

logger = logging.getLogger(__name__)

# Known captcha selectors on Boss直聘
_CAPTCHA_SELECTORS = [
    "#captcha",
    ".slide-verify",
    ".geetest_panel",
    ".captcha-wrapper",
    "[class*='verify']",
    "[class*='captcha']",
    "div.dialog-container:has(canvas)",  # slider captcha dialog
]


async def detect_captcha(page: Page) -> bool:
    """Detect if the page is showing a captcha challenge.

    Checks multiple known selectors and also looks for common
    captcha-related text in visible dialogs.
    """
    for selector in _CAPTCHA_SELECTORS:
        try:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                logger.warning("Captcha detected via selector: %s", selector)
                return True
        except Exception:
            continue

    # Text-based fallback: check for common captcha prompt text
    try:
        body_text = await page.inner_text("body")
        captcha_keywords = ["请完成安全验证", "滑动验证", "图形验证", "安全检测"]
        for kw in captcha_keywords:
            if kw in body_text:
                logger.warning("Captcha detected via keyword: %s", kw)
                return True
    except Exception:
        pass

    return False


async def notify_captcha(notifier: object, job_url: str) -> None:
    """Send a captcha alert via the notifier (e.g. Telegram).

    Args:
        notifier: Object with an async ``send_text(text)`` method
                  (e.g. TelegramNotifier).
        job_url: The URL where captcha was encountered.
    """
    message = (
        "🚨 <b>Boss直聘 验证码拦截</b>\n\n"
        f"投递时遇到验证码，需要手动处理：\n"
        f"<code>{job_url}</code>\n\n"
        "请在浏览器中完成验证后，投递将自动继续。"
    )
    try:
        if hasattr(notifier, "send_text"):
            await notifier.send_text(message)
            logger.info("Captcha notification sent")
        else:
            logger.warning("Notifier does not support send_text")
    except Exception as e:
        logger.error("Failed to send captcha notification: %s", e)
