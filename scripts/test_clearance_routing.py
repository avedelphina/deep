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
    invalid_routing["routing"]["clearance_rules"]["CL5"]["agent_execution"] = "allowed"
    expect_rejected(AUTONOMY_VALIDATOR, invalid_routing, "CL5 agent execution")

    opaque_exception = copy.deepcopy(infrastructure)
    opaque_exception["escalation"]["required_fields"] = ["reason", "unblock_action", "deadline"]
    expect_rejected(INFRA_VALIDATOR, opaque_exception, "opaque exception packet")

    legacy_exception = copy.deepcopy(infrastructure)
    legacy_exception["escalation"]["required_fields"].append("reason")
    expect_rejected(INFRA_VALIDATOR, legacy_exception, "legacy exception field")

    print("OK: clearance routing negative fixtures rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
