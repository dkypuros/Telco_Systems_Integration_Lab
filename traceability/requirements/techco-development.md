# Tech-Co Development Guide

How to extend the Tech-Co 5G lab. Covers the repository layout, service
architecture, and step-by-step recipes for adding products, adapters,
AI observer components, and storefront pages.

For running the stack see `docs/operations.md`. For testing see `docs/testing.md`.

---

## Repository Layout

```
Tech-Co/
  components/          Third-party and external component trees (do not modify)
    legacy-standalone-5g-emulator/         NVIDIA accelerated edge 5G emulator (Python ~21k lines)
      open-digital-platform-2_0/
        clean_5g_emulator_api/ Python NF source (nrf.py, amf.py, smf.py, ...)
        start_3gpp_services.sh
        stop_services.sh
  external/            External repos included as source trees
    oran_o2ims/          Red Hat O-RAN O2IMS Go binary source
  specs/               Standards documents and TMF CTK conformance kits
    tmforum_standards/
      CTK-TMF620-ProductCatalog/
      CTK-TMF622-ProductOrdering/
  src/                 Tech-Co services (actively developed)
    order_engine/        FastAPI, TMFC003/TMF622, port 8080
    catalog_api/         FastAPI, TMF620, port 8081
    ai_observer/         FastAPI, anomaly detection, port 8090
    storefront/          Next.js 14, customer UI, port 3000
    ims_test_client/     VoNR call flow test driver
  scripts/             Automation scripts (bootstrap, bring_up, stop, demo, ...)
    .pids/               PID files written at runtime
    bootstrap.sh
    bring_up.sh
    stop_all.sh
    status.sh
    demo_order_flow.sh
    demo_vonr_call.sh
    demo_oran_closed_loop.sh
    integration_test_full.sh
    start_dashboard.sh
    init_udr_db.py
  config/              Configuration files
    paths.yaml           Absolute paths and port assignments (source of truth)
    services.yaml        Service definitions for scripts
  dashboard/           Static HTML dashboard served on port 8095
  build_logs/          Historical stage evidence (stage1_*.md, stage2_*.md, ...)
    run/               Timestamped runtime logs (gitignored, created at runtime)
  docs/                This documentation directory
  .env.example         Environment variable reference
```

---

## The Four Service Types

| Service | Language | Framework | Port | Entry point |
|---------|---------|---------|------|------------|
| order_engine | Python | FastAPI + SQLAlchemy | 8080 | `src/order_engine/app/main.py` |
| catalog_api | Python | FastAPI | 8081 | `src/catalog_api/app/main.py` |
| ai_observer | Python | FastAPI | 8090 | `src/ai_observer/app/main.py` |
| storefront | TypeScript | Next.js 14 | 3000 | `src/storefront/src/app/` |
| legacy standalone 5G emulator NFs | Python | FastAPI (per NF) | 8000-9010 | `components/.../clean_5g_emulator_api/` |
| oran_o2ims | Go | net/http | 8083 | `external/oran_o2ims/` |

All Python services use:
- Python type hints throughout.
- `async`/`await` for all I/O (httpx for outbound HTTP, SQLAlchemy async for DB).
- Pydantic v2 for request/response validation.
- pytest for unit tests.

---

## How to Add a New Product Offering

Adding a product requires two files: seed_data.py and rules.yaml.

### Step 1: Add the offering to seed_data.py

File: `src/catalog_api/app/loader/seed_data.py`

Add entries to three lists:

**PRODUCT_SPECIFICATIONS** - technical spec with characteristics:

```python
{
    "id": "SPEC-5G-YOUR-PRODUCT",
    "href": "/tmf-api/productCatalogManagement/v4/productSpecification/SPEC-5G-YOUR-PRODUCT",
    "name": "Your Product Specification",
    "description": "Technical description of the product.",
    "version": "1.0",
    "brand": "Tech-Co",
    "lifecycleStatus": "Active",
    "lastUpdate": _NOW,
    "isBundle": False,
    "validFor": _VALID_FOR,
    "productNumber": "PN-5G-YOUR-001",
    "productSpecCharacteristic": [
        _spec_char("downloadSpeed", "200", "string", "Mbps"),
        _spec_char("latency", "5", "string", "ms"),
        # add more characteristics as needed
    ],
    "@type": "ProductSpecification",
}
```

