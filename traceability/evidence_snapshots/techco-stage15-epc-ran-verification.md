# Stage 15: EPC + RAN Verification
**Date**: 2026-05-18
**Scope**: 4G EPC NFs (MME, SGW, PGW, HSS), Non-3GPP interworking (N3IWF, ipsec.py), RAN NFs (gNB, CU, DU, RRU, Near-RT RIC, Non-RT RIC)
**Venv**: `clean_5g_emulator_api/venv/` (Python 3.14.4)

---

## Pre-flight Fixes Required

Two environment issues blocked startup and were fixed in the venv (not in NF code):

1. **Jaeger exporter/SDK version mismatch**: `opentelemetry-exporter-jaeger==1.21.0` imports
   `OTEL_EXPORTER_JAEGER_AGENT_HOST` and 6 other constants that were removed from
   `opentelemetry-sdk==1.41.1`. Fix: appended the 7 missing constants as string assignments
   to `venv/lib/python3.14/site-packages/opentelemetry/sdk/environment_variables/__init__.py`.

2. **Missing OTLP gRPC exporter**: `opentelemetry-exporter-otlp-proto-grpc` was not installed.
   Fix: `pip install opentelemetry-exporter-otlp-proto-grpc` (installed 1.41.1).

---

## Results Table

| Component | File | Port | Started? | Health Check | Functional Test | Verdict |
|-----------|------|------|----------|--------------|-----------------|---------|
| MME | `core_network/mme.py` | 9020 | Yes | 200 OK - healthy, 3GPP TS 23.401 | `POST /emm/v1/attach` -> `attach_accept` with GUTI, EPS bearer (QCI-9), NAS security EEA2/EIA2 | PASS |
| SGW | `core_network/sgw.py` | 9021 | Yes | 200 OK - healthy, 3GPP TS 23.401 | `POST /s11/v1/create-session` -> `REQUEST_ACCEPTED`, S11/S5 TEIDs, PDN address 10.45.0.2 | PASS |
| PGW | `core_network/pgw.py` | 9022 | Yes | 200 OK - healthy, 3GPP TS 23.401 | `POST /s5/v1/create-session` -> `REQUEST_ACCEPTED`, PDN addr, AMBR, DNS, bearer QCI-9 | PASS |
| HSS | `core_network/hss.py` | 9023 | Yes | 200 OK - healthy, 3GPP TS 29.272, 10 pre-loaded subscribers | `POST /s6a/v1/ulr` -> result_code 2001 (DIAMETER_SUCCESS), full subscription data with APN configs | PASS |
| N3IWF | `core_network/n3iwf.py` | 9015 | Yes | 200 OK - healthy, 3GPP TS 29.502/24.502 | `POST /n3iwf/registration` -> REGISTRATION_INITIATED; `POST /n3iwf/ipsec/initiate` -> IKE SA ESTABLISHED with SPIs, AES-CBC, Child SA | PASS |
| ipsec.py | `core_network/ipsec.py` | none | N/A | N/A | N/A - library module only, no FastAPI app, no `__main__` block | LIBRARY (not a service) |
| gNB | `ran/gnb.py` | 38412 | Yes | 200 OK - healthy, 3GPP TS 38.413, rest mode | `GET /gnb_status` -> operational, cell served, PLMN 00101; `POST /ngap/initial-ue-message` -> correct 503 (AMF not running, expected) | PASS |
| CU | `ran/cu.py` | 38472 | Yes | 200 OK - healthy, 3GPP TS 38.463/38.331 | `POST /f1ap/f1-setup-request` -> SUCCESS with F1AP PDU, RRC 16.6.0, SIB1 | PASS |
| DU | `ran/du.py` | 38473 | Yes | 200 OK - healthy, 3GPP TS 38.463/38.321/38.322/38.323/38.201 | `POST /f1ap/f1-setup-response` -> SUCCESS, RRC 16.6.0, frame/slot tracking active | PASS |
| RRU | `ran/rru/rru.py` | none | N/A | N/A | N/A - stub process only (`print("RRU running...")` loop, no HTTP, no port) | STUB (not a service) |
| Near-RT RIC | `ran/ric/near_rt_ric.py` | 8095 | Yes | 200 OK - healthy, ETSI TS 104038/104039/104040 | `POST /e2/setup` -> E2 setup accepted, ranFunctionsAccepted, transactionId returned | PASS |
| Non-RT RIC | `ran/ric/non_rt_ric.py` | 8096 | Yes | 200 OK - healthy, ETSI TS 103983 | `GET /a1-p/policytypes` -> 3 ORAN types; `GET /a1-p/policytypes/ORAN_QoSTarget_1.0.0` -> full schema with QoS objectives | PASS |

