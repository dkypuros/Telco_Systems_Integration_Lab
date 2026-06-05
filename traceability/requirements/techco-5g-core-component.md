# 5G Core Component Reference

**Codebase**: BF3-5G-Demo Python emulator (~21,000 lines across 15 NFs)
**Base path**: `components/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/`
**Framework**: FastAPI + uvicorn (all NFs)
**Port config**: `config/ports.py` (centralized, canonical)
**Spec sidecars**: each NF has a `core_network/<nf>.py.spec.txt` tracing code sections to 3GPP TSes

---

## How to Start the 5G Core

The preferred launch path is the Tech-Co bring-up script, which calls the BF3 start script after
initializing the UDR SQLite database:

```bash
# From Tech-Co root
bash scripts/bring_up.sh
```

`bring_up.sh` does three things before handing off to BF3:

1. Creates the UDR SQLite `users` table if it does not exist (UDR startup bug: `init_db()` is
   defined but not called at import time, so the table must be seeded externally):

   ```bash
   python3 -c "
   import sqlite3
   conn = sqlite3.connect('Tech-Co/udr.db')
   conn.execute('CREATE TABLE IF NOT EXISTS users (imsi TEXT PRIMARY KEY, key TEXT NOT NULL)')
   conn.commit(); conn.close()
   "
   ```

2. Calls `components/BF3-5G-Demo/open-digital-platform-2_0/start_3gpp_services.sh`, which uses
   `${BASH_SOURCE[0]}` to derive absolute paths and launches NFs in four phases:
   - Phase 1: NRF (port 8000) -- polls `/health` up to 30 s before proceeding
   - Phase 2: UPF (port 9002) -- polls `/health` up to 20 s, then 2 s pause so UPF registers
   - Phase 3: AMF, SMF, AUSF, UDM, UDR, UDSF concurrently (SMF discovers UPF already registered)
   - Phase 4: NSSF (added stage 16), then RAN/auxiliary NFs

   As of stage 16, NSSF is included in the start script between NRF (phase 1) and AMF (phase 3).

3. Waits in a non-blocking `process.poll()` loop; `Ctrl-C` terminates all children cleanly.

To stop: `bash components/BF3-5G-Demo/open-digital-platform-2_0/stop_services.sh`

**PYTHONPATH requirement**: each NF must be launched with `PYTHONPATH` set to the
`5G_Emulator_API/` root so `from config.ports import get_port` resolves correctly.

---

## Network Functions

### NRF -- Network Repository Function

**Purpose**: Central service registry for the 5G SBA; manages NF registration, discovery, and
OAuth2 token issuance per 3GPP TS 29.510.

**Source**: `core_network/nrf.py` (722 lines)
**Port**: 8000
**Spec**: 3GPP TS 29.510, TS 29.500, TS 29.571
**Spec sidecar**: `core_network/nrf.py.spec.txt`

