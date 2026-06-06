#!/usr/bin/env python3
"""Local dashboard for registered visual/service modules.

The dashboard can activate registered modules, but it is intentionally not an
arbitrary shell runner. It starts only entrypoints listed in ``modules/index.json``
and only stops PIDs it previously recorded under ``.lab/state``.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import shlex
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
MODULE_INDEX_PATH = REPO_ROOT / "modules" / "index.json"
MODULE_METADATA_PATH = MODULE_DIR / "module.json"
CONTROL_DIR = REPO_ROOT / ".lab" / "state"
MODULE_STATE_PATH = CONTROL_DIR / "modules_dashboard.json"
MODULE_LOG_DIR = REPO_ROOT / "build_logs" / "modules"
MANAGER_OWNER = "modules-dashboard"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def module_metadata() -> dict[str, Any]:
    return load_json(MODULE_METADATA_PATH)


def module_index() -> dict[str, Any]:
    return load_json(MODULE_INDEX_PATH)


def load_module_state() -> dict[str, Any]:
    if not MODULE_STATE_PATH.exists():
        return {"schema_version": "1.0", "owner": MANAGER_OWNER, "modules": {}}
    try:
        state = load_json(MODULE_STATE_PATH)
    except Exception:
        return {"schema_version": "1.0", "owner": MANAGER_OWNER, "modules": {}}
    state.setdefault("schema_version", "1.0")
    state.setdefault("owner", MANAGER_OWNER)
    state.setdefault("modules", {})
    return state


def save_module_state(state: dict[str, Any]) -> None:
    CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    MODULE_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


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


def port_open(host: str, port: int, timeout: float = 0.15) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def registered_module(module_id: str) -> dict[str, Any] | None:
    return next((module for module in module_index().get("modules", []) if module.get("id") == module_id), None)


def reserved_port_for(module_id: str) -> int | None:
    reserved = next((item for item in module_index().get("reserved_ports", []) if item.get("module_id") == module_id), None)
    if reserved:
        return int(reserved["port"])
    module = registered_module(module_id)
    if module and module.get("default_port"):
        return int(module["default_port"])
    return None


def is_lab_lifecycle_module(module: dict[str, Any] | None) -> bool:
    return bool(module and module.get("surface") == "lab_lifecycle")


def run_lab_command(*args: str, timeout: float = 120.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(REPO_ROOT / "lab"), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def lab_runtime_report() -> dict[str, Any]:
    result = run_lab_command("services", "--json", timeout=20.0)
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {}
    ready = int(payload.get("ready", 0) or 0)
    total = int(payload.get("total", 0) or 0)
    return {
        "ok": result.returncode == 0 or bool(payload),
        "ready": ready,
        "total": total,
        "activated": ready > 0,
        "all_ready": bool(payload.get("all_ready")),
        "status_label": "activated" if ready > 0 else "registered",
        "raw": payload,
        "returncode": result.returncode,
    }


def activate_lab_runtime(module_id: str) -> dict[str, Any]:
    result = run_lab_command("up", timeout=180.0)
    report = lab_runtime_report()
    return {
        "ok": result.returncode == 0,
        "module_id": module_id,
        "status": "started" if result.returncode == 0 else "start_failed",
        "ready": report["ready"],
        "total": report["total"],
        "stdout_tail": result.stdout.splitlines()[-20:],
        "stderr_tail": result.stderr.splitlines()[-20:],
    }


def stop_lab_runtime(module_id: str) -> dict[str, Any]:
    result = run_lab_command("down", timeout=120.0)
    return {
        "ok": result.returncode == 0,
        "module_id": module_id,
        "status": "stopped" if result.returncode == 0 else "stop_failed",
        "stdout_tail": result.stdout.splitlines()[-20:],
        "stderr_tail": result.stderr.splitlines()[-20:],
    }


def safe_entrypoint_args(entrypoint: str) -> list[str]:
    """Return a safe argv list for a registered Python module entrypoint.

    The registry stores friendly commands such as
    ``python3 modules/lab_chatter_service/server.py``. The dashboard converts the
    Python executable to the current interpreter and verifies that the target
    script lives under this repo's ``modules/`` tree.
    """

    parts = shlex.split(entrypoint)
    if len(parts) < 2:
        raise ValueError("entrypoint must include a Python executable and script path")
    executable = parts[0]
    if Path(executable).name not in {"python", "python3", Path(sys.executable).name}:
        raise ValueError("module entrypoint must use python/python3")
    script = (REPO_ROOT / parts[1]).resolve()
    modules_root = (REPO_ROOT / "modules").resolve()
    if not script.exists() or not script.is_file():
        raise ValueError(f"module script does not exist: {parts[1]}")
    if not script.is_relative_to(modules_root):
        raise ValueError("module script must live under modules/")
    return [sys.executable, str(script), *parts[2:]]


def managed_record(module_id: str) -> dict[str, Any] | None:
    state = load_module_state()
    record = state.get("modules", {}).get(module_id)
    if not isinstance(record, dict):
        return None
    if record.get("owner") != MANAGER_OWNER:
        return None
    if not pid_alive(record.get("pid")):
        state["modules"].pop(module_id, None)
        save_module_state(state)
        return None
    return record


def activate_module(module_id: str, *, host: str = "127.0.0.1", wait_seconds: float = 3.0) -> dict[str, Any]:
    errors = validate_registered_ports(module_index())
    if errors:
        return {"ok": False, "error": "module registry invalid", "validation_errors": errors}

    module = registered_module(module_id)
    if not module:
        return {"ok": False, "error": f"unknown module: {module_id}"}
    if is_lab_lifecycle_module(module):
        return activate_lab_runtime(module_id)
    port = reserved_port_for(module_id)
    if not port:
        return {"ok": False, "error": f"module has no registered port: {module_id}"}

    record = managed_record(module_id)
    if port_open(host, port):
        return {
            "ok": True,
            "module_id": module_id,
            "port": port,
            "status": "already_active",
            "managed": record is not None,
            "url": f"http://{host}:{port}/",
        }

    try:
        argv = safe_entrypoint_args(str(module["entrypoint"]))
    except ValueError as exc:
        return {"ok": False, "module_id": module_id, "error": str(exc)}

    MODULE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = MODULE_LOG_DIR / f"{module_id}.log"
    log_file = log_path.open("a", encoding="utf-8")
    log_file.write(f"\n{now()} START {module_id} command={json.dumps(argv)}\n")
    log_file.flush()
    process = subprocess.Popen(  # noqa: S603 - argv is registry-validated and shell=False
        argv,
        cwd=REPO_ROOT,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    pgid = os.getpgid(process.pid)
    state = load_module_state()
    state["modules"][module_id] = {
        "owner": MANAGER_OWNER,
        "pid": process.pid,
        "pgid": pgid,
        "command": argv,
        "port": port,
        "started_at": now(),
        "log_path": display_path(log_path),
    }
    save_module_state(state)
    log_file.close()

    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if port_open(host, port):
            return {
                "ok": True,
                "module_id": module_id,
                "port": port,
                "pid": process.pid,
                "managed": True,
                "status": "started",
                "url": f"http://{host}:{port}/",
            }
        if process.poll() is not None:
            return {
                "ok": False,
                "module_id": module_id,
                "port": port,
                "pid": process.pid,
                "status": "exited_before_ready",
                "log_path": display_path(log_path),
            }
        time.sleep(0.1)

    return {
        "ok": False,
        "module_id": module_id,
        "port": port,
        "pid": process.pid,
        "managed": True,
        "status": "started_but_port_not_ready",
        "log_path": display_path(log_path),
    }


def stop_module(module_id: str, *, timeout: float = 3.0) -> dict[str, Any]:
    module = registered_module(module_id)
    if is_lab_lifecycle_module(module):
        return stop_lab_runtime(module_id)
    state = load_module_state()
    record = state.get("modules", {}).get(module_id)
    if not isinstance(record, dict) or record.get("owner") != MANAGER_OWNER:
        return {"ok": False, "module_id": module_id, "error": "module is not managed by this dashboard"}

    pid = int(record.get("pid", 0) or 0)
    pgid = int(record.get("pgid", 0) or 0)
    if not pid_alive(pid):
        state["modules"].pop(module_id, None)
        save_module_state(state)
        return {"ok": True, "module_id": module_id, "status": "already_stopped"}

    try:
        if pgid:
            os.killpg(pgid, signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            waited_pid, _ = os.waitpid(pid, os.WNOHANG)
            if waited_pid == pid:
                state["modules"].pop(module_id, None)
                save_module_state(state)
                return {"ok": True, "module_id": module_id, "status": "stopped"}
        except ChildProcessError:
            pass
        if not pid_alive(pid):
            state["modules"].pop(module_id, None)
            save_module_state(state)
            return {"ok": True, "module_id": module_id, "status": "stopped"}
        time.sleep(0.1)

    return {"ok": False, "module_id": module_id, "status": "stop_timeout", "pid": pid}


def module_cards(host: str = "127.0.0.1") -> dict[str, Any]:
    index = module_index()
    reserved_by_module = {item["module_id"]: item for item in index.get("reserved_ports", [])}
    cards: list[dict[str, Any]] = []
    for module in index.get("modules", []):
        module_path = REPO_ROOT / module["path"]
        metadata_path = module_path / "module.json"
        metadata = load_json(metadata_path) if metadata_path.exists() else {}
        reserved = reserved_by_module.get(module["id"], {})
        record = None
        runtime_report: dict[str, Any] | None = None
        if is_lab_lifecycle_module(module):
            port = None
            runtime_report = lab_runtime_report()
            activated = bool(runtime_report["activated"])
            status_label = "all ready" if runtime_report["all_ready"] else runtime_report["status_label"]
        else:
            port = int(reserved.get("port", module.get("default_port", 0)))
            activated = port_open(host, port) if port else False
            record = managed_record(module["id"])
            status_label = "activated" if activated else "registered"
        cards.append(
            {
                "id": module["id"],
                "name": module["name"],
                "path": module["path"],
                "port": port,
                "url": f"http://{host}:{port}/" if port else None,
                "activated": activated,
                "managed": record is not None,
                "status_label": status_label,
                "entrypoint": module["entrypoint"],
                "surface": module.get("surface", "unknown"),
                "action_kind": "lab_lifecycle" if is_lab_lifecycle_module(module) else "local_http",
                "runtime_status": runtime_report,
                "description": reserved.get("description", metadata.get("name", module["name"])),
                "depends_on": module.get("depends_on", metadata.get("depends_on", [])),
                "recommended_with": module.get("recommended_with", metadata.get("recommended_with", [])),
                "claim_boundary": metadata.get("claim_boundary", index.get("claim_boundary", "Local module only.")),
            }
        )
    return {
        "ok": True,
        "schema_version": index.get("schema_version", "1.0"),
        "module_count": len(cards),
        "activated_count": sum(1 for card in cards if card["activated"]),
        "cards": cards,
        "validation_errors": validate_registered_ports(index),
        "claim_boundary": module_metadata()["claim_boundary"],
    }


def html_page() -> str:
    metadata = module_metadata()
    title = html.escape(metadata["name"])
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #020617; color: #e2e8f0; }}
    header {{ padding: 1.5rem; border-bottom: 1px solid #1e293b; background: linear-gradient(135deg, #0f172a, #052e16); }}
    h1 {{ margin: 0; font-size: 1.5rem; color: #86efac; }}
    .sub {{ color: #cbd5e1; margin-top: .4rem; }}
    main {{ padding: 1.5rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }}
    .card {{ background: #0f172a; border: 1px solid #334155; border-radius: 14px; padding: 1rem; box-shadow: 0 10px 30px rgba(0,0,0,.25); }}
    .row {{ display: flex; justify-content: space-between; gap: 1rem; align-items: start; }}
    .title {{ font-weight: 700; color: #f8fafc; }}
    .chiclet {{ border-radius: 999px; padding: .2rem .55rem; font-size: .75rem; text-transform: uppercase; letter-spacing: .04em; }}
    .on {{ background: #14532d; color: #bbf7d0; border: 1px solid #22c55e; }}
    .off {{ background: #334155; color: #cbd5e1; border: 1px solid #64748b; }}
    code {{ color: #93c5fd; }}
    a {{ color: #86efac; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .muted {{ color: #94a3b8; font-size: .9rem; }}
    .actions {{ display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }}
    button {{ background: #166534; color: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: .45rem .75rem; cursor: pointer; }}
    button.stop {{ background: #7f1d1d; border-color: #ef4444; }}
    button:disabled {{ opacity: .55; cursor: wait; }}
  </style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <div class=\"sub\">Registered local module cards from <code>modules/index.json</code>. Green means the registered port is active. Activate starts only registered entrypoints.</div>
</header>
<main>
  <button onclick=\"loadModules()\">Refresh</button>
  <p id=\"summary\" class=\"muted\"></p>
  <section id=\"cards\" class=\"grid\"></section>
</main>
<script>
function esc(s) {{ return String(s).replace(/[&<>'\"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}}[c])); }}
async function moduleAction(id, action) {{
  const res = await fetch(`/api/modules/${{encodeURIComponent(id)}}/${{action}}`, {{ method: 'POST' }});
  const data = await res.json();
  if (!data.ok) alert(data.error || data.status || 'module action failed');
  await loadModules();
}}
async function loadModules() {{
  const res = await fetch('/api/modules');
  const data = await res.json();
  document.getElementById('summary').textContent = `${{data.activated_count}}/${{data.module_count}} modules activated`;
  document.getElementById('cards').innerHTML = data.cards.map(card => `
    <article class=\"card\">
      <div class=\"row\"><div class=\"title\">${{esc(card.name)}}</div><span class=\"chiclet ${{card.activated ? 'on' : 'off'}}\">${{card.managed ? 'managed ' : ''}}${{card.status_label}}</span></div>
      <p>${{esc(card.description)}}</p>
      <p class=\"muted\"><code>${{esc(card.path)}}</code><br/>port <code>${{card.port}}</code><br/><code>${{esc(card.entrypoint)}}</code></p>
      <div class=\"actions\">
        ${{card.activated ? `<a href=\"${{esc(card.url)}}\" target=\"_blank\" rel=\"noreferrer\">Open module ↗</a>` : `<button onclick=\"moduleAction('${{esc(card.id)}}','activate')\">Activate</button>`}}
        ${{card.managed ? `<button class=\"stop\" onclick=\"moduleAction('${{esc(card.id)}}','stop')\">Stop</button>` : ''}}
      </div>
    </article>`).join('');
}}
loadModules(); setInterval(loadModules, 3000);
</script>
</body>
</html>"""


