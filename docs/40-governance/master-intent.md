# Master Intent & Global Assumptions

> Status: **FRAMEWORK template v1.0** — this document doubles as the
> reference example a new instance starts from. Each DEEP instance keeps its
> own authoritative copy in its private control repository, seeded by its
> architect; the Board audits that copy, not this template.

## Purpose

This file is the **why** of a DEEP instance. Blueprints answer *how*; this
file answers *what we are still trying to achieve* and *what must stay true
about the world for those achievements to make sense*.

A service with no link here is a **zombie** (operating model P15). An
assumption that fails invalidates every blueprint that depends on it (P16).

**How to read an intent:** outcome first, tools second. Product names belong
in blueprints and assumptions — not in the intent statement — so a forced
swap of implementation does not rewrite the organisation's reason to exist.

## North-star (one paragraph)

*Instance-specific. Example shape:* a small organisation runs a
**self-hosted, sovereign estate**: it keeps control over its data and
communications, gets **cloud-like day-to-day utility** without renting that
sovereignty to a hyperscaler, and runs the platform under explicit privacy,
security, and cost discipline. DEEP is how that platform is operated —
intent-driven, documented, rebuildable — not a second product competing with
the real-world outcome.

## Active Intents

### Machine-readable intent hierarchy

The canonical registry for intent IDs, parentage, lifecycle, and links to
fulfilment contracts is `intents/intent-catalog.json`. This document remains
the authoritative explanatory source for the master and domain outcomes; the
catalog deliberately keeps concise outcome summaries to avoid competing
copies of the same prose.

The hierarchy is:

- `master` — the single root intent of the instance.
- `I1`–`I7` — domain intents defined below (an instance may add, rename, or
  retire domains as amendments).
- service, engagement, and change intents — bounded or enduring outcomes
  beneath one or more domain intents.

A catalog entry must not be marked active until its owner, outcome contract,
implementation, evidence path, and funding decision are ready. Catalog
changes and linked contract changes travel through the normal PR and CI
review path. In this framework repository, `example-service` stands in as the
illustrative registered operational contract (see
[`services/example-service/`](../../services/example-service/)); real
instances register their own.

### I1 — Sovereign platform

**Outcome:** The organisation has a stable self-hosted platform for compute,
storage, identity-adjacent access, and remote use that it controls end-to-end
— not a pile of unrelated pet services.

**Means (non-binding):** hypervisors/VMs, storage hosts, overlay network,
reverse proxy, backup plumbing, agent fleet as operators.

**Done looks like:** named platform capabilities with owners; critical path
documented; non-contributing services labeled pet/PoC/zombie rather than
silently "part of the platform."

**Invalidators:** platform control cannot be restored after loss of a host or
provider without heroics; majority of runtime exists with no intent link;
cost or complexity grows without new capability.

---

### I2 — Data sovereignty & governance

**Outcome:** Organisational data has a known home, classification, retention
idea, and restore path. We know *what* we keep, *where*, *who can reach it*,
and *how to get it back*.

**Means (non-binding):** storage pools, DB volumes, backup/restore jobs,
access inventory — always as data-plane artefacts (operating model P5 /
§6.1), not as config snapshots alone.

**Done looks like:** data-store inventory; backup + periodic restore test for
data that would hurt to lose; no critical dataset that exists only on one
undocumented disk with no owner.

**Invalidators:** silent data loss; "everyone assumed someone else backed it
up"; encryption/access so opaque that restore is mythical.

---

### I3 — Privacy by default

**Outcome:** Personal and organisational activity is not the product. Third
parties do not get bulk behavioral data as the price of features we host
ourselves; sharing is explicit and minimal.

**Means (non-binding):** prefer self-hosted over ad-funded SaaS where
capability allows; scoped access; no unnecessary telemetry egress; clear
boundaries for agent context (what agents may see).

**Done looks like:** external processors listed; default deny on data leaving
the perimeter; agents operate on the least context needed.

**Invalidators:** routine workflows that only work by uploading private life
to a surveillance vendor without an accepted-risk entry (P23); agents
hoarding unrelated personal content in prompts/logs.

---

### I4 — Cloud-parity services (selective)

**Outcome:** For the service classes we choose to cover, daily UX is "good
enough that the hyperscaler subscription is optional," not "works if you are
the admin."

**Priority classes (example set):**

| Class | Meaning | Notes |
|-------|---------|-------|
| **Media library (video)** | Find and play the video library; practical streaming-class *library + playback* utility | Implementation is replaceable (see A5) |
| **Music / audio** | Library + playback that can displace streaming subscriptions over time | Often a known weak spot — the intent must stay honest about delivery |
| **Secure communications** | A private messaging/calls path users can rely on | Channel must be hardened before it counts (P21) |
| **Docs & knowledge** | Durable notes/docs without single-vendor lock-in | git-markdown or whatever the blueprint says |
| **Remote access** | Use the estate from outside without ceremony | overlay + auth patterns |

**Explicit non-goals (by default):** full office-suite parity, full
photo-social-graph parity, arbitrary SaaS clone checklist. Parity is
**selective**, not encyclopedic — each new class needs an intent amendment or
it is a pet.

**Done looks like:** per class, a user-outcome SLO draft and a criticality
map; weak classes have an honest status (gap), not a green dashboard.

**Invalidators:** "we run sixty services" while the covered classes still
fail basic user outcomes; new classes accrete without cutting elsewhere.

---

### I5 — Security commensurate with the estate