**PRODUCT_OFFERINGS** - the sellable offering linked to the spec:

```python
{
    "id": "OFF-5G-YOUR-PRODUCT",
    "href": "/tmf-api/productCatalogManagement/v4/productOffering/OFF-5G-YOUR-PRODUCT",
    "name": "5G_Your_Product",
    "description": "Customer-facing description.",
    "version": "1.0",
    "lifecycleStatus": "Active",
    "isSellable": True,
    "isBundle": False,
    "lastUpdate": _NOW,
    "validFor": _VALID_FOR,
    "productSpecification": _spec_ref("SPEC-5G-YOUR-PRODUCT", "Your Product Specification"),
    "category": [_category_ref("CAT-5G-BUSINESS", "5G Business")],
    "productOfferingPrice": [
        _price("PRICE-YOUR-MRC", "Your Product - Monthly", "recurring", 199.00, period="month"),
    ],
    "@type": "ProductOffering",
}
```

**CATEGORIES** - add the offering ID to the relevant category's `productOffering` list,
or create a new category following the existing pattern.

### Step 2: Add a decomposition rule

File: `src/order_engine/app/decomposition/rules.yaml`

Add a new entry under `offering_patterns` using the offering ID as the key:

```yaml
offering_patterns:

  OFF-5G-YOUR-PRODUCT:
    service_category: "5G_YourCategory"
    steps:
      - step_name: allocate_slice
        adapter: o2ims
        payload_extra:
          slice_type: eMBB
          sst: 1
          sd: "000099"
      - step_name: provision_subscriber
        adapter: legacy_5g_emulator_python
        payload_extra:
          subscriber_profile: your_profile
          qos_class: 9
          _adapter: legacy_5g_emulator_python
```

The `adapter` field maps to adapter keys registered in
`src/order_engine/app/api/tmf622.py` (`_resolve_adapter_for_step`). Current
valid keys are `legacy_5g_emulator_python` and `o2ims`. The `_adapter` key in `payload_extra`
overrides the routing for that specific step (used for explicit routing in
multi-adapter rules).

### Step 3: Restart the services

```bash
bash scripts/stop_all.sh
bash scripts/bring_up.sh
```

### Step 4: Test with curl

```bash
# Confirm the new offering appears in the catalog
curl -s http://localhost:8081/tmf-api/productCatalogManagement/v4/productOffering \
  | jq '.[] | select(.id == "OFF-5G-YOUR-PRODUCT")'

# Place an order for the new offering
curl -s -X POST http://localhost:8080/tmf-api/productOrderingManagement/v4/productOrder \
  -H "Content-Type: application/json" \
  -d '{
    "externalId": "test-001",
    "priority": "1",
    "orderItem": [{
      "id": "1",
      "action": "add",
      "productOffering": {"id": "OFF-5G-YOUR-PRODUCT", "name": "5G_Your_Product"}
    }]
  }' | jq .
```

---

## How to Add a New Southbound Adapter

### Step 1: Subclass SouthboundAdapter

File: `src/order_engine/app/adapters/base.py` defines the interface:

```python
class SouthboundAdapter(ABC):
    async def activate(self, step_name: str, payload: dict[str, Any]) -> Any: ...
    async def rollback(self, step_name: str, payload: dict[str, Any]) -> None: ...
```

Create `src/order_engine/app/adapters/your_adapter.py`:

