# O-RAN WG/interface candidate matrices for issues #8 #9 #10

Status: **candidate/reference/readiness mapping only**. This artifact does **not** claim
formal O-RAN conformance, O-RAN Alliance certification, OTIC badging, protocol
interoperability, or standards compliance. It is a derived traceability aid built from:

- Local O-RAN reference inventory: `specs/oran/Latest_Versions/index.md` and
  `specs/oran/Latest_Versions/website_data.txt` in the leader workspace.
- Existing repo evidence and copied-source maps, especially
  [`adapters/mock_oran/oran/o_ran_spec_map.py`](../../../adapters/mock_oran/oran/o_ran_spec_map.py),
  [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py),
  [`traceability/requirements/oran-compliance.md`](../../requirements/oran-compliance.md), and
  [`traceability/requirements/oran-fronthaul.md`](../../requirements/oran-fronthaul.md).

Use this matrix to decide where implementation, validation, or evidence work should be
attached. Every row remains a candidate until backed by executable tests, run captures,
path validation, and release-specific review.

## Legend

| Readiness | Meaning |
|---|---|
| `candidate-direct` | Repo has a concrete path that appears to model the interface or procedure family. |
| `candidate-adjacent` | Repo has adjacent RAN/O-RAN evidence, but the named WG/interface needs a more exact mapping before promotion. |
| `candidate-test` | Spec is primarily test/conformance/security-test guidance; use it to shape future tests, not as proof. |
| `candidate-background` | Spec is architecture, use-case, or threat-model context. It informs mappings but is not direct implementation evidence. |
| `gap` | Local spec exists, but this repo has no clear implementation/evidence path yet. |

## WG1-WG3 matrix: architecture, Non-RT RIC/A1/R1, Near-RT RIC/E2/Y1

### Candidate direct interface/procedure specs