**Outcome:** Baseline security fits an exposed-ish self-hosted estate: least
privilege, patch/renewal hygiene, segmented access, secrets not in git, blast
radius limited when something pops.

**Means (non-binding):** scoped credentials, HTTPS where relevant, update
cadence, backup encryption, agent permission boundaries (P14).

**Done looks like:** an identities-and-secrets document real enough to
follow; no shared root-by-default for agents; kill-chain nodes known
(I1–I2 touching).

**Invalidators:** one stolen token = whole fleet; secrets in repos or chat
logs; "we'll harden later" on internet-facing entry points with no
accepted-risk record.

---

### I6 — Documented, rebuildable operations (the DEEP method)

**Outcome:** The platform is operable and recoverable without tribal memory.
A competent human can rebuild critical pieces from docs + snapshots + data
backups; agents multiply effort under the same spine.

**Means (non-binding):** the control repository, blueprints/snapshots,
death-proof drills, ticketed change, Board/Steward loops — the DEEP operating
model.

**Done looks like:** critical path blueprinted; at least one death-proof
drill done; inventory exists; the organisation's narrative matches reality.

**Invalidators:** only one human can operate it and only from memory; docs
describe a fleet that no longer exists; agents cannot act because nothing is
written down.

---

### I7 — Cost-viable sovereignty

**Outcome:** Self-hosting stays cheaper *in money + scarce human attention*
than the combination of subscriptions + risk we are replacing — or the gap is
an explicit accepted trade (privacy/security premium).

**Done looks like:** rough monthly infra + energy + AI/token envelope; pets
that burn time without I1–I6 value get cut.

**Invalidators:** endless hardware/SaaS creep with no outcome gain; AI spend
without reduction in operator toil.

---

## Intent map (priority for prune vs invest)

When something must lose (example ordering for the reference instance):

1. Protect **I2/I3/I5** (data, privacy, security) — existential for "why
   self-host."
2. Protect the primary user-visible utility class of **I4**.
3. Invest in weaker I4 classes until honest parity, or demote the class.
4. **I6** is how the organisation survives; starve it and I1–I5 rot.
5. **I7** is the brake pedal on everything else.
6. Anything outside I1–I7 is pet, PoC, or zombie unless promoted here.

## Global Assumptions

Example assumption set for a household-/team-scale instance; each instance
writes its own:

| ID | Assumption | If false… |
|----|------------|-----------|
| **A1** | Primary users are a small group (single-digit to ~20 humans), not a public ISP-scale audience. | Capacity, threat model, and support-model blueprints break — redesign. |
| **A2** | Self-hosting remains legally and practically viable for content *we have rights to use*. | I4 media intent must shrink or stop; legal review. |
| **A3** | Architect human time is the scarcest resource; agent labour is usable for reversible ops and docs. | Autonomy tiers and agent roster assumptions fail. |
| **A4** | Site connectivity and power are "good enough" with occasional blips; we accept non-five-nines — or the estate is deliberately distributed with local hardware under central orchestration. | If HA/multi-site becomes required, I1 blueprints change materially. |
| **A5** | **Every product is replaceable.** A media server migration already happened once under license pressure; the current binary may become unacceptable too. I4 names the *outcome*, not the product. | Blueprint swap / accepted-risk — not a new Master Intent. |
| **A6** | Where a service class underdelivers, it is reported as a gap, not as satisfied. | Board re-opens the class: invest or narrow. |
| **A7** | Some incumbent ugly pieces will remain for a while (legacy auth, PoC certificate paths, etc.) and must be **contained** (P23), not ignored. | If we pretend they are fine, criticality maps lie. |
| **A8** | Showcasing the method must not override real outcomes — if framework process harms I2–I4, the real outcome wins. | Split intents or stop showcase scope on that surface. |
| **A9** | A reachable two-way channel to users will exist. Silence ≠ satisfaction. | User-closing rule and P21 blocked. |
| **A10** | Provider pricing (VPS, DNS, domains, energy) stays within an order of magnitude of today's envelope. | I7 and hosting blueprints reopen. |

## Non-intents (explicit)

Example non-intents for the reference instance:

- Running every self-hosted app that looks cool.
- Multi-tenant cloud for external customers on estate hardware.
- Perfect uptime cosplay.
- Replacing every SaaS the organisation has ever touched.
- Other legal-entity operations that may share the spine later — not these
  intents.

## Open prompts for architect review

A seeded instance should answer, during Phase 0–1:

1. Which weak service classes do we actually fund, and which drop to
   non-intents until someone cares enough?
2. Is each communications class in-scope for this estate, or provided
   elsewhere with the estate only supplying network?
3. Should "showcasing the method" stay folded into I6 or become a separate
   domain intent with its own success metrics?
4. Any hard **cost envelope** numbers for I7/A10 worth writing down now?
5. What is the one-sentence **kill-chain** fear (storage? identity? upstream
   provider? git hosting?) to pin under I1/I2?

## Governance

| Rule | Detail |
|------|--------|
| Who edits intents | Architect (T5 for deprecation; T4 for material rewrite) |
| Who audits linkage | The Board — monthly intent–assumption audit, event-driven on material change (operating model §8.1) |
| Missing link | Blueprint without an active-intent link → Pending decommission queue |
| Failed assumption | Board opens redesign/decommission tickets for every dependent blueprint |
| Zombie definition | Running service, no active intent, no approved exception |
| Implementation churn | Swapping one product for another updates blueprints + A5 evidence, **not** the domain intent text |

## Decision log

| Date | Change | Why |
|------|--------|-----|
| — | *(instance keeps its own dated log here)* | — |
