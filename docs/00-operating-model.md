# DEEP — Operating Model

> Status: **FRAMEWORK v1.0** — genericized from a production instance's
> target operating model. Instance-specific profiles (estate inventory,
> concrete hostnames, named agents, incident history) live in each
> deployment's private control repository, never here.

## 1. Purpose

DEEP converts an infrastructure estate (hypervisors, VMs, DNS, VPN, services,
agent fleet) into a fully AI-managed, **human-sovereign** environment,
operated to SME enterprise standards. The human role is **architect only**:
setting Master Intent, approving irreversible transitions, and owning the
break-glass ability to rebuild from scratch. Everything else — design,
documentation, monitoring, change execution, recovery — is delegated to
agents.

**Why (north star):** multiply one clear intent into sustained organisational
work a single operator could not finish alone — without turning that operator
into a full-time approver of their own automation. Agents are leverage, not a
headcount substitute and not the product.

A DEEP instance is an **intent-driven entity**: infrastructure exists solely
to carry out active business objectives. A service that does not map to an
active intent is an existential liability, not an asset — no matter how
healthy its uptime looks.

The framework deliberately covers **integration of heterogeneous existing
tools** — the common SME pain point. An instance does not get to pick only
best-fit greenfield tooling; it must absorb what a real organisation already
runs. Incumbent ticketing systems, legacy auth, and awkward-but-load-bearing
tools are first-class citizens of the model (see P23).

**Instance vs. framework:** this repository is the reusable spine. Each
deployment instantiates it with its own master intent, fleet inventory,
authority matrix, and agent roster. The spine is written so that instances of
different shapes — a single-architect household-scale estate, a small
professional-services firm with multiple humans and thin own infrastructure —
can reuse it without a ground-up rewrite. Portability rules: an instance must
not hardcode single-human assumptions into shared structure; the human ladder
above CL4 is extensible (§4).

## 2. Scope

### In scope (managed plane)

- The estate: hypervisor(s), VMs, physical hosts, containers (`<host-a>`,
  `<host-b>`, … — named only in the instance repository)
- Networking: overlay/mesh VPN, DNS, public endpoints
- Services running on the estate (agent gateways, dashboards, messaging, …)
- The agent organisation itself (roles, budgets, models, fallbacks)
- Third-party infrastructure consumed by the estate (VPS providers, hosted
  DNS, cloud services)
- Monitoring and the continuous improvement loop built on top of it —
  deliberately split the way SMEs split it: **operational monitoring stays
  in-house; security monitoring may run as a separate (outsourced-shaped)
  organisation**, mimicking the classic SOC-outsourcing pattern (§10).
- **Cost management, for both infrastructure and AI spend.** The ability of
  the organisation to understand and control its own costs is arguably the
  most important viability proof of an agent-run estate.
- **External signal intake** — an input pipeline for outside-world signals:
  security advisories, emerging attack patterns, vendor/EOL notices, and
  operational signals (upstream incidents, provider status pages). Autonomy
  without situational awareness is just automation with its eyes closed.
- **Licensing** — the core stack may be OSS, but a real organisation also
  runs paid software; license inventory, renewals, and cost treatment (P9)
  are part of the model.
- Ticketing: an incumbent system of record for changes (see P8) — including
  **tickets created by human users**, not only the architect.

### Out of scope (control plane)

- The DEEP control repository and its mirrors. *Placement rationale:* with
  identities and secrets designed correctly — **no secrets in the repo,
  ever** — the content is architecture documentation, not crown jewels. A
  private repository is then an acceptable pattern for SMEs; self-hosted git
  works equally well.
- The architect's own workstation
- Third-party SaaS accounts (they are dependencies, not managed objects)

## 3. Design principles

These principles extend an antifragile consulting corpus (structural
decoupling, optionality preservation, stress-to-signal, sovereign
intelligence, asymmetric payoff; move-fast-and-fix-things rules) into
agent-organisation form.

