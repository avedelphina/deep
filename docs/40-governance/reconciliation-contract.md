# Ticket-to-configuration reconciliation contract

**Owner:** Management / Documentation class
**Primary implementation:** Alice
**Status:** normative design; scheduler and forge integration remain deployment work

Mantis is evidence and coordination, not a direct configuration API. A ticket is eligible for reconciliation only when it contains an explicit `configuration_fact`, `inventory_update`, `decision_recorded`, or verified `execution_evidence` classification. Discussion, proposals, and a `resolved` status alone never overwrite desired state.

## Daily pass

1. Read all visible tickets changed since the checkpoint, plus all open decision markers; do not restrict the scan to Alice's queue.
2. Classify each relevant ticket as `discussion`, `decision_pending`, `observed_fact`, `desired_state`, `approved_change`, `execution_evidence`, or `verification_evidence`.
3. Require authority: an authenticated Tomáš decision, an active intent's standing authority, or independently verified operational evidence.
4. Resolve references to canonical inventory/service IDs and compare three layers: ticket evidence, repository desired state, and live observed state.
5. Emit `consistent`, `documentation_drift`, `configuration_drift`, `runtime_drift`, `conflict`, `insufficient_evidence`, or `blocked`.
6. For an accepted repository change, create or update one deterministic branch/PR per ticket and object. Never mutate production directly.
7. Add a Mantis note containing the classification, result, PR/commit, evidence references, and next owner. Re-read the ticket after every write.
8. Persist a checkpoint, input hash, result, and failure state. Use a lock, timeout, retry, and stale-run alert.

## Authority and conflict

Ticket text does not outrank verified live evidence. A ticket may describe desired state, observed state, or a decision; the record must say which. When sources conflict, do not overwrite either source: create a conflict result and ask the accountable owner. Freshness limits and outage behavior must be declared per object.

## Role boundary

Alice may read, classify, document, update inventory, and prepare configuration PRs within an active intent. She may not self-approve or merge her PR, claim runtime verification from a Mantis note, or execute an infrastructure change outside her declared operations. CQRE customer work remains assigned to `avedelphina`; agent tickets route to Anikke when the CQRE rule does not apply.

## Result states

`recorded` means Mantis evidence exists; `proposed` means a PR exists; `applied` means the change was merged or executed by its owner; `verified` requires an independent live/user-outcome probe. These states must never be conflated.
