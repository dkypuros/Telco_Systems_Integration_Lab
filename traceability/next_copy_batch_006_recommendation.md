# Next Copy-Only Batch Recommendation: Evidence Batch 006

Date: 2026-06-05
Target lab: `<LAB_ROOT>`
Source umbrella: `<SOURCE_5G_LAB_SIMULATOR_ROOT>`
Status: recommendation approved for immediate copy-only execution in the current Ralph loop.

## Selection rule

Batch 006 should add standards-facing reference/API/component documentation that explains the evidence already copied. These are documentation/reference artifacts only, not formal conformance proof.

## Ready source-to-destination candidates

All source files below were checked for existence on 2026-06-05 and are not already present in `traceability/copy_manifest.csv` as copied source paths.

| Priority | Source | Recommended destination | Standards domain | Reason | Risk / label |
|---:|---|---|---|---|---|
| 1 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/api_reference.md` | `traceability/requirements/techco-api-reference.md` | TM Forum; 3GPP; O-RAN | API reference context for copied service/run evidence. | Reference doc; verify links and claims. |
| 2 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/operations.md` | `traceability/requirements/techco-operations.md` | TM Forum; 3GPP; O-RAN | Operations/reference guide with no local relative link fan-out. | Reference doc; not conformance proof. |
| 3 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/components/ims.md` | `traceability/requirements/techco-ims-component.md` | 3GPP IMS/VoNR | Component doc to pair with IMS and VoNR evidence. | Documentation evidence only. |
| 4 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/components/epc.md` | `traceability/requirements/techco-epc-component.md` | 3GPP EPC/RAN | Component doc to pair with EPC/RAN verification. | Documentation evidence only. |
| 5 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/Tech-Co/docs/components/order_engine.md` | `traceability/requirements/techco-order-engine-component.md` | TM Forum; service orchestration | Component doc for order orchestration and TMF-facing service flow. | Documentation evidence; not TMF conformance. |
| 6 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/testing.md` | `traceability/requirements/bf3-testing.md` | 3GPP; O-RAN | BF3 testing documentation for existing BF3 maps and reports. | Documentation evidence; check claim language. |
| 7 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/api-reference.md` | `traceability/requirements/bf3-api-reference.md` | 3GPP; O-RAN | BF3 API reference for emulator/service evidence. | Reference doc only. |
| 8 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/core-network.md` | `traceability/requirements/bf3-core-network.md` | 3GPP 5GC | Core-network documentation for 5G emulator claims. | Documentation evidence only. |
| 9 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/ric-architecture.md` | `traceability/requirements/ric-architecture.md` | O-RAN RIC | RIC architecture context for O-RAN material. | Documentation evidence only. |
| 10 | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/BF3-5G-Demo/docs/ran-components.md` | `traceability/requirements/bf3-ran-components.md` | 3GPP RAN; O-RAN adjacency | RAN component docs for RAN/O-RAN mapping. | Documentation evidence only. |

## Not-copy-yet exclusions

- Do not copy full directories: `Tech-Co/docs/`, `Tech-Co/src/`, `BF3-5G-Demo/`, `open_source_5g_cores/`, `5G_Wireline_Simulator/`.
- Do not copy caches, virtualenvs, `node_modules`, `.git`, `.omx`, local DBs, generated outputs, or uncurated runtime logs.
- If Markdown files contain local relative links, either copy required linked files under matching relative names or record a deliberate caveat before approval.
- Do not claim formal TM Forum, 3GPP, or O-RAN conformance from documentation/reference files alone.


## Execution correction

During Ralph pre-copy link validation, `Tech-Co/docs/reference.md` was replaced with `Tech-Co/docs/operations.md` to avoid a large unresolved build-history link fan-out. `BF3-5G-Demo/docs/ric-architecture.md` keeps its original filename at the destination so `bf3-ran-components.md` can resolve its local relative link.
