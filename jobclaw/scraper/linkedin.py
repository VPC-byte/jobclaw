"""LinkedIn scraper using Playwright."""

from __future__ import annotations

import logging
from typing import Self

from playwright.async_api import Browser, Playwright, async_playwright

from jobclaw.models import Job, JobSource
from jobclaw.scraper.base import BaseScraper

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """Scrape job listings from LinkedIn Jobs."""

    source = JobSource.LINKEDIN

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
        """Scrape LinkedIn public job search results.

        Uses cookie-based auth from settings.linkedin_cookie for
        authenticated access (more results, less rate limiting).
        """
        if not self._browser:
            raise RuntimeError("Scraper not initialized. Use 'async with' context.")

        context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )

        cookie = getattr(self._settings, "linkedin_cookie", None)
        if cookie:
            await context.add_cookies([
                {"name": "li_at", "value": cookie, "domain": ".linkedin.com", "path": "/"}
            ])

        page = await context.new_page()
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={query}"
        if location:
            search_url += f"&location={location}"

        jobs: list[Job] = []
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)  # Let dynamic content load

            cards = await page.query_selector_all(".base-card")

            for card in cards[:limit]:
                try:
                    title_el = await card.query_selector(".base-search-card__title")
                    company_el = await card.query_selector(".base-search-card__subtitle a")
                    location_el = await card.query_selector(".job-search-card__location")
                    link_el = await card.query_selector("a.base-card__full-link")

                    title = await title_el.inner_text() if title_el else "Unknown"
                    company = await company_el.inner_text() if company_el else "Unknown"
                    loc = await location_el.inner_text() if location_el else (location or "Remote")
                    href = await link_el.get_attribute("href") if link_el else ""

                    url = href if href.startswith("http") else f"https://www.linkedin.com{href}"

                    jobs.append(Job(
                        source=JobSource.LINKEDIN,
                        title=title.strip(),
                        company=company.strip(),
                        location=loc.strip(),
                        url=url,
                        description="",  # Full desc requires clicking into job detail
                        tags=[],
                    ))
                except Exception as e:
                    logger.warning("Failed to parse LinkedIn card: %s", e)
                    continue

        except Exception as e:
            logger.error("LinkedIn scrape failed: %s", e)
        finally:
            await context.close()

        logger.info("LinkedIn: scraped %d jobs for query '%s'", len(jobs), query)
        return jobs
