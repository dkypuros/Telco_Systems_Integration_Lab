# Ralph Context Snapshot: Batch 009 Remaining Mock Core/RIC/O-RAN Code Intake

## Task statement
Continue the Ralph loop after batch 008 by copying the next safe code-intake slice, then verify checksums and Python AST parses until clean.

## Desired outcome
- Add planned rows for remaining mock 5G core functions and RIC/O-RAN support files.
- Copy byte-identical source files into `services/` and `adapters/` buckets.
- Record source/destination checksums in `traceability/copy_manifest.csv`.
- Verify all copied Python files parse with `ast.parse`.
- Preserve copy-only and caveat runtime/conformance claims.

## Known facts/evidence
- Batch 008 copied AMF, SMF, UDR, NSSF, config, transport, gNB, CU, DU.
- Batch 008 suggested a later batch for NRF, UPF, UDM, AUSF, RIC files, E2SM files, and O-RAN gateway files.
- Target lab: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_Telco_Systems_Integration_Lab`
- Canonical source root: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API`

## Constraints
- Copy-only; do not edit copied source files.
- Do not refactor imports or install dependencies.
- Do not run services.
- Do not copy virtualenvs, caches, `.pyc`, logs, DB files, or whole directories.
- Code intake is not formal standards conformance proof.

## Likely touchpoints
- `traceability/copy_manifest.csv`
- `traceability/batch_009_code_intake_candidate_manifest.csv`
- `traceability/evidence_batch_009_copy_report.json`
- `traceability/evidence_batch_009_review_summary.md`
- `.omx/ultragoal/copy-batches/2026-06-05-evidence-batch-009.json`
- `services/mock_5g_core/core_network/`
- `adapters/mock_ran/ran/ric/`
- `adapters/mock_oran/`
