# Next Copy-Only Batch Recommendation: Evidence Batch 004

Date: 2026-06-05
Target lab: `<LAB_ROOT>`
Source umbrella: `<SOURCE_5G_LAB_SIMULATOR_ROOT>`
Status: recommendation only; no batch-004 files copied yet.

## Selection rule

Batch 004 should add higher-signal test/run evidence and standards-facing documentation, still avoiding bulk source trees and formal conformance claims.

## Ready source-to-destination candidates

All source files below were checked for existence on 2026-06-05 and are not already present in `traceability/copy_manifest.csv` as copied source paths.

| Priority | Source | Recommended destination | Standards domain | Reason | Risk / label |
|---:|---|---|---|---|---|
| 1 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/build_logs/stage18_tmf620_lift.md` | `traceability/evidence_snapshots/techco-stage18-tmf620-lift.md` | TM Forum TMF620 | Captures TMF620 lift/modernization evidence after v4 CTK preservation. | Implementation/lift evidence only; do not claim TMF620 v5 conformance without v5 CTK run. |
| 2 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/build_logs/stage25_oran_run_capture.md` | `traceability/evidence_snapshots/techco-stage25-oran-run-capture.md` | O-RAN | Run-capture evidence to pair with O-RAN closed-loop mapping. | Demo/run evidence, not formal O-RAN certification. |
| 3 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/build_logs/stage31_docs_specs_verify.md` | `traceability/evidence_snapshots/techco-stage31-docs-specs-verify.md` | TM Forum; O-RAN; 3GPP | Evidence of docs/specs honesty/verification stage. | Documentation verification evidence only; not protocol conformance. |
| 4 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/3gpp-compliance.md` | `traceability/requirements/bf3-3gpp-compliance.md` | 3GPP | Detailed 3GPP compliance mapping for BF3 material. | Check relative links if copied; claims must be reconciled to release register. |
| 5 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/docs/compliance_report.txt` | `traceability/evidence_snapshots/bf3-5g-emulator-compliance-report.txt` | 3GPP; O-RAN | Concrete emulator compliance report complementing existing BF3 spec maps. | Source-generated report; validate scope/release before external claims. |
| 6 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/spec-analysis/2_Depth-of-Understanding.txt` | `traceability/requirements/bf3-depth-of-understanding.txt` | 3GPP; O-RAN | Explains source understanding and mapping depth behind spec/code claims. | Narrative analysis, not proof. |
| 7 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/spec-analysis/4_Specification-Map-Index.txt` | `traceability/requirements/bf3-specification-map-index.txt` | 3GPP; O-RAN | Index artifact for the already copied complete specification map. | Index/mapping evidence only. |
| 8 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/components/oran_o2ims.md` | `traceability/requirements/techco-oran-o2ims-component.md` | O-RAN O2IMS | Component-level explanation for O2IMS boundary copied in batch 003. | Documentation evidence; corroborate with run captures/tests. |
| 9 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/components/catalog_api.md` | `traceability/requirements/techco-catalog-api-component.md` | TM Forum TMF620 | Component-level explanation for catalog/TMF620 surface. | Documentation evidence; do not claim v5 conformance without v5 CTK. |
| 10 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/5G_Wireline_Simulator/00_simulator_requirements.txt` | `experimental/wireline_convergence/5g-wireline-simulator-requirements.txt` | 3GPP; transport/wireline convergence | Keeps wireline convergence separated as experimental/reference material. | Reference/requirements only; not current telco conformance evidence. |

## Not-copy-yet exclusions

- Do not copy full directories: `Tech-Co/docs/`, `Tech-Co/src/`, `BF3-5G-Demo/`, `open_source_5g_cores/`, or `5G_Wireline_Simulator/`.
- Do not copy caches, virtualenvs, `node_modules`, `.git`, `.omx`, local DBs, generated outputs, or uncurated runtime logs.
- If Markdown files contain local relative links, either copy required linked files under matching relative names or record a deliberate caveat before approval.
- Do not claim formal TM Forum, 3GPP, or O-RAN conformance from documentation/run captures alone.

## Suggested manifest handling when this batch is approved

Append candidates as planned rows first, then run the same loop:

1. Validate planned rows.
2. Copy with `shutil.copy2`.
3. Record SHA-256 source/destination checksums.
4. Verify manifest/report/tracker and Markdown link integrity.
5. Review conformance-claim hygiene before approval.
