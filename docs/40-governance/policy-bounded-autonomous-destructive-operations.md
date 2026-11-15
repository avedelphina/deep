# Policy-bounded autonomous destructive operations

> Status: framework proposal; not yet normative
> Scope: DEEP clearance, intent, policy execution, and destructive data operations
> Change class: governance amendment
> Owner: DEEP governance; instances bind the policy to their own assets

## Decision requested

Add a policy-bounded execution path for destructive operations against an
explicitly disposable data domain.

The path must allow an approved retention or lifecycle policy to perform
routine deletion without a per-item human approval queue, while keeping direct,
adaptive, unbounded, or policy-changing destructive actions human-only.

The proposed model is:

1. A human authority approves a versioned policy boundary and its destructive
   trade-offs.
2. A deterministic executor applies only the approved operations to only the
   approved targets.
3. Independent verification reconciles every action and can disable the policy.
4. Any policy, boundary, credential, target, or eligibility change returns to
   the human approval gate.

This is a standing delegation of a declared policy, not a downgrade of
high-risk data operations to ordinary agent autonomy. The executor does not
invent actions, choose free-form targets, widen scope, edit the policy, or
re-arm itself after failure.

This proposal does not grant any instance access, name any host or identity,
or authorize any current operation. It defines the generic contract that an
instance may later bind to its own service and data plane.

## Problem

The current DEEP model correctly puts destructive data operations in the
human-only category. That rule is safe but too coarse for a declared data
zone whose purpose is controlled turnover. If every item still requires a
human decision after the retention rules, scope, recovery model, and exclusion
rules have been tuned, the organisation has built a manual queue rather than
an autonomous operating loop.

The opposite failure is worse: allowing a general-purpose agent or an exposed
third-party API to delete data because a prompt or a loose rule says that the
data is old. That turns a policy decision into an unbounded execution path.

DEEP needs a third shape:

- human ownership of the destructive trade-off;
- machine-enforced scope and eligibility;
- deterministic execution without per-item approval;
- independent evidence and automatic demotion on failure.

The policy boundary, not the conversational agent, is the unit of authority.

## Terms

### Disposable data domain

A declared namespace or set of resources where the owner has accepted routine
removal under a specific retention policy. It may still contain valuable data;
"disposable" means replaceable or intentionally subject to turnover under the
approved policy, not worthless.

The domain must be identifiable by machine-enforceable boundaries such as:

- service or tenant identity;
- library, dataset, collection, or database identity;
- exact filesystem roots or object-store prefixes;
- resource labels or immutable IDs;
- an allowlist of records prepared by the control plane.

A natural-language label is not a boundary.

### Protected data domain

A namespace or set of resources excluded from the disposable data domain. The
executor must not be able to enumerate, mutate, or delete it through the
credentials and network paths used for the disposable domain.

A policy exclusion is useful, but a separate service credential, root, tenant,
or instance is stronger. Where the platform's API key is instance-wide, a
folder or UI filter is not a sufficient protection boundary.

### Policy-Bounded Destructive Operation (PBDO)

A PBDO is a versioned, human-approved contract that grants a named executor
the ability to perform specified destructive operations inside one disposable
data domain. It includes the target boundary, eligibility guards, recovery
assumptions, action semantics, evidence contract, and kill switch.

### Policy lifecycle

The human-gated operations that create, revise, approve, arm, widen, re-arm, or
retire a PBDO are never autonomous. Suspension is a protective state change:
it may be triggered automatically by a systemic kill condition or requested by
an owner/user-outcome monitor. Re-arming after suspension is always human-gated.

### Policy execution

The bounded, non-discretionary application of an already armed PBDO to an
eligible item. Policy execution does not include editing the policy, deciding a
new trade-off, or selecting targets outside the prepared candidate set.

### Action receipt

The immutable record of one execution attempt, including policy revision,
subject identity, before and after observations, executor, result, and
independent verification status.

## Proposed clearance clarification

The clearance ladder remains CL0 through CL5. The proposal adds an execution
mode orthogonal to the ladder rather than creating a lower clearance for
deletion.

### Policy lifecycle is CL5

The following remain human-only CL5 decisions:

- creating a PBDO;
- approving its first revision;
- changing its target boundary or protected exclusions;
- adding a destructive action type;
- changing the recovery or loss-acceptance model;
- changing the hold period or eligibility guards in a materially more
  permissive direction;
