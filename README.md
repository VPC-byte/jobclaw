#
#       __      _      _____ _
#      / /___  (_)____/ ___/(_)___ _      __
# __  / / __ \/ / ___/\__ \/ / __ \ | /| / /
#/ /_/ / /_/ / / /__ ___/ / / /_/ / |/ |/ /
#\____/\____/_/\___//____/_/\____/|__/|__/
#
# JobClaw: AI-Powered Job Hunting Agent

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

JobClaw is an open-source automation agent that helps candidates discover, evaluate, and apply for jobs at scale.

中文说明: JobClaw 旨在自动化找工作流程, 降低重复劳动, 让你把精力放在高价值决策上。

## Why JobClaw

Job searching is repetitive and fragmented:
- You search across multiple platforms repeatedly.
- You manually compare each job against your profile.
- You lose time tracking application status.

JobClaw solves this with an AI-first pipeline:
- Scrape jobs from Boss直聘 and LinkedIn.
- Match each job with your profile/resume using an LLM.
- Auto-apply to high-fit roles.
- Notify you via Telegram/Discord with match and application updates.

## Features

- Async Playwright scrapers for modern dynamic job sites
- Typed data models with Pydantic v2
- Config management with `.env` + `pydantic-settings`
- LLM matching pipeline with explainable scoring
- Auto-application adapters per platform
- Notification channels: Telegram and Discord
- Extensible architecture for new platforms and strategies

## Quick Start

```bash
# 1) Clone + install
pip install -e .

# 2) Install browser runtime for Playwright
playwright install chromium

# 3) Configure secrets
cp .env.example .env

# 4) Update your profile
cp profiles/example.yaml profiles/me.yaml

# 5) Run the agent
jobclaw run --profile profiles/me.yaml --query "Python Engineer"
```

中文提示: 首次使用请先配置 `.env` 和 `profiles/me.yaml`。

## Architecture

```text
+---------------------+
|   Profile Loader    |  YAML/JSON
+----------+----------+
           |
           v
+---------------------+      +----------------------+
|   Scraper Layer     |----->| Unified Job Objects  |
| Boss / LinkedIn     |      | (Pydantic Models)    |
+----------+----------+      +----------+-----------+
           |                            |
           v                            v
+---------------------+      +----------------------+
|   LLM Matcher       |----->| Match Score + Reason |
+----------+----------+      +----------+-----------+
           |                            |
           v                            v
+---------------------+      +----------------------+
|  Auto Applier       |----->| Application Status   |
| Boss / LinkedIn     |      | Submitted/Failed/... |
+----------+----------+      +----------+-----------+
           |                            |
           +------------+---------------+
                        v
              +--------------------+
              | Notification Layer |
              | Telegram / Discord |
              +--------------------+
```

See detailed design in [docs/architecture.md](./docs/architecture.md).

## Supported Platforms

| Platform | Status | Notes |
| --- | --- | --- |
| Boss直聘 (zhipin.com) | ✅ | Scrape + apply adapters included |
| LinkedIn | ✅ | Scrape + apply adapters included |
| 拉勾 (Lagou) | 🔜 | Planned adapter |
| 51Job | 🔜 | Planned adapter |

## CLI Usage

```bash
# Validate profile file
jobclaw validate-profile --profile profiles/example.yaml

# Scrape only
jobclaw scrape --platform all --query "Backend Engineer" --limit 20

# Full run
jobclaw run --platform all --profile profiles/example.yaml --query "AI Engineer" --limit 20
```

## Repository Layout

```text
jobclaw/
  applier/
  matcher/
  notifier/
  profile/
  scraper/
  cli.py
  config.py
  models.py
profiles/
  example.yaml
docs/
  architecture.md
tests/
  test_models.py
```

## Contributing

PRs are welcome for:
- New platform connectors
- Better matching prompts/heuristics
- Reliability improvements for automation flows
- Additional notification channels

Development commands:

```bash
pip install -e .[dev]
pytest -q
```

Before opening a PR:
- Run tests
- Add/adjust typing and docstrings
- Update docs for behavior changes

## Legal and Responsible Use

Automated job-site interactions may be subject to platform terms, local laws, and anti-bot policies.
Use this project responsibly and only on accounts/data you are authorized to operate.

## License

MIT License. See [LICENSE](./LICENSE).
