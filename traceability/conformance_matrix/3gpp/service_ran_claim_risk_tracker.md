# 3GPP Service/RAN Candidate Claim Risk Tracker

Generated: 2026-06-05
Issue: #7 — 3GPP service/RAN wording and risky claims
Status: candidate/readiness traceability only; **not formal 3GPP conformance evidence**.

## Scope and rules

This tracker preserves copied-source identity by recording risky wording and candidate
mappings in traceability metadata instead of editing copied mock source files. It is a
promotion gate for service/session/RAN language that appears in copied code or docs.

Use this artifact to decide whether a claim may be repeated in external docs, release
notes, demos, or issue comments. Source-authored claims such as `100% Compliant`,
`compliant implementation`, or response fields named `compliance` remain copied-source
content unless a later task explicitly authorizes source edits.

## Evidence baseline

- Existing policy: [`docs/conformance-boundary.md`](../../../docs/conformance-boundary.md)
  says the lab is standards-traceable, not automatically standards-conformant.
- Existing mapping: [`docs/standards-mapping.md`](../../../docs/standards-mapping.md)
  limits 3GPP transport claims to minimal/mock helpers and requires release/evidence rows
  before stronger claims.
- Local Rel-19 spec filename probe for TS `23.501`, `23.502`, `23.503`, `24.501`,
  `29.502`, `29.503`, `29.509`, `29.510`, `29.531`, `38.413`, `38.463`, and `38.473`
  returned no direct filename matches from this worker path. Treat spec-asset evidence for
  this lane as **not verified here** until the inventory lane publishes derived filenames.

## Candidate mapping and risky wording register

| ID | Repo surface | Source-authored wording or behavior | Candidate standards mapping | Risk | Safe external wording | Required promotion evidence |
|---|---|---|---|---|---|---|
| 3gpp-svc-udm | [`services/mock_5g_core/core_network/udm.py`](../../../services/mock_5g_core/core_network/udm.py) lines 2, 323, 590, 602 | `100% Compliant Implementation`, FastAPI description says TS 29.503 compliant, status responses expose `compliance: 3GPP TS 29.503`. | Nudm UECM/SDM/UEAU candidate surface; source also references TS 29.505 for SDM endpoints. | High: copied source makes complete conformance language without release-row/test proof; TS 29.503 vs TS 29.505 references need reconciliation. | Mock UDM-style service with candidate Nudm endpoint shapes and telemetry labels; not formal conformance. | Release register row for TS 29.503/29.505, endpoint-to-clause matrix, executable tests for required request/response/error behavior, and latest-release gap review. |
| 3gpp-svc-ausf | [`services/mock_5g_core/core_network/ausf.py`](../../../services/mock_5g_core/core_network/ausf.py) lines 2, 353, 391 | `100% Compliant Implementation`; health/legacy responses expose `compliance: 3GPP TS 29.509`. | Nausf authentication candidate surface. | High: authentication vectors and security behavior are sensitive; smoke/runtime checks do not prove 3GPP security conformance. | Mock AUSF-style authentication service for local readiness tests. | TS 29.509 release row, security review, vector/negative-path tests, and explicit non-production cryptographic caveat. |
| 3gpp-svc-nrf | [`services/mock_5g_core/core_network/nrf.py`](../../../services/mock_5g_core/core_network/nrf.py) lines 2, 707 | `100% Compliant Implementation`; health response exposes `compliance: 3GPP TS 29.510`. | Nnrf discovery/management candidate surface. | High: discovery registration/deregistration may be useful, but conformance needs release-specific API behavior and schema validation. | Mock NRF-style service registry/discovery surface. | TS 29.510 release row, OpenAPI/schema validation, registration/discovery/deregistration tests, and error/status-code matrix. |
| 3gpp-svc-nssf | [`services/mock_5g_core/core_network/nssf.py`](../../../services/mock_5g_core/core_network/nssf.py) lines 2, 854 | `100% Compliant Implementation`; health response exposes `compliance: 3GPP TS 29.531`. | Nnssf slice selection candidate surface. | High: slice-selection semantics and reject/allowed NSSAI behavior need clause-level proof. | Mock NSSF-style slice-selection readiness surface. | TS 29.531 release row, slice-info request/response tests, reject/allowed NSSAI matrix, and latest-release gap review. |
| 3gpp-session-amf-smf | [`services/mock_5g_core/core_network/amf.py`](../../../services/mock_5g_core/core_network/amf.py) lines 419, 438, 968 and [`services/mock_5g_core/core_network/smf.py`](../../../services/mock_5g_core/core_network/smf.py) lines 215, 328 | `3GPP-compliant` PDU session wording and response `compliance` fields. | Candidate AMF/SMF session-control flow; service/session mapping crosses TS 29.518, TS 29.502, TS 23.501/23.502. | High: end-to-end PDU session behavior crosses multiple specs and transport protocols; local mock flow is not enough for conformance. | Mock AMF/SMF PDU-session readiness flow with candidate 3GPP mapping. | Flow-level test evidence, release rows for 23/29-series specs, negative/error-path tests, and transport gap matrix linkage. |
| 3gpp-ran-gnb | [`adapters/mock_ran/ran/gnb.py`](../../../adapters/mock_ran/ran/gnb.py) lines 2, 873 | `100% Compliant` NGAP implementation and response `compliance: 3GPP TS 38.413`. | Candidate gNB/NGAP/N2 mapping. | High: existing docs say NGAP-like JSON over TCP, not ASN.1/PER NGAP over SCTP. | Mock gNB with NGAP-like readiness behavior. | TS 38.413/38.412 release rows, ASN.1/PER/SCTP gap statement, and executable tests that distinguish mock JSON transport from formal NGAP. |
| 3gpp-ran-cu-du-f1 | [`adapters/mock_ran/ran/cu.py`](../../../adapters/mock_ran/ran/cu.py) lines 2, 415, 595 and [`adapters/mock_ran/ran/du.py`](../../../adapters/mock_ran/ran/du.py) lines 2-6, 533, 756 | F1AP/RRC/MAC/RLC/PDCP/PHY `100% Compliant` and response `compliance` fields. | Candidate CU/DU/F1/RRC/radio-stack mapping. | Critical: copied comments label F1AP as TS 38.463, while the E2SM-NI map records F1AP as TS 38.473 and E1AP as TS 38.463; this must be reconciled before any promotion. | Mock CU/DU components with F1-like message models and RAN readiness examples. | Corrected traceability row distinguishing F1AP TS 38.473 from E1AP TS 38.463, clause-level endpoint map, and tests for the modeled procedures only. |
| 3gpp-ran-e2sm-ni | [`adapters/mock_ran/ran/ric/e2sm_ni.py`](../../../adapters/mock_ran/ran/ric/e2sm_ni.py) lines 10, 46-49, 238 | E2SM-NI claims support for NGAP/XnAP/F1AP/E1AP/S1AP tracing. | Candidate O-RAN E2SM-NI model with 3GPP NI references; F1/E1 mapping says F1AP TS 38.473 and E1AP TS 38.463. | Medium-high: this is a metadata/model surface, not proof that the underlying 3GPP protocol PDUs are decoded or conformant. | E2SM-NI-style model listing candidate network-interface types for readiness/testing. | O-RAN E2SM-NI spec-map validation plus 3GPP NI release rows and tests proving what is traced: raw mock bytes, selected IEs, or decoded PDUs. |
| 3gpp-ran-ric-wording | [`adapters/mock_ran/ran/ric/e2ap.py`](../../../adapters/mock_ran/ran/ric/e2ap.py) line 4, [`near_rt_ric.py`](../../../adapters/mock_ran/ran/ric/near_rt_ric.py) line 4, [`non_rt_ric.py`](../../../adapters/mock_ran/ran/ric/non_rt_ric.py) line 4 | ETSI/O-RAN `Compliant Implementation` language. | RIC/E2/A1 candidate mapping adjacent to O-RAN lanes, with 3GPP RAN interfaces only where NI/E2 models reference them. | Medium-high: not strictly a 3GPP claim, but can bleed into RAN conformance marketing if repeated. | Mock RIC/E2/A1 readiness components with candidate standards references. | O-RAN lane validation, E2/A1 release rows, and separation from 3GPP RAN protocol conformance claims. |