- changing the executor, credentials, or network path;
- arming or re-arming a suspended policy;
- overriding a guard, receipt mismatch, or kill condition;
- retiring a protected domain or moving data into the disposable domain.

An agent may prepare the policy, dry-run evidence, impact analysis, and PR. It
may not approve, arm, widen, or re-arm the policy.

### Policy execution is a delegated mode

An already armed PBDO may be executed by a deterministic service, scheduler, or
scoped worker without per-item human approval. This is `policy-autonomous`
execution, not ordinary CL2 autonomy and not discretionary agent authority.

The executor's effective capability is the intersection of:

```text
human-approved policy
∩ machine-enforced target boundary
∩ current eligibility guards
∩ credential and network scope
```

If any term cannot be evaluated, execution stops. The executor must not fall
back to a broader credential, an inferred path, a guessed identity, or a
manual free-form action.

### Direct destructive operations stay CL5

A one-off deletion, an adaptive cleanup decision, a model-generated target,
an operation outside an armed PBDO, or an action after policy drift remains a
CL5 human-only operation. A ticket, a high confidence score, a dry-run match,
or a previous approval does not convert it into policy execution.

### Proposed amendment to the clearance table

The CL5 row in `docs/00-operating-model.md` should be clarified as follows:

> **CL5 - Human-only policy authority.** The human authority creates, approves,
> arms, changes, widens, overrides, and re-arms destructive or otherwise
> high-impact policies. Direct or adaptive destructive operations remain
> human-only. A deterministic executor may carry out an already armed,
> policy-bounded destructive operation only through the PBDO contract; it may
> not choose, broaden, or re-arm that contract.

The existing CL0-CL4 meanings do not change. PBDO execution must never be
presented as a general promotion of destructive data work to CL2.

## PBDO contract

Every armed PBDO must be represented as structured data that the executor and
verifier can validate. Prose may explain the decision but cannot be the only
policy representation.

A minimum contract contains:

```yaml
schema: pbdo/v1
policy_id: stable-policy-identifier
revision: 7
policy_state: draft | reviewed | human-approved | armed | suspended | retired
run_state: not-started | dry-run | executing | held/deferred | terminal
run_result: none | verified | blocked | mismatch | failed
state_machine: pbdo-state-machine/v1
intent_id: active-intent-serving-this-policy

owner:
  accountable_class: business | infrastructure | management | coding
  human_authority: external-instance-binding

author:
  principal: stable-policy-author-id
  kind: human | agent

boundary:
  disposable_domain_id: stable-domain-identifier
  allowed_services: [stable-service-id]
  allowed_tenants: [stable-tenant-id]
  allowed_libraries: [stable-library-id]
  allowed_roots: [canonical-root-id]
  allowed_resource_types: [declared-type]
  protected_domains: [stable-protected-domain-id]
  path_resolution: exact-live-resolution-required
  symlinks: reject
  scope_expiry: timestamp-or-review-window

operations:
  - id: delete-declared-resource
    action: delete
    target: prepared-candidate-id
    service_side_effects: [declared-side-effect]
    idempotence: required

eligibility:
  required_guards:
    - stable_identity_match
    - exact_boundary_match
    - hold_period_elapsed
    - no_active_transaction
    - no_active_use
    - recovery_gate_passed
    - no_protected_demand
  stale_after: duration
  abstain_on_unknown: true

recovery:
  class: backup | authoritative-source | re-acquisition | quarantine-first | accepted-loss
  evidence_required: [probe-id]
  restore_or_rebuild_path: runbook-or-operation-id
  loss_tradeoff: explicit-human-decision-reference
  loss_ceiling:
    max_resources: bounded-count-or-null
    max_bytes: bounded-bytes-or-null
    authority_record: explicit-human-decision-reference

approval:
  approver: validated-human-principal
  approver_authentication: control-plane-attested
  approved_at: timestamp
  approved_revision_hash: digest
  review_due: timestamp
  distinct_from: [executor.principal, verification.independent_principal, verification.closure_principal, kill_switch.principal]
  author_separation: required-unless-author-is-this-human-principal

review:
  reviewer: stable-independent-reviewer-id
  execution_context: separate-from-author-and-executor
  reviewed_revision_hash: digest
  reviewed_at: timestamp
  distinct_from: [author.principal, owner.human_authority, approval.approver, executor.principal, verification.independent_principal, verification.closure_principal]
  no_review_or_closure_overlap: true

executor:
  principal: stable-executor-id
  credential_scope: exact-capability-reference
  network_scope: exact-route-reference
  may_modify_policy: false
  may_expand_scope: false
  may_rearm: false

execution:
  mode: policy-autonomous
  max_batch_size: bounded-count
  parallelism: bounded-count
  lock_scope: policy | disposable-domain | resource
  action_timeout: duration
  retry:
    max_attempts: bounded-count
    only_after_reconciliation: true
    never_retry_for_missing_receipt: true

verification:
  independent_principal: stable-verifier-id
  closure_principal: stable-verifier-id
  require_separate_closure_write: true
  probes: [before-state, action-receipt, after-state, user-outcome]
  reconcile_deadline: duration

kill_switch:
  operation_id: disable-and-revoke-executor
  principal: stable-kill-switch-principal
  verified_stop_required: true
  stop_observed_by: stable-independent-observer-id
  distinct_from: [author.principal, owner.human_authority, approval.approver, review.reviewer, executor.principal, verification.independent_principal, verification.closure_principal]
  triggers: [declared-trigger]
  rearm_requires: human-policy-lifecycle-approval

audit:
  receipt_schema: schema-version
  retention: declared-duration
  immutable_sink: evidence-destination
```

