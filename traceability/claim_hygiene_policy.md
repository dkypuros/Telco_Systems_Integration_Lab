# Claim Hygiene Policy

This lab must not make standards claims that outrun evidence.

## Required evidence for standards claims

Any use of terms like `100%`, `compliant`, `conformance`, `release-complete`, `O-RAN complete`, `3GPP compliant`, or `TMF compliant` must reference:

1. a row in `traceability/standards_release_register.yaml`,
2. the `local_tested_against` baseline,
3. a `local_test_evidence_path`,
4. a clear `conformance_level`,
5. a `known_gap_to_latest`, and
6. an executable conformance test path when claiming formal conformance.

## Allowed labels

- `reference_only`
- `planned`
- `partial`
- `functional_smoke`
- `demo_evidence`
- `formal_conformance_missing`
- `conformance_candidate`
- `formal_conformance_evidence`

## Forbidden shortcuts

- Do not infer v5 TM Forum conformance from v4 CTK evidence.
- Do not infer O-RAN conformance from HTTP-mock closed-loop demos.
- Do not infer 3GPP release conformance from marketing docs or file names.
- Do not treat UI validation/mock panels as protocol validators.

## Promotion rule

A copied summary can be promoted from reference to conformance evidence only after it has:

- a release-register row,
- a copy-manifest row marked copied and verified,
- a conformance test or official CTK result,
- a preserved evidence snapshot, and
- a reviewed gap-to-latest decision.
