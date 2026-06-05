# Stage 15 Code Testing Summary

Date: 2026-06-05

## Result

Initial repeatable code testing is in place and passing.

## Tests added

- `tests/unit/test_runtime_requirements.py`
  - Verifies runtime dependency declarations include packages imported by copied mock services.
  - Verifies runtime integration plan retains no-formal-conformance caveat language.
- `tests/regression/test_copy_identity.py`
  - Verifies copied manifest destinations exist and match recorded checksums.
  - Verifies copied source checksum equals destination checksum for copied rows.
  - Verifies copied Python files parse with `ast.parse`.
- `tests/integration/test_mock_runtime_smoke.py`
  - Runs `scripts/mock_service_smoke.py` in the active test Python environment.
  - Verifies AST/import smoke status is pass, with no missing dependencies or import errors.

## Commands run

```bash
/tmp/telco_lab_runtime_venv/bin/python scripts/mock_service_smoke.py
/tmp/telco_lab_runtime_venv/bin/python -m pytest -q tests/unit tests/regression tests/integration
/tmp/telco_lab_runtime_venv/bin/python -m pytest -q tests
```

## Evidence

- `build_logs/stage15_runtime_smoke_test.json`
- `build_logs/stage15_pytest_initial.log`
- `build_logs/stage15_pytest_all.log`
- `build_logs/stage15_test_report.json`

## Outcome

- Runtime smoke: PASS
- Copied Python AST count: 25
- Imported runtime targets: 23
- Missing dependencies: 0
- Import errors: 0
- Pytest: 5 passed

## Caveat

These tests validate runtime/import readiness, dependency declaration, AST parsing, and copy identity. They are not formal 3GPP, O-RAN, or TM Forum conformance tests.