`policy_state`, `run_state`, and `run_result` are the three canonical state
namespaces. They are validated together from the versioned `state_machine`
registry; prose diagrams and implementation enums must be generated from or
checked against that same registry. `dry-run`, `executing`, and
`held/deferred` are run phases, while `verified`, `blocked`, `mismatch`, and
`failed` are terminal run results. They are not untracked policy lifecycle
states. An implementation must reject unknown or missing security-critical
fields and validate all three namespaces before a policy can enter `armed`
state. The state invariant is strict: `run_result` is `none` for every
non-terminal `run_state`, and a terminal run has exactly one non-`none`
`run_result`; a terminal result is immutable and any later attempt gets a new
run ID.

## Boundary rules

### Exact scope

The policy must identify the concrete service, tenant, library, root, dataset,
or resource class it may affect. A title, filename, label, or user-facing
collection name may be part of the explanation, but it is not enough to
establish authorization.

The executor must resolve a candidate to the current live boundary immediately
before action. A stale path, changed mount, missing tenant, duplicate identity,
or ambiguous resource match is a hard stop.

### Protected-domain exclusion

The protected domain must be excluded at more than one layer where practical:

1. the policy's explicit deny set;
2. the executor credential's resource scope;
3. the executor network path and service endpoint scope;
4. the filesystem, object-store, or database ACL;
5. the verifier's boundary audit.

The strongest available boundary is required. If the underlying service has
only instance-wide credentials, the disposable and protected domains must use
separate service instances or an equivalent enforced isolation mechanism.

A policy that says "all except protected items" while holding an instance-wide
delete key is not an acceptable PBDO. It has an exclusion list, not a real
blast-radius boundary.

### No policy self-modification

The executor must not have write access to:

- the policy definition;
- the approval record;
- the policy hash or signature;
- the protected-domain registry;
- the credential and network scope;
- the kill-switch configuration;
- the evidence sink in a way that permits rewriting prior receipts.

The policy control plane and the action executor must have separate identities.
A scheduler that can edit its own rules is not a policy executor; it is an
unreviewed administrator.

### Candidate preparation

A policy engine may prepare eligible candidate IDs, but candidate selection
never grants permission. The executor revalidates each selected candidate
against live state, policy revision, freshness, and clearance before acting.
The decision-boundary rules in `docs/40-governance/decision-boundaries.md`
continue to apply:

- bounded inputs and opaque candidate IDs;
- a state fingerprint and expiry;
- abstention when the input is incomplete or ambiguous;
- a verified executor;
- fresh independent observation after execution.

Free-form model output is never an executable delete instruction.

## Eligibility and retention

A PBDO is not a license to delete old things. It is a policy engine with
explicit eligibility gates.

### Required guards

Every destructive policy must define and machine-check, as applicable:

- stable identity and type match;
- exact disposable-domain membership;
- exact path or resource match;
- no protected-domain overlap;
- no active use, playback, lock, lease, or dependent transaction;
- no active download, import, migration, restore, backup, or replication;
- no pending request or retention hold that outranks the policy;
- no unresolved identity, ownership, language, edition, companion, or health
  ambiguity where the instance declares those dimensions relevant;
