#!/usr/bin/env python3
"""Validate the machine-readable autonomy operation contract."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import NoReturn

REQUIRED = {"intent_id", "contract_version", "status", "routing", "success_probes", "operations"}
CLEARANCE_LADDER = {"CL0", "CL1", "CL2", "CL3", "CL4", "CL5"}
FIELDS = {"id", "clearance", "decision_authority", "target_scope", "owner_route", "executor", "independent_verifier", "exception_policy", "normal_autonomy", "notify_after", "ask_before", "stop_conditions", "rollback", "verification", "idempotent"}
DECISION_AUTHORITIES = {"standing-delegation", "methodical-skeptic", "affected-agent-human-or-resource-owner", "instance-governance-authority"}
EXECUTOR_BINDINGS = {"declared-agent", "human-only", "deterministic-service"}
ROUTING_ROLES = {"affected_agent_human", "affected_resource_owner", "fleet_operator", "methodical_skeptic"}
FLEET_SCOPE_VALUES = {"fleet-wide", "cross-owner", "identity", "authority", "kill-chain"}

def fail(message: str) -> NoReturn:
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
    routing = data["routing"]
    if not isinstance(routing, dict) or routing.get("version") != 1:
        fail("routing.version must be 1")
    roles = routing.get("authority_roles")
    if not isinstance(roles, list) or not ROUTING_ROLES.issubset(roles):
        fail(f"routing.authority_roles must include: {', '.join(sorted(ROUTING_ROLES))}")
    if routing.get("unresolved_owner_route") != "fleet_operator":
        fail("unresolved_owner_route must be fleet_operator")
    scopes = routing.get("fleet_scope_values")
    if not isinstance(scopes, list) or not FLEET_SCOPE_VALUES.issubset(scopes):
        fail(f"routing.fleet_scope_values must include: {', '.join(sorted(FLEET_SCOPE_VALUES))}")
    rules = routing.get("clearance_rules")
    if not isinstance(rules, dict):
        fail("routing.clearance_rules must be an object")
    for clearance in ("CL3", "CL4", "CL5"):
        if clearance not in rules or not isinstance(rules[clearance], dict):
            fail(f"routing.clearance_rules missing {clearance}")
    if rules["CL3"].get("reviewer") != "methodical_skeptic":
        fail("CL3 reviewer must be methodical_skeptic")
    if rules["CL4"].get("fleet_override") != "fleet_operator":
        fail("CL4 fleet_override must be fleet_operator")
    if rules["CL4"].get("decision_authority") != "affected-agent-human-or-resource-owner":
        fail("CL4 decision_authority must be affected-agent-human-or-resource-owner")
    if rules["CL4"].get("execution") != "operation-binding":
        fail("CL4 execution must be resolved from the operation binding")
    if rules["CL5"].get("decision_authority") != "instance-defined":
        fail("CL5 decision_authority must be instance-defined")
    if rules["CL5"].get("execution") != "operation-binding":
        fail("CL5 execution must be resolved from the operation binding")
    if rules["CL5"].get("duet") != "prepare-review-verify-only":
        fail("CL5 duet must be prepare-review-verify-only")

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
        for key in ("owner_route", "executor", "independent_verifier", "exception_policy"):
            if not isinstance(operation[key], str) or not operation[key]:
                fail(f"operation {operation['id']} {key} must be non-empty")
        if not isinstance(operation["decision_authority"], str) or not operation["decision_authority"]:
            fail(f"operation {operation['id']} decision_authority must be non-empty")
        if operation["decision_authority"] not in DECISION_AUTHORITIES:
            fail(f"operation {operation['id']} decision_authority must be one of: {', '.join(sorted(DECISION_AUTHORITIES))}")
        if operation["executor"] not in EXECUTOR_BINDINGS:
            fail(f"operation {operation['id']} executor must be one of: {', '.join(sorted(EXECUTOR_BINDINGS))}")
        if operation["clearance"] == "CL5" and operation["decision_authority"] != "instance-governance-authority":
            fail(f"operation {operation['id']} CL5 decision_authority must be instance-governance-authority")
        if operation["clearance"] == "CL4":
            if operation["decision_authority"] != "affected-agent-human-or-resource-owner":
                fail(f"operation {operation['id']} CL4 decision_authority must be affected-agent-human-or-resource-owner")
            if operation["owner_route"] not in {"affected-agent-human", "affected-resource-owner", "fleet-operator"}:
                fail(f"operation {operation['id']} CL4 owner_route must resolve to an affected owner or fleet-operator")
        if operation["clearance"] == "CL3" and operation["independent_verifier"] != "methodical-skeptic":
            fail(f"operation {operation['id']} CL3 independent_verifier must be methodical-skeptic")
        if operation["normal_autonomy"]:
            if operation["executor"] == "human-only":
                fail(f"operation {operation['id']} cannot be normal_autonomy with human-only executor")
            if operation["clearance"] != "CL2":
                fail(f"operation {operation['id']} has normal autonomy but clearance {operation['clearance']} (only CL2 may act first)")
            for key in ("ask_before", "stop_conditions", "verification"):
                if not operation[key]:
                    fail(f"operation {operation['id']} has normal autonomy but empty {key}")
    print(f"OK: {path} operations={len(operations)} probes={len(data['success_probes'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