| WG | Interface / area | Local reference spec candidates | Candidate repo paths | Readiness | Evidence/action needed before promotion |
|---|---|---|---|---|---|
| WG1 | Overall O-RAN architecture and SMO role | `O-RAN.WG1.TS.OAD-R005-v16.00`, `O-RAN.WG1.TS.SMO-ARCH-R005-v02.00` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`adapters/mock_oran/oran/o_ran_spec_map.py`](../../../adapters/mock_oran/oran/o_ran_spec_map.py), [`docs/standards-mapping.md`](../../../docs/standards-mapping.md) | `candidate-background` | Keep as topology/readiness context unless SMO services are backed by executable endpoints and tests. |
| WG1 | O-RAN slicing architecture / RAN NSSMF-style flows | `O-RAN.WG1.TS.Slicing-Architecture-R004-v14.01`, `O-RAN.WG1.Study-on-O-RAN-Slicing-v02.00` | [`adapters/mock_ran/ran/slicing/oran_slicing.py`](../../../adapters/mock_ran/ran/slicing/oran_slicing.py), [`capabilities/slice_provisioning/.gitkeep`](../../../capabilities/slice_provisioning/.gitkeep) | `candidate-direct` | Add focused tests for slice lifecycle, per-slice RRM policy, and mapping to 3GPP NSSAI/NSSF evidence before any readiness upgrade. |
| WG1 | Network energy saving / mMIMO use cases | `O-RAN.WG1.Network-Energy-Savings-Technical-Report-R003-v02.00`, `O-RAN.WG1.TR.O-RES.0-R004-v01.00`, `O-RAN.WG1.mMIMO-Use-Cases-TR-v01.00` | [`adapters/mock_oran/oran/o_ran_spec_map.py`](../../../adapters/mock_oran/oran/o_ran_spec_map.py), [`capabilities/ran_control_loop/.gitkeep`](../../../capabilities/ran_control_loop/.gitkeep) | `candidate-adjacent` | The map names energy/resiliency surfaces, but no matching repo implementation path was found in this worktree; treat as gap until paths/tests exist. |
| WG2 | A1 policy / enrichment | `O-RAN.WG2.TS.A1AP-R005-v06.00`, `O-RAN.WG2.TS.A1TD-R005-v11.01`, `O-RAN.WG2.TS.A1UCR-R005-v05.00` | [`adapters/mock_ran/ran/ric/non_rt_ric.py`](../../../adapters/mock_ran/ran/ric/non_rt_ric.py), [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py) | `candidate-direct` | Verify endpoint behavior and policy-type payload shapes against the current local spec release before stronger claims. |
| WG2 | R1 rApp/SMO services and AI/ML workflow | `O-RAN.WG2.TS.R1AP-R005-v10.00`, `O-RAN.WG2.TS.R1GAP-R005-v13.00`, `O-RAN.WG2.AIML-v01.03` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`traceability/requirements/techco-ai-observer-component.md`](../../requirements/techco-ai-observer-component.md) | `candidate-adjacent` | Gateway exposes candidate aggregation routes; dedicated R1/AI-ML source paths were not found in this worktree. |
| WG3 | Near-RT RIC / E2 application protocol | `O-RAN.WG3.TS.RICARCH-R005-v08.00`, `O-RAN.WG3.TS.E2AP-R004-v08.00`, `O-RAN.WG3.TS.E2GAP-R004-v08.00` | [`adapters/mock_ran/ran/ric/near_rt_ric.py`](../../../adapters/mock_ran/ran/ric/near_rt_ric.py), [`adapters/mock_ran/ran/ric/e2ap.py`](../../../adapters/mock_ran/ran/ric/e2ap.py), [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py) | `candidate-direct` | Add E2 setup/subscription/control regression coverage and keep copied-source identity evidence tied to the current release. |
| WG3 | E2 service models | `O-RAN.WG3.TS.E2SM-KPM-R004-v07.00`, `O-RAN.WG3.TS.E2SM-RC-R004-v09.00`, `O-RAN.WG3.TS.E2SM-CCC-R004-v06.00`, `ORAN-WG3.E2SM-NI-v01.00`, `O-RAN.WG3.TS.E2SM-LLC-R004-v01.00` | [`adapters/mock_ran/ran/ric/e2ap.py`](../../../adapters/mock_ran/ran/ric/e2ap.py), [`adapters/mock_ran/ran/ric/e2sm_ccc.py`](../../../adapters/mock_ran/ran/ric/e2sm_ccc.py), [`adapters/mock_ran/ran/ric/e2sm_ni.py`](../../../adapters/mock_ran/ran/ric/e2sm_ni.py), [`adapters/mock_ran/ran/ric/e2sm_llc.py`](../../../adapters/mock_ran/ran/ric/e2sm_llc.py) | `candidate-direct` | Validate each service-model payload against local spec definitions and keep results as readiness evidence only. |
| WG3 | Y1 analytics | `O-RAN.WG3.TS.Y1AP-R005-v01.02`, `O-RAN.WG3.TS.Y1GAP-R005-v01.02` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`adapters/mock_oran/oran/o_ran_spec_map.py`](../../../adapters/mock_oran/oran/o_ran_spec_map.py) | `candidate-adjacent` | Spec map/gateway mention Y1, but no dedicated `y1.py` path exists in this worktree; keep as gap-adjacent. |

### WG1-WG3 test/conformance and background buckets

| Bucket | Local reference spec candidates | Candidate use in repo |
|---|---|---|
| Test/conformance specs | Current local WG2/WG3 API and type-definition specs plus future generated payload tests. | Build unit/API smoke tests under `tests/conformance/` only after exact payload contracts are extracted; do not treat current simulator smoke as conformance proof. |
| Architecture/background specs | WG1 OAD/SMO/slicing/use-case/energy reports; WG2 Non-RT RIC architecture; WG3 RIC architecture. | Use for diagrams, route grouping, and traceability labels in `docs/standards-mapping.md`, gateway inventory, and capability manifests. |
| Promotion blockers | Missing dedicated R1/Y1/energy implementation paths in this worktree; no formal O-RAN protocol harness. | Keep all claims at candidate/readiness level until paths and tests are present. |

## WG4-WG6 matrix: Open Fronthaul, WG5 O-CU/O-DU OAM/D2, O-Cloud/O2

### Candidate direct interface/procedure specs

