# Tech-Co Spec Library Guide

**Date**: 2026-05-18
**Scope**: Which standards are referenced, which are implemented, and what conformance
status each has achieved. Cross-references the spec library at `Tech-Co/specs/` and the
per-NF sidecar files at `components/BF3-5G-Demo/.../core_network/*.py.spec.txt`.

---

## 1. Overview

Tech-Co references real standards from five bodies:

| Standards body | Area covered | Spec location in this repo |
|---|---|---|
| TM Forum | OSS/BSS Open APIs, ODA, MODA | `specs/tmforum_standards/` |
| 3GPP | 5G system architecture, NF interfaces, IMS | `specs/3gpp_releases/` |
| O-RAN Alliance (via ETSI ISG) | RAN open interfaces: A1, E2, O1, O2, Fronthaul | `specs/oran/` |
| ETSI | NFV, MEC, ZSM infrastructure | `specs/etsi/` |
| AI-RAN Alliance | AI in the RAN editorial and whitepapers | `specs/ai_ran_alliance/` |

The `Tech-Co/specs/` tree is a curated subset of the larger
`4Public_Networking_Public_Data/` library (see `networking_specs_inventory.txt` for the
full catalogue). Only the specs that directly govern Tech-Co components were copied here.

**Implementation honesty note**: All Tech-Co NFs use functional HTTP/REST over Python
FastAPI. None implement the binary transport protocols (NGAP over SCTP, PFCP over UDP,
SIP over UDP, DIAMETER over TCP, ASN.1/PER encoding). The procedure logic is faithfully
modeled from the specs; the wire format is REST/JSON for testability without specialized
infrastructure. Each NF documents this gap explicitly in its `.py.spec.txt` sidecar.

---

## 2. TM Forum Specs

### 2.1 Conformance summary

| Spec | Short name | Status | CTK result | Implementation location |
|---|---|---|---|---|
| TMF620 v4 | ProductCatalog | IMPLEMENTED | 100% (1421/1421) | `src/catalog_api/` |
| TMF622 v4 | ProductOrdering | IMPLEMENTED | 100% (63/63) | `src/order_engine/` |
| TMF641 v4 | ServiceOrdering | PARTIAL | not CTK-tested | `src/order_engine/` (GET only) |
| TMFC003 | ProductOrderDelivery, Orchestration and Management | IMPLEMENTED | n/a (pattern-based) | `src/order_engine/` |
| TMF640 | ServiceActivation | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF640-*` |
| TMF645 | ServiceQualification | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF645-*` |
| TMF630 | API Design Guidelines / Hub-Listener events | NOT IMPLEMENTED | n/a | would unlock event-driven arch |
| TMF633 | ServiceCatalog | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF633-*` |
| TMF637 | ProductInventory | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF637-*` |
| TMF638 | ServiceInventory | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF638-*` |
| TMF639 | ResourceInventory | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF639-*` |
| TMF629 | CustomerManagement | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF629-*` |
| TMF642 | Alarm | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF642-*` |
| TMF915 | AI in OSS/BSS | NOT IMPLEMENTED | CTK available | `specs/tmforum_standards/CTK-TMF915-AI/` |

All other CTK packages in `specs/tmforum_standards/` are referenced for architectural
alignment but have no corresponding Tech-Co implementation.

### 2.2 TMF620 ProductCatalog (IMPLEMENTED, 100%)

**Source**: `src/catalog_api/`
**Port**: 8081
**CTK run**: `specs/tmforum_standards/CTK-TMF620-ProductCatalog/` targeting
`http://127.0.0.1:8081`
**Stage 13 baseline**: 76.4% (469/614). Stage 18 lifted to 100% (1421/1421).

Mandatory TMF620 resources implemented:

| Resource | GET list | GET by-id | POST | PATCH | DELETE | `?fields=` |
|---|---|---|---|---|---|---|
| productCatalog | yes | yes | no | no | no | yes |
| category | yes | yes | no | no | no | yes |
| productOffering | yes | yes | yes | yes | yes | yes |
| productSpecification | yes | yes | yes | no | no | yes |
| productOfferingPrice | yes | yes | yes | yes | yes | yes |

