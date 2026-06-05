# Stage 8: O2IMS Integration Build Log

Date: 2026-05-18
Go version: go1.25.5 darwin/arm64
Python: 3.14.4

---

## Part 1: Go Build

**Attempted:** yes

**Succeeded:** yes

**Method:**
- `go build ./...` -- compiles all packages, downloads all dependencies, exit code 0
- `go build -o /tmp/oran-o2ims-binary .` -- produces named binary, exit code 0

**Binary location:** `/tmp/oran-o2ims-binary` (110 MB, darwin/arm64)

Note: The Makefile `build` target requires controller-gen, gofmt, and go vet as
prerequisites and depends on a git submodule (`telco5g-konflux`) that is not
present in this single-directory copy.  Direct `go build` bypasses those
prerequisites and succeeds because all module dependencies are fetched from
the Go module proxy.  The `make binary` target (`go build -o bin/oran-o2ims
-mod=vendor`) would require a vendor directory, which is also absent.

**Build error:** none (direct `go build` path)

**Known limitation:** vendored dependencies are not present. Running the full
`make build` or `make binary` flow requires either `go mod vendor` or network
access to the Go module proxy. Network access was available and `go build`
succeeded by downloading from the proxy.

---

## Part 2: Python Southbound Adapter

**Adapter file created:**
`Tech-Co/src/order_engine/app/adapters/o2ims_real_adapter.py`

**Test file created:**
`Tech-Co/src/order_engine/tests/test_o2ims_real_adapter.py`

**Existing stub left untouched:**
`Tech-Co/src/order_engine/app/adapters/o2ims_adapter.py` -- not modified

### What the adapter does

- Implements `SouthboundAdapter` (from `app/adapters/base.py`) with `activate()`
  and `rollback()` async methods.
- Uses `httpx.AsyncClient` (async) consistent with the rest of the order engine.
- Reads `O2IMS_BASE_URL` (default `http://localhost:8083`) and optional
  `O2IMS_TOKEN` for Bearer auth from environment variables.
- Retries up to 3 attempts with 1 / 2 / 4 second waits for 5xx and network
  errors. 4xx errors are not retried (they are client errors, not transient).
- Logs every call at INFO level (warnings on failure).
- `rollback()` is idempotent: a 404 on DELETE is treated as already-gone and
  does not raise.

### Test results

```
34 passed in 0.52s (16 new + 18 pre-existing)
```

All 18 pre-existing tests continue to pass (zero regressions).
All 16 new tests for O2IMSRealAdapter pass.

---

## O2IMS Endpoint Mapping Table

| Order engine step              | O2IMS API call                                                                        | HTTP method | Notes                                                                 |
|-------------------------------|--------------------------------------------------------------------------------------|-------------|-----------------------------------------------------------------------|
| allocate_o_cloud_resource      | /o2ims-infrastructureProvisioning/v1/provisioningRequests                            | POST        | Body: spec.{name, description, templateName, templateVersion, templateParameters}. Stores PR id in payload["_o2ims_pr_id"] for rollback. |
| allocate_o_cloud_resource (rb) | /o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}                       | DELETE      | Rollback path. 404 treated as idempotent success.                    |
| query_deployment_managers      | /o2ims-infrastructureInventory/v1/deploymentManagers                                 | GET         | Returns list of deployment managers (spoke clusters).                 |
| query_resource_pools           | /o2ims-infrastructureInventory/v1/resourcePools                                      | GET         | Returns list of resource pools.                                       |
| query_resources                | /o2ims-infrastructureInventory/v1/resourcePools/{resource_pool_id}/resources         | GET         | Requires payload["resource_pool_id"].                                 |

Additional O2IMS endpoints documented but not yet mapped to order steps:

| Endpoint                                                              | Purpose                         |
|----------------------------------------------------------------------|---------------------------------|
| GET /o2ims-infrastructureInventory/v1/                               | O-Cloud info / health check     |
| GET /o2ims-infrastructureInventory/v1/api_versions                   | Supported API versions          |
| GET /o2ims-infrastructureInventory/v1/resourceTypes                  | Resource type catalog           |
| GET /o2ims-infrastructureInventory/v1/subscriptions                  | Inventory change subscriptions  |
| POST /o2ims-infrastructureInventory/v1/subscriptions                 | Subscribe to inventory events   |
| GET /o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}   | Poll provisioning status        |

---

## What is needed to make it work for real

1. **Running O2IMS operator** on an OpenShift hub cluster with ACM.
   Deploy via `make deploy` (requires oc, kustomize, and a kubeconfig pointing
   at the hub).

2. **O2IMS_BASE_URL** set to the cluster ingress route, e.g.:
   `https://o2ims.apps.<cluster-domain>`

3. **O2IMS_TOKEN** set to a valid bearer token from the cluster OAuth server.
   The operator expects OpenID Connect / OAuth2 tokens.

4. **Spoke clusters registered with ACM** so the deployment manager server
   can return real cluster data.

5. **ClusterTemplates** pre-created on the hub so `allocate_o_cloud_resource`
   can reference a valid `templateName` / `templateVersion`. Without a matching
   ClusterTemplate the ProvisioningRequest will be rejected by the webhook.

6. **Hardware (Metal3 / BareMetalHosts)** visible to the hub for the provisioning
   flow to proceed past the `HardwareProvisioned` stage.

7. **Network connectivity** from the order engine container to the O2IMS ingress
   (or a port-forward for local development: `oc port-forward svc/resource-server
   8083:8000 -n oran-o2ims`).

8. **TLS CA bundle** if the O2IMS ingress uses a non-public CA. Pass via
   `httpx.AsyncClient(verify=...)` or mount the CA into the container.

---

## File inventory

| File                                                                              | Role                          |
|-----------------------------------------------------------------------------------|-------------------------------|
| Tech-Co/external/oran_o2ims/                                                      | Red Hat O2IMS Go source (RO)  |
| Tech-Co/src/order_engine/app/adapters/o2ims_adapter.py                           | Original stub (untouched)     |
| Tech-Co/src/order_engine/app/adapters/o2ims_real_adapter.py                      | New real adapter (created)    |
| Tech-Co/src/order_engine/tests/test_o2ims_real_adapter.py                        | Unit tests (created)          |
| Tech-Co/build_logs/stage8_o2ims.md                                                | This log                      |
