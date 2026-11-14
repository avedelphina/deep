#!/usr/bin/env python3
"""Focused tests for path-sensitive DEEP review policy."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repository_review_gate", ROOT / "scripts/repository_review_gate.py")
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


BASE = {
    "governance_reviewer": "alice",
    "human_gate": "avedelphina",
    "merge_executor": "anikke",
    "deep_sensitive_paths": ["docs/40-governance/**", "config/**"],
    "reviewer_rules": [
        {"patterns": ["docs/30-architecture/**"], "reviewers": ["holly"]},
        {"patterns": ["docs/10-inventory/hosts/**"], "reviewers": ["saga"]},
    ],
}


def pr(assignees: list[str] | None = None) -> dict:
    return {
        "user": {"login": "avril"},
        "assignees": [{"login": login} for login in (assignees or [])],
    }


def test_routine_instance_change_is_not_tom_gated() -> None:
    required, sensitive = GATE.required_reviewers(pr(), ["docs/10-inventory/agents/avril.md"], BASE)
    assert sensitive is False
    assert required == ["alice"]


def test_instance_governance_change_is_tom_gated() -> None:
    required, sensitive = GATE.required_reviewers(pr(), ["docs/40-governance/master-intent.md"], BASE)
    assert sensitive is True
    assert required == ["alice", "avedelphina"]


def test_selected_boundary_reviewer_is_added_without_tom() -> None:
    required, sensitive = GATE.required_reviewers(pr(), ["docs/30-architecture/stack.md"], BASE)
    assert sensitive is False
    assert required == ["alice", "holly"]


def test_assigned_boundary_reviewer_is_preserved() -> None:
    required, sensitive = GATE.required_reviewers(pr(["saga"]), ["docs/README.md"], BASE)
    assert sensitive is False
    assert required == ["alice", "saga"]


def test_framework_policy_can_make_tom_unconditional() -> None:
    rules = {**BASE, "human_gate_always": True}
    required, sensitive = GATE.required_reviewers(pr(), ["docs/README.md"], rules)
    assert sensitive is True
    assert required == ["alice", "avedelphina"]


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_"):
            value()
    print("repository review gate tests: valid")
