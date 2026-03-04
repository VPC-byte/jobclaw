"""Abstract base class for job scrapers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from jobclaw.models import Job, JobSource


class BaseScraper(ABC):
    """Base scraper that all platform scrapers must implement."""

    source: JobSource

    @abstractmethod
    async def scrape_jobs(
        self,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[Job]:
        """Scrape job listings matching the query.

        Args:
            query: Search keywords (e.g. "Python Engineer").
            location: Optional location filter.
            limit: Maximum number of jobs to return.

        Returns:
            List of normalized Job objects.
        """
        ...

    async def __aenter__(self) -> Self:
        """Set up browser/session resources."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Tear down browser/session resources."""
