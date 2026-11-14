#!/usr/bin/env python3
"""Evaluate and, only when requested, merge a DEEP pull request."""
from __future__ import annotations

import fnmatch
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/repository-review-policy.json"


def api_request(method: str, path: str, payload: Optional[object] = None) -> Any:
    api_root = os.environ.get("GITEA_API_ROOT", "https://git.ocean/api/v1")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITEA_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN/GITEA_TOKEN is required")
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(
        api_root.rstrip("/") + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
    except (HTTPError, URLError) as exc:
        status = getattr(exc, "code", "transport-error")
        raise SystemExit(f"Gitea API {method} {path} failed: {status}") from exc
    if not body:
        return None
    return json.loads(body)


def policy() -> dict:
    return json.loads(POLICY_PATH.read_text())


def pull_request(repo: str, number: str) -> dict:
    return api_request("GET", f"/repos/{repo}/pulls/{number}")  # type: ignore[return-value]


def changed_files(repo: str, number: str) -> list[str]:
    result: list[str] = []
    for page in range(1, 11):
        batch = api_request(
            "GET", f"/repos/{repo}/pulls/{number}/files?limit=100&page={page}"
        )
        if not isinstance(batch, list):
            raise SystemExit("Gitea files response was not a list")
        result.extend(item["filename"] for item in batch)
        if len(batch) < 100:
            break
    return result


def sensitive(files: list[str], rules: dict) -> bool:
    paths = rules.get("framework_sensitive_paths") or rules.get("deep_sensitive_paths") or []
    return any(fnmatch.fnmatchcase(filename, pattern) for filename in files for pattern in paths)


def required_reviewers(pr: dict, files: list[str], rules: dict) -> tuple[list[str], bool]:
    names = [rules["governance_reviewer"]]
    is_sensitive = rules.get("human_gate_always", False) or sensitive(files, rules)
    if is_sensitive:
        names.append(rules["human_gate"])
    author = pr["user"]["login"]
    controls = {rules["governance_reviewer"], rules["human_gate"], rules["merge_executor"], author}
    for reviewer_rule in rules.get("reviewer_rules", []):
        if any(
            fnmatch.fnmatchcase(filename, pattern)
            for filename in files
            for pattern in reviewer_rule["patterns"]
        ):
            for login in reviewer_rule["reviewers"]:
                if login not in controls and login not in names:
                    names.append(login)
    for assignee in pr.get("assignees") or []:
        login = assignee["login"]
        if login not in controls and login not in names:
            names.append(login)
    return names, is_sensitive


def current_reviews(repo: str, number: str, head: str) -> list[dict]:
    reviews = api_request("GET", f"/repos/{repo}/pulls/{number}/reviews?limit=100")
    if not isinstance(reviews, list):
        raise SystemExit("Gitea reviews response was not a list")
    allowed = {"APPROVED", "PENDING", "COMMENT", "REQUEST_CHANGES", "REQUEST_REVIEW"}
    unknown = sorted({item.get("state") for item in reviews} - allowed)
    if unknown:
        raise SystemExit(f"unknown forge review state(s): {unknown}")
    return [
        item
        for item in reviews
        if item.get("official") is True
        and item.get("stale") is False
        and item.get("dismissed") is False
        and item.get("commit_id") == head
    ]


def evaluate(repo: str, number: str, wait_for_ci: bool = False) -> tuple[bool, str, dict]:
    rules = policy()
    pr = pull_request(repo, number)
    head = pr["head"]["sha"]
    files = changed_files(repo, number)
    required, is_sensitive = required_reviewers(pr, files, rules)
    reviews = current_reviews(repo, number, head)
    reports: list[str] = []
    ok = True

    if pr.get("state") != "open" or pr.get("draft") or not pr.get("mergeable"):
        ok = False
        reports.append("pull request is not open, non-draft, and mergeable")
    if pr.get("user", {}).get("login") == rules["merge_executor"]:
        ok = False
        reports.append("original author is the merge executor")

    requested = [item["login"] for item in pr.get("requested_reviewers") or []]
    if requested or pr.get("requested_reviewers_teams"):
        ok = False
        reports.append("official review requests remain: " + ", ".join(requested or ["team request"]))

    blocking = [item for item in reviews if item.get("state") == "REQUEST_CHANGES"]
    pending = [
        item
        for item in reviews
        if item.get("state") in {"PENDING", "REQUEST_REVIEW"}
    ]
    if blocking:
        ok = False
        reports.append("active exact-head REQUEST_CHANGES review remains")
    if pending:
        ok = False
        reports.append("exact-head review is PENDING")

    approved_by = {
        item.get("user", {}).get("login")
        for item in reviews
        if item.get("state") == "APPROVED"
    }
    missing = [name for name in required if name not in approved_by]
    if missing:
        ok = False
        reports.append("missing exact-head formal approval from: " + ", ".join(missing))

    status = api_request("GET", f"/repos/{repo}/commits/{head}/status")
    statuses = status.get("statuses") or []
    ignored = {
        "Repository Review Policy / review-gate",
        "Repository Review Policy / autopilot-merge",
    }
    ci = [
        item
        for item in statuses
        if not any(item.get("context", "").startswith(prefix) for prefix in ignored)
        and item.get("status") != "skipped"
    ]
    if not ci:
        ok = False
        reports.append("no completed exact-head CI status is available")
    else:
        failures = [item["context"] for item in ci if item.get("status") != "success"]
        if failures:
            ok = False
            reports.append("exact-head CI is not fully successful: " + ", ".join(failures))

    report = "ready" if ok else "blocked: " + "; ".join(reports)
    print(f"head={head}")
    print(f"sensitive={str(is_sensitive).lower()}")
    print("required_reviewers=" + ",".join(required))
    print(report)
    return ok, report, {"head": head, "sensitive": is_sensitive, "required": required}


def assign(repo: str, number: str) -> None:
    rules = policy()
    pr = pull_request(repo, number)
    files = changed_files(repo, number)
    required, _ = required_reviewers(pr, files, rules)
    current = {item["login"] for item in pr.get("assignees") or []}
    desired = sorted(current | set(required))
    if pr.get("user", {}).get("login") in desired:
        desired.remove(pr["user"]["login"])
    api_request("PATCH", f"/repos/{repo}/issues/{number}", {"assignees": desired})
    print("assigned=" + ",".join(desired))


def merge(repo: str, number: str) -> None:
    ready, report, details = evaluate(repo, number)
    if not ready:
        raise SystemExit(report)
    response = api_request(
        "POST",
        f"/repos/{repo}/pulls/{number}/merge",
        {
            "do": "merge",
            "head_commit_id": details["head"],
            "force_merge": False,
            "merge_when_checks_succeed": False,
            "delete_branch_after_merge": False,
            "merge_title_field": "Autopilot merge after exact-head review gates",
            "merge_message_field": "All configured review, CI, branch-state, and human-gate predicates passed.",
        },
    )
    print(json.dumps(response or {}, sort_keys=True))


def scan(repo: str) -> None:
    pulls = api_request("GET", f"/repos/{repo}/pulls?state=open&limit=100")
    if not isinstance(pulls, list):
        raise SystemExit("Gitea pulls response was not a list")
    for pr in pulls:
        number = str(pr["number"])
        try:
            ready, report, details = evaluate(repo, number)
            set_status(repo, details["head"], "success" if ready else "failure", report)
            if ready:
                merge(repo, number)
        except SystemExit as exc:
            print(f"PR #{number}: {exc}")


def set_status(repo: str, sha: str, state: str, description: str) -> None:
    api_request(
        "POST",
        f"/repos/{repo}/statuses/{sha}",
        {
            "state": state,
            "context": "Repository Review Policy / review-gate",
            "description": description[:140],
            "target_url": os.environ.get("GITHUB_SERVER_URL", "https://git.ocean"),
        },
    )


def main() -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "scan":
        scan(repo)
        return 0
    number = os.environ["PR_NUMBER"]
    if mode == "assign":
        assign(repo, number)
    elif mode == "merge":
        merge(repo, number)
    elif mode == "status":
        ready, report, details = evaluate(repo, number)
        set_status(repo, details["head"], "success" if ready else "failure", report)
        return 0 if ready else 1
    elif mode == "check":
        ready, _, _ = evaluate(repo, number)
        return 0 if ready else 1
    else:
        raise SystemExit(f"unknown mode: {mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
