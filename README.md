# DEEP — Delegated Execution & Enforced Policies

**Intent-driven governance for AI-agent-operated infrastructure.**

> Execution is delegated to agents. Policies are enforced by design.
> Agents may reason about work, but only controlled operations may change
> managed state.

DEEP is a governance framework for running real infrastructure — hypervisors,
VMs, networking, DNS, services, backups — with a team of AI agents and one
human architect. Design, documentation, monitoring, change execution, and
recovery are delegated to agents; what agents may do, when, and under whose
approval is enforced by mechanism (clearance gates, scoped credentials, CI
validation, independent gates), not by instructions alone.

This repository is the **generic framework**. A concrete deployment (an
**instance**) keeps its own private control repository with the real estate:
hosts, intents, incidents, identities, and audit trail. Nothing
instance-specific belongs here.

## The five-layer intent hierarchy

Infrastructure exists only to serve an active intent. A service that does not
map to an active intent is a liability, not an asset — no matter how healthy
its uptime looks.

| Layer of intent | Kind | Meaning |
|---|---|---|
| 1 | **Master** | The one root outcome of the instance (the "why we exist"). |
| 2 | **Domain** | Enduring outcome areas beneath the master intent (platform, data, privacy, security, operations, cost). |
| 3 | **Service** | An enduring operational contract that keeps a capability fulfilled (e.g. `infrastructure-availability`). |
| 4 | **Engagement** | Bounded cooperation with a beneficiary toward an outcome. |
| 5 | **Change** | A single bounded change serving one of the above. |

The hierarchy is machine-readable: [`intents/intent-catalog.json`](intents/intent-catalog.json)
is the canonical registry of IDs, parentage, lifecycle, and fulfilment
contracts, validated in CI by [`scripts/validate_intent_catalog.py`](scripts/validate_intent_catalog.py).

## The four agent classes

Responsibility is separated from identity. One agent may hold several classes
in a small installation, but the classes — and the independent gates between
them — stay distinct:

- **Infrastructure** — technical service health end to end: OS, networking,
  DNS, storage, backups, capacity, recovery, technical observability.
- **Coding** — produces and ships software changes; never mutates production
  infrastructure directly.
- **Management / Documentation** — coordination, registry, policy, evidence,
  change records, escalation. May gate or close work; cannot substitute prose
  for execution evidence.
- **Business** — application behaviour and user outcomes: functional
  acceptance, prioritisation, confirming the service does what users need.

## Clearance ladder (CL0–CL5)

Every action class maps to exactly one clearance: **CL0** observe (read-only),
**CL1** propose (PRs/plans, no execution), **CL2** execute reversible changes,
**CL3** execute with senior-agent approval (the "Methodical Skeptic" gate),
**CL4** execute with human approval, **CL5** human-only. Failures demote an
action class; clean history promotes it. Full model:
[`docs/00-operating-model.md`](docs/00-operating-model.md) §4.

## Core documents

- [`docs/00-operating-model.md`](docs/00-operating-model.md) — the founding
  design document: purpose, scope, 25 design principles, clearance model, agent
  organisation, documentation architecture, governance mechanics, phases.
- [`docs/40-governance/master-intent.md`](docs/40-governance/master-intent.md)
  — master intent, domain intents, and global assumptions (template +
  reference example).
- [`docs/40-governance/agent-classes-and-independent-gates.md`](docs/40-governance/agent-classes-and-independent-gates.md)
  — class model and machine-enforced four-eyes independence.
- [`docs/40-governance/infrastructure-operations-workflow.md`](docs/40-governance/infrastructure-operations-workflow.md)
  — how a service intent is fulfilled as a closed operational loop.
- [`docs/40-governance/decision-boundaries.md`](docs/40-governance/decision-boundaries.md)
  — how agent *decisions* are bounded before any action executes.
- [`services/example-service/`](services/example-service/) — a fictional
  worked example of a service fulfilment folder.

## Machine-checkable spine

- [`intents/intent-catalog.json`](intents/intent-catalog.json) — intent
  registry (hierarchy, lifecycle, ownership, commitment).
- [`intents/infrastructure.json`](intents/infrastructure.json) — operational
  contract for the `infrastructure-availability` service intent: health
  dimensions, thresholds, automation, escalation, evidence schema.
- [`scripts/`](scripts/) — validators; run them locally:

```sh
python3 scripts/validate_intent_catalog.py intents/intent-catalog.json
python3 scripts/validate_infrastructure_intent.py intents/infrastructure.json
```

- [`.github/workflows/deep-intent-review.yml`](.github/workflows/deep-intent-review.yml)
  — CI: intent changes are reviewed like code, with impact summaries.
- [`.github/ISSUE_TEMPLATE/intent-proposal.md`](.github/ISSUE_TEMPLATE/intent-proposal.md)
  — propose a new intent or amend an existing one.

## Principles in one breath

1. **Docs before autonomy** — no agent operates on what isn't documented.
2. **Delegated execution** — agents do the work; humans review proposals and
   outcomes, not keystrokes.
3. **Enforced policies** — autonomy is granted by clearance and enforced by
   mechanism.
4. **Reversibility-first** — read-only before writes, PRs before pushes,
   rollback paths before migrations.
5. **Weak beliefs, careful commitments** — reports separate observed from
   inferred; incidents rebuild from verified facts.

## License

MIT — see [LICENSE](LICENSE).
