# Dependencies and boundaries

> Fictional worked example. See [README](README.md).

## Parent intents

- I4 — Cloud-parity services (the example service is one covered class)
- I6 — Documented, rebuildable operations

## Owned capability

The owning infrastructure-class agent owns the availability conditions listed
in [`intent.md`](intent.md) for the service on `<host-a>` and its standby on
`<host-b>`.

## Related service boundary

Application feature work belongs to the Coding class (artifacts and
deployment contracts, never direct production mutation); functional
acceptance belongs to the Business class. A feature problem that requires
host, storage, network, DNS, or access work becomes an infrastructure
exception for this service's owner. A healthy host with a broken
user-facing feature remains a Business/Coding issue.

## External dependencies

- approved host inventory and access paths for `<host-a>` and `<host-b>`;
- scheduler and structured evidence destination;
- backup and restore systems for the service data volume;
- DNS names and certificate authority for the service endpoint;
- cost-ledger allocation when this service is accepted and funded.