| # | Principle | Meaning |
|---|-----------|---------|
| P1 | **Docs before autonomy** | No agent operates on what isn't documented. Inventory → runbooks → delegation. **Blueprint-as-source:** every managed object has a canonical blueprint in `docs/`; an object that exists in the hypervisor but not in the repo is *drift* — a CL0 alert. **Live troubleshooting exception:** during an active incident, humans (and clearance-allowed agents) may change a live host to restore service *without* a prior blueprint update. The incident is not closed until each live delta is either **promoted** into blueprint + snapshot or **explicitly discarded** with a recorded reason — otherwise it is just untracked drift with a story. |
| P2 | **Delegated execution** | Agents do the work. The architect reviews proposals and outcomes, not keystrokes. |
| P3 | **Enforced policies** | Autonomy is granted by clearance, enforced by mechanism (branch protection, approval gates, scoped credentials) — not by instructions alone. |
| P4 | **Reversibility-first** | Actions ordered by reversibility. Irreversible actions need observed certainty or an explicit rollback path. |
| P5 | **Control ≠ managed plane** | The documentation/governance plane survives the failure of the managed plane. **Durable business/user data is a third plane:** it is neither "docs" nor "compute." Backups, restore tests, and retention live under data-plane runbooks; losing the fleet must not imply losing the data, and a config snapshot is not a data backup (§6.1). |
| P6 | **Weak beliefs, careful commitments** | Reports separate observed / inferred / consistent. Incidents rebuild from verified facts. |
| P7 | **Mixed agent types** | The organisation deliberately mixes agent platforms and runtimes — no single-vendor monoculture. |
| P8 | **Ticket-driven change** | Every change is documented as a ticket before execution. What is a hated chore for humans is a must-have for agents: tickets are the audit spine and the context carrier. |
| P9 | **Cost awareness** | Every change is evaluated by cost as well as risk — infrastructure and AI/token spend alike. An organisation that cannot meter itself is not viable. |
| P10 | **Antifragile by design** | Stress-to-signal: every change and every incident must produce a signal — a lesson, a doc update, a rule improvement. No silent failures, no wasted stress. |
| P11 | **Kill-chain-first** | Map the shortest sequence of failures that would end the organisation; protect those nodes above all else. Never spend more preventing a risk than its realisation would cost — *except* on the kill chain, where the cost is existential. |
| P12 | **Housekeeping is a stream** | Cleanup is a permanent, resourced stream with its own queue, cadence, and **named owner role** (Steward, §5) — never a project and never "someone will get to it." Stale accounts, orphaned DNS, unused services and legacy configs accumulate by default; only a standing stream removes them. |
| P13 | **Exit by design** | Every critical external dependency (model provider, hosting, SaaS) has a tested exit path executable within 90 days. The managed plane must be rebuildable from `docs/` alone — and the rebuild must be exercised, not assumed. |
| P14 | **Secure by design — environment over instruction** | Agents take *available* actions, not *instructed* ones — so the easiest available action must also be the secure one: scoped credentials, no secrets in repo or context, PR-only write paths, read-only defaults. Security is a property of the environment, not of the prompt. |
| P15 | **Intent-driven infrastructure** | Infrastructure exists only to serve an *active* Master Intent (`40-governance/master-intent.md`). No active intent → the service is a liability and enters the decommission queue. Uptime without intent is vanity. |
| P16 | **Assumption-based invalidation** | Every blueprint lists the world-assumptions under which it is the right shape. When an assumption fails (pricing change, scale jump, criticality flip), the blueprint is automatically flagged for review — the system is self-invalidating. |
| P17 | **Lean-mean — PoC is a liability** | Proof-of-concept code is never ignored. Isolate it from critical paths, or promote it to full blueprint standard (docs, SLAs, monitoring, death-proof). A PoC that silently became load-bearing is a technical-debt *incident*, not a curiosity. |
| P18 | **Dependency mapping** | No service is standalone. Agents maintain the value-chain graph so silent load-bearers (the certificate authority behind the media service) are visible as critical, while high-uptime pets with no chain are visible as candidates for isolation. |
| P19 | **User-centric observability** | A service is "healthy" only if the user can do the intended thing. CPU/RAM/uptime are secondary signals. Failed playback, unresolved tickets, and zero feature usage override green dashboards. |
| P20 | **Feedback-as-CL0** | User feedback (tickets, complaints, usage patterns) is high-priority observational data. A user complaint invalidates the current "healthy" belief about the service until re-verified. |
| P21 | **Reliability contract** | Agents deliver user outcomes, not just managed infra. If the organisation cannot communicate reliably *to* users and cannot hear what they want, the feedback loop is broken — establishing that channel is itself a kill-chain priority (P11). |
| P22 | **Elegance = transparency for the rebuilder** | Elegance is not cosmic aesthetics and not "short for short's sake." It is *minimisation of hidden state and cognitive load* so a stressed human can reclaim the system. If an architect cannot read a service blueprint and understand its shape in under 30 minutes, the system is too complex — rewrite the blueprint or simplify the service. Logically weak, representationally elegant. |
| P23 | **Contain what you cannot yet exit** | Some liabilities stay — legacy apps, incumbent vendors, ugly but load-bearing tools. That is allowed **only as an explicit accepted risk**, not as silence. Accepted risks are inventory items with owner, residual risk, **compensating controls**, and a review cadence. While the exit is deferred, agents are obligated to *evolve the containment* (monitoring, least privilege, blast-radius limits, backup/restore proof, user communication) so the problem gets smaller in impact even when it cannot yet go away. "We live with it" never means "we stop managing it." |
| P24 | **Bifurcated identity plane (topology by exposure)** | Human authentication and infrastructure recovery trust must not share fate. A centralised identity provider (OIDC/OAuth2) is the right authority for **humans and external-facing organisational agents** (coordinators, client-facing bots, public API integrations) where enterprise auditability, delegation, and dynamic lifecycle management are primary. Conversely, **internal infrastructure and recovery agents** must operate on decentralised, capability-scoped trust (mesh-VPN node keys, scoped pre-shared tokens, asymmetric keypairs) so an IdP outage never halts autonomous operations or recovery loops. Each instance records its identity and secrets policy in a dedicated governance document. |
| P25 | **Automate deterministic work** | Use scripts, declarative configuration, schedulers, policy engines, and machine-verifiable checks whenever a task is repeatable or its outcome can be specified precisely. Do not spend model tokens to imitate a script. Agents design, invoke, monitor, and improve automation, then handle exceptions, ambiguity, and decisions. Automation is preferred not merely because it is cheaper, but because deterministic execution is more consistent, testable, auditable, retryable, and scalable than repeated natural-language instructions. |

