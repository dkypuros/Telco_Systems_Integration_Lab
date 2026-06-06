# PRD: Service Inventory / Activation Bridge

## Objective

Add the next downstream layer after Product Front Door: a bounded, lab-owned
service inventory and service activation bridge that turns the current activation
plan into a visible service instance record before any O-RAN or O-Cloud work is
claimed.

## Decision

Build the **TMF service inventory / activation bridge** next.

This is the highest-leverage next gap because the current front door can create
an order and mock activation result, but it cannot yet show a service instance as
a durable object that downstream O-RAN, O-Cloud, ODA, OCP, Kubernetes, or bare
metal remediation steps can attach to.

## Current baseline

The repository already has:

- product front door module: `modules/product_front_door/`
- basic product fixture: `prod-5g-data-basic`
- catalog lookup: `services/catalog_api/`
- product order lifecycle: `services/order_engine/`
- orchestration mapping: `services/orchestration/`
- mock 3GPP adapter: `adapters/3gpp/mock_core_activation_adapter.py`
- demo evidence bundle: `traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json`

The current Product Front Door timeline correctly marks service inventory as a
planned gap.

## User story

As an operator or reviewer, I want the Product Front Door activation to create or
show a service instance record so I can see the boundary between commercial order
state and downstream network/domain fulfillment.

## Scope

Implement a narrow, local, functional-smoke service bridge:

1. Add a callable service inventory/activation facade under `services/service_inventory/` or another clearly named service bucket.
2. Create a public-safe service instance record from the existing activation plan.
3. Track state transitions such as:
   - `service_order_received`
   - `service_instance_reserved`
   - `activation_requested`
   - `mock_core_activation_recorded`
   - `downstream_domain_pending`
4. Preserve identifiers:
   - `correlation_id`
   - `product_id`
   - `order_id`
   - `service_id`
   - `customer_id`
5. Add TMF638/TMF640-referenced metadata without claiming formal conformance.
6. Update Product Front Door so the service inventory step can move from
   `planned_gap` to `complete` when this bridge is present.
7. Keep O-RAN/O-Cloud/ODA/OCP/Kubernetes as planned downstream gaps.
8. Add evidence/test coverage proving the bridge is repeatable and public-safe.

## Non-goals

- No formal TM Forum CTK result.
- No full TMF638/TMF640 implementation claim.
- No persistent production database.
- No authenticated customer workflow.
- No O-RAN, SMO, O2, O-Cloud, OCP, Kubernetes, or bare-metal execution.
- No new dependencies.
- No external upstream project import.

## Recommended shape

### Backend/callable service

Suggested path:

```text
services/service_inventory/
├── README.md
├── __init__.py
├── service_inventory.py
└── api.py          # optional FastAPI wrapper only if existing API pattern warrants it
```

The callable service should accept the activation plan and adapter response, then
return:

```json
{
  "ok": true,
  "correlation_id": "...",
  "service_id": "...",
  "order_id": "...",
  "product_id": "prod-5g-data-basic",
  "service_state": "downstream_domain_pending",
  "state_history": [...],
  "standards_reference": {
    "standards_body": "TM Forum",
    "service_inventory_spec_id": "TMF638",
    "service_activation_spec_id": "TMF640",
    "evidence_label": "functional_smoke"
  },
  "claim_boundary": "...not formal TM Forum conformance..."
}
```

### Product Front Door integration

Update `modules/product_front_door/server.py` so its fixed activation path calls
the service inventory bridge after orchestration/adapter activation.

Timeline behavior should become:

```text
Product found                         complete
Order created                         complete
Activation plan generated             complete
Service instance recorded             complete
Orchestration mapped                  complete
Mock core adapter activated           complete
Evidence bundle linked                complete
O-RAN / SMO downstream action          planned_gap
O-Cloud / ODA / OCP / Kubernetes       planned_gap
```

### Optional module

A separate visual module can come later. Do not build it first unless the service
record exists. If built, suggested future module:

```text
modules/service_inventory_viewer/   # suggested port 8768
```

## Acceptance criteria

- A service inventory/activation bridge creates a service instance record from
  the existing activation plan.
- The record preserves `correlation_id`, `product_id`, `order_id`, and `service_id`.
- The record includes TMF638/TMF640 references and explicit claim boundaries.
- Product Front Door no longer marks service inventory as a planned gap once the
  bridge is integrated.
- O-RAN/O-Cloud/ODA/OCP/Kubernetes remain planned gaps.
- Tests prove unknown/invalid activation plans are rejected.
- Tests prove no private paths or conformance overclaims appear in payloads.
- No new dependencies are introduced.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Accidentally implying TMF638/TMF640 conformance | Use `functional_smoke` evidence labels and explicit claim boundary in service, module, docs, and tests. |
| Creating a fake production inventory | Keep it in-memory/callable for MVP; name it a lab-owned facade/bridge. |
| Skipping to O-RAN/O-Cloud too soon | Product Front Door continues to show those as planned gaps until separate evidence exists. |
| Duplicating order state | Service inventory should consume activation plans and create service-state records, not replace order lifecycle. |

## Verification plan

Run:

```bash
python3 -m py_compile services/service_inventory/*.py modules/product_front_door/server.py
pytest tests/unit/test_service_inventory_bridge.py tests/unit/test_product_front_door_module.py -q
pytest tests/unit/test_modules_registry.py tests/unit/test_modules_dashboard_service.py -q
pytest tests/integration/test_service_order_to_activation_evidence.py tests/regression/test_evidence_bundle_schema.py -q
git diff --check
```

Before commit, run the repo public-safe scans from `AGENTS.md`.

## ADR

### Decision

Build the TMF service inventory / activation bridge before O-RAN or O-Cloud
execution.

### Drivers

1. The Product Front Door already exposes the missing service-inventory layer.
2. Downstream O-RAN/O-Cloud work needs a service instance to attach to.
3. TMF638/TMF640 are already identified as gaps in the release register.
4. A narrow bridge can improve demo honesty without claiming formal conformance.

### Alternatives considered

- **Build O-RAN/SMO connection next** — rejected because it would attach network
  action directly to product/order state without a service instance boundary.
- **Build O-Cloud/OCP substrate view next** — rejected because it is farther
  downstream and would still need service identity and activation state.
- **Build TMF Evidence Explorer next** — useful, but less directly advances the
  purchase-to-service fulfillment path than the bridge.

### Consequences

- Product Front Door becomes more structurally truthful.
- Future O-RAN/O-Cloud work can attach to `service_id` and service state.
- The repository still avoids formal conformance claims until CTK/evidence work
  is separately performed.

### Follow-ups

1. Add O-RAN/SMO handoff after service instance state exists.
2. Add O-Cloud/O2/OCP substrate view after O-RAN/SMO handoff is mapped.
3. Add a TMF Evidence Explorer module as a companion viewer for CTK/spec gaps.
