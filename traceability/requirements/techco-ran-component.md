# RAN Component Reference

**Codebase**: BF3-5G-Demo Python disaggregated RAN implementation
**Base path**: `components/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/`
**Framework**: FastAPI + uvicorn (gNB, CU, DU, Near-RT RIC, Non-RT RIC)
**Port config**: `config/ports.py` (RIC: 8095/8096; gNB: 38412 default; CU: 38472; DU: 38473)
**O-RAN spec refs**: ETSI TS 104038/104039/104040 (E2), ETSI TS 103983 (A1-P)

Stage 15 verified all functional RAN NFs (gNB, CU, DU, Near-RT RIC, Non-RT RIC: all PASS).
Stage 25 captured a clean A1-to-E2 closed-loop run (exit code 0).

---

## Component Overview

| Component | Source | Port | Status |
|-----------|--------|------|--------|
| gNB | `ran/gnb.py` | 38412 (default `__main__`) | PASS (stage 15) |
| CU | `ran/cu.py` | 38472 | PASS (stage 15) |
| DU | `ran/du.py` | 38473 | PASS (stage 15) |
| Near-RT RIC | `ran/ric/near_rt_ric.py` | 8095 | PASS (stage 15, stage 25) |
| Non-RT RIC | `ran/ric/non_rt_ric.py` | 8096 | PASS (stage 15, stage 25) |
| RRU | `ran/rru/rru.py` | none | STUB (no HTTP server) |

---

## Network Functions

### gNB -- Next-Generation NodeB

**Purpose**: 5G base station; terminates NGAP (N2) toward AMF and GTP-U (N3) toward UPF;
schedules UE radio resources; supports disaggregated CU/DU split.

**Source**: `ran/gnb.py`
**Port**: 38412 (hard-coded in `__main__` at line 901: `default=38412`)
**Spec**: 3GPP TS 38.413 (NGAP)

**Key endpoints** (gnb.py lines 622-882):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/ngap/initial-ue-message` | Initial UE Message to AMF (N2) |
| POST | `/ngap/downlink-nas-transport` | Downlink NAS Transport from AMF |
| POST | `/ngap/ue-context-setup-request` | UE Context Setup Request |
| POST | `/ngap/pdu-session-resource-setup-request` | PDU Session Resource Setup |
| POST | `/ngap/handover-request` | Handover Request |
| POST | `/ngap/uplink-nas-transport` | Uplink NAS Transport toward AMF |
| POST | `/initial_ue_message` | Convenience alias for initial UE message |
| GET | `/gnb_status` | gNB operational status, cell info, PLMN |
| GET | `/gnb/ue-contexts` | Active UE contexts |
| GET | `/gnb/cell-contexts` | Served cells |
| GET | `/gnb/transport-stats` | GTP-U transport statistics |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Protocol mode**: `--mode rest` (default, HTTP only) or `--mode real` (NGAP/SCTP + GTP-U over
UDP). In rest mode, NGAP messages are HTTP POSTs. In real mode, a real SCTP connection to AMF
is established on port 38412.

**Stage 15 functional test**:
- `GET /gnb_status` returned: operational, cell served, PLMN 00101
- `POST /ngap/initial-ue-message` returned correct 503 (AMF was not running -- expected;
  confirms gNB correctly attempts the N2 connection)

**Status**: PASS (stage 15).

---

### CU -- Central Unit

**Purpose**: Upper-layer RAN processing; terminates F1AP (toward DU), E2 (toward Near-RT RIC),
and RRC (Radio Resource Control); manages UE bearers and PDCP.

**Source**: `ran/cu.py`
**Port**: 38472 (hard-coded in `__main__` at line 800: `port=38472`; also in lifespan
registration at line 383: `"port": 38472`)
**Spec**: 3GPP TS 38.463 (F1AP), TS 38.331 (RRC), ETSI TS 104038/104039/104040 (E2)

**Key endpoints** (cu.py lines 422-793):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/f1ap/f1-setup-request` | F1AP F1 Setup Request from DU |
| POST | `/f1ap/initial-ul-rrc-message` | Initial UL RRC Message Transfer |
| POST | `/f1ap/dl-rrc-message-transfer` | DL RRC Message Transfer |
| POST | `/f1ap/ue-context-setup-response` | UE Context Setup Response |
| POST | `/rrc/create-setup` | RRC Setup procedure |
| GET | `/cu/status` | CU operational status |
| GET | `/cu/ue-contexts` | Active UE contexts |
| GET | `/health` | Health check |
| POST | `/e2/subscription` | E2 subscription (from Near-RT RIC) |
| DELETE | `/e2/subscription/{ric_request_id}` | Delete E2 subscription |
| POST | `/e2/control` | E2 Control message (from Near-RT RIC) |
| GET | `/e2/status` | E2 node registration status and RAN functions |

