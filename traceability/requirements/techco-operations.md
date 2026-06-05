# Tech-Co Operations Guide

Day-to-day reference for running the Tech-Co 5G lab stack. Covers prerequisites,
bring-up, verification, demos, and tear-down. For extending the system see
`docs/development.md`. For the testing strategy see `docs/testing.md`.

---

## Prerequisites

Install the following before running any Tech-Co script. No Homebrew installs
are performed by the lab scripts themselves; all required tools must already be
on your PATH.

| Tool | Minimum version | Used for |
|------|----------------|---------|
| Python | 3.11+ | BF3 NFs, order_engine, catalog_api, ai_observer |
| Node.js | 18+ | Storefront (optional), Newman CTK conformance |
| Go | 1.20+ | O2IMS binary (external/oran_o2ims), only if compiling from source |
| curl | any | Health checks, demo scripts |
| jq | any | JSON parsing in demo scripts (required by demo_order_flow.sh) |

**Platform**: macOS (arm64 or x86_64) or Linux. All scripts derive absolute
paths from `${BASH_SOURCE[0]}` so they are safe to call from any working
directory.

Verify your Python version:

```bash
python3 --version
```

---

## One-Time Bootstrap

Run bootstrap once before the first bring-up and whenever dependencies change.
The script is idempotent: it skips services whose venv already exists.

```bash
bash scripts/bootstrap.sh
```

What it does:

1. Creates `components/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/venv`
   and runs `pip install -r requirements.txt`.
2. Creates `src/order_engine/venv` and runs `pip install -e .`
   (editable install from `pyproject.toml`).
3. Creates `src/catalog_api/venv` and runs `pip install -e .`.

Expected output (first run):

```
[bootstrap] CREATE venv for BF3 5G_Emulator_API at .../venv
[bootstrap] OK    BF3 5G_Emulator_API venv ready.
[bootstrap] CREATE venv for order_engine at .../venv
[bootstrap] OK    order_engine venv ready.
[bootstrap] CREATE venv for catalog_api at .../venv
[bootstrap] OK    catalog_api venv ready.

[bootstrap] All venvs ready.
[bootstrap] Next step: bash scripts/bring_up.sh
```

To rebuild a venv from scratch (e.g. after a dependency change):

```bash
bash scripts/bootstrap.sh --force
```

The ai_observer service is not bootstrapped by bootstrap.sh. Bootstrap it
separately when you need it:

```bash
cd src/ai_observer && python3 -m venv venv && venv/bin/pip install -e . && cd -
```

---

## Bring Up the Full Stack

```bash
bash scripts/bring_up.sh
```

The script starts services in strict dependency order with health gates between
each step. Do not start services manually in a different order.

### Bring-up sequence

| Step | What starts | Health gate | Port |
|------|-------------|------------|------|
| 1 | BF3 5G NFs via `start_3gpp_services.sh` | `GET http://localhost:8000/health` (60s timeout) | 8000 |
| 1b | UDR database init sidecar (`init_udr_db.py`) | Script exit 0 | n/a |
| 2 | catalog_api via uvicorn | `GET http://localhost:8081/health` (30s timeout) | 8081 |
| 3 | order_engine via uvicorn | `GET http://localhost:8080/health` (30s timeout) | 8080 |

### BF3 NF startup sub-order (handled by start_3gpp_services.sh)

The BF3 script enforces its own ordering internally:

1. NRF starts first. Health polled up to 30 seconds.
2. UPF starts next. Health polled up to 20 seconds. A registration gate then
   polls `http://localhost:8000/discover/UPF` (0.5 s interval, 30 s timeout)
   until UPF appears in NRF. This prevents the SMF/UPF discovery race fixed in
   stage 22.
3. AMF, SMF, AUSF, UDM, UDR, UDSF start together.
4. CU, DU, and service_assurance start as the auxiliary wave.

If you start BF3 NFs manually (outside bring_up.sh), always start NRF first,
then UPF, then SMF.

### Port-by-port reference after bring-up

| Service | Port | Bound address | Health URL |
|---------|------|--------------|-----------|
| BF3 NRF | 8000 | 0.0.0.0 | http://localhost:8000/health |
| BF3 AMF | 9000 | 0.0.0.0 | http://localhost:9000/health |
| BF3 SMF | 9001 | 0.0.0.0 | http://localhost:9001/health |
| BF3 UPF | 9002 | 0.0.0.0 | http://localhost:9002/health |
| BF3 AUSF | 9003 | 0.0.0.0 | http://localhost:9003/health |
| BF3 UDM | 9004 | 0.0.0.0 | http://localhost:9004/health |
| BF3 UDR | 9005 | 0.0.0.0 | http://localhost:9005/health |
| BF3 UDSF | 9006 | 0.0.0.0 | http://localhost:9006/health |
| catalog_api | 8081 | 0.0.0.0 | http://localhost:8081/health |
| order_engine | 8080 | 0.0.0.0 | http://localhost:8080/health |

