# Test Spec: Batch 008 Code Intake Verification

## Required checks
1. Batch-008 rows exist in `traceability/copy_manifest.csv` and are `status=copied`, `verified=true` after copy.
2. Every batch-008 source exists and every destination exists under `services/` or `adapters/`.
3. Every batch-008 source SHA-256 equals destination SHA-256 and manifest checksum values.
4. Every copied batch-008 Python file parses with `ast.parse`.
5. Batch report and tracker JSON parse and contain every batch-008 result.
6. Root target does not contain whole source workspace folders or excluded artifacts.
7. Architect verification approves the final state.