Gaps: Hub/Listener event notification (TMF630 pattern) not implemented. POST
productCatalog and category not implemented. No `X-Total-Count` pagination headers.

### 2.3 TMF622 ProductOrdering (IMPLEMENTED, 100%)

**Source**: `src/order_engine/`
**Port**: 8080
**CTK run**: `specs/tmforum_standards/CTK-TMF622-ProductOrdering/` targeting
`http://127.0.0.1:8080`
**Stage 13**: 100% (63/63). All mandatory operations pass.

Operations exercised by CTK: POST /productOrder (201), GET /productOrder list (200),
GET /productOrder/{id} (200), GET with `?fields=` projection, GET with `?id=` filter,
GET /productOrder/nonexistent (404).

Gaps: Hub/Listener pattern not implemented. `X-Total-Count` header not set.
Optional null fields returned in responses (cosmetic, does not cause CTK failures).

### 2.4 TMF641 ServiceOrdering (PARTIAL)

**Source**: `src/order_engine/` -- `app/api/tmf641.py`

GET /serviceOrder and GET /serviceOrder/{id} are implemented. Service orders are created
internally by the decomposer when a product order is processed; they are not
independently creatable via POST (returns 501). CTK for TMF641 was skipped in stage 13
and has not been run.

### 2.5 TMFC003 ProductOrderDelivery Orchestration and Management (IMPLEMENTED)

Full spec at `specs/tmforum_standards/TMForum-ODA-Ready-for-publication/TMFC003-ProductOrderDeliveryOrchestrationAndManagement/`
(if present; otherwise see `networking_specs_inventory.txt` pointer to the public
TMForum ODA library).

TMFC003 defines the ODA component pattern for order orchestration via decomposition and
saga coordination. Tech-Co implements this pattern in `src/order_engine/`:
decomposer maps offering IDs to saga steps (rules.yaml), saga coordinator executes
steps sequentially with compensating rollback, southbound adapters call live NFs.
The implementation is pattern-conformant; there is no binary TMFC003 API or
conformance test kit.

### 2.6 TMF630 Hub/Listener (NOT IMPLEMENTED)

Implementing TMF630 would add event-driven notification: when an order state changes,
the order engine would POST a `ProductOrderStateChangeNotification` to any registered
listener. This would enable real BSS integration. The CTK packages for several APIs
(TMF622, TMF641, TMF640) include Hub endpoint tests that are currently skipped.

---

## 3. 3GPP Specs

Tech-Co's Python NFs are each pinned to governing 3GPP TSes via `.py.spec.txt` sidecars
in `components/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/core_network/`.

**Important transport caveat**: All NF-to-NF calls use HTTP/1.1 (FastAPI/httpx). The
spec requires HTTP/2 for the SBI (TS 29.500 Section 5). Binary protocols (NGAP/SCTP,
PFCP/UDP, NAS, GTP-U, SIP/UDP, Diameter/TCP) are simulated as HTTP REST. This is
documented in each sidecar under "GAPS VS FULL COMPLIANCE."

### 3.1 5G Core NFs