PID files are written to `scripts/.pids/`. Logs stream to `build_logs/run/`.

Expected bring-up output:

```
[bring_up] UP    BF3 NFs responded 200
[bring_up] INIT  UDR database (init_udr_db.py)
[init_udr_db] Table 'users' ready (created or already existed).
[bring_up] UP    catalog_api responded 200
[bring_up] UP    order_engine responded 200

[bring_up] All services up.
[bring_up] BF3 NFs      -> http://localhost:8000
[bring_up] catalog_api  -> http://localhost:8081
[bring_up] order_engine -> http://localhost:8080
```

---

## Verify Status

```bash
bash scripts/status.sh
```

The script reads PID files, probes each health URL, checks listening ports via
`lsof`, and scans recent log files for ERROR/EXCEPTION/TRACEBACK lines.

What to look for in the output:

- Each service line should show `RUNNING` and `health 200`.
- The listening port block should show `LISTENING` for ports 8000, 8080, 8081.
- The error scan section should be empty (no ERROR lines from the run logs).

Example healthy output:

```
Tech-Co Status -- Mon May 18 22:30:00 2026
------------------------------------------------------------

Services (from PID files):
  BF3 NFs               RUNNING  (PID 12345 )  health 200  port 8000
  catalog_api           RUNNING  (PID 12346 )  health 200  port 8081
  order_engine          RUNNING  (PID 12347 )  health 200  port 8080

Listening on telco ports (8000, 8080, 8081):
  port 8000: LISTENING
  port 8080: LISTENING
  port 8081: LISTENING
```

If `health 000` appears for a running process, the service is alive but not
responding. Check `build_logs/run/<service>.log` for startup exceptions.

---

## View the Dashboard

Start the static status dashboard server:

```bash
bash scripts/start_dashboard.sh
```

Then open in a browser:

```bash
open http://localhost:8095
```

The dashboard serves `dashboard/index.html` on port 8095 via Python's built-in
HTTP server. It auto-refreshes every 5 seconds by fetching from the three
backend APIs (ports 8080, 8081, 8090).

If the health dots show red while services are running, CORS is blocking
browser fetch calls. The FastAPI services allow `http://localhost:8095` and
`http://127.0.0.1:8095` by default. If you access the dashboard from a
different origin, add that origin to the relevant environment variable and
restart the service. See the environment variables section below.

Press Ctrl-C in the start_dashboard.sh terminal to stop it.

---

## End-to-End Demo: Order Flow

Requires: bring_up.sh complete, jq installed.

```bash
bash scripts/demo_order_flow.sh
```

The script walks through the full TMF620/TMF622 order journey:

1. Health-checks catalog_api and order_engine.
2. Fetches all product offerings from catalog_api (`GET /tmf-api/productCatalogManagement/v4/productOffering`).
3. Selects the first offering (typically `OFF-5G-BIZ-PREMIUM`).
4. Posts a TMF622 productOrder to order_engine (`POST /tmf-api/productOrderingManagement/v4/productOrder`).
5. Polls the order every 3 seconds (timeout 120 seconds) until the state is `completed`.

Success requires `state=completed`. If the order reaches `state=partial`, the
script exits nonzero with the message:

```
[demo] ERROR: FAIL: order ended in partial state; saga step did not complete
```

This was a deliberate hardening change in stage 22. A partial order means a
saga step did not finish, which is a real failure requiring investigation.

Expected success output:

```
==> Demo complete.
    Order id:     <uuid>
    Final state:  completed
    Offering:     5G_Business_Premium (OFF-5G-BIZ-PREMIUM)

[demo] SUCCESS
```

---

## Voice Demo: VoNR Call Flow

The VoNR demo requires the IMS NFs to be running. They are not started by
bring_up.sh and must be brought up manually first.

### Start IMS NFs in dependency order

```bash
cd components/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API
source venv/bin/activate

python core_network/ims_hss.py --host 0.0.0.0 --port 9040 &
sleep 3
python core_network/scscf.py --host 0.0.0.0 --port 9032 &
sleep 2
python core_network/icscf.py --host 0.0.0.0 --port 9031 &
sleep 2
python core_network/pcscf.py --host 0.0.0.0 --port 9030 &
sleep 2
python core_network/mrf.py --host 0.0.0.0 --port 9033 &
```