| WG | Interface / area | Local reference spec candidates | Candidate repo paths | Readiness | Evidence/action needed before promotion |
|---|---|---|---|---|---|
| WG4 | Open Fronthaul C/U/S planes | `O-RAN.WG4.TS.CUS.0-R005-v20.00`, `O-RAN.WG4.CTI-TMP.0-R003-v04.00` | [`adapters/mock_ran/ran/fronthaul/cus_plane.py`](../../../adapters/mock_ran/ran/fronthaul/cus_plane.py), [`traceability/requirements/oran-fronthaul.md`](../../requirements/oran-fronthaul.md), [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py) | `candidate-direct` | Validate C-plane/U-plane/S-plane stats and synchronization models with executable tests; current evidence is model-level only. |
| WG4 | Open Fronthaul M-plane and O-RU management | `O-RAN.WG4.TS.MP.0-R005-v20.00`, `O-RAN.WG4.TS.MP-YANGs-R005-v20.00` | [`traceability/requirements/oran-fronthaul.md`](../../requirements/oran-fronthaul.md), [`adapters/mock_oran/oran/o_ran_spec_map.py`](../../../adapters/mock_oran/oran/o_ran_spec_map.py) | `candidate-adjacent` | M-plane is described in requirements/spec map; no `m_plane.py` or `o_ru.py` path was found in this worktree, so keep as not-yet-promoted. |
| WG4 | Fronthaul interoperability/conformance | `O-RAN.WG4.TS.CONF.0-R005-v15.00`, `O-RAN.WG4.TS.IOT.0-R005-v15.00` | [`traceability/requirements/oran-fronthaul.md`](../../requirements/oran-fronthaul.md), [`tests/conformance/.gitkeep`](../../../tests/conformance/.gitkeep) | `candidate-test` | Use to design future fronthaul test cases; current repo does not contain OTIC/interoperability proof. |
| WG5 | O-CU / O-DU O1, C/U interfaces, D2 | `O-RAN.WG5.O-CU-O1.0-R003-v07.00`, `O-RAN.WG5.O-DU-O1.0-R003-v09.00`, `O-RAN.WG5.TS.C.1-R005-v17.00`, `O-RAN.WG5.U.0-R003-v07.00`, `O-RAN.WG5.TS.D2AP-0.R005-v01.00`, `O-RAN.WG5.TS-D2-O&MRequirements-R005_v01.00` | [`adapters/mock_ran/ran/cu.py`](../../../adapters/mock_ran/ran/cu.py), [`adapters/mock_ran/ran/du.py`](../../../adapters/mock_ran/ran/du.py), [`docs/ran-components.md`](../../../docs/ran-components.md) | `candidate-adjacent` | CU/DU source exists as RAN adjacency evidence, but no exact WG5 C/U/D2/O1 mapping or tests were found. Treat as a clear gap for #9/#10 follow-up. |
| WG5 | O-CU/O-DU test and interoperability | `O-RAN.WG5.TS.IOT.0-R005-v15.00`, local D2/O1 spec family | [`tests/conformance/.gitkeep`](../../../tests/conformance/.gitkeep), [`tests/integration/test_mock_runtime_smoke.py`](../../../tests/integration/test_mock_runtime_smoke.py) | `gap` | Add targeted tests only after exact candidate implementation paths are introduced. |
| WG6 | O2 IMS and O-Cloud inventory | `O-RAN.WG6.TS.O2IMS-INTERFACE-R005-v11.00`, `O-RAN.WG6.TS.O2-GA&P-R005-v10.00`, `O-RAN.WG6.TS.O-Cloud-IM-R005-v06.00` | [`traceability/standards_mapping/oran-o2ims-real-adapter.py`](../../standards_mapping/oran-o2ims-real-adapter.py), [`traceability/requirements/techco-oran-o2ims-component.md`](../../requirements/techco-oran-o2ims-component.md), [`traceability/evidence_snapshots/techco-stage8-o2ims.md`](../../evidence_snapshots/techco-stage8-o2ims.md) | `candidate-direct` | Evidence is copied/derived and should be corroborated with live adapter tests before any readiness promotion. |
| WG6 | O2 DMS / Kubernetes or ETSI NFV deployment management | `O-RAN.WG6.TS.O2DMS-INTERFACE-K8S-PROFILE-R005-v07.00`, `O-RAN.WG6.TS.O2DMS-INTERFACE-ETSI-NFV-PROFILE-R005-v10.00` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`traceability/requirements/techco-oran-o2ims-component.md`](../../requirements/techco-oran-o2ims-component.md) | `candidate-adjacent` | Gateway has candidate O2-DMS aggregation; no dedicated DMS implementation path was found in this worktree. |
| WG6 | O-Cloud notifications, architecture, descriptors | `O-RAN.WG6.O-Cloud Notification API-v04.00`, `O-RAN.WG6.CADS-v08.01`, `O-RAN.WG6.ASD-R004-v02.00`, `O-RAN.WG6.ORCH-USE-CASES-R005-v15.00` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`traceability/requirements/techco-operations.md`](../../requirements/techco-operations.md) | `candidate-background` | Keep as orchestration/O-Cloud context unless notification and descriptor APIs are implemented and tested. |

