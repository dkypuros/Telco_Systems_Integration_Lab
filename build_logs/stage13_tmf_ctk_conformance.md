# Stage 13: TM Forum CTK Conformance Test Results

**Date**: 2026-05-18
**Tester**: automated executor run (Claude Sonnet 4.6)
**Services under test**: catalog_api (TMF620) on port 8081, order_engine (TMF622) on port 8080

---

## CTKs Attempted

| CTK | Runtime | Target Endpoint | Status |
|-----|---------|-----------------|--------|
| CTK-TMF620-ProductCatalog | Node.js v25.9.0 + Newman (local npm) | http://127.0.0.1:8081/tmf-api/productCatalogManagement/v4/ | Run completed |
| CTK-TMF622-ProductOrdering | Node.js v25.9.0 + Newman (local npm) | http://127.0.0.1:8080/tmf-api/productOrderingManagement/v4/ | Run completed |
| CTK-TMF641-ServiceOrdering-R18-0 | Node.js / Newman | N/A | Skipped - partial implementation only, reserved for follow-up |
| CTK-TMF640-ServiceActivation-R18-5 | Node.js / Newman | N/A | Skipped - not implemented |
| CTK-TMF645-ServiceQualification-R18-0 | Node.js / Newman | N/A | Skipped - not implemented |

Runtime note: Newman is not installed globally. Each CTK ships Newman as a local `node_modules`
dependency via `package.json`. `npm install` inside `ctk/` resolves it. No global packages
were installed and no `brew install` was used.

---

## Pass / Fail / Error Counts per CTK

### TMF622 ProductOrdering (order_engine, port 8080)

| Metric | Count |
|--------|-------|
| Total requests | 9 |
| Total assertions | 63 |
| Passed assertions | 63 |
| Failed assertions | 0 |
| Errors | 0 |
| **Pass rate** | **100%** |

Operations exercised:
- POST /productOrder -> 201 Created (pass)
- GET /productOrder -> 200 (pass)
- GET /productOrder/{id} -> 200 (pass)
- GET /productOrder?fields=href -> 200 (pass)
- GET /productOrder?fields=id -> 200 (pass)
- GET /productOrder?id={id} -> 200 (pass)
- GET /productOrder?fields=orderDate -> 200 (pass)
- GET /productOrder?orderDate={date} -> 200 (pass)
- GET /productOrder/404ID -> 404 (pass)

### TMF620 ProductCatalog (catalog_api, port 8081)

| Metric | Count |
|--------|-------|
| Total requests | 47 |
| Total assertions | 614 |
| Passed assertions | 469 |
| Failed assertions | 145 |
| Errors | 0 |
| **Pass rate** | **76.4%** |

Breakdown by resource:

| Resource | Requests | Assertions Pass | Assertions Fail | Root Cause |
|----------|----------|-----------------|-----------------|------------|
| ProductSpecification (GET ops) | 12 | 205 | 0 | Fully conformant |
| ProductSpecification (POST) | 1 | 0 | 12 | POST not implemented (405) |
| ProductOffering (GET ops) | 12 | 201 | 0 | Fully conformant |
| ProductOffering (POST) | 1 | 0 | 13 | POST not implemented (405) |
| ProductOffering (PATCH) | 1 | 0 | 2 | PATCH not implemented (405) |
| ProductOffering (DELETE) | 1 | 0 | 1 | DELETE not implemented (405) |
| ProductOffering href-check | 1 | 0 | 1 | `fields` sparse fieldsets not implemented |
| ProductOfferingPrice (all) | 18 | 63 | 116 | Entire resource not implemented (404 on all) |

---

## Top Failures

### 1. Missing POST /productSpecification (405 Method Not Allowed)

Test: "Status code is 201"
Message: expected response to have status code 201 but got 405
Cascade: 12 downstream assertions fail because no resource was created, so all subsequent
GET-by-id / field / value checks return undefined or the 405 error body.

Root cause: The catalog_api router in `app/api/tmf620.py` exposes only GET endpoints for
ProductSpecification. No POST, PATCH, or DELETE handlers exist. FastAPI returns 405 when
the path matches but the method does not.

### 2. Missing POST /productOffering (405 Method Not Allowed)

Test: "Status code is 201"
Message: expected response to have status code 201 but got 405
Cascade: 13 downstream assertions fail (same pattern as above, plus the `productSpecification`
reference attribute check).

Root cause: Same as above. The router has GET-only coverage for productOffering.

### 3. PATCH and DELETE not implemented for ProductOffering (405)

Tests: "Successful PATCH request" / "Status code is 204"
Messages: expected 200 but got 405 / expected 204 but got 405

Root cause: No PATCH or DELETE handlers in the catalog_api router. TMF620 mandates
PATCH for partial update and DELETE for removal.

### 4. Entire ProductOfferingPrice resource missing (404 on all 18 requests)

Tests: "Status code is 201", "Response has priceType attribute", "Instance has all
mandatory attributes", "Status code is 200", "Successful PATCH request", "Status code is 204"
Messages: 404 Not Found on POST, all GETs, PATCH, and DELETE