**Key endpoints** (from nrf.py, lines 403-698):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/oauth2/token` | Issue JWT bearer tokens (HS256) |
| PUT | `/nnrf-nfm/v1/nf-instances/{nfInstanceId}` | Register or update NF profile |
| GET | `/nnrf-nfm/v1/nf-instances/{nfInstanceId}` | Retrieve NF profile |
| PATCH | `/nnrf-nfm/v1/nf-instances/{nfInstanceId}` | Patch NF profile |
| DELETE | `/nnrf-nfm/v1/nf-instances/{nfInstanceId}` | Deregister NF |
| GET | `/nnrf-disc/v1/nf-instances` | Service discovery (query by NF type) |
| POST | `/nnrf-nfm/v1/subscriptions` | Subscribe to NF status notifications |
| POST | `/register` | Legacy registration endpoint (simulation convenience) |
| GET | `/discover/{nf_type}` | Legacy discovery by NF type |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**NFType enum** (nrf.py line 39): includes all standard 3GPP types (AMF, SMF, UPF, AUSF, UDM,
UDR, NSSF, PCF, NEF, BSF, CHF, N3IWF, UDSF, AF, SMSF, LMF, GMLC, UPF) plus `gNodeB` for
simulation. CU, DU, and SERVICE_ASSURANCE are not in the enum.

**Status**: Working. All other NFs register successfully and are discoverable. JWT secret
configurable via `NRF_JWT_SECRET` environment variable.

**NRF-registerable**: NRF itself, AMF, SMF, UPF, AUSF, UDM, UDR, UDSF, PCF, NSSF, BSF, SCP,
SEPP, NEF, CHF, N3IWF, gNB.

**Not NRF-registerable**: CU, DU, RRU, SERVICE_ASSURANCE (not in NFType enum; NRF returns 500
on `/register` for these; they run and serve HTTP but are invisible to service discovery).

**test_3gpp_compliance.py**: `test_service_health()` polls `GET /health` on NRF as the first
gate. If NRF is unhealthy, the entire compliance suite aborts.

---

### AMF -- Access and Mobility Management Function

**Purpose**: Access and mobility management, terminates N1 NAS and N2 NGAP; orchestrates PDU
session requests to SMF via N11.

**Source**: `core_network/amf.py` (1000 lines) + `core_network/amf_nas.py` (728 lines, NAS layer)
**Port**: 9000
**Spec**: 3GPP TS 29.518, TS 38.413, TS 23.502
**Spec sidecar**: `core_network/amf.py.spec.txt`

**Key endpoints** (amf.py lines 309-985):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/amf/ue/{ue_id}` | Create or update UE context (line 340) |
| GET | `/amf/ue/{ue_id}` | Retrieve UE context (line 334) |
| POST | `/amf/ue/{supi}/deregister` | Deregister UE, remove context (line 911) |
| POST | `/amf/ue/register` | Alternate registration endpoint (line 849) |
| POST | `/amf/pdu-session/create` | AMF triggers SMF PDU session via N11 (line 416) |
| POST | `/amf/handover` | Handover initiation (line 309) |
| POST | `/ngap/ng-setup` | gNB NG Setup procedure (line 453) |
| POST | `/ngap/initial-ue-message` | Initial UE Message from gNB (line 522) |
| POST | `/ngap/uplink-nas-transport` | Uplink NAS Transport (line 571) |
| POST | `/ngap/downlink-nas-transport` | Downlink NAS Transport (line 797) |
| POST | `/ngap/ue-context-release` | UE Context Release (line 603) |
| POST | `/ngap/paging` | Paging (line 671) |
| POST | `/ngap/error-indication` | Error Indication (line 737) |
| GET | `/health` | Health check (line 962) |
| GET | `/metrics` | Prometheus metrics (line 985) |
| GET | `/amf/transport-stats` | Real-protocol transport statistics (line 976) |

**Route ordering note**: `POST /amf/ue/{ue_id}` (line 340) is declared before
`POST /amf/ue/register` (line 849), so FastAPI routes the parameterized form first. The
BF3PythonAdapter uses `POST /amf/ue/{supi}` directly (confirmed in stage 11).

**Status**: Working. Registers with NRF on startup. BF3PythonAdapter calls AMF during order
activation (steps: `register_with_amf` via `POST /amf/ue/{supi}`, rollback via
`POST /amf/ue/{supi}/deregister`).

**test_3gpp_compliance.py**: `create_test_ue_context()` posts to `POST /amf/ue/test_ue_001`;
`test_3gpp_pdu_session_establishment()` posts to `POST /amf/pdu-session/create` which chains
to SMF N11.

---

### SMF -- Session Management Function

**Purpose**: PDU session lifecycle management; allocates UE IP addresses; controls UPF via N4
PFCP; handles N11 interface from AMF.

**Source**: `core_network/smf.py` (345 lines)
**Port**: 9001
**Spec**: 3GPP TS 29.502, TS 29.244, TS 23.502
**Spec sidecar**: `core_network/smf.py.spec.txt`