**E2 RAN functions** (from cu.py lifespan): E2SM-KPM-CU (ranFunctionId=1) and E2SM-RC-CU
(ranFunctionId=2). Both accepted by Near-RT RIC in stage 25 (`ranFunctionsAccepted` confirmed).

**Periodic E2 reporting**: CU has a background task (`e2_periodic_report`, cu.py line 746)
that sends periodic E2 Indication reports to Near-RT RIC with CU metrics when a subscription
with `reportingPeriodMs` is active.

**Stage 15 functional test**: `POST /f1ap/f1-setup-request` returned SUCCESS with F1AP PDU,
RRC version 16.6.0, and SIB1.

**Stage 25 functional test**: E2 control message acknowledged (success=true, HTTP 200) when
Near-RT RIC posted to `POST /e2/control` via relay.

**Note**: `e2Registered` flag in `GET /e2/status` reflects CU's own self-registration attempt
to Near-RT RIC at startup (tries to reach NRF on port 8000 for discovery). In stage 25, NRF
was not running, so this flag was `false`. This is informational; the RIC-driven E2 setup path
(Near-RT RIC `POST /e2/setup`) succeeded independently and is the authoritative path for the
closed-loop demo.

**Status**: PASS (stage 15, stage 25).

---

### DU -- Distributed Unit

**Purpose**: Lower-layer RAN processing; terminates F1AP (toward CU) and fronthaul (toward
RRU); implements MAC scheduling, RLC segmentation/reassembly, PDCP, and PHY interface.

**Source**: `ran/du.py`
**Port**: 38473 (hard-coded in `__main__` at line 961: `port=38473`; also in lifespan
registration at line 481: `"port": 38473`)
**Spec**: 3GPP TS 38.463 (F1AP), TS 38.321 (MAC), TS 38.322 (RLC), TS 38.323 (PDCP),
TS 38.201 (PHY)