### WG4-WG6 test/conformance and background buckets

| Bucket | Local reference spec candidates | Candidate use in repo |
|---|---|---|
| Direct specs | WG4 CUS/MP, WG6 O2IMS/O2DMS/O-Cloud IM. | Candidate mapping to fronthaul model docs, copied O2IMS adapter, and gateway aggregate routes. |
| Test/conformance specs | WG4 conformance/IOT, WG5 IOT/D2 test materials, WG6 O-Cloud interface conformance. | Future `tests/conformance/oran_*` suites; do not infer proof from `.gitkeep` or smoke tests. |
| Architecture/background specs | WG6 CADS/ASD/orchestration use cases; WG5 transport/OAM descriptions. | Use for roadmap and gap labeling, not implementation status. |
| Promotion blockers | Missing dedicated WG5 mapping; missing M-plane/O-RU implementation paths in this worktree; O2IMS evidence is copied/derived. | Keep candidate wording and require path validation plus tests before status changes. |

## WG10-WG11 matrix: O1/OAM/TE&IV and security

### Candidate direct interface/procedure specs

| WG | Interface / area | Local reference spec candidates | Candidate repo paths | Readiness | Evidence/action needed before promotion |
|---|---|---|---|---|---|
| WG10 | O1 interface, OAM architecture, NRM | `O-RAN.WG10.TS.O1-Interface.0-R005-v18.00`, `O-RAN.WG10.TS.OAM-Architecture-R005-v17.00`, `O-RAN.WG10.TS.O1NRM.0-R004-v04.00` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`traceability/requirements/oran-compliance.md`](../../requirements/oran-compliance.md), [`traceability/requirements/oran-fronthaul.md`](../../requirements/oran-fronthaul.md) | `candidate-adjacent` | Gateway/spec-map mention O1/OAM, but no dedicated `oam/o1.py` path exists in this worktree; require implementation path validation. |
| WG10 | O1 performance measurements | `O-RAN.WG10.TS.O1PMeas-R005-v05.00` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`traceability/evidence_snapshots/techco-stage19-oran-closed-loop.md`](../../evidence_snapshots/techco-stage19-oran-closed-loop.md) | `candidate-adjacent` | Treat run captures as demo evidence only until PM job/file reporting logic is directly implemented and tested. |
| WG10 | Topology Exposure and Inventory | `O-RAN.WG10.TS.TE&IV-API.0-R005-v04.00`, `O-RAN.WG10.TS.TE&IV-CIMI.0-R005-v06.00`, `O-RAN.WG10.TS.TE&IV-DM.0-R005-v04.00`, `O-RAN.WG10.TE&IV-UCR.0-R004-v03.01` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`traceability/evidence_snapshots/techco-stage25-oran-run-capture.md`](../../evidence_snapshots/techco-stage25-oran-run-capture.md) | `candidate-adjacent` | Add TE&IV entity/relationship implementation and API tests before promotion. |
| WG10 | Application packaging / onboarding SMOS | `O-RAN.WG10.TS.AppPkgGAP-R005-v01.00`, `O-RAN.WG10.TS.OnboardingSMOSGAP.0-R004-v02.00` | [`traceability/requirements/techco-development.md`](../../requirements/techco-development.md), [`traceability/requirements/techco-operations.md`](../../requirements/techco-operations.md) | `candidate-background` | Useful for lifecycle/onboarding roadmap only; no direct onboarding SMOS implementation path found. |
| WG11 | Security protocol and controls | `O-RAN.WG11.TS.SecProtSpec.0-R005-v14.00`, `O-RAN.WG11.TS.SRCS.0-R005-v14.00` | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../../../adapters/mock_oran/api_gateway/oran_gateway.py), [`traceability/requirements/techco-ai-observer-component.md`](../../requirements/techco-ai-observer-component.md), [`traceability/evidence_batch_004_claim_caveats.md`](../../evidence_batch_004_claim_caveats.md) | `candidate-adjacent` | Gateway exposes candidate security aggregation, but no dedicated security service source path exists in this worktree. |
| WG11 | Security test specification | `O-RAN.WG11.TS.STS-R005-v12.00` | [`tests/conformance/.gitkeep`](../../../tests/conformance/.gitkeep), [`traceability/evidence_batch_004_claim_caveats.md`](../../evidence_batch_004_claim_caveats.md) | `candidate-test` | Use for future security test scaffolding; current artifacts are caveats/readiness notes, not security conformance tests. |
| WG11 | Zero Trust, threat modeling, OAuth2, certificates, PQC, O-Cloud/Open FH security | `O-RAN.WG11.TR.ZTA-R005-v05.00`, `O-RAN.WG11.TR.Threat-Modeling-R005-v08.00`, `O-RAN.WG11.TR.OAuth2.0-Security.0-R005-v07.00`, `O-RAN.WG11.TR.Certficate-Management-Framework.0-R005-v06.00`, `O-RAN.WG11.TR.PQC-Security.0-R005-v02.00`, `O-RAN.WG11.TR.O-CLOUD-Security.0-R005-v09.00`, `O-RAN.WG11.TR.Open-FH-Security.0-R004-v05.00` | [`traceability/requirements/techco-ai-observer-component.md`](../../requirements/techco-ai-observer-component.md), [`traceability/requirements/techco-operations.md`](../../requirements/techco-operations.md), [`traceability/requirements/oran-fronthaul.md`](../../requirements/oran-fronthaul.md) | `candidate-background` | Use as risk/control context. Dedicated controls, auth, certificate, and PQC code paths must be added before direct mapping. |

