# Test Spec: Batch 006 Copy-Only Verification

## Required checks
1. Manifest row count and statuses: all copied rows have `status=copied` and `verified=true` after execution.
2. For every batch-006 row: source exists, destination exists, destination is under target lab, SHA-256 source equals SHA-256 destination and manifest values.
3. Report/tracker JSON parse successfully and contain all batch-006 results.
4. Python copied artifacts parse with `ast.parse` where present.
5. Markdown copied artifacts have no unresolved local relative links, or link-fix/caveat artifacts are explicitly recorded.
6. Claim-heavy language is caveated outside copied artifacts.
7. Root target does not contain whole source workspace folders or excluded artifacts.
8. Architect verification approves the final state.
