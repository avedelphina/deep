# DEEP Incident Response

**Status:** Framework contract proposal v1.0
**Scope:** Declared operational incidents and emergency stabilisation
**Authority note:** This document defines a workflow, not a live grant or runtime permission. An instance must bind, approve, and enforce its incident envelopes before responders may use them.

## 1. Separate operating modes

DEEP has two operating modes. They share evidence discipline and verification, but they do not share an approval path.

### Planned operation

A planned operation fulfils an active intent or deliberately changes it. It uses standing delegation, decision-clearance routing, a separate execution-authority binding, change or PR records, and planned verification. Routine bounded work proceeds under policy. A human sees an exception only when the policy cannot decide.

### Incident response

An incident is an active or credible threat to service availability, user outcome, data integrity, security, identity, or a kill-chain asset. Incident response uses temporary command coordination and, only where an instance has pre-authorised it, a bounded emergency execution envelope. It must not wait for planned-change approval to perform a matching pre-authorised containment operation.

An incident declaration, ticket, Beacon card, commander assignment, or severity label grants no authority by itself. The declaration opens the incident record; authority comes only from a valid, previously bound envelope and an authorised activation. An envelope cannot be created or widened by declaring an incident.

## 2. Lifecycle and severity

```text
detected -> declared -> triaged -> active -> contained -> recovering
    -> monitoring -> resolved -> review -> closed
```

`escalated`, `handed_off`, and `suspended` may be recorded from any state. `resolved` means the technical state and affected user outcome have recovered. `closed` additionally requires the review, authority-revocation, and live-delta gates below.

Severity describes impact and response urgency; it does not change authority:

| Severity | Meaning | Response |
|---|---|---|
| P1 | Critical outage, material data/integrity threat, active compromise, or kill-chain impact | Immediate declaration, command assignment, and escalation |
| P2 | Major service or user outcome unavailable with limited workaround | Start within the instance target, normally four hours |
| P3 | Limited degradation with a viable workaround | Normal incident handling, normally within 24 hours |
| P4 | Minor or non-urgent issue | Planned maintenance; no emergency envelope by default |

Record evidence and rationale for every severity change. A higher severity never widens the target or operation list.

## 3. Roles and accountability

The instance binding must identify these roles per affected service/resource. Technical access, host operation, or incident declaration does not imply ownership or decision authority.

| Role | Accountability |
|---|---|
| Accountable service/resource owner | Owns the service, data, or user outcome and its residual risk; remains accountable during delegation |
| Resource/host operator | Operates the declared host or platform within its technical domain; is not thereby the service or data owner |
| Incident commander | Coordinates priority, scope, roles, handoff, and escalation for this incident; receives no credentials or execution rights from the role |
| Operations lead/executor | Performs only operations permitted by the active envelope and exact execution binding |
| Decision authority | Approves planned trade-offs under CL4/CL5 routing or pre-authorises the relevant envelope; is distinct from the executor |
| Independent verifier | Verifies containment, recovery, and user outcome; is not the executor and, where practical, is not the commander or decision authority for that action |
| Scribe/coordinator | Maintains timeline, evidence, grants, decisions, communications, and cross-system links |

A fleet commander coordinates cross-domain response but does not become the accountable owner of each affected service. Domain owners retain their safety constraints and stop/refusal right when a requested action conflicts with their binding, exceeds the envelope, or creates an unbounded risk. Conflicts that cannot be resolved within the bindings stop the conflicting action and escalate to the named fleet decision authority.

## 4. Pre-authorised envelope and activation

An instance may approve incident envelopes in advance. The envelope must be approved by the accountable owner and the decision authority required by its scope; cross-owner or fleet-wide envelopes use the instance's fleet decision authority. The instance binding names which authenticated principals may request
evaluation of each installed envelope, which principals may activate it, which
may command, and which may execute each operation. A partition-resilient instance may
expose local evaluation to any authenticated in-scope agent; that does not make
every caller an activator or executor. Activation succeeds only when the caller
is eligible for the envelope and the local activation checks pass. The selected
operation separately resolves an executor binding; the executor is
re-authenticated at action time. Invoking evaluation does not let the caller
edit the envelope, obtain a credential, or direct another domain to violate its
safety binding.

