# Repository Review Policy

**Status:** Active policy for the canonical DEEP framework repository  
**Scope:** Pull requests against `OCEAN/deep` `main`

The `deep` repository is the canonical DEEP governance framework. Changes to
its authority model, clearance rules, destructive-action policy, agent classes,
independence rules, or governance contracts are framework changes, not routine
instance documentation.

## Review gates

Every pull request requires Alice's governance review. Alice may request
additional technical reviews from the owner of the affected boundary.

A framework-sensitive pull request also requires Tom's explicit formal approval
on the exact current head. The authorized autopilot may merge only after all
required reviews are formally `APPROVED`, no official review request remains,
no active exact-head `REQUEST_CHANGES` review exists, CI is green, and the pull
request is open, non-draft, and forge-mergeable.

The original author does not approve their own pull request. Anikke's merge
permission is execution authority only; it is not a review or approval.

## Framework-sensitive paths

The machine-readable list in
[`repository-review-policy.json`](../../config/repository-review-policy.json)
is authoritative for path classification. It covers:

- the clearance and operating model;
- agent classes and independent gates;
- decision boundaries, master intent, and governance contracts;
- autonomy, reconciliation, and intent manifests/validators;
- the review-policy workflow and its contract.

A pull request that changes a file outside that list remains subject to Alice
and selected technical reviewers, but does not acquire the Tom gate merely
because it is in the canonical repository.

This policy controls repository merge eligibility. It does not authorize a
runtime operation, credential change, deployment, data movement, or destructive
operation. Those actions retain their separate DEEP clearance and approval
requirements.
