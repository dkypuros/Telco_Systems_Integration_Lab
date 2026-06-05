# Next Copy-Only Batch Recommendation: Evidence Batch 003

Date: 2026-06-05
Target lab: `<LAB_ROOT>`
Source umbrella: `<SOURCE_5G_LAB_SIMULATOR_ROOT>`
Status: recommendation only; no batch-003 files copied yet.

## Selection rule

Batch 003 should keep prioritizing standards/release traceability and only include small boundary source files when they directly explain a standards interface. Do not copy app/runtime directories wholesale.

## Ready source-to-destination candidates

All source files below were checked for existence on 2026-06-05 and are not already present in `traceability/copy_manifest.csv` as copied source paths.

| Priority | Source | Recommended destination | Standards domain | Reason | Risk / label |
|---:|---|---|---|---|---|
| 1 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/specs_guide.md` | `traceability/requirements/tmf-specs-guide.md` | TM Forum; O-RAN; 3GPP | Consolidated guidance linking specs and implementation intent. | Narrative/mapping evidence only; validate against concrete conformance rows before claims. |
| 2 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/networking_specs_inventory.txt` | `traceability/requirements/networking-spec-inventory.txt` | 3GPP; TM Forum; O-RAN | Inventory of available spec set and expected coverage scope. | Inventory only; does not prove conformance or release maturity. |
| 3 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/build_logs/stage19_oran_closed_loop.md` | `traceability/evidence_snapshots/techco-stage19-oran-closed-loop.md` | O-RAN | Concrete O-RAN closed-loop behavior evidence for release-mapping validation. | Observed/demo behavior, not formal O-RAN certification. |
| 4 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/specs/tmforum_standards/CTK-TMF638-ServiceInventory-R18-0/README.md` | `traceability/requirements/tmf638-ctk-r18-0-readme.md` | TMF638 | CTK package context supporting the TMF638 gap in the release register. | README/package context only; no implementation proof. |
| 5 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/src/order_engine/app/adapters/o2ims_real_adapter.py` | `traceability/standards_mapping/oran-o2ims-real-adapter.py` | O-RAN O2IMS | Small boundary file showing interface/endpoint mapping useful for standards-release correlation. | Source-code mapping evidence only; corroborate behavior with tests/reports. |
| 6 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/src/order_engine/app/adapters/bf3_python_adapter.py` | `traceability/standards_mapping/bf3-python-adapter.py` | 3GPP-derived service orchestration/control-plane mapping | Small boundary file for BF3 interaction and operation semantics. | Operational workaround code can be mistaken for protocol compliance; keep interpretation conservative. |
| 7 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/tmforum_psr_learning/00_README.txt` | `references/learning_assets/tmforum-psr-learning-readme.txt` | TM Forum reference/learning | Context for TM Forum PSR learning artifacts already copied as reference-only evidence. | Reference-only; do not treat as conformance proof. |

## Excluded from the explorer suggestion

- `Tech-Co/build_logs/stage13_tmf_ctk_conformance.md` — already copied in batch 001 as `build_logs/stage13_tmf_ctk_conformance.md`.
- `BF3-5G-Demo/spec-analysis/5_Live-Spec-Compliance-Test-Results.txt` — already copied in batch 001 as `traceability/evidence_snapshots/bf3-live-spec-compliance-results.txt`.
- `Tech-Co/specs/tmforum_standards/CTK-TMF638-ServiceInventory-R18-0/ctk/README.md` — not present; corrected ready path is `Tech-Co/specs/tmforum_standards/CTK-TMF638-ServiceInventory-R18-0/README.md`.

## Not-copy-yet exclusions

- Do not copy full source trees such as `Tech-Co/src/`, `BF3-5G-Demo/`, `tmforum_psr_learning/`, or `open_source_5g_cores/`.
- Do not copy `.git`, `.omx`, `.omc`, virtualenvs, `node_modules`, caches, local DBs, generated build outputs, or raw logs.
- Do not copy bulk spec trees unless each file is listed as an explicit manifest row.
- Do not claim formal standards conformance from source code or narrative docs alone.

## Suggested manifest handling when this batch is approved

Append candidates as planned rows first, then run the same 5-step loop:

1. Validate planned rows.
2. Copy with `shutil.copy2`.
3. Record SHA-256 source/destination checksums.
4. Verify manifest/report/tracker and link integrity.
5. Run code review before any conformance claims.