| NF | Port | Primary 3GPP TS | Key secondary specs | Implementation fidelity |
|---|---|---|---|---|
| NRF | 8000 | TS 29.510 | TS 29.500, TS 29.571, RFC 6749 (OAuth2) | PUT /nnrf-nfm/v1/nf-instances, GET /nnrf-disc/v1/nf-instances, OAuth2 token, subscriptions. Legacy /register + /discover endpoints also present. |
| AMF | 9000 | TS 29.518, TS 38.413, TS 23.502, TS 24.501 | TS 29.510 (NRF) | NGAP handover (HTTP-mock), N11 PDU session trigger, UE context CRUD. Missing: Namf_EventExposure, Namf_Location, NAS procedures. |
| SMF | 9001 | TS 29.502, TS 29.244, TS 23.502, TS 23.501 | TS 29.510 (NRF) | POST /nsmf-pdusession/v1/sm-contexts, PFCP session establishment (HTTP-mock N4). Missing: UpdateSMContext, ReleaseSMContext, Nsmf_EventExposure. |
| UPF | 9002 | TS 29.244, TS 29.281, TS 23.501 | TS 29.510 (NRF) | PFCP message types (exact match TS 29.244 Table 7.2.2.1-1), 5QI table (exact match TS 23.501 Table 5.7.4-1), GTP-U header (HTTP-mock). Transport is HTTP not UDP/2152. |
| AUSF | 9003 | TS 29.509, TS 33.501 | TS 29.510 (NRF) | Nausf_UEAuthentication, 5G-AKA vector generation, KSEAF derivation. RAND/AUTN/HXRES* structurally correct; simplified key derivation (not production AES-128). |
| UDM | 9004 | TS 29.503, TS 29.505 | TS 29.510 (NRF) | Nudm_UECM (AMF registration N8), Nudm_SDM (AM/SM subscription data N10), Nudm_UEAU (auth vectors N13). |
| UDR | 9005 | TS 29.504 | TS 29.505 | Simplified: POST /register_user, GET /get_user/{imsi} backed by SQLite (udr.db). Full Nudr_DataRepository CRUD not implemented. |
| NSSF | 9010 | TS 29.531, TS 23.501 | TS 29.510 (NRF) | Nnssf_NSSelection (N22), Nnssf_NSSAIAvailability, roaming S-NSSAI mapping, SST 1/2/3 slices configured. |
| PCF | -- | TS 29.512, TS 29.514, TS 23.503 | TS 29.510 (NRF) | Npcf_SMPolicyControl (N7), Npcf_AMPolicyControl (N15), PCC rules, 5QI profiles. |
| SCP | -- | TS 29.500, TS 23.501 | TS 29.510 (NRF) | Indirect communication proxy, load balancing (round-robin, least-load, priority), circuit breaker, routing bindings. |
| SEPP | -- | TS 29.573, TS 33.501 | TS 29.510 (NRF) | N32-c security capability negotiation, N32-f forwarding with PRINS protection, roaming partner management, message filter rules. |
| BSF | -- | TS 29.521, TS 23.501 | TS 29.510 (NRF) | Nbsf_Management: PCF binding register/discover/update/delete. Full CRUD per TS 29.521. |
| NEF | -- | TS 29.522, TS 29.551 | TS 29.510 (NRF) | Monitoring Event API, Traffic Influence API, PFD Management, AS Session with QoS, Chargeable Party. |
| CHF | -- | TS 32.290, TS 32.291, TS 29.594 | TS 29.510 (NRF) | Nchf_ConvergedCharging (N40), Nchf_SpendingLimitControl (N28), CDR generation. |

### 3.2 IMS NFs

| NF | Port | Primary 3GPP TS | Implementation fidelity |
|---|---|---|---|
| P-CSCF | 9030 | TS 24.229, TS 33.203, TS 29.214 | SIP REGISTER and INVITE (HTTP-mock JSON). Registration state machine, IPSec SA negotiation (simulated), Rx AAR to PCRF for QoS (simulated). Kamailio ims_registrar_pcscf internals used as reference. |
| I-CSCF | 9031 | TS 24.229, TS 29.228 | UAR/UAA to HSS, S-CSCF selection, routing. |
| S-CSCF | 9032 | TS 24.229, TS 29.228 | SAR/SAA to HSS, SIP dialog management, service triggering via iFC. |
| MRF (MRFC/MRFP) | 9033 | TS 23.228, TS 23.218, TS 24.147 | Conference room management, media session allocation (HTTP-mock, no real RTP). Based on FreeSWITCH mod_conference internals. |
| IMS-HSS | 9040 | TS 29.228, TS 29.229, TS 33.203, TS 35.206 | Full Cx interface: UAR/UAA, LIR/LIA, MAR/MAA, SAR/SAA, RTR/RTA, PPR/PPA. Milenage algorithm present (MD5 stand-in for AES-128). Diameter AVP codes per TS 29.229 Section 6. |