**Key endpoints** (smf.py lines 212-322):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/nsmf-pdusession/v1/sm-contexts` | PDU session establishment; allocates IP, notifies UPF via N4 |
| GET | `/smf/sessions` | List active PDU sessions |
| GET | `/smf_service` | Service status check |
| GET | `/smf/transport-stats` | PFCP transport statistics |
| GET | `/health` | Health check |

**Protocol mode**: `PROTOCOL_MODE` env var selects `rest` (default HTTP to UPF) or `real`
(PFCP over UDP 8805). In rest mode, SMF calls `POST /n4/sessions` on UPF directly.

**Startup race condition**: SMF discovers UPF once at startup via `GET /discover/UPF` on NRF
(smf.py line 43 sets `upf_url = None` initially). If UPF has not registered when SMF starts,
`upf_url` stays `None` and all PDU session requests return 502. The start script addresses this
by starting UPF (phase 2) before AMF/SMF (phase 3).

**Status**: Working (when started after UPF per bring-up script). BF3PythonAdapter calls SMF
during order activation (`establish_pdu_session` via `POST /nsmf-pdusession/v1/sm-contexts`).

**test_3gpp_compliance.py**: triggered indirectly via AMF `POST /amf/pdu-session/create`;
`test_smf_session_state()` independently queries `GET /smf/sessions`.

---

### UPF -- User Plane Function

**Purpose**: N4/PFCP session management, packet forwarding and traffic steering on the user
plane; N3 (toward gNB) and N6 (toward DN) interface anchor.

**Source**: `core_network/upf.py` (370 lines) + `core_network/upf_enhanced.py` (1051 lines)
**Port**: 9002
**Spec**: no spec sidecar (upf.py.spec.txt absent)
**Note**: upf_enhanced.py provides extended forwarding and PFCP state; upf.py is the entry point.

**Key endpoints** (upf.py lines 193-345):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/n4/sessions` | Create PFCP session (called by SMF on PDU establishment) |
| GET | `/upf/forwarding-rules` | List active forwarding rules and PFCP sessions |
| POST | `/upf/simulate-traffic` | Simulate traffic packet through forwarding plane |
| GET | `/upf_service` | Service status |
| GET | `/upf/transport-stats` | GTP-U transport statistics |
| GET | `/health` | Health check |

**Status**: Working. Registers with NRF on startup. Must be started and registered before SMF
initializes (phase 2 in bring-up script). Verified in stage 1: 1 active PFCP session, 1
forwarding rule after PDU establishment.

**test_3gpp_compliance.py**: `verify_n4_session_establishment()` queries
`GET /upf/forwarding-rules`; `simulate_user_plane_traffic()` posts to
`POST /upf/simulate-traffic` (returns DROPPED in emulation mode -- expected).

---

### AUSF -- Authentication Server Function

**Purpose**: Handles 5G-AKA and EAP-AKA' authentication for UEs; generates authentication
vectors; interfaces with UDM for subscriber authentication data.

**Source**: `core_network/ausf.py` (420 lines)
**Port**: 9003
**Spec**: 3GPP TS 29.509, TS 33.501, TS 29.510
**Spec sidecar**: `core_network/ausf.py.spec.txt`
**Based on**: Open5GS, Free5GC AUSF implementations

**Key endpoints** (ausf.py lines 203-396):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/nausf-auth/v1/ue-authentications` | Initiate UE authentication; returns auth context |
| PUT | `/nausf-auth/v1/ue-authentications/{authCtxId}/5g-aka-confirmation` | Confirm 5G-AKA RES* |
| GET | `/nausf-auth/v1/ue-authentications/{authCtxId}` | Retrieve authentication context |
| DELETE | `/nausf-auth/v1/ue-authentications/{authCtxId}` | Delete auth context |
| GET | `/ausf_service` | Service status |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Status**: Working. Registers with NRF on startup. Health verified in stage 1.

**test_3gpp_compliance.py**: not directly exercised by the 6-test compliance suite (which tests
AMF-SMF-UPF chain). AUSF is exercised indirectly when AMF triggers NAS authentication.

---

### UDM -- Unified Data Management

**Purpose**: Subscription data management; UE context management registration (Nudm-UECM);
access and mobility data (Nudm-SDM); authentication data generation (Nudm-UEAU).

**Source**: `core_network/udm.py` (631 lines)
**Port**: 9004
**Spec**: 3GPP TS 29.503, TS 29.505, TS 29.510
**Spec sidecar**: `core_network/udm.py.spec.txt`
**Based on**: Open5GS, Free5GC UDM implementations

**Key endpoints** (udm.py lines 329-607):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/nudm-uecm/v1/{supi}/registrations/amf-3gpp-access` | AMF registers UE context |
| GET | `/nudm-uecm/v1/{supi}/registrations/amf-3gpp-access` | Retrieve AMF registration |
| PATCH | `/nudm-uecm/v1/{supi}/registrations/amf-3gpp-access` | Update AMF registration |
| DELETE | `/nudm-uecm/v1/{supi}/registrations/amf-3gpp-access` | Deregister from AMF |
| GET | `/nudm-sdm/v1/{supi}/am-data` | Access and mobility subscription data |
| GET | `/nudm-sdm/v1/{supi}/sm-data` | Session management subscription data |
| GET | `/nudm-sdm/v1/{supi}/nssai` | Subscribed NSSAI for UE |
| POST | `/nudm-ueau/v1/{supi}/security-information/generate-auth-data` | Generate auth vectors |
| GET | `/udm_service` | Service status |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Pre-seeded subscribers**: `imsi-001010000000001` through `imsi-001010000000004`. Dynamically
provisioned SUPIs (via UDR `POST /register_user`) are not in UDM's in-memory store and return
404 on `GET /nudm-sdm/v1/{supi}/am-data` -- this is expected and handled gracefully by
BF3PythonAdapter (stage 11).

