# JobClaw Architecture

## Overview

JobClaw follows a pipeline architecture with five stages:

```
Profile → Scrape → Match → Apply → Notify
```

Each stage is modular and can be extended with new platform adapters.

## Pipeline Flow

```
┌─────────────┐
│   Profile    │  User's skills, preferences, salary range
│   Loader     │  Supports YAML and JSON formats
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Scraper    │  Playwright-based browser automation
│   Layer      │  One adapter per platform (Boss/LinkedIn/...)
│              │  Outputs normalized Job objects
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    LLM      │  Sends (Job + Profile) to LLM
│   Matcher   │  Returns score (0-1) + reasoning
│              │  Configurable model (GPT-4o-mini default)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Auto     │  Platform-specific application flow
│   Applier   │  Boss: "打招呼" chat initiation
│              │  LinkedIn: Easy Apply form fill
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Notifier   │  Telegram Bot API / Discord Webhook
│   Layer     │  Summary of matches + application status
└─────────────┘
```

## Data Flow

All stages communicate through Pydantic models:

- **Profile** → loaded from YAML/JSON, validated
- **Job** → normalized from any platform, includes salary, tags, URL
- **Match** → LLM scoring result with reasoning
- **Application** → tracks status (draft → submitted → interview → offer)

## Key Design Decisions

1. **Playwright over API scraping** — Job sites have aggressive anti-bot, browser automation is more reliable
2. **LLM for matching** — Rules-based matching is too rigid; LLM understands nuance (e.g. "3 years Python" ≈ "senior backend")
3. **Async throughout** — Scraping and API calls are I/O bound, async improves throughput
4. **Platform adapters** — Abstract base classes ensure consistent interface, easy to add new platforms
5. **Cookie-based auth** — Simpler than OAuth, user exports cookies from their browser session

## Adding a New Platform

1. Create `jobclaw/scraper/newplatform.py` extending `BaseScraper`
2. Create `jobclaw/applier/newplatform.py` extending `BaseApplier`
3. Add new `JobSource` enum value in `models.py`
4. Register in `cli.py`

## Security Considerations

- API keys and cookies stored in `.env` (gitignored)
- No credentials hardcoded in source
- Rate limiting respected per platform
- User responsible for compliance with platform ToS