```python
"""Your adapter: southbound integration with <system>."""
import logging
from typing import Any
from app.adapters.base import SouthboundAdapter

logger = logging.getLogger(__name__)


class YourAdapter(SouthboundAdapter):

    async def activate(self, step_name: str, payload: dict[str, Any]) -> Any:
        logger.info("[YourAdapter] ACTIVATE step='%s'", step_name)
        if step_name == "your_step":
            # call your downstream system here
            return {"status": "success", "adapter": "your_adapter"}
        logger.warning("[YourAdapter] unknown step '%s'", step_name)
        return {"status": "stub_success", "step": step_name}

    async def rollback(self, step_name: str, payload: dict[str, Any]) -> None:
        logger.info("[YourAdapter] ROLLBACK step='%s'", step_name)
        # undo what activate did
```

Follow the existing adapters for patterns:
- `legacy_5g_emulator_python_adapter.py`: multi-step adapter hitting live NF endpoints via httpx.
- `o2ims_real_adapter.py`: adapter with retry logic and idempotent rollback.

### Step 2: Register the adapter key

File: `src/order_engine/app/api/tmf622.py`

Find `_resolve_adapter_for_step` and add a branch for your key:

```python
from app.adapters.your_adapter import YourAdapter

def _resolve_adapter_for_step(adapter_key: str) -> SouthboundAdapter:
    if adapter_key == "legacy_5g_emulator_python":
        return LegacyFiveGEmulatorAdapter()
    if adapter_key == "o2ims":
        return O2IMSRealAdapter()
    if adapter_key == "your_adapter":
        return YourAdapter()
    raise ValueError(f"Unknown adapter key: {adapter_key!r}")
```

### Step 3: Reference it in rules.yaml

```yaml
  OFF-5G-YOUR-PRODUCT:
    service_category: "5G_YourCategory"
    steps:
      - step_name: your_step
        adapter: your_adapter
        payload_extra:
          some_param: value
          _adapter: your_adapter
```

### Step 4: Add tests

Use `httpx.MockTransport` or `respx` for HTTP-level mocking. See
`src/order_engine/tests/test_o2ims_real_adapter.py` as the template pattern.

---

## How to Add a New AI Observer Collector

The ai_observer polls the stack on a configurable interval and feeds results to
analyzers. Collectors are the data-gathering layer.

### Step 1: Subclass TelemetryCollector

File: `src/ai_observer/app/collectors/base.py`

Create `src/ai_observer/app/collectors/your_collector.py`:

```python
"""Collector for <your data source>."""
import logging
from typing import Any
from app.collectors.base import TelemetryCollector

logger = logging.getLogger(__name__)


class YourCollector(TelemetryCollector):

    async def collect(self) -> dict[str, Any]:
        """Fetch data from your source and return a dict."""
        logger.info("[YourCollector] collecting")
        # call an API, read a file, query a DB, etc.
        return {
            "collector": "your_collector",
            "data": {},
        }
```

### Step 2: Register in app/main.py lifespan

File: `src/ai_observer/app/main.py`

Import your collector and add it to the list of collectors started in the
lifespan context manager, following the pattern used by `legacy standalone 5G emulatorNfCollector`,
`OrderEngineCollector`, and `OtelLogCollector`.

### Step 3: Add tests

See `src/ai_observer/tests/test_collectors.py` for the existing fixture pattern.
Use `respx` or `httpx.MockTransport` for any HTTP calls your collector makes.

---

## How to Add a New Analyzer

Analyzers consume telemetry observations and produce alerts.

### Step 1: Subclass Analyzer

File: `src/ai_observer/app/analyzers/base.py`

Create `src/ai_observer/app/analyzers/your_analyzer.py`:

```python
"""Analyzer for <anomaly type>."""
import logging
from typing import Any
from app.analyzers.base import Analyzer

logger = logging.getLogger(__name__)


class YourAnalyzer(Analyzer):

    def analyze(self, observation: dict[str, Any]) -> list[dict[str, Any]]:
        """Return a list of alert dicts if anomalies are detected, else []."""
        alerts = []
        # inspect observation, generate alerts
        return alerts
```

### Step 2: Register in app/main.py

