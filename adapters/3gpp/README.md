# 3GPP Mock-Core Activation Adapter

This directory owns the MVP adapter boundary from `services/orchestration/` to a
mock 5G core activation result.

## Boundary

- Capability slices: `service_order_to_activation/`, `subscriber_lifecycle/`
- Evidence label: `functional_smoke`
- Standards reference: `3GPP release-baseline` in the release register
- External runtime required: no
- Full upstream source copied: no

The adapter translates orchestration `subscriber_intent` and `session_intent`
into a small mock-core payload and uses a controlled local stub by default. Tests
can inject a mock-core surface callable to prove the adapter contract without
requiring external upstream repositories or live network services.

## HTTP surface

```text
POST /adapters/3gpp/v1/mock-core/activate
```

## Claim boundary

This is not formal 3GPP conformance evidence. It proves only that the MVP
activation intent can cross the adapter boundary and produce a public-safe,
correlated functional-smoke result.