Activation materialises a time-bounded grant from that existing envelope. The
authorised commander may select only a matching incident, target, and operation
from it. The commander cannot issue credentials, add targets or operation types,
remove exclusions, extend expiry, or appoint an unbound executor. A new or wider
grant requires a new recorded authority decision from the binding's decision
authority. If that authority is unavailable, the agent uses only
already-authorised operations and escalates; urgency does not create a substitute
authority.

Every envelope and activation record must bind:

```yaml
mode: incident_response
schema_version: 1
status: example-not-active
envelope_id: <stable envelope id>
revision: <immutable revision or digest>
signature_ref: <sha256 digest reference>
preauthorising_authorities: [<bound decision principal IDs>]
accountable_owner_ids: [<service/resource owners; one per outcome>]
activation_eligibility: [<authenticated principals allowed to activate>]
commander_eligibility: [<authenticated principals allowed to command>]
executor_eligibility: [<exact principals/classes allowed by operation binding>]
host_operator_eligibility: [<exact host/resource operators>]
trigger_conditions: [<observable conditions>]
target_ids: [<exact targets>]
allowed_operation_ids: [<registered operation IDs>]
incident_playbooks:
  - operation_id: <registered operation id>
    revision: <immutable playbook revision>
    sha256: <playbook content digest>
operation_bindings:
  - operation_id: <registered operation id>
    target_revision: <immutable target or state snapshot revision>
    accountable_owner_id: <owner for this operation's outcome>
    decision_authority_id: <authority that pre-authorised this operation>
    host_operator_id: <operator for the target's host/resource layer>
    activator_may_execute: false
    target_ids: [<exact targets for this operation>]
    executor_eligibility: [<exact executors for this operation>]
    playbook_revision: <immutable playbook revision>
    playbook_digest: <sha256 digest of the playbook content>
    verifier: <bound operation verifier>
    rollback_or_safe_stop: <bound rollback or safe-stop path>
    evidence_sink: <bound evidence sink>
    not_before: <operation validity start>
    expires_at: <operation validity end>
max_blast_radius: <explicit numeric or categorical bound>
max_action_count: <positive integer>
max_rate: <bound rate>
stop_conditions: [<observable conditions>]
explicit_exclusions: [<forbidden targets and operations>]
rollback_or_safe_stop: <verified path or stop condition>
required_local_capabilities: [<tools and dependencies>]
network_dependency: none | reconciliation-only
purser_dependency: none | named pre-authorised local budget policy
trusted_time_source: local-trusted-time | attested-trusted-time
not_before: <timestamp with timezone>
expires_at: <timestamp with timezone>
replay_guard: <durable envelope replay identifier>
local_evidence_sink: <append-only local path or service>
reconciliation_route: <durable incident record route>
verification: [<fresh technical and user outcome probes>]
```

## Activation record

```yaml
mode: incident_response
schema_version: 1
envelope_id: <exact envelope id>
envelope_revision: <exact envelope revision>
grant_id: <unique grant id>
incident_id: <incident record id>
activator: <authenticated activation principal>
commander: <eligible incident commander>
accountable_owner_id: <owner for the selected operation>
decision_authority_id: <preauthorising authority for the selected operation>
host_operator_id: <operator for the selected target layer>
executor: <authenticated executor principal>
verifier: <bound operation verifier>
observed_trigger: <declared trigger condition>
trigger_evidence_ref: <evidence reference for observed trigger>
target_ids: [<exact bound targets>]
allowed_operation_ids: [<exactly one operation id>]
action_count: 1
issued_at: <timestamp with timezone>
expires_at: <timestamp with timezone>
replay_guard: <unique activation replay identifier>
evidence_ref: <activation evidence reference>
```


