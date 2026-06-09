#!/usr/bin/env python3
"""Local browser demo for NANDA-style skill import under harness governance."""

from __future__ import annotations

import argparse
import html
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
EXPERIMENT_DIR = REPO_ROOT / "experimental" / "nanda_harness_commerce"
INTENT_PATH = EXPERIMENT_DIR / "fixtures" / "intent.json"
INDEX_PATH = EXPERIMENT_DIR / "fixtures" / "nanda_index.json"
POLICY_PATH = EXPERIMENT_DIR / "fixtures" / "harness_policy.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experimental.nanda_harness_commerce.simulator import build_plan, load_json  # noqa: E402


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def module_metadata() -> dict[str, Any]:
    return read_json(MODULE_METADATA_PATH)


def module_index() -> dict[str, Any]:
    return read_json(MODULE_INDEX_PATH)


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


def demo_plan() -> dict[str, Any]:
    return build_plan(load_json(INTENT_PATH), load_json(INDEX_PATH), load_json(POLICY_PATH))


def demo_payload() -> dict[str, Any]:
    plan = demo_plan()
    accepted = plan.get("verified_imports", [])
    rejected = plan.get("rejected_candidates", [])
    return {
        "ok": True,
        "module_id": module_metadata()["id"],
        "claim_boundary": module_metadata()["claim_boundary"],
        "flow": [
            {"step": "human_intent", "label": "Human intent", "status": "complete", "detail": "A human asks for a verified telco security audit skill."},
            {"step": "nanda_discovery", "label": "NANDA-style discovery", "status": "complete", "detail": "The demo reads a local NANDA-style index snapshot instead of calling a live registry."},
            {"step": "agentfacts_verification", "label": "AgentFacts-like verification", "status": "complete", "detail": "Candidate records are checked for issuer, signature presence, protocol, evidence, quality, risk, budget, audit, and revocation support."},
            {"step": "harness_gate", "label": "Harness governance gate", "status": "complete", "detail": f"{len(accepted)} candidate passed; {len(rejected)} candidates were rejected with reasons."},
            {"step": "disabled_import", "label": "Disabled import prepared", "status": "awaiting_human_approval", "detail": "The accepted skill is prepared as a disabled local binding and cannot run yet."},
            {"step": "human_approval", "label": "Human approval required", "status": "blocked_by_design", "detail": "A human must explicitly approve before the imported skill is enabled."},
        ],
        "plan": plan,
    }