Add your analyzer instance to the list of analyzers passed to the observation
loop, following the existing pattern.

### Step 3: Add tests

See `src/ai_observer/tests/test_analyzers.py` for the fixture pattern.

---

## How to Add a New Actuator (Phase 2 Closed Loop)

Actuators take autonomous action when the AI observer detects anomalies with
sufficient confidence. Confidence below 0.7 (the default threshold) results in
a proposal only; the actuator does not execute.

### Step 1: Subclass Actuator

File: `src/ai_observer/app/actuators/base.py`

Create `src/ai_observer/app/actuators/your_actuator.py`:

```python
"""Actuator for <remediation action>."""
import logging
from typing import Any
from app.actuators.base import Actuator

logger = logging.getLogger(__name__)


class YourActuator(Actuator):

    def can_act(self, alert: dict[str, Any]) -> bool:
        """Return True if this actuator can handle the alert type."""
        return alert.get("type") == "your_alert_type"

    def propose_action(self, alert: dict[str, Any]) -> dict[str, Any]:
        """Describe what the actuator would do (returned even below threshold)."""
        return {"action": "your_remediation", "target": alert.get("target")}

    async def execute(self, alert: dict[str, Any]) -> dict[str, Any]:
        """Execute the remediation. Called only when confidence >= threshold."""
        logger.info("[YourActuator] executing remediation for %s", alert)
        # call the actual remediation API, restart a service, etc.
        return {"result": "executed"}
```

Set confidence carefully. Anything below 0.7 generates a proposal only and does
not call `execute`. See `src/ai_observer/app/control/action_engine.py` for the
threshold logic.

### Step 2: Register in ActionEngine

File: `src/ai_observer/app/main.py`

Add your actuator to the ActionEngine instantiation.

### Step 3: Add tests

See `src/ai_observer/tests/test_actuators.py` for the pattern.

---

## How to Add a New Storefront Page

The storefront is a Next.js 14 app with the App Router. All routes live under
`src/storefront/src/app/`.

### Step 1: Create the route directory and page file

```bash
mkdir -p src/storefront/src/app/your-route
```

Create `src/storefront/src/app/your-route/page.tsx`:

```typescript
// src/storefront/src/app/your-route/page.tsx
import { getProductOfferings } from "@/lib/api";

export default async function YourRoutePage() {
  const offerings = await getProductOfferings();
  return (
    <main>
      <h1>Your Route</h1>
      {/* render content */}
    </main>
  );
}
```

### Step 2: Use the typed API client

File: `src/storefront/src/lib/api.ts` contains the typed client functions that
call catalog_api (port 8081) and order_engine (port 8080). Use these functions
rather than calling fetch directly. The base URLs are set via environment
variables in `.env.local`.

### Step 3: Build to verify

```bash
cd src/storefront && npm run build
```

Fix any TypeScript errors before committing. The build must pass cleanly.

---

## Coding Standards

All new Python code in `src/` must follow these conventions to match the
existing codebase:

- **Type hints**: all function signatures fully annotated.
- **Async I/O**: use `async`/`await` for all network and database calls.
  Use `httpx.AsyncClient` for outbound HTTP. Do not use `requests` in async
  contexts.
- **Pydantic v2**: request and response models use `model_config`, `model_validator`,
  and `field_validator` (not the v1 `@validator` decorator).
- **Logging**: use `logging.getLogger(__name__)` in every module. Log at INFO
  for normal flow, WARNING for expected-but-notable conditions, ERROR for
  failures that are propagated.
- **Error handling**: raise exceptions rather than returning error dicts from
  adapter `activate()`. The saga coordinator catches exceptions and triggers
  rollback.
- **Rollback idempotency**: `rollback()` must be safe to call multiple times.
  A resource that is already absent (404, missing row) is not an error.
- **No em dashes in comments**: use commas, periods, or parentheses instead.
- **No hardcoded URLs**: all NF base URLs are read from environment variables
  with localhost defaults. See `.env.example` for the full variable list.
