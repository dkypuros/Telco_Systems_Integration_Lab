# Standards Release Tracking Procedure

Purpose: keep source code, tests, and claims mapped to the standards releases they target.

## Step mechanism

For every standard/API/interface used by the lab:

1. **Refresh official baseline**
   - Check the official source, not memory.
   - Record `latest_open_or_active` and `latest_frozen_or_stable` separately.
   - For O-RAN, refresh per WG/spec/interface.

2. **Snapshot evidence**
   - Record `official_evidence_checked_at`.
   - Record the official URL.
   - Save or reference an evidence snapshot path under `traceability/evidence_snapshots/`.

3. **Record local tested-against baseline**
   - Capture the standard version/release the local source is actually tested against.
   - Link to local test evidence, e.g. CTK JSON, build log, compliance report, or test file.
   - Do not turn smoke tests or demos into formal conformance claims.

4. **Calculate the gap**
   - Compare latest official baseline to local tested-against baseline.
   - Mark gap as `none`, `minor_asset_update`, `major_version_gap`, `formal_conformance_missing`, or `unknown_requires_audit`.

5. **Choose next step**
   - Examples: preserve as reference, copy docs only, add conformance tests, update CTK, audit clauses, or defer.

6. **Only then update code/tests**
   - Source code changes happen after release mapping and acceptance criteria are explicit.

## Required register fields

- `standards_body`
- `standard_family`
- `spec_id`
- `interface_or_api`
- `latest_open_or_active`
- `latest_frozen_or_stable`
- `stable_target_baseline`
- `local_tested_against`
- `local_test_evidence_path`
- `implementation_path`
- `source_asset_version`
- `conformance_level`
- `known_gap_to_latest`
- `next_step`
- `official_source_url`
- `official_evidence_checked_at`
- `evidence_snapshot_path`
- `notes`
