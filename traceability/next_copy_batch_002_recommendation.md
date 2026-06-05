# Next Copy-Only Batch Recommendation: Evidence Batch 002

Date: 2026-06-05
Target lab: `<LAB_ROOT>`
Source umbrella: `<SOURCE_5G_LAB_SIMULATOR_ROOT>`
Status: recommendation only; no files copied in this batch recommendation step.

## Selection rule

Prioritize standards/release mapping evidence before source code:

1. TM Forum CTK collections/environments and reproducibility docs.
2. O-RAN coverage matrices and machine-readable coverage snapshots.
3. 3GPP/5G specification mapping evidence.
4. Defer runtime code, app code, bulk folders, generated caches, and environment-specific files.

## Ready source-to-destination candidates

All source files below were checked for existence on 2026-06-05.

| Priority | Source | Recommended destination | Reason | Risk / label |
|---:|---|---|---|---|
| 1 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/specs/tmforum_standards/CTK-TMF641-ServiceOrdering/ctk/CTK-TMF641-ServiceOrdering-R18-5.postman_collection.json` | `traceability/evidence_snapshots/tmf641-r18.5-ctk-collection.json` | TMF641 Service Ordering CTK collection for release-labeled test surface. | Evidence-only; do not claim official v5 conformance from this alone. |
| 2 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/specs/tmforum_standards/CTK-TMF641-ServiceOrdering/ctk/CTK-TMFENV-V3.0.0.postman_environment.json` | `traceability/evidence_snapshots/tmf641-r18.5-ctk-environment.json` | CTK execution environment for reproducibility. | Environment version must be tied to the CTK run/version it supports. |
| 3 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/specs/tmforum_standards/CTK-TMF641-ServiceOrdering/README.md` | `traceability/requirements/tmf641-ctk-readme.md` | README support artifact for CTK usage and reproducibility. | Reference evidence only; not a test result. |
| 4 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/specs/tmforum_standards/CTK-TMF638-ServiceInventory/ctk/CTK-TMF638-ServiceInventory-R18-5.postman_collection.json` | `traceability/evidence_snapshots/tmf638-r18.5-ctk-collection.json` | TMF638 Service Inventory CTK collection for gap and release mapping. | Register currently treats TMF638 as missing implementation; label coverage/gap evidence only. |
| 5 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/specs/tmforum_standards/CTK-TMF638-ServiceInventory-R18-0/ctk/CTK-TMF638-ServiceInventory-R18-5.postman_collection.json` | `traceability/evidence_snapshots/tmf638-r18-alt-ctk-collection.json` | Alternate R18-family TMF638 CTK collection for release reconciliation. | Potential duplicate functional intent with priority 4; dedupe before claims. |
| 6 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/specs/tmforum_standards/CTK-TMF638-ServiceInventory-R16.5/ctk/TMForum.postman_environment.json` | `traceability/evidence_snapshots/tmf638-r16.5-ctk-environment.json` | Legacy TMF638 environment evidence for version comparison. | Historical/reference only; likely semantic drift vs R18. |
| 7 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/oran-compliance.md` | `traceability/requirements/bf3-oran-compliance-matrix.md` | O-RAN compliance/coverage matrix for WG and spec mapping. | Derived evidence; verify recency before external claims. |
| 8 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/oran-architecture.md` | `traceability/requirements/bf3-oran-enhancement-architecture.md` | Architecture-to-module map for O-RAN enhancement scope. | Architecture claims need implementation/transport caveats. |
| 9 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/oran/oran_spec_coverage.json` | `traceability/evidence_snapshots/oran-spec-coverage.json` | Machine-readable O-RAN coverage snapshot for future diffing. | Snapshot can go stale; preserve hash and source date when copied. |
| 10 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/spec-analysis/3_Complete-Specification-Map.txt` | `traceability/requirements/bf3-complete-specification-map.txt` | High-level 3GPP/5G specification map. | Coverage-map evidence, not conformance proof. |

## Not-copy-yet / exclusion notes

- Do not copy source code in the next batch unless a manifest row explicitly identifies a small, reviewed standards adapter/service boundary.
- Do not copy whole project folders such as `Tech-Co/`, `BF3-5G-Demo/`, or `tmforum_psr_learning/`.
- Do not copy excluded folders/files from `traceability/exclusion_policy.md`: `.git`, `.omx`, `.omc`, virtualenvs, `node_modules`, caches, local databases, and raw runtime artifacts.
- The originally suggested `TMF641B_Service_Ordering_Conformance_Profile_R18.0.0.pdf` was not found in the source tree and is not ready for copying.
- TMF641/TMF638 CTK collections/environments are test-surface/reference evidence unless paired with actual CTK execution outputs.

## Suggested manifest handling when this batch is approved

Append these as planned rows first, with:

- `copy_batch_id=evidence-batch-002`
- `copy_method=shutil.copy2`
- `verified=false`
- `status=planned`
- notes that distinguish CTK collections/environments, O-RAN derived coverage evidence, and 3GPP/5G coverage-map evidence from passed conformance results.