**Status**: Working. BF3PythonAdapter calls UDM during order activation (`provision_subscriber`
verify step: `GET /nudm-sdm/v1/{supi}/am-data`; slice step:
`GET /nudm-sdm/v1/{supi}/nssai`).

---

### UDR -- Unified Data Repository

**Purpose**: Raw subscriber data storage (SQLite-backed); provides persistent IMSI/key store
that UDM reads from; minimal REST surface.

**Source**: `core_network/udr.py` (+ `udr.db` SQLite file)
**Port**: 9005
**Spec**: 3GPP TS 29.504, TS 29.505
**Spec sidecar**: `core_network/udr.py.spec.txt`

**Key endpoints** (udr.py lines 27-48):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/register_user` | Store IMSI + key in SQLite `users` table |
| GET | `/get_user/{imsi}` | Retrieve subscriber record |
| GET | `/health` | Health check |

**Startup prerequisite**: `init_db()` must be called before first `/register_user` request.
The bring-up script handles this. The UDR database file is at `Tech-Co/udr.db`.

**Status**: Working. BF3PythonAdapter calls `POST /register_user` in the `provision_subscriber`
step. No DELETE endpoint exists; subscriber rollback is log-only (known gap, stage 16).

---

### UDSF -- Unstructured Data Storage Function

**Purpose**: General-purpose unstructured data storage (SQLite-backed); stores arbitrary
structured data blobs for NFs that require persistent state outside their own memory.

**Source**: `core_network/udsf.py` (+ `udsf.db` SQLite file)
**Port**: 9006
**Spec**: no spec sidecar (udsf.py.spec.txt absent)

**Key endpoints** (udsf.py lines 27-48):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/store_data` | Store arbitrary JSON blob with ID |
| GET | `/get_data/{id}` | Retrieve stored data by ID |
| GET | `/health` | Health check |

**Status**: Working. SQLite-backed. Registers with NRF on startup (stage 1 confirmed). Not
directly exercised by compliance tests or order flow demos.

---

### PCF -- Policy Control Function

**Purpose**: Session management policy control (SM-PCF) and access/mobility policy control
(AM-PCF); installs PCC rules and QoS data; interfaces with SMF via Npcf-SMPolicyControl.

**Source**: `core_network/pcf.py` (762 lines)
**Port**: 9007
**Spec**: 3GPP TS 29.507, TS 29.512, TS 29.514
**Spec sidecar**: `core_network/pcf.py.spec.txt`
**Based on**: Open5GS, Free5GC PCF implementations

**Key endpoints** (pcf.py lines 510-741):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/npcf-smpolicycontrol/v1/sm-policies` | Create SM policy (SMF calls on PDU establishment) |
| GET | `/npcf-smpolicycontrol/v1/sm-policies/{smPolicyId}` | Retrieve SM policy |
| PATCH | `/npcf-smpolicycontrol/v1/sm-policies/{smPolicyId}` | Update SM policy |
| DELETE | `/npcf-smpolicycontrol/v1/sm-policies/{smPolicyId}` | Delete SM policy |
| POST | `/npcf-am-policy-control/v1/policies` | Create AM policy |
| GET | `/pcf/pcc-rules` | List installed PCC rules |
| GET | `/pcf/qos-data` | List QoS data profiles |
| POST | `/pcf/pcc-rules` | Add PCC rule |
| POST | `/pcf/qos-data` | Add QoS data profile |
| GET | `/pcf/status` | PCF operational status |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Status**: Working. Not exercised by the 6-test compliance suite; called by SMF internally
during PDU session establishment.

---

### NSSF -- Network Slice Selection Function

**Purpose**: Slice selection for UE registration and PDU session establishment; returns
authorized S-NSSAI and NSI information based on subscribed and requested NSSAI.

**Source**: `core_network/nssf.py` (882 lines)
**Port**: 9010
**Spec**: 3GPP TS 29.531, TS 23.501, TS 29.571
**Spec sidecar**: `core_network/nssf.py.spec.txt`
**Based on**: Free5GC NSSF implementation

**Key endpoints** (nssf.py lines 660-860):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/nnssf-nsselection/v1/network-slice-information` | Slice selection (registration or PDU) |
| PUT | `/nnssf-nssaiavailability/v1/nssai-availability/{nfId}` | Update NSSAI availability |
| PATCH | `/nnssf-nssaiavailability/v1/nssai-availability/{nfId}` | Patch NSSAI availability |
| DELETE | `/nnssf-nssaiavailability/v1/nssai-availability/{nfId}` | Delete NSSAI availability |
| POST | `/nnssf-nssaiavailability/v1/nssai-availability/subscriptions` | Subscribe to NSSAI notifications |
| DELETE | `/nnssf-nssaiavailability/v1/nssai-availability/subscriptions/{subscriptionId}` | Delete subscription |
| GET | `/nssf/configuration` | PLMN/TAI configuration |
| GET | `/nssf/slices` | List configured slice instances |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Pre-configured slices** (stateless selection, no persistent allocation):