### Verify IMS NFs are healthy

```bash
for port in 9040 9032 9031 9030 9033; do
  echo "port $port: $(curl -s http://localhost:$port/health)"
done
```

Each port should return `"status": "healthy"`.

### Run the VoNR demo

```bash
bash scripts/demo_vonr_call.sh
```

The script checks that all 5 IMS ports are healthy, then runs the Python VoNR
call flow driver at `src/ims_test_client/test_vonr_call.py`. It exercises SIP
REGISTER through P-CSCF, routing via I-CSCF, S-CSCF authentication, and MRF
media resource allocation.

Exit 0 means the full call signalling sequence passed. Add `--verbose` for
step-by-step SIP flow detail.

### Stop IMS NFs

```bash
pkill -f pcscf.py; pkill -f icscf.py; pkill -f scscf.py; pkill -f ims_hss.py; pkill -f mrf.py
```

If ports linger after pkill:

```bash
lsof -ti:9030,9031,9032,9033,9040 | xargs kill -9
```

---

## O-RAN Closed Loop Demo

```bash
bash scripts/demo_oran_closed_loop.sh
```

This script manages its own process lifecycle. It starts and stops the RAN
processes internally (via an EXIT trap) and does not depend on bring_up.sh.

What it starts (in order):

| Component | Port |
|-----------|------|
| Non-RT RIC | 8096 |
| Near-RT RIC | 8095 |
| gNB | 38412 |
| CU | 38472 |
| DU | 38473 |
| O2IMS binary (optional) | 8083 |

The A1 to E2 closed loop flow:

1. GET policy types from Non-RT RIC.
2. PUT an A1 policy to Non-RT RIC.
3. GET the policy back to confirm storage.
4. Push the policy to Near-RT RIC via `/a1/policies`.
5. Confirm Near-RT RIC received the policy.
6. Register CU as an E2 node with Near-RT RIC (`/e2/setup`).
7. Send E2 control message to CU via Near-RT RIC (`/e2/control`).
8. Confirm CU E2 status.
9. (Optional, if O2IMS binary is present at `/tmp/oran-o2ims-binary`) POST a
   provisioning request, GET it back, then DELETE it.

Log output is written to `build_logs/run/oran_closed_loop_<timestamp>.log`.

Exit 0 means the A1 to E2 cycle completed. The O2IMS bonus step does not
affect the exit code.

---

## Full Integration Sweep

```bash
bash scripts/integration_test_full.sh
```

Runs all phases in sequence: pre_clean, bootstrap, bring_up, wait_udr_ready,
start_ai_observer, status, demo_order_flow, demo_vonr_call (SKIP unless IMS
NFs are running), demo_oran_closed_loop, four curl API checks, three pytest
suites, stop_all, port_cleanliness.

Expected result as of stage 22:

```
RESULT: PASS -- 17 required phases succeeded, 0 failed, 1 optional phases skipped (demo_vonr_call)
Run time: 47s
```

Timestamped log: `build_logs/run/integration_test_<timestamp>.log`

The sweep takes approximately 47 seconds on a warm machine with all venvs
already created. The demo_vonr_call phase is SKIPped (not FAILed) when IMS NFs
are not running. Start the IMS NFs before running the sweep if you want to
include VoNR.

---

## Tear Down

```bash
bash scripts/stop_all.sh
```

Stop order (reverse of start order):

1. ai_observer (if PID file exists in scripts/.pids/ai_observer.pid)
2. order_engine
3. catalog_api
4. BF3 NFs (via SIGTERM, 5 s grace, SIGKILL if needed)
5. BF3 stop_services.sh (additional NF cleanup if available)

After all kills, the script polls ports 8090, 8080, 8081, 8000 via `lsof`
for up to 10 seconds and warns if any remain bound.

Confirm everything stopped:

```bash
bash scripts/status.sh
```

All services should show `NO PID FILE` or `DEAD`.

---

## Inspecting Logs

| Log file | Contents |
|---------|---------|
| `build_logs/run/bf3_nfs.log` | stdout/stderr from start_3gpp_services.sh and all BF3 NF processes |
| `build_logs/run/catalog_api.log` | uvicorn stdout for catalog_api |
| `build_logs/run/order_engine.log` | uvicorn stdout for order_engine |
| `build_logs/run/ai_observer.log` | uvicorn stdout for ai_observer |
| `build_logs/run/init_udr_db.log` | UDR init sidecar output |
| `build_logs/run/integration_test_<timestamp>.log` | Full integration sweep output |
| `build_logs/run/oran_closed_loop_<timestamp>.log` | O-RAN closed loop demo output |
| `build_logs/run/non_rt_ric_<timestamp>.log` | Non-RT RIC output from oran demo |
| `build_logs/run/near_rt_ric_<timestamp>.log` | Near-RT RIC output from oran demo |

