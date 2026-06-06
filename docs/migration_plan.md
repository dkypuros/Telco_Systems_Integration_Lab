# Copy-Only Migration Plan

## Decision

Create a new formal lab root at `9.LABS_Telco_Systems_Integration_Lab` using copy-only intake, release tracking, and mandatory traceability.

## Principles

1. Copy only. Do not move, rename, or delete existing source material.
2. Track official latest standards separately from local tested-against baselines.
3. Do not update source code until a gap and next conformance step are recorded.
4. Keep canonical models separate from standard-native models.
5. Only `tests/conformance/` can support standards conformance claims.
6. O-RAN is tracked per WG/spec/interface, not as one global version.
7. TM Forum API spec version and CTK/RI asset version are tracked separately.

## First-pass source workspaces

- `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co`
- `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator`
- `<SOURCE_5G_LAB_SIMULATOR_ROOT>/tmforum_psr_learning`
- `<SOURCE_5G_LAB_SIMULATOR_ROOT>/open_source_5g_cores`
- `<SOURCE_5G_LAB_SIMULATOR_ROOT>/5G_Wireline_Simulator`
- `<USER_HOME>/Documents/Git_Offline/active/9.LABS_telco_soup_to_nuts`

## Migration sequence

1. Refresh standards release register from official sources.
2. Record evidence snapshot date and URL/path.
3. Inventory source artifact and classify it.
4. Record local tested-against baseline and evidence path.
5. Decide target bucket and copy eligibility.
6. Copy only curated artifact batches.
7. Verify copy integrity and update copy manifest.
8. Only after traceability and gap are explicit, consider code/test updates.

## Do not copy by default

- `.git/`, `.omc/`, `.omx/`
- `node_modules/`, `venv/`, `.venv/`, `test_venv/`
- `__pycache__/`, `.pytest_cache/`, `.next/`
- PID files, raw runtime logs unless curated, build outputs
- SQLite/db files unless explicitly retained as evidence
- `.DS_Store`
