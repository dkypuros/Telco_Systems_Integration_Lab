# EPC Component Reference

**Codebase**: legacy-standalone-5g-emulator Python 4G EPC implementation
**Base path**: `components/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/`
**Framework**: FastAPI + uvicorn (all NFs)
**Port config**: `config/ports.py` (EPC range: 9020-9023; N3IWF at 9015)
**Spec sidecars**: `core_network/mme.py.spec.txt`, `core_network/hss.py.spec.txt`,
and matching files for SGW and PGW

All four EPC NFs passed stage 15 verification (4/4 PASS). N3IWF (non-3GPP interworking) also
passed and is documented here alongside the EPC.

---

## Network Functions

### MME -- Mobility Management Entity

**Purpose**: 4G LTE mobility management; terminates S1AP from eNBs; handles EMM (EPS Mobility
Management) attach/detach/TAU procedures and ESM (EPS Session Management) PDN connectivity.

**Source**: `core_network/mme.py` (832 lines)
**Port**: 9020
**Spec**: 3GPP TS 23.401, TS 24.301, TS 36.413
**Spec sidecar**: `core_network/mme.py.spec.txt`

**Key endpoints** (mme.py lines 316-805):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| GET | `/mme/v1/configuration` | MME configuration (PLMN, TAC, EMM/ESM timers) |
| POST | `/s1ap/v1/enb/setup` | eNB S1AP Setup Request |
| POST | `/emm/v1/attach` | UE Attach Request; returns attach_accept with GUTI, EPS bearer |
| POST | `/emm/v1/detach` | UE Detach |
| POST | `/emm/v1/service-request` | Service Request |
| POST | `/emm/v1/tau` | Tracking Area Update |
| POST | `/esm/v1/pdn-connectivity` | PDN Connectivity Request |
| POST | `/esm/v1/pdn-disconnect` | PDN Disconnect |
| POST | `/s1ap/v1/handover/required` | S1AP Handover Required |
| POST | `/s1ap/v1/handover/notify` | S1AP Handover Notify |
| GET | `/mme/v1/ue` | List UE contexts |
| GET | `/mme/v1/ue/{ue_id}` | Get UE context |
| GET | `/mme/v1/statistics` | MME statistics |

**Stage 15 functional test**: `POST /emm/v1/attach` returned `attach_accept` with:
- GUTI assigned
- EPS bearer context with QCI-9
- NAS security algorithms EEA2 (AES-CTR) and EIA2 (AES-CMAC)

**Status**: PASS (stage 15).

---

### SGW -- Serving Gateway

**Purpose**: 4G user-plane anchor in the visited network; terminates S11 (GTPv2-C from MME)
and S5 (GTPv2-C to PGW); manages per-UE GTP-U tunnels and TEIDs.

**Source**: `core_network/sgw.py` (644 lines)
**Port**: 9021
**Spec**: 3GPP TS 23.401 (same as MME; SGW is co-specified)
**Spec sidecar**: `core_network/sgw.py.spec.txt`

**Key endpoints** (sgw.py lines 223-619):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| GET | `/sgw/v1/configuration` | SGW configuration |
| POST | `/s11/v1/create-session` | GTPv2-C Create Session Request (from MME) |
| POST | `/s11/v1/modify-bearer` | Modify Bearer Request |
| POST | `/s11/v1/delete-session` | Delete Session Request |
| POST | `/s11/v1/release-access-bearers` | Release Access Bearers Request |
| POST | `/s5/v1/create-bearer` | Create Bearer Request (toward PGW) |
| POST | `/sgw/v1/data-notification` | Downlink data notification |
| POST | `/sgw/v1/traffic` | Simulate user-plane traffic |
| GET | `/sgw/v1/sessions` | List active GTP sessions |
| GET | `/sgw/v1/sessions/{s11_sgw_teid}` | Get session by S11 TEID |
| GET | `/sgw/v1/statistics` | SGW statistics |

**Stage 15 functional test**: `POST /s11/v1/create-session` returned:
- `REQUEST_ACCEPTED`
- S11 and S5 TEIDs assigned
- PDN address 10.45.0.2

**Status**: PASS (stage 15).

---

### PGW -- Packet Data Network Gateway

**Purpose**: 4G PDN anchor; terminates S5 (from SGW) and Gx (PCEF toward PCRF) and Gy (online
charging toward OCS); allocates UE IP addresses; enforces PCC rules.