The example envelope and activation in `intents/incident-envelope.example.json`
and `intents/incident-activation.example.json` are validated by
`scripts/validate_incident_envelope.py`. They are inactive examples, not live
grants. The validator requires an explicit deterministic `--at` clock and does
not verify installed signatures, provide a replay ledger, or authorize runtime
actions. Instances must provide an equivalent signed, immutable binding and
controlled executor before runtime use.

## 5. Permitted action classes and stop rules

An instance may pre-authorise narrowly scoped operations such as read-only diagnosis, reversible isolation/drain of a declared target, restart of a declared service, rollback to an exact recorded revision, failover to a pre-declared healthy target, or disabling a specifically implicated scheduled job. Backup restoration is permitted only where the target and data-loss trade-off are already authorised. Each operation must be registered, target-bound, and independently verifiable.

The envelope does not permit unlisted actions, target expansion, unbounded scans/restarts, durable-data deletion or overwrite, changes to standing policy or ownership, credential/identity/trust-boundary changes, disabling audit or safety controls, or legal, financial, contractual, or external commitments. Such work follows its explicit operation and decision bindings; it is not made permissible by calling it an incident.

Before each action, the executor checks the incident, envelope revision, exact target, operation ID, principal, expiry, stop conditions, and evidence path. If discovery shows that target, impact, or state differs from the envelope, do not start the action. If an action is already running, stop it at the next safe point or use its pre-authorised rollback/containment path, record what could not safely be stopped, and escalate. Never continue out of scope while waiting for a decision.

A host/service operator may refuse or stop an action that violates a domain safety constraint. The fleet commander may coordinate or request a bound operation but cannot override that constraint. Resolving a conflict requires the authority named by the affected binding and a new explicit grant where scope changes.

## 6. Escalation and handoff

Escalate immediately for P1 impact, security/data/identity or kill-chain impact, missing or unenforceable envelope, conflicting owner/authority, unavailable audit/control plane, failed containment or verification, recovery risk, a grant nearing expiry, or any action outside the allowlist.

A handoff records the outgoing and incoming commander, acceptance time, current state and severity, each affected service/resource owner, targets, active envelope revision and grant expiry, actions and results, verified facts versus inference, open risks, stop conditions, next actions, and evidence links. The incoming commander explicitly accepts the coordination role. Any executor or scope change is checked against the envelope; if it is not already bound, obtain a new grant before proceeding.

The instance defines a fallback record for Beacon or Mantis unavailability. Offline evidence is reconciled into the durable incident record once service returns. A coordination outage does not expand execution authority.

## 7. Verification, closure, and learning

An incident is closed only when:

- containment and recovery have a fresh technical probe and user-outcome verification;
- the verifier is independent of the executor; inability to verify means the incident remains open or explicitly unresolved;
- each residual impact/risk has one accountable owner and a deadline;
- every incident grant is revoked or expired and no emergency capability remains active;
- every live hotfix delta is promoted through the planned decision/execution path or explicitly discarded with a reason;
- the post-incident review is complete or has an owner and deadline;
- the durable record, evidence, handoffs, and corrective changes are linked.

The review separates observed facts, inference, and hypotheses; records decisions, envelope revisions, activations, expiries, revocations, actions, results, communications, root-cause confidence, and evidence for any decision not to change the system.

Successful emergency execution does not promote an envelope or operation to standing authority. Promotion, retention, or deletion of a temporary policy is a new planned decision with an explicit owner, scope, executor, expiry/review date, and evidence. Incident response restores service; planned governance decides what the permanent system should become.

## 8. Records and system boundaries

Beacon may coordinate the live incident and workflow state. Mantis or the instance's designated durable incident store holds the formal record and evidence. Neither a ticket, card, nor chat message grants runtime authority. The bound policy and controlled executor must enforce grants. If enforcement is absent, treat the incident workflow as documentation and coordination only; do not claim emergency actions are authorised by this framework document.

Use the incident template in the instance binding. Keep incident evidence and formal work in the authoritative tracker; informal coordination channels are not approval or task systems.
