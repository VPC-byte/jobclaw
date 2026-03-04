"""Abstract base class for job application adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from jobclaw.models import Application, Job, Profile


class BaseApplier(ABC):
    """Base applier that platform-specific appliers must implement."""

    @abstractmethod
    async def apply(self, job: Job, profile: Profile) -> Application:
        """Submit an application for the given job.

        Args:
            job: The job to apply to.
            profile: The candidate profile.

        Returns:
            Application object with status.
        """
        ...

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        pass