def html_page() -> str:
    metadata = module_metadata()
    safe_title = html.escape(metadata["name"])
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{safe_title}</title>
  <style>
    body {{ margin: 0; background: #020617; color: #e0f2fe; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    header {{ padding: 1rem; border-bottom: 1px solid #0891b2; background: linear-gradient(90deg, #082f49, #172554, #312e81); }}
    h1 {{ margin: 0 0 .35rem; color: #67e8f9; font-size: 1.25rem; }}
    .meta {{ color: #bae6fd; max-width: 82rem; line-height: 1.45; }}
    main {{ padding: 1rem; display: grid; gap: 1rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr)); gap: .8rem; }}
    .card {{ background: #0f172a; border: 1px solid #334155; border-radius: 14px; padding: 1rem; }}
    .step {{ border-left: 5px solid #38bdf8; }}
    .awaiting_human_approval {{ border-left-color: #f59e0b; }}
    .blocked_by_design {{ border-left-color: #fb7185; }}
    .title {{ color: #f8fafc; font-weight: 700; }}
    .muted {{ color: #94a3b8; }}
    .good {{ color: #86efac; }}
    .bad {{ color: #fda4af; }}
    button {{ background: #155e75; color: #ecfeff; border: 1px solid #22d3ee; border-radius: 8px; padding: .65rem .9rem; cursor: pointer; }}
    button:disabled {{ opacity: .6; cursor: wait; }}
    code, a {{ color: #93c5fd; }}
    pre {{ white-space: pre-wrap; overflow: auto; max-height: 24rem; background: #020617; padding: .75rem; border-radius: 8px; border: 1px solid #1e293b; }}
  </style>
</head>
<body>
<header>
  <h1>{safe_title}</h1>
  <div class=\"meta\">Offline demo of the control-plane idea: human intent enters the harness, NANDA-style discovery returns AgentFacts-like records, policy rejects unsafe candidates, and the only accepted skill stays disabled until human approval.</div>
</header>
<main>
  <section class=\"card\">
    <div class=\"title\">Demo action</div>
    <p class=\"muted\">Runs deterministic fixtures only. No live NANDA lookup, no remote agent, no payment, no production change.</p>
    <button id=\"run\">Run NANDA Skill Import Demo</button>
  </section>
  <section class=\"grid\" id=\"flow\"></section>
  <section class=\"card\" id=\"summary\"><span class=\"muted\">Run the demo to see the import decision.</span></section>
  <section class=\"card\">
    <div class=\"title\">Raw plan</div>
    <pre id=\"raw\">No run yet.</pre>
  </section>
</main>
<script>
function esc(value) {{
  return String(value).replace(/[&<>\"']/g, function (char) {{
    return {{'&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', "'": '&#39;'}}[char];
  }});
}}
function render(data) {{
  document.getElementById('flow').innerHTML = data.flow.map(function (step) {{
    return '<div class="card step ' + esc(step.status) + '"><div class="title">' + esc(step.label) + '</div><div class="muted">' + esc(step.status) + '</div><p>' + esc(step.detail) + '</p></div>';
  }}).join('');
  const plan = data.plan || {{}};
  const accepted = plan.verified_imports || [];
  const rejected = plan.rejected_candidates || [];
  const first = accepted[0] || {{}};
  document.getElementById('summary').innerHTML = [
    '<div class="title">Decision: <span class="good">' + esc(plan.status || 'unknown') + '</span></div>',
    '<p>Accepted disabled imports: <strong>' + accepted.length + '</strong></p>',
    '<p>Rejected candidates: <strong>' + rejected.length + '</strong></p>',
    first.agent_id ? '<p>Prepared skill: <code>' + esc(first.agent_id) + '</code></p>' : '',
    '<p class="muted">Boundary: ' + esc(data.claim_boundary) + '</p>'
  ].join('');
  document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
}}
async function runDemo() {{
  const button = document.getElementById('run');
  button.disabled = true;
  button.textContent = 'Running…';
  try {{
    const response = await fetch('/api/run-demo', {{method: 'POST'}});
    render(await response.json());
  }} catch (err) {{
    document.getElementById('raw').textContent = String(err);
  }} finally {{
    button.disabled = false;
    button.textContent = 'Run NANDA Skill Import Demo';
  }}
}}
document.getElementById('run').addEventListener('click', runDemo);
fetch('/api/demo-plan').then(r => r.json()).then(data => {{
  document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
}}).catch(() => {{}});
</script>
</body>
</html>"""


class NandaSkillImportRequestHandler(BaseHTTPRequestHandler):
    server_version = "TelcoNandaSkillImportDemo/0.1"

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
        if path == "/api/demo-plan":
            self.send_json(demo_payload())
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        if self.headers.get("Content-Length"):
            self.rfile.read(int(self.headers["Content-Length"]))
        path = urlparse(self.path).path
        if path == "/api/run-demo":
            self.send_json(demo_payload())
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
    return ThreadingHTTPServer((host, port), NandaSkillImportRequestHandler)


def main(argv: list[str] | None = None) -> int:
    metadata = module_metadata()
    parser = argparse.ArgumentParser(description="Serve the local NANDA skill import demo.")
    parser.add_argument("--host", default=metadata.get("default_host", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(metadata.get("default_port", 8768)))
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
        print("\nStopped NANDA skill import demo.")
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
