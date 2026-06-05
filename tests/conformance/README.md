# Conformance Test Scaffold

This directory is the only repo test bucket allowed to support future formal
standards-conformance claims. The current contents are a **claim gate scaffold**:
they validate that evidence artifacts and public wording stay bounded before any
future 3GPP, O-RAN, or TM Forum claim is promoted.

## Current status

- Current tests are readiness and policy checks, not formal conformance tests.
- Passing tests in this directory do not certify 3GPP, O-RAN, TM Forum, or vendor
  conformance by themselves.
- A future formal test must name the standard/API/spec release, implementation
  path, executable evidence path, conformance level, known gap, and next step.

## Promotion checklist

Before adding or promoting a conformance test, verify all of the following:

1. `traceability/standards_release_register.yaml` has a matching row.
2. The artifact under test has a copied/source identity record where applicable.
3. The test is executable in this repository or points to preserved official
   CTK/spec evidence.
4. The result is stored as a curated evidence artifact, not raw runtime output.
5. The public wording uses `candidate`, `reference`, or `readiness` until the
   full evidence gate is satisfied.
6. Known gaps to the latest open/active release remain explicit.

## Security and public-readiness note

Conformance evidence often contains environment URLs, tokens, subscriber IDs,
IMSI/SUPI-like values, or vendor-specific details. Curate and review evidence
before publication; raw logs, secrets, local databases, standards bundles, and
large vendor drops should stay out of git unless explicitly approved and
sanitized.
