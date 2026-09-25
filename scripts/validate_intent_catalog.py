#!/usr/bin/env python3
"""Validate the DEEP intent catalog and its hierarchy."""
from __future__ import annotations

import json
import sys
from pathlib import Path

KINDS = {"master", "domain", "service", "engagement", "change"}
STATUSES = {"draft", "proposed", "active", "amended", "paused", "completed", "retired"}
ROOT_ID = "master"  # canonical ID of the single root master intent


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "intents/intent-catalog.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")

    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        fail("entries must be a non-empty array")

    by_id = {}
    for entry in entries:
        for key in ("id", "kind", "status", "outcome", "owner", "parent_ids", "source"):
            if key not in entry:
                fail(f"entry missing {key}: {entry}")
        ident = entry["id"]
        if not isinstance(ident, str) or not ident or ident in by_id:
            fail(f"entry IDs must be unique non-empty strings: {ident!r}")
        if entry["kind"] not in KINDS:
            fail(f"invalid kind for {ident}: {entry['kind']}")
        if entry["status"] not in STATUSES:
            fail(f"invalid status for {ident}: {entry['status']}")
        if not isinstance(entry["parent_ids"], list) or len(set(entry["parent_ids"])) != len(entry["parent_ids"]):
            fail(f"parent_ids must be a unique array for {ident}")
        by_id[ident] = entry

    roots = [e for e in entries if e["kind"] == "master"]
    if len(roots) != 1 or roots[0]["id"] != ROOT_ID or roots[0]["parent_ids"]:
        fail(f"catalog must have exactly one root master intent: {ROOT_ID}")

    for ident, entry in by_id.items():
        for parent in entry["parent_ids"]:
            if parent not in by_id:
                fail(f"{ident} references unknown parent {parent}")
        if entry["kind"] == "master" and entry["parent_ids"]:
            fail(f"master intent {ident} cannot have parents")
        if entry["kind"] != "master" and not entry["parent_ids"]:
            fail(f"non-master intent {ident} must have a parent")
        if entry["kind"] in {"service", "engagement", "change"} and not entry.get("manifest") and entry["status"] == "active":
            fail(f"active operational intent {ident} requires a manifest")
        manifest = entry.get("manifest")
        if manifest:
            try:
                manifest_data = json.loads(Path(manifest).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                fail(f"cannot read manifest for {ident}: {exc}")
            if manifest_data.get("id") != ident:
                fail(f"manifest ID mismatch for {ident}: {manifest_data.get('id')!r}")

    def reaches_root(ident: str, seen: tuple[str, ...] = ()) -> bool:
        if ident in seen:
            fail(f"cycle in intent ancestry: {' -> '.join((*seen, ident))}")
        entry = by_id[ident]
        return ident == ROOT_ID or any(reaches_root(parent, (*seen, ident)) for parent in entry["parent_ids"])

    for ident in by_id:
        reaches_root(ident)

    print(f"OK: {path} entries={len(entries)} root={ROOT_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
