# Capabilities Manifest

Capabilities are vertical slices. They connect standards, models, procedures, adapters, services, tests, and evidence.

`traceability/standards_release_register.yaml` remains authoritative for standard release/test/gap status.

## Current planned slices

| Capability | Purpose | Expected standards | Current status | Next evidence step |
|---|---|---|---|---|
| `service_order_to_activation/` | Customer/order journey from TM Forum order to activation | TMF620, TMF622, TMF641, 3GPP core APIs | planned | Link Tech-Co CTK evidence and order-flow logs before copying service code. |
| `slice_provisioning/` | Network slice offer/order/provision path | TM Forum, 3GPP NSSF/NSSAI, O-RAN O2/O1 as applicable | planned | Map local NSSF/slice artifacts and tested-against baseline. |
| `ran_control_loop/` | RAN policy/control loop | O-RAN A1/E2/E2SM, 3GPP RAN refs | planned | Map O-RAN closed-loop evidence as demo evidence, not formal conformance. |
| `subscriber_lifecycle/` | Subscriber provisioning and lifecycle | TM Forum order/service APIs, 3GPP UDM/UDR/AMF | planned | Map UDR row/AMF context evidence and local gaps. |
| `assurance_to_remediation/` | Observability, assurance, remediation workflow | TM Forum assurance APIs as applicable, O-RAN, 3GPP management refs | planned | Map AI/falsification and assurance evidence as experimental until promoted. |

## Claim rule

A capability is not complete until each linked standards claim points to:

- release-register row,
- implementation path,
- test/evidence path,
- conformance level,
- known gap, and
- next step.
