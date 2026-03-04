"""Command-line interface for JobClaw workflows."""

from __future__ import annotations

import asyncio
from pathlib import Path

import click

from jobclaw.applier.boss import BossApplier
from jobclaw.applier.linkedin import LinkedInApplier
from jobclaw.config import get_settings
from jobclaw.matcher.llm_matcher import LLMMatcher
from jobclaw.models import JobSource
from jobclaw.notifier.discord import DiscordNotifier
from jobclaw.notifier.telegram import TelegramNotifier
from jobclaw.profile.loader import load_profile
from jobclaw.scraper.boss import BossScraper
from jobclaw.scraper.linkedin import LinkedInScraper


@click.group(help="JobClaw: AI-powered job hunting agent.")
def main() -> None:
    """Root CLI group."""


@main.command("validate-profile")
@click.option(
    "--profile",
    "profile_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
    help="Path to profile YAML or JSON file.",
)
def validate_profile_command(profile_path: Path) -> None:
    """Validate a profile document against the Profile model."""

    profile = load_profile(profile_path)
    click.echo(f"Profile OK: {profile.name} ({len(profile.skills)} skills)")


@main.command("scrape")
@click.option("--platform", type=click.Choice(["boss", "linkedin", "all"]), default="all")
@click.option("--query", required=True, help="Search query, e.g. 'Python Engineer'.")
@click.option("--location", default=None, help="Optional location filter.")
@click.option("--limit", default=20, show_default=True, type=int)
def scrape_command(platform: str, query: str, location: str | None, limit: int) -> None:
    """Scrape jobs from selected platforms and print a summary."""

    asyncio.run(_scrape(platform=platform, query=query, location=location, limit=limit))


@main.command("run")
@click.option("--platform", type=click.Choice(["boss", "linkedin", "all"]), default="all")
@click.option("--query", required=True, help="Search query, e.g. 'AI Engineer'.")
@click.option("--location", default=None, help="Optional location filter.")
@click.option(
    "--profile",
    "profile_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
)
@click.option("--limit", default=20, show_default=True, type=int)
def run_command(
    platform: str,
    query: str,
    location: str | None,
    profile_path: Path,
    limit: int,
) -> None:
    """Run end-to-end pipeline: scrape -> match -> notify."""

    asyncio.run(
        _run_pipeline(
            platform=platform,
            query=query,
            location=location,
            profile_path=profile_path,
            limit=limit,
        )
    )


async def _scrape(platform: str, query: str, location: str | None, limit: int) -> None:
    """Internal async scrape workflow."""

    settings = get_settings()
    scrapers = []
    if platform in {"boss", "all"}:
        scrapers.append(BossScraper(settings))
    if platform in {"linkedin", "all"}:
        scrapers.append(LinkedInScraper(settings))

    if not scrapers:
        click.echo("No scraper configured for requested platform.")
        return

    total_jobs = 0
    for scraper in scrapers:
        async with scraper:
            jobs = await scraper.scrape_jobs(query=query, location=location, limit=limit)
            total_jobs += len(jobs)
            click.echo(f"{scraper.source.value}: scraped {len(jobs)} job(s)")

    click.echo(f"Total scraped jobs: {total_jobs} | Headless={settings.jobclaw_headless}")


async def _run_pipeline(
    platform: str,
    query: str,
    location: str | None,
    profile_path: Path,
    limit: int,
) -> None:
    """Internal async end-to-end workflow."""

    settings = get_settings()
    profile = load_profile(profile_path)
    matcher = LLMMatcher(model_name=settings.jobclaw_llm_model)

    scrapers = []
    if platform in {"boss", "all"}:
        scrapers.append(BossScraper(settings))
    if platform in {"linkedin", "all"}:
        scrapers.append(LinkedInScraper(settings))

    jobs = []
    for scraper in scrapers:
        async with scraper:
            jobs.extend(await scraper.scrape_jobs(query=query, location=location, limit=limit))

    if not jobs:
        click.echo("No jobs found.")
        return

    matches = await matcher.batch_match(jobs=jobs, profile=profile)
    ranked_matches = sorted(matches, key=lambda match: match.score, reverse=True)

    top_matches = ranked_matches[: min(5, len(ranked_matches))]
    click.echo(f"Top matches for {profile.name}:")
    for match in top_matches:
        click.echo(f"- {match.job_id}: score={match.score:.2f}")

    boss_applier = BossApplier(settings)
    linkedin_applier = LinkedInApplier(settings)

    applications = []
    for job in jobs:
        score = next((item.score for item in top_matches if item.job_id == job.id), 0.0)
        if score < 0.75:
            continue

        if job.source == JobSource.BOSS:
            async with boss_applier:
                applications.append(await boss_applier.apply(job=job, profile=profile))
        elif job.source == JobSource.LINKEDIN:
            async with linkedin_applier:
                applications.append(await linkedin_applier.apply(job=job, profile=profile))

    click.echo(f"Applications attempted: {len(applications)}")

    await _notify_summary(
        settings=settings,
        profile_name=profile.name,
        total_jobs=len(jobs),
        total_matches=len(top_matches),
        total_applications=len(applications),
    )


async def _notify_summary(
    *,
    settings: object,
    profile_name: str,
    total_jobs: int,
    total_matches: int,
    total_applications: int,
) -> None:
    """Send summary notifications to configured channels."""

    summary = (
        f"JobClaw run complete for {profile_name}. "
        f"Jobs={total_jobs}, TopMatches={total_matches}, Applications={total_applications}."
    )

    if getattr(settings, "telegram_bot_token", None) and getattr(settings, "telegram_chat_id", None):
        telegram = TelegramNotifier(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
        )
        await telegram.send_text(summary)

    if getattr(settings, "discord_webhook_url", None):
        discord = DiscordNotifier(webhook_url=settings.discord_webhook_url)
        await discord.send_text(summary)


if __name__ == "__main__":
    main()
