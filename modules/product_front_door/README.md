# Product Front Door

Local no-dependency storefront-style module for the first service-order-to-activation MVP product. It lets an operator view the basic 5G data product and run one fixed demo activation path from the browser.

## Dependencies

Required:

- Python 3 from the local development environment.
- Repository root as the working directory.
- Registered module port `8767` from `modules/index.json`.
- Existing MVP callable services:
  - `services/catalog_api/`
  - `services/order_engine/`
  - `services/orchestration/`
  - `adapters/3gpp/mock_core_activation_adapter.py`

Recommended module stack:

```bash
./lab up
python3 modules/dashboard_service/server.py
python3 modules/product_front_door/server.py
python3 modules/lab_chatter_service/server.py
./lab down
```

The MVP activation action runs in-process against the lab-owned functional-smoke services. It does not require live O-RAN, O-Cloud, OCP, ODA Canvas, or Kubernetes services.

`module.json` intentionally has no hard `depends_on` entry because this module
does not require `./lab up` or a live runtime daemon to run the fixed MVP action.
It uses existing in-repository callable services in process. Lab Runtime, Chatter,
and UE / Scenario Generator remain recommended companion views for broader demos.

## Run

From the repository root:

```bash
python3 modules/product_front_door/server.py
```

Then open:

```text
http://127.0.0.1:8767/
```

Useful JSON endpoints:

```text
http://127.0.0.1:8767/api/module
http://127.0.0.1:8767/api/ports
http://127.0.0.1:8767/api/product
POST http://127.0.0.1:8767/api/activate-demo-product
```

Optional host/port override:

```bash
python3 modules/product_front_door/server.py --host 127.0.0.1 --port 8767
```

## Stop

Press `Ctrl-C` in the terminal running the module, or use the Modules Dashboard Stop button if the dashboard started it.

This module does not own the telco services. Use the normal lab lifecycle to stop the runtime services when finished:

```bash
./lab down
```

## Special commands

Use this module alongside the current module workspace:

```bash
python3 modules/dashboard_service/server.py
# activate Product Front Door from the dashboard
./lab chatter all --follow
./lab scenario pdu-session
```

The Product Front Door action runs the fixed service-order-to-activation MVP and links the current evidence bundle path. Use Lab Chatter and UE / Scenario Generator as adjacent views for network-side lab activity; they are not yet downstream of this product purchase flow.

## Boundary

This module is a local product-front-door demo. It can show that the existing MVP spine carries `prod-5g-data-basic` through catalog lookup, order creation, activation planning, orchestration, mock 3GPP adapter activation, and evidence linkage.

It does **not** prove formal TM Forum CTK conformance, formal 3GPP protocol conformance, O-RAN behavior, O-Cloud/O2/OCP execution, ODA Canvas deployment, Kubernetes fulfillment, production service inventory, billing, authentication, or real customer commerce.
