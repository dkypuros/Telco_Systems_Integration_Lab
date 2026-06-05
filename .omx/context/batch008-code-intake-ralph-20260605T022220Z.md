# Ralph Context Snapshot: Batch 008 Mock Core/RAN Code Intake

## Task statement
Continue with batch-008 recommendation, execute copy operations, and run the Ralph verification loop to confirm AST parses cleanly.

## Desired outcome
- Batch-008 code-intake rows are added to `traceability/copy_manifest.csv` as planned first.
- Actual mock core network functions are copied into `services/mock_5g_core/`.
- RAN simulator files are copied into `adapters/mock_ran/`.
- All copied files are byte-identical to sources and have recorded SHA-256 checksums.
- Python AST parse checks pass for every copied batch-008 `.py` file.
- No source workspace files are edited, moved, or deleted.

## Known facts/evidence
- Target lab: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_Telco_Systems_Integration_Lab`
- Canonical source root: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API`
- Batch-008 recommendation exists at `traceability/next_copy_batch_008_recommendation.md`.
- Candidate manifest exists at `traceability/batch_008_code_intake_candidate_manifest.csv`.
- Candidate files were prechecked as AST-clean.

## Constraints
- Copy-only: do not edit copied source files.
- Code intake is not runtime integration.
- Do not add dependencies.
- Do not copy virtualenvs, caches, `.pyc`, logs, DB files, or whole directories.
- Mock code is functional simulation/source intake, not 3GPP/O-RAN conformance proof.

## Likely touchpoints
- `traceability/copy_manifest.csv`
- `traceability/evidence_batch_008_copy_report.json`
- `traceability/evidence_batch_008_review_summary.md`
- `.omx/ultragoal/copy-batches/2026-06-05-evidence-batch-008.json`
- `services/mock_5g_core/`
- `adapters/mock_ran/`