Root cause: The `/tmf-api/productCatalogManagement/v4/productOfferingPrice` path is not
registered at all. ProductOfferingPrice is a mandatory TMF620 resource. 116 of 145 failures
(80%) originate here.

### 5. Sparse fieldset projection (`?fields=`) not enforced

Test: "Body includes value held on href" (href check on a `?fields=href` response)
Message: The `fields` query parameter is accepted but ignored. The API returns the full
object regardless, so the assertion that only the requested fields appear fails.

Specifically the CTK GETs `?fields=href` and checks the href value - but because the
full object is returned, the CTK's environment variable capture logic fails and the
downstream `Body includes value held on href` test gets undefined.

### 6. Null fields in ProductOrder response (informational, TMF622 still passes)

TMF622 passed 100% but the order engine returns `null` for many optional fields
(`priority`, `description`, `category`, `requestedCompletionDate`, `requestedStartDate`,
`notificationContact`, `note`, and nested `product`/`productOffering` inside order items).
The CTK v4.0.0 test kit does not assert on optional-field presence, so these nulls do not
cause failures today. However, a stricter CTK version or a real integration partner would
reject null-valued fields that should be omitted entirely per JSON serialization best
practice (use `exclude_none=True` in FastAPI response models).

---

## Conformance Verdict

| API | Conformance | Assessment |
|-----|-------------|------------|
| TMF622 ProductOrdering | **100%** (63/63) | Fully conformant for the tested mandatory operations |
| TMF620 ProductCatalog | **76.4%** (469/614) | Partial - read-only conformant, write operations absent |

**Biggest gap: TMF620 is a read-only catalog.** The CTK requires full CRUD (Create, Read,
Update, Delete) on three resources: ProductSpecification, ProductOffering, and
ProductOfferingPrice. The catalog_api implements only GET for the first two and does not
implement ProductOfferingPrice at all.

The 76.4% figure is somewhat generous because the GET operations all pass cleanly. If
weighted by mandatory operation surface area, the write-method deficit drops effective
conformance closer to 50% of required behaviors.

TMF622 is fully conformant for the CTK's mandatory test scope. The order engine correctly
handles POST (create), GET (list + get-by-id), field filtering, attribute filtering, and
404 handling.

---

## Recommended Fixes

### Priority 1 - Add write methods to ProductSpecification and ProductOffering (TMF620)

Add POST, PATCH, and DELETE handlers to `src/catalog_api/app/api/tmf620.py`.

- POST /productSpecification - create a new spec, return 201 with `id`, `href`,
  `name`, `lastUpdate`, `lifecycleStatus` fields populated.
- PATCH /productSpecification/{id} - partial update, return 200 with updated resource.
- DELETE /productSpecification/{id} - remove, return 204 No Content.
- Same three methods for /productOffering.

The in-memory `catalog_store` already holds the data structures; the handlers just need
to call `store.add_*`, `store.update_*`, and `store.delete_*` equivalents.

### Priority 2 - Implement the ProductOfferingPrice resource entirely (TMF620)

Register a new router path `/productOfferingPrice` with full CRUD. This single gap
accounts for 116 of 145 failures (80%). Minimum mandatory fields on a
ProductOfferingPrice: `id`, `href`, `name`, `lastUpdate`, `lifecycleStatus`, `priceType`.

### Priority 3 - Implement `?fields=` sparse fieldset projection (TMF620)

When `fields=href,name` is present in the query string, the response must contain ONLY
those keys. FastAPI does not do this automatically. Add a response-filtering utility that
strips keys not in the `fields` list before returning. This affects both catalog_api and
should be pre-emptively added to order_engine for future CTK versions.

### Priority 4 - Suppress null fields in JSON responses (TMF622)

In the order_engine Pydantic models, set `model_config = ConfigDict(exclude_none=True)` or
use `response_model_exclude_none=True` on each endpoint. Returning `null` for every
optional field makes responses bulkier and diverges from TMF API reference implementations
that omit unset attributes. This will not break the current CTK but will matter for
integration testing with real BSS/OSS partners.

### Priority 5 - Add href auto-population on resource creation (TMF620, TMF622)

The CTK checks that the `href` field returned after a POST equals the canonical URL of
the created resource. Ensure POST handlers set `href` to the full path, e.g.:
`/tmf-api/productCatalogManagement/v4/productSpecification/{id}`.

---

## Artifacts Produced

| File | Location |
|------|----------|
| TMF620 JSON results | `specs/tmforum_standards/CTK-TMF620-ProductCatalog/jsonResults.json` |
| TMF620 HTML report | `specs/tmforum_standards/CTK-TMF620-ProductCatalog/htmlResults.html` |
| TMF622 JSON results | `specs/tmforum_standards/CTK-TMF622-ProductOrdering/jsonResults.json` |
| TMF622 HTML report | `specs/tmforum_standards/CTK-TMF622-ProductOrdering/htmlResults.html` |
| This report | `build_logs/stage13_tmf_ctk_conformance.md` |
