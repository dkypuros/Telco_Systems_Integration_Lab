import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
SERVER_PATH = ROOT / "modules" / "lab_chatter_service" / "server.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("lab_chatter_service_server", SERVER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_embedded_scripts_are_valid(html: str) -> None:
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert scripts
    assert r"join('\n')" in html
    node = shutil.which("node")
    if node is None:
        return
    with tempfile.TemporaryDirectory() as tmp_dir:
        for index, script in enumerate(scripts):
            script_path = Path(tmp_dir) / f"script-{index}.js"
            script_path.write_text(script, encoding="utf-8")
            subprocess.run([node, "--check", str(script_path)], check=True, capture_output=True, text=True)


def test_lab_chatter_service_reads_prefixed_lines_from_lab_logs(monkeypatch, tmp_path):
    server = load_server_module()
    monkeypatch.setattr(server.lab_cli, "SERVICE_LOG_DIR", tmp_path)
    (tmp_path / "amf.log").write_text("AMF ready\nSCENARIO OK pdu-session\n", encoding="utf-8")
    (tmp_path / "smf.log").write_text("SMF ready\n", encoding="utf-8")

    payload = server.read_chatter(group="core", lines=1)

    assert payload["ok"] is True
    assert payload["group"] == "core"
    assert payload["entry_count"] == 2
    assert {entry["service_id"] for entry in payload["entries"]} == {"amf", "smf"}
    assert any("SCENARIO OK" in entry["prefixed"] for entry in payload["entries"])
    assert "not formal" in payload["claim_boundary"].lower()


def test_lab_chatter_service_rejects_unknown_group():
    server = load_server_module()

    payload = server.read_chatter(group="does-not-exist", lines=5)

    assert payload["ok"] is False
    assert "unknown service/group" in payload["error"]
    assert "all" in payload["known_groups"]


def test_lab_chatter_service_html_has_valid_embedded_javascript():
    server = load_server_module()

    assert_embedded_scripts_are_valid(server.html_page())


def test_lab_chatter_service_http_api_serves_module_and_chatter(monkeypatch, tmp_path):
    server_mod = load_server_module()
    monkeypatch.setattr(server_mod.lab_cli, "SERVICE_LOG_DIR", tmp_path)
    (tmp_path / "nrf.log").write_text("NRF started\n", encoding="utf-8")

    httpd = server_mod.create_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        with urlopen(f"http://{host}:{port}/", timeout=5) as response:  # noqa: S310 - local test server
            html = response.read().decode("utf-8")
        with urlopen(f"http://{host}:{port}/api/module", timeout=5) as response:  # noqa: S310 - local test server
            module_payload = json.loads(response.read().decode("utf-8"))
        with urlopen(f"http://{host}:{port}/api/chatter?group=nrf&lines=5", timeout=5) as response:  # noqa: S310 - local test server
            chatter_payload = json.loads(response.read().decode("utf-8"))
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)

    assert "Loading chatter" in html
    assert module_payload["id"] == "lab-chatter-service"
    assert chatter_payload["ok"] is True
    assert chatter_payload["entries"][0]["prefixed"] == "[nrf          ] NRF started"
