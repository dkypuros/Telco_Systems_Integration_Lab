# Tech-Co Testing Guide

The testing strategy for the Tech-Co 5G lab. Covers the test pyramid, how to
run each layer, mocking patterns, test data, and CI-readiness notes.

For running the stack see `docs/operations.md`. For extending the system see
`docs/development.md`.

---

## Test Pyramid

```
         [ E2E demos ]        demo_order_flow, demo_vonr_call, demo_oran_closed_loop
        [  Integration  ]     integration_test_full.sh (17 PASS / 0 FAIL / 1 SKIP)
       [ TMF Conformance ]    CTK TMF620 1421/1421 (100%), CTK TMF622 63/63 (100%)
      [ 3GPP Compliance  ]    test_3gpp_compliance.py 6/6 pass
     [    Unit Tests      ]   148+ tests across 3 services (pytest)
```

| Layer | Count | Coverage area |
|-------|-------|--------------|
| Unit tests | 148+ (43 order_engine, 68 catalog_api, 37 ai_observer) | Individual functions, adapters, models, analyzers |
| TMF Conformance (CTK) | 1484 tests (1421 TMF620 + 63 TMF622) | API contract conformance to TM Forum standards |
| 3GPP compliance | 6/6 | BF3 NF protocol compliance (NRF, AMF, SMF) |
| Integration sweep | 17 phases | Full stack from bootstrap through port cleanliness |
| E2E demos | 3 scripts | Customer-facing flows (order, voice, O-RAN closed loop) |

---

## Unit Tests

### order_engine (43 tests)

```bash
cd /path/to/Tech-Co/src/order_engine
pytest -v
```

Test files in `src/order_engine/tests/`:

| File | What it tests |
|------|--------------|
| `test_tmf622.py` | TMF622 order creation, state machine, decomposer routing |
| `test_o2ims_real_adapter.py` | O2IMS adapter activate/rollback with httpx mock transport |
| `test_bf3_adapter_env_config.py` | BF3 adapter reads NF URLs from environment variables |
| `test_bf3_adapter_rollback_real.py` | BF3 adapter rollback paths (UDR sidecar, AMF deregister) |
| `test_decomposer.py` | Rules YAML parsing, offering-to-step mapping |
| `test_saga.py` | Saga coordinator success, partial failure, compensating rollback |

### catalog_api (68 tests)

```bash
cd /path/to/Tech-Co/src/catalog_api
pytest -v
```

Test files in `src/catalog_api/tests/`:

| File | What it tests |
|------|--------------|
| `test_product_offering.py` | GET list, GET by ID, filtering, TMF620 schema conformance |
| `test_product_specification.py` | CRUD on product specifications |
| `test_category.py` | Category hierarchy, parent/child references |
| `test_catalog.py` | Top-level catalog retrieval |
| `test_seed_data.py` | All 5 seed offerings are present and schema-valid after startup |

### ai_observer (37 tests)

```bash
cd /path/to/Tech-Co/src/ai_observer
pytest -v
```

Test files in `src/ai_observer/tests/`:

| File | What it tests |
|------|--------------|
| `test_collectors.py` | BF3NfCollector, OrderEngineCollector, OtelLogCollector with mocked HTTP |
| `test_analyzers.py` | LatencyAnalyzer, OrderFailureAnalyzer alert generation |
| `test_actuators.py` | NfRestartActuator, OrderRetryActuator, PlaybookActuator can_act/execute |
| `test_action_engine.py` | Confidence threshold gating, propose vs execute paths |
| `test_health.py` | GET /health returns 200 with correct schema |

### Using alternate venv names

The integration sweep looks for pytest in both `venv/` and `.venv/`. If your
venv uses the `.venv` convention, pytest will still be found. For manual runs,
call the venv's pytest directly:

```bash
src/order_engine/venv/bin/pytest -v
src/catalog_api/venv/bin/pytest -v
src/ai_observer/venv/bin/pytest -v
```

---

## TMF Conformance Test Kits

The TM Forum provides Conformance Test Kits (CTKs) built on Newman (Postman
CLI runner). Both CTKs ship inside `specs/tmforum_standards/`.

### Prerequisites

Node.js 18+ and Newman must be installed. Install Newman once inside the CTK
directory (each CTK has its own `package.json`):

```bash
cd specs/tmforum_standards/CTK-TMF622-ProductOrdering/ctk
npm install
cd ../CTK-TMF620-ProductCatalog/ctk
npm install
```

If `npm install` fails with peer dependency errors:

```bash
npm install --legacy-peer-deps
```

### TMF622 Product Ordering CTK (63/63 at 100%)

Requires: order_engine running on port 8080.

```bash
bash scripts/bring_up.sh   # if not already running

cd specs/tmforum_standards/CTK-TMF622-ProductOrdering
bash Mac-Linux-RUNCTK.sh
```

