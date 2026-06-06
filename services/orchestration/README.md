# MVP Orchestration Graph

This package owns the lab orchestration side of the `service_order_to_activation/`
MVP. It accepts the activation plan from `services/order_engine/`, maps the
subscriber/session intent, and invokes a 3GPP mock-core adapter contract.

## Boundary

- Evidence label: `functional_smoke`
- Standards reference: `3GPP release-baseline` row in the release register
- Claim boundary: not formal 3GPP, O-RAN, or TM Forum conformance
- Adapter execution: pending issue #24 under `adapters/3gpp/`

The service intentionally does not import copied mock-core internals. It only
builds the request payload that the adapter issue must implement.

## State transitions

1. `activation_plan_received`
2. `subscriber_session_intent_mapped`
3. `mock_core_adapter_invoked`
4. `mock_core_adapter_acknowledged`

Every state carries `correlation_id`, `order_id`, and `service_id` for later
evidence-bundle capture.

## HTTP surface

```text
POST /orchestration/v1/service-order-to-activation
```