- hold or cooling-off period elapsed;
- required user notification completed where the policy requires it;
- recovery or re-acquisition evidence meets the declared threshold;
- policy revision and configuration fingerprint are current;
- candidate and world-state fingerprints are fresh.

The instance may add stricter guards. It may not omit a required guard without
a new policy revision and explicit human approval.

### Unknown and identity mismatch are not eligible

A missing probe, stale snapshot, unavailable service, path that cannot be
resolved, or contradictory record is `unknown`, not `false` and not `true`.
The affected candidate is held or deferred without destructive action. It is
not silently dropped from the evidence set, and the policy does not keep
retrying it against the same stale snapshot.

A candidate-level identity mismatch is held for resolution. If fresh evidence
shows that the candidate belongs to a protected domain, crosses a protected
boundary, or exposes a systemic crosswalk/configuration defect, the policy
transitions to `suspended` and blocks new destructive runs. The hold receipt
must retain the original mismatch, the candidate fingerprint, and the evidence
that caused the policy-wide reclassification. This distinction prevents one
bad item from needlessly disabling an otherwise bounded policy while treating
evidence of boundary failure as a policy-wide incident.

Unknown blocks destructive execution; it never authorizes a best-effort delete.
A safe, human-approved handling path may preserve or quarantine the candidate,
but may not destroy it.

### Hold and notification

A holding period is a policy control, not a substitute for a boundary. The
policy must record when the item became eligible, when notification occurred,
what changed during the hold, and why the final action remained eligible.

The policy may implement stages such as:

```text
eligible → held → notified → rechecked → actioned → verified
```

A new playback, request, or lock resets or extends the candidate's hold
according to the policy. Candidate-specific recovery failure or identity
mismatch defers that candidate; systemic recovery-source failure, protected-
boundary evidence, or policy drift suspends the policy. None of these signals
may be ignored merely because the original timer elapsed.

### Recovery and accepted loss

Before approving permanent deletion, the human authority must choose and record
the recovery model. Valid models include:

- an independently tested backup and restore path;
- a verified authoritative source from which the item can be rebuilt;
- a verified re-acquisition path with the instance's required availability
  threshold;
- a quarantine-first window with tested restoration;
- explicit accepted loss for a domain whose purpose and risk justify it.

"It is probably downloadable" is not recovery evidence. Recovery evidence is
versioned, dated, and tied to the same identity and policy revision as the
action. A policy may choose a quarantine-first model, but a quarantine is not
required when the approved recovery model is otherwise credible and the human
authority has accepted the trade-off.

An `accepted-loss` policy must also record a bounded loss ceiling in the
approval record, such as a maximum resource count, byte count, value class, or
other domain-specific blast-radius limit. The executor must refuse an action
that would exceed that ceiling, and the verifier must reconcile cumulative loss
against it. A policy revision or fresh human approval is required before the
ceiling can change; repeated accepted-loss actions must not accumulate
unbounded loss under one approval.

Protected data must never become eligible merely because it lacks playback,
is expensive, or has an old timestamp. Its exclusion is a boundary property,
not a scoring rule.

## Four-eyes and authority separation

A PBDO separates policy authority from mechanical execution.

### Policy author, reviewer, and human approver

The policy author must not satisfy the independent review gate. A reviewer with
a separate execution context and fresh policy export checks the boundary,
operation, recovery model, and dry-run evidence. The human authority of record
then approves the exact policy revision, target boundary, loss trade-off, and
action set. The approval must be recorded before arming.

The approval record must contain a control-plane-authenticated human principal,
not a free-form name or a reference supplied by the policy author. That
principal must be distinct from the executor, verifier, kill-switch principal,
and, for a policy authored by an agent or an untrusted automation context, the
policy author. A single-architect instance may use the same human as author and
human authority of record only when the author is that authenticated human
principal; it must still use a separate reviewer, executor, verifier, and
kill-switch principal. An agent may draft or relay an approval request but may
not satisfy the human approval field.

For high-risk or irreversible policy authority, the human approver must be
distinct from the executor principal, and the executor must not approve, arm,
modify, or close its own policy. The policy authoring identity must not be able
to alter the approved revision or its evidence after approval. The reviewer
may be an independently scoped agent, but a second prompt in the author's
execution context is not independent review.

This follows the framework's high-risk independence rule: the executor cannot
approve its own plan or close its own change. Independent post-action
verification remains a separate gate and cannot be performed by the executor
principal.