## 4. Clearance model

The core governance instrument. Every action class maps to exactly one clearance.
Agents differ in reasoning capability — the model reflects that: approval for
mid-clearance actions is delegated to a higher-capability agent, and only what
exceeds its judgement reaches a human authority.

| Clearance | Name | Description | Examples |
|------|------|-------------|----------|
| **CL0** | Observe | Read-only operations, always allowed. | metrics, logs, inventory, drift detection, doc reads |
| **CL1** | Propose | Agents prepare changes as proposals (PR, plan, runbook, ticket). No execution. | config PRs, capacity plans, incident postmortems |
| **CL2** | Execute reversible | Agents execute low-risk, reversible changes autonomously; notify after. | service restarts, cert renewals, doc publishing, cache clears |
| **CL3** | Execute with senior-agent approval | A higher-capability agent ("methodical skeptic") reviews the staged change for risk, then approves, rejects, or escalates to CL4. For changes where a human cannot honestly measure risk but a stronger model can. | package upgrades, dependency updates, routine rollouts |
| **CL4** | Execute with human approval | Agents prepare and stage; a **human authority of record** approves; agents may execute and verify. In a single-architect instance that authority is the architect. In a multi-human instance it is whoever the authority matrix names for that object class. | config rollouts, new service deploys, DNS changes |
| **CL5** | Human-only | A human authority executes personally. Agents may prepare, never run. | credential rotation, payment/subscription changes, destructive data ops, hardware decommission |

**Human ladder above the agent ceiling:** CL0–CL3 are the agent-usable band
(with CL3 still gated by the Methodical Skeptic function). **CL4 and above are
human clearances.** A larger organisation may insert additional *human-only* rungs
above CL4 (e.g. engagement lead → firm architect → CEO/legal) without minting
new agent powers — those rungs refine *which human* must approve or execute,
not what an agent may do alone. A single-architect instance collapses the
human ladder to one person; the spine keeps the ladder extensible.

