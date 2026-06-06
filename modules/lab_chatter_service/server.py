#!/usr/bin/env python3
"""Local HTTP module for viewing lab chatter logs.

This intentionally uses only the Python standard library. It is an example
visual/service module over the existing ``./lab chatter`` surface, not a new
runtime dependency for the telco lab.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import socket
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
MODULE_INDEX_PATH = REPO_ROOT / "modules" / "index.json"
MODULE_METADATA_PATH = MODULE_DIR / "module.json"
LAB_CLI_PATH = REPO_ROOT / "scripts" / "lab_cli.py"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_lab_cli():
    spec = importlib.util.spec_from_file_location("telco_lab_cli_for_chatter_module", LAB_CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {LAB_CLI_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lab_cli = load_lab_cli()


def module_metadata() -> dict[str, Any]:
    return load_json(MODULE_METADATA_PATH)


def module_index() -> dict[str, Any]:
    return load_json(MODULE_INDEX_PATH)


def validate_registered_ports(index: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ports: dict[int, str] = {}
    for item in index.get("reserved_ports", []):
        port = int(item["port"])
        module_id = str(item["module_id"])
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


def service_group_names() -> list[str]:
    groups = sorted(lab_cli.CHATTER_GROUPS)
    services = sorted(service["id"] for service in lab_cli.SERVICE_INVENTORY)
    return groups + services


def read_chatter(group: str = "all", lines: int = 80) -> dict[str, Any]:
    try:
        lines = max(0, min(int(lines), 500))
    except (TypeError, ValueError):
        lines = 80

    paths = lab_cli.selected_log_paths(group)
    if not paths:
        return {
            "ok": False,
            "error": f"unknown service/group: {group}",
            "known_groups": service_group_names(),
            "entries": [],
        }

    entries: list[dict[str, str]] = []
    for service_id, path in paths:
        for line in lab_cli.tail_lines(path, lines):
            entries.append(
                {
                    "service_id": service_id,
                    "line": line,
                    "prefixed": f"[{service_id:<13}] {line}",
                    "source_path": display_path(path),
                }
            )

    return {
        "ok": True,
        "group": group,
        "requested_lines_per_service": lines,
        "log_dir": display_path(lab_cli.SERVICE_LOG_DIR),
        "entry_count": len(entries),
        "entries": entries,
        "note": "Run ./lab up and ./lab scenario <name> to generate more chatter.",
        "claim_boundary": module_metadata()["claim_boundary"],
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
    body {{ margin: 0; background: #020617; color: #d1fae5; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    header {{ padding: 1rem; border-bottom: 1px solid #134e4a; background: #03150f; }}
    h1 {{ margin: 0 0 .35rem; color: #22c55e; font-size: 1.1rem; }}
    .controls, .meta {{ display: flex; gap: .75rem; flex-wrap: wrap; align-items: center; }}
    .meta {{ color: #86efac; font-size: .85rem; margin-top: .35rem; }}
    select, input, button {{ background: #052e16; color: #dcfce7; border: 1px solid #16a34a; padding: .35rem .5rem; }}
    main {{ padding: 1rem; }}
    pre {{ white-space: pre-wrap; line-height: 1.35; margin: 0; }}
    .empty {{ color: #fde68a; }}
    .error {{ color: #fecaca; }}
  </style>
</head>
<body>
<header>
  <h1>{safe_title}</h1>
  <div class=\"controls\">
    <label>group <select id=\"group\"><option>all</option><option>core</option><option>ran</option><option>oran</option><option>radio</option></select></label>
    <label>lines <input id=\"lines\" type=\"number\" min=\"0\" max=\"500\" value=\"80\" /></label>
    <button id=\"refresh\">refresh</button>
  </div>
  <div class=\"meta\">Local-only viewer over build_logs/services/*.log. Not formal conformance evidence.</div>
</header>
<main><pre id=\"output\" class=\"empty\">Loading chatter…</pre></main>
<script>
async function loadChatter() {{
  const group = document.getElementById('group').value;
  const lines = document.getElementById('lines').value;
  const out = document.getElementById('output');
  try {{
    const res = await fetch(`/api/chatter?group=${{encodeURIComponent(group)}}&lines=${{encodeURIComponent(lines)}}`);
    const data = await res.json();
    if (!data.ok) {{ out.className = 'error'; out.textContent = data.error || 'unknown error'; return; }}
    out.className = data.entries.length ? '' : 'empty';
    out.textContent = data.entries.length ? data.entries.map(e => e.prefixed).join('\n') : 'No lab chatter found yet. Run ./lab up or ./lab scenario <name>.';
  }} catch (err) {{
    out.className = 'error'; out.textContent = String(err);
  }}
}}
document.getElementById('refresh').addEventListener('click', loadChatter);
document.getElementById('group').addEventListener('change', loadChatter);
setInterval(loadChatter, 2000);
loadChatter();
</script>
</body>
</html>"""


class ChatterRequestHandler(BaseHTTPRequestHandler):
    server_version = "TelcoLabChatterModule/0.1"

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
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_html(html_page())
            return
        if parsed.path == "/api/module":
            self.send_json(module_metadata())
            return
        if parsed.path == "/api/ports":
            index = module_index()
            payload = {**index, "validation_errors": validate_registered_ports(index)}
            self.send_json(payload)
            return
        if parsed.path == "/api/chatter":
            query = parse_qs(parsed.query)
            group = query.get("group", ["all"])[0]
            lines = query.get("lines", ["80"])[0]
            payload = read_chatter(group=group, lines=int(lines) if str(lines).isdigit() else 80)
            status = HTTPStatus.OK if payload.get("ok") else HTTPStatus.NOT_FOUND
            self.send_json(payload, status=status)
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
    return ThreadingHTTPServer((host, port), ChatterRequestHandler)


def main(argv: list[str] | None = None) -> int:
    metadata = module_metadata()
    parser = argparse.ArgumentParser(description="Serve a local web/API view over ./lab chatter logs.")
    parser.add_argument("--host", default=metadata.get("default_host", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(metadata.get("default_port", 8765)))
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
        print("\nStopped lab chatter service.")
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
