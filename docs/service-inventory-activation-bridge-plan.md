# Service Inventory / Activation Bridge Plan

The next downstream gap after Product Front Door is the service inventory and
service activation boundary.

Product Front Door now proves a narrow local path from product selection to mock
activation, but it still jumps from activation plan to mock-core result without a
service instance record that future domains can attach to. Before O-RAN, O-Cloud,
OCP, ODA Canvas, or remediation work can be made meaningful, the lab needs a
bounded service identity and service state layer.

Planning artifacts:

- [`../.omx/plans/prd-service-inventory-activation-bridge.md`](../.omx/plans/prd-service-inventory-activation-bridge.md)
- [`../.omx/plans/test-spec-service-inventory-activation-bridge.md`](../.omx/plans/test-spec-service-inventory-activation-bridge.md)

Recommended next implementation target:

```text
services/service_inventory/
```

Then update:

```text
modules/product_front_door/server.py
```

to show service inventory as complete while keeping O-RAN and O-Cloud as planned
gaps.

Boundary: this is TMF638/TMF640-referenced functional-smoke work only. It is
not formal TM Forum conformance and does not replace CTK testing.
