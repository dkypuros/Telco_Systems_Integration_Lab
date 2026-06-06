# PRD: Product Front Door Module

## Objective

Create a local visual module that lets an operator select the existing basic 5G
data product and run the repository's current service-order-to-activation MVP
spine from a browser.

## User story

As an operator or reviewer, I want to open a local module, see the first sellable
product, click one bounded activation action, and watch how far the lab can carry
that product intent through TM Forum-style order handling, orchestration, mock
3GPP activation, and evidence.

## Current evidence baseline

The MVP spine already exists:

- `services/catalog_api/`
- `services/order_engine/`
- `services/orchestration/`
- `adapters/3gpp/mock_core_activation_adapter.py`
- `tests/integration/test_service_order_to_activation_evidence.py`
- `traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json`

## Requirements

1. Register a new module in `modules/index.json` with a unique localhost port.
2. Add `modules/product_front_door/module.json` and `README.md`.
3. Add a standard-library local server module.
4. Render the basic product from the existing catalog fixture/service.
5. Provide one fixed browser action to run the existing MVP path.
6. Return a timeline with product, order, activation plan, orchestration, adapter,
   and evidence bundle status.
7. Show O-RAN/O-Cloud/ODA/OCP as planned gaps for this MVP, not successful steps.
8. Preserve public-safe claim boundaries in HTML, JSON, and README text.

## Non-goals

- No formal TM Forum, 3GPP, O-RAN, ODA, OCP, Kubernetes, or O-Cloud conformance claim.
- No arbitrary shell execution.
- No new package dependencies.
- No multi-product catalog builder in the first slice.
- No external upstream project import.

## Acceptance criteria

- Dashboard card can activate/open the module.
- `GET /api/product` returns `prod-5g-data-basic` metadata.
- `POST /api/activate-demo-product` runs only the fixed MVP path.
- Response includes `correlation_id`, `product_id`, `order_id`, `service_id`, and
  `mock_activation_result`.
- Response includes explicit downstream gap statuses for O-RAN and O-Cloud.
- Unit tests cover registry metadata, product view payload, fixed activation path,
  and rejection of unknown routes/actions.
