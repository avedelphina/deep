# Autonomous Operation and Antifragile Improvement

**Status:** Framework v1.0
**Scope:** How an agent acts inside an active intent, learns from stress, and proposes improvements.

## 1. Purpose

DEEP is not a request-for-permission workflow. Agents are expected to operate autonomously inside a clearly declared intent. The control question is not "did somebody approve this command?" but:

> Is this action an ordinary way to fulfil the active intent, and can its result be observed and recovered?

When the answer is yes, the agent acts and records the result. When the action changes the intent's trade-offs or exceeds its declared boundaries, the agent stops and asks the owner to decide that trade-off.

The operating loop is:

```text
intent → act → observe → learn → propose → adapt → verify
```

A ticket is normally an audit and coordination record. It is not automatically a prior permission slip.

## 2. Three response modes

### 2.1 Act and record

The agent acts without waiting when all of these are true:

- an active intent explains the desired outcome;
- the action is a normal means of fulfilling that intent;
- the target and blast radius are understood;
- the action is reversible, contained, or covered by a recovery path;
- success and user outcome can be checked;
- the action does not change ownership, identity, durable data policy, or the intent's fundamental trade-off.

Afterwards the agent records what it observed, what it changed, why it fit the intent, the result, and the verification evidence.

### 2.2 Act, then notify

The agent still acts without waiting, but sends an immediate notification when the event has meaningful impact: an outage, degraded user outcome, rollback, repeated failure, emergency stabilisation, or a change that users or another owner should know about.

Notification is not a request for retrospective permission. It is operational communication and an opportunity for correction.

### 2.3 Stop and ask

The agent stops before the adaptive change when the unresolved question is about what the organisation should want, accept, or trade away. Examples include:

- destructive or hard-to-reverse operations;
- credentials, identity, or trust-boundary changes;
- a change to durable data retention or audit obligations without a declared policy;
- a new owner, tenant, or responsibility boundary;
- an architecture or provider choice with multiple materially different options;
- downtime beyond the intent's declared tolerance;
- a rollback that cannot be made credible;
- a decision involving legal, contractual, financial, or customer impact;
- an intent that is contradictory, stale, or too vague to determine a safe outcome.

The agent should not ask "may I run command X?" It should present the actual trade-off, alternatives, recommendation, impact of delay, and the next action that the decision would unblock.

## 3. Intent contract

An intent must define more than a desired end state. It must declare the autonomous operating space and the boundaries where the agent must ask.

A service intent should provide at least:

```yaml
intent: infrastructure-availability
outcome: "Users can reach and use critical services."

success:
  - health probes pass
  - the primary user workflow completes
  - durable data is available and consistent

normal_autonomy:
  - restart_affected_service
  - renew_expiring_certificate
  - remove_expired_rotated_logs
  - retry_failed_backup
  - repair_declared_reversible_drift

notify_after:
  - actual_outage
  - degraded_user_outcome
  - rollback
  - repeated_failure

ask_before:
  - destructive_data_operation
  - credential_or_identity_change
  - architecture_or_provider_change
  - owner_or_tenant_change
  - downtime_above_declared_limit
  - rollback_not_proven

stop_conditions:
  - backup_unavailable
  - target_scope_unclear
  - user_data_at_risk
  - intent_conflict

success_probes:
  - independent_health_probe
  - primary_user_workflow
  - data_consistency_probe
```

The exact schema is instance-specific, but an active intent without a measurable success contract, normal autonomy, stop conditions, and probes is incomplete and should not grant new autonomy.

## 4. Antifragile response to stress

A stress signal must produce more than a mechanical reaction. The minimum loop is:

```text
stress or deviation
        ↓
 safe stabilisation
        ↓
 measure impact and cause
        ↓
 capture a signal or lesson
        ↓
 propose systemic improvement
        ↓
 execute or ask according to intent boundaries
        ↓
 verify that recurrence risk changed
```

For example, when storage fills because of logs:

1. Stabilise safely by removing only expired rotated logs or applying another declared containment action.
2. Measure which services produced the volume, the growth trend, current retention, and the effect on user outcomes.
3. Record whether the event is capacity growth, abnormal producer behaviour, bad retention policy, or an unknown cause.
4. Propose an adaptation: retention change, log classification, verbosity correction, storage expansion, or monitoring change.
5. Apply the adaptation autonomously only when it is inside the intent's normal autonomy and does not violate audit/security retention. Otherwise ask about the trade-off.
6. Verify free capacity, diagnostic usefulness, user outcome, and recurrence over time.

Repeated stress must not be closed by repeating the same temporary repair without producing an improvement proposal. A proposal may conclude that no change is justified, but that conclusion must be explicit and evidence-based.

## 5. Required stress record

For a material or repeated stress, record structured evidence using the single template in [`autonomy-stress-record.md`](autonomy-stress-record.md). That template holds the schema and the checklist; this framework document does not duplicate it.

Narrative may explain the record, but it does not replace observed evidence.

## 6. What counts as improvement

A stress response must produce at least one of these outcomes when the event exposes a repeatable or structural weakness:

- a configuration or policy change;
- a new or corrected probe;
- a new threshold or trend alert;
- a runbook or intent update;
- a new bounded automation operation;
- an accepted-risk record with owner, controls, and review date;
- an explicit decision that no change is justified.

An incident without a preventive signal is not complete when the underlying weakness remains unexplained.

## 7. Relationship to clearance

Clearance remains a safety ceiling, not a reason to ask about every routine operation. CL0–CL5 answers how much authority an action has; the intent contract answers whether the action is a normal fulfilment or a change in organisational intent.

A normal reversible action inside the active intent may be autonomous at the applicable clearance. An action that changes the intent's trade-off still needs the relevant decision even if the command itself is technically easy. Conversely, an agent should not use a low-risk label to hide a change to identity, durable data, ownership, or a kill-chain asset.

## 8. Verification and learning

After an autonomous action, verify both:

1. **technical state:** the declared probes and recovery checks pass;
2. **user outcome:** the intended user workflow works.

After an adaptation, continue observing long enough to test the hypothesis. If the same stress recurs, escalate the analysis level rather than mechanically repeating the same fix. Repeated manual intervention is an automation defect candidate; repeated intent violations are a policy, capacity, or intent defect candidate.

The goal is not a fleet with no incidents. The goal is a fleet in which incidents reduce hidden weaknesses instead of merely consuming operators.