| SST | SD | NSI ID | Type |
|-----|----|--------|------|
| 1 | 010203 | nsi-embb-001, nsi-embb-002 | eMBB |
| 2 | 010203 | nsi-urllc-001 | URLLC |
| 3 | 010203 | nsi-miot-001 | MIoT |
| 1 | (null) | nsi-default-001 | Default |

**Start script**: NSSF was added to `start_3gpp_services.sh` in stage 16, launched between NRF
and AMF. Before stage 16, it was not started by default.

**Status**: Working (stage 16). BF3PythonAdapter calls NSSF in the `allocate_slice` step:
`GET /nnssf-nsselection/v1/network-slice-information?nf-type=AMF&nf-id=...` with
`SliceInfoForRegistration` body. Returns `AuthorizedNetworkSliceInfo` with allowed S-NSSAI.

---

### NEF -- Network Exposure Function

**Purpose**: Secure northbound exposure of 5G core capabilities to external AFs; handles
monitoring events, traffic influence, PFD management, and QoS for AS sessions.

**Source**: `core_network/nef.py` (697 lines)
**Port**: 9016
**Spec**: 3GPP TS 29.522, TS 29.551, TS 23.502
**Spec sidecar**: `core_network/nef.py.spec.txt`

**Key endpoints** (nef.py lines 400-674):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/3gpp-monitoring-event/v1/subscriptions` | Create monitoring event subscription |
| GET | `/3gpp-monitoring-event/v1/subscriptions` | List subscriptions |
| GET | `/3gpp-monitoring-event/v1/subscriptions/{subscriptionId}` | Get subscription |
| DELETE | `/3gpp-monitoring-event/v1/subscriptions/{subscriptionId}` | Delete subscription |
| POST | `/3gpp-traffic-influence/v1/subscriptions` | Create traffic influence subscription |
| GET | `/3gpp-traffic-influence/v1/subscriptions` | List traffic influence subscriptions |
| DELETE | `/3gpp-traffic-influence/v1/subscriptions/{subscriptionId}` | Delete traffic influence subscription |
| POST | `/3gpp-pfd-management/v1/transactions` | Create PFD management transaction |
| GET | `/3gpp-pfd-management/v1/transactions` | List PFD transactions |
| POST | `/3gpp-as-session-with-qos/v1/subscriptions` | AS session with QoS |
| GET | `/3gpp-as-session-with-qos/v1/subscriptions` | List AS-QoS subscriptions |
| DELETE | `/3gpp-as-session-with-qos/v1/subscriptions/{subscriptionId}` | Delete AS-QoS subscription |
| POST | `/3gpp-chargeable-party/v1/transactions` | Chargeable party transaction |
| GET | `/3gpp-chargeable-party/v1/transactions` | List chargeable party transactions |
| POST | `/nef/test-notification` | Inject test notification |
| GET | `/nef/notification-history` | Notification history |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Status**: Working. Not exercised by core compliance tests or order flow demos.

---

### CHF -- Charging Function

**Purpose**: Converged charging for 5G sessions; spending limit control; generates CDRs; manages
per-SUPI subscriber balance.

**Source**: `core_network/chf.py` (766 lines)
**Port**: 9013
**Spec**: 3GPP TS 32.290, TS 32.291, TS 29.594
**Spec sidecar**: `core_network/chf.py.spec.txt`

**Key endpoints** (chf.py lines 544-740):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/nchf-convergedcharging/v3/chargingData` | Create charging data session (HTTP 201) |
| POST | `/nchf-convergedcharging/v3/chargingData/{chargingDataRef}/update` | Update charging data |
| POST | `/nchf-convergedcharging/v3/chargingData/{chargingDataRef}/release` | Release charging session |
| POST | `/nchf-spendinglimitcontrol/v1/subscriptions` | Subscribe to spending limit notifications |
| GET | `/nchf-spendinglimitcontrol/v1/subscriptions/{subscriptionId}` | Get spending limit subscription |
| DELETE | `/nchf-spendinglimitcontrol/v1/subscriptions/{subscriptionId}` | Delete spending limit subscription |
| GET | `/chf/sessions` | List active charging sessions |
| GET | `/chf/cdrs` | List CDRs |
| GET | `/chf/rating-config` | Rating configuration |
| POST | `/chf/subscriber-balance` | Set subscriber balance |
| GET | `/chf/subscriber-balance/{supi}` | Get subscriber balance |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Status**: Working. Not exercised by core compliance tests.

