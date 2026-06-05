# Order Engine

TM Forum TMFC003 Product Order Delivery, Orchestration and Management.

**Port:** 8080
**Framework:** FastAPI (Python, async)
**Persistence:** SQLite via SQLAlchemy async (`order_engine.db`, created at startup)
**Source root:** `src/order_engine/`

---

## Purpose

The order engine is the central orchestration layer for the Tech-Co lab. It receives
customer product orders from the storefront (or any TMF622-compliant northbound caller),
decomposes them into network-function provisioning steps, executes those steps via
southbound adapters against live 5G core NFs (and stub O-RAN stubs), and tracks the
full saga lifecycle in SQLite. It exposes both the TMF622 Product Ordering and TMF641
Service Ordering APIs.

---

## Endpoints

All routes are served on port 8080.

### Health

| Method | Path    | Description              |
|--------|---------|--------------------------|
| GET    | /health | Returns `{"status":"ok"}` |
| GET    | /       | Service root with endpoint index |

### TMF622 Product Ordering (`/tmf-api/productOrderingManagement/v4`)

Defined in `app/api/tmf622.py` (line 28: `prefix="/tmf-api/productOrderingManagement/v4"`).

| Method | Path                        | Description                                              | Status codes    |
|--------|-----------------------------|----------------------------------------------------------|-----------------|
| GET    | /productOrder               | List all product orders. `?offset=` `?limit=` supported. | 200             |
| POST   | /productOrder               | Create a new order. Triggers background saga execution.  | 201             |
| GET    | /productOrder/{order_id}    | Retrieve a single product order by UUID.                 | 200, 404        |
| PATCH  | /productOrder/{order_id}    | Shallow-merge update (description, priority, category, notificationContact, note). | 200, 404 |
| DELETE | /productOrder/{order_id}    | Delete an order record. Cascades to service orders and execution steps. | 204, 404 |

### TMF641 Service Ordering (`/tmf-api/serviceOrdering/v4`)

Defined in `app/api/tmf641.py` (line 19: `prefix="/tmf-api/serviceOrdering/v4"`).

| Method | Path                        | Description                                              | Status codes    |
|--------|-----------------------------|----------------------------------------------------------|-----------------|
| GET    | /serviceOrder               | List all service orders. `?offset=` `?limit=` supported. | 200             |
| POST   | /serviceOrder               | Not implemented (returns 501). Service orders are created internally by the decomposer. | 501 |
| GET    | /serviceOrder/{order_id}    | Retrieve a single service order by UUID.                 | 200, 404        |
| DELETE | /serviceOrder/{order_id}    | Delete a service order record.                           | 204, 404        |

---

## Internal Architecture

```
src/order_engine/app/
  main.py               FastAPI app, CORS config, lifespan (init_db)
  api/
    tmf622.py           Product order routes + _execute_order background task
    tmf641.py           Service order routes (read-only; POST returns 501)
  models/
    tmf622_models.py    Pydantic: ProductOrder, ProductOrderCreate, ProductOrderItem
    tmf641_models.py    Pydantic: ServiceOrder, ServiceOrderItem, ServiceRefOrValue
    common.py           OrderStateType, OrderItemStateType, OrderItemActionType, TMFError
  state/
    order_state.py      State machine: valid transitions and next_state_from_step_results
    saga.py             Saga coordinator: SagaStep, SagaResult, SagaOutcome, run_saga()
  decomposition/
    decomposer.py       ProductOrder -> [ServiceOrder] mapping via rules.yaml
    rules.yaml          Offering-ID-to-step rules (see Decomposition section below)
  adapters/
    base.py             SouthboundAdapter ABC: activate() and rollback()
    bf3_python_adapter.py   Real adapter: calls live 5G core NFs
    o2ims_adapter.py        Stub adapter: logs and returns success (no real O2IMS call)
    o2ims_real_adapter.py   Real O2IMS adapter: calls Red Hat oran-o2ims REST API
  db/
    database.py         SQLAlchemy async engine (SQLite), AsyncSessionLocal, init_db()
    schema.py           ORM tables: ProductOrderRow, ServiceOrderRow, ExecutionStepRow
```

---

## State Machine

Defined in `app/state/order_state.py`.

```
acknowledged --> inProgress --> completed
                           --> failed
                           --> partial
                           --> cancelled
acknowledged --> cancelled
```

Terminal states (`completed`, `failed`, `partial`, `cancelled`) accept no further
transitions. The roll-up logic in `next_state_from_step_results()` maps saga step
outcomes to the parent order's terminal state:

- All steps completed -> `completed`
- All steps failed or rolled back -> `failed`
- Mixed -> `partial`

---

## The Saga Pattern