**Transport note for IMS**: All SIP messages are JSON-encoded Pydantic models POSTed to
REST endpoints. No UDP port 5060 is bound. A real SIP UA cannot connect without a
SIP-to-HTTP adapter. The cryptographic AKA uses MD5 as a stand-in for AES-128 per
TS 35.206, so auth vectors are structurally correct but not cryptographically compliant.

### 3.3 4G EPC NFs (secondary, not wired to 5G RAN)

| NF | Port | Primary spec area |
|---|---|---|
| MME | 9020 | S1AP/EMM/ESM (HTTP-mock) |
| SGW | 9021 | GTPv2-C S11/S5 (HTTP-mock) |
| PGW | 9022 | S5/Gx/Gy (HTTP-mock) |
| HSS | 9023 | S6a/Diameter (HTTP-mock) |

The 4G EPC NFs run standalone. There is no N26 EPC-to-5GC interworking path in the
current release.

### 3.4 3GPP spec coverage in the library

The `specs/3gpp_releases/` directory contains the full 3GPP Release 19 specification
bundle (21-series through 38-series, `.docx`/`.doc` format). The specs most directly
referenced by Tech-Co NF implementations are in the 23-series (architecture/procedures)
and 29-series (SBI APIs). Key files:

- TS 23.501 -- 5G System Architecture
- TS 23.502 -- Procedures for 5G System
- TS 29.500 -- Technical Realization of SBA
- TS 29.502 -- Nsmf PDU Session
- TS 29.503 -- Nudm services
- TS 29.504 -- Nudr DataRepository
- TS 29.509 -- Nausf UEAuthentication
- TS 29.510 -- Nnrf NF Management/Discovery
- TS 29.512 -- Npcf SMPolicyControl
- TS 29.518 -- Namf Communication
- TS 29.521 -- Nbsf Management
- TS 29.522 -- NEF Northbound APIs
- TS 29.531 -- Nnssf NSSelection
- TS 29.573 -- Inter-PLMN N32-c/N32-f (SEPP)
- TS 32.290/32.291 -- Converged Charging (CHF)
- TS 33.501 -- Security Architecture

---

## 4. O-RAN Specs

Tech-Co's RAN and RIC components map to O-RAN Alliance documents published via ETSI ISG
ORI. The `.tex` source files are in `specs/oran/`.

| Interface | ETSI TS | Status | Tech-Co implementation |
|---|---|---|---|
| A1 (Non-RT RIC to Near-RT RIC) | ETSI TS 103983 v3 (`ETSI_TS_103983_A1_Interface_v3.tex`) | IMPLEMENTED (HTTP-mock) | Non-RT RIC (`ran/ric/non_rt_ric.py`) serves A1 policy types; Near-RT RIC (`ran/ric/near_rt_ric.py`) receives A1-P policies. Verified in stage 25: PUT policy returns 201, status=ENFORCED. |
| E2GAP | ETSI TS 104038 v4 (`ETSI_TS_104038_WG3_E2GAP_v4.tex`) | IMPLEMENTED (HTTP-mock) | E2 Setup and E2 Control between Near-RT RIC and CU. |
| E2AP | ETSI TS 104039 v4 (`ETSI_TS_104039_E2AP_v4.tex`) | IMPLEMENTED (HTTP-mock) | E2SM-KPM and E2SM-RC RAN functions registered on CU. Verified in stage 25: E2 Setup accepted 2 RAN functions, E2 Control success=true. |
| E2SM | ETSI TS 104040 v4 (`ETSI_TS_104040_E2SM_v4.tex`) | IMPLEMENTED (HTTP-mock) | KPM and RC service models referenced in CU E2 node registration. |
| O1 management plane | ETSI TS 104043 v11 (`ETSI_TS_104043_O1_Interface_v11.tex`) | NOT IMPLEMENTED | Spec available. NETCONF/YANG management plane not implemented. |
| O2IMS (O-Cloud infra inventory) | O-RAN O2 specification | IMPLEMENTED (real adapter) | Red Hat Go binary `external/oran_o2ims/` compiled to `/tmp/oran-o2ims-binary`; connected via `src/order_engine/app/adapters/o2ims_real_adapter.py`. Binary requires live OpenShift hub with ACM to serve requests. |
| Open Fronthaul CUS plane | ETSI TS 103859 v12 (`ETSI_TS_103859_Fronthaul_CUS_v12.tex`) | NOT IMPLEMENTED | Spec available. No O-RU or fronthaul transport implemented. RRU is a stub (while-loop). |
| O-RAN Architecture | ETSI TS 103982 v8 (`ETSI_TS_103982_WG1_Architecture_v8.tex`) | REFERENCED | Governs overall O-RAN architecture; Tech-Co's split (CU/DU/RIC) follows this. |
| O-RAN Security | ETSI TS 104104/104106/104107 | REFERENCED | No security enforcement implemented. Lab only. |