---

### BSF -- Binding Support Function

**Purpose**: PCF binding management; maps UE sessions to a specific PCF instance to avoid
double-binding; supports dynamic PCF discovery.

**Source**: `core_network/bsf.py` (520 lines)
**Port**: 9011
**Spec**: 3GPP TS 29.521, TS 23.501, TS 29.571
**Spec sidecar**: `core_network/bsf.py.spec.txt`

**Key endpoints** (bsf.py lines 329-498):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/nbsf-management/v1/pcfBindings` | Create PCF binding (HTTP 201) |
| GET | `/nbsf-management/v1/pcfBindings` | Discover PCF binding |
| GET | `/nbsf-management/v1/pcfBindings/{bindingId}` | Get binding by ID |
| PATCH | `/nbsf-management/v1/pcfBindings/{bindingId}` | Update binding |
| DELETE | `/nbsf-management/v1/pcfBindings/{bindingId}` | Delete binding (HTTP 204) |
| GET | `/bsf/bindings` | List all bindings (simulation convenience) |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Status**: Working. Not exercised by core compliance tests.

---

### SCP -- Service Communication Proxy

**Purpose**: Indirect SBA communication; routes inter-NF messages, caches NRF discovery results,
manages routing bindings; implements indirect communication model per TS 29.500.

**Source**: `core_network/scp.py` (618 lines)
**Port**: 9012
**Spec**: 3GPP TS 29.500, TS 23.501, TS 29.510
**Spec sidecar**: `core_network/scp.py.spec.txt`

**Key endpoints** (scp.py lines 453-593):

| Method | Path | Purpose |
|--------|------|---------|
| ALL | `/scp/{target_nf_type}/{path:path}` | Generic proxy to target NF (GET/POST/PUT/PATCH/DELETE) |
| POST | `/scp/nf-instances` | Register NF in SCP routing table |
| DELETE | `/scp/nf-instances/{nfInstanceId}` | Deregister NF |
| GET | `/scp/nf-instances` | List registered NFs |
| POST | `/scp/routing-bindings` | Create routing binding |
| GET | `/scp/routing-bindings/{bindingId}` | Get routing binding |
| DELETE | `/scp/routing-bindings/{bindingId}` | Delete routing binding |
| POST | `/scp/refresh-cache` | Refresh NRF discovery cache |
| GET | `/scp/config` | SCP configuration |
| PATCH | `/scp/config` | Update SCP configuration |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Status**: Working. Not exercised by core compliance tests.

---

### SEPP -- Security Edge Protection Proxy

**Purpose**: Inter-PLMN roaming security; N32-c security capability negotiation; N32-f message
forwarding with encryption and integrity protection.

**Source**: `core_network/sepp.py` (716 lines)
**Port**: 9014
**Spec**: 3GPP TS 29.573, TS 33.501, TS 29.500
**Spec sidecar**: `core_network/sepp.py.spec.txt`

**Key endpoints** (sepp.py lines 471-693):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/n32c-handshake/v1/security-capability-negotiation` | N32-c security negotiation |
| POST | `/n32c-handshake/v1/security-capability-termination` | Terminate N32-c session |
| POST | `/n32f-forward/v1/n32f-process` | N32-f message forwarding |
| POST | `/n32f-forward/v1/n32f-error` | N32-f error handling |
| POST | `/sepp/roaming-partners` | Add roaming partner |
| GET | `/sepp/roaming-partners` | List roaming partners |
| GET | `/sepp/roaming-partners/{partnerId}` | Get roaming partner |
| DELETE | `/sepp/roaming-partners/{partnerId}` | Remove roaming partner |
| GET | `/sepp/n32-peers` | List N32 peers |
| GET | `/sepp/active-connections` | Active connections |
| GET | `/sepp/filter-rules` | List filter rules |
| POST | `/sepp/filter-rules` | Add filter rule |
| DELETE | `/sepp/filter-rules/{ruleId}` | Delete filter rule |
| GET | `/sepp/protection-policy` | Protection policy |
| PUT | `/sepp/protection-policy` | Update protection policy |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Status**: Working. Not exercised by core compliance tests.

