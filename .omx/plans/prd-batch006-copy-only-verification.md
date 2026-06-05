# PRD: Batch 006 Copy-Only Verification Continuation

## Objective
Continue curated standards-release-aware copy-only evidence intake through batch 006.

## Requirements
1. Finish batch-005 verification and summary.
2. Create a batch-006 recommendation from safe, not-yet-copied evidence artifacts.
3. Append batch-006 planned rows before copying.
4. Validate source existence, destination safety, artifact classification, and exclusion policy.
5. Copy only manifest-listed files using `shutil.copy2`.
6. Record source/destination SHA-256 checksums and mark copied rows verified.
7. Verify checksums, JSON report/tracker consistency, Python AST parseability, and Markdown link integrity.
8. Preserve copy-only byte identity for copied evidence; use separate caveat artifacts for claim hygiene.
9. Do not copy whole source folders or excluded artifacts.

## Non-goals
- No source-code migration.
- No formal standards conformance claims.
- No editing copied source evidence.
