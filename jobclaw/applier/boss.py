"""Boss直聘 auto-apply adapter."""

from __future__ import annotations

import logging

from jobclaw.applier.base import BaseApplier
from jobclaw.models import Application, ApplicationStatus, Job, JobSource, Profile

logger = logging.getLogger(__name__)


class BossApplier(BaseApplier):
    """Auto-apply to jobs on Boss直聘.

    Note: Boss直聘 uses a chat-based application flow ("打招呼").
    This adapter sends the initial greeting message.
    """

    def __init__(self, settings: object) -> None:
        self._settings = settings

    async def apply(self, job: Job, profile: Profile) -> Application:
        """Send a greeting to the recruiter on Boss直聘.

        TODO: Implement Playwright-based chat initiation.
        """
        logger.info(
            "Boss apply: %s @ %s [%s]",
            job.title, job.company, job.url,
        )

        # Placeholder — real implementation uses Playwright to:
        # 1. Navigate to job detail page
        # 2. Click "立即沟通" button
        # 3. Send greeting message
        # 4. Confirm application status

        return Application(
            job_id=job.id,
            source=JobSource.BOSS,
            status=ApplicationStatus.DRAFT,
            message=f"Applied via JobClaw: {job.title} @ {job.company}",
        )
