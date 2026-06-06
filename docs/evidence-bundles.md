# Evidence bundles and correlation IDs

Evidence bundles are public-safe summaries that connect a scenario run to its
inputs, touched services/adapters, standards rows, evidence label, known gaps,
and artifact paths.

The schema lives at
[`traceability/evidence_bundle.schema.json`](../traceability/evidence_bundle.schema.json).
A minimal example lives at
[`traceability/evidence_snapshots/example-mvp-evidence-bundle.json`](../traceability/evidence_snapshots/example-mvp-evidence-bundle.json).

## Correlation ID convention

- Every end-to-end scenario starts with one `correlation_id`.
- The storefront/client, catalog, order engine, orchestration, adapters, mock
  core/RAN/O-RAN services, tests, and evidence snapshots should propagate that
  value in request metadata or logs.
- Evidence artifacts should record the same `correlation_id`, plus order/service
  identifiers when available.

## Claim boundary

Evidence bundles support `functional_smoke` or `demo_evidence` only within the
recorded scope. They do not prove formal 3GPP, O-RAN, or TM Forum conformance
unless promoted through the release register, executable tests, and the claim
hygiene policy.

## Public-safety requirements

Evidence bundles must not contain:

- private local paths such as user home directories;
- secrets, tokens, credentials, keys, certs, or cookies;
- raw standards documents;
- unsupported wording such as `production-ready`, `certified`, or
  `release-complete`.