### Executor and verifier

The executor and independent verifier use separate principals or execution
contexts. The verifier must receive a fresh view of target state and must not
be able to rewrite the executor's receipts. The validator must reject a
contract where `verification.independent_principal` or
`verification.closure_principal` equals the executor principal, owner human
authority, or policy author. The `verified` result requires a separate,
verifier-owned closure write; the executor can submit evidence but cannot mark
its own receipt verified.

The verifier must independently establish, as appropriate:

- the intended subject was inside the disposable boundary;
- the protected boundary was untouched;
- the action result matches the receipt;
- the expected service and data records changed;
- the user outcome or downstream consistency remains acceptable;
- the evidence was written to the immutable or append-only sink.

A second prompt in one process is not independent verification.

### Closure

The executor cannot close a failed or mismatched action. Missing receipts,
conflicting state, and failed verification remain `blocked`, `mismatch`, or
`failed` until the owner resolves them. A green scheduler is not proof of
successful destructive work.

## Canonical state registry and transitions

The schema has three deliberately separate state namespaces. `policy_state`
describes human-owned authority over a policy revision. `run_state` describes
the current phase of one dry-run or execution attempt. `run_result` records its
terminal outcome. A run result never grants, changes, or restores policy
authority.

The canonical `policy_state` transitions are:

| From | To | Required gate |
| --- | --- | --- |
| `draft` | `reviewed` | Independent review of the exact revision, boundary, recovery model, and dry-run evidence |
| `reviewed` | `human-approved` | Authenticated human approver records the exact revision hash and target scope |
| `human-approved` | `armed` | Startup read-back proves policy, credentials, network scope, and kill switch match the approval |
| `armed` | `suspended` | Declared systemic failure, protected-boundary risk, failed verification, owner request, or verified kill-switch stop |
| `armed` | `retired` | Human lifecycle authority retires the exact revision |
| `suspended` | `reviewed` | Cause is resolved, evidence is refreshed, and a new review is recorded; no direct resume to `armed` |
| `reviewed` | `draft` | A new revision is created; the prior revision remains immutable |

A policy revision is never advanced by a run result or by the executor. A
material edit creates a new revision in `draft`; `retired` is terminal.

The canonical `run_state` transitions are:

| From | To | Required gate |
| --- | --- | --- |
| `not-started` | `dry-run` | Read-only evaluation starts against a declared policy revision |
| `not-started` | `executing` | The referenced policy is `armed` and all startup gates pass |
| `dry-run` | `not-started` | A new dry-run cycle is required after changed inputs or an expired result |
| `executing` | `held/deferred` | One candidate has unknown, stale, or candidate-local identity evidence; no destructive action occurs |
| `held/deferred` | `executing` | Fresh candidate evidence passes while the policy remains `armed` |
| `executing` | `terminal` | The action attempt stops and a verifier records one terminal `run_result` |
| `terminal` | `not-started` | A new run ID and fresh candidate fingerprint are created; no stale receipt-only retry |

The canonical `run_result` values are emitted only with `run_state: terminal`:

| Result | Required evidence |
| --- | --- |
| `verified` | Every expected action and independent postcondition is reconciled |
| `blocked` | A missing receipt, unavailable required gate, or bounded timeout is recorded and requires reconciliation |
| `mismatch` | The observed result differs from the declared action or boundary |
| `failed` | The declared action failed and reconciliation records the failure |

A terminal result is immutable for that run. A new attempt receives a new run ID
and starts at `not-started`; it may not reuse a stale candidate fingerprint or
retry solely to obtain a missing receipt. A candidate held locally may later be
reclassified as policy-wide `suspended` if fresh evidence shows protected data,
systemic crosswalk failure, or another kill condition. The original hold reason
and the evidence causing promotion must remain in the receipt.

The lifecycle diagram below is explanatory notation generated from these
canonical tables; it is not a second state vocabulary.

## Policy lifecycle

The human-gated policy path is:

```text
draft → reviewed → human-approved → armed
                                      ↓
                                  suspended
                                      ↓
                         reviewed → human-approved → armed

armed → retired
```

Run states may be attached to a declared policy revision during dry-run, and
execution run states require an `armed` revision. They do not appear as policy
states: a run result never grants, changes, or restores policy authority.

```text
not-started → dry-run → not-started
not-started → executing ↔ held/deferred → terminal
                                      terminal → not-started (new run ID)
```

