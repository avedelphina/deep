#!/usr/bin/env python3
"""Validate the machine-readable autonomy operation contract."""
from __future__ import annotations
import json
import sys
from pathlib import Path

REQUIRED = {"intent_id", "contract_version", "status", "success_probes", "operations"}
CLEARANCE_LADDER = {"CL0", "CL1", "CL2", "CL3", "CL4", "CL5"}
FIELDS = {"id", "clearance", "target_scope", "normal_autonomy", "notify_after", "ask_before", "stop_conditions", "rollback", "verification", "idempotent"}

def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "intents/infrastructure-autonomy.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")
    missing = REQUIRED - data.keys()
    if missing:
        fail(f"missing top-level fields: {', '.join(sorted(missing))}")
    if not isinstance(data["success_probes"], list) or not data["success_probes"]:
        fail("success_probes must be non-empty")
    operations = data["operations"]
    if not isinstance(operations, list) or not operations:
        fail("operations must be non-empty")
    allowed = {"restart_affected_service", "renew_expiring_certificate", "remove_expired_rotated_logs", "retry_failed_backup", "repair_declared_reversible_drift"}
    unknown = {item.get("id") for item in operations} - allowed
    if unknown:
        fail(f"unknown operation ids: {', '.join(sorted(unknown))}")
    ids = set()
    for operation in operations:
        missing = FIELDS - operation.keys()
        if missing:
            fail(f"operation {operation.get('id', '<unknown>')} missing: {', '.join(sorted(missing))}")
        if operation["id"] in ids:
            fail(f"duplicate operation id: {operation['id']}")
        ids.add(operation["id"])
        if operation["clearance"] not in CLEARANCE_LADDER:
            fail(f"operation {operation['id']} clearance {operation['clearance']!r} is not on the ladder CL0-CL5")
        if not isinstance(operation["normal_autonomy"], bool):
            fail(f"operation {operation['id']} normal_autonomy must be a boolean")
        for key in ("ask_before", "stop_conditions", "verification"):
            if not isinstance(operation[key], list):
                fail(f"operation {operation['id']} field {key} must be a list")
        if operation["normal_autonomy"]:
            if operation["clearance"] != "CL2":
                fail(f"operation {operation['id']} has normal autonomy but clearance {operation['clearance']} (only CL2 may act first)")
            for key in ("ask_before", "stop_conditions", "verification"):
                if not operation[key]:
                    fail(f"operation {operation['id']} has normal autonomy but empty {key}")
    print(f"OK: {path} operations={len(operations)} probes={len(data['success_probes'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
