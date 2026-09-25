#!/usr/bin/env python3
"""Validate the machine-readable DEEP infrastructure intent."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = {
    "id", "version", "owner", "class", "outcome", "scope",
    "health_dimensions", "thresholds", "automation", "escalation", "evidence",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "intents/infrastructure.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")

    missing = REQUIRED - data.keys()
    if missing:
        fail(f"missing top-level fields: {', '.join(sorted(missing))}")
    if data["class"] != "infrastructure":
        fail("class must be infrastructure")
    if not isinstance(data["version"], int) or data["version"] < 1:
        fail("version must be a positive integer")
    if not data["owner"] or not data["scope"].get("asset_group"):
        fail("owner and scope.asset_group are required")
    dimensions = data["health_dimensions"]
    if not isinstance(dimensions, list) or not dimensions:
        fail("health_dimensions must be non-empty")
    for dimension in dimensions:
        for key in ("id", "measurement", "severity"):
            if not dimension.get(key):
                fail(f"health dimension missing {key}: {dimension}")
    sweep = data["automation"].get("sweep", {})
    for key in ("id", "schedule", "timeout_seconds", "lock", "verification"):
        if not sweep.get(key):
            fail(f"automation.sweep missing {key}")
    if sweep["timeout_seconds"] <= 0:
        fail("automation.sweep.timeout_seconds must be positive")
    escalation = data["escalation"]
    for key in ("owner", "blocked_after_hours", "critical_after_minutes", "required_fields"):
        if key not in escalation:
            fail(f"escalation missing {key}")
    evidence = data["evidence"]
    if not evidence.get("required_fields") or not evidence.get("results"):
        fail("evidence requires required_fields and results")
    print(f"OK: {path} intent={data['id']} v{data['version']} dimensions={len(dimensions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