**Transport note for O-RAN**: A1 and E2 are HTTP-mock REST, not the binary SCTP/ASN.1
production protocols. The procedure logic (policy types, E2 Setup, E2 Control messages)
is faithful to the specs. This is an intentional lab trade-off for testability.

Also present in `specs/oran/`:
- `ATIS_Open_RAN_MVP_v2_2025.tex` -- ATIS Open RAN MVP requirements
- `ETSI_TR_104037_Use_Cases_Analysis_v12.tex` -- O-RAN use case analysis
- `ETSI_TR_104106_Security_v3.tex` -- Security threat analysis
- `ETSI_TS_104041_Slicing_Architecture_v11.tex` -- Network slicing in O-RAN
- `ETSI_TS_104226_WG2_Use_Cases_v10.tex` -- WG2 use cases

---

## 5. IMS Specs (Summary)

The IMS NFs draw from a separate cluster of 3GPP specs covering SIP-based multimedia:

| Protocol area | Governing spec | Tech-Co status |
|---|---|---|
| SIP call control (P/I/S-CSCF) | TS 24.229 (IMS SIP), TS 23.228 (IMS Architecture) | HTTP-mock SIP; procedure logic faithful, no real SIP/UDP |
| IMS HSS Cx/Dx interface | TS 29.228, TS 29.229 | Implemented: all six Cx operations (UAR, LIR, MAR, SAR, RTR, PPR) |
| IMS authentication | TS 33.203, TS 35.206 (Milenage) | Structurally correct; MD5 stand-in for AES-128 |
| Rx interface (P-CSCF to PCRF) | TS 29.214 | Simulated (HTTP POST to PCRF URL); no real Diameter/Rx |
| Media resource control | TS 23.228, TS 24.147 | HTTP-mock; no real RTP/RTCP |

A complete VoNR call signaling trace (REGISTER + INVITE + MRF allocation + BYE) is
verified in stage 12 via `src/ims_test_client/test_vonr_call.py`.

---

## 6. ETSI Specs

ETSI NFV, MEC, and ZSM specs are in `specs/etsi/`:

| Area | Location | Tech-Co status |
|---|---|---|
| NFV (MANO, VIM, NFVI) | `specs/etsi/NFV/` | REFERENCED. Informs architecture decisions. No VIM or VNFM implemented. |
| MEC (Multi-access Edge Computing) | `specs/etsi/MEC/` | PARTIALLY REFERENCED. MEC location API sidecar present at `5G_Emulator_API/etsi/mec/location_api.py.spec.txt` and `mec_platform.py.spec.txt`. No production MEC platform implemented. |
| ZSM (Zero-touch Service Management) | `specs/etsi/ZSM/` | REFERENCED. Informs the AI observer's autonomous control-loop design. No ZSM framework implemented. |

---

## 7. AI-RAN Alliance

Whitepapers and editorial reports from the AI-RAN Alliance are in `specs/ai_ran_alliance/`:

