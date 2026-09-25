# Example service

**Intent:** `example-service`
**Kind:** Service intent
**Status:** Draft (fictional worked example)
**Owner:** example-agent — Infrastructure class
**Parents:** I4, I6
**Beneficiary:** the declared users of the example estate

> This folder is a **fully fictional** worked example of a DEEP service
> fulfilment folder. It shows the shape a real instance copies: intent
> contract, operations, dependencies, evidence. Hosts `<host-a>` and
> `<host-b>` are placeholders; nothing here describes a real system.

## Human outcome

The example internal service stays available to its declared users: they can
reach it, authenticate, and complete their task. The architect should not need
to remember whether the service on `<host-a>` (primary) or its cold standby
on `<host-b>` is quietly drifting out of shape.

## Current state

This service is a draft example. In a real instance it becomes active only
when the owner, operational loop, evidence path, and funding decision are
accepted — and it is registered with a machine-readable manifest in
`intents/`. A healthy sweep is evidence that the declared conditions were
observed; it is not a claim that every possible service property is perfect.

## Read next

- [Intent contract](intent.md)
- [Operations](operations.md)
- [Dependencies](dependencies.md)
- [Evidence](evidence.md)
- [Catalog entry](../../intents/intent-catalog.json)
- [Governance workflow](../../docs/40-governance/infrastructure-operations-workflow.md)

## Lifecycle and funding

- Mode: managed service
- Sponsor: the example estate's master intent
- Beneficiary: declared internal users
- Funding: pending cost-ledger allocation
- Review: quarterly after acceptance
- Exit: replace the service owner and preserve a working recovery path
