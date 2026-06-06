# Team Mapping Summary

Date: 2026-06-05
Scope: Copy-only source-to-bucket mapping for Telco Systems Integration Lab.

No original source files were moved or deleted. This file records copy candidates and priorities only.

## Lane 1: Tech-Co

High-priority candidates:

- TMF620 CTK evidence: `Tech-Co/specs/tmforum_standards/CTK-TMF620-ProductCatalog/jsonResults.json`
  - Target: `traceability/`, `specs/tmforum/`, `tests/conformance/`
  - Tested against: local TMF620 v4 CTK evidence, Tech-Co reports 1421/1421.
- TMF622 CTK evidence: `Tech-Co/specs/tmforum_standards/CTK-TMF622-ProductOrdering/jsonResults.json`
  - Target: `traceability/`, `specs/tmforum/`, `tests/conformance/`
  - Tested against: local TMF622 v4 CTK evidence, Tech-Co reports 63/63.
- TMF runtime entrypoints:
  - `Tech-Co/src/catalog_api/app/api/tmf620.py`
  - `Tech-Co/src/order_engine/app/api/tmf622.py`
  - `Tech-Co/src/order_engine/app/api/tmf641.py` (partial)
- O-RAN/3GPP evidence:
  - `Tech-Co/build_logs/stage13_tmf_ctk_conformance.md`
  - `Tech-Co/build_logs/stage25_oran_run_capture.md`
  - `Tech-Co/build_logs/stage1_legacy_5g_emulator_verification.md`
  - `Tech-Co/scripts/demo_oran_closed_loop.sh`
  - `Tech-Co/src/order_engine/app/adapters/o2ims_real_adapter.py`

Important caveat:
- 3GPP evidence is functional smoke, not full formal protocol conformance.
- O-RAN closed-loop evidence is demo/functional unless mapped per WG/spec/interface.

## Lane 2: legacy-standalone-5g-emulator

High-priority candidates:

- `legacy-standalone-5g-emulator/spec-analysis/5_Live-Spec-Compliance-Test-Results.txt`
  - Target: `traceability/evidence_snapshots/`
  - Best caveat artifact because it includes PASS/PARTIAL/NOT TESTED.
- `legacy-standalone-5g-emulator/spec-analysis/1_Spec-to-Code-Analysis.txt`
  - Target: `traceability/requirements/`, `traceability/coverage/`
- `legacy-standalone-5g-emulator/docs/3gpp-compliance.md`
  - Target: `traceability/conformance_matrix/`, `docs/`
  - Caveat: self-asserted/marketing style, corroborate before claims.
- `legacy-standalone-5g-emulator/docs/oran-compliance.md`
  - Target: `traceability/coverage/`, `docs/`
- O-RAN mapping engine:
  - `open-digital-platform-2_0/clean_5g_emulator_api/oran/o_ran_spec_map.py`
  - `open-digital-platform-2_0/clean_5g_emulator_api/oran/oran_spec_coverage.json`
- Test candidates:
  - `open-digital-platform-2_0/clean_5g_emulator_api/test_oran_compliance.py`
  - `open-digital-platform-2_0/test_100_compliance.py`
- Service candidates:
  - `open-digital-platform-2_0/clean_5g_emulator_api/main.py`
  - `open-digital-platform-2_0/clean_5g_emulator_api/core_network/amf.py`
  - `open-digital-platform-2_0/clean_5g_emulator_api/core_network/upf_enhanced.py`
  - representative O-RAN files under `ran/ric/`, `smo/`, and gateway.

Important caveat:
- Do not copy `node_modules`, `.next`, venv/test_venv, caches, db files, generated outputs, runtime logs.

## Lane 3: Supporting sources

High-priority candidates:

- `tmforum_psr_learning`
  - Target: `references/learning_assets/`, `specs/tmforum/`, `tests/unit/`, `docs/`
  - Evidence: 30 spec tests passed per `06_test_results.txt`.
- `5G-AI-middleware/falsifiable_test`
  - Target: `experimental/ai_middleware/`, `tests/integration/`, `tests/unit/`, `tests/fixtures/`
  - Evidence: falsification test docs and real-results artifacts.
- `open_source_5g_cores`
  - Target: `references/open_source_cores/`, `vendor_profiles/free5gc/`, `vendor_profiles/open5gs/`
  - Caveat: reference only; do not bulk copy without explicit profile scope.
- `5G_Wireline_Simulator/00_simulator_requirements.txt`
  - Target: `experimental/wireline_convergence/`, `docs/`, `specs/3gpp/`
- `AI_Human_Collaboration`
  - Target: `docs/`, `references/source_workspaces/`, `capabilities/*`
- `michael-softbank`
  - Target: `vendor_profiles/nvidia_bluefield/`, `experimental/wireline_convergence/`, `docs/`

## Exclusion summary

Do not copy unless explicitly curated:

- `.git/`, `.omc/`, `.omx/`
- `node_modules/`, `.next/`
- `venv/`, `.venv/`, `test_venv/`
- `__pycache__/`, `.pytest_cache/`
- raw runtime logs, PID files, generated build outputs
- `*.db` unless retained as evidence
- `.DS_Store`

## Next copy batch recommendation

Start with evidence and traceability, not implementation:

1. Tech-Co TMF620/TMF622 CTK JSON results and stage13 log.
2. legacy standalone 5G emulator live compliance results and spec-to-code analysis.
3. O-RAN coverage map docs/JSON/Python mapping file.
4. tmforum_psr_learning docs/test results.
5. Only after the above are mapped, copy service entrypoints in small batches with tests.

Authoritative release/conformance status lives in `traceability/standards_release_register.yaml`; this file is a derived view.
