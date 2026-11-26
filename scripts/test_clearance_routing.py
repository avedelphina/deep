#!/usr/bin/env python3
"""Exercise the clearance and exception validators at their real file boundary."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTONOMY = ROOT / "intents/infrastructure-autonomy.json"
INFRA = ROOT / "intents/infrastructure.json"
AUTONOMY_VALIDATOR = ROOT / "scripts/validate_autonomy_contract.py"
INFRA_VALIDATOR = ROOT / "scripts/validate_infrastructure_intent.py"
INCIDENT_VALIDATOR = ROOT / "scripts/validate_incident_envelope.py"
INCIDENT_ENVELOPE = ROOT / "intents/incident-envelope.example.json"
INCIDENT_ACTIVATION = ROOT / "intents/incident-activation.example.json"


def run(validator: Path, payload: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fixture.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(validator), str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )


def expect_rejected(validator: Path, payload: dict, label: str) -> None:
    result = run(validator, payload)
    if result.returncode == 0:
        raise AssertionError(f"{label}: malformed fixture was accepted")


def main() -> int:
    autonomy = json.loads(AUTONOMY.read_text(encoding="utf-8"))
    infrastructure = json.loads(INFRA.read_text(encoding="utf-8"))

    for operation in autonomy["operations"]:
        missing_route = copy.deepcopy(autonomy)
        del missing_route["operations"][autonomy["operations"].index(operation)]["owner_route"]
        expect_rejected(AUTONOMY_VALIDATOR, missing_route, f"{operation['id']} owner route")

    invalid_routing = copy.deepcopy(autonomy)
    invalid_routing["routing"]["clearance_rules"]["CL5"]["decision_authority"] = "affected-agent-human-or-resource-owner"
    expect_rejected(AUTONOMY_VALIDATOR, invalid_routing, "CL5 decision authority")

    invalid_cl5_binding = copy.deepcopy(autonomy)
    cl5 = invalid_cl5_binding["operations"][0]
    cl5.update(clearance="CL5", decision_authority="instance-governance-authority", executor="declared-agent", normal_autonomy=False)
    result = run(AUTONOMY_VALIDATOR, invalid_cl5_binding)
    if result.returncode != 0:
        raise AssertionError(f"CL5 agent executor should be allowed by an explicit operation binding: {result.stderr}")

    missing_cl5_authority = copy.deepcopy(invalid_cl5_binding)
    missing_cl5_authority["operations"][0]["decision_authority"] = "standing-delegation"
    expect_rejected(AUTONOMY_VALIDATOR, missing_cl5_authority, "CL5 missing instance authority")

    opaque_exception = copy.deepcopy(infrastructure)
    opaque_exception["escalation"]["required_fields"] = ["reason", "unblock_action", "deadline"]
    expect_rejected(INFRA_VALIDATOR, opaque_exception, "opaque exception packet")

    legacy_exception = copy.deepcopy(infrastructure)
    legacy_exception["escalation"]["required_fields"].append("reason")
    expect_rejected(INFRA_VALIDATOR, legacy_exception, "legacy exception field")

    envelope = json.loads(INCIDENT_ENVELOPE.read_text(encoding="utf-8"))
    activation = json.loads(INCIDENT_ACTIVATION.read_text(encoding="utf-8"))
    command = [sys.executable, str(INCIDENT_VALIDATOR), str(INCIDENT_ENVELOPE), str(INCIDENT_ACTIVATION), str(AUTONOMY)]
    result = subprocess.run(command + ["--at", "2026-11-26T12:30:00Z"], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise AssertionError(f"separate activator/executor example should validate: {result.stderr}")

    def reject_incident(mutated_envelope: dict, mutated_activation: dict, label: str, at: str = "2026-11-26T12:30:00Z") -> None:
        with tempfile.TemporaryDirectory() as directory:
            envelope_path = Path(directory) / "envelope.json"
            activation_path = Path(directory) / "activation.json"
            envelope_path.write_text(json.dumps(mutated_envelope), encoding="utf-8")
            activation_path.write_text(json.dumps(mutated_activation), encoding="utf-8")
            rejected = subprocess.run(
                [sys.executable, str(INCIDENT_VALIDATOR), str(envelope_path), str(activation_path), str(AUTONOMY), "--at", at],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            if rejected.returncode == 0:
                raise AssertionError(f"{label}: invalid incident grant was accepted")

    bad = copy.deepcopy(activation)
    bad["activator"] = "not-envelope-eligible"
    reject_incident(envelope, bad, "ineligible activator")
    bad = copy.deepcopy(activation)
    bad["commander"] = "not-commander-eligible"
    reject_incident(envelope, bad, "ineligible commander")
    bad_envelope = copy.deepcopy(envelope)
    bad_activation = copy.deepcopy(activation)
    bad_envelope["executor_eligibility"].append("agent-activator-a")
    bad_envelope["operation_bindings"][0]["executor_eligibility"].append("agent-activator-a")
    bad_activation["activator"] = "agent-activator-a"
    bad_activation["executor"] = "agent-activator-a"
    reject_incident(bad_envelope, bad_activation, "unauthorized self-execution")
    bad = copy.deepcopy(activation)
    bad["executor"] = "not-operation-eligible"
    reject_incident(envelope, bad, "executor not operation-bound")
    bad = copy.deepcopy(activation)
    bad["verifier"] = "wrong-verifier"
    reject_incident(envelope, bad, "operation verifier mismatch")
    bad = copy.deepcopy(activation)
    bad["action_count"] = 2
    reject_incident(envelope, bad, "action count overflow")
    bad = copy.deepcopy(activation)
    bad["expires_at"] = "2026-11-26T12:15:00Z"
    reject_incident(envelope, bad, "expired activation")
    bad = copy.deepcopy(activation)
    bad["target_ids"] = ["service/outside-envelope"]
    reject_incident(envelope, bad, "target expansion")
    bad = copy.deepcopy(activation)
    bad["replay_guard"] = envelope["replay_guard"]
    reject_incident(envelope, bad, "reused replay guard")
    reject_incident(envelope, activation, "expired envelope", "2100-01-01T00:00:00Z")

    invalid_autonomy = copy.deepcopy(autonomy)
    invalid_autonomy["operations"][0]["executor"] = "human-only"
    expect_rejected(AUTONOMY_VALIDATOR, invalid_autonomy, "autonomous human-only operation")

    print("OK: clearance routing and incident envelope negative fixtures rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
