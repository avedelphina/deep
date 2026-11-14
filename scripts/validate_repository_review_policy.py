#!/usr/bin/env python3
"""Validate the DEEP repository review-policy contract."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/repository-review-policy.json"

REQUIRED = {
    "version",
    "repository",
    "default_branch",
    "governance_reviewer",
    "human_gate",
    "merge_executor",
    "framework_sensitive_paths",
    "required_conditions",
    "prohibitions",
}


def main() -> int:
    policy = json.loads(POLICY.read_text())
    missing = REQUIRED - policy.keys()
    if missing:
        raise SystemExit(f"missing policy fields: {sorted(missing)}")
    if policy["repository"] != "OCEAN/deep":
        raise SystemExit("policy repository must be OCEAN/deep")
    if policy["governance_reviewer"] == policy["human_gate"]:
        raise SystemExit("governance reviewer and human gate must be distinct")
    if policy["merge_executor"] in {
        policy["governance_reviewer"],
        policy["human_gate"],
    }:
        raise SystemExit("merge executor must be separate from approval identities")
    paths = policy["framework_sensitive_paths"]
    if not paths or not any(p.startswith("docs/40-governance/") for p in paths):
        raise SystemExit("framework-sensitive governance paths are incomplete")
    print("repository review policy: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
