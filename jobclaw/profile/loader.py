"""Load candidate profiles from YAML or JSON files."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from jobclaw.models import Profile, SalaryRange


def load_profile(path: Path) -> Profile:
    """Load and validate a Profile from a YAML or JSON file.

    Args:
        path: Path to profile file (.yaml, .yml, or .json).

    Returns:
        Validated Profile object.

    Raises:
        ValueError: If file format is unsupported.
        FileNotFoundError: If the file doesn't exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")

    raw = path.read_text(encoding="utf-8")

    if path.suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(raw)
    elif path.suffix == ".json":
        data = json.loads(raw)
    else:
        raise ValueError(f"Unsupported profile format: {path.suffix}")

    # Map simplified YAML fields to Profile model
    preferences = data.pop("preferences", {})

    if "salary_min" in preferences or "salary_max" in preferences:
        data["salary_expectation"] = SalaryRange(
            min_annual=preferences.get("salary_min", 0) * 12,
            max_annual=preferences.get("salary_max", 0) * 12,
            currency="CNY",
        )

    if "locations" in preferences:
        data["preferred_locations"] = preferences["locations"]

    if "remote" in preferences:
        data["remote_ok"] = preferences["remote"]

    # Store extra preferences as metadata
    data.setdefault("desired_roles", data.pop("target_roles", []))

    return Profile.model_validate(data)