Build stage evidence logs live in `build_logs/` (not under `run/`) with names
like `stage6_integration_test.md`. These are historical records and are not
overwritten by subsequent runs.

---

## Environment Variables

The following environment variables control service behavior. Copy `.env.example`
to `.env` and adjust for your deployment target.

| Variable | Default | Service | Purpose |
|---------|---------|---------|---------|
| `BF3_UDR_URL` | `http://localhost:9005` | order_engine | UDR base URL for subscriber registration |
| `BF3_UDM_URL` | `http://localhost:9004` | order_engine | UDM base URL for subscription data |
| `BF3_AMF_URL` | `http://localhost:9000` | order_engine | AMF base URL for UE context |
| `BF3_SMF_URL` | `http://localhost:9001` | order_engine | SMF base URL for PDU session |
| `BF3_NSSF_URL` | `http://localhost:9010` | order_engine | NSSF base URL for slice selection |
| `ORDER_ENGINE_CORS_ORIGINS` | `http://localhost:8095,http://127.0.0.1:8095` | order_engine | Comma-separated allowed CORS origins |
| `CATALOG_API_CORS_ORIGINS` | `http://localhost:8095,http://127.0.0.1:8095` | catalog_api | Comma-separated allowed CORS origins |
| `AI_OBSERVER_CORS_ORIGINS` | `http://localhost:8095,http://127.0.0.1:8095` | ai_observer | Comma-separated allowed CORS origins |
| `O2IMS_BASE_URL` | `http://localhost:8083` | order_engine | O2IMS API base URL |
| `O2IMS_TOKEN` | (empty) | order_engine | Bearer token for O2IMS if required |
| `BF3_UDR_DB_PATH` | Tech-Co root `udr.db` | order_engine | Explicit path to UDR SQLite file (rollback) |

For the full canonical reference see `config/paths.yaml` (env_defaults section)
and `docs/reference.md` (if present).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `main.py crashed with psutil.AccessDenied` | BF3 NF called `psutil.net_connections()` globally (blocked by macOS SIP) | Fixed in stage 6. Always use `bash scripts/bring_up.sh` rather than launching `main.py` directly. |
| `SMF discovery failed: SMF not found` or orders returning 502 | UPF not registered in NRF when SMF started | Fixed in stage 22. The NRF registration gate in `start_3gpp_services.sh` prevents SMF from starting until UPF is visible in NRF. Rerun `bash scripts/bring_up.sh`. |
| `Order ends in state=partial` | BF3 NF not fully healthy, typically UDR not ready | Run `bash scripts/status.sh`. Check `build_logs/run/bf3_nfs.log`. The integration sweep's `wait_udr_ready` phase (30 s gate on port 9005) handles this automatically. If running manually, wait 10-15 s after bring-up before placing orders. Also verify `udr.db` was initialized (check `build_logs/run/init_udr_db.log`). |
| `Port 8090 still bound after stop_all` | ai_observer PID not tracked by early versions of stop_all.sh | Fixed in stage 22. `stop_all.sh` now explicitly kills ai_observer before the other services. |
| `CORS errors in dashboard` (all dots red) | Browser blocked cross-origin fetch to service APIs | Fixed in stages 20 and 23. Services allow `http://localhost:8095` by default. If accessing from a different origin, update the `*_CORS_ORIGINS` environment variable and restart the service. |
| `npm install hangs or fails` | Peer dependency conflict in storefront | Run `npm install --legacy-peer-deps` inside `src/storefront/`. |
| `bring_up.sh` times out on BF3 NFs | venv not created, or Python path issue | Run `bash scripts/bootstrap.sh --force` then retry. Check `build_logs/run/bf3_nfs.log` for the specific failure. |
| `demo_order_flow.sh: HTTP 422` | Order payload field name mismatch | The `orderItem` alias validator is present in `src/order_engine/app/models/tmf622_models.py`. Verify you have the stage 6 version of the order engine. |
| `status.sh shows RUNNING but health 000` | Service alive but port blocked or startup exception | Check `build_logs/run/<service>.log` for the exception. Most common cause is a port already in use from a previous run. Run `stop_all.sh` to clear, then `bring_up.sh`. |
| `No such table: product_orders` | order_engine SQLite DB created in wrong directory | Fixed in stage 22 integration sweep (pre_clean removes stale DB). For manual runs, delete `src/order_engine/order_engine.db` and any `order_engine.db` at Tech-Co root before starting. |
