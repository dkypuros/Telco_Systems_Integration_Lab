# TM Forum Components

TM Forum evidence is currently represented as copied requirements, CTK snapshots, and
planned service buckets for catalog/order/service API work.

## Repo areas

| Area | Purpose |
|---|---|
| [`adapters/tmforum/`](../adapters/tmforum/) | Future TM Forum API/client adapters. |
| [`services/catalog_api/`](../services/catalog_api/) | Future catalog API implementation bucket. |
| [`services/order_engine/`](../services/order_engine/) | Future order engine implementation bucket. |
| [`traceability/evidence_snapshots/`](../traceability/evidence_snapshots/) | CTK/result snapshots and copied evidence. |
| [`traceability/requirements/`](../traceability/requirements/) | Requirements/reference material copied from source workspaces. |

## Current evidence

| API/evidence | Current baseline note | Evidence path |
|---|---|---|
| TMF620 Product Catalog | Local evidence references a v4 CTK baseline; release register tracks v5 target/gap separately. | [`traceability/evidence_snapshots/tmf620-v4-ctk-jsonResults.json`](../traceability/evidence_snapshots/tmf620-v4-ctk-jsonResults.json) |
| TMF622 Product Ordering | Local evidence references a v4 CTK baseline; release register tracks v5 target/gap separately. | [`traceability/evidence_snapshots/tmf622-v4-ctk-jsonResults.json`](../traceability/evidence_snapshots/tmf622-v4-ctk-jsonResults.json) |
| TMF638 / TMF641 | Multiple copied CTK/environment/collection artifacts exist and need asset-version-specific interpretation. | [`traceability/evidence_snapshots/`](../traceability/evidence_snapshots/) |
| TM Forum guide docs | Copied requirements/reference material. | [`traceability/requirements/tmf-specs-guide.md`](../traceability/requirements/tmf-specs-guide.md) |

## Promotion path

Before claiming conformance for a TM Forum API:

1. identify the API spec version,
2. identify the CTK/RI asset version,
3. run or preserve the executable CTK evidence,
4. link the implementation path,
5. update the release register with local tested-against and gap state,
6. record the conformance level.

Do not infer v5 conformance from v4 CTK evidence.
