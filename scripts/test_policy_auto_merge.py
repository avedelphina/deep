#!/usr/bin/env python3
"""Controlled, loopback-only tests for the policy auto-merge workflow.

The tests execute the actual embedded shell against a disposable TLS Gitea
double bound to 127.0.0.1.  They never use a real forge credential or target.
A token is a test fixture, not a deployment credential; all write endpoints
are denied unless the individual positive test explicitly enables them.

Run from the repository root:

    python3 scripts/test_policy_auto_merge.py

Dependencies: Python 3, curl, jq, and openssl.  This is a source and
logic test, not live forge authorization, least-privilege, or merge evidence.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import http.server
import json
import os
from pathlib import Path
import shutil
import ssl
import subprocess
import tempfile
import threading

FIXTURE_HEAD = "a" * 40
VALID_TOKEN = "loopback-only-fixture"
PR = 7
ROOT = "/api/v1/repos/ocean/deep-ocean"


def review(login, state="APPROVED", *, head=FIXTURE_HEAD, official=True,
           stale=False, dismissed=False):
    return {"user": {"login": login}, "state": state, "commit_id": head,
            "official": official, "stale": stale, "dismissed": dismissed}


def pull(*, reviewers=("alice",), head=FIXTURE_HEAD, state="open", draft=False,
         mergeable=True):
    return {"number": PR, "state": state, "draft": draft,
            "mergeable": mergeable, "base": {"ref": "main"},
            "head": {"sha": head},
            "requested_reviewers": [{"login": login} for login in reviewers]}


def statuses(*items, sha=FIXTURE_HEAD):
    return {"sha": sha, "statuses": [{"context": c, "status": s} for c, s in items]}


BASE = {
    "pulls": [pull()],
    "pr": pull(),
    "reviews": [review("alice")],
    "status": statuses(("test", "success"),
                       ("DEEP Policy Auto Merge / merge-eligible", "pending")),
}


class ForgeHandler(http.server.BaseHTTPRequestHandler):
    server_version = "LoopbackForge/1.0"

    def log_message(self, *_args):
        pass

    def _send(self, code, body):
        if code == 204:
            self.send_response(code)
            self.end_headers()
            return
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _handle(self):
        size = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(size) if size else b""
        call = {"method": self.command, "path": self.path,
                "auth": self.headers.get("Authorization"),
                "body": json.loads(raw) if raw else None}
        self.server.calls.append(call)
        if self.headers.get("Authorization") != f"token {VALID_TOKEN}":
            return self._send(401, {"message": "unauthorized"})
        path = self.path.split("?", 1)[0]
        if self.command != "GET" and not self.server.allow_mutations:
            # Denied writes are deliberate evidence.  Do not turn this into a
            # successful response or silently pretend the mutation occurred.
            return self._send(403, {"message": "loopback write denied"})
        if self.command == "GET" and path == f"{ROOT}/pulls":
            return self._send(200, self.server.state["pulls"])
        if self.command == "GET" and path == f"{ROOT}/pulls/{PR}":
            self.server.pr_reads += 1
            if self.server.pr_reads >= 3 and self.server.late_pr is not None:
                self.server.state["pr"] = copy.deepcopy(self.server.late_pr)
            return self._send(200, self.server.state["pr"])
        if self.command == "GET" and path == f"{ROOT}/pulls/{PR}/reviews":
            self.server.review_reads += 1
            if self.server.review_reads >= 2 and self.server.after_cleanup_reviews is not None:
                self.server.state["reviews"] = self.server.after_cleanup_reviews
            return self._send(200, self.server.state["reviews"])
        if self.command == "GET" and path == f"{ROOT}/commits/{FIXTURE_HEAD}/status":
            return self._send(200, self.server.state["status"])
        if self.command == "DELETE" and path == f"{ROOT}/pulls/{PR}/requested_reviewers":
            assert call["body"] == {"reviewers": ["alice"]}
            self.server.state["pr"]["requested_reviewers"] = []
            return self._send(204, None)
        if self.command == "POST" and path == f"{ROOT}/pulls/{PR}/merge":
            assert call["body"] == {"do": "squash", "head_commit_id": FIXTURE_HEAD,
                                     "delete_branch_after_merge": False,
                                     "merge_when_checks_succeed": False}
            self.server.state["pr"]["merged"] = True
            return self._send(200, {"merged": True})
        return self._send(404, {"message": "not found"})

    do_GET = _handle
    do_DELETE = _handle
    do_POST = _handle


def tls_certificate(root):
    """Create a throwaway CA and a SAN-valid loopback server certificate."""
    openssl = shutil.which("openssl")
    if not openssl:
        raise RuntimeError("openssl is required for the loopback TLS test")
    ca_key, ca_cert = root / "ca.key", root / "ca.crt"
    server_key, csr, server_cert = root / "server.key", root / "server.csr", root / "server.crt"
    ext = root / "server.ext"
    ext.write_text("subjectAltName=IP:127.0.0.1\n")
    subprocess.run([openssl, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                    "-days", "1", "-subj", "/CN=DEEP Loopback Test CA",
                    "-keyout", str(ca_key), "-out", str(ca_cert)],
                   check=True, capture_output=True)
    subprocess.run([openssl, "req", "-newkey", "rsa:2048", "-nodes",
                    "-subj", "/CN=127.0.0.1", "-keyout", str(server_key),
                    "-out", str(csr)], check=True, capture_output=True)
    subprocess.run([openssl, "x509", "-req", "-in", str(csr), "-CA", str(ca_cert),
                    "-CAkey", str(ca_key), "-CAcreateserial", "-days", "1",
                    "-extfile", str(ext), "-out", str(server_cert)],
                   check=True, capture_output=True)
    return ca_cert, server_cert, server_key


@contextlib.contextmanager
def run_forge(state, *, allow_mutations=False, after_cleanup_reviews=None, late_pr=None):
    with tempfile.TemporaryDirectory(prefix="policy-gate-tls-") as tmp:
        ca_cert, server_cert, server_key = tls_certificate(Path(tmp))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ForgeHandler)
        server.state = copy.deepcopy(state)
        server.calls = []
        server.allow_mutations = allow_mutations
        server.review_reads = 0
        server.pr_reads = 0
        server.late_pr = late_pr
        server.after_cleanup_reviews = after_cleanup_reviews
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(server_cert, server_key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server, ca_cert
        finally:
            server.shutdown()
            thread.join()
            server.server_close()


def execute(workflow, name, *, changes=None, token=VALID_TOKEN,
            allow_mutations=False, expect_exit=0, expect_writes=0,
            expect_output=None, expect_auth=True, after_cleanup_reviews=None, late_pr=None):
    state = copy.deepcopy(BASE)
    state.update(copy.deepcopy(changes or {}))
    with run_forge(state, allow_mutations=allow_mutations,
                   after_cleanup_reviews=after_cleanup_reviews, late_pr=late_pr) as (server, ca_cert):
        env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", ""),
               "BOT_TOKEN": token, "CURL_CA_BUNDLE": str(ca_cert),
               "API_ROOT": f"https://127.0.0.1:{server.server_port}{ROOT}"}
        proc = subprocess.run(["bash", "-c", workflow], env=env, text=True,
                              capture_output=True, timeout=30)
    writes = [call for call in server.calls if call["method"] != "GET"]
    result = {"name": name, "exit": proc.returncode,
              "stdout": proc.stdout, "stderr": proc.stderr,
              "write_count": len(writes), "writes": writes,
              "auth": sorted(set(call["auth"] for call in server.calls))}
    assert proc.returncode == expect_exit, result
    assert len(writes) == expect_writes, result
    if expect_output is not None:
        assert expect_output in proc.stdout + proc.stderr, result
    if expect_auth:
        assert result["auth"] == [f"token {token}"], result
    if name == "green eligible":
        assert [call["method"] for call in writes] == ["DELETE", "POST"], result
        merge_at = next(i for i, call in enumerate(server.calls) if call["method"] == "POST")
        preceding = [call["path"] for call in server.calls[:merge_at]]
        assert preceding.count(f"{ROOT}/pulls/{PR}") >= 3, result
        assert preceding.count(f"{ROOT}/pulls/{PR}/reviews?limit=100") >= 3, result
        assert len([path for path in preceding if path.startswith(f"{ROOT}/commits/{FIXTURE_HEAD}/status")]) >= 2, result
    return result


def validate_production_auth_source(path):
    """Assert the committed workflow binds the runtime token into its header."""
    lines = path.read_text().splitlines()
    auth_lines = [line for line in lines if "AUTH_HEADER=" in line]
    expected_auth = '          AUTH_HEADER="Authorization: token ${BOT_TOKEN}"'
    assert auth_lines == [expected_auth], auth_lines
    token_lines = [line for line in lines if line.startswith("      BOT_TOKEN:")]
    assert token_lines == ["      BOT_TOKEN: ${{ secrets.DEEP_MERGE_BOT_TOKEN }}"], token_lines
    assert any('test -n "${BOT_TOKEN:-}"' in line for line in lines)
    print("production auth source: BOT_TOKEN expansion is present")


def workflow_run_blocks(path):
    lines = path.read_text().splitlines()
    blocks = []
    for index, line in enumerate(lines):
        if not line.endswith("run: |"):
            continue
        base_indent = len(line) - len(line.lstrip(" "))
        block = []
        for child in lines[index + 1:]:
            if child.strip() and len(child) - len(child.lstrip(" ")) <= base_indent:
                break
            if child.strip():
                block.append(child[base_indent + 2:])
            else:
                block.append("")
        blocks.append("\n".join(block).rstrip() + "\n")
    return blocks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", nargs="?", type=Path,
                        default=Path(__file__).parents[1] / ".github/workflows/policy-auto-merge.yml")
    parser.add_argument("--json", type=Path, help="Write the complete non-secret case results here.")
    args = parser.parse_args()
    for command in ("curl", "jq", "openssl"):
        if not shutil.which(command):
            raise SystemExit(f"required command not found: {command}")
    blocks = workflow_run_blocks(args.workflow)
    assert len(blocks) == 1, "the gate must remain one self-contained tested shell block"
    workflow = blocks[0]
    validate_production_auth_source(args.workflow.parent / "policy-auto-merge.yml")
    cases = [
        ("placeholder is rejected", {"token": "***", "changes": {"pulls": [{"number": PR}]},
          "expect_exit": 1, "expect_output": ""}),
        ("supported secret expansion", {"changes": {"pr": pull(reviewers=()), "status": statuses()},
          "expect_output": "no exact-head CI contexts"}),
        ("no current approval", {"changes": {"reviews": []},
          "expect_output": "no current official Alice approval"}),
        ("current change request", {"changes": {"reviews": [review("alice"), review("bob", "REQUEST_CHANGES")]},
          "expect_output": "unresolved review"}),
        ("current pending review", {"changes": {"reviews": [review("alice"), review("bob", "PENDING")]},
          "expect_output": "unresolved review"}),
        ("current request-review", {"changes": {"reviews": [review("alice"), review("bob", "REQUEST_REVIEW")]},
          "expect_output": "unresolved review"}),
        ("unknown review state", {"changes": {"reviews": [review("alice"), review("bob", "FUTURE_STATE")]},
          "expect_output": "unknown review state"}),
        ("stale approval", {"changes": {"reviews": [review("alice", stale=True)]},
          "expect_output": "no current official Alice approval"}),
        ("dismissed approval", {"changes": {"reviews": [review("alice", dismissed=True)]},
          "expect_output": "no current official Alice approval"}),
        ("old-head approval", {"changes": {"reviews": [review("alice", head="old-head")]},
          "expect_output": "no current official Alice approval"}),
        ("requested human", {"changes": {"pr": pull(reviewers=("avedelphina",))},
          "expect_output": "human review requested"}),
        ("requested reviewer missing approval", {"changes": {"pr": pull(reviewers=("bob",))},
          "expect_output": "requested reviewer approval missing: bob"}),
        ("draft", {"changes": {"pr": pull(draft=True), "pulls": [pull(draft=True)]},
          "expect_output": "blocked, draft"}),
        ("missing CI", {"changes": {"pr": pull(reviewers=()), "status": statuses()},
          "expect_output": "no exact-head CI contexts"}),
        ("pending CI", {"changes": {"pr": pull(reviewers=()), "status": statuses(("test", "pending"))},
          "expect_output": "non-green exact-head CI"}),
        ("self pending only", {"changes": {"pr": pull(reviewers=()),
          "status": statuses(("DEEP Policy Auto Merge / merge-eligible", "pending"))},
          "expect_output": "no exact-head CI contexts"}),
        ("validation gate is not self", {"changes": {"pr": pull(reviewers=()),
          "status": statuses(("DEEP Policy Auto Merge Test / controlled-gate-test (pull_request)", "failure"))},
          "expect_output": "non-green exact-head CI"}),
        ("head mismatch CI", {"changes": {"pr": pull(reviewers=()),
          "status": statuses(("test", "success"), sha="different")},
          "expect_output": "status SHA mismatch"}),
        ("late blocking review", {"allow_mutations": True, "expect_writes": 1,
          "after_cleanup_reviews": [review("alice"), review("bob", "REQUEST_CHANGES")],
          "expect_output": "review state changed"}),
        ("late head change", {"allow_mutations": True, "expect_writes": 1,
          "late_pr": pull(reviewers=(), head="b" * 40),
          "expect_output": "head changed during evaluation"}),
        ("late unknown review", {"allow_mutations": True, "expect_writes": 1,
          "after_cleanup_reviews": [review("alice"), review("bob", "FUTURE_STATE")],
          "expect_output": "review state changed"}),
        ("green eligible", {"allow_mutations": True, "expect_writes": 2,
          "expect_output": f"merged by deep-merge-bot at head {FIXTURE_HEAD}"}),
        ("already clean and green", {"changes": {"pr": pull(reviewers=())},
          "allow_mutations": True, "expect_writes": 1,
          "expect_output": f"merged by deep-merge-bot at head {FIXTURE_HEAD}"}),
    ]
    results = [execute(workflow, name, **options) for name, options in cases]
    report = {"workflow": str(args.workflow), "mode": "loopback-only",
              "live_forge_writes": False, "live_token_scope_verified": False,
              "case_count": len(results), "passed": len(results), "cases": results}
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"PASS: {len(results)}/{len(cases)} controlled cases; no live forge or credential used")
    for result in results:
        print(f"  {result['name']}: exit={result['exit']} writes={result['write_count']}")


if __name__ == "__main__":
    main()
