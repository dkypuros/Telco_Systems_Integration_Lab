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
SERVER_PATH = ROOT / "modules" / "ue_scenario_generator" / "server.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("ue_scenario_generator_server", SERVER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_embedded_scripts_are_valid(html: str) -> None:
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert scripts
    assert r"join('\n')" in html
    assert "data-scenario" in html
    assert "onclick" not in html
    node = shutil.which("node")
    if node is None:
        return
    with tempfile.TemporaryDirectory() as tmp_dir:
        for index, script in enumerate(scripts):
            script_path = Path(tmp_dir) / f"script-{index}.js"
            script_path.write_text(script, encoding="utf-8")
            subprocess.run([node, "--check", str(script_path)], check=True, capture_output=True, text=True)


def test_scenario_generator_lists_fixed_scenarios_and_dependencies():
    server = load_server_module()

    payload = server.scenario_list()

    ids = {scenario["id"] for scenario in payload["scenarios"]}
    assert {"pdu-session", "radio", "oran-overview", "cu-du", "all"} == ids
    assert payload["depends_on"] == ["lab-runtime"]
    assert payload["recommended_with"] == ["lab-chatter-service"]
    assert "not formal" in payload["claim_boundary"].lower()


def test_scenario_generator_runs_only_fixed_lab_scenario_commands(monkeypatch):
    server = load_server_module()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="scenario ok\n", stderr="")

    monkeypatch.setattr(server.subprocess, "run", fake_run)

    payload = server.run_lab_scenario("pdu-session")

    assert payload["ok"] is True
    assert payload["command"] == ["./lab", "scenario", "pdu-session", "--timeout", "3"]
    assert calls[0][0] == [str(ROOT / "lab"), "scenario", "pdu-session", "--timeout", "3"]
    assert "shell" not in calls[0][1]


def test_scenario_generator_rejects_unknown_scenario_before_subprocess(monkeypatch):
    server = load_server_module()

    def should_not_run(*args, **kwargs):
        raise AssertionError("subprocess must not run for an unknown scenario")

    monkeypatch.setattr(server.subprocess, "run", should_not_run)

    payload = server.run_lab_scenario("../../bad")

    assert payload["ok"] is False
    assert "unknown scenario" in payload["error"]


def test_scenario_generator_html_has_valid_embedded_javascript():
    server = load_server_module()

    assert_embedded_scripts_are_valid(server.html_page())


def test_scenario_generator_http_api(monkeypatch):
    server_mod = load_server_module()

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="radio ok\n", stderr="")

    monkeypatch.setattr(server_mod.subprocess, "run", fake_run)
    httpd = server_mod.create_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address
        with urlopen(f"http://{host}:{port}/", timeout=5) as response:  # noqa: S310 - local test server
            html = response.read().decode("utf-8")
        with urlopen(f"http://{host}:{port}/api/scenarios", timeout=5) as response:  # noqa: S310 - local test server
            list_payload = json.loads(response.read().decode("utf-8"))
        request = Request(f"http://{host}:{port}/api/scenarios/radio", data=b"", method="POST")
        with urlopen(request, timeout=5) as response:  # noqa: S310 - local test server
            run_payload = json.loads(response.read().decode("utf-8"))
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)

    assert "Loading scenarios" in html
    assert list_payload["ok"] is True
    assert run_payload["ok"] is True
    assert run_payload["scenario_id"] == "radio"
    assert "radio ok" in run_payload["stdout"]
