# Catalog API

TM Forum TMF620 Product Catalog Management.

**Port:** 8081
**Framework:** FastAPI (Python, sync handlers)
**Persistence:** In-memory dict store (`CatalogStore`), populated at startup
**Source root:** `src/catalog_api/`

---

## Purpose

The catalog API is the authoritative source of product offerings for the Tech-Co lab.
The storefront reads from it to populate the browsable product list, and the order engine
references offering IDs from it when decomposing orders. It exposes the full TMF620 surface
including productCatalog, category, productOffering, productSpecification, and
productOfferingPrice resources.

---

## Endpoints

All routes are served on port 8081 under the base path
`/tmf-api/productCatalogManagement/v4`, defined in `app/api/tmf620.py` (line 39).

### Health

| Method | Path    | Description                                         |
|--------|---------|-----------------------------------------------------|
| GET    | /health | Returns `{"status":"ok"}` plus store summary counts |
| GET    | /       | Service root with docs and offerings links          |

### productCatalog

| Method | Path                                           | Description                              |
|--------|------------------------------------------------|------------------------------------------|
| GET    | /tmf-api/productCatalogManagement/v4/productCatalog          | List all catalogs. `?fields=` `?offset=` `?limit=` |
| GET    | /tmf-api/productCatalogManagement/v4/productCatalog/{id}     | Retrieve a single catalog. `?fields=`    |

### category

| Method | Path                                           | Description                              |
|--------|------------------------------------------------|------------------------------------------|
| GET    | /tmf-api/productCatalogManagement/v4/category                | List all categories. `?fields=` `?offset=` `?limit=` |
| GET    | /tmf-api/productCatalogManagement/v4/category/{id}           | Retrieve a single category. `?fields=`   |

### productOffering

| Method | Path                                                    | Description                                                    |
|--------|---------------------------------------------------------|----------------------------------------------------------------|
| GET    | /tmf-api/productCatalogManagement/v4/productOffering          | List all offerings. `?fields=` `?lifecycleStatus=` `?offset=` `?limit=` |
| GET    | /tmf-api/productCatalogManagement/v4/productOffering/{id}     | Retrieve a single offering. `?fields=`                         |
| POST   | /tmf-api/productCatalogManagement/v4/productOffering          | Create a new offering. Body: JSON dict. Returns 201.           |
| PATCH  | /tmf-api/productCatalogManagement/v4/productOffering/{id}     | Partial update. `id` and `href` are ignored in patch body.     |
| DELETE | /tmf-api/productCatalogManagement/v4/productOffering/{id}     | Remove an offering. Returns 204.                               |

### productSpecification

| Method | Path                                                         | Description                                      |
|--------|--------------------------------------------------------------|--------------------------------------------------|
| GET    | /tmf-api/productCatalogManagement/v4/productSpecification          | List all specifications. `?fields=` `?offset=` `?limit=` |
| GET    | /tmf-api/productCatalogManagement/v4/productSpecification/{id}     | Retrieve a single specification. `?fields=`      |
| POST   | /tmf-api/productCatalogManagement/v4/productSpecification          | Create a new specification. Returns 201.         |

### productOfferingPrice

| Method | Path                                                            | Description                                            |
|--------|-----------------------------------------------------------------|--------------------------------------------------------|
| GET    | /tmf-api/productCatalogManagement/v4/productOfferingPrice             | List all prices. `?fields=` `?lifecycleStatus=` `?priceType=` `?offset=` `?limit=` |
| GET    | /tmf-api/productCatalogManagement/v4/productOfferingPrice/{id}        | Retrieve a single price. `?fields=`                    |
| POST   | /tmf-api/productCatalogManagement/v4/productOfferingPrice             | Create a new price. Returns 201.                       |
| PATCH  | /tmf-api/productCatalogManagement/v4/productOfferingPrice/{id}        | Partial update.                                        |
| DELETE | /tmf-api/productCatalogManagement/v4/productOfferingPrice/{id}        | Remove a price. Returns 204.                           |

### Field projection

All GET list and detail endpoints support a `?fields=` query parameter. Pass a
comma-separated list of field names to receive only those fields plus `id` and `href`.
Implemented in `_apply_fields()` / `_apply_fields_list()` in `app/api/tmf620.py`
(lines 55-67).

---

## Internal Architecture

```
src/catalog_api/app/
  main.py               FastAPI app, CORS config, lifespan (_bootstrap_store)
  api/
    tmf620.py           All TMF620 route handlers
  models/
    tmf620_models.py    Pydantic models (used for validation in extended features)
  loader/
    psr_loader.py       Reads offerings from tmforum_psr_learning codebase (if present)
    seed_data.py        5 seed offerings + specs + prices + catalogs + categories
  db/
    catalog_store.py    In-memory dict store: CatalogStore singleton + summary()
```

