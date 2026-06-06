#!/usr/bin/env python3
"""Local product-front-door module for the service-order-to-activation MVP."""

from __future__ import annotations

import argparse
import copy
import html
import importlib.util
import json
import socket
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
MODULE_INDEX_PATH = REPO_ROOT / "modules" / "index.json"
MODULE_METADATA_PATH = MODULE_DIR / "module.json"
ADAPTER_PATH = REPO_ROOT / "adapters" / "3gpp" / "mock_core_activation_adapter.py"
EVIDENCE_BUNDLE_PATH = "traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json"
DEFAULT_PRODUCT_ID = "prod-5g-data-basic"
DEFAULT_CUSTOMER_ID = "customer-demo-001"
DEFAULT_CORRELATION_ID = "corr-product-front-door-demo-0001"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.catalog_api import lookup_product  # noqa: E402
from services.order_engine.order_service import create_product_order  # noqa: E402
from services.orchestration.orchestration_service import orchestrate_activation  # noqa: E402


class ProductFrontDoorError(RuntimeError):
    """Raised when the fixed product-front-door demo path cannot complete."""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def module_metadata() -> dict[str, Any]:
    return load_json(MODULE_METADATA_PATH)


def module_index() -> dict[str, Any]:
    return load_json(MODULE_INDEX_PATH)


