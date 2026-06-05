# Ralph Context Snapshot: Batch 006 Copy-Only Verification Loop

## Task statement
Continue the Telco Systems Integration Lab copy-only evidence intake, produce and execute the batch-006 recommendation, and run a Ralph verification loop to ensure all checksums, Python AST parses, and Markdown links are clean.

## Desired outcome
- Batch-005 is verified and summarized.
- Batch-006 recommendation is created from remaining safe evidence candidates.
- Batch-006 planned rows are appended, validated, copied with `shutil.copy2`, checksummed, and verified.
- No original source workspace is modified.
- No bulk source folders, caches, virtualenvs, `.git`, `.omx`, `node_modules`, or generated/runtime artifacts are copied.
- Ralph verification produces fresh evidence for checksums, AST parses, Markdown links, manifest/report/tracker consistency, and architect sign-off.

## Known facts/evidence
- Target lab: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_Telco_Systems_Integration_Lab`
- Source umbrella: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator`
- Batch-004 finished with 35 copied/verified rows.
- Batch-005 rows 036-045 have been copied and require final verification/caveat/summary.
- Existing guardrail artifacts include `traceability/exclusion_policy.md`, `traceability/copy_manifest.csv`, and release/claim hygiene policies.

## Constraints
- Copy-only: source artifacts must not be edited, moved, or deleted.
- Copied artifacts should remain byte-identical to sources; caveats go in separate traceability files.
- Formal TM Forum/3GPP/O-RAN conformance must not be claimed without release-specific executable evidence.
- Ralph deslop/cleanup must not mutate copied source evidence because that would violate copy-only integrity.

## Unknowns/open questions
- Which remaining source artifacts are best for batch-006 after batch-005 is verified.
- Whether batch-006 Markdown artifacts need link-fix copies or caveats.
- Whether batch-006 contains Python files requiring AST parse checks.

## Likely touchpoints
- `traceability/copy_manifest.csv`
- `traceability/evidence_batch_005_*`
- `traceability/evidence_batch_006_*`
- `.omx/ultragoal/copy-batches/2026-06-05-evidence-batch-006.json`
- `traceability/next_copy_batch_006_recommendation.md`
- `traceability/next_copy_batch_007_recommendation.md`