`run_result` is written only at `terminal`:

```text
terminal + verified | blocked | mismatch | failed
```

### Draft

The owner defines the intended outcome, target domain, operation, guards,
recovery model, evidence, and kill switch. No destructive action is possible.

### Dry-run

The policy evaluates real or representative candidates without mutating data.
Dry-run output must include false-positive analysis, excluded/protected items,
identity resolution, scope evidence, recovery evidence, and resource impact.
The number of dry-run cycles and stability window are instance-specific but
must be declared before approval.

### Reviewed

An independent reviewer checks the contract schema, boundary, action
implementation, recovery path, observability, and rollback or kill switch.
The reviewer must use a fresh policy export and not rely on the author's
summary alone.

### Human-approved

The human authority approves an exact policy revision hash. Approval does not
cover later rule edits, new resources, or a new executor.

### Armed

The executor can act, but only after all startup gates pass. The control plane
must read back the live policy, scope, credentials, version, and revision hash
and compare them with the approval record.

### Executing and run results

Each action is bounded, serialized or concurrency-controlled as declared,
receipted, and independently reconciled. `verified` is a verifier-owned run
result, not a policy state. `held/deferred` is candidate-local unless its
fresh evidence demonstrates a systemic or protected-boundary condition.

### Suspended

Suspension prevents new destructive actions while preserving evidence and
holding existing candidates. Suspension is automatic on a declared kill
condition and can be requested by an owner or user-outcome monitor.

Re-arming after suspension is a CL5 policy lifecycle operation. The executor
cannot clear the condition and resume itself.

## Action transaction

A generic PBDO transaction is:

1. Load the approved policy and verify its revision hash and state. A
   destructive run is admissible only when `policy_state: armed` and its
   `run_state` starts at `not-started` with `run_result: none`.
2. Verify executor credential, network scope, service version, and target
   boundary.
3. Acquire the per-policy or per-domain lock.
4. Prepare a bounded candidate set from live state.
5. For each candidate, record a fresh fingerprint and evaluate every guard.
6. Execute exactly the declared idempotent operation.
7. Write an action receipt before releasing the lock.
8. Run independent after-state and user-outcome probes.
9. Record the terminal `run_result` only with `run_state: terminal`: `verified`,
   `blocked`, `mismatch`, or `failed`. A candidate that cannot pass its guards
   remains in `held/deferred` and is not a terminal receipt result.
10. Suspend the policy when a boundary, receipt, or verification condition
    requires it.

A timeout after the operation boundary is not proof that the operation failed.
The system reconciles the target independently before deciding whether to retry.
It must never retry a destructive action solely to obtain a missing receipt.

### Batch size and concurrency

The policy declares maximum batch size, parallelism, lock scope, timeout, and
retry semantics. The default is one title/resource unit at a time when the
operation has no transactional rollback. A later batch is rebuilt from live
remaining candidates; a fixed offset into an old inventory is not valid.

### No-clobber and identity rules

A destructive operation must never act on a path or object because its name
merely resembles a prepared candidate. It must verify stable identity, exact
scope, and the expected resource version. It must not replace an object at a
new path, follow an untrusted symlink, flatten a directory, or delete a
shared companion without an explicit policy rule.

## Failure and demotion

The following are automatic suspension conditions unless the policy declares a
strictly safer handling path:

- policy hash or configuration drift;
- missing or expired approval;
- target scope cannot be resolved exactly;
- disposable and protected domains overlap;
- executor credential reaches an undeclared resource;
- protected resource appears in a candidate set;
- systemic guard source is stale or unavailable;
- required system-wide queue, lock, playback, restore, or replication state is
  unknown;
- missing, duplicate, or contradictory action receipt;
- after-state does not match the declared result;
- independent verifier fails or cannot read fresh state;
- backup, re-acquisition, or recovery evidence falls below the policy gate;
- error rate or mismatch rate exceeds the policy threshold;
- service, container, image, or policy-engine version drifts outside the
  approved compatibility range;
- kill switch cannot be reached and verified.

A candidate-specific stale or unavailable guard defers that candidate without
suspending unrelated candidates, unless it indicates a systemic source failure
or protected-boundary risk. A candidate identity mismatch is likewise deferred;
if it resolves to protected data or demonstrates a systemic crosswalk defect,
the policy is suspended. No unresolved candidate may be deleted.

