# DEEP Decision Boundaries

**Status:** Framework v1.0
**Scope:** How agent *decisions* are bounded before any action touches managed state.

## Purpose

DEEP's tier model (operating model §4) governs *actions*: what an agent may
observe, propose, and execute. This document governs the step just before
action — the **decision**, where an agent (or a model acting as selector)
chooses what to do next.

The core rule:

> **Agents may reason about work, but only controlled operations may change
> managed state.**

A decision — however well reasoned, however confident the model — is an
input to the control plane, never a grant of authority. The host owns the
options, the state checks, and the permissions; the selector returns a choice
or abstains.

Inspiration: the Keel decision architecture
(<https://github.com/codejunkie99/keel>, `docs/decision-architecture.md`),
which separates a bounded model selector from a host that prepares candidates,
validates results, and owns execution. DEEP adopts the same shape at the
governance level.

## The five principles

### DB1 — Selection never grants permission

Choosing among candidates authorises nothing by itself. The host prepares a
set of eligible options; the agent's choice identifies *which prepared option*
to consider. Every existing gate still applies afterwards: DEEP tier,
four-eyes independence (`agent-classes-and-independent-gates.md`), approval
records, scoped credentials. A model's name in the picker does not give the
organisation control over that model's internal loop — and a model's choice
in a picker does not give the choice executive power.

Control-plane consequences:

- An approval path that a decision "selects" is still an approval path: the
  required human or senior-agent answer must actually be obtained.
- No component may treat a selector result as evidence of authorisation in an
  audit record. Evidence records the *executed operation*, its tier, and its
  approvals — not the confidence of the chooser.

### DB2 — Bounded decision inputs

A decision is made over a **limited state snapshot plus opaque candidate
IDs** — never over a free-form action space. The contract is:

- **State input:** a bounded, current, redacted view of the relevant world
  (asset state, probe results, declared thresholds). What is not in the
  snapshot is not decidable.
- **Candidates:** IDs referring to options the host already prepared and
  validated (an ID names an operation the control plane knows how to execute
  within policy). A candidate that would exceed the acting agent's tier is not
  a candidate.
- **Output:** a selected ID, or abstention. Free-text "actions" invented by
  the model are not executable; if the model wants something outside the
  candidate set, that is a proposal (T1), routed through the normal PR/ticket
  path.

This is the decision-level twin of P14 (environment over instruction): the
safest available choice set is the *only* available choice set.

### DB3 — Freshness checks: decisions expire

A decision is only valid against the state it was made from. Every prepared
action carries:

- a **state fingerprint** (read-set fingerprint / task revision) capturing
  the snapshot the decision was based on;
- an **expiry** (time bound and revision bound).

The execution path re-checks freshness before applying the choice. If the
world moved — state changed, revision advanced, window elapsed — the decision
is **rejected as stale** and the system falls back, re-decides on fresh
state, or escalates. A decision approved on Monday's snapshot does not
authorise Tuesday's divergent reality; this mirrors the T-tier rule that a
staged change must match what was approved.

### DB4 — Abstention is a first-class outcome

"Not decided" is a legitimate, expected result — not a failure to be
engineered away. Every decision point must define:

- an **abstention threshold** (when the selector must decline);
- a **defined fallback** for abstention: the safe default action, hold-and-
  escalate to the owning class, or route to the applicable human tier.

Abstention routes into the same escalation machinery as an operational
exception (see `infrastructure-operations-workflow.md` §5.2): classified,
owned, with a deadline. A decision loop that cannot abstain will eventually
act on noise; a decision loop whose abstentions are silently dropped will
eventually stall without evidence. Both are defects.

### DB5 — No selector without a verified executor

Do not govern what you cannot intercept. A decision point exists only where
the control plane can enforce the full boundary:

1. inspect current state,
2. select from prepared candidates,
3. validate the selection (freshness, tier, independence),
4. execute the stored action through the controlled operation,
5. observe the result again with an independent probe.

If any step is impossible — because the operation runs inside an external
loop, a third-party SaaS, or an agent runtime the control plane cannot
intercept end to end — then no selector is wired up there. Instead, the
surface is handled by containment (P23): scoped credentials, blast-radius
limits, and the appropriate human tier. An advertised capability is not an
executable host action; governing a fiction produces audit theatre, not
control.

## Summary table

| Principle | Rule | Failure it prevents |
|---|---|---|
| DB1 | Selection never grants permission | Model output laundered into authority |
| DB2 | Bounded inputs: snapshot + opaque candidate IDs | Free-form action spaces; prompt-injected operations |
| DB3 | State fingerprint + expiry on every decision | Acting on stale reality with a fresh-looking approval |
| DB4 | Abstention with defined fallback | Forced choices on noise; silent stalls |
| DB5 | No selector without a verified executor | Governance of paths the control plane cannot enforce |

## Relationship to tiers and gates

- **Tiers (T0–T5)** bound *what may be executed and by whom*.
- **Classes and independent gates** bound *who may approve, execute, and
  close*.
- **Decision boundaries** bound *how a choice is produced and validated
  before it reaches those gates*.

A decision that passes DB1–DB5 still enters the normal change flow (ticket →
proposal → PR → checks → tier gate → execute → verify → audit entry). The
boundaries make the front of that pipeline trustworthy; they do not shorten
it.

## Evidence

Each completed decision records, in the evidence stream:

- candidate set summary and the typed result (selected ID or abstention);
- confidence/probability where the backend supplies it (never invented
  narrative reasoning);
- host validation outcome: freshness check, tier check, fallback taken;
- the observed outcome of execution, including denials and failures.

As everywhere in DEEP: the agent may summarise evidence, but narrative does
not replace it.
