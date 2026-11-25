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
- the affected agent, when an agent is acting for the target;
- the affected resource owner, when one exists;
- the affected agent's human/operator;
- the fleet operator for fleet-wide or globally consequential work;
- the independent verifier and the rollback or containment path.

If ownership or scope cannot be resolved, the operation is blocked and routed to
the fleet operator as an authority decision. It is never silently routed to the
last human who happened to receive a notification.

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
5. CL4 is agent execution after human approval. For an agent- or
   resource-scoped operation, the approval route is the human/operator
   responsible for the affected agent or resource. For a cross-owner,
   fleet-wide, identity, authority, or kill-chain operation, the route is the
   fleet operator or the human named by the instance authority binding.
6. CL5 is human-only execution. Agents may prepare, perform an independent
   review, and verify the result, but no agent executes the operation. An
   instance may require a duet for preparation or verification; a duet never
   replaces the required human action. The instance binding chooses whether a
   private agent-owned action goes to that agent's human or to the fleet
   operator. Fleet-wide, cross-owner, and highest-risk actions go to the fleet
   operator.

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