Suspension is not a failure of the data; it is a successful containment action.
The owner then classifies the event, preserves evidence, fixes the cause or
revises the policy, and seeks human re-approval before re-arming.

A failed autonomous action demotes the policy execution class according to the
existing DEEP demotion rule. The minimum demotion is to `suspended`; repeated
failures may require the whole operation type to return to proposal-only until
a human authority re-promotes it.

## Kill switch

Every PBDO has a kill switch that is independent of the executor's normal UI
and credentials. The kill-switch principal is an authenticated, separately
scoped identity and must be distinct from the policy author, human authority,
executor, and verifier. It must be able to:

- stop new policy runs;
- disable the collection handler or scheduler;
- revoke or narrow executor credentials;
- block the executor's network path;
- preserve the current policy and action receipts;
- report whether the stop was observed and verified.

A kill-switch request is not complete when the control plane merely reports
success. The switch must record a read-back or independent observation binding
the stop to the operation and policy revision. `verified_stop_required` is a
precondition for arming, and the policy suspends when the switch cannot be
reached or its effect cannot be independently verified.

The kill switch is tested before the policy is armed and at the review cadence.
An inaccessible kill switch is a precondition failure, not an emergency plan.
The executor cannot disable, edit, or re-arm the kill switch.

## Evidence contract

PBDO evidence extends the normal DEEP evidence contract. Each policy revision
and action must be attributable, replayable, and bound to the exact state on
which the decision was made.

### Policy evidence

- policy ID and revision;
- canonical policy hash or signature;
- intent ID and version;
- target boundary and protected-domain references;
- operation list and action semantics;
- eligibility and recovery gates;
- dry-run snapshots and stability results;
- reviewer and human approval records;
- executor, verifier, credential scope, and network scope;
- approval time, review deadline, and arming read-back;
- policy engine and service versions;
- kill-switch test and result.

### Action evidence

- action and run IDs;
- policy revision hash;
- candidate identity and type;
- before-state fingerprint and fresh guard results;
- exact resolved target and boundary proof;
- executor principal and start/finish timestamps;
- operation response or error;
- action receipt and immutable sink reference;
- independent after-state and user-outcome probes;
- result and next action;
- suspension, rollback, quarantine, or recovery references where applicable.

Evidence is not complete when the executor says "done." The policy engine,
service, filesystem/database/object store, consumer, and independent verifier
must agree on the result required by the contract.

## Observability and user outcome

The system must monitor both technical safety and the intended user outcome.
Useful signals include:

- policy run freshness;
- candidate and action counts;
- held, deferred, blocked, mismatched, and verified counts;
- action latency and failure rate;
- protected-domain exposure attempts;
- recovery/re-acquisition probe health;
- stale or drifting credentials and boundaries;
- storage, cost, and capacity effect;
- user complaints, playback failures, missing records, or unexpected
  re-acquisition.

A successful deletion count is not a success metric by itself. The policy is
healthy only when it turns over the declared disposable domain while keeping
protected data untouched, preserving catalogue consistency, and satisfying
the user outcome.

## Compatibility with existing DEEP rules

This PR is proposal-only. It does not modify or supersede any current DEEP
normative document, clearance, intent contract, validator, or runtime behavior.
Until a separate framework-amendment PR is reviewed and accepted, the existing
CL5 rule remains in force and destructive data operations must stop for human
execution/approval as currently defined.

If this proposal is accepted, a separate normative amendment must update the
following documents together and reconcile their wording:

- [`00-operating-model.md`](../00-operating-model.md): retain CL0-CL5 while
  defining human-only PBDO lifecycle authority and the bounded execution mode.
- [`autonomy-and-antifragility.md`](autonomy-and-antifragility.md): retain
  destructive operations under `ask_before` except for execution by an already
  armed PBDO within its exact contract.
- [`decision-boundaries.md`](decision-boundaries.md): continue to require
  bounded candidate IDs, freshness, abstention, and a verified executor.
- [`agent-classes-and-independent-gates.md`](agent-classes-and-independent-gates.md):
  require human policy authority to be distinct from the executor and preserve
  separate verification and closure gates for high-risk actions.
- [`reconciliation-contract.md`](reconciliation-contract.md): define the
  PBDO-specific evidence and result-state fields.
- [`infrastructure-operations-workflow.md`](infrastructure-operations-workflow.md):
  require locks, timeouts, recovery, and independent verification for PBDO
  execution.

