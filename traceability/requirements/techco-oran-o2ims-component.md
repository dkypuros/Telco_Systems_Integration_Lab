# O-RAN O2IMS Component Reference

**Spec**: O-RAN O2 Interface (O-Cloud Infrastructure Management Services)
**Implementation**: Red Hat oran-o2ims (Go)
**Source**: `external/oran_o2ims/` (read-only clone)
**Adapter**: `src/order_engine/app/adapters/o2ims_real_adapter.py`
**Tests**: `src/order_engine/tests/test_o2ims_real_adapter.py` (16 tests, all pass)

---

## Source Location

```
Tech-Co/external/oran_o2ims/
  main.go
  api/
  internal/
  pkg/
  hwmgr-plugins/
  config/
  docs/                  <-- canonical API docs and user guides
  Makefile
  go.mod
  go.sum
  Dockerfile
  bundle/
  bundle.Dockerfile
  catalog.Dockerfile
  dev-tools/
  hack/
```

The upstream repo is the Red Hat `oran-o2ims` project. This directory is a read-only copy.
Canonical user documentation lives inside `external/oran_o2ims/docs/` (user-guide/,
cluster-provisioning.md, inventory-api.md). Consult those docs for the authoritative API
reference.

Parallel clone (future/alternate):
`9.LABS_pure_os_stack/source_code/3_future/49_oran-o2ims/`

---

## Build

**Go version**: go1.25.5 darwin/arm64 (stage 8)
**Build command**: `go build ./...` (downloads dependencies from Go module proxy)
**Named binary**: `go build -o /tmp/oran-o2ims-binary .`

```bash
cd Tech-Co/external/oran_o2ims
go build ./...
go build -o /tmp/oran-o2ims-binary .
```

**Result (stage 8)**: exit code 0, binary produced at `/tmp/oran-o2ims-binary`
**Binary size**: 115 MB (stage 25 confirmed: `-rwxr-xr-x`, Mach-O arm64)

**Note on Makefile targets**: `make build` requires `controller-gen`, `gofmt`, `go vet`, and
a `telco5g-konflux` git submodule not present in this single-directory copy. `make binary`
requires a `vendor/` directory also absent. Direct `go build` bypasses those prerequisites
and succeeds with network access to the Go module proxy.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `O2IMS_BASE_URL` | `http://localhost:8083` | Base URL of the O2IMS API server |
| `O2IMS_TOKEN` | (empty) | Bearer token for O2IMS auth (optional; sent as `Authorization: Bearer` if set) |

The adapter reads both variables at call time via `os.environ.get()` (o2ims_real_adapter.py
lines 69-77). Changes take effect without restart.

---

## Endpoint Mapping Table

Endpoints are drawn from `external/oran_o2ims/docs/` (inventory-api.md and
cluster-provisioning.md) and confirmed in stage 8.

### Inventory / Resource Server

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/o2ims-infrastructureInventory/v1/` | O-Cloud info and health check |
| GET | `/o2ims-infrastructureInventory/v1/api_versions` | Supported API versions |
| GET | `/o2ims-infrastructureInventory/v1/deploymentManagers` | List deployment managers (spoke clusters) |
| GET | `/o2ims-infrastructureInventory/v1/deploymentManagers/{id}` | Get deployment manager by ID |
| GET | `/o2ims-infrastructureInventory/v1/resourcePools` | List resource pools |
| GET | `/o2ims-infrastructureInventory/v1/resourcePools/{id}/resources` | Resources within a pool |
| GET | `/o2ims-infrastructureInventory/v1/resourceTypes` | Resource type catalog |
| GET | `/o2ims-infrastructureInventory/v1/subscriptions` | Inventory change subscriptions |
| POST | `/o2ims-infrastructureInventory/v1/subscriptions` | Subscribe to inventory events |

### Provisioning Server

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/o2ims-infrastructureProvisioning/v1/provisioningRequests` | Create provisioning request |
| GET | `/o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}` | Poll provisioning status |
| DELETE | `/o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}` | Cancel / rollback provisioning |

---

## Python Adapter

**File**: `src/order_engine/app/adapters/o2ims_real_adapter.py`
**Interface**: implements `SouthboundAdapter` from `src/order_engine/app/adapters/base.py`
**HTTP client**: `httpx.AsyncClient` (async, consistent with rest of order engine)
**Retry policy**: up to 3 attempts; waits of 1 s, 2 s, 4 s for 5xx and network errors;
4xx errors not retried (client errors, not transient)

### Step-to-Endpoint Mapping

| Order engine step | O2IMS call | Method | Notes |
|-------------------|-----------|--------|-------|
| `allocate_o_cloud_resource` | `/o2ims-infrastructureProvisioning/v1/provisioningRequests` | POST | Body: `spec.{name, description, templateName, templateVersion, templateParameters}`. Stores PR ID in `payload["_o2ims_pr_id"]` for rollback reference. |
| `allocate_o_cloud_resource` (rollback) | `/o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}` | DELETE | 404 treated as idempotent success (already gone). |
| `query_deployment_managers` | `/o2ims-infrastructureInventory/v1/deploymentManagers` | GET | Returns list of spoke clusters registered with ACM hub. |
| `query_resource_pools` | `/o2ims-infrastructureInventory/v1/resourcePools` | GET | Returns list of resource pools. |
| `query_resources` | `/o2ims-infrastructureInventory/v1/resourcePools/{resource_pool_id}/resources` | GET | Requires `payload["resource_pool_id"]`. |

Step constants (o2ims_real_adapter.py lines 59-62):
- `_STEP_ALLOCATE = "allocate_o_cloud_resource"`
- `_STEP_QUERY_DM = "query_deployment_managers"`
- `_STEP_QUERY_POOLS = "query_resource_pools"`
- `_STEP_QUERY_RESOURCES = "query_resources"`

