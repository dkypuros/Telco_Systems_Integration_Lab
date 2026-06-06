# Adapter contract template

Use this checklist before writing runtime-specific adapter code.

## Boundary

- Adapter name:
- Capability slice:
- Lab-owned path:
- External profile path, if any:
- External runtime required: yes/no

## Standards and evidence

- Standards family/spec/API:
- Release-register row:
- Current evidence label:
- Target evidence label:
- Known gap to latest/formal conformance:

## Inputs

- Accepted request shape:
- Required identifiers:
- Correlation ID behavior:
- Validation failures:

## Outputs

- Success response shape:
- Error response shape:
- Evidence fields emitted:
- External-runtime skip behavior:

## Ownership guardrails

- Adapter code remains lab-owned.
- Full upstream source remains outside the repository.
- External runtime behavior is proven only through pinned-profile
  interoperability tests.
- No standards-conformance claim is promoted without release-register rows,
  executable evidence, and claim-hygiene review.