Implemented in `app/state/saga.py`. `run_saga(steps: list[SagaStep])` executes saga
steps sequentially. On any step failure it iterates previously completed steps in
reverse and calls `adapter.rollback()` on each.

`SagaStep` fields: `step_name`, `adapter` (a `SouthboundAdapter` instance), `payload`.

`SagaOutcome` fields: `success`, `results` (list of `SagaResult`), `rollback_triggered`.

Each `SagaResult` records: `step_name`, `success`, `response`, `error`, `rolled_back`.

### Rollback status per step (as of stage 24)

| Step                    | Activate          | Rollback                                              |
|-------------------------|-------------------|-------------------------------------------------------|
| `provision_subscriber`  | Real (UDR POST)   | Real via sidecar: direct SQLite DELETE on `udr.db`    |
| `allocate_slice`        | Real (NSSF + UDM) | Real: UDM POST nssai-update with `{"remove": true}`   |
| `register_with_amf`     | Real (AMF POST)   | Real: AMF POST `/amf/ue/{supi}/deregister`            |
| `establish_pdu_session` | Real (SMF POST)   | Best-effort: SMF has no DELETE endpoint; adapter logs orphaned session key and continues |

UDR rollback rationale (see `bf3_python_adapter.py` lines 160-211): UDR exposes no
DELETE endpoint. The adapter opens `udr.db` directly with `sqlite3` and executes
`DELETE FROM users WHERE imsi=?`. This is safe because UDR performs a fresh
`sqlite3.connect()` on every query. The operation is idempotent (rowcount=0 if already
absent).

SMF rollback is explicitly best-effort because `smf.py` holds session state in-memory
only and exposes no DELETE endpoint. The adapter calls `GET /smf/sessions` to confirm
whether the session key is still active, logs the result for operator awareness, and
completes without raising an error. Stale sessions are cleaned up when the SMF restarts.

---

## Decomposition

`app/decomposition/decomposer.py` reads `app/decomposition/rules.yaml` to map each
`ProductOrderItem`'s offering ID substring to a list of service steps. One `ServiceOrder`
is created per `ProductOrderItem`, containing one `ServiceOrderItem` per step.

### Offering patterns in rules.yaml

| Offering ID substring  | Service category   | Steps (in order)                                                                 |
|------------------------|--------------------|---------------------------------------------------------------------------------|
| `OFF-5G-BIZ-PREMIUM`   | 5G_Enterprise      | allocate_slice (o2ims stub), provision_subscriber (bf3_python)                  |
| `OFF-5G-IOT-BASIC`     | 5G_IoT             | allocate_slice (o2ims stub), provision_subscriber (bf3_python)                  |
| `OFF-5G-URLLC-LATENCY` | 5G_URLLC           | allocate_slice (o2ims stub), configure_ran (o2ims stub), provision_subscriber (bf3_python) |
| `OFF-5G-ORAN-BUNDLE`   | 5G_ORAN_Edge       | allocate_o_cloud_resource (o2ims_real), provision_subscriber (bf3_python), register_with_amf (bf3_python) |
| `OFF-5G-URLLC-SLICE`   | 5G_URLLC           | allocate_slice (bf3_python), provision_subscriber (bf3_python), register_with_amf (bf3_python), establish_pdu_session (bf3_python) |
| `DEFAULT`              | GenericService     | provision_subscriber (bf3_python)                                               |

Each step's `payload_extra` fields are merged into the `ServiceOrderItem.serviceCharacteristic`
list and passed through to `adapter.activate()`.

---

## Adapter Routing

`_resolve_adapter_for_step()` in `app/api/tmf622.py` (lines 134-149) determines which
adapter handles each step. Priority:

1. Checks `serviceCharacteristic` for a characteristic named `_adapter`. If found and
   the value is a registered adapter key, that adapter is used. This is set by
   `payload_extra._adapter` in `rules.yaml`.
2. Falls back to step-name heuristics: if `"slice"` or `"ran"` appears in the step
   name, uses `o2ims`; otherwise uses `bf3_python`.

The adapter registry (`_ADAPTERS` dict, `tmf622.py` lines 34-38):

| Key           | Class                | Real or stub |
|---------------|----------------------|--------------|
| `bf3_python`  | `BF3PythonAdapter`   | Real         |
| `o2ims`       | `O2IMSAdapter`       | Stub         |
| `o2ims_real`  | `O2IMSRealAdapter`   | Real         |

---

## Adapters in Detail

### BF3PythonAdapter (`app/adapters/bf3_python_adapter.py`)

Real adapter. Calls live 5G core NFs for four steps:

