# PRD: Batch 008 Mock Core/RAN Code Intake

## Objective
Copy the first curated set of actual mock 5G core and RAN simulator Python files into formal `services/` and `adapters/` buckets.

## Requirements
1. Use the batch-008 candidate manifest as the source of planned rows.
2. Append rows as planned before copying.
3. Validate source existence, destination safety, non-duplication, and exclusion policy.
4. Copy files with `shutil.copy2` only.
5. Record source/destination SHA-256 checksums in `traceability/copy_manifest.csv`.
6. Run Python AST parse verification on every copied batch-008 `.py` file.
7. Preserve copy-only byte identity; do not refactor imports or make runtime fixes.
8. Add a caveat that batch-008 is code intake, not runnable integration or formal conformance proof.

## Non-goals
- No runtime service launch.
- No dependency installation.
- No import/PYTHONPATH refactor.
- No formal standards conformance claim.
