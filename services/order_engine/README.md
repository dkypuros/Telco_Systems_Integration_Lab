# MVP Order Engine

This package owns the product-order side of the `service_order_to_activation/`
MVP. It accepts the basic 5G data product from `services/catalog_api/`, records a
small order lifecycle, and returns an activation plan for the later orchestration
and mock-core adapter issues.

## Boundary

- Product order reference: `TMF622`
- Later service-order mapping reference: `TMF641`
- Evidence label: `functional_smoke`
- Claim boundary: not formal TM Forum conformance and not CTK evidence

## Lifecycle states

The MVP emits only the states needed for downstream activation work:

1. `acknowledged`
2. `activation_requested`

## Downstream plug-in points

The activation plan intentionally names where future work plugs in:

- `services/orchestration/` for issue #23 service-order/orchestration mapping;
- `adapters/3gpp/` for issue #24 mock 5G core activation;
- a future service-inventory/TMF640 facade for service inventory state.

## HTTP surface

```text
POST /tmf-api/productOrderingManagement/v5/productOrder
```

The route accepts a public-safe demo `customer_id`, a catalog `product_id`, and
an `x-correlation-id` header.
