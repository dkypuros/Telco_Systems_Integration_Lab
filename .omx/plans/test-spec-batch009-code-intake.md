# Test Spec: Batch 009 Code Intake Verification

## Required checks
1. Batch-009 rows are present and copied/verified in `traceability/copy_manifest.csv`.
2. Every batch-009 source exists and every destination exists under `services/` or `adapters/`.
3. Every source SHA-256 equals destination SHA-256 and manifest checksums.
4. Every copied Python file parses with `ast.parse`.
5. Report/tracker JSON parse and contain every batch-009 result.
6. Root target has no whole source workspace folders or excluded artifacts.
7. Architect verification approves the final state.