---

## Compliance Test Coverage

`components/BF3-5G-Demo/open-digital-platform-2_0/test_3gpp_compliance.py`

Six tests, all pass (6/6, stage 1 result):

| Test | NFs exercised | What it checks |
|------|--------------|----------------|
| `service_health` | NRF, AMF, SMF, UPF | `GET /health` on NRF; `GET /metrics` on AMF; `GET /smf_service` on SMF; `GET /upf_service` on UPF |
| `ue_context_creation` | AMF | `POST /amf/ue/test_ue_001` with IMSI/SUPI/location |
| `pdu_session_establishment` | AMF, SMF, UPF | `POST /amf/pdu-session/create` triggers N11 to SMF which runs N4 to UPF |
| `n4_session_verification` | UPF | `GET /upf/forwarding-rules` confirms active PFCP session and forwarding rule |
| `smf_session_verification` | SMF | `GET /smf/sessions` confirms active session with UE IP 10.2.0.1 |
| `traffic_simulation` | UPF | `POST /upf/simulate-traffic` -- returns DROPPED (no active bearer, expected in emulation) |

---

## Known Limitations

1. **main.py unusable on macOS without sudo**: `kill_process_on_port()` originally called
   `psutil.net_connections()` which is blocked by macOS SIP. Fixed in stage 6 (`main.py`
   lines 25-51). Use `scripts/bring_up.sh` which calls the rewritten `start_3gpp_services.sh`.

2. **SMF UPF discovery race**: SMF discovers UPF once at startup; no retry. Bring-up script
   resolves this by ensuring UPF is registered before SMF starts.

3. **CU, DU, SERVICE_ASSURANCE not NRF-registerable**: `NFType` enum in `nrf.py` (line 39)
   follows strict 3GPP TS 29.510 and does not include these simulation-specific types. NRF
   returns 500 on their `/register` calls. They run correctly but are invisible to
   service discovery. Decision in stage 6: accepted as-is.

4. **RRU is a stub**: `ran/rru/rru.py` is a `while True: time.sleep(60)` loop. No HTTP server,
   no port binding. Port 9103 never responds.

5. **NSSF not in start script before stage 16**: Added to `start_3gpp_services.sh` in stage 16.
   If running an older bring-up sequence, NSSF (port 9010) may not be started.

6. **UDR has no DELETE endpoint**: Subscriber rollback on order failure is log-only (stage 16).

7. **UDM has no POST for NSSAI write**: `nssai-update` returns 404 for dynamic SUPIs;
   BF3PythonAdapter handles this gracefully (stage 16).

8. **main.py blocking wait design**: original `process.wait()` called sequentially -- NRF
   blocks forever. Fixed in stage 6 with non-blocking `process.poll()` loop.

---

## Cross-References

- Order engine adapter that calls AMF, SMF, UDR, UDM, NSSF:
  `src/order_engine/app/adapters/bf3_python_adapter.py`
- O2IMS adapter (separate southbound, does not call BF3 NFs directly):
  `src/order_engine/app/adapters/o2ims_real_adapter.py`
- Decomposition rules linking product offerings to NF step sequences:
  `src/order_engine/app/decomposition/rules.yaml`
- Port assignments (canonical): `config/ports.py`
- EPC (4G) NFs: see `docs/components/epc.md`
- IMS (VoNR) NFs: see `docs/components/ims.md`
- RAN and O-RAN: see `docs/components/ran.md`
