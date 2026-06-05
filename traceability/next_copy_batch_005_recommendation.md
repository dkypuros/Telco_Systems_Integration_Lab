# Next Copy-Only Batch Recommendation: Evidence Batch 005

Date: 2026-06-05  
Target lab: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_Telco_Systems_Integration_Lab`  
Source umbrella: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator`  
Status: recommendation only; no batch-005 files copied yet.

## Selection rule

Batch 005 should add remaining high-signal verification logs and component documentation that connect the copied standards evidence to network functions. Continue avoiding bulk source trees.

## Ready source-to-destination candidates

All source files below were checked for existence on 2026-06-05 and are not already present in `traceability/copy_manifest.csv` as copied source paths.

| Priority | Source | Recommended destination | Standards domain | Reason | Risk / label |
|---:|---|---|---|---|---|
| 1 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/build_logs/stage8_o2ims.md` | `traceability/evidence_snapshots/techco-stage8-o2ims.md` | O-RAN O2IMS | Earlier O2IMS evidence to pair with stage25 run capture and O2IMS boundary mapping. | Demo/implementation evidence only; not certification. |
| 2 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/build_logs/stage15_epc_ran_verification.md` | `traceability/evidence_snapshots/techco-stage15-epc-ran-verification.md` | 3GPP RAN/EPC | Verification log tying RAN/EPC behavior to 3GPP-adjacent simulator claims. | Functional verification only; release mapping still required. |
| 3 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/build_logs/stage16_slicing_e2e.md` | `traceability/evidence_snapshots/techco-stage16-slicing-e2e.md` | 3GPP slicing | End-to-end slicing evidence for service orchestration and network slice mapping. | E2E demo evidence, not protocol conformance. |
| 4 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/build_logs/stage9_ims_verification.md` | `traceability/evidence_snapshots/techco-stage9-ims-verification.md` | 3GPP IMS | IMS verification evidence supporting VoNR/IMS mapping. | Functional verification only. |
| 5 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/build_logs/stage12_vonr_call.md` | `traceability/evidence_snapshots/techco-stage12-vonr-call.md` | 3GPP IMS/VoNR | VoNR call evidence to connect IMS docs and verification logs. | Demo evidence; not formal IMS/VoNR conformance. |
| 6 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/build_logs/stage1_bf3_verification.md` | `traceability/evidence_snapshots/techco-stage1-bf3-verification.md` | 3GPP/O-RAN BF3 integration | Early BF3 verification evidence for source lineage. | Source-local verification only. |
| 7 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/docs/testing.md` | `traceability/requirements/techco-testing.md` | TM Forum; 3GPP; O-RAN | Test strategy/documentation context for copied run evidence. | Documentation evidence; check links when copied. |
| 8 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/tests/requirements-test.txt` | `traceability/evidence_snapshots/bf3-5g-emulator-requirements-test.txt` | 3GPP/O-RAN | Minimal requirements test artifact from emulator API tree. | Small test artifact only; not full test suite migration. |
| 9 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/docs/components/5g_core.md` | `traceability/requirements/techco-5g-core-component.md` | 3GPP 5GC | Component-level 5G core explanation for mapping network functions. | Documentation evidence; not conformance proof. |
| 10 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/docs/components/ran.md` | `traceability/requirements/techco-ran-component.md` | 3GPP RAN; O-RAN adjacency | RAN component explanation to connect RAN evidence and O-RAN docs. | Documentation evidence; check links when copied. |

## Excluded from this batch recommendation

- Missing PSR files: `tmforum_psr_learning/01_domain_model.txt` through `05_traceability_matrix.txt` were not found and should not be planned.
- Large docs such as full API references can be copied later, but smaller test/run evidence is higher priority first.

## Not-copy-yet exclusions

- Do not copy full directories: `Tech-Co/docs/`, `Tech-Co/src/`, `BF3-5G-Demo/`, `open_source_5g_cores/`, `5G_Wireline_Simulator/`.
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
