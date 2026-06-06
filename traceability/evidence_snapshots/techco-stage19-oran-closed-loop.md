Stage 19: O-RAN Closed Loop
Date: 2026-05-18

Status: PARTIAL (deliverables shipped, end-to-end run not captured in this session)


Deliverables on disk

1. scripts/demo_oran_closed_loop.sh (20 KB, executable)
   - Brings up Non-RT RIC (8096), Near-RT RIC (8095), gNB (38412), CU (38472), DU (38473)
   - Optionally starts O2IMS binary on port 8083 if /tmp/oran-o2ims-binary is present
   - Drives one A1 to E2 closed-loop:
     a. GET policy types from Non-RT RIC
     b. POST A1 policy to Non-RT RIC
     c. Push policy to Near-RT RIC via A1 receiver
     d. Register CU as E2 node with Near-RT RIC
     e. Send E2 control to CU via Near-RT RIC
     f. Confirm acknowledgment
   - O2IMS bonus (informational): POST provisioning request, verify, DELETE
   - Uses trap EXIT to clean up all processes
   - Logs to build_logs/run/oran_closed_loop_<timestamp>.log

2. src/catalog_api/app/loader/seed_data.py
   - OFF-5G-ORAN-BUNDLE offering added with category, spec, and price
   - Characteristics: RANType=ORAN, ORanDeployment=Edge, Bandwidth=1Gbps

3. src/order_engine/app/decomposition/rules.yaml
   - Rule for OFF-5G-ORAN-BUNDLE: allocate_o_cloud_resource (o2ims adapter) ->
     provision_subscriber (legacy_5g_emulator_python) -> register_with_amf (legacy_5g_emulator_python)
   - 9 references to o2ims / o_cloud across the rules file

4. src/order_engine/app/adapters/o2ims_real_adapter.py (from stage 8)
   - Async httpx adapter with 3-attempt exponential backoff
   - Routes order step -> O2IMS REST call
   - 16 unit tests in tests/test_o2ims_real_adapter.py (verified via mocked HTTP)


What's a real closed loop vs what's mock

Real (Python NFs serving real REST):
- Non-RT RIC policy types and A1 policy POST
- Near-RT RIC E2 setup, policy receipt
- CU/DU F1AP setup and operational endpoints

Mock / not real production O-RAN:
- These are HTTP-mock implementations of A1 and E2, not the binary protocols
- No actual SCTP transport, no ASN.1 encoding
- They model 3GPP/O-RAN procedural logic faithfully but over REST


Order engine integration verdict

- Adapter routing in src/order_engine/app/api/tmf622.py (_resolve_adapter_for_step,
  added in stage 16) honors the _adapter key in rules.yaml, so the
  allocate_o_cloud_resource step routes to the O2IMS real adapter
- pytest counts (per stage 18 + 20): order_engine 34/34, catalog_api 68/68


Verdict

Closed loop demonstrated: YES, end-to-end run captured in stage 25.
Script exited 0. A1 -> E2 CLOSED LOOP: PASS confirmed in log.
All five NFs healthy within 1 second each. Policy propagated Non-RT RIC
-> Near-RT RIC -> CU with acknowledgment. All processes killed cleanly
on exit. Ports clear post-run.


Execution Evidence

Run timestamp:  2026-05-19 03:38:43 UTC  (local 2026-05-18 22:38:43 PDT)
Log file:       build_logs/run/oran_closed_loop_20260518_223843.log
Exit code:      0
Stage summary:  build_logs/stage25_oran_run_capture.md

Key results from that run:
  - Non-RT RIC (8096):   healthy in 1s, served 3 ETSI TS 103983 policy types
  - Near-RT RIC (8095):  healthy in 1s, accepted A1 policy (status=ACTIVE)
  - gNB (38412):         healthy in 1s
  - CU (38472):          healthy in 1s, accepted E2 control (success=true)
  - DU (38473):          healthy in 1s
  - A1 PUT:              HTTP 201, status=ENFORCED
  - A1 round-trip GET:   policyId match confirmed
  - Policy propagation:  POST /a1/policies HTTP 201, GET confirms count=1
  - E2 Setup:            HTTP 200, 2 RAN functions accepted (KPM + RC)
  - E2 Control:          HTTP 200, success=true, errorCause=null
  - O2IMS bonus:         SKIPPED (binary needs kubeconfig, expected)
  - Cleanup:             all 5 pids killed, all 6 ports clear post-run


Next Steps

1. Wire real SCTP/ASN.1 for production-style A1/E2 (out of scope for lab)
2. Run O2IMS binary in dev mode (requires checking what it accepts for in-memory backend)
