"""Tests for ApplyHistory — anti-duplicate tracking."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jobclaw.applier.history import ApplyHistory


@pytest.fixture()
def history_path(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


class TestApplyHistory:
    def test_empty_history(self, history_path: Path) -> None:
        h = ApplyHistory(path=history_path)
        assert not h.is_applied("job-1")
        assert h.today_count() == 0

    def test_mark_and_check(self, history_path: Path) -> None:
        h = ApplyHistory(path=history_path)
        h.mark_applied("job-1", "submitted")
        assert h.is_applied("job-1")
        assert not h.is_applied("job-2")
        assert h.today_count() == 1

    def test_persistence(self, history_path: Path) -> None:
        h1 = ApplyHistory(path=history_path)
        h1.mark_applied("job-x", "submitted")

        # Reload from disk
        h2 = ApplyHistory(path=history_path)
        assert h2.is_applied("job-x")
        assert h2.today_count() == 1

    def test_today_count_multiple(self, history_path: Path) -> None:
        h = ApplyHistory(path=history_path)
        for i in range(5):
            h.mark_applied(f"job-{i}", "submitted")
        assert h.today_count() == 5

    def test_corrupt_file_recovers(self, history_path: Path) -> None:
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text("not json", encoding="utf-8")
        h = ApplyHistory(path=history_path)
        assert not h.is_applied("anything")
        # Should still work after recovery
        h.mark_applied("job-1", "submitted")
        assert h.is_applied("job-1")

    def test_today_count_excludes_old(self, history_path: Path) -> None:
        """Jobs from a different date should not count toward today."""
        h = ApplyHistory(path=history_path)
        h.mark_applied("today-job", "submitted")

        # Manually inject an old entry
        data = json.loads(history_path.read_text())
        data["jobs"]["old-job"] = {
            "status": "submitted",
            "applied_at": "2020-01-01T00:00:00+00:00",
            "source": "boss",
        }
        history_path.write_text(json.dumps(data))

        h2 = ApplyHistory(path=history_path)
        assert h2.today_count() == 1  # only today's job