- **provision_subscriber**: UDR `POST /register_user` then UDM `GET /nudm-sdm/v1/{supi}/am-data`
- **allocate_slice**: NSSF `GET /nnssf-nsselection/v1/network-slice-information` then UDM `POST /nudm-sdm/v1/{supi}/am-data/nssai-update`
- **register_with_amf**: AMF `POST /amf/ue/{supi}` then verify with `GET /amf/ue/{supi}`
- **establish_pdu_session**: SMF `POST /nsmf-pdusession/v1/sm-contexts`

Unknown step names return a stub success dict with a warning log.

### O2IMSAdapter (`app/adapters/o2ims_adapter.py`)

Stub. Logs the intended call and returns `{"status": "success", "adapter": "o2ims"}`.
Replace the body of `activate()` with real O2IMS REST calls when the O-RAN stack is present.

### O2IMSRealAdapter (`app/adapters/o2ims_real_adapter.py`)

Real. Calls the Red Hat oran-o2ims REST API with 3-attempt exponential retry (1s, 2s, 4s).
4xx errors are not retried. Handles four steps:

- `allocate_o_cloud_resource`: `POST /o2ims-infrastructureProvisioning/v1/provisioningRequests`
- `query_deployment_managers`: `GET /o2ims-infrastructureInventory/v1/deploymentManagers`
- `query_resource_pools`: `GET /o2ims-infrastructureInventory/v1/resourcePools`
- `query_resources`: `GET /o2ims-infrastructureInventory/v1/resourcePools/{id}/resources`

Rollback for `allocate_o_cloud_resource` calls `DELETE /o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}`. 404 on rollback is treated as idempotent success.

---

## Database Schema

Defined in `app/db/schema.py`. SQLite file: `order_engine.db` (created at startup in
the working directory where uvicorn is launched).

| Table             | Key columns                                                                            |
|-------------------|----------------------------------------------------------------------------------------|
| `product_orders`  | id (PK), external_id, state, order_date, completion_date, description, category, priority, payload (JSON) |
| `service_orders`  | id (PK), product_order_id (FK), state, order_date, completion_date, description, payload (JSON) |
| `execution_steps` | id (PK), product_order_id (FK), service_order_id, step_name, adapter_name, sequence, state, result_payload (JSON), created_at, completed_at |

All three tables cascade delete from `product_orders`.

---

## Tests

**43/43 pytest pass** (stage 24). Run from `src/order_engine/`:

```bash
cd src/order_engine
source .venv/bin/activate
pytest
```

**TMF622 CTK conformance: 100% (63/63 assertions)** per stage 13.

---

## Environment Variables

| Variable                  | Default                                          | Description                                      |
|---------------------------|--------------------------------------------------|--------------------------------------------------|
| `BF3_UDR_URL`             | `http://localhost:9005`                          | UDR base URL                                     |
| `BF3_UDM_URL`             | `http://localhost:9004`                          | UDM base URL                                     |
| `BF3_AMF_URL`             | `http://localhost:9000`                          | AMF base URL                                     |
| `BF3_SMF_URL`             | `http://localhost:9001`                          | SMF base URL                                     |
| `BF3_NSSF_URL`            | `http://localhost:9010`                          | NSSF base URL                                    |
| `BF3_UDR_DB_PATH`         | `<Tech-Co root>/udr.db`                          | Path to UDR SQLite file for sidecar rollback     |
| `O2IMS_BASE_URL`          | `http://localhost:8083`                          | O2IMS API base URL (O2IMSRealAdapter)            |
| `O2IMS_TOKEN`             | (empty)                                          | Bearer token for O2IMS auth (optional)           |
| `ORDER_ENGINE_CORS_ORIGINS` | `http://localhost:8095,http://127.0.0.1:8095`  | Comma-separated allowed CORS origins             |

---

## Running Standalone

```bash
cd src/order_engine
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --port 8080 --reload
```

Interactive docs: http://localhost:8080/docs

---

## How to Add a New Adapter

1. Create `app/adapters/my_adapter.py` implementing `SouthboundAdapter`:

   ```python
   from app.adapters.base import SouthboundAdapter

   class MyAdapter(SouthboundAdapter):
       async def activate(self, step_name: str, payload: dict) -> dict:
           ...
       async def rollback(self, step_name: str, payload: dict) -> None:
           ...
   ```

2. Register it in `app/api/tmf622.py` by adding an entry to `_ADAPTERS`:

   ```python
   _ADAPTERS = {
       "bf3_python": BF3PythonAdapter(),
       "o2ims": O2IMSAdapter(),
       "o2ims_real": O2IMSRealAdapter(),
       "my_adapter": MyAdapter(),   # add this
   }
   ```

3. Reference it in `app/decomposition/rules.yaml` by setting `adapter: my_adapter`
   on the relevant step, and optionally `_adapter: my_adapter` in `payload_extra`
   to force routing via the explicit characteristic lookup path.
