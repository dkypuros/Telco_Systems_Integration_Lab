import importlib.util
import json
import socket
import threading
from pathlib import Path
from urllib.request import Request, urlopen

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


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def fake_index_for_port(port: int) -> dict:
    return {
        "schema_version": "1.0",
        "purpose": "test registry",
        "claim_boundary": "Local test registry only; not formal conformance.",
        "reserved_ports": [
            {
                "port": port,
                "module_id": "test-dashboard-module",
                "path": "modules/dashboard_service/",
                "description": "Test dashboard module on a temporary port.",
            }
        ],
        "modules": [
            {
                "id": "test-dashboard-module",
                "name": "Test Dashboard Module",
                "path": "modules/dashboard_service/",
                "default_port": port,
                "entrypoint": f"python3 modules/dashboard_service/server.py --host 127.0.0.1 --port {port}",
                "surface": "local_http",
                "status": "test",
            }
        ],
    }


def test_dashboard_activation_starts_registered_entrypoint_and_stop_only_managed_pid(monkeypatch, tmp_path):
    server = load_server_module()
    port = free_port()
    monkeypatch.setattr(server, "module_index", lambda: fake_index_for_port(port))
    monkeypatch.setattr(server, "MODULE_STATE_PATH", tmp_path / "modules_dashboard.json")
    monkeypatch.setattr(server, "MODULE_LOG_DIR", tmp_path / "module_logs")

    started = server.activate_module("test-dashboard-module", wait_seconds=5)
    try:
        assert started["ok"] is True, started
        assert started["status"] == "started"
        assert started["managed"] is True
        assert server.port_open("127.0.0.1", port) is True
        cards = server.module_cards(host="127.0.0.1")
        card = cards["cards"][0]
        assert card["activated"] is True
        assert card["managed"] is True
    finally:
        stopped = server.stop_module("test-dashboard-module")

    assert stopped["ok"] is True, stopped
    assert stopped["status"] in {"stopped", "already_stopped"}


def test_dashboard_activation_refuses_unregistered_or_unsafe_entrypoint(monkeypatch, tmp_path):
    server = load_server_module()
    unsafe = fake_index_for_port(free_port())
    unsafe["modules"][0]["entrypoint"] = "bash -c whoami"
    monkeypatch.setattr(server, "module_index", lambda: unsafe)
    monkeypatch.setattr(server, "MODULE_STATE_PATH", tmp_path / "modules_dashboard.json")

    result = server.activate_module("test-dashboard-module")

    assert result["ok"] is False
    assert "python" in result["error"]


def test_dashboard_http_post_can_activate_and_stop_registered_module(monkeypatch, tmp_path):
    server_mod = load_server_module()
    managed_port = free_port()
    monkeypatch.setattr(server_mod, "module_index", lambda: fake_index_for_port(managed_port))
    monkeypatch.setattr(server_mod, "MODULE_STATE_PATH", tmp_path / "modules_dashboard.json")
    monkeypatch.setattr(server_mod, "MODULE_LOG_DIR", tmp_path / "module_logs")
    httpd = server_mod.create_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        activate_req = Request(
            f"http://{host}:{port}/api/modules/test-dashboard-module/activate",
            data=b"",
            method="POST",
        )
        with urlopen(activate_req, timeout=10) as response:  # noqa: S310 - local test server
            activate_payload = json.loads(response.read().decode("utf-8"))
        assert activate_payload["ok"] is True, activate_payload

        stop_req = Request(
            f"http://{host}:{port}/api/modules/test-dashboard-module/stop",
            data=b"",
            method="POST",
        )
        with urlopen(stop_req, timeout=10) as response:  # noqa: S310 - local test server
            stop_payload = json.loads(response.read().decode("utf-8"))
    finally:
        # Best effort cleanup if assertion fails before POST /stop.
        try:
            server_mod.stop_module("test-dashboard-module")
        except Exception:
            pass
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)

    assert stop_payload["ok"] is True, stop_payload
