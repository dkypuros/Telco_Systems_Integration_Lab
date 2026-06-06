# Standards-traceable issue authoring

Use the GitHub issue form in `.github/ISSUE_TEMPLATE/capability-slice.yml` for
work derived from the [End-to-End Telco Capability Blueprint](end-to-end-telco-capability-blueprint.md).

Every standards-related issue must include:

- capability slice name;
- affected standards family and release-register row or planned row;
- current and target canonical evidence labels;
- implementation paths the issue may edit;
- tests/evidence the issue must produce;
- explicit known gap to latest or formal conformance;
- explicit statement that no full upstream project should be copied.

Allowed standards-evidence labels are defined in
[`traceability/claim_hygiene_policy.md`](../traceability/claim_hygiene_policy.md):

- `reference_only`
- `planned`
- `partial`
- `functional_smoke`
- `demo_evidence`
- `formal_conformance_missing`
- `conformance_candidate`
- `formal_conformance_evidence`

External implementation terms from
[ADR 0001](adr/0001-external-implementation-profiles.md), such as
`external implementation profile` or `interoperability target`, describe runtime
roles. They are not standards-conformance labels.

## Default verification floor

Use the command-level gates in the capability blueprint unless the issue gives a
narrower justified subset. Public-facing, standards, source-intake, and
traceability issues should also run the public-safe scans from `AGENTS.md`.