## F1AP/E1AP mismatch checkpoint

Do not promote CU/DU/F1 wording until the team resolves this mismatch:

- `adapters/mock_ran/ran/cu.py` and `adapters/mock_ran/ran/du.py` source comments label
  F1AP as TS 38.463.
- `adapters/mock_ran/ran/ric/e2sm_ni.py` maps F1AP to TS 38.473 and E1AP to TS 38.463.

For external wording, use only: "mock CU/DU F1-like message models" unless a later
traceability artifact and release register row confirm the exact spec mapping and tests.

## Promotion checklist for issue #7 claims

A service/session/RAN claim may move from candidate wording to stronger wording only when
all checks below are satisfied:

1. Release row exists for every cited spec ID.
2. Implementation path is mapped to exact procedures/endpoints/messages.
3. Executable tests prove the bounded behavior being claimed.
4. Transport/protocol gaps are stated explicitly, including JSON-over-TCP vs SCTP/ASN.1
   where relevant.
5. Copied-source strong wording is not repeated in docs without the caveat from this
   tracker and [`docs/conformance-boundary.md`](../../../docs/conformance-boundary.md).
6. Any public/readiness artifact uses `candidate`, `mock`, `standards-inspired`, or
   `readiness` language, not `compliant`, `certified`, or `conformant`.

## Open blockers / handoffs

- Needs inventory lane output to confirm local 3GPP spec filenames and versions for the
  cited 23/24/29/38-series specs.
- Needs release/gap lane output before service/session claims are promoted.
- Needs O-RAN mapping lane output for RIC/E2SM-NI surfaces to avoid duplicate or
  conflicting RAN/O-RAN claims.
