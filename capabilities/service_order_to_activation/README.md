# Service Order to Activation MVP Contract

Status: `demo_evidence` for the narrow MVP path
Evidence label: `demo_evidence` for the local MVP only

This slice defines the first API-first vertical path for the Telco Systems
Integration Lab:

```text
product/catalog -> product order -> activation/orchestration -> mock 5G core adapter -> evidence bundle
```

The goal is not to import an external telco source tree. The goal is to keep a
small, lab-owned contract that local implementation and module work can build on
without overclaiming 3GPP, TM Forum, or O-RAN conformance.

## Source boundary

- No full upstream repository is required for this MVP.
- Open5GS, free5GC, OAI, and vendor systems remain future external
  implementation profiles/interoperability targets.
- Passing this MVP can support `demo_evidence` only for the scenario recorded in
  the evidence bundle. It does not prove formal standards conformance.

## Required identifiers

| Identifier | Owner | Purpose |
|---|---|---|
| `correlation_id` | scenario client or integration test | End-to-end trace key propagated through every step and evidence artifact. |
| `product_id` | catalog API | Selected sellable product, starting with `prod-5g-data-basic`. |
| `order_id` | product order lifecycle | Commercial order instance created from the selected product. |
| `service_id` | activation/service inventory facade | Service instance to activate and later observe. |
| `subscriber_intent` | orchestration layer | Public-safe description of the subscriber/profile action to request. |
| `session_intent` | orchestration layer | Public-safe description of PDU/session action, such as DNN, slice, and QoS intent. |

## Flow contract

The machine-readable contract is
[`flow-contract.yaml`](flow-contract.yaml). The summary is:

1. **Catalog product lookup** — `services/catalog_api/` returns a basic 5G data
   product and carries `correlation_id`.
2. **Product order create** — `services/order_engine/` accepts `product_id`,
   returns `order_id`, and records order lifecycle state.
3. **Service activation plan** — `services/order_engine/` derives a service
   activation plan with `service_id` and a network-facing action.
4. **Orchestration intent mapping** — `services/orchestration/` maps the service
   plan to `subscriber_intent` and `session_intent`.
5. **Mock core activation adapter** — `adapters/3gpp/` translates the intent into
   one narrow mock 5G core activation request.
6. **Evidence bundle record** — `traceability/evidence_snapshots/` records the
   public-safe evidence bundle and known gaps by `correlation_id`.

## Standards rows used as planning references

| Standards row | Current role in this MVP |
|---|---|
| `TMF620` | Product catalog reference/planned smoke path. |
| `TMF622` | Product order reference/planned smoke path. |
| `TMF641` | Service order split/activation-plan reference; formal coverage missing. |
| `TMF640` | Service activation/management reference; implementation planned only. |
| `3GPP release-baseline` | Mock 5G core activation boundary; no formal protocol conformance. |

Authoritative status remains in
[`traceability/standards_release_register.yaml`](../../traceability/standards_release_register.yaml).

## Current demo evidence

This slice has moved from `planned` to narrow `demo_evidence` through the
repeatable integration test and evidence snapshot:

- [`tests/integration/test_service_order_to_activation_evidence.py`](../../tests/integration/test_service_order_to_activation_evidence.py)
- [`traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json`](../../traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json)

The demo evidence covers:

- catalog response for `prod-5g-data-basic`;
- order lifecycle with `order_id` and state history;
- service activation plan with `service_id`;
- orchestration output containing `subscriber_intent` and `session_intent`;
- mock-core adapter transcript with a bounded mock activation result;
- public-safe evidence bundle that validates against
  [`traceability/evidence_bundle.schema.json`](../../traceability/evidence_bundle.schema.json);
- known gaps to formal TM Forum and 3GPP conformance explicitly recorded;
- tests that run without external upstream repositories.

It still does **not** cover formal TM Forum CTK conformance, formal 3GPP
protocol conformance, O-RAN behavior, O-Cloud/O2/OCP execution, or production
service inventory.

## Completed MVP implementation sequence

| Issue | Scope |
|---|---|
| #21 | Catalog fixture/API for a basic 5G data product. |
| #22 | Product order lifecycle and activation-plan output. |
| #23 | Orchestration graph from order to mock network action. |
| #24 | 3GPP mock-core activation adapter. |
| #25 | End-to-end MVP integration test and public-safe evidence snapshot. |
