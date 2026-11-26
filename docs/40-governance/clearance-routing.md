# Clearance routing and human exceptions

**Status:** Framework v1.1
**Scope:** Resolving the accountable human and the execution boundary for CL0-CL5

The clearance ladder describes the authority of an operation. It does not, by
itself, identify a person. Instances must resolve the operation against a
versioned authority binding before an approval request or execution handoff is
created. A generic `human` label is an eligibility class, not an identity.

## Required subject

Every staged operation and every exception packet identifies:

- the target kind and stable target ID;
- the requested operation and clearance;
- whether the target is agent-scoped, resource-scoped, cross-owner, or fleet-wide;
- the accountable owner of the affected service, data, or user outcome;
- the affected resource/host operator, when distinct from that owner;
- the affected agent and that agent's human/operator, when agent-scoped;
- the fleet decision authority for fleet-wide or globally consequential work;
- the independent verifier and the rollback or containment path.

Technical host ownership, login access, or incident discovery does not make an
operator the accountable service/data owner. CL4 resolves to the affected
agent's own human for an agent-scoped decision, or to the bound owner for a
resource/service outcome. If the decision affects multiple owners or fleet-wide
scope, the instance fleet authority decides. The instance binding must resolve
these subjects for each operation; role names are not inferred from hostnames,
credentials, ticket authors, or notification recipients.

## Routing rules

1. CL0 is observation. No approval is requested. Evidence still identifies the
   target and actor.
2. CL1 is a proposal. The proposal may be prepared without approval, but it is
   not execution authority.
3. CL2 is bounded reversible execution under a standing operation policy. The
   policy defines scope, preconditions, rollback or recovery, verification, and
   notification. Exceptions wake an agent or human only when the policy cannot
   decide.
4. CL3 is agent review by an independent Methodical Skeptic. The reviewer may
   approve, reject, or escalate. The executor cannot satisfy the dependent
   review or closure gate.
5. CL4 is an approval decision by the human/operator responsible for the
   affected agent or resource, or by the instance fleet authority for
   cross-owner, fleet-wide, identity, authority, or kill-chain scope. Execution
   is resolved separately from `execution-authority.md`.
6. CL5 is an instance/fleet governance decision. It identifies who must decide
   the fleet-wide or reserved matter; it does not require that person to type
   the implementation. An agent or human may execute only when the exact
   execution-authority binding permits it. A particular operation may still
   require human execution for legal, financial, identity, destructive, or
   other reserved reasons.
7. Incident response does not use CL4/CL5 as its live command path. A valid,
   time-bounded incident grant may authorize only its named responder, target,
   and allowlisted operation; actions outside the grant return to this planned
   route or escalate.

The route is selected from the affected subject and scope, not from the agent
that happened to discover the problem. A resource owner and an agent owner may
be different people; the authority binding must say which one approves and
which one executes. Approval, execution, verification, and closure remain
separate identities whenever the clearance or four-eyes policy requires it.

## Plain-language exception packet

A human sees a short decision request, not internal transport, model, or
workflow details. The structured record must contain these fields:

- `decision_request`: one sentence saying what the human is being asked to decide;
- `target` and `operation`;
- `clearance` and resolved human route;
- `consequence`: what changes for users, data, cost, or availability;
- `why_policy_cannot_decide`: the exact failed precondition or ambiguity;
- `options`: include the safe no-op or defer option;
- `recommendation`;
- `rollback_or_containment`;
- `impact_of_delay`;
- `uncertainty`;
- `deadline`;
- `evidence_ref` and a compact verification summary.

A packet may retain hashes, revision IDs, and transport details for the audit
record, but those are supporting evidence rather than the human question. A
missing owner, target, or evidence reference is an evidence blocker, not a
reason to ask a person to approve an opaque action.

## Instance binding

The framework owns this routing vocabulary and its invariants. An instance owns
principal identities, resource-to-owner mappings, fleet-operator assignment,
validity windows, revocation, and any special duet rule. The instance must keep
that binding separate from the generic framework so a second organisation can
choose different humans without changing the ladder.