class DashboardRequestHandler(BaseHTTPRequestHandler):
    server_version = "TelcoModulesDashboard/0.2"

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
        path = self.path.split("?", 1)[0]
        if path == "/":
            self.send_html(html_page())
            return
        if path == "/api/module":
            self.send_json(module_metadata())
            return
        if path == "/api/modules":
            host = self.headers.get("Host", "127.0.0.1").split(":", 1)[0] or "127.0.0.1"
            self.send_json(module_cards(host=host))
            return
        if path == "/api/ports":
            index = module_index()
            self.send_json({**index, "validation_errors": validate_registered_ports(index)})
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        if self.headers.get("Content-Length"):
            self.rfile.read(int(self.headers["Content-Length"]))
        path = self.path.split("?", 1)[0]
        parts = [part for part in path.split("/") if part]
        if len(parts) == 4 and parts[:2] == ["api", "modules"] and parts[3] in {"activate", "stop"}:
            module_id = parts[2]
            host = self.headers.get("Host", "127.0.0.1").split(":", 1)[0] or "127.0.0.1"
            payload = activate_module(module_id, host=host) if parts[3] == "activate" else stop_module(module_id)
            self.send_json(payload, status=HTTPStatus.OK if payload.get("ok") else HTTPStatus.BAD_REQUEST)
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)


def create_server(host: str, port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), DashboardRequestHandler)


def main(argv: list[str] | None = None) -> int:
    metadata = module_metadata()
    parser = argparse.ArgumentParser(description="Serve the local module dashboard.")
    parser.add_argument("--host", default=metadata.get("default_host", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(metadata.get("default_port", 8764)))
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
        print("\nStopped modules dashboard.")
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
