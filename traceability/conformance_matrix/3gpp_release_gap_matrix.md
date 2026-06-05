# 3GPP candidate release gap matrix

This matrix is a readiness and traceability aid for issues #4, #5, and #6. It separates local reference availability from implementation and conformance evidence. It does not assert formal 3GPP conformance.

| Candidate area | Spec baseline candidate | Local Rel-19 filename evidence | Repo implementation/readiness path | Current gap to claim | Next evidence step |
|---|---|---|---|---|---|
| 5GS architecture | TS 23.501 | `23_series/23501-j60.docx` | `services/mock_5g_core/; docs/core-network.md` | Reference present, but no clause-by-clause architecture trace or executable conformance evidence. | Map high-level AMF/SMF/UPF/NSSF claims to clauses and existing smoke tests before stronger wording. |
| 5GS procedures | TS 23.502 | `23_series/23502-j60.docx` | `services/mock_5g_core/; tests/integration/` | Reference present, but local flows are mock/readiness flows, not protocol conformance procedures. | Add scenario-to-procedure trace rows and preserve mock/readiness wording. |
| Policy and charging | TS 23.503 | `23_series/23503-j60.docx` | `services/mock_5g_core/ (policy/session surfaces if present)` | Reference present, implementation path requires audit and test evidence. | Identify exact policy code paths or mark as reference-only. |
| 5GS NAS | TS 24.501 | `24_series/24501-j40.docx` | `services/mock_5g_core/; adapters/mock_ran/` | Reference present, but no NAS encoder/decoder or UE protocol conformance evidence established. | Track any NAS-like messages as modeled/mock only until tests exist. |
| PFCP / N4 | TS 29.244 | not found in local Rel-19 folder | `services/mock_5g_core/core_network/transport.py` | Local Rel-19 reference missing; helper status only, no complete IE/PDR/FAR/QER proof. | Acquire/record official reference and add targeted PFCP header/IE tests before claims. |
| GTP-U / N3 | TS 29.281 | not found in local Rel-19 folder | `services/mock_5g_core/core_network/transport.py` | Local Rel-19 reference missing; minimal G-PDU helper only. | Acquire/record official reference and add packet-level tests/evidence before claims. |
| 5GS security | TS 33.501 | not found in local Rel-19 folder | `security/config docs if any; services/mock_5g_core/` | Local Rel-19 reference missing; security conformance not established. | Keep security claims policy-level/readiness-only until reference and tests are mapped. |
| NG signalling transport | TS 38.412 | not found in local Rel-19 folder | `services/mock_5g_core/core_network/transport.py; adapters/mock_ran/` | Local Rel-19 reference missing; SCTP requirement not proven by TCP fallback. | Record TCP fallback as lab-only and add SCTP/transport gap evidence if in scope. |
| NGAP | TS 38.413 | not found in local Rel-19 folder | `services/mock_5g_core/core_network/transport.py; adapters/mock_ran/` | Local Rel-19 reference missing; JSON-modeled messages are not ASN.1/PER NGAP evidence. | Track NGAP-like messages as mock representations unless ASN.1/PER tests are added. |

## Promotion gate

Before promoting any row beyond candidate/reference readiness, update the release register with official-source evidence, add executable tests or accepted external evidence, and keep `known_gap_to_latest` explicit.