**Source**: `core_network/pgw.py` (829 lines)
**Port**: 9022
**Spec**: 3GPP TS 23.401
**Spec sidecar**: `core_network/pgw.py.spec.txt`

**Key endpoints** (pgw.py lines 332-798):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| GET | `/pgw/v1/configuration` | PGW configuration |
| POST | `/s5/v1/create-session` | GTPv2-C Create Session Request (from SGW) |
| POST | `/s5/v1/delete-session` | Delete Session |
| POST | `/s5/v1/modify-bearer` | Modify Bearer |
| POST | `/pgw/v1/create-bearer` | Create Dedicated Bearer |
| DELETE | `/pgw/v1/delete-bearer` | Delete Bearer |
| POST | `/gx/v1/install-rule` | Install Gx PCC rule |
| DELETE | `/gx/v1/remove-rule` | Remove Gx PCC rule |
| POST | `/gy/v1/report-usage` | Gy usage report (online charging) |
| GET | `/pgw/v1/sessions` | List active sessions |
| GET | `/pgw/v1/sessions/{session_id}` | Get session by ID |
| GET | `/pgw/v1/statistics` | PGW statistics |

**Stage 15 functional test**: `POST /s5/v1/create-session` returned:
- `REQUEST_ACCEPTED`
- PDN address assigned
- AMBR configured
- DNS servers provided
- Default bearer with QCI-9

**Status**: PASS (stage 15).

---

### HSS -- Home Subscriber Server (EPC)

**Purpose**: 4G subscriber database; S6a/Diameter interface for authentication (AIR/AIA) and
location update (ULR/ULA); stores subscriber profiles, APNs, and QoS parameters.

**Source**: `core_network/hss.py` (786 lines)
**Port**: 9023
**Spec**: 3GPP TS 29.272, TS 33.401, TS 35.206 (Milenage)
**Spec sidecar**: `core_network/hss.py.spec.txt`

**Key endpoints** (hss.py lines 374-758):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| GET | `/hss/v1/configuration` | HSS configuration |
| POST | `/s6a/v1/air` | Authentication-Information-Request (auth vectors) |
| POST | `/s6a/v1/ulr` | Update-Location-Request (subscriber registration) |
| POST | `/s6a/v1/pur` | Purge-UE-Request |
| POST | `/s6a/v1/clr` | Cancel-Location-Request |
| POST | `/s6a/v1/idr` | Insert-Subscriber-Data-Request |
| GET | `/hss/v1/subscribers` | List all subscribers |
| GET | `/hss/v1/subscribers/{imsi}` | Get subscriber by IMSI |
| POST | `/hss/v1/subscribers` | Provision new subscriber |
| PUT | `/hss/v1/subscribers/{imsi}` | Update subscriber |
| DELETE | `/hss/v1/subscribers/{imsi}` | Delete subscriber |
| POST | `/hss/v1/subscribers/{imsi}/apn` | Add APN configuration |
| GET | `/hss/v1/statistics` | HSS statistics |

**Pre-loaded subscribers**: 10 test subscribers seeded at startup (confirmed in stage 15 health
check response: `"subscribers": 10`).

**Stage 15 functional test**: `POST /s6a/v1/ulr` returned:
- `result_code: 2001` (DIAMETER_SUCCESS)
- Full subscription data including APN configurations

**Status**: PASS (stage 15).

---

## N3IWF -- Non-3GPP Interworking Function

**Purpose**: Enables non-3GPP access (Wi-Fi, wireline) to the 5G core; terminates IKEv2/IPSec
for UE-to-core tunneling; registers with AMF via N2; establishes IPSec SAs with UEs.

**Source**: `core_network/n3iwf.py` (736 lines) + `core_network/ipsec.py` (647 lines, library)
**Port**: 9015
**Spec**: 3GPP TS 29.502, TS 24.502
**Spec sidecar**: `core_network/n3iwf.py.spec.txt`

