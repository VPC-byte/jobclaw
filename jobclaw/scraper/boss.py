"""Boss直聘 (zhipin.com) scraper using Playwright."""

from __future__ import annotations

import logging
from typing import Self

from playwright.async_api import Browser, Playwright, async_playwright

from jobclaw.models import Job, JobSource, SalaryRange
from jobclaw.scraper.base import BaseScraper

logger = logging.getLogger(__name__)


class BossScraper(BaseScraper):
    """Scrape job listings from Boss直聘."""

    source = JobSource.BOSS

    def __init__(self, settings: object) -> None:
        self._settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def __aenter__(self) -> Self:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=getattr(self._settings, "jobclaw_headless", True),
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def scrape_jobs(
        self,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[Job]:
        """Scrape Boss直聘 for jobs matching query.

        Uses cookie-based auth from settings.boss_cookie.
        """
        if not self._browser:
            raise RuntimeError("Scraper not initialized. Use 'async with' context.")

        context = await self._browser.new_context()
        cookie = getattr(self._settings, "boss_cookie", None)
        if cookie:
            await context.add_cookies([
                {"name": "wt2", "value": cookie, "domain": ".zhipin.com", "path": "/"}
            ])

        page = await context.new_page()
        search_url = f"https://www.zhipin.com/web/geek/job?query={query}&city=101280600"
        if location:
            search_url += f"&location={location}"

        jobs: list[Job] = []
        try:
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            cards = await page.query_selector_all(".job-card-wrapper")

            for card in cards[:limit]:
                try:
                    title_el = await card.query_selector(".job-name")
                    company_el = await card.query_selector(".company-name a")
                    salary_el = await card.query_selector(".salary")
                    link_el = await card.query_selector(".job-card-left a")
                    tags_els = await card.query_selector_all(".tag-list span")
                    desc_el = await card.query_selector(".job-card-desc")

                    title = await title_el.inner_text() if title_el else "Unknown"
                    company = await company_el.inner_text() if company_el else "Unknown"
                    salary_text = await salary_el.inner_text() if salary_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""
                    tags = [await t.inner_text() for t in tags_els]
                    desc = await desc_el.inner_text() if desc_el else ""

                    url = f"https://www.zhipin.com{href}" if href else "https://www.zhipin.com"

                    salary = _parse_boss_salary(salary_text)

                    jobs.append(Job(
                        source=JobSource.BOSS,
                        title=title.strip(),
                        company=company.strip(),
                        location=location or "深圳",
                        url=url,
                        description=desc.strip(),
                        salary=salary,
                        tags=tags,
                    ))
                except Exception as e:
                    logger.warning("Failed to parse Boss card: %s", e)
                    continue

        except Exception as e:
            logger.error("Boss scrape failed: %s", e)
        finally:
            await context.close()

        logger.info("Boss: scraped %d jobs for query '%s'", len(jobs), query)
        return jobs


def _parse_boss_salary(text: str) -> SalaryRange | None:
    """Parse Boss salary text like '25-50K·16薪' into SalaryRange."""
    import re

    match = re.search(r"(\d+)-(\d+)K", text)
    if not match:
        return None

    low = int(match.group(1)) * 1000
    high = int(match.group(2)) * 1000

    # Check for bonus months (e.g. 16薪)
    months = 12
    bonus_match = re.search(r"(\d+)薪", text)
    if bonus_match:
        months = int(bonus_match.group(1))

    return SalaryRange(
        min_annual=low * months,
        max_annual=high * months,
        currency="CNY",
    )
