#!/usr/bin/env python3
"""Validate inactive DEEP incident-envelope examples, not runtime authority."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import NoReturn

ENVELOPE_FIELDS = {
    "mode", "schema_version", "status", "envelope_id", "revision", "signature_ref",
    "preauthorising_authorities", "accountable_owner_ids", "activation_eligibility",
    "commander_eligibility", "executor_eligibility", "host_operator_eligibility",
    "trigger_conditions", "target_ids", "allowed_operation_ids", "operation_bindings",
    "incident_playbooks", "max_blast_radius", "max_action_count", "max_rate",
    "stop_conditions", "explicit_exclusions", "rollback_or_safe_stop",
    "required_local_capabilities", "network_dependency", "purser_dependency",
    "trusted_time_source", "not_before", "expires_at", "replay_guard",
    "local_evidence_sink", "reconciliation_route", "verification",
}
ACTIVATION_FIELDS = {
    "mode", "schema_version", "envelope_id", "envelope_revision", "grant_id",
    "incident_id", "activator", "commander", "accountable_owner_id",
    "decision_authority_id", "host_operator_id", "executor", "verifier",
    "observed_trigger", "trigger_evidence_ref", "target_ids", "allowed_operation_ids",
    "action_count", "issued_at", "expires_at", "replay_guard", "evidence_ref",
}
BINDING_FIELDS = {
    "operation_id", "target_revision", "accountable_owner_id", "decision_authority_id",
    "host_operator_id", "activator_may_execute", "target_ids", "executor_eligibility",
    "playbook_revision", "playbook_digest", "verifier", "rollback_or_safe_stop",
    "evidence_sink", "not_before", "expires_at",
}
PLAYBOOK_FIELDS = {"operation_id", "revision", "sha256"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"{path} must contain an object")
    return data


def timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        fail(f"{field} must be a non-empty timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{field} must be ISO-8601")
    if parsed.tzinfo is None:
        fail(f"{field} must include an explicit timezone")
    return parsed


def nonempty_string(data: dict, field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        fail(f"{field} must be a non-empty string")
    return value


def nonempty_list(data: dict, field: str) -> list[str]:
    value = data.get(field)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        fail(f"{field} must be a non-empty list of strings")
    if len(value) != len(set(value)):
        fail(f"{field} must not contain duplicates")
    return value


def exact_fields(value: object, required: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != required:
        fail(f"{label} must contain exactly: {', '.join(sorted(required))}")
    return value


def validate(envelope: dict, activation: dict, registered: dict, at: str) -> None:
    if set(envelope) != ENVELOPE_FIELDS:
        fail(f"envelope fields differ: missing={sorted(ENVELOPE_FIELDS - envelope.keys())}, unknown={sorted(envelope.keys() - ENVELOPE_FIELDS)}")
    if envelope["mode"] != "incident_response" or envelope["schema_version"] != 1:
        fail("envelope mode/schema_version must be incident_response/1")
    if envelope["status"] != "example-not-active":
        fail("this validator checks inactive examples only; installed-envelope authorization is not implemented")
    for field in ("envelope_id", "revision", "signature_ref", "max_blast_radius", "max_rate", "rollback_or_safe_stop", "purser_dependency", "trusted_time_source", "replay_guard", "local_evidence_sink", "reconciliation_route"):
        nonempty_string(envelope, field)
    if not envelope["signature_ref"].startswith("sha256:") or not SHA256.fullmatch(envelope["signature_ref"][7:]):
        fail("example signature_ref must be sha256:<64 lowercase hex chars>")

    start = timestamp(envelope["not_before"], "envelope not_before")
    end = timestamp(envelope["expires_at"], "envelope expires_at")
    if start >= end:
        fail("envelope not_before must precede expires_at")
    observed_now = timestamp(at, "--at (explicit example-validation clock)")
    if not start <= observed_now < end:
        fail("example validation clock is outside envelope validity")

    list_fields = (
        "preauthorising_authorities", "accountable_owner_ids", "activation_eligibility",
        "commander_eligibility", "executor_eligibility", "host_operator_eligibility",
        "trigger_conditions", "target_ids", "allowed_operation_ids", "stop_conditions",
        "explicit_exclusions", "required_local_capabilities", "verification",
    )
    for field in list_fields:
        nonempty_list(envelope, field)
    if envelope["network_dependency"] not in {"none", "reconciliation-only"}:
        fail("network_dependency must be none or reconciliation-only")
    if envelope["trusted_time_source"] not in {"local-trusted-time", "attested-trusted-time"}:
        fail("trusted_time_source must name a supported trusted-time mode")
    if type(envelope["max_action_count"]) is not int or envelope["max_action_count"] < 1:
        fail("max_action_count must be a positive integer")
    if envelope["max_rate"] != "one action per activation":
        fail("max_rate must be the explicitly supported 'one action per activation' bound")

    registered_operations = registered.get("operations")
    if not isinstance(registered_operations, list):
        fail("registered autonomy contract operations must be a list")
    registered_ids = {item.get("id") for item in registered_operations if isinstance(item, dict)}
    if set(envelope["allowed_operation_ids"]) - registered_ids:
        fail("envelope references an operation absent from the autonomy contract")

    playbooks = envelope["incident_playbooks"]
    if not isinstance(playbooks, list) or not playbooks:
        fail("incident_playbooks must be a non-empty list")
    playbook_by_key: dict[tuple[str, str], dict] = {}
    for raw in playbooks:
        playbook = exact_fields(raw, PLAYBOOK_FIELDS, "incident playbook record")
        op = nonempty_string(playbook, "operation_id")
        revision = nonempty_string(playbook, "revision")
        digest = nonempty_string(playbook, "sha256")
        if not SHA256.fullmatch(digest):
            fail(f"incident playbook {op}/{revision} sha256 must be 64 lowercase hex chars")
        key = (op, revision)
        if key in playbook_by_key:
            fail(f"duplicate incident playbook record {op}/{revision}")
        playbook_by_key[key] = playbook

    raw_bindings = envelope["operation_bindings"]
    if not isinstance(raw_bindings, list) or not raw_bindings:
        fail("operation_bindings must be a non-empty list")
    binding_by_id: dict[str, dict] = {}
    for raw in raw_bindings:
        binding = exact_fields(raw, BINDING_FIELDS, "operation binding")
        operation_id = nonempty_string(binding, "operation_id")
        if operation_id in binding_by_id:
            fail(f"duplicate operation binding {operation_id}")
        binding_by_id[operation_id] = binding
        for field in ("target_revision", "accountable_owner_id", "decision_authority_id", "host_operator_id", "playbook_revision", "playbook_digest", "verifier", "rollback_or_safe_stop", "evidence_sink"):
            nonempty_string(binding, field)
        if type(binding["activator_may_execute"]) is not bool:
            fail(f"operation binding {operation_id} activator_may_execute must be boolean")
        targets = nonempty_list(binding, "target_ids")
        executors = nonempty_list(binding, "executor_eligibility")
        if not set(targets).issubset(set(envelope["target_ids"])):
            fail(f"operation binding {operation_id} targets exceed envelope")
        if not set(executors).issubset(set(envelope["executor_eligibility"])):
            fail(f"operation binding {operation_id} executors exceed envelope")
        if binding["host_operator_id"] not in envelope["host_operator_eligibility"]:
            fail(f"operation binding {operation_id} host operator is not envelope-eligible")
        if binding["accountable_owner_id"] not in envelope["accountable_owner_ids"]:
            fail(f"operation binding {operation_id} accountable owner is not envelope-bound")
        if binding["decision_authority_id"] not in envelope["preauthorising_authorities"]:
            fail(f"operation binding {operation_id} decision authority is not a preauthorising authority")
        bstart = timestamp(binding["not_before"], f"{operation_id} not_before")
        bend = timestamp(binding["expires_at"], f"{operation_id} expires_at")
        if bstart >= bend or bstart < start or bend > end:
            fail(f"operation binding {operation_id} validity must fit inside envelope")
        if not bstart <= observed_now < bend:
            fail(f"example validation clock is outside operation {operation_id} validity")
        if not SHA256.fullmatch(binding["playbook_digest"]):
            fail(f"operation binding {operation_id} playbook_digest must be 64 lowercase hex chars")
        if playbook_by_key.get((operation_id, binding["playbook_revision"]), {}).get("sha256") != binding["playbook_digest"]:
            fail(f"operation binding {operation_id} playbook revision/digest is not in the example playbook registry")

    if set(binding_by_id) != set(envelope["allowed_operation_ids"]):
        fail("operation_bindings must cover exactly the allowed operation IDs")

    if set(activation) != ACTIVATION_FIELDS:
        fail(f"activation fields differ: missing={sorted(ACTIVATION_FIELDS - activation.keys())}, unknown={sorted(activation.keys() - ACTIVATION_FIELDS)}")
    if activation["mode"] != "incident_response" or activation["schema_version"] != 1:
        fail("activation mode/schema_version must be incident_response/1")
    for field in ("envelope_id", "envelope_revision", "grant_id", "incident_id", "activator", "commander", "accountable_owner_id", "decision_authority_id", "host_operator_id", "executor", "verifier", "observed_trigger", "trigger_evidence_ref", "replay_guard", "evidence_ref"):
        nonempty_string(activation, field)
    if activation["envelope_id"] != envelope["envelope_id"] or activation["envelope_revision"] != envelope["revision"]:
        fail("activation must reference the exact envelope revision")
    if activation["activator"] not in envelope["activation_eligibility"]:
        fail("activation principal is not envelope-eligible")
    if activation["commander"] not in envelope["commander_eligibility"]:
        fail("commander is not envelope-eligible")
    if activation["executor"] not in envelope["executor_eligibility"]:
        fail("executor is not envelope-eligible")
    if activation["host_operator_id"] not in envelope["host_operator_eligibility"]:
        fail("host operator is not envelope-eligible")
    if activation["observed_trigger"] not in envelope["trigger_conditions"]:
        fail("observed trigger is not one of the envelope's declared trigger conditions")
    target_ids = nonempty_list(activation, "target_ids")
    operation_ids = nonempty_list(activation, "allowed_operation_ids")
    if len(operation_ids) != 1:
        fail("one activation may select exactly one operation; issue separate action grants")
    if type(activation["action_count"]) is not int or activation["action_count"] != 1 or activation["action_count"] > envelope["max_action_count"]:
        fail("action_count must be exactly one and within the envelope limit")
    if activation["replay_guard"] == envelope["replay_guard"]:
        fail("activation replay_guard must be distinct from the envelope replay identifier")

    operation_id = operation_ids[0]
    if operation_id not in envelope["allowed_operation_ids"]:
        fail("activation operation is outside the envelope")
    binding = binding_by_id[operation_id]
    if not set(target_ids).issubset(set(binding["target_ids"])):
        fail(f"activation targets exceed operation binding {operation_id}")
    if activation["accountable_owner_id"] != binding["accountable_owner_id"]:
        fail("activation accountable owner must exactly match the selected operation binding")
    if activation["decision_authority_id"] != binding["decision_authority_id"]:
        fail("activation decision authority must exactly match the selected operation binding")
    if activation["host_operator_id"] != binding["host_operator_id"]:
        fail("activation host operator must exactly match the selected operation binding")
    if activation["executor"] not in binding["executor_eligibility"]:
        fail("activation executor is not eligible for the selected operation")
    if activation["verifier"] != binding["verifier"]:
        fail("activation verifier must exactly match the selected operation binding")
    if activation["activator"] == activation["executor"] and not binding["activator_may_execute"]:
        fail("activator cannot execute unless the selected operation explicitly permits it")

    roles = {
        "activator": activation["activator"], "commander": activation["commander"],
        "accountable owner": activation["accountable_owner_id"],
        "decision authority": activation["decision_authority_id"],
        "host operator": activation["host_operator_id"], "executor": activation["executor"],
        "verifier": activation["verifier"],
    }
    by_identity: dict[str, str] = {}
    for role, identity in roles.items():
        if identity in by_identity:
            pair = f"{by_identity[identity]} and {role}"
            if {by_identity[identity], role} == {"activator", "executor"} and binding["activator_may_execute"]:
                continue
            fail(f"role identity overlap is not permitted: {pair}")
        by_identity[identity] = role

    issued = timestamp(activation["issued_at"], "activation issued_at")
    grant_expires = timestamp(activation["expires_at"], "activation expires_at")
    if issued >= grant_expires or issued < start or grant_expires > end:
        fail("activation validity must fit inside envelope validity")
    bstart = timestamp(binding["not_before"], f"{operation_id} not_before")
    bend = timestamp(binding["expires_at"], f"{operation_id} expires_at")
    if issued < bstart or grant_expires > bend:
        fail("activation validity must fit inside operation validity")
    if issued > observed_now or observed_now >= grant_expires:
        fail("explicit example-validation clock is outside activation validity")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("envelope", type=Path)
    parser.add_argument("activation", type=Path)
    parser.add_argument("autonomy", type=Path)
    parser.add_argument("--at", required=True, help="explicit deterministic clock used only to validate the inactive example")
    args = parser.parse_args()
    validate(load(args.envelope), load(args.activation), load(args.autonomy), args.at)
    print(f"OK: {args.envelope} inactive example schema and binding consistency valid; no runtime authority verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
