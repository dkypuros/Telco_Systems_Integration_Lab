# Evidence Batch 004 Claim Caveats

Date: 2026-06-05  
Batch: `evidence-batch-004`  
Recorded at: `2026-06-05T01:50:25Z`

## Purpose

Batch 004 intentionally preserves copied source artifacts exactly as they existed in the source workspace. Some copied artifacts contain strong source-language such as "100% compliance", "100% conformance", "fully implemented", or similar.

Those phrases are preserved as **source evidence**, not accepted as current lab conclusions.

## Caveat rule

For this lab, batch-004 artifacts are treated as:

- local run evidence,
- local documentation evidence,
- source-authored compliance mapping,
- source-generated reports,
- release-gap inputs.

They are **not** formal TM Forum, 3GPP, or O-RAN conformance proof unless separately tied to:

1. an official target release/version in `traceability/standards_release_register.yaml`,
2. executable test evidence for that target release/version,
3. preserved source/destination checksums,
4. a traceable test result or certification artifact,
5. explicit approval in a later conformance review.

## Claim-heavy artifacts identified

- `traceability/evidence_snapshots/techco-stage18-tmf620-lift.md`
- `traceability/evidence_snapshots/techco-stage31-docs-specs-verify.md`
- `traceability/requirements/legacy_5g_emulator-3gpp-compliance.md`
- `traceability/evidence_snapshots/legacy_5g_emulator-5g-emulator-compliance-report.txt`

## Interpretation

- TMF620/TMF622 CTK percentages remain local CTK evidence and must be mapped to the exact CTK/API major version.
- 3GPP "100%" language remains source-authored Release 16-era mapping evidence and must be reconciled against the current release register before external use.
- O-RAN run captures remain demo/functional evidence, not formal O-RAN Alliance certification.

## Handling instruction

Do not quote these artifacts as formal compliance claims in README, release notes, demos, or future conformance summaries without a new release-specific test/certification review.