---

## Startup Sequence

`_bootstrap_store()` in `app/main.py` (lines 43-71) runs at lifespan start:

1. Attempts to load offerings from the PSR codebase via `psr_loader.load_psr_offerings()`.
   If the PSR path is absent or fails, returns empty dicts gracefully.
2. Merges seed data from `seed_data.py`. Seed items fill in whatever PSR did not provide
   (PSR items take precedence by ID).
3. Loads catalogs and categories (always from seed data).
4. Loads prices (always from seed data).
5. Logs a summary line with counts per resource type.

---

## Seed Offerings (`app/loader/seed_data.py`)

Five product offerings are always present after startup:

| ID                  | Name                  | Category       | Price (recurring)   | Price (one-time)  |
|---------------------|-----------------------|----------------|---------------------|-------------------|
| `OFF-5G-BIZ-PREMIUM`  | 5G Business Premium   | 5G Business    | $299.00/month       | $99.00 activation |
| `OFF-5G-CON-MOBILE`   | 5G Consumer Mobile    | 5G Consumer    | $49.99/month        | (none)            |
| `OFF-5G-IOT-SLICE`    | 5G IoT Slice          | 5G IoT         | $499.00/month + $0.50/device | $250.00 provisioning |
| `OFF-5G-ORAN-BUNDLE`  | 5G O-RAN Bundle       | 5G O-RAN       | $799.00/month       | $200.00 activation |
| `OFF-5G-URLLC-SLICE`  | 5G URLLC Slice        | 5G URLLC       | $1,999.00/month     | $500.00 provisioning |

Each offering references a `ProductSpecification` with `productSpecCharacteristic` entries
describing technical parameters (speed, latency, QoS class, etc.). All five specs are
defined in `PRODUCT_SPECIFICATIONS` in `seed_data.py` (lines 85-229).

The master catalog object is `CAT-TECHCO-5G`, which references all five category nodes.

---

## In-Memory Store (`app/db/catalog_store.py`)

`CatalogStore` (lines 19-179) is a module-level singleton (`store = CatalogStore()` at
line 179) holding five dicts keyed by resource ID:

- `_offerings`, `_specifications`, `_categories`, `_catalogs`, `_prices`

All dict lookups are O(1). No persistence across process restarts; data is re-seeded
on each startup. `store.summary()` returns a dict of counts per resource type, used by
the `/health` endpoint.

---

## PSR Loader (`app/loader/psr_loader.py`)

Reads additional offerings from a TM Forum PSR (Product Specification Reference)
codebase pointed to by the `PSR_LEARNING_PATH` environment variable. If the path is
absent, the loader returns empty dicts and seed data provides all offerings.

---

## Tests

**68/68 pytest pass** (stage 18). Run from `src/catalog_api/`:

```bash
cd src/catalog_api
source .venv/bin/activate
pytest
```

**TMF620 CTK conformance: 100% (1421/1421 assertions)** per stage 18.

---

## Environment Variables

| Variable                  | Default                                          | Description                                      |
|---------------------------|--------------------------------------------------|--------------------------------------------------|
| `CATALOG_API_CORS_ORIGINS` | `http://localhost:8095,http://127.0.0.1:8095`  | Comma-separated allowed CORS origins             |
| `PSR_LEARNING_PATH`        | (empty)                                         | Path to tmforum_psr_learning codebase for additional offerings |

---

## Running Standalone

```bash
cd src/catalog_api
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --port 8081 --reload
```

Interactive docs: http://localhost:8081/docs

---

## How to Add a New Offering

Add an entry to `PRODUCT_OFFERINGS` in `app/loader/seed_data.py`, following the
existing pattern. At minimum provide:

```python
{
    "id": "OFF-5G-MY-OFFERING",
    "href": "/tmf-api/productCatalogManagement/v4/productOffering/OFF-5G-MY-OFFERING",
    "name": "My New Offering",
    "description": "...",
    "lifecycleStatus": "Active",
    "isSellable": True,
    "isBundle": False,
    "lastUpdate": _NOW,
    "validFor": _VALID_FOR,
    "productSpecification": _spec_ref("SPEC-MY-SPEC", "My Spec Name"),
    "category": [_category_ref("CAT-5G-MY-CATEGORY", "My Category")],
    "productOfferingPrice": [
        _price("PRICE-MY-MRC", "My Monthly", "recurring", 99.00, period="month"),
    ],
    "@type": "ProductOffering",
}
```

Also add a matching entry to `PRODUCT_SPECIFICATIONS` and ensure the category exists in
`CATEGORIES`. Then add a corresponding decomposition rule in
`src/order_engine/app/decomposition/rules.yaml` so the order engine knows what steps
to execute when an order for this offering is placed.