---

## Components That Work

- MME (4G core, S1AP/EMM/ESM interfaces)
- SGW (4G core, GTPv2-C S11/S5 interfaces)
- PGW (4G core, S5/Gx/Gy interfaces)
- HSS (4G core, S6a/Diameter interface)
- N3IWF (Non-3GPP interworking, IKEv2/IPSec simulation)
- gNB (5G RAN, NGAP/NAS transport, SCTP-REST mode)
- CU (5G RAN, F1AP, E2, RRC 16.6.0)
- DU (5G RAN, F1AP, MAC/RLC/PDCP/PHY sublayers)
- Near-RT RIC (O-RAN, E2 interface, A1-P, xApp management)
- Non-RT RIC (O-RAN, A1-P policy types, A1-EI enrichment, rApp management)

---

## Components That Fail

- **ipsec.py**: Not a failure - it is a library module (`XfrmManager`, `IKEv2` crypto primitives) imported by n3iwf.py. No standalone service. Expected.
- **RRU (rru.py)**: Not a failure - it is a placeholder stub with a `while True: sleep(60)` loop. No HTTP server, no port, no API surface. Expected.

---

## Gaps to Address for Credible 4G + 5G + O-RAN Integrated Demo

1. **EPC-to-RAN bridge missing**: MME/SGW/PGW/HSS are standalone. The MME has no eNB connection path to the gNB (gNB speaks 5G NGAP to AMF, not S1AP to MME). A 4G+5G unified test needs either an eNB stub or a proper EPC-to-5GC interworking layer (N26 or an evolved packet core bridge). As-is, 4G and 5G live in separate planes with no cross-connection.

2. **RRU is a stub**: No RF front-end simulation, no CPRI/eCPRI protocol, no O-RU interface. The O-RAN stack is CU+DU+RIC but no O-RU. For a credible O-RAN demo the RRU needs to become at minimum an HTTP service with O-RU management endpoints (O1, M-Plane).

3. **E2 interface is one-hop only**: Near-RT RIC accepts E2 setup from gNB but the CU/DU E2 endpoints (`/e2/subscription`, `/e2/control`) are present but not wired back to the RIC in isolated tests. A closed-loop xApp demo requires CU or DU to subscribe and receive control actions.

4. **No persistent inter-NF state**: Each NF boots with in-memory state. A UE attach through MME does not provision the HSS session table, and the SGW/PGW TEID created in one process is invisible to another. An integrated test requires an orchestrated bring-up sequence (HSS first, then MME, then SGW+PGW) or a shared DB layer.

5. **gNB defaults to REST mode**: The gNB supports real NGAP/SCTP (`--mode real`) but the AMF (5G core) would need to be running. For a 4G+5G integrated demo the gNB needs to speak to both an MME (S1AP) and an AMF (NGAP) simultaneously, which the current gNB code does not support.

6. **Non-RT RIC has no southbound to Near-RT RIC**: The Non-RT RIC status shows `nearRtRicUrl: http://127.0.0.1:8095` but there is no automated A1 policy push path exercised. The link needs an end-to-end test: Non-RT RIC pushes a QoS policy via A1-P, Near-RT RIC translates it to an E2 control message to CU.

---

## Recommended Priority

**Priority 1: Wire the E2 closed loop (Near-RT RIC -> CU -> DU)**
This is the most impactful single demo path. CU and DU both have `/e2/subscription` and `/e2/control` endpoints already implemented. A working xApp subscribing to CU metrics and sending a control action back closes the O-RAN control loop and makes the Near-RT/Non-RT RIC stack credible. Estimated effort: 1-2 days of integration scripting, no new NF code needed.

**Priority 2: Replace the RRU stub with a minimal O-RU HTTP service**
Even a 200-line FastAPI service with `/o-ran-hardware/status`, `/o-ran-radio-head/config`, and a simulated antenna element array would close the O-RAN physical layer gap. This gives the demo a complete 4-layer O-RAN stack (Non-RT RIC, Near-RT RIC, O-DU, O-RU) and makes the architecture diagram match the running code. Estimated effort: 1 day.

---

## Environment Notes

- All 10 NFs/components were tested one at a time with port cleanup verified between each.
- No ports were left open at the end of testing.
- venv fix (Jaeger constants + OTLP gRPC install) is persistent and will not need to be repeated.
- All NFs use `config/ports.py` for canonical port assignments.
