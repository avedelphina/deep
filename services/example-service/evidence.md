# Evidence

> Fictional worked example. See [README](README.md).

Every sweep or repair should emit structured evidence containing:

- intent ID and version;
- target asset and scope (e.g. `<host-a>` / `<host-b>`);
- operation ID and implementation version;
- scheduler or actor identity;
- start and finish timestamps;
- observed before and after state;
- probe results;
- snapshot or rollback reference where applicable;
- result: fulfilled, degraded, blocked, or failed;
- next action and deadline for non-fulfilled results.

In a real instance the machine-readable evidence contract lives in the
service's manifest under `intents/` (canonical example:
[`intents/infrastructure.json`](../../intents/infrastructure.json)). The
agent may summarise evidence, but narrative does not replace it.

## Evidence review

A running timer, open ticket, or successful command is not completion
evidence. Completion requires a fresh post-change version/health observation
from the target or an independent client. Missing or stale evidence is itself
a service exception.
