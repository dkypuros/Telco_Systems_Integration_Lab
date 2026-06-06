import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SERVER_PATH = ROOT / "modules" / "product_front_door" / "server.py"
INDEX_PATH = ROOT / "modules" / "index.json"

PRIVATE_PATH_RE = re.compile(r"/(Users|home)/[^\s\"']+")


def load_server_module():
    spec = importlib.util.spec_from_file_location("product_front_door_server", SERVER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from flatten_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from flatten_strings(item)


def assert_public_safe(payload: dict):
    values = "\n".join(flatten_strings(payload))
    assert not PRIVATE_PATH_RE.search(values)
    assert "not formal" in values.lower()


def assert_embedded_scripts_are_valid(html: str) -> None:
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert scripts
    assert "activate-demo-product" in html
    assert "O-RAN/O-Cloud" in html
    assert "onclick" not in html
    node = shutil.which("node")
    if node is None:
        return
    with tempfile.TemporaryDirectory() as tmp_dir:
        for index, script in enumerate(scripts):
            script_path = Path(tmp_dir) / f"script-{index}.js"
            script_path.write_text(script, encoding="utf-8")
            subprocess.run([node, "--check", str(script_path)], check=True, capture_output=True, text=True)


def test_product_front_door_is_registered_with_unique_port():
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    ports = [item["port"] for item in index["reserved_ports"]]
    module = next(item for item in index["modules"] if item["id"] == "product-front-door")
    reserved = next(item for item in index["reserved_ports"] if item["module_id"] == "product-front-door")

    assert len(ports) == len(set(ports))
    assert reserved["port"] == 8767
    assert module["default_port"] == 8767
    assert module["entrypoint"] == "python3 modules/product_front_door/server.py"
    assert "lab-chatter-service" in module["recommended_with"]


def test_product_front_door_metadata_declares_boundary_and_recommendations():
    server = load_server_module()
    metadata = server.module_metadata()

    assert metadata["id"] == "product-front-door"
    assert metadata["default_port"] == 8767
    assert "lab-chatter-service" in metadata["recommended_with"]
    assert "not formal" in metadata["claim_boundary"].lower()
    assert "O-Cloud" in metadata["claim_boundary"]


def test_product_view_returns_basic_product_without_private_paths():
    server = load_server_module()

    payload = server.product_view(correlation_id="corr-unit-product-front-door")

    assert payload["ok"] is True
    assert payload["product_id"] == "prod-5g-data-basic"
    assert payload["fixed_action"] == "activate_demo_product"
    assert payload["fixed_action_endpoint"] == "/api/activate-demo-product"
    assert_public_safe(payload)


def test_demo_activation_runs_fixed_mvp_path_and_marks_downstream_gaps():
    server = load_server_module()

    payload = server.run_demo_activation(correlation_id="corr-unit-product-front-door", customer_id="customer-demo-001")

    assert payload["ok"] is True
    assert payload["product_id"] == "prod-5g-data-basic"
    assert payload["order_id"].startswith("order-")
    assert payload["service_id"].startswith("svc-")
    assert payload["mock_activation_result"] == "activated"
    statuses = {step["step_id"]: step["status"] for step in payload["timeline"]}
    details = {step["step_id"]: step["detail"] for step in payload["timeline"]}
    assert statuses["01_catalog_product_lookup"] == "complete"
    assert statuses["05_mock_core_activation_adapter"] == "complete"
    assert statuses["08_oran_connection"] == "planned_gap"
    assert statuses["09_ocloud_oda_ocp_connection"] == "planned_gap"
    assert "ODA Canvas" in details["09_ocloud_oda_ocp_connection"]
    assert "OpenShift/OCP" in details["09_ocloud_oda_ocp_connection"]
    assert payload["evidence_bundle_path"] == "traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json"
    assert_public_safe(payload)


def test_demo_activation_requires_fixed_public_identifiers():
    server = load_server_module()

    try:
        server.run_demo_activation(correlation_id="", customer_id="customer-demo-001")
    except server.ProductFrontDoorError as exc:
        assert "correlation_id is required" in str(exc)
    else:
        raise AssertionError("empty correlation_id should be rejected")


def test_product_front_door_html_has_valid_embedded_javascript():
    server = load_server_module()

    assert_embedded_scripts_are_valid(server.html_page())


def test_product_front_door_http_api_serves_product_and_activation():
    server_mod = load_server_module()
    httpd = server_mod.create_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        with urlopen(f"http://{host}:{port}/", timeout=5) as response:  # noqa: S310 - local test server
            html = response.read().decode("utf-8")
        with urlopen(f"http://{host}:{port}/api/product", timeout=5) as response:  # noqa: S310 - local test server
            product_payload = json.loads(response.read().decode("utf-8"))
        request = Request(f"http://{host}:{port}/api/activate-demo-product", data=b"", method="POST")
        with urlopen(request, timeout=10) as response:  # noqa: S310 - local test server
            activation_payload = json.loads(response.read().decode("utf-8"))
        try:
            with urlopen(f"http://{host}:{port}/api/not-real", timeout=5) as response:  # noqa: S310 - local test server
                response.read()
        except HTTPError as exc:
            not_found_status = exc.code
        else:
            not_found_status = 200
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)

    assert "Product Front Door" in html
    assert product_payload["product_id"] == "prod-5g-data-basic"
    assert activation_payload["mock_activation_result"] == "activated"
    assert any(step["status"] == "planned_gap" for step in activation_payload["timeline"])
    assert not_found_status == 404