def validate_registered_ports(index: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ports: dict[int, str] = {}
    module_ids = {module["id"] for module in index.get("modules", [])}
    for item in index.get("reserved_ports", []):
        port = int(item["port"])
        module_id = str(item["module_id"])
        if module_id not in module_ids:
            errors.append(f"reserved port references unknown module: {module_id}")
        if port in ports:
            errors.append(f"port {port} is registered by both {ports[port]} and {module_id}")
        ports[port] = module_id
        path = REPO_ROOT / str(item["path"])
        if not path.exists():
            errors.append(f"registered module path does not exist: {item['path']}")
    return errors


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return path.name


def load_adapter_module():
    spec = importlib.util.spec_from_file_location("product_front_door_mock_core_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise ProductFrontDoorError(f"unable to load {display_path(ADAPTER_PATH)}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def timeline_step(
    step_id: str,
    label: str,
    status: str,
    detail: str,
    *,
    artifact_path: str | None = None,
    standards_rows: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "label": label,
        "status": status,
        "detail": detail,
        "artifact_path": artifact_path,
        "standards_rows": standards_rows or [],
    }


def planned_gap(step_id: str, label: str, detail: str, standards_rows: list[str] | None = None) -> dict[str, Any]:
    return timeline_step(step_id, label, "planned_gap", detail, standards_rows=standards_rows)


def product_view(*, correlation_id: str = DEFAULT_CORRELATION_ID) -> dict[str, Any]:
    catalog = lookup_product(DEFAULT_PRODUCT_ID, correlation_id=correlation_id)
    product = copy.deepcopy(catalog["product"])
    return {
        "ok": True,
        "correlation_id": correlation_id,
        "product_id": catalog["product_id"],
        "product": product,
        "catalog_metadata": catalog["catalog_metadata"],
        "fixed_action": "activate_demo_product",
        "fixed_action_endpoint": "/api/activate-demo-product",
        "claim_boundary": module_metadata()["claim_boundary"],
    }


def activation_timeline(catalog: dict[str, Any], order_result: dict[str, Any], orchestration: dict[str, Any]) -> list[dict[str, Any]]:
    order = order_result["order"]
    activation_plan = order_result["activation_plan"]
    adapter_response = orchestration["adapter_response"]
    return [
        timeline_step(
            "01_catalog_product_lookup",
            "Product found",
            "complete",
            f"Catalog returned {catalog['product_id']} for the shared correlation_id.",
            artifact_path="services/catalog_api/",
            standards_rows=["TMF620"],
        ),
        timeline_step(
            "02_product_order_create",
            "Order created",
            "complete",
            f"Order {order['id']} reached state {order['state']}.",
            artifact_path="services/order_engine/",
            standards_rows=["TMF622"],
        ),
        timeline_step(
            "03_service_activation_plan",
            "Activation plan generated",
            "complete",
            f"Service {activation_plan['service_id']} maps to {activation_plan['network_action']}.",
            artifact_path="services/order_engine/",
            standards_rows=["TMF641", "TMF640"],
        ),
        timeline_step(
            "04_orchestration_intent_mapping",
            "Orchestration mapped",
            "complete",
            "Subscriber and session intent were mapped for the mock-core adapter.",
            artifact_path="services/orchestration/",
            standards_rows=["3GPP release-baseline"],
        ),
        timeline_step(
            "05_mock_core_activation_adapter",
            "Mock core adapter activated",
            "complete",
            f"Adapter result: {adapter_response['mock_activation_result']} via {adapter_response['mock_core_surface']}.",
            artifact_path="adapters/3gpp/mock_core_activation_adapter.py",
            standards_rows=["3GPP release-baseline"],
        ),
        timeline_step(
            "06_evidence_bundle_record",
            "Evidence bundle linked",
            "complete",
            "Current repeatable MVP evidence bundle is linked for this narrow demo path.",
            artifact_path=EVIDENCE_BUNDLE_PATH,
            standards_rows=["TMF620", "TMF622", "TMF641", "3GPP release-baseline"],
        ),
        planned_gap(
            "07_real_service_inventory",
            "Production service inventory",
            "A real TMF638/TMF640 service inventory and activation facade is not connected to this module yet.",
            ["TMF638", "TMF640"],
        ),
        planned_gap(
            "08_oran_connection",
            "O-RAN / SMO downstream action",
            "This purchase flow does not yet drive O-RAN, SMO, O1, O2, A1, or E2 behavior.",
            ["O-RAN"],
        ),
        planned_gap(
            "09_ocloud_oda_ocp_connection",
            "O-Cloud / ODA / OCP / Kubernetes fulfillment",
            "No O-Cloud, ODA Canvas, OpenShift/OCP, Kubernetes, bare-metal, or remediation path is executed by this MVP.",
            ["O-RAN O2", "ODA", "OCP", "Kubernetes"],
        ),
    ]


def run_demo_activation(
    *,
    correlation_id: str = DEFAULT_CORRELATION_ID,
    customer_id: str = DEFAULT_CUSTOMER_ID,
) -> dict[str, Any]:
    if not correlation_id or not correlation_id.strip():
        raise ProductFrontDoorError("correlation_id is required")
    if not customer_id or not customer_id.strip():
        raise ProductFrontDoorError("customer_id is required")

    adapter = load_adapter_module()
    catalog = lookup_product(DEFAULT_PRODUCT_ID, correlation_id=correlation_id.strip())
    order_result = create_product_order(
        product_id=catalog["product_id"],
        correlation_id=correlation_id.strip(),
        customer_id=customer_id.strip(),
    )
    orchestration = orchestrate_activation(
        order_result["activation_plan"],
        mock_core_adapter=adapter.activate_subscriber_session,
    )
    adapter_response = orchestration["adapter_response"]
    activation_plan = order_result["activation_plan"]

    return {
        "ok": True,
        "correlation_id": correlation_id.strip(),
        "product_id": catalog["product_id"],
        "order_id": order_result["order"]["id"],
        "service_id": activation_plan["service_id"],
        "customer_id": customer_id.strip(),
        "subscriber_intent": activation_plan["subscriber_intent"],
        "session_intent": activation_plan["session_intent"],
        "mock_activation_result": adapter_response["mock_activation_result"],
        "evidence_bundle_path": EVIDENCE_BUNDLE_PATH,
        "timeline": activation_timeline(catalog, order_result, orchestration),
        "claim_boundary": module_metadata()["claim_boundary"],
        "next_validation_step": "Connect a real service inventory, then explicitly add O-RAN/O-Cloud evidence before marking those layers complete.",
    }


def html_page() -> str:
    safe_title = html.escape(module_metadata()["name"])
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{safe_title}</title>
  <style>
    body {{ margin: 0; background: #020617; color: #dbeafe; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    header {{ padding: 1rem; border-bottom: 1px solid #1d4ed8; background: linear-gradient(90deg, #031525, #052e16); }}
    h1 {{ margin: 0 0 .35rem; color: #86efac; font-size: 1.25rem; }}
    .meta {{ color: #bfdbfe; max-width: 76rem; line-height: 1.45; }}
    main {{ padding: 1rem; display: grid; gap: 1rem; }}
    .card {{ background: #0f172a; border: 1px solid #334155; border-radius: 14px; padding: 1rem; }}
    .row {{ display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }}
    .title {{ color: #f8fafc; font-weight: 700; }}
    .muted {{ color: #94a3b8; }}
    button {{ background: #166534; color: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: .65rem .9rem; cursor: pointer; }}
    button:disabled {{ opacity: .6; cursor: wait; }}
    .timeline {{ display: grid; gap: .65rem; }}
    .step {{ border-left: 5px solid #64748b; padding: .65rem .8rem; background: #111827; border-radius: 8px; }}
    .complete {{ border-left-color: #22c55e; }}
    .planned_gap {{ border-left-color: #f59e0b; }}
    code, a {{ color: #93c5fd; }}
    pre {{ white-space: pre-wrap; overflow: auto; max-height: 20rem; background: #020617; padding: .75rem; border-radius: 8px; border: 1px solid #1e293b; }}
  </style>
</head>
<body>
<header>
  <h1>{safe_title}</h1>
  <div class=\"meta\">Local storefront-style module for the basic 5G data MVP. It shows how far this repo can carry product intent today, while marking O-RAN/O-Cloud/OCP/ODA as planned gaps.</div>
</header>
<main>
  <section class=\"card\" id=\"product\">Loading product…</section>
  <section class=\"card\">
    <div class=\"row\">
      <div>
        <div class=\"title\">Fixed MVP action</div>
        <div class=\"muted\">Runs only the registered in-process demo path. No arbitrary shell commands.</div>
      </div>
      <button id=\"activate\" disabled>Activate Demo Product</button>
    </div>
  </section>
  <section class=\"card\">
    <div class=\"title\">Activation timeline</div>
    <div id=\"timeline\" class=\"timeline muted\">Run the fixed action to generate a timeline.</div>
  </section>
  <section class=\"card\">
    <div class=\"title\">Raw result</div>
    <pre id=\"raw\">No run yet.</pre>
  </section>
</main>
<script>
function esc(value) {{
  return String(value).replace(/[&<>\"']/g, function (char) {{
    return {{'&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', "'": '&#39;'}}[char];
  }});
}}
function renderProduct(data) {{
  const product = data.product || {{}};
  document.getElementById('product').innerHTML = [
    '<div class="row"><div><div class="title">' + esc(product.name || data.product_id) + '</div>',
    '<div class="muted">Product ID: <code>' + esc(data.product_id) + '</code></div></div>',
    '<div class="muted">Action: <code>' + esc(data.fixed_action) + '</code></div></div>',
    '<p>' + esc(product.description || 'Basic 5G data service demo product.') + '</p>',
    '<div class="muted">' + esc(data.claim_boundary) + '</div>'
  ].join('');
  document.getElementById('activate').disabled = false;
}}
function renderTimeline(steps) {{
  document.getElementById('timeline').innerHTML = steps.map(function (step) {{
    const artifact = step.artifact_path ? '<div class="muted">artifact: <code>' + esc(step.artifact_path) + '</code></div>' : '';
    const rows = (step.standards_rows || []).length ? '<div class="muted">rows: ' + esc(step.standards_rows.join(', ')) + '</div>' : '';
    return '<div class="step ' + esc(step.status) + '"><div class="title">' + esc(step.label) + ' — ' + esc(step.status) + '</div><div>' + esc(step.detail) + '</div>' + artifact + rows + '</div>';
  }}).join('');
}}
async function loadProduct() {{
  try {{
    const data = await (await fetch('/api/product')).json();
    renderProduct(data);
  }} catch (err) {{
    document.getElementById('product').textContent = String(err);
  }}
}}
async function activateDemoProduct() {{
  const button = document.getElementById('activate');
  button.disabled = true;
  button.textContent = 'Activating…';
  try {{
    const data = await (await fetch('/api/activate-demo-product', {{method: 'POST'}})).json();
    document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
    renderTimeline(data.timeline || []);
  }} catch (err) {{
    document.getElementById('raw').textContent = String(err);
  }} finally {{
    button.disabled = false;
    button.textContent = 'Activate Demo Product';
  }}
}}
document.getElementById('activate').addEventListener('click', activateDemoProduct);
loadProduct();
</script>
</body>
</html>"""


class ProductFrontDoorRequestHandler(BaseHTTPRequestHandler):
    server_version = "TelcoProductFrontDoorModule/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib method name
        return

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_html(self, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        path = urlparse(self.path).path
        if path == "/":
            self.send_html(html_page())
            return
        if path == "/api/module":
            self.send_json(module_metadata())
            return
        if path == "/api/ports":
            index = module_index()
            self.send_json({**index, "validation_errors": validate_registered_ports(index)})
            return
        if path == "/api/product":
            self.send_json(product_view())
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        if self.headers.get("Content-Length"):
            self.rfile.read(int(self.headers["Content-Length"]))
        path = urlparse(self.path).path
        if path == "/api/activate-demo-product":
            try:
                self.send_json(run_demo_activation())
            except (ProductFrontDoorError, ValueError, KeyError) as exc:
                self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)


def port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), ProductFrontDoorRequestHandler)


def main(argv: list[str] | None = None) -> int:
    metadata = module_metadata()
    parser = argparse.ArgumentParser(description="Serve a local product front door over the MVP activation path.")
    parser.add_argument("--host", default=metadata.get("default_host", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(metadata.get("default_port", 8767)))
    args = parser.parse_args(argv)

    errors = validate_registered_ports(module_index())
    if errors:
        for error in errors:
            print(f"module registry error: {error}", file=sys.stderr)
        return 2
    if not port_available(args.host, args.port):
        print(f"port unavailable: {args.host}:{args.port}", file=sys.stderr)
        return 2

    server = create_server(args.host, args.port)
    print(f"Serving {metadata['name']} at http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped product front door.")
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
