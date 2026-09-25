# DEEP Infrastructure Operations Workflow

**Status:** Framework v1.0
**Owner:** the infrastructure-class operator agent (named per instance)
**Scope:** Hosts, operating systems, networking, DNS, access paths, storage, resources, backups, certificates, and infrastructure drift

## 1. Purpose

The infrastructure operator owns an operational intent, not a ticket queue:

> The DEEP infrastructure is secure, reachable, recoverable, sufficiently resourced, and capable of supporting its declared services.

The workflow keeps that intent fulfilled continuously. Automation performs repeatable checks and bounded repairs. The operator agent spends model attention on exceptions, diagnosis, prioritisation, intent changes, and improving the automation loop.

The workflow is deliberately thin. It does not require every routine action to pass through a central approval or operation gateway. It requires the automation and evidence path to be explicit, bounded, and independently observable.

## 2. Scope and boundaries

The infrastructure operator owns:

- host reachability through approved access paths;
- OS support level, security updates, reboot state, and system services;
- CPU, memory, swap, storage, and inode capacity;
- networking, DNS, certificates, overlay/access infrastructure;
- backup freshness, backup failure, and restore-test evidence;
- host configuration drift and the automation that detects it;
- hosts without a resident specialist agent.

A separate container/runtime operator (also infrastructure class) owns the container/application-runtime intent: container images, compose stacks, container dependencies, feature capability, and user-facing runtime health. If a container problem requires host, storage, network, or access work, the runtime operator raises an infrastructure exception to the infrastructure operator, who remains accountable for the infrastructure outcome.

## 3. Intent hierarchy and linkage

This workflow fulfils the catalog entry `infrastructure-availability`, a
service intent with parent domains `I1`, `I2`, `I3`, `I5`, `I6`, and `I7`.
The catalog owns identity, parentage, and lifecycle; this document and
`intents/infrastructure.json` own the explanatory and operational contract.

## 4. Versioned operational intent

The canonical intent is the machine-readable manifest in
`intents/infrastructure.json`. The explanatory contract and thresholds belong
in the same pull request as changes to the manifest, probes, schedules, or
runbooks.

Every intent declares:

- owner and scope;
- health dimensions and thresholds;
- required probes;
- permitted automation and escalation;
- reporting and evidence requirements.

A change to the intent is a PR. The infrastructure operator is the required operational reviewer. CI must identify the affected probes, schedules, hosts, thresholds, and runbooks; the operator does not need to reread the entire repository every day.

## 5. Normal operating loop

```text
versioned intent
      ↓
host-local / scheduled probes
      ↓
healthy → structured evidence, no model run
      ↓
drift or failure
      ↓
operator receives an exception summary
      ↓
bounded automation repairs safe cases
      ↓
fresh verification
      ↓
fulfilled / deferred with deadline / escalated / intent amendment
```

### 5.1 Scheduled sweep

A deterministic scheduler runs the infrastructure sweep on the declared
cadence. The sweep must use locks, bounded timeouts, structured output, and
non-zero failure status. It checks at least:

- approved access-path reachability;
- OS package state and reboot-required status;
- failed system services;
- CPU, memory, swap, disk, and inode pressure;
- certificates and machine identities approaching expiry;
- critical DNS names from approved resolver paths;
- backup freshness and last restore-test result;
- configuration drift and scheduler failures;
- the age and result of the last successful maintenance run.

Healthy results are recorded without creating conversational work. Only
exceptions wake the operator agent or create/update an operational record.

### 5.2 Exception handling

The operator classifies each exception:

- **repairable:** an approved bounded automation can correct it;
- **diagnostic:** the cause is unclear and requires investigation;
- **blocked:** access, approval, backup, registry, or dependency prevents safe work;
- **cross-domain:** the issue belongs to the runtime operator, Coding, Business, or another owner;
- **intent conflict:** the declared target is unsafe, impossible, or no longer appropriate.

The operator must produce one of:

- repaired and freshly verified;
- safely deferred with reason, owner, and deadline;
- escalated with a named unblock action;
- cross-domain handoff with the infrastructure dependency explicit;
- proposed intent amendment.

