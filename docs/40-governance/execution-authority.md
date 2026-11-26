# Execution authority

**Status:** Framework contract v1.0
**Scope:** Who may perform an approved planned operation or incident action

Decision clearance and execution authority are separate. Anyone with a valid
proposal route may prepare a proposal. Approval by a decision authority does
not grant the proposer, approver, or ticket owner the right to execute.

## Required execution binding

Every write-capable operation declares:

- exact target scope and operation ID;
- allowed executor principals or executor roles;
- the accountable decision principal;
- the independent verifier;
- whether the operation permits agent execution after approval;
- whether a human must execute because of law, contract, identity, financial,
  destructive, or other reserved constraints;
- expiry, revocation, and delegation conditions;
- rollback or containment and post-action verification.

A missing or conflicting executor binding fails closed. The system never infers
execution authority from the proposer, approver, ticket author, or last notifier.

## Instance binding shape

An instance may bind its domains with a matrix such as:

| Scope | Allowed executor roles | Decision authority | Required consultation |
|---|---|---|---|
| Agent-owned local scope | named agent/domain executor | affected agent human or resource owner | management/documentation where records change |
| Resource-owned domain | declared domain executor | resource owner | affected agents and verifier |
| Cross-domain change | named cross-domain executor | instance fleet authority | every affected domain owner and management/documentation |
| Fleet-wide governance | fleet executor set | instance fleet authority | management/documentation and affected domains |
| Reserved legal, financial, identity, or destructive action | explicitly named human or reserved executor | authority named by the instance | independent verifier and required domain owners |

The matrix is instance-specific. It may allow agents to execute a CL5-approved
operation when the exact decision and execution bindings permit it. It may also
require a human for a particular operation regardless of clearance.

## Planned operation

The controlled executor checks the approved decision against the exact target,
operation, revision or snapshot, executor identity, validity window, and active
intent. It rejects stale, broadened, revoked, or differently owned work. After
execution, an independent verifier checks the technical state and intended user
outcome.

## Incident action

Incident response uses a separate temporary grant from
[`incident-response.md`](incident-response.md). The grant can authorize a
bound responder to execute a small allowlist of containment or recovery
operations without waiting for the planned-operation approval path. It does not
change the normal execution matrix, standing delegation, ownership, or
clearance ladder. It expires, is revocable, and must be recorded per action.

## Separation of roles

Where required by the instance or operation, keep these identities distinct:

- proposer;
- decision-accountable authority;
- executor;
- independent verifier;
- closure reviewer.

The same principal may hold multiple roles only where the binding explicitly
allows it and no independence rule is violated. A duet is a review and
verification arrangement, not an implicit execution grant.