**Key endpoints** (du.py lines 540-943):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/f1ap/f1-setup-response` | F1AP F1 Setup Response from CU |
| POST | `/f1ap/initial-ul-rrc-message` | Initial UL RRC Message |
| POST | `/mac/process-pdu` | MAC PDU processing |
| POST | `/rlc/process-sdu` | RLC SDU processing |
| POST | `/pdcp/process-sdu` | PDCP SDU processing |
| POST | `/phy/process-prach` | PHY PRACH processing |
| GET | `/du/status` | DU operational status, frame/slot tracking |
| GET | `/health` | Health check |
| POST | `/e2/subscription` | E2 subscription (from Near-RT RIC) |
| DELETE | `/e2/subscription/{ric_request_id}` | Delete E2 subscription |
| POST | `/e2/control` | E2 Control message (from Near-RT RIC) |
| GET | `/e2/status` | E2 node registration status |

**Frame/slot tracking**: DU maintains a frame and slot counter (confirmed in stage 15:
`GET /du/status` showed `frame_slot_tracking_active: true`).

**Stage 15 functional test**: `POST /f1ap/f1-setup-response` returned SUCCESS with RRC version
16.6.0 and frame/slot tracking active.

**Status**: PASS (stage 15).

---

### Near-RT RIC -- Near-Real-Time RAN Intelligent Controller

**Purpose**: Closed-loop RAN optimization at 10 ms to 1 s timescales; accepts E2 setup from
CU/DU; manages xApp lifecycle; receives A1 policies from Non-RT RIC; sends E2 control
actions to CU/DU.

**Source**: `ran/ric/near_rt_ric.py`
**Port**: 8095 (hard-coded in `__main__` at line 894: `port=8095`)
**Spec**: ETSI TS 104038/104039/104040 (E2GAP/E2AP/E2SM)

**Key endpoints** (near_rt_ric.py lines 688-866):

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/e2/setup` | E2 node registration (from CU or DU) |
| POST | `/e2/subscription` | Create E2 subscription (HTTP 201) |
| GET | `/e2/subscriptions` | List E2 subscriptions |
| GET | `/e2/subscriptions/{subscription_id}` | Get subscription |
| DELETE | `/e2/subscriptions/{subscription_id}` | Delete subscription |
| POST | `/e2/indication` | Receive E2 Indication from E2 node |
| POST | `/e2/control` | Send E2 control to CU (relays to CU `/e2/control`) |
| POST | `/e2/query` | Query E2 node |
| GET | `/ric/e2-nodes` | List registered E2 nodes |
| GET | `/ric/e2-nodes/{e2_node_id}` | Get E2 node |
| GET | `/ric/xapps` | List registered xApps |
| POST | `/ric/xapps` | Register xApp (HTTP 201) |
| DELETE | `/ric/xapps/{xapp_id}` | Deregister xApp |
| POST | `/a1/policies` | Receive A1 policy from Non-RT RIC (HTTP 201) |
| GET | `/a1/policies` | List received A1 policies |
| DELETE | `/a1/policies/{policy_id}` | Delete A1 policy |
| POST | `/a1/enrichment` | A1 Enrichment Information |
| GET | `/ric/radio/ue/{ue_id}` | UE radio metrics |
| GET | `/ric/radio/cells` | Cell radio metrics |
| GET | `/health` | Health check |
| GET | `/ric/status` | RIC operational status |
| GET | `/metrics` | Prometheus metrics |

**Stage 25 result**:
- `POST /e2/setup` accepted CU as e2NodeId=`gnb-cu-001`, 2 RAN functions accepted
- `POST /e2/control` relayed to CU port 38472, received success=true
- `POST /a1/policies` accepted policy from Non-RT RIC (HTTP 201, status=ACTIVE)

**Status**: PASS (stage 15, stage 25).

---

### Non-RT RIC -- Non-Real-Time RAN Intelligent Controller

**Purpose**: Policy management and enrichment at greater than 1 s timescales; maintains A1-P
policy type registry; pushes policies to Near-RT RIC; manages rApps and O1 VNF intents.

**Source**: `ran/ric/non_rt_ric.py`
**Port**: 8096 (hard-coded in `__main__` at line 906: `port=8096`)
**Spec**: ETSI TS 103983 (A1-P), A1-EI

