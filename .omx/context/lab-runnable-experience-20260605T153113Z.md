# Ralph Context Snapshot: Lab Runnable Experience Fix

## Task statement
User is frustrated that the Telco Systems Integration Lab has too much scaffolding and not enough runnable value. They asked to "fix it on ralph loop".

## Desired outcome
Add a small, obvious command surface so the lab feels runnable:

- `./lab up` prepares a disposable runtime environment and runs smoke checks.
- `./lab test` runs the repeatable test suite.
- `./lab status` shows current evidence/status.
- `./lab demo` prints a concise demo-oriented status from smoke/test evidence.

## Known facts/evidence
- Lab root: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_Telco_Systems_Integration_Lab`.
- Current work has copy-only intake through batch 009 and runtime smoke/testing through batch 010/stage15.
- `scripts/mock_service_smoke.py` passes with dependencies installed in `/tmp/telco_lab_runtime_venv`.
- Pytest suite under `tests/` passes: 5 tests.
- The lab must preserve copied source byte identity and avoid false conformance claims.

## Constraints
- Do not edit copied source files under `services/mock_5g_core`, `adapters/mock_ran`, or `adapters/mock_oran`.
- Do not claim formal 3GPP/O-RAN/TM Forum conformance.
- Keep new wrapper tooling small, reversible, and evidence-producing.
- Use disposable venv outside the repo for dependencies.

## Unknowns/open questions
- Whether user ultimately wants full service launching (`lab up` starting daemons) or a readiness workflow. For safety, implement `up` as environment prepare + smoke readiness, not long-running daemon orchestration.

## Likely touchpoints
- `lab` executable wrapper
- `scripts/lab_cli.py`
- `docs/runtime_integration_plan.md`
- `tests/integration/`
- `build_logs/`
- `traceability/`