**Key endpoints** (n3iwf.py lines 509-712):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/n3iwf/ipsec/initiate` | Initiate IKEv2 SA establishment |
| GET | `/n3iwf/ipsec/tunnels` | List active IPSec tunnels |
| DELETE | `/n3iwf/ipsec/tunnels/{tunnelId}` | Tear down IPSec tunnel |
| POST | `/n3iwf/registration` | Register UE for non-3GPP access |
| POST | `/n3iwf/authentication/{ueId}` | Authenticate UE |
| POST | `/n3iwf/registration/{ueId}/complete` | Complete registration |
| POST | `/n3iwf/deregistration/{ueId}` | Deregister UE |
| POST | `/n3iwf/pdu-session` | Establish PDU session via non-3GPP |
| DELETE | `/n3iwf/pdu-session/{ueId}/{pduSessionId}` | Release PDU session |
| GET | `/n3iwf/ue-contexts` | List UE contexts |
| GET | `/n3iwf/ue-contexts/{ueId}` | Get UE context |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**ipsec.py**: Library module only (no FastAPI app, no `__main__` block, no port binding).
Provides `XfrmManager` and `IKEv2` crypto primitives imported by n3iwf.py. Not a standalone
service.

**Stage 15 functional test**:
- `POST /n3iwf/registration` returned `REGISTRATION_INITIATED`
- `POST /n3iwf/ipsec/initiate` returned `IKE SA ESTABLISHED` with SPIs and AES-CBC Child SA

**Status**: PASS (stage 15). N3IWF is categorized with EPC here because it bridges non-3GPP
access into the 5G core and shares the 9015 port slot adjacent to the EPC range.

---

## 4G / 5G Interworking

The EPC and 5G core NFs are currently independent planes with no cross-connection wired.

### N26 Interface (MME to AMF)

The N26 interface enables single-registration mode handover between EPC and 5G SA. It is defined
in 3GPP TS 23.502 Section 4.11 and requires:

- MME to maintain a connection to AMF (S10/N26 over GTPv2-C or REST)
- AMF to accept `POST /ngap/handover-request` with EPS-to-5GS context transfer IEs

The current MME (`core_network/mme.py`) has S1AP handover endpoints
(`POST /s1ap/v1/handover/required`, `POST /s1ap/v1/handover/notify`) but no N26 path to the
AMF (port 9000). The AMF has no MME-facing N26 receiver. N26 is documented here as a wiring
gap, not a code gap.

To enable N26:
1. MME needs a southbound HTTP client targeting AMF port 9000.
2. AMF needs an N26 receiver endpoint (e.g., `POST /n26/ue-context-transfer`).
3. The two NFs need to exchange UE MM/SM context at handover trigger.

### EPC-to-RAN bridge

The MME speaks S1AP to eNBs. The gNB (`ran/gnb.py`) speaks 5G NGAP to AMF. There is no eNB
stub or S1AP-to-NGAP translation layer in the codebase. A 4G+5G unified test would require
either a separate eNB stub or a proper EPC-to-5GC interworking layer.

### Shared subscriber data

MME and HSS use separate subscriber stores from UDR (5G) and IMS-HSS (IMS). There is no shared
IMSI database across the 4G and 5G planes. An integrated end-to-end test requires coordinated
bring-up (HSS first, then MME, then SGW+PGW) and a shared or synchronized subscriber store.

---

## Known Limitations

1. **N26 not wired**: MME and AMF have no inter-working connection. 4G-to-5G handover is not
   testable end-to-end.

2. **No eNB stub**: gNB speaks 5G NGAP; no 4G eNB component exists in the codebase. MME's
   `POST /s1ap/v1/enb/setup` cannot be exercised without an eNB counterpart.

3. **No persistent inter-NF state**: UE attach through MME does not update the HSS session
   table automatically. SGW/PGW TEIDs created in one call are invisible to other NFs unless
   explicitly coordinated.

4. **ipsec.py is a library, not a service**: It provides crypto primitives for N3IWF but has
   no standalone HTTP interface. It is listed in `component_locations.txt` as a component but
   does not bind any port.

5. **EPC NFs not NRF-registerable**: The 4G EPC NFs (MME, SGW, PGW, HSS) do not register with
   the 5G NRF. They are standalone services reachable only by direct URL.

---

## Cross-References

- 5G core NFs: `docs/components/5g_core.md`
- IMS (VoNR): `docs/components/ims.md`
- RAN and O-RAN: `docs/components/ran.md`
- Port assignments: `config/ports.py`
- Stage 15 full verification evidence: `build_logs/stage15_epc_ran_verification.md`
