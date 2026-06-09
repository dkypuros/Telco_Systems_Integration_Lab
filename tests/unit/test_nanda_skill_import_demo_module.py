import importlib.util
import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SERVER_PATH = ROOT / "modules" / "nanda_skill_import_demo" / "server.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("nanda_skill_import_demo_server", SERVER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nanda_skill_import_demo_payload_shows_disabled_import_and_rejections():
    server = load_server_module()

    payload = server.demo_payload()
    plan = payload["plan"]

    assert payload["ok"] is True
    assert plan["status"] == "awaiting_human_approval"
    assert len(plan["verified_imports"]) == 1
    assert plan["verified_imports"][0]["enabled"] is False
    assert plan["verified_imports"][0]["human_approval_required"] is True
    assert len(plan["rejected_candidates"]) == 2
    assert "not formal NANDA interoperability" in payload["claim_boundary"]


def test_nanda_skill_import_demo_http_api_runs_demo():
    server_mod = load_server_module()
    httpd = server_mod.create_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        req = Request(f"http://{host}:{port}/api/run-demo", data=b"", method="POST")
        with urlopen(req, timeout=5) as response:  # noqa: S310 - local test server
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)

    assert payload["ok"] is True
    assert payload["plan"]["status"] == "awaiting_human_approval"
    assert any(step["step"] == "disabled_import" for step in payload["flow"])
