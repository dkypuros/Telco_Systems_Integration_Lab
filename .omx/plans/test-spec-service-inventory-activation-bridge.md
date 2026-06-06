# Test Spec: Service Inventory / Activation Bridge

## Unit tests

Create `tests/unit/test_service_inventory_bridge.py` covering:

1. Valid activation plan creates a service instance record.
2. Record preserves:
   - `correlation_id`
   - `product_id`
   - `order_id`
   - `service_id`
   - `customer_id`
3. State history includes:
   - `service_order_received`
   - `service_instance_reserved`
   - `activation_requested`
   - `mock_core_activation_recorded`
   - `downstream_domain_pending`
4. Standards metadata references TMF638 and TMF640.
5. Claim boundary says not formal TM Forum conformance.
6. Missing required activation-plan fields are rejected before any state is recorded.
7. Unsupported network actions are rejected.
8. Returned payload contains no private absolute paths.

## Product Front Door regression

Update `tests/unit/test_product_front_door_module.py` so:

1. `POST /api/activate-demo-product` includes the service inventory record.
2. Timeline marks service inventory as `complete`.
3. O-RAN and O-Cloud/OCP/ODA/Kubernetes stay `planned_gap`.
4. The response still includes `mock_activation_result` and evidence bundle path.

## Integration / evidence tests

Run existing tests to ensure the service-order-to-activation evidence bundle does
not drift accidentally:

```bash
pytest tests/integration/test_service_order_to_activation_evidence.py tests/regression/test_evidence_bundle_schema.py -q
```

If the evidence snapshot intentionally changes, update it and preserve known gaps.

## Safety checks

Run:

```bash
python3 -m py_compile services/service_inventory/*.py modules/product_front_door/server.py
pytest tests/unit/test_service_inventory_bridge.py tests/unit/test_product_front_door_module.py -q
pytest tests/unit/test_modules_registry.py tests/unit/test_modules_dashboard_service.py -q
git diff --check
```

Then run the public-safe scans required by `AGENTS.md`.

## Manual smoke

1. Start the dashboard.
2. Activate Product Front Door.
3. Open `http://127.0.0.1:8767/`.
4. Click **Activate Demo Product**.
5. Confirm the timeline shows service inventory complete and O-RAN/O-Cloud gaps still planned.