Escalation: an agent that hits a boundary above its clearance mid-task stops,
reports, and waits. The Methodical Skeptic escalates to the relevant human
authority whenever its confidence is insufficient — never guesses at approval.

**Demotion:** any failed autonomous action auto-demotes that action class one
clearance until a human authority re-promotes it. **Not all agents are created
equal** — default clearances per role (§5) reflect measured capability, not title.

**Promotion:** approval scope shrinks, not only grows. Quarterly, the
Methodical Skeptic reviews action classes with clean execution history and
promotes them down a clearance step (CL4→CL3→CL2) subject to the human authority that owns
that class. Controls concentrate where irreversibility lives and relax where
evidence proves safety — minimum effective control, not maximum possible
control.

## 5. Agent organisation

An orchestration layer (org chart, goals, tasks, budgets) sits above the
worker agents; the framework is deliberately platform-agnostic and instances
may mix agent runtimes (P7). Roles are defined by **class** (see
`40-governance/agent-classes-and-independent-gates.md`), not by name; each
instance binds names and platforms to these roles privately.

| Role | Class | Responsibility | Default clearance |
|------|-------|----------------|--------------|
| Infrastructure operator | Infrastructure | fleet config, services, backups, monitoring | CL2, CL3 via PR |
| Container/runtime operator | Infrastructure | images, compose stacks, runtime health | CL2, CL3 via PR |
| Architect's reviewer / designer | Management / Documentation | design docs, doc reviews, cross-checks | CL1 (docs CL2) |
| Work coordinator | Business + Management / Documentation | task tracking, prioritisation, user-facing coordination | CL1 |
| Structural problem-solver | (cross-class) | cross-domain analysis, architecture review | CL1 |
| Methodical Skeptic (delegated approval) | (gate) | risk review of CL3 proposals; approve / reject / escalate. Every CL3 review answers in writing: *is this over-committed?* and *does it have a rollback path?* | approves CL3 |
| The Board (steering) | (gate) | holds Master Intent and Global Assumptions; **monthly** intent–assumption audit (plus event-driven on material change); flags zombies, accepted-risk reviews (P23), and cascading invalidation; never touches the hypervisor | CL0 observe + CL1 propose decommission |
| Steward (housekeeping) | Infrastructure | owns the P12 housekeeping stream end-to-end: backlog, cadence, tickets, evidence of removal; feeds on drift and inventory; does not replace build-out work — *removes and contains* | CL1 propose; CL2 on approved reversible cleanup classes |
| User-Rep (customer antibody) | Business | monitors the feedback loop (tickets, messaging, usage); advocates for the user; may *pause* infra agents when user experience is being compromised; owns the user-closing rule | CL1 + pause authority |

Notes:

- The Methodical Skeptic is the pivotal *execution* gate: the standing
  embodiment of the weak-beliefs/careful-commitments doctrine (P6) — the
  organisation's immune system against over-commitment.
- The Board is the pivotal *intent* gate: it does not approve changes, it
  audits whether the organisation still wants the thing the change serves.
  The architect owns Master Intent; the Board holds and audits it.
- The Steward is the pivotal *entropy* gate: without a named owner, P12
  decays into a backlog nobody pulls. Steward success is measured in removed
  surface area and closed accepted-risk reviews — not in tickets opened.
- The User-Rep is the pivotal *outcome* gate: green dashboards without a
  working user outcome are a failure, not a success (P19–P21).
- Worker evaluation is on **user success**, not task completion. Restarting a
  service ten times and failing is failure; pausing, asking the user, and
  fixing the real fault is success.
- Credentials are scoped per role; no agent holds hypervisor root by default.
- Every agent action is logged to the audit trail (§8).
- Identity and secrets handling is specified in a dedicated instance
  governance document (P24); this framework repo never contains identities,
  secrets, or hostnames.

## 6. Documentation architecture

The instance's control repository is the single source of truth.

