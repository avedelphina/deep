# Intent contract

> Fictional worked example. See [README](README.md).

## Desired outcome

The example internal service is available, correct, and recoverable for its
declared users, within stated thresholds and without heroic intervention.

## Scope

The owning agent (Infrastructure class) keeps the service available on
`<host-a>` (primary) and maintains the cold standby path on `<host-b>`:
process health, listening endpoints, authentication reachability, storage the
service depends on, certificate validity for its endpoint, backup freshness of
its data volume, and drift between declared and effective configuration.

Application feature development, user account semantics, and functional
acceptance are separate responsibilities (Coding and Business classes). They
may raise dependencies or exceptions against this service but do not silently
change its boundaries.

## Healthy means

- the service endpoint on `<host-a>` answers and completes a synthetic
  user-path probe;
- authentication for the service works from an approved access path;
- the service's data volume has a fresh backup and a restore-test within the
  declared window;
- the endpoint certificate is valid beyond the warning threshold;
- declared configuration matches effective configuration, or the delta is a
  tracked change;
- the standby on `<host-b>` is provisioned and its promotion runbook is
  current.

## Degraded or blocked means

The service is degraded when a declared health condition fails, evidence is
stale, or the probe cannot observe a declared asset. It is blocked when safe
repair depends on unavailable access, approval, backup, registry, or another
owner. A blocked condition must include an unblock action, owner, deadline,
and evidence reference.

## Contract references

In a real instance, thresholds, automation, escalation fields, and the
evidence schema are maintained in a machine-readable manifest under
`intents/` (see [`intents/infrastructure.json`](../../intents/infrastructure.json)
for the canonical example). Changes to the outcome or boundaries require an
intent proposal or amendment; changes to implementation follow the service
operations workflow.