"Ticket created" is not an outcome.

### 5.3 Safe automation

Routine operations should be executable without model reasoning:

- package metadata and security-update checks;
- bounded OS updates within policy;
- certificate renewal;
- approved cleanup;
- backup retry;
- service restart after a validated change;
- drift reconciliation;
- post-change probes.

Each operation must define target scope, authority, idempotence, concurrency
behaviour, timeout/retry semantics, rollback or recovery, structured output,
and an independent verification probe. The agent designs and improves these
operations; it does not manually imitate them every day.

### 5.4 Maintenance change

For a planned or automatically authorised change:

1. Capture current state and a rollback/snapshot reference where required.
2. Acquire a per-target maintenance lock.
3. Execute one bounded operation against one target or explicitly safe batch.
4. Restart only affected services.
5. Probe the effective result from a fresh process or independent client.
6. Record before/after versions, evidence, result, and rollback reference.
7. Reopen, rollback, or escalate on failed verification.

High-risk or irreversible changes follow the applicable DEEP tier and four-eyes
rule. Routine reversible housekeeping does not need a ceremonial second agent;
it does need an independent automated verification or fresh probe.

## 6. Intent changes and CI

Intent changes are reviewed like code:

```text
intent / probe / schedule PR
      ↓
manifest and reference validation
      ↓
impact report
      ↓
operator review (infrastructure class)
      ↓
merge
      ↓
post-merge baseline sweep
      ↓
exception queue or fulfilled intent
```

CI should reject or flag:

- unknown assets, probes, or automation IDs;
- missing owner, scope, threshold, or escalation;
- thresholds without a measurement path;
- changed probes without tests or a schedule;
- schedules without timeout/lock/failure semantics;
- automation without independent verification;
- intent changes that immediately leave declared assets non-compliant without a migration plan.

After merge, the affected probes run once to establish a baseline. If the new
intent exposes existing drift, the baseline creates a remediation queue; it
does not silently claim the fleet is compliant.

## 7. Daily operator rhythm

The operator does not reread the intent every morning.

- **Automated sweep:** probes all scoped assets and records healthy state.
- **Exception intake:** the operator receives only failures, drift, blocked
  work, and intent-impact notifications.
- **Diagnosis and repair:** the operator uses bounded automation where
  possible and reasons only about exceptions.
- **Verification:** fresh probes determine whether the intent is fulfilled.
- **Improvement:** recurring exceptions become automation, policy, or intent
  work rather than recurring prose.
- **Briefing:** a compact report states fulfilled coverage, degraded assets,
  repairs, blockers, and next actions.

## 8. Evidence contract

Every sweep or repair emits structured evidence containing:

- intent ID and version;
- target asset and scope;
- operation ID and implementation version;
- start and finish timestamps;
- actor or scheduler identity;
- observed before/after state;
- probe results;
- rollback or snapshot reference where applicable;
- result: fulfilled, degraded, blocked, or failed;
- next action and deadline for non-fulfilled results.

The agent may summarise evidence but must not substitute narrative for it.

## 9. Failure of the workflow

The infrastructure intent is considered degraded when the sweep is stale, the
scheduler is failing, evidence is missing, or declared assets cannot be
observed. This is itself an infrastructure exception. Silent absence of the
maintenance loop is not equivalent to healthy infrastructure.

Repeated manual intervention is an automation defect candidate. Repeated
blocked work is an access or ownership defect candidate. Repeated intent
violations are a policy or capacity defect candidate.

## 10. Initial implementation sequence

1. Commit and validate `intents/infrastructure.json`.
2. Implement a read-only sweep with structured JSON output.
3. Run it locally against one operator-owned host and one inaccessible-host case.
4. Add lock, timeout, scheduler, and alert behaviour.
5. Add bounded repair operations one at a time, beginning with low-risk tasks.
6. Run a real baseline and route only exceptions to the operator.
7. Add the container/runtime intent as a separate contract with explicit host dependencies.
