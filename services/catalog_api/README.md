# MVP Catalog API

This package owns the catalog side of the `service_order_to_activation/` MVP.
It provides a small callable service and FastAPI wrapper for one basic 5G data
product fixture:

- product ID: `prod-5g-data-basic`
- model path: `models/standard_native/tmf/product_catalog/basic_5g_data_service.json`
- standards reference row: `TMF620` in `traceability/standards_release_register.yaml`
- evidence label: `functional_smoke`

## Boundary

This is a TMF620-referenced functional-smoke fixture/API. It is not formal TM
Forum conformance evidence and does not replace CTK testing. Downstream MVP
issues should pass through `correlation_id`, `product_id`, `subscriber_intent`,
and `session_intent` from this catalog response.

## Callable surface

```python
from services.catalog_api import lookup_product

response = lookup_product(
    "prod-5g-data-basic",
    correlation_id="corr-catalog-example-0001",
)
```

## HTTP surface

The FastAPI app is exposed as `services.catalog_api.api:app` and includes:

```text
GET /tmf-api/productCatalogManagement/v5/productSpecification
GET /tmf-api/productCatalogManagement/v5/productSpecification/{product_id}
```