The normative amendment and its machine-readable schema, validator, tests, and
executor gates must be reviewed as a coherent change. This proposal alone does
not change those rules. An instance must bind its own target domains, identities,
secrets, recovery thresholds, and user-outcome probes in its operations
repository; the framework must not contain hostnames, credentials, or
instance-specific libraries.

## Machine-readable follow-up

This proposal should not be implemented by adding a free-form operation to the
current autonomy contract. A follow-up implementation change must:

1. define a versioned PBDO schema separate from ordinary low-risk operations;
2. publish one canonical registry for `policy_state`, `run_state`, and
   `run_result`, and drift-check prose, transition tables, and implementation
   enums against it;
3. extend the validator to reject missing boundary, approval, review, recovery,
   verifier, and kill-switch fields, including principal distinctness rules;
4. model policy lifecycle transitions and immutable revision hashes;
5. enforce `policy-autonomous` execution only for `armed` policies and require
   `run_result` only with `run_state: terminal`;
6. reject executor attempts to edit policy or protected-domain data;
7. validate candidate freshness and exact boundary membership at action time;
8. emit the policy, action, phase, result, and principal evidence schema;
9. implement automatic suspension and demotion, including promotion of a
   candidate hold to policy suspension on systemic or protected-boundary evidence;
10. provide an independent kill-switch probe and verified-stop receipt;
11. add fixtures for boundary overlap, stale state, missing receipt, failed
    verification, role-overlap rejection, accepted-loss ceiling, and successful
    autonomous execution.

The existing `infrastructure-autonomy.json` contract must remain unchanged until
that schema and validator work is accepted. A service may not claim that a
normal CL2 operation authorizes destructive data deletion merely because the
operation is listed as `normal_autonomy`.

## Adoption sequence for an instance

An instance adopting this framework capability should proceed in this order:

1. Declare the active intent and the disposable and protected data domains.
2. Prove the domain boundary with live manifests, service inventory, and
   credential/network tests.
3. Implement read-only candidate evaluation and evidence snapshots.
4. Run dry-run cycles long enough to expose identity, recovery, and false-
   positive problems.
5. Build and independently test the executor, verifier, receipt sink, and kill
   switch with disposable fixtures.
6. Submit the exact policy revision and evidence to the human authority.
7. Arm the policy only after approval read-back and startup gates pass.
8. Run a bounded pilot with the declared batch and concurrency limits.
9. Review every mismatch and suspend on any boundary violation.
10. Expand only through a new policy revision; never by editing a live rule
    behind the approval record.

The policy should become more autonomous only when evidence shows that the
boundary, recovery model, and user outcome remain stable. A clean history may
support promotion of execution scope; it never permits silently widening the
policy.

## Acceptance criteria for this governance change

The framework amendment is ready for adoption only when:

- the clearance table distinguishes policy authority from policy execution;
- direct and adaptive destructive operations remain human-only;
- PBDO lifecycle states, required fields, and approval semantics are defined;
- protected-domain and exact-boundary requirements are enforceable;
- policy execution cannot edit or widen its own authority;
- stale and unknown inputs fail closed;
- candidate selection cannot grant permission;
- executor, verifier, policy owner, and human approval provenance are distinct
  where required;
- action receipts and independent reconciliation are mandatory;
- suspension and demotion are automatic on declared failures;
- the kill switch is independent, tested, and observable;
- recovery or accepted-loss trade-offs are explicit and versioned;
- machine-readable validation and test fixtures exist;
- at least one instance proves the contract on disposable fixtures before real
  data is placed under autonomous action;
- the framework's human-rebuildability and audit requirements remain intact.

## Open decisions

The following require framework review before implementation:

1. Whether `policy-autonomous` should be a named execution mode in the
   machine-readable contract or a separate PBDO resource type.
2. The minimum approval and review cadence for different destructive-risk
   classes.
3. Whether accepted-loss policies require a quarantine-first default, or may
   be armed directly when the human authority records the trade-off.
4. The required minimum evidence for backup, authoritative-source, and
   re-acquisition recovery classes.
5. The standard action-receipt schema and immutable evidence sink interface.
6. Whether policy suspension may be requested by a user-outcome monitor in
   addition to the owner and verifier.
7. The compatibility and rollback contract for third-party policy engines that
   cannot expose a true authenticated API or cannot isolate their credentials.

Until these decisions and the implementation gates are accepted, CL5 remains
the effective rule for destructive data operations and every instance must
stop before deletion.
