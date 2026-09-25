# Operations

> Fictional worked example. See [README](README.md).

The service runs as a closed loop:

```text
detect → snapshot/backup → bounded repair → restart affected services
→ fresh verification → evidence → fulfilled, deferred, or escalated
```

## Routine loop

A deterministic scheduler runs the service sweep every 30 minutes with
one-per-asset-group locking, bounded timeouts, structured output, and
non-zero failure status. Healthy results remain machine evidence; only
exceptions wake the owning agent.

The sweep checks endpoint reachability, the synthetic user-path probe,
process and service state on `<host-a>`, certificate validity, data-volume
backup freshness and last restore-test result, declared-vs-effective
configuration drift, and standby readiness on `<host-b>`.

## Safe automation

Approved operations for this example include: service restart after a
validated change, certificate renewal, backup retry, approved cleanup of
temporary artifacts, drift reconciliation for declared configuration keys,
and post-change probes. Each operation needs explicit target scope,
authority, idempotence, lock behaviour, timeout/retry semantics, recovery
path, structured output, and independent verification.

Failover from `<host-a>` to the standby on `<host-b>` is **not** safe
automation in this example: it is a T4 change (staged by agents, approved by
the human authority of record, executed and verified by agents).

## Exception handling

The owning agent classifies failures as repairable, diagnostic, blocked,
cross-domain, or intent conflict. The result is repaired and verified, safely
deferred with a deadline, escalated with a named unblock action, handed
across a declared boundary, or proposed as an intent amendment. "Ticket
created" is not a successful operation.

## Change rules

Routine reversible housekeeping may run without a ceremonial second agent,
but must have a fresh or independent verification probe. High-risk or
irreversible changes follow the applicable DEEP four-eyes rule (see
[`agent-classes-and-independent-gates.md`](../../docs/40-governance/agent-classes-and-independent-gates.md))
and require separate authority before execution.

## Canonical workflow

See
[`infrastructure-operations-workflow.md`](../../docs/40-governance/infrastructure-operations-workflow.md).