- `AI-RAN_Alliance_Whitepaper.tex` -- foundational AI-RAN whitepaper
- `AI_in_the_RAN_Editorial_Report.tex` -- editorial summary
- `AI-RAN_Alliance_MediaBriefing_Feb2024.tex` -- Feb 2024 media briefing
- `SoftBank_AI_RAN_Whitepaper_Dec2024.tex` -- SoftBank AI-RAN whitepaper
- `NVIDIA_AI-RAN_FAQ.tex` -- NVIDIA AI-RAN FAQ
- `STL_RedHat_AI-RAN_Webinar_Presentation.tex` -- STL/Red Hat AI-RAN webinar
- `Integrating_AIML_in_Open-RAN.tex` -- AIML integration in Open RAN
- `arXiv_Transforming_RAN_AI_Computing_Infrastructure.tex` -- academic paper

Tech-Co's `src/ai_observer/` is broadly aligned in intent with the AI-RAN vision:
autonomous anomaly detection, threshold-gated control actions, and feedback to the
order engine. The ai_observer is not a conformant implementation of any specific
AI-RAN Alliance interface or API; it is an original design inspired by the architectural
concepts in these documents.

---

## 8. TM Forum CTK Runner Instructions

The CTK (Conformance Test Kit) packages ship with Node.js/Newman and run against a
live service endpoint. Two CTKs are currently configured and have achieved 100%.

### Prerequisites

- Node.js 18 or higher
- The target service running and reachable on localhost

### One-time setup

Run `npm install` inside the `ctk/` subdirectory of each CTK package:

```bash
cd Tech-Co/specs/tmforum_standards/CTK-TMF620-ProductCatalog/ctk
npm install

cd Tech-Co/specs/tmforum_standards/CTK-TMF622-ProductOrdering/ctk
npm install
```

Newman is bundled as a local `node_modules` dependency via `package.json`. No global
npm packages are required.

### Running the CTK

After the target service is running, execute the shell runner from the CTK root
(one level above `ctk/`):

```bash
# TMF622 (order_engine on port 8080)
cd Tech-Co/specs/tmforum_standards/CTK-TMF622-ProductOrdering
bash Mac-Linux-RUNCTK.sh

# TMF620 (catalog_api on port 8081)
cd Tech-Co/specs/tmforum_standards/CTK-TMF620-ProductCatalog
bash Mac-Linux-RUNCTK.sh
```

### Results

| File | Format | Description |
|---|---|---|
| `jsonResults.json` | Machine-readable JSON | Newman assertion results per test case |
| `htmlResults.html` | Human-readable HTML | Visual pass/fail report |

### Current target configuration

| CTK | Configured target |
|---|---|
| CTK-TMF622-ProductOrdering | `http://127.0.0.1:8080` |
| CTK-TMF620-ProductCatalog | `http://127.0.0.1:8081` |

To change the target URL, edit the `environment` file inside `ctk/` or pass
`--env-var` overrides to the Newman command in `Mac-Linux-RUNCTK.sh`.

### Achieved results

| CTK | Assertions | Pass rate | Build log |
|---|---|---|---|
| TMF622 ProductOrdering | 63/63 | 100% | `build_logs/stage13_tmf_ctk_conformance.md` |
| TMF620 ProductCatalog | 1421/1421 | 100% | `build_logs/stage18_tmf620_lift.md` |

Stage 13 ran the TMF620 baseline (76.4%, 469/614). Stage 18 added write methods and
the ProductOfferingPrice resource, lifting the result to 100% (1421/1421). The
assertion count increase from 614 to 1421 is expected: the CTK dynamically generates
downstream assertions once resources are successfully created.

---

## See Also

- `networking_specs_inventory.txt` -- full spec library catalogue with paths
- `build_logs/stage13_tmf_ctk_conformance.md` -- CTK baseline run details
- `build_logs/stage18_tmf620_lift.md` -- TMF620 lift to 100% details
- `docs/architecture.md` -- system architecture and layer descriptions
- `docs/components/catalog_api.md` -- catalog_api TMF620 endpoint reference
- `docs/components/order_engine.md` -- order_engine TMF622/641 endpoint reference
