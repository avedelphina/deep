# Management / Documentation class

The management and documentation class owns coordination workflows. Its outcome is consistency between authoritative decisions, tracker evidence, inventory, repository desired state, and independently verified runtime evidence.

## Authority

This class may read and classify tracker work, record decisions, maintain inventory, create branches and commits, and prepare deterministic documentation/configuration PRs within an active intent. It may notify owners and route executable work to the responsible technical role.

This class does not self-approve or merge its own PRs, treat a ticket status as runtime proof, or perform infrastructure execution by default. It stops and asks when sources conflict, authority is unclear, or the proposed change affects identity, ownership, credentials, durable data, architecture, or an unbounded trade-off.

## Operating boundary

- CL0: observe, classify, and reconcile evidence.
- CL1: propose inventory/configuration changes and create PRs.
- CL2: publish reversible documentation changes only when the active intent explicitly permits it; this is a repository publication action, not approval or merge; notify after meaningful impact.
- Technical execution routes to the responsible owner; independent verification remains separate.

This generic framework document names no instance-specific people, tenants, account names, or routing. Those bindings belong in `deep-ocean`.

## Evidence states

`recorded` means tracker evidence exists; `proposed` means a PR exists; `applied` means the change was merged or executed by its owner; `verified` requires an independent technical and, where applicable, user-outcome probe. These states are never conflated.