Unknown step names return a no-op result dict without raising.

### Key Methods

```
O2IMSRealAdapter.activate(step_name, payload)   -- dispatches to one of four private methods
O2IMSRealAdapter.rollback(step_name, payload)   -- DELETE provisioningRequests/{id} on allocate; noop otherwise
_create_provisioning_request(payload)           -- builds body, POSTs, stores PR ID
_query_deployment_managers(payload)             -- GET deploymentManagers
_query_resource_pools(payload)                  -- GET resourcePools
_query_resources(payload)                       -- GET resourcePools/{id}/resources
_request_with_retry(client, method, url, ...)   -- retry wrapper with 5xx backoff
_base_url()                                     -- reads O2IMS_BASE_URL env var
_auth_headers()                                 -- reads O2IMS_TOKEN env var
```

---

## Tests

**Test file**: `src/order_engine/tests/test_o2ims_real_adapter.py`
**Test count**: 16 (all pass; zero regressions against 18 pre-existing tests)
**Framework**: pytest-asyncio with mocked httpx (no live O2IMS required)

| Test | What it verifies |
|------|-----------------|
| `test_activate_allocate_posts_to_provisioning_endpoint` | Correct URL used for POST |
| `test_activate_allocate_request_body_shape` | Request body contains expected spec fields |
| `test_activate_allocate_stores_pr_id_in_payload` | PR ID stored in payload for rollback |
| `test_activate_query_deployment_managers` | GET deploymentManagers URL correct |
| `test_activate_query_resource_pools` | GET resourcePools URL correct |
| `test_activate_query_resources` | GET resourcePools/{id}/resources URL correct |
| `test_activate_query_resources_missing_pool_id_raises` | Missing pool ID raises ValueError |
| `test_activate_unknown_step_returns_noop` | Unknown step name returns noop, no HTTP call |
| `test_retry_succeeds_on_third_attempt` | 5xx on attempts 1+2, success on attempt 3 |
| `test_retry_exhaustion_raises_runtime_error` | 3x 5xx raises RuntimeError |
| `test_rollback_sends_delete_for_pr_id` | DELETE sent to correct URL with stored PR ID |
| `test_rollback_idempotent_on_404` | 404 on DELETE treated as success (no raise) |
| `test_rollback_noop_for_query_steps` | Rollback is no-op for query steps |
| `test_rollback_without_pr_id_is_safe` | Missing `_o2ims_pr_id` in payload does not raise |
| `test_bearer_token_sent_when_env_set` | `Authorization: Bearer {token}` header present |
| `test_no_auth_header_when_token_absent` | No Authorization header when env var absent |

Run tests:

```bash
cd Tech-Co/src/order_engine
python -m pytest tests/test_o2ims_real_adapter.py -v
```

---

## Status

**Binary**: builds (`go build ./...` exits 0, produces 115 MB Mach-O arm64 binary).

**Adapter**: tested via mocked HTTP (all 16 tests pass). No live O2IMS server required for
unit tests.

**Live O2IMS**: skipped in stage 25 (closed-loop demo). The binary was started
(`pid 5747`), but `GET /o2ims-infrastructureInventory/v1/` on port 8083 returned no response
after 4 seconds. The binary requires a kubeconfig or ACM hub cluster connection to serve
requests. It was killed and the bonus section was skipped. This is expected and documented
behavior from stage 8.

The A1-to-E2 closed-loop demo (`scripts/demo_oran_closed_loop.sh`) does not depend on O2IMS.
O2IMS is purely an additive integration for cluster provisioning scenarios.

---

## How to Run in Dev Mode

For the canonical operator deployment and API documentation, read the docs inside the source:

```
Tech-Co/external/oran_o2ims/docs/
```

For local development without a cluster, use `oc port-forward` to expose the in-cluster
O2IMS service:

```bash
oc port-forward svc/resource-server 8083:8000 -n oran-o2ims
export O2IMS_BASE_URL=http://localhost:8083
export O2IMS_TOKEN=$(oc whoami --show-token)
```

To deploy the operator onto an OpenShift hub with ACM, follow
`external/oran_o2ims/docs/user-guide/` and run `make deploy` (requires `oc`, `kustomize`,
and a kubeconfig pointing at the hub cluster).

Prerequisites for a working live integration:
1. Running O2IMS operator on an OpenShift hub cluster with ACM
2. `O2IMS_BASE_URL` set to the cluster ingress route
3. `O2IMS_TOKEN` set to a valid OAuth2/OIDC bearer token
4. Spoke clusters registered with ACM (for `deploymentManagers` to return real data)
5. ClusterTemplates pre-created on the hub (for `allocate_o_cloud_resource` to reference a
   valid `templateName`/`templateVersion`)
6. Hardware visible to the hub (Metal3 / BareMetalHosts) for provisioning to proceed past
   `HardwareProvisioned` stage
7. TLS CA bundle if the O2IMS ingress uses a non-public CA

---

## Cross-References

- RAN components (Near-RT RIC, Non-RT RIC, CU, DU, gNB): `docs/components/ran.md`
- 5G core NFs: `docs/components/5g_core.md`
- legacy standalone 5G emulator Python adapter (5G core southbound): `src/order_engine/app/adapters/legacy_5g_emulator_python_adapter.py`
- Original O2IMS stub (untouched): `src/order_engine/app/adapters/o2ims_adapter.py`
- Order decomposition rules: `src/order_engine/app/decomposition/rules.yaml`
- Stage 8 build log: `build_logs/stage8_o2ims.md`
- Stage 25 run capture: `build_logs/stage25_oran_run_capture.md`