### WG10-WG11 test/conformance and background buckets

| Bucket | Local reference spec candidates | Candidate use in repo |
|---|---|---|
| Direct specs | WG10 O1/OAM/TE&IV; WG11 security protocol and controls. | Candidate grouping for gateway routes and traceability docs, pending implementation-path validation. |
| Test/conformance specs | WG11 STS and any O1/TE&IV API contract tests generated from local specs. | Future conformance-readiness tests under `tests/conformance/`; no formal conformance claim. |
| Architecture/background specs | WG11 ZTA/threat model/OAuth/cert/PQC/O-Cloud security reports; WG10 onboarding/application packaging. | Use to prioritize controls and onboarding roadmap; avoid mapping to implementation unless a concrete path exists. |
| Promotion blockers | Missing dedicated O1/TE&IV/security implementation paths in this worktree; existing evidence is mostly gateway aggregation, copied docs, or run captures. | Keep status at candidate/readiness until implementation and tests are added. |

## Issue progress and remaining blockers

- **Issue #8** progressed by separating WG/interface candidate mappings for WG1-3, WG4-6, and WG10-11 without adding raw standards files.
- **Issue #9** progressed by identifying WG5 as an explicit O-CU/O-DU/O1/D2 gap rather than folding it into WG4/WG6 evidence.
- **Issue #10** progressed by separating direct specs, test/conformance specs, and architecture/background specs so future evidence promotion has a safer gate.

Remaining blockers before any stronger readiness claim:

1. Validate candidate paths against the latest integrated branch after other workers land their lanes.
2. Add exact implementation paths for WG5, Y1, R1/AI-ML, O1/TE&IV, and WG11 security services where the current worktree only has gateway/spec-map references.
3. Add focused `tests/conformance/` or API smoke tests derived from the exact local spec release; current smoke and copied evidence remain readiness evidence only.
4. Keep release-specific reviews tied to `specs/oran/Latest_Versions/index.md` and avoid committing raw PDF/DOCX/ZIP bundles.
