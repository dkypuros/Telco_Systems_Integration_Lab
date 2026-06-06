# ROF Loop: Product Front Door to Network Activation

Date: 2026-06-06

This ROF loop captures the current boundary-aware path toward the repository's
north-star intent: a front door where a customer or operator can select or build
a product, submit it through a TM Forum-style order flow, and see how far the lab
can carry that intent toward services, 3GPP core behavior, O-RAN, O-Cloud, and
evidence.

ROF here means:

1. **Reality** — what the repository can honestly support today.
2. **Options** — what we could build next without violating claim boundaries.
3. **Forward path** — the recommended first implementation slice.

## Boundary conditions

The next step must preserve these boundaries:

- It must not claim formal TM Forum, 3GPP, O-RAN, ODA, O-Cloud, OCP, or Kubernetes conformance.
- It must use the existing single-product MVP first: `prod-5g-data-basic`.
- It must show unsupported downstream layers as explicit gaps, not as fake success.
- It must keep modules local-only and registered in `modules/index.json` before use.
- It must avoid arbitrary shell execution from browser controls.
- It must not vendor external telco projects or raw upstream repositories.
- It should prefer the Python standard library and existing repo services before adding dependencies.
- It must keep `correlation_id`, `product_id`, `order_id`, and `service_id` visible across the flow.

## Reality: current pyramid strength

| Layer | Current state | Evidence paths | Readiness |
| --- | --- | --- | --- |
| Standards / traceability | TMF, 3GPP, and O-RAN references are inventoried with explicit release/gap language. | `traceability/standards_release_register.yaml`, `docs/tmforum-components.md`, `docs/standards-mapping.md` | Strong for navigation; not conformance proof. |
| Product model | One TMF620-referenced product fixture exists. | `models/standard_native/tmf/product_catalog/basic_5g_data_service.json`, `services/catalog_api/` | Enough for first storefront product. |
| Product order | A TMF622/TMF641-referenced order lifecycle creates an activation plan. | `services/order_engine/` | Enough for first order demo. |
| Orchestration | A lab-owned orchestration graph maps activation plans to subscriber/session intent. | `services/orchestration/` | Enough for first intent handoff. |
| 3GPP mock adapter | A controlled local adapter records mock subscriber/session activation. | `adapters/3gpp/mock_core_activation_adapter.py` | Enough for functional smoke, not protocol conformance. |
| Evidence | A repeatable integration test and demo evidence bundle exist. | `tests/integration/test_service_order_to_activation_evidence.py`, `traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json` | Enough to support a visible MVP timeline. |
| Module ecosystem | Dashboard, lab runtime, UE scenario generator, and chatter modules are registered and working. | `modules/`, `docs/modules.md` | Enough to add a product front-door module. |
| O-RAN descent | Mock O-RAN/RAN services and scenario chatter exist, but the order flow does not drive them. | `adapters/mock_oran/`, `adapters/mock_ran/`, `./lab scenario ...` | Partial; must display as gap for this slice. |
| O-Cloud / ODA / OCP descent | Architecture intent exists, but no executable order-to-O-Cloud path exists. | release/register and planning docs | Planned only; must display as gap. |
| Storefront/front door | No browser product-builder module exists yet. | n/a | Missing; best next build. |

## Options

### Option A — TMF Evidence Explorer module

Build a viewer that lists TMF APIs, CTK snapshots, release-register rows,
implementation paths, evidence paths, and gaps.

**Pros**

- Very safe.
- Strengthens the pyramid viewer idea.
- Helps avoid overclaiming before more UI is built.

**Cons**

- Does not yet give the customer/operator purchase experience.
- Less emotionally close to the north-star front door.

### Option B — Product Front Door module

Build a local module where a user can view the basic 5G data product, click a
bounded **Activate Demo Product** action, and see a correlated timeline:

```text
product found
order created
activation plan generated
orchestration mapped
mock core adapter activated
evidence bundle path linked
O-RAN / O-Cloud gaps shown honestly
```

**Pros**

- Directly serves the north-star intent.
- Reuses the existing implemented spine.
- Creates a visible product-to-activation demo without new standards claims.

**Cons**

- It can only honestly reach the current mock-core adapter.
- It must be clear that O-RAN/O-Cloud are not yet connected.

### Option C — Full backend HTTP chain first

Expose and run every service over HTTP before building the front door.

**Pros**

- Closer to production-style decomposition.
- Useful later for API-level module composition.

**Cons**

- More moving parts before the first visual front door.
- Higher risk of building infrastructure before validating the user story.

## Completed first implementation

The first implementation is complete:

- module id: `product-front-door`
- port: `8767`
- entrypoint: `python3 modules/product_front_door/server.py`
- scope: fixed activation path for `prod-5g-data-basic`
- evidence boundary: local MVP demo only; O-RAN/O-Cloud/ODA/OCP remain planned gaps

## Next downstream recommendation

Build the **Service Inventory / Activation Bridge** before O-RAN or O-Cloud
fulfillment. The Product Front Door can now create an order and run mock
activation, but a downstream domain still needs a service instance and service
state boundary to attach to.

Planning artifacts:

- [Service Inventory / Activation Bridge Plan](service-inventory-activation-bridge-plan.md)
- [PRD](../.omx/plans/prd-service-inventory-activation-bridge.md)
- [Test spec](../.omx/plans/test-spec-service-inventory-activation-bridge.md)

## Historical first implementation recommendation

Build **Option B: Product Front Door module** first, then follow with a service
inventory / activation bridge and a TMF Evidence Explorer companion.

The first product front door should be intentionally narrow:

- module id: `product-front-door`
- suggested port: `8767`
- entrypoint: `python3 modules/product_front_door/server.py`
- depends on: no hard runtime dependency for the MVP execution path;
- recommended with: `modules-dashboard`, `lab-chatter-service`, `ue-scenario-generator`;
- product: `prod-5g-data-basic` only;
- action: fixed local function call path through existing catalog/order/orchestration/adapter code;
- output: an HTML timeline plus JSON payload for the correlated MVP run.

The page should explicitly separate:

- **proven for this MVP** — catalog lookup, order lifecycle, activation plan,
  orchestration mapping, mock-core activation, evidence bundle path;
- **partial / adjacent** — lab chatter and UE scenario generation;
- **planned only** — TMF CTK conformance, real service inventory, O-RAN control,
  SMO/O2, O-Cloud/OCP/ODA Canvas, bare metal remediation.

## Historical stop condition for the first implementation

The first implementation was considered complete when:

1. the dashboard shows a Product Front Door card;
2. the module opens at its registered localhost port;
3. the page shows the basic product and a fixed activation action;
4. clicking the action produces `correlation_id`, `product_id`, `order_id`,
   `service_id`, and `mock_activation_result`;
5. the timeline marks O-RAN/O-Cloud as planned gaps;
6. tests prove the module cannot execute arbitrary commands;
7. docs preserve the claim boundary.

## Historical first issue shape

Title:

```text
Build a Product Front Door module for the basic 5G data MVP
```

Scope:

- `modules/product_front_door/`
- `modules/index.json`
- `tests/unit/test_product_front_door_module.py`
- small README/doc updates only where needed

Out of scope:

- new dependencies;
- formal TM Forum CTK execution;
- O-RAN/O-Cloud implementation;
- multi-product catalog builder;
- authenticated commerce flow;
- production service discovery.
