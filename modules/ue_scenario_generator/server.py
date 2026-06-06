#!/usr/bin/env python3
"""Local fixed-command UE/scenario generator for lab chatter."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import socket

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
MODULE_INDEX_PATH = REPO_ROOT / "modules" / "index.json"
MODULE_METADATA_PATH = MODULE_DIR / "module.json"

SCENARIOS: dict[str, dict[str, Any]] = {
    "pdu-session": {
        "label": "PDU Session",
        "command": ["scenario", "pdu-session", "--timeout", "3"],
        "description": "Create UE context, trigger PDU session flow, and append core SCENARIO lines.",
    },
    "radio": {
        "label": "Radio",
        "command": ["scenario", "radio", "--timeout", "3"],
        "description": "Advance the NTN radio trace and append RAN/radio chatter.",
    },
    "oran-overview": {
        "label": "O-RAN Overview",
        "command": ["scenario", "oran-overview", "--timeout", "3"],
        "description": "Query O-RAN gateway/management endpoints for overview chatter.",
    },
    "cu-du": {
        "label": "CU/DU",
        "command": ["scenario", "cu-du", "--timeout", "3"],
        "description": "Exercise CU/DU-oriented lab scenario traffic.",
    },
    "all": {
        "label": "All Scenarios",
        "command": ["scenario", "all", "--timeout", "3"],
        "description": "Run all fixed lab scenarios in sequence.",
    },
}


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


def port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def scenario_list() -> dict[str, Any]:
    return {
        "ok": True,
        "scenarios": [
            {"id": scenario_id, **{key: value for key, value in spec.items() if key != "command"}}
            for scenario_id, spec in SCENARIOS.items()
        ],
        "depends_on": module_metadata().get("depends_on", []),
        "recommended_with": module_metadata().get("recommended_with", []),
        "claim_boundary": module_metadata()["claim_boundary"],
    }


def run_lab_scenario(scenario_id: str, *, timeout: float = 60.0) -> dict[str, Any]:
    spec = SCENARIOS.get(scenario_id)
    if not spec:
        return {"ok": False, "error": f"unknown scenario: {scenario_id}", "known_scenarios": sorted(SCENARIOS)}
    command = [str(REPO_ROOT / "lab"), *spec["command"]]
    result = subprocess.run(  # noqa: S603 - command is selected from fixed SCENARIOS table and shell=False
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "ok": result.returncode == 0,
        "scenario_id": scenario_id,
        "label": spec["label"],
        "returncode": result.returncode,
        "command": ["./lab", *spec["command"]],
        "stdout": result.stdout,
        "stderr": result.stderr,
        "stdout_tail": result.stdout.splitlines()[-40:],
        "stderr_tail": result.stderr.splitlines()[-40:],
        "claim_boundary": module_metadata()["claim_boundary"],
    }


def html_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>UE / Scenario Generator</title>
  <style>
    body { margin: 0; background: #020617; color: #d1fae5; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    header { padding: 1rem; border-bottom: 1px solid #134e4a; background: #03150f; }
    h1 { margin: 0 0 .4rem; color: #22c55e; font-size: 1.2rem; }
    .meta { color: #86efac; }
    main { padding: 1rem; }
    .buttons { display: flex; gap: .65rem; flex-wrap: wrap; margin-bottom: 1rem; }
    button { background: #166534; color: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: .55rem .8rem; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    pre { white-space: pre-wrap; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 1rem; min-height: 18rem; }
    a { color: #86efac; }
  </style>
</head>
<body>
<header>
  <h1>UE / Scenario Generator</h1>
  <div class="meta">Runs fixed <code>./lab scenario</code> commands. Pair with <a href="http://127.0.0.1:8765/" target="_blank" rel="noreferrer">Lab Chatter Service</a>.</div>
</header>
<main>
  <section id="buttons" class="buttons"></section>
  <pre id="output">Loading scenarios…</pre>
</main>
<script>
function escapeText(value) {
  return String(value).replace(/[&<>"']/g, function (char) {
    return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char];
  });
}
async function loadScenarios() {
  const data = await (await fetch('/api/scenarios')).json();
  const buttons = document.getElementById('buttons');
  buttons.innerHTML = data.scenarios.map(function (s) {
    return '<button data-scenario="' + escapeText(s.id) + '">' + escapeText(s.label) + '</button>';
  }).join('');
  buttons.querySelectorAll('button').forEach(function (button) {
    button.addEventListener('click', function () {
      runScenario(button.getAttribute('data-scenario'));
    });
  });
  document.getElementById('output').textContent = 'Ready. Activate Lab Runtime first, then run a scenario.';
}
async function runScenario(id) {
  const out = document.getElementById('output');
  for (const b of document.querySelectorAll('button')) b.disabled = true;
  out.textContent = `Running ${id}…`;
  try {
    const res = await fetch(`/api/scenarios/${encodeURIComponent(id)}`, { method: 'POST' });
    const data = await res.json();
    out.textContent = [
      `ok=${data.ok} scenario=${data.scenario_id} returncode=${data.returncode}`,
      `command=${(data.command || []).join(' ')}`,
      '',
      data.stdout || '',
      data.stderr ? `STDERR:\\n${data.stderr}` : ''
    ].join('\\n');
  } catch (err) {
    out.textContent = String(err);
  } finally {
    for (const b of document.querySelectorAll('button')) b.disabled = false;
  }
}
loadScenarios();
</script>
</body>
</html>"""


class ScenarioRequestHandler(BaseHTTPRequestHandler):
    server_version = "TelcoUeScenarioGenerator/0.1"

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
        if path == "/api/scenarios":
            self.send_json(scenario_list())
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        if self.headers.get("Content-Length"):
            self.rfile.read(int(self.headers["Content-Length"]))
        parts = [part for part in urlparse(self.path).path.split("/") if part]
        if len(parts) == 3 and parts[:2] == ["api", "scenarios"]:
            payload = run_lab_scenario(parts[2])
            self.send_json(payload, status=HTTPStatus.OK if payload.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), ScenarioRequestHandler)


def main(argv: list[str] | None = None) -> int:
    metadata = module_metadata()
    parser = argparse.ArgumentParser(description="Serve fixed UE/scenario generator controls.")
    parser.add_argument("--host", default=metadata.get("default_host", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(metadata.get("default_port", 8766)))
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
    print(f"Serving {module_metadata()['name']} at http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped UE / Scenario Generator.")
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
