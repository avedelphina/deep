# Ticket-to-configuration reconciliation contract

**Owner:** Management / Documentation class
**Primary implementation:** the management/documentation class
**Status:** normative design; scheduler and forge integration remain deployment work

The instance tracker is evidence and coordination, not a direct configuration API. A ticket is eligible for reconciliation only when it contains an explicit `configuration_fact`, `inventory_update`, `decision_recorded`, or verified `execution_evidence` classification. Discussion, proposals, and a `resolved` status alone never overwrite desired state.

## Daily pass

1. Read all visible tickets changed since the checkpoint, plus all open decision markers; do not restrict the scan to the implementing agent's queue.
2. Classify each relevant ticket as `discussion`, `decision_pending`, `observed_fact`, `desired_state`, `approved_change`, `execution_evidence`, or `verification_evidence`.
3. Require authority: an authenticated decision by the accountable human owner, an active intent's standing authority, or independently verified operational evidence.
4. Resolve references to canonical inventory/service IDs and compare three layers: ticket evidence, repository desired state, and live observed state.
5. Emit `consistent`, `documentation_drift`, `configuration_drift`, `runtime_drift`, `conflict`, `insufficient_evidence`, or `blocked`.
6. For an accepted repository change, create or update one deterministic branch/PR per ticket and object. Never mutate production directly.
7. Add a tracker note containing the classification, result, PR/commit, evidence references, and next owner. Re-read the ticket after every write.
8. Persist a checkpoint, input hash, result, and failure state. Use a lock, timeout, retry, and stale-run alert.

## Authority and conflict

Ticket text does not outrank verified live evidence. A ticket may describe desired state, observed state, or a decision; the record must say which. When sources conflict, do not overwrite either source: create a conflict result and ask the accountable owner. Freshness limits and outage behavior must be declared per object.

## Role boundary

The management/documentation agent may read, classify, document, update inventory, and prepare configuration PRs within an active intent. It may not self-approve or merge its PR, claim runtime verification from a tracker note, or execute an infrastructure change outside its declared operations. Ticket routing and handler rules are instance bindings and live in the operations repository.

## Result states

`recorded` means tracker evidence exists; `proposed` means a PR exists; `applied` means the change was merged or executed by its owner; `verified` requires an independent live/user-outcome probe. These states must never be conflated.