**Key endpoints** (non_rt_ric.py lines 675-875):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/a1-p/policytypes` | List supported A1-P policy types |
| GET | `/a1-p/policytypes/{policy_type_id}` | Get policy type schema |
| PUT | `/a1-p/policytypes/{policy_type_id}` | Register policy type (HTTP 201) |
| GET | `/a1-p/policytypes/{policy_type_id}/policies` | List policies for type |
| PUT | `/a1-p/policytypes/{policy_type_id}/policies/{policy_id}` | Create/update policy (HTTP 201) |
| GET | `/a1-p/policytypes/{policy_type_id}/policies/{policy_id}` | Get policy |
| DELETE | `/a1-p/policytypes/{policy_type_id}/policies/{policy_id}` | Delete policy |
| GET | `/a1-p/policytypes/{policy_type_id}/policies/{policy_id}/status` | Get policy status |
| GET | `/a1-ei/eitypes` | List A1-EI enrichment types |
| PUT | `/a1-ei/eitypes/{ei_type_id}` | Register enrichment type |
| GET | `/a1-ei/eijobs` | List enrichment jobs |
| PUT | `/a1-ei/eijobs/{ei_job_id}` | Create enrichment job |
| DELETE | `/a1-ei/eijobs/{ei_job_id}` | Delete enrichment job |
| POST | `/a1-ei/eijobs/{ei_job_id}/deliver` | Deliver enrichment data |
| GET | `/ric/rapps` | List registered rApps |
| POST | `/ric/rapps` | Register rApp (HTTP 201) |
| DELETE | `/ric/rapps/{rapp_id}` | Deregister rApp |
| GET | `/o1/intents` | O1 management intents |
| POST | `/o1/intents` | Create O1 intent |
| GET | `/o1/vnf-instances` | VNF instances |
| POST | `/o1/vnf-instances/{vnf_id}/scale` | Scale VNF |
| GET | `/ric/analytics` | RIC analytics |
| GET | `/ric/analytics/latest` | Latest analytics snapshot |
| GET | `/health` | Health check |
| GET | `/ric/status` | RIC operational status |
| GET | `/metrics` | Prometheus metrics |

**Pre-configured policy types** (from stage 25 `GET /a1-p/policytypes`):
- `ORAN_QoSTarget_1.0.0`
- `ORAN_TrafficSteering_1.0.0`
- `ORAN_LoadBalancing_1.0.0`

**Status**: PASS (stage 15, stage 25).

---

### RRU -- Remote Radio Unit

**Purpose**: Intended RF front-end simulation; O-RU interface placeholder.

**Source**: `ran/rru/rru.py`
**Port**: none (config/ports.py maps `rru` to 9103 but rru.py ignores port arguments)

**Implementation**: `while True: time.sleep(60)` loop with `print("RRU running...")`. No FastAPI
app, no HTTP server, no O-RAN Open Fronthaul endpoints, no CPRI/eCPRI protocol.

**Status**: STUB. Not a functional component. Port 9103 (and port 9009 referenced in stage 1)
never responds.

---

## A1 to E2 Closed-Loop Demo

### Script

`scripts/demo_oran_closed_loop.sh`

### Captured Run (stage 25)

Run timestamp: 2026-05-19 03:38:43 UTC. Exit code: 0. All ports clear before and after run.

**Bring-up sequence** (each NF healthy within 1 s):

```
Step 1  Non-RT RIC  port 8096  pid 5599  healthy in 1s
Step 2  Near-RT RIC port 8095  pid 5686  healthy in 1s
Step 3  gNB         port 38412 pid 5698  healthy in 1s
Step 4  CU          port 38472 pid 5711  healthy in 1s
Step 5  DU          port 38473 pid 5727  healthy in 1s
Total bring-up elapsed: ~5 seconds
```

**A1 policy push** (Non-RT RIC to Near-RT RIC):

```
GET  /a1-p/policytypes                   -> ["ORAN_QoSTarget_1.0.0",
                                             "ORAN_TrafficSteering_1.0.0",
                                             "ORAN_LoadBalancing_1.0.0"]

PUT  /a1-p/policytypes/ORAN_QoSTarget_1.0.0/policies/demo-closed-loop-policy-001
     HTTP 201 Created
     policyId:     demo-closed-loop-policy-001
     policyTypeId: ORAN_QoSTarget_1.0.0
     policyData:   {qosObjective: minimize_latency,
                    targetKpi: {maxLatencyMs: 10, minThroughputMbps: 50},
                    scope: {ueGroup: all, cells: [cell-001, cell-002]}}
     status:       ENFORCED  (Near-RT RIC was already up; push happened at creation time)

GET  /a1-p/policytypes/ORAN_QoSTarget_1.0.0/policies/demo-closed-loop-policy-001
     HTTP 200 -- policyId round-trip verified
