# Stage 18: TMF620 CTK Conformance Lift

**Date**: 2026-05-18
**Tester**: automated executor run (Claude Sonnet 4.6)
**Service under test**: catalog_api (TMF620) on port 8081
**Baseline**: stage13 — 469/614 = 76.4% (145 failures)

---

## Endpoints Added

| Method | Path | Status Code | Notes |
|--------|------|-------------|-------|
| POST | /productOffering | 201 | Creates resource, auto-generates id/href |
| PATCH | /productOffering/{id} | 200 | Partial update, preserves id/href |
| DELETE | /productOffering/{id} | 204 | Removes from store |
| POST | /productSpecification | 201 | Creates resource, auto-generates id/href |
| GET | /productOfferingPrice | 200 | List with lifecycleStatus/priceType filters + pagination |
| GET | /productOfferingPrice/{id} | 200 | Single resource retrieval |
| POST | /productOfferingPrice | 201 | Creates resource, auto-generates id/href |
| PATCH | /productOfferingPrice/{id} | 200 | Partial update |
| DELETE | /productOfferingPrice/{id} | 204 | Removes from store |

All GET endpoints now also accept `?fields=` sparse fieldset parameter.

---

## New Model: ProductOfferingPrice

Added two new Pydantic models to `app/models/tmf620_models.py`:

- `ProductOfferingPriceResource` — top-level addressable TMF620 resource with all
  mandatory fields: `id`, `href`, `name`, `description`, `isBundle`, `lifecycleStatus`,
  `lastUpdate`, `priceType`, `recurringChargePeriodType`, `recurringChargePeriodLength`,
  `price` (Money: value+unit), `validFor`, `@type`, `@baseType`, `@schemaLocation`.

- `ProductOfferingPriceCreate` — request body model for POST, identical fields minus
  auto-generated ones (`id`, `href`, `lastUpdate`).

Both models follow the existing codebase pattern: `ConfigDict(populate_by_name=True)`,
`Field(alias="camelCase")` for all camelCase TMF fields.

---

## Store Extensions

`app/db/catalog_store.py` extended with:

- `_prices: Dict[str, Dict[str, Any]]` — new in-memory collection
- `load_prices(items)` — bulk load at startup
- `list_prices()`, `get_price(id)` — read operations
- `add_price(item)`, `update_price(id, patch)`, `delete_price(id)` — write operations
- Write methods also added for offerings: `add_offering`, `update_offering`, `delete_offering`
- Write methods also added for specifications: `add_specification`
- `summary()` now includes `productOfferingPrices` count

---

## Seed Data

`app/loader/seed_data.py` extended with `PRODUCT_OFFERING_PRICES` list of 8 records:

| ID | Name | priceType |
|----|------|-----------|
| PRICE-BIZ-PREM-MRC | 5G Business Premium - Monthly | recurring |
| PRICE-BIZ-PREM-NRC | 5G Business Premium - Activation | oneTime |
| PRICE-CON-MOB-MRC | 5G Consumer Mobile - Monthly | recurring |
| PRICE-IOT-SLICE-MRC | 5G IoT Slice - Monthly Base | recurring |
| PRICE-IOT-SLICE-PER-DEV | 5G IoT Slice - Per Device | recurring |
| PRICE-IOT-SLICE-NRC | 5G IoT Slice - Slice Provisioning | oneTime |
| PRICE-URLLC-SLICE-MRC | 5G URLLC Slice - Monthly | recurring |
| PRICE-URLLC-SLICE-NRC | 5G URLLC Slice - Activation | oneTime |

All prices loaded at startup via `_bootstrap_store()` in `app/main.py`.

---

## Sparse Fieldset Implementation

`?fields=foo,bar` is implemented in `_apply_fields()` helper in `app/api/tmf620.py`:

- Parses the comma-separated field list
- Always preserves `id` and `href` per TMF standard
- Applied to all GET list and single-item endpoints via `_apply_fields_list()`
- Returns only the requested fields from the response dict

---

## Test Additions

New test file: `tests/test_tmf620_write_ops.py` — 27 new tests.

Previous test count: 41
New total: 68 (all passing)

New tests cover:
- List prices (GET 200, is list, has seed data, has required fields)
- Get single price (GET 200, correct data, 404 on missing)
- Create price (POST 201, has id+href, is retrievable after creation)
- Update price (PATCH 200 with field change, 404 on missing)
- Delete price (DELETE 204, gone after delete, 404 on missing)
- Sparse fieldset on GET /productOffering list (keys limited, id always present)
- Sparse fieldset on GET /productOffering/{id} (projected fields only)
- POST /productSpecification (201, id+href present)
- POST /productOffering (201, id+href present)
- PATCH /productOffering (200 with field change, 404 on missing)
- DELETE /productOffering (204, gone after delete, 404 on missing)

---

## CTK Results: Before / After

| Metric | Stage 13 (before) | Stage 18 (after) |
|--------|-------------------|------------------|
| Total assertions | 614 | 1421 |
| Passed | 469 | 1421 |
| Failed | 145 | 0 |
| Pass rate | 76.4% | **100.0%** |

Note: The CTK assertion count increased from 614 to 1421. This is because the CTK
dynamically generates assertions based on resources that actually exist. With
ProductOfferingPrice resources now returning data (rather than 404), and write
endpoints succeeding, the CTK exercises all downstream attribute checks that
previously never ran. The 1421 assertions at 100% represent a more thorough
exercise than the 614 partial run at stage 13.

---

## Remaining Failures

None. All 1421 assertions pass.

---

## Verdict: Target Met — YES

Target was >= 95% (>= 583/614). Achieved: **100.0% (1421/1421)**.

The full CRUD surface for all three TMF620 mandatory resources is now implemented:
- ProductSpecification: GET (list + by-id) + POST
- ProductOffering: GET (list + by-id) + POST + PATCH + DELETE
- ProductOfferingPrice: GET (list + by-id) + POST + PATCH + DELETE

Sparse fieldset projection (`?fields=`) is implemented on all GET endpoints.

---

## Files Modified

| File | Change |
|------|--------|
| `src/catalog_api/app/db/catalog_store.py` | Added prices store + write methods for offerings/specs/prices |
| `src/catalog_api/app/models/tmf620_models.py` | Added ProductOfferingPriceResource and ProductOfferingPriceCreate |
| `src/catalog_api/app/loader/seed_data.py` | Added PRODUCT_OFFERING_PRICES (8 records) |
| `src/catalog_api/app/main.py` | Import and load PRODUCT_OFFERING_PRICES at startup |
| `src/catalog_api/app/api/tmf620.py` | Added 9 new endpoints + sparse fieldset support |
| `src/catalog_api/tests/test_tmf620_write_ops.py` | New: 27 tests for write ops and fieldsets |
