"""Apply history tracker to prevent duplicate applications."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ApplyHistory:
    """Track applied jobs to avoid duplicates. Uses JSON file storage.

    Schema:
        {
            "jobs": {
                "<job_id>": {
                    "status": "submitted",
                    "applied_at": "2026-03-04T05:00:00+00:00",
                    "source": "boss"
                }
            }
        }
    """

    def __init__(self, path: str | Path = ".jobclaw/apply_history.json") -> None:
        self._path = Path(path)
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        """Load history from disk, or return empty structure."""
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to load apply history: %s", e)
        return {"jobs": {}}

    def _save(self) -> None:
        """Persist history to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def is_applied(self, job_id: str) -> bool:
        """Check if a job has already been applied to."""
        return job_id in self._data.get("jobs", {})

    def mark_applied(
        self,
        job_id: str,
        status: str,
        source: str = "boss",
    ) -> None:
        """Record an application attempt."""
        self._data.setdefault("jobs", {})[job_id] = {
            "status": status,
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "source": source,
        }
        self._save()
        logger.debug("Marked job %s as %s", job_id, status)

    def today_count(self) -> int:
        """Return how many jobs were applied to today (UTC)."""
        today = date.today().isoformat()
        count = 0
        for entry in self._data.get("jobs", {}).values():
            applied_at = entry.get("applied_at", "")
            if applied_at.startswith(today):
                count += 1
        return count