```

**Policy propagation to Near-RT RIC**:

```
POST /a1/policies (Near-RT RIC port 8095)
     HTTP 201 Created
     policyId:   demo-closed-loop-policy-001
     status:     ACTIVE
     receivedAt: 2026-05-19T03:38:53.154130

GET  /a1/policies  ->  count=1, policy found in Near-RT RIC store
```

**E2 control to CU**:

```
POST /e2/setup (Near-RT RIC)
     HTTP 200
     e2NodeId:             gnb-cu-001
     ranFunctionsAccepted: [{ranFunctionId:1, ranFunctionRevision:1},
                            {ranFunctionId:2, ranFunctionRevision:1}]
     ranFunctionsRejected: []
     transactionId:        46c72922-acc9-498c-8002-a2fb054e14c0

POST /e2/control (Near-RT RIC, relayed to CU port 38472)
     HTTP 200
     e2NodeId:      gnb-cu-001
     ranFunctionId: 2
     success:       true
     errorCause:    null
```

**Verdict**: Closed loop demoed end-to-end. Full A1 to E2 cycle completed in one clean run.

---

## Known Gaps

1. **RRU is a stub**: No RF front-end simulation. No CPRI/eCPRI, no O-RAN Open Fronthaul
   (CUS-plane or M-plane), no O-RU management endpoints. The O-RAN stack is CU+DU+RIC but
   has no O-RU. Port 9103 never responds.

2. **HTTP-mock A1 and E2**: The A1 and E2 interfaces are HTTP/REST simulations, not real
   protocol implementations. Real A1-P uses HTTP over TLS with O-RAN security profiles. Real
   E2 uses SCTP/ASN.1 (E2AP over SCTP, per ETSI TS 104039). No SCTP sockets are opened.

3. **No real NGAP/SCTP in rest mode**: The gNB defaults to `--mode rest` where NGAP messages
   are HTTP POSTs. Real mode (`--mode real`) opens a real SCTP connection to AMF but was not
   exercised in integrated testing (AMF was not running in stage 25).

4. **CU/DU not NRF-registerable**: CU and DU attempt NRF registration at startup but NRF
   rejects them (not in `NFType` enum). They are not discoverable via NRF service discovery.
   This is accepted as-is (stage 6 decision).

5. **E2 closed loop does not propagate to DU in closed-loop demo**: Stage 25 wired Near-RT
   RIC to CU only. DU has `POST /e2/subscription` and `POST /e2/control` endpoints but they
   were not exercised in the stage 25 captured run.

6. **Non-RT RIC has no automated southbound push**: Non-RT RIC's `nearRtRicUrl` is configured
   to `http://127.0.0.1:8095` but there is no background task that pushes policies
   automatically. Policy push is triggered by the demo script calling
   `PUT /a1-p/policytypes/{type}/policies/{id}` which internally calls `POST /a1/policies`
   on Near-RT RIC at creation time.

7. **No actual RU function**: RRU (`ran/rru/rru.py`) is a placeholder loop. For a credible
   4-layer O-RAN demo (Non-RT RIC, Near-RT RIC, O-DU, O-RU) the RRU would need at minimum
   an HTTP service with O-RU management endpoints (O1, M-Plane).

---

## Cross-References

- 5G core NFs (AMF handles NGAP from gNB): `docs/components/5g_core.md`
- EPC: `docs/components/epc.md`
- O-RAN O2IMS: `docs/components/oran_o2ims.md`
- Port assignments: `config/ports.py`
- Stage 15 evidence: `build_logs/stage15_epc_ran_verification.md`
- Stage 25 captured run: `build_logs/stage25_oran_run_capture.md`
- Run log: `build_logs/run/oran_closed_loop_20260518_223843.log`
- O-RAN spec library: `4Public_Networking_Public_Data/53_O-RAN/` (ETSI TS 103983, 104038-40)
