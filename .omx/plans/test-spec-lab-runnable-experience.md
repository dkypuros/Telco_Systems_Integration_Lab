# Test Spec: Lab Runnable Experience

## Required checks
1. `./lab status` exits 0 and prints caveated status.
2. `./lab demo` exits 0 and prints runtime/test readiness summary.
3. `./lab up` exits 0, runs runtime smoke, and writes `build_logs/lab_up_runtime_smoke.json`.
4. `./lab test` exits 0, runs pytest, and writes `build_logs/lab_test_pytest.log`.
5. Existing tests still pass with `/tmp/telco_lab_runtime_venv/bin/python -m pytest -q tests`.
6. Copied source checksum identity remains preserved.
7. Ralph final report includes remaining risks and caveat boundaries.
