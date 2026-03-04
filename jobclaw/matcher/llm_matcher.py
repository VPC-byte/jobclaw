"""LLM-based job-profile matching engine."""

from __future__ import annotations

import json
import logging

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage

from jobclaw.models import Job, Match, Profile

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a job matching assistant. Given a candidate profile and a job listing,
evaluate the match quality. Return a JSON object with:
- score: float 0.0-1.0 (how well the candidate fits)
- reasoning: list of strings explaining the score
- matched_skills: skills the candidate has that the job wants
- missing_skills: skills the job wants that the candidate lacks

Be objective. Consider skills, experience level, location preferences, and salary range.
Return ONLY valid JSON, no markdown."""


class LLMMatcher:
    """Score job-profile fit using an LLM."""

    def __init__(self, model_name: str = "gpt-4o-mini") -> None:
        self._model_name = model_name
        self._llm = init_chat_model(model_name)

    async def match(self, job: Job, profile: Profile) -> Match:
        """Score a single job against a profile.

        Args:
            job: The job listing to evaluate.
            profile: The candidate profile.

        Returns:
            Match object with score and reasoning.
        """
        prompt = self._build_prompt(job, profile)

        try:
            response = await self._llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])

            result = json.loads(response.content)

            return Match(
                job_id=job.id,
                score=max(0.0, min(1.0, float(result.get("score", 0.0)))),
                reasoning=result.get("reasoning", []),
                matched_skills=result.get("matched_skills", []),
                missing_skills=result.get("missing_skills", []),
            )
        except Exception as e:
            logger.error("LLM match failed for job %s: %s", job.id, e)
            return Match(
                job_id=job.id,
                score=0.0,
                reasoning=[f"Match evaluation failed: {e}"],
            )

    async def batch_match(
        self,
        jobs: list[Job],
        profile: Profile,
    ) -> list[Match]:
        """Score multiple jobs against a profile.

        Args:
            jobs: List of job listings.
            profile: The candidate profile.

        Returns:
            List of Match objects, one per job.
        """
        matches = []
        for job in jobs:
            match = await self.match(job, profile)
            matches.append(match)
            logger.info(
                "Matched %s @ %s → %.2f",
                job.title, job.company, match.score,
            )
        return matches

    @staticmethod
    def _build_prompt(job: Job, profile: Profile) -> str:
        """Build the matching prompt from job and profile data."""
        salary_info = ""
        if job.salary:
            salary_info = f"Salary: {job.salary.min_annual}-{job.salary.max_annual} {job.salary.currency}/year"

        return f"""## Candidate Profile
Name: {profile.name}
Experience: {profile.years_experience} years
Skills: {', '.join(profile.skills)}
Desired Roles: {', '.join(profile.desired_roles)}
Preferred Locations: {', '.join(profile.preferred_locations)}
Remote OK: {profile.remote_ok}

## Job Listing
Title: {job.title}
Company: {job.company}
Location: {job.location}
{salary_info}
Tags: {', '.join(job.tags)}
Description: {job.description[:2000]}

Evaluate the match and return JSON."""