Results are written to:
- `jsonResults.json`: machine-readable pass/fail per test case
- `htmlResults.html`: human-readable report

### TMF620 Product Catalog CTK (1421/1421 at 100%)

Requires: catalog_api running on port 8081.

```bash
bash scripts/bring_up.sh   # if not already running

cd specs/tmforum_standards/CTK-TMF620-ProductCatalog
bash Mac-Linux-RUNCTK.sh
```

Results are written to the same `jsonResults.json` and `htmlResults.html`
pattern in the CTK directory.

### Interpreting CTK output

The CTK runner prints a summary line like:

```
TMF620 Conformance Tests | 1421 passing (8s)
```

Any failures appear as `X failing` with the failing test name. A test failure
means the API response does not match the TMF specification schema or behavior.

---

## 3GPP Compliance Smoke Test

Tests that the BF3 NFs conform to the relevant 3GPP interfaces.

Requires: BF3 NFs running (bring_up.sh or manual start).

```bash
cd components/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API
source venv/bin/activate
python test_3gpp_compliance.py
```

Expected output: `6/6 pass` covering NRF registration (TS 29.510), AMF UE
context (TS 23.502), SMF PDU session (TS 23.502), AUSF authentication
(TS 33.501), UDM subscription data (TS 29.505), and UDR data storage
(TS 29.504).

---

## Integration Sweep

The integration sweep runs all layers of the test pyramid in sequence against
the live stack. It is the primary gate for verifying a complete Tech-Co build.

```bash
bash scripts/integration_test_full.sh
```

The sweep manages its own lifecycle: it runs `stop_all.sh` first (pre_clean),
then `bootstrap.sh`, then `bring_up.sh`, and tears everything down at the end.

### Phase list

| Phase | Type | Notes |
|-------|------|-------|
| pre_clean | lifecycle | Stops any running services, removes stale DB files |
| bootstrap | lifecycle | Creates venvs, installs dependencies |
| bring_up | lifecycle | Starts BF3 NFs, catalog_api, order_engine |
| wait_udr_ready | health gate | Polls port 9005 up to 30 s (UDR startup lag) |
| start_ai_observer | lifecycle | Starts ai_observer on port 8090 |
| status | verification | Runs status.sh, confirms all services RUNNING |
| demo_order_flow | E2E demo | Full TMF622 order to state=completed |
| demo_vonr_call | E2E demo | **SKIP** unless IMS NFs are running on 9030-9033, 9040 |
| demo_oran_closed_loop | E2E demo | A1 to E2 closed loop with RIC and RAN NFs |
| curl_catalog_offerings | API check | GET /productOffering returns HTTP 200 |
| curl_order_engine_orders | API check | GET /productOrder returns HTTP 200 |
| curl_ai_observer_summary | API check | GET /summary returns HTTP 200 |
| curl_ai_observer_alerts | API check | GET /alerts returns HTTP 200 |
| pytest_order_engine | unit | 43 tests |
| pytest_catalog_api | unit | 68 tests |
| pytest_ai_observer | unit | 37 tests |
| stop_all | lifecycle | Stops all services |
| port_cleanliness | verification | Confirms ports 8000/8080/8081/8090/9000-9006 released |

### Expected result (stage 22 baseline)

```
RESULT: PASS -- 17 required phases succeeded, 0 failed, 1 optional phases skipped (demo_vonr_call)
Run time: 47s
```

SKIP phases are not failures. `demo_vonr_call` is SKIPped when IMS NFs are not
running on ports 9030-9033 and 9040. Start IMS NFs before running the sweep to
include this phase.

### Log location

```
build_logs/run/integration_test_<YYYY-MM-DD_HHMMSS>.log
```

Each phase is delimited by a `====` banner in the log. Grep for `FAIL` to find
failing phases without reading the full log:

```bash
grep -E "^>>> .* FAIL" build_logs/run/integration_test_*.log | tail -20
```

---

## O-RAN Closed Loop Run Capture

To run and capture the O-RAN closed loop demo independently of the full sweep:

```bash
bash scripts/demo_oran_closed_loop.sh
```

Log: `build_logs/run/oran_closed_loop_<timestamp>.log`

The script handles its own bring-up and teardown of the RAN NFs (Non-RT RIC,
Near-RT RIC, gNB, CU, DU) via an EXIT trap. It does not require `bring_up.sh`
to be run first. A1, E2, and optional O2IMS phases are all captured to the log.

---

## Mocking Strategy

### HTTP-level mocking for adapter tests

Use `httpx.MockTransport` or `respx` (a higher-level respx library) to mock
outbound HTTP calls from adapters without requiring live NF endpoints.

The canonical pattern from `test_o2ims_real_adapter.py`:

