"""LinkedIn auto-apply adapter."""

from __future__ import annotations

import logging

from jobclaw.applier.base import BaseApplier
from jobclaw.models import Application, ApplicationStatus, Job, JobSource, Profile

logger = logging.getLogger(__name__)


class LinkedInApplier(BaseApplier):
    """Auto-apply to jobs on LinkedIn.

    Handles LinkedIn's "Easy Apply" flow where available,
    falls back to external application link tracking.
    """

    def __init__(self, settings: object) -> None:
        self._settings = settings

    async def apply(self, job: Job, profile: Profile) -> Application:
        """Submit a LinkedIn Easy Apply or track external application.

        TODO: Implement Playwright-based Easy Apply flow.
        """
        logger.info(
            "LinkedIn apply: %s @ %s [%s]",
            job.title, job.company, job.url,
        )

        # Placeholder — real implementation uses Playwright to:
        # 1. Navigate to job detail page
        # 2. Detect "Easy Apply" vs external link
        # 3. Fill Easy Apply form fields
        # 4. Submit application

        return Application(
            job_id=job.id,
            source=JobSource.LINKEDIN,
            status=ApplicationStatus.DRAFT,
            message=f"Applied via JobClaw: {job.title} @ {job.company}",
        )