```
deep-instance/
├── README.md
├── docs/
│   ├── 00-operating-model.md          ← instance profile of this document
│   ├── 10-inventory/                  # fleet inventory (generated + curated)
│   ├── 20-architecture/               # ADRs, diagrams
│   ├── 30-runbooks/                   # operational procedures
│   ├── 40-governance/                 # policies, clearance definitions, budgets, identities
│   ├── 50-operations/                 # SLOs, monitoring, incident reports, audit log
│   └── 90-meta/                       # how the docs themselves are maintained
├── intents/                           # machine-readable intent registry + contracts
├── services/<service-name>/           # fulfilment folders per service intent
└── (mirrors: read-only copy on managed infra; break-glass clone offline)
```

Publishing pipeline:

1. **Draft** — local markdown + git; review with anchored comments.
2. **Published** — team/public view rendering the repository.
3. **Site** — optional curated public subset. *(Deferred per instance; the
   repo comes first.)*

### 6.1 The epistemic duality: blueprints and snapshots

We maintain two distinct forms of documentation. They are not interchangeable;
they are complementary. **Neither is a data backup.**

- **Blueprints (the logic)** — *weak hypotheses*. They capture the generative
  logic, constraints, reasoning, and the *why* behind the infrastructure.
  Written for humans (and agents) to understand intent — they let us adapt,
  modify, and rebuild the system when context changes.
- **Snapshots (the config state)** — *strong hypotheses*. They capture the
  exact *configuration* state at a point in time: configs, versions, schemas,
  IaC outputs, package pins. Built for mechanical restoration of *how the
  system was wired* — reverting to a known-good shape when an agent (or a
  hotfix) causes local failure. Snapshots live **outside the managed plane**,
  otherwise the safety net shares fate with the thing it is meant to save
  (P5).
- **Data backups (the durable payload)** — a **third artefact class**, not a
  flavour of snapshot. User/business data (media libraries, databases, mail,
  object stores) has its own backup, retention, encryption, and
  **restore-test** regime. A config snapshot without restorable data can
  rebuild an empty shell; a data backup without blueprint/snapshot can leave
  you with bits and no known-good shape. Death-proof drills must eventually
  prove *both* paths where the service is data-bearing.

The necessity:

- **Without snapshots**, every failure is an incident — no safety net for
  config, only slow, error-prone manual repair of shape.
- **Without blueprints**, every change is cargo-cult — when the world changes
  (vendor EOL, new scale, new threat), you cannot adapt; you are a hostage of
  the existing configuration.
- **Without data backups**, rebuilds are museums — perfect empty
  infrastructure.

### 6.2 Human-rebuildability protocol (break-glass)

A DEEP instance must be rebuildable by a human architect **without agents**.
The agent fleet is a productivity multiplier, never a dependency: if the fleet
dies, the architect is not dead — merely slow. This is the sovereign-
infrastructure property.

Three conditions:

1. **Blueprint-as-source constraint** — every service is defined in `docs/`
   such that a human with basic technical knowledge can identify: the
   OS/runtime image required; the configuration files and their locations;
   the required environment variables/secrets (referencing the secret
   manager, never the secret itself); the external network dependencies.
2. **Snapshot-to-blueprint parity** — `docs/10-inventory/` contains a
   `bootstrap.sh` (or equivalent) per service: a script that takes the latest
   snapshot (config dump) and produces a functional environment *without*
   needing any agent orchestration logic.
3. **The slow-rebuild runbook** — `docs/30-runbooks/human-rebuild.md` is the
   death-proof document: provision a bare hypervisor → apply the
   `10-inventory/` state → bring services up one by one, verifying each
   against its blueprint logic.

**The death-proof drill (mandatory, quarterly):** the architect disables all
agents, picks a random service, and rebuilds it on a clean machine by hand
using only `docs/` and the latest snapshot. Getting stuck = a critical
documentation defect — fix the blueprint or runbook. Success = the service is
death-proof.

In a rebuild, **snapshots are the ground truth for initial state; blueprints
are the ground truth for logic and adaptation.**

### 6.3 Blueprint minimum schema

Every service blueprint must contain, at minimum:

