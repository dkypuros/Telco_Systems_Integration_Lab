import importlib.util
import json
import threading
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
SERVER_PATH = ROOT / "modules" / "dashboard_service" / "server.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("modules_dashboard_server", SERVER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_modules_dashboard_cards_include_registered_modules():
    server = load_server_module()

    payload = server.module_cards(host="127.0.0.1")

    ids = {card["id"] for card in payload["cards"]}
    assert payload["ok"] is True
    assert {"modules-dashboard", "lab-chatter-service"} <= ids
    assert payload["module_count"] >= 2
    assert payload["validation_errors"] == []
    assert "not production" in payload["claim_boundary"].lower()


def test_modules_dashboard_marks_active_registered_port():
    server = load_server_module()
    temp_server = server.create_server("127.0.0.1", 0)
    thread = threading.Thread(target=temp_server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = temp_server.server_address
        assert server.port_open(host, port) is True
    finally:
        temp_server.shutdown()
        temp_server.server_close()
        thread.join(timeout=5)


def test_modules_dashboard_http_api_lists_cards():
    server_mod = load_server_module()
    httpd = server_mod.create_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        with urlopen(f"http://{host}:{port}/api/modules", timeout=5) as response:  # noqa: S310 - local test server
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)

    assert payload["ok"] is True
    assert any(card["id"] == "lab-chatter-service" for card in payload["cards"])
