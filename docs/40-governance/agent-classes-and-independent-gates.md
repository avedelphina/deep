# DEEP Agent Classes and Independent Gates

**Status:** Framework v1.0
**Scope:** DEEP operating model — generic; instances bind named agents to these roles privately.

## Purpose

DEEP separates organisational responsibility from the identity of a particular
agent. An agent may hold more than one class, especially in a small
installation, but the classes remain distinct capability and authority
profiles.

The four classes are:

- **Infrastructure:** owns technical service health end to end: operating
  systems, networking, DNS, storage, backups, runtimes, containers,
  microservices, capacity, recovery, and technical observability.
- **Coding:** produces and ships software changes: implementation, tests,
  packaging, release artifacts, migrations, and deployment contracts. Coding
  does not directly mutate production infrastructure.
- **Management / Documentation:** owns coordination, registry, policy,
  evidence, change records, dependencies, deadlines, and escalation. It may
  gate or close work, but cannot substitute prose for execution evidence.
- **Business:** owns application behavior and user outcomes: functional
  acceptance, application configuration and data semantics, prioritisation,
  and confirmation that a service does what users need.

These classes complement the DEEP autonomy tiers (T0-T5). A class answers
"what responsibility is being exercised?" A tier answers "what authority does
this action have?"

## Accountability boundaries

Each outcome has one accountable class even when several classes contribute:

| Outcome | Accountable class | Typical evidence |
|---|---|---|
| Technical platform is healthy and recoverable | Infrastructure | versions, capacity, service health, backup/restore probe |
| Change is correctly implemented and releasable | Coding | commit/ref, tests, artifact, migration and rollback contract |
| Change is governed and traceable | Management / Documentation | ticket, owner, risk, approvals, evidence, closure record |
| Application serves the intended user outcome | Business | functional acceptance, user-path probe, data/result validation |

A class may request or provide work to another class, but must not silently
assume the other class's acceptance responsibility. Tickets coordinate the
work; they do not transfer accountability.

## Standard change path

A normal application change follows this control graph:

1. **Coding** creates a release artifact and deployment contract.
2. **Management / Documentation** registers the change, dependencies, risk,
   owner, rollback, and required gates.
3. **Infrastructure** stages and executes the technical deployment within its
   DEEP tier.
4. **Infrastructure** performs technical acceptance from a fresh process and
   independent probe.
5. **Business** performs functional acceptance against the intended user
   outcome.
6. **Management / Documentation** closes the record only when the required
   evidence and gate identities are present.

Routine infrastructure housekeeping can use a shorter path:

1. Infrastructure detects drift.
2. Management correlates or creates the maintenance record.
3. Infrastructure snapshots, updates, restarts affected services, and
   verifies the effective state.
4. Management records evidence or escalates the blocker.

A blocker is not execution. Missing access, a dirty checkout, divergent
history, unavailable registry, failed backup, or failed verification remains
open and carries an explicit unblock action and owner.

## Four-eyes without human-scale assumptions

Four-eyes is an independence requirement, not a requirement that two humans
press buttons. DEEP should scale the required independence with risk.

- **Low risk / reversible:** one agent may detect and execute; an independent
  automated verifier or fresh probe confirms the result.
- **Medium risk:** the executor must not also satisfy the next dependent gate.
  Separate execution contexts or class-scoped subagents may perform review,
  technical acceptance, or business acceptance, with provenance recorded.
- **High risk / irreversible:** separate authority is mandatory. The executor
  cannot approve its own plan or close its own change; separate agent
  credentials or human approval are required according to the applicable DEEP
  tier.

A new prompt is not automatically an independent reviewer. Independence is
credible only when the gate has a separate execution context, restricted
permissions, a fresh view of target state, and evidence the executor cannot
rewrite. Separate subagents in one principal's process may satisfy a low-risk
verification step, but must not be used as ceremonial self-approval for a
high-risk action.

The enforcement rule is:

> An agent may perform multiple classes, but may not satisfy two dependent
> gates in the same execution chain when those gates are defined as
> independent for the action's risk tier.

The control plane should reject, rather than merely warn about:

- approval and execution by the same principal where separation is required;
- deployment without an accepted artifact and rollback contract;
- closure by the executor where independent closure is required;
- business acceptance performed by the infrastructure identity;
- approvals created after execution has started;
- evidence that cannot be tied to a target, actor, timestamp, and fresh probe.

## Classes, agents, and subagents

Classes are capability profiles, not necessarily permanent populations of
separate agents. In a small deployment, one agent may hold Infrastructure,
Coding, Management / Documentation, and Business capabilities. The control
plane must still keep their authority and gate provenance separate.

Subagents are scalable workers inside the control graph. They reduce the cost
of independent analysis, testing, and verification, but do not create genuine
independence merely by being spawned. Independence depends on authority,
credentials, context, and write access, not on the number of prompts.

This lets DEEP avoid copying human staffing assumptions while preserving the
human principle: routine checks need not consume two agents, while risky
changes cannot be approved by an agent that is effectively approving itself.

## Example role mapping

A small instance might evolve toward these profiles (names are placeholders;
real rosters live in the instance repository):

- **Infrastructure-class agent of host group A:** OS, network, DNS, and
  agentless-host responsibility.
- **Infrastructure-class agent of host group B:** container and platform
  specialisation; Business responsibility may be added for specific
  user-facing outcomes where explicitly assigned.
- **Coordination agent:** Business and Management / Documentation class for
  user-facing applications and coordination.
- **Architect's workstation agent:** Management / Documentation and
  Infrastructure for its own host, with Coding or Business capability only
  when explicitly assigned for a workflow.
- **Coding agents:** Coding class, producing release artifacts and contracts
  without direct production mutation.

This mapping is illustrative. A role assignment must name the asset or
service scope, authority tier, required gates, and escalation path.

## Scaling path

The class model is compatible with both host and domain ownership:

- At small scale, one agent may own a host end to end while exposing the four
  class profiles internally.
- As the fleet grows, domain agents provide standards, tooling, and fleet
  automation while host or site owners remain accountable for local execution
  and final technical state.
- At larger scale, DEEP routes typed operations against asset groups rather
  than asking one agent to hold every host in conversational context.

The invariant is not "one agent per class" or "one agent per host." It is one
accountable owner per outcome, explicit class boundaries, and machine-enforced
independence at the gates where risk requires it.

## Required implementation work

1. Add class and gate fields to the DEEP asset, service, and change registry.
2. Map every current agent to one or more classes and record its scopes.
3. Define risk-to-independence policy alongside T0-T5 action policy.
4. Implement gate state transitions that reject invalid self-approval.
5. Give each class a standard evidence schema: actor, target, timestamp,
   action, result, probe, and rollback reference.
6. Pilot the model with one routine infrastructure update and one application
   deployment before extending it across the fleet.