```python
import httpx
import pytest
from app.adapters.o2ims_real_adapter import O2IMSRealAdapter

@pytest.mark.asyncio
async def test_activate_allocate_creates_provisioning_request():
    # Build a MockTransport that intercepts the POST to /provisioningRequests
    def handler(request: httpx.Request) -> httpx.Response:
        assert "/provisioningRequests" in str(request.url)
        return httpx.Response(
            201,
            json={"id": "pr-001", "status": "accepted"},
        )

    adapter = O2IMSRealAdapter()
    # Patch httpx.AsyncClient to use the mock transport
    # ... (see test file for full fixture pattern)
    result = await adapter.activate("allocate_o_cloud_resource", {
        "templateName": "oran-edge-slice",
        "templateVersion": "v1",
        "templateParameters": {"sst": 1},
    })
    assert result["status"] == "success"
    assert "provisioning_request_id" in result
```

### Database isolation for order_engine tests

The order_engine uses SQLite. Tests use either:
- An in-memory SQLite database (`sqlite:///:memory:`) configured via the
  test-specific database URL override.
- A temporary file path via `tmp_path` (pytest fixture) that is deleted after
  the test session.

See `src/order_engine/tests/conftest.py` for the fixture that wires the
in-memory database into the FastAPI app.

### FastAPI TestClient with lifespan

For endpoint tests that need the full app lifecycle (startup events, DB init),
use the `TestClient` with the lifespan context manager:

```python
from fastapi.testclient import TestClient
from app.main import app

# The TestClient runs the lifespan on enter/exit
with TestClient(app) as client:
    response = client.get("/health")
    assert response.status_code == 200
```

See `src/catalog_api/tests/conftest.py` for the existing fixture pattern.

---

## Test Data

### Catalog seed offerings

Five product offerings are seeded automatically at startup by
`src/catalog_api/app/loader/seed_data.py`. These are used by all integration
tests and demo scripts.

| Offering ID | Name | Monthly price |
|-------------|------|--------------|
| `OFF-5G-BIZ-PREMIUM` | 5G_Business_Premium | $299.00 |
| `OFF-5G-CON-MOBILE` | 5G_Consumer_Mobile | $49.99 |
| `OFF-5G-IOT-SLICE` | 5G_IoT_Slice | $499.00 base |
| `OFF-5G-ORAN-BUNDLE` | 5G O-RAN Bundle | $799.00 |
| `OFF-5G-URLLC-SLICE` | 5G_URLLC_Slice | $1,999.00 |

`demo_order_flow.sh` always selects the first offering returned by the catalog
(index 0), which is `OFF-5G-BIZ-PREMIUM`.

### Default subscriber identifiers

| Field | Value | Source |
|-------|-------|--------|
| Default IMSI | `0010102268e6` | Stage 11 evidence (BF3 test UE) |
| URLLC S-NSSAI | SST=2, SD=010203 | Stage 16 evidence, rules.yaml OFF-5G-URLLC-SLICE |
| Enterprise S-NSSAI | SST=1, SD=000001 | rules.yaml OFF-5G-BIZ-PREMIUM |
| IoT S-NSSAI | SST=3, SD=000002 | rules.yaml OFF-5G-IOT-BASIC |

The `BF3PythonAdapter` generates a random SUPI (`imsi-001010<6-hex-chars>`) for
each order unless the payload explicitly includes a `supi` field. UDM returns
404 for dynamically generated SUPIs outside its pre-seeded range, which is
expected behavior (the subscriber is still registered in UDR).

### VoNR test identity

The VoNR demo registers `alice@ims.example.com` through P-CSCF to exercise the
SIP registration flow. This identity is hardcoded in `demo_vonr_call.sh` and
the `test_vonr_call.py` driver.

---

## CI-Readiness Assessment

| Test layer | CI-ready? | Notes |
|-----------|----------|-------|
| Unit tests (pytest) | Yes | Self-contained, no live services required. Run with `pytest -v` in each service directory. |
| TMF CTK conformance | Partial | Requires the relevant FastAPI service running on its port. Can be incorporated into CI by adding a bring-up step before Newman. |
| Integration sweep | Partial | Requires the full stack. Suitable for a dedicated integration CI job. The sweep manages its own lifecycle. |
| E2E demos | Manual | VoNR requires IMS NFs started manually. O-RAN closed loop is self-managing. Order flow demo is included in the integration sweep. |
| 3GPP compliance | Partial | Requires BF3 NFs running. Can be added to CI as a post-bring-up step. |

For pure unit test CI (no services), the order_engine, catalog_api, and
ai_observer test suites are fully self-contained and can run as:

```bash
# order_engine
cd src/order_engine && venv/bin/pytest -v --tb=short

# catalog_api
cd src/catalog_api && venv/bin/pytest -v --tb=short

# ai_observer
cd src/ai_observer && venv/bin/pytest -v --tb=short
```

None of these suites make network calls to live services. All outbound HTTP is
mocked at the transport level.