1. **What** — one sentence on what the service does for a user or for another service.
2. **Why** — constraints and reasoning that produced the current shape.
3. **Intent link** — which active Master Intent(s) this service serves (P15). No link → zombie candidate.
4. **Assumptions** — world-facts that must hold for this blueprint to remain correct (P16).
5. **Invalidators** — conditions that, if true, force a redesign or decommission.
6. **Alternatives considered** — what was rejected and why (so we don't re-litigate forever).
7. **Dependencies** — upstream/downstream value-chain links (P18).
8. **Decision log** — dated entries of material changes with reasoning.

The 30-minute test (P22): if a cold reader cannot reconstruct the shape of
the service from the blueprint alone in under half an hour, the blueprint
fails — rewrite it or simplify the service.

### 6.4 Blueprint update discipline

Every material change to the system follows:

1. **Update the blueprint first** (articulate the new why / assumption / invalidator).
2. **Apply the change.**
3. **Take a new snapshot.**

If you cannot write the blueprint update, you do not yet understand the
change well enough to make it. Ticket extraction (closed tickets → proposed
blueprint PRs) is the standing pipeline that keeps this discipline alive at
scale; ticket quality below the extraction bar is refused, not papered over.

## 7. Automation-first operating rule

DEEP treats deterministic automation as a first-class organisational
capability, not as a convenience added after agents are deployed.

When a task is repeatable, mechanically checkable, or precisely specifiable,
prefer a script, declarative configuration, scheduler, policy engine,
workflow, or machine-verifiable probe over repeated model-driven execution.
Do not burn model tokens imitating a script: natural-language instructions do
not create determinism, and even a well-written runbook can be followed
inconsistently.

Agents remain responsible for deciding what should happen, designing and
reviewing the automation, invoking it within the applicable clearance, observing
its result, and handling exceptions. They should not repeatedly perform the
same mechanical steps by hand when those steps can be encoded and tested.

Automation is preferred because it is deterministic, cheaper in token and
operator attention, testable, auditable, retryable, and scalable. It is not
an instruction to automate judgement blindly. Keep ambiguity, novel
diagnosis, risk acceptance, and user-facing decisions with the appropriate
agent class and DEEP gate.

A good automation boundary is:

1. the owner defines the desired outcome and constraints;
2. the Coding or Infrastructure class implements a bounded, idempotent operation;
3. Management / Documentation records ownership, risk, schedule, and evidence requirements;
4. a scheduler or control plane runs it and emits structured results;
5. agents handle exceptions, investigate drift, and improve the automation.

A recurring task that still depends on an agent remembering a prompt is a
control-plane defect candidate. It should become deterministic automation or
be explicitly accepted as a judgement task.

### 7.1 Automation acceptance criteria

Production automation must specify inputs and target scope, authority
boundary, idempotence and concurrency behaviour, timeout/retry/failure
semantics, backup or rollback behaviour where state changes, structured
output, an independent verification probe, owner, schedule, escalation path,
and a safe dry-run or test mode where practical.

A ticket saying that an agent "will check" something is not automation. The
system must show when the check ran, what it observed, what it changed, and
whether independent verification passed.

## 8. Governance mechanics

- **Change flow:** ticket → agent proposal → PR → (auto-checks) → clearance gate →
  execute → verify → audit entry.
- **Audit trail — both stores:** every agent action is appended to
  `docs/50-operations/audit-log/` in the instance repo (human-readable,
  reviewable) *and* to an external append-only store (tamper evidence;
  product selection is an instance decision, §10).
- **Drift-as-PR (default):** scheduled comparison of live state vs. repo
  state. Drift is never silently applied *and never merely reported* — the
  detecting agent opens a PR that either **imports** the unmanaged object
  into the blueprint or **deletes** it. Infrastructure must be explicitly
  defined; undefined state is treated as an incident, not a curiosity.
- **Rollback:** every CL2–CL4 change declares its rollback path before execution.
- **Budgets:** per-agent LLM/token budgets tracked by the orchestration
  layer; over-budget agents degrade to CL0. Infra spend and AI spend are both
  reported as first-class metrics (P9).
- **Housekeeping stream (P12):** owned by the **Steward** — a permanent
  cleanup queue (stale accounts, orphaned DNS, unused services, legacy
  configs, overdue accepted-risk reviews) worked as ordinary tickets on a
  monthly cadence, fed by drift detection and inventory. Housekeeping is
  attack-surface and cost reduction, not janitorial work. Success = surface
  area removed and risks re-contained, not tickets filed.
- **Incident close requires promote-or-discard (P1):** every live hotfix
  delta is listed on the incident; each item is either merged into blueprint
  + new snapshot or rejected with reason before the ticket may close.
  Unlisted live change after close is drift and is handled as drift-as-PR.
- **Decision boundaries:** where agents make choices that feed automation,
  the choice itself is governed — bounded inputs, freshness checks, defined
  abstention, and verified executors. See
  `40-governance/decision-boundaries.md`.

### 8.1 Steering layer (The Board)

Canonical source: `40-governance/master-intent.md`.

- The Board holds the **Master Intent** and **Global Assumptions**. It does
  not execute infrastructure changes.
- **Monthly intent–assumption audit** (default cadence; **event-driven**
  sooner when Master Intent, a global assumption, or a kill-chain node
  changes): every blueprint must link to an active intent and list its
  assumptions. Broken links or stale assumptions → "Pending decommission /
  redesign" queue (cascading invalidation, P15–P16). Weekly full passes are
  not required — noise destroys the audit.
- **Accepted-risk register (P23):** liabilities we deliberately keep (legacy
  software, incumbent tools) appear as inventory rows with owner, residual
  risk, compensating controls, and next review date. "Stay" is a decision,
  renewed on cadence; between renewals agents **tighten containment**, they
  do not pretend the risk vanished.
- **Zombie detection:** a service with green uptime and no active intent is a
  zombie. Propose isolation (sandbox) or decommission; do not "manage it
  better."
- **Criticality map:** the Board (with P18 dependency maps) distinguishes
  *user-outcome critical* paths from high-uptime pets. Silent load-bearers on
  a critical path that are still PoC-grade become technical-debt incidents
  under P17 — promote or rebuild lean for that path, don't generalise the PoC.
- The architect owns the Master Intent content; the Board audits linkage and
  proposes deprecation. Deprecating an intent is CL4/CL5 — never silent.

### 8.2 User feedback loop

- **Ingress:** all user signals (tickets, messaging channels, usage patterns)
  are classified as *operational* (triggers incident), *intent* (triggers
  Board review), or *noise*.
- **User-closing rule:** no incident or ticket is *Resolved* until the agent
  verifies the user can perform the intended outcome (P19–P20). Dashboard
  green is not verification.
- **User-Rep pause authority:** the User-Rep may pause infra agents when
  ongoing automation is degrading user experience. Pause is logged; resume
  requires either user-outcome restored or architect override.
- Establishing a reliable two-way channel to users is itself early-phase
  kill-chain work (P21), not a nice-to-have.

## 9. Phases

| Phase | Content | Entry gate | Exit gate |
|-------|---------|-----------|-----------|
| **0 — Design** | operating model, repo structure, doc conventions, Master Intent draft | repo exists | model approved by architect; Master Intent seeded |
| **1 — Inventory & read-only ops** | fleet inventory, runbooks, monitoring, kill-chain map (P11), **criticality/dependency map (P18)**, first death-proof drill; two-way user channel designed (P21); agents at CL0–CL1 | model approved | inventory complete; runbooks for top-10 ops; first death-proof drill passed (§6.2); criticality map for the primary user outcome; user channel decision recorded |
| **2 — Proposal-driven changes** | agents prepare PRs; CL3/CL4 chain exercised; Board monthly audit live; Steward housekeeping live; User-Rep + user-closing rule live | phase 1 exit | 2 weeks of clean proposal/execute cycles; first zombie/decommission proposal from Board |
| **3 — Graduated autonomy** | CL2 for proven action classes; drift-as-PR; auto-rollback; lean-mean isolation of non-critical pets | phase 2 exit | zero unrecovered autonomous failures over 4 weeks; death-proof drills on quarterly cadence; non-critical pets sandboxed or decommissioned |

## 10. Open questions (per instance)

An instance answers these during its Phase 0–1; the framework deliberately
leaves them open:

1. **SLO targets per service** — which services get formal SLOs, and what are
   the target values? SLOs are framed as *user-outcome* targets (P19), not
   host metrics alone.
2. **External append-only audit store** — product/mechanism selection
   (e.g. object-lock object storage, dedicated log service).
3. **Ticketing integration** — which incumbent system of record, and how
   agents file and link tickets (API, per-change ticket template), including
   the channel for human-user tickets.
4. **Outsourced security monitoring** — which platform runs it, which
   external feeds it consumes (advisories, attack patterns), and what
   authority it holds. It should behave like a real outsourced supplier: own
   identity, contracted scope, reporting back into the in-house org.
5. **Kill chain** — the shortest failure sequence that ends the organisation
   (hypervisor storage? repo availability? identity plane? user-comms
   channel?). Mapped in Phase 1; kill-chain nodes pin to CL5 change authority
   regardless of convenience (P11).
6. **User communication channel** — reliable two-way path to end users
   (messenger? email? ticket replies?). Required before User-Rep and
   user-closing rule can function (P21).
7. **Master Intent seed content** — the architect drafts the initial active
   intents and global assumptions (`40-governance/master-intent.md`). The
   Board cannot audit empty intent.
8. **Gate-role platform binding** — which runtime hosts the Board, User-Rep,
   and Methodical Skeptic. Deferred to orchestration adoption, but the
   *roles* are defined now.
9. **Multi-human profiles** — when to open an authority matrix for instances
   with several humans. Must not be foreclosed by single-architect
   assumptions.

## 11. Terminology

- **ADR** — Architecture Decision Record; a short doc capturing one decision
  and its rationale (`docs/20-architecture/`).
- **SLO** — Service Level Objective: a measurable target for a service's
  reliability framed as user outcome where possible (e.g. "a user can start
  playback within 5 s, 99 % of attempts monthly"). SLOs drive alerting and
  error budgets — how an SME says "reliable" with numbers instead of
  adjectives.
- **Clearance (CL0–CL5)** — autonomy level of an action class, §4.
- **Methodical Skeptic** — higher-capability agent holding delegated CL3
  approval authority; doctrine holder for weak beliefs / careful
  commitments (P6), see §4/§5.
- **The Board** — non-executing steering role holding Master Intent and
  Global Assumptions; runs the monthly intent–assumption audit (event-driven
  on material change), see §5/§8.1.
- **Steward** — owner of the P12 housekeeping stream; measures success in
  removed surface area, see §5/§8.
- **User-Rep** — customer-antibody role; owns the feedback loop and
  user-closing rule; may pause infra agents, see §5/§8.2.
- **Master Intent** — the active set of business objectives the
  infrastructure is allowed to serve (`40-governance/master-intent.md`).
- **Accepted risk** — a liability we deliberately keep under P23, with owner,
  compensating controls, and review cadence — not an undiscussed scar.
- **Zombie service** — running service with no link to an active Master
  Intent; candidate for isolation or decommission (P15).
- **Silent load-bearer** — service that looks non-critical (PoC, low profile)
  but sits on a user-outcome dependency chain (P17, P18).
- **Existential asset** — an asset class whose loss is existential (domain
  controllers, root CAs, key material). Kept distinct from "CL0" the action
  clearance; kill-chain nodes (P11) are typically existential assets. Human orgs
  may add human-only rungs above CL4 without extending agent power (§4).
- **Blueprint** — documentation of generative logic and intent (weak
  hypothesis; for adaptation), §6.1. Minimum schema in §6.3.
- **Snapshot** — point-in-time *configuration* capture: configs, versions,
  schemas (strong hypothesis; for mechanical restoration of shape), §6.1.
  Stored outside the managed plane. **Not a data backup.**
- **Data backup** — restorable copy of durable user/business payload; third
  artefact class beside blueprint and snapshot (P5, §6.1).
- **Elegance** — transparency for the human rebuilder: minimised hidden state
  and cognitive load (P22). Not aesthetic brevity; logically weak,
  representationally clear.
