#!/usr/bin/env python3
"""Operator CLI for the Telco Systems Integration Lab.

`lab up` is lab-managed instead of delegating to the BF3
``5G_Emulator_API/main.py`` launcher.  The original launcher uses psutil to
scan/kill arbitrary processes by port, which is fragile on macOS and produced
AccessDenied failures.  This CLI starts the same BF3 service inventory in the
background, tracks only the PIDs it owns, writes per-service logs, and never
kills untracked/external processes.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

LAB_ROOT = Path(__file__).resolve().parents[1]
VENV = Path(os.environ.get("TELCO_LAB_VENV", "/tmp/telco_lab_runtime_venv"))
PY = VENV / "bin" / "python"
PIP = VENV / "bin" / "pip"
BUILD_LOGS = LAB_ROOT / "build_logs"
REQ = LAB_ROOT / "config" / "requirements.txt"
SMOKE_LOG = BUILD_LOGS / "lab_smoke_runtime.json"
TEST_LOG = BUILD_LOGS / "lab_test_pytest.log"
STATUS_LOG = BUILD_LOGS / "lab_status.json"
CONTROL_DIR = LAB_ROOT / ".lab" / "state"
SERVICES_STATE = CONTROL_DIR / "lab_services.json"
SERVICES_EVIDENCE = BUILD_LOGS / "lab_services.json"
SERVICE_LOG_DIR = BUILD_LOGS / "services"
LAB_OWNER = "telco-lab-cli"

CAVEAT = "Runtime/demo readiness only; not formal 3GPP/O-RAN/TM Forum conformance."
BF3_API_ROOT = Path(os.environ.get(
    "BF3_5G_API_ROOT",
    "<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API",
))

# Mirrors the service list in the original BF3 5G_Emulator_API/main.py while
# avoiding its psutil port-scan/kill behavior.
SERVICE_INVENTORY: list[dict[str, Any]] = [
    {"id": "nrf", "label": "NRF", "path": "core_network/nrf.py", "port": 8000, "health": ["/health"]},
    {"id": "amf", "label": "AMF", "path": "core_network/amf.py", "port": 9000, "health": ["/health"], "protocol_aware": True},
    {"id": "smf", "label": "SMF", "path": "core_network/smf.py", "port": 9001, "health": ["/health"], "protocol_aware": True},
    {"id": "upf", "label": "UPF", "path": "core_network/upf.py", "port": 9002, "health": ["/health"], "protocol_aware": True},
    {"id": "ausf", "label": "AUSF", "path": "core_network/ausf.py", "port": 9003, "health": ["/health"]},
    {"id": "udm", "label": "UDM", "path": "core_network/udm.py", "port": 9004, "health": ["/health"]},
    {"id": "udr", "label": "UDR", "path": "core_network/udr.py", "port": 9005, "health": ["/health"]},
    {"id": "udsf", "label": "UDSF", "path": "core_network/udsf.py", "port": 9006, "health": ["/health"]},
    {"id": "cu", "label": "CU", "path": "ran/cu/cu.py", "port": 9008, "health": [], "fixed_args": True},
    {"id": "du", "label": "DU", "path": "ran/du/du.py", "port": 9007, "health": [], "fixed_args": True},
    {"id": "rru", "label": "RRU", "path": "ran/rru/rru.py", "port": 9009, "health": [], "fixed_args": True, "process_only": True},
    {"id": "ptp", "label": "PTP", "path": "ptp/ptp.py", "port": 9010, "health": [], "fixed_args": True, "process_only": True},
    {"id": "assurance", "label": "Service Assurance", "path": "service_assurance/assurance_api.py", "module": "service_assurance.assurance_api", "port": 9011, "health": ["/health"]},
    {"id": "smo", "label": "SMO Framework", "path": "smo/smo_framework.py", "module": "smo.smo_framework", "port": 8122, "health": ["/health"]},
    {"id": "r1", "label": "R1", "path": "smo/r1.py", "module": "smo.r1", "port": 8124, "health": ["/health"]},
    {"id": "y1", "label": "Y1 Analytics", "path": "ran/ric/y1.py", "port": 8123, "health": ["/health"]},
    {"id": "o_ru", "label": "O-RU", "path": "ran/fronthaul/o_ru.py", "module": "ran.fronthaul.o_ru", "port": 8120, "health": ["/health"]},
    {"id": "o1", "label": "O1", "path": "oam/o1.py", "module": "oam.o1", "port": 8125, "health": ["/health"]},
    {"id": "teiv", "label": "TEIV", "path": "oam/teiv.py", "port": 8126, "health": ["/health"]},
    {"id": "o2", "label": "O-Cloud Notification", "path": "etsi/o2/o_cloud_notification.py", "port": 8127, "health": ["/health", "/o-cloud/v1/health"]},
    {"id": "security", "label": "Security", "path": "security/security_service.py", "module": "security.security_service", "port": 8128, "health": ["/health"]},
    {"id": "slicing", "label": "O-RAN Slicing", "path": "ran/slicing/oran_slicing.py", "port": 8129, "health": ["/health"]},
    {"id": "energy", "label": "Network Energy Savings", "path": "ran/energy/nes.py", "port": 8130, "health": ["/health"]},
    {"id": "xhaul", "label": "xHaul", "path": "transport/xhaul.py", "port": 8131, "health": ["/health"]},
    {"id": "ntn_radio", "label": "NTN Radio", "path": "ran/ntn_radio.py", "port": 8132, "health": ["/health"]},
    {"id": "oran_gateway", "label": "O-RAN Gateway", "path": "api_gateway/oran_gateway.py", "port": 8088, "health": ["/health"]},
]

CORE_SERVICES = ["nrf", "amf", "smf", "upf", "ausf", "udm", "udr", "udsf"]
RAN_SERVICES = ["cu", "du", "rru", "ptp", "ntn_radio"]
ORAN_SERVICES = [
    "assurance",
    "smo",
    "r1",
    "y1",
    "o_ru",
    "o1",
    "teiv",
    "o2",
    "security",
    "slicing",
    "energy",
    "xhaul",
    "oran_gateway",
]
CHATTER_GROUPS = {
    "all": [service["id"] for service in SERVICE_INVENTORY],
    "core": CORE_SERVICES,
    "ran": RAN_SERVICES,
    "oran": ORAN_SERVICES,
    "radio": ["ntn_radio"],
}

SCENARIO_CHOICES = ["pdu-session", "radio", "oran-overview", "cu-du", "all"]
STARTUP_ORDER_IDS = ["nrf", "upf", "smf", "amf"]
STARTUP_READY_BARRIERS = {
    "nrf": 6.0,
    "upf": 6.0,
    "smf": 6.0,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], *, capture: bool = True, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=LAB_ROOT, text=True, capture_output=capture, check=check)


def ensure_venv() -> None:
    if not PY.exists():
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    subprocess.run([str(PIP), "install", "--quiet", "-r", str(REQ)], cwd=LAB_ROOT, check=True)


def extract_json(stdout: str) -> dict[str, Any]:
    start = stdout.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in output: {stdout[:200]}")
    return json.loads(stdout[start:])


def bf3_env() -> dict[str, str]:
    env = os.environ.copy()
    venv_bin = BF3_API_ROOT / "venv" / "bin"
    if venv_bin.exists():
        env["PATH"] = f"{venv_bin}{os.pathsep}" + env.get("PATH", "")
    env["PYTHONPATH"] = f"{BF3_API_ROOT}{os.pathsep}" + env.get("PYTHONPATH", "")
    env.setdefault("PYTHONUNBUFFERED", "1")
    return env


def bf3_python() -> str:
    venv_python = BF3_API_ROOT / "venv" / "bin" / "python"
    return str(venv_python if venv_python.exists() else Path(sys.executable))


def service_path(service: dict[str, Any]) -> Path:
    return BF3_API_ROOT / service["path"]


def service_log_path(service: dict[str, Any]) -> Path:
    return SERVICE_LOG_DIR / f"{service['id']}.log"


def service_marker(service: dict[str, Any]) -> str:
    return str(service.get("module") or service_path(service))


def service_cmd(service: dict[str, Any], protocol_mode: str) -> list[str]:
    cmd = [bf3_python()]
    if service.get("module"):
        cmd.extend(["-m", service["module"]])
    else:
        cmd.append(str(service_path(service)))
    if not service.get("fixed_args"):
        cmd.extend(["--host", "0.0.0.0", "--port", str(service["port"])])
        if service.get("protocol_aware"):
            cmd.extend(["--protocol-mode", protocol_mode])
    return cmd


def load_services_state() -> dict[str, Any]:
    source = SERVICES_STATE if SERVICES_STATE.exists() else SERVICES_EVIDENCE
    if not source.exists():
        return {"services": {}}
    try:
        data = json.loads(source.read_text())
    except Exception:
        return {"services": {}}
    if not isinstance(data, dict):
        return {"services": {}}
    data.setdefault("services", {})
    return data


def write_services_state(state: dict[str, Any]) -> None:
    BUILD_LOGS.mkdir(exist_ok=True)
    CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2)
    SERVICES_STATE.write_text(payload)
    SERVICES_EVIDENCE.write_text(payload)


def archive_services_state() -> None:
    BUILD_LOGS.mkdir(exist_ok=True)
    archive = BUILD_LOGS / f"lab_services.stopped.{int(time.time())}.json"
    if SERVICES_EVIDENCE.exists():
        try:
            SERVICES_EVIDENCE.replace(archive)
        except OSError:
            SERVICES_EVIDENCE.unlink(missing_ok=True)
    SERVICES_STATE.unlink(missing_ok=True)


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


def ps_field(pid: int, field: str) -> str | None:
    try:
        proc = subprocess.run(["ps", "-p", str(pid), "-o", f"{field}="], cwd=LAB_ROOT, text=True, capture_output=True, check=False)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    value = proc.stdout.strip()
    return value or None


def pid_command(pid: int) -> str:
    return ps_field(pid, "command") or ""


def pid_cwd(pid: int) -> str:
    try:
        proc = subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"], cwd=LAB_ROOT, text=True, capture_output=True, check=False)
    except OSError:
        return ""
    for line in proc.stdout.splitlines():
        if line.startswith("n"):
            return line[1:]
    return ""


def process_start_signature(pid: int) -> str:
    return ps_field(pid, "lstart") or ""


def process_group(pid: int) -> int | None:
    value = ps_field(pid, "pgid")
    if value and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    try:
        return os.getpgid(pid)
    except OSError:
        return None


def tcp_listening(port: int, host: str = "127.0.0.1", timeout: float = 0.25) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            return sock.connect_ex((host, port)) == 0
        except OSError:
            return False


def listening_pids(port: int) -> list[int]:
    try:
        proc = subprocess.run(["lsof", "-nP", f"-tiTCP:{port}", "-sTCP:LISTEN"], cwd=LAB_ROOT, text=True, capture_output=True, check=False)
    except OSError:
        return []
    return sorted({int(line.strip()) for line in proc.stdout.splitlines() if line.strip().isdigit()})


def process_pids_for_service(service: dict[str, Any]) -> list[int]:
    try:
        proc = subprocess.run(["pgrep", "-f", service_marker(service)], cwd=LAB_ROOT, text=True, capture_output=True, check=False)
    except OSError:
        return []
    found: set[int] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.isdigit():
            pid = int(line)
            if pid != os.getpid():
                found.add(pid)
    return sorted(found)


def safe_to_terminate(pid: int, record: dict[str, Any]) -> tuple[bool, str]:
    """Protect against stale PID-file reuse before sending signals."""
    if record.get("owner") != LAB_OWNER:
        return False, "missing lab owner marker"
    if not pid_alive(pid):
        return True, "already exited"

    tracked_pgid = record.get("pgid")
    if isinstance(tracked_pgid, str) and tracked_pgid.lstrip("-").isdigit():
        tracked_pgid = int(tracked_pgid)
    live_pgid = process_group(pid)
    if isinstance(tracked_pgid, int) and live_pgid != tracked_pgid:
        return False, f"process group mismatch tracked={tracked_pgid} live={live_pgid}"

    tracked_signature = record.get("process_start_signature")
    live_signature = process_start_signature(pid)
    if tracked_signature and live_signature and tracked_signature != live_signature:
        return False, "PID start signature changed"

    command = pid_command(pid)
    marker = str(record.get("marker") or "")
    if marker and command and marker in command:
        return True, "verified command match"
    if marker and pid_cwd(pid) == str(BF3_API_ROOT) and marker in " ".join(str(value) for value in record.get("command", [])):
        return True, "verified cwd/recorded command match"
    return False, f"pid command did not match tracked service: {command[:160]}"


def check_http(port: int, paths: list[str], timeout: float = 0.7) -> dict[str, Any]:
    errors: list[str] = []
    for path in paths:
        url = f"http://127.0.0.1:{port}{path}"
        try:
            with urlopen(url, timeout=timeout) as response:  # noqa: S310 - local lab health checks only
                return {"ok": 200 <= response.status < 400, "url": url, "status_code": response.status}
        except Exception as exc:
            if isinstance(exc, URLError):
                errors.append(f"{url}: {exc.reason}")
            else:
                errors.append(f"{url}: {exc}")
    return {"ok": False, "errors": errors[:3]}


def summarize_service(service: dict[str, Any], record: dict[str, Any] | None = None) -> dict[str, Any]:
    record = record or {}
    pid = record.get("pid")
    if isinstance(pid, str) and pid.isdigit():
        pid = int(pid)
    pid_int = pid if isinstance(pid, int) else None
    alive = pid_alive(pid_int)
    port = int(service["port"])
    process_only = bool(service.get("process_only"))
    port_open = False if process_only else tcp_listening(port)
    external_pids = process_pids_for_service(service) if process_only else (listening_pids(port) if port_open else [])
    health: dict[str, Any] = {"ok": None}
    ready = False
    state = record.get("state", "not_started")

    if state in {"missing_entrypoint", "failed_to_start"}:
        ready = False
    elif state in {"external_port_listening", "external_process_running"}:
        if process_only:
            ready = bool(external_pids or record.get("external_pids"))
            state = "external_process_running"
        elif service.get("health"):
            health = check_http(port, service["health"])
            ready = bool(health.get("ok"))
            state = "external_port_listening"
        else:
            ready = port_open
            state = "external_port_listening"
    elif alive:
        if process_only:
            ready = True
            state = "running"
        elif service.get("health"):
            health = check_http(port, service["health"])
            ready = bool(health.get("ok"))
            state = "running" if ready else "running_not_healthy"
        else:
            ready = port_open
            state = "running" if ready else "running_port_not_open"
    elif process_only and external_pids and not pid_int:
        ready = True
        state = "external_process_running"
    elif port_open and not pid_int:
        if service.get("health"):
            health = check_http(port, service["health"])
            ready = bool(health.get("ok"))
        else:
            ready = True
        state = "external_port_listening"
    elif pid_int:
        state = "exited"
    else:
        state = "not_started"

    return {
        "id": service["id"],
        "label": service["label"],
        "path": service["path"],
        "port": port,
        "pid": pid_int,
        "external_pids": external_pids,
        "alive": alive,
        "port_open": port_open,
        "ready": ready,
        "state": state,
        "health": health,
        "log": record.get("log", str(service_log_path(service))),
        "command": record.get("command"),
    }


def wait_for_startup_barrier(service: dict[str, Any], record: dict[str, Any]) -> None:
    timeout = STARTUP_READY_BARRIERS.get(service["id"])
    if not timeout or record.get("state") in {"missing_entrypoint", "failed_to_start"}:
        return

    started = time.time()
    deadline = started + timeout
    ready = False
    last_state = record.get("state", "unknown")
    while time.time() < deadline:
        item = summarize_service(service, record)
        last_state = item["state"]
        if item["ready"]:
            ready = True
            break
        time.sleep(0.25)

    record["startup_barrier"] = {
        "ready": ready,
        "waited_seconds": round(time.time() - started, 3),
        "last_state": last_state,
    }


def put_service_record(state: dict[str, Any], service: dict[str, Any], record: dict[str, Any]) -> None:
    wait_for_startup_barrier(service, record)
    state["services"][service["id"]] = record


def services_report() -> dict[str, Any]:
    state = load_services_state()
    records = state.get("services", {}) if isinstance(state.get("services"), dict) else {}
    services = [summarize_service(service, records.get(service["id"])) for service in SERVICE_INVENTORY]
    ready_count = sum(1 for item in services if item["ready"])
    external = [item for item in services if item["state"] in {"external_port_listening", "external_process_running"}]
    failed = [item for item in services if item["state"] in {"failed_to_start", "missing_entrypoint", "exited"}]
    return {
        "recorded_at": now(),
        "bf3_api_root": str(BF3_API_ROOT),
        "state_file": str(SERVICES_STATE),
        "evidence_file": str(SERVICES_EVIDENCE),
        "log_dir": str(SERVICE_LOG_DIR),
        "total": len(services),
        "ready": ready_count,
        "all_ready": ready_count == len(services),
        "external": [item["id"] for item in external],
        "failed": [item["id"] for item in failed],
        "services": services,
        "caveat": CAVEAT,
    }


def print_services_table(report: dict[str, Any]) -> None:
    print(f"Services: {report['ready']}/{report['total']} ready")
    for item in report["services"]:
        marker = "OK" if item["ready"] else "--"
        if item["pid"]:
            pid = str(item["pid"])
        elif item.get("external_pids"):
            pid = ",".join(str(value) for value in item["external_pids"]) + "*"
        else:
            pid = "-"
        health = f" health={item['health']['url']}" if item.get("health", {}).get("url") else ""
        print(f"  {marker} {item['id']:<13} port={item['port']:<5} pid={pid:<8} state={item['state']}{health}")
    if report.get("external"):
        print("Note: PID values ending in * are external/untracked; ./lab down will not kill them.")
    print(f"Evidence: {SERVICES_EVIDENCE}")
    print(f"State: {SERVICES_STATE}")
    print(f"Logs: {SERVICE_LOG_DIR}")
    print(f"Caveat: {CAVEAT}")


def service_by_id(service_id: str) -> dict[str, Any] | None:
    return next((service for service in SERVICE_INVENTORY if service["id"] == service_id), None)


def service_start_sequence() -> list[dict[str, Any]]:
    """Return dependency-aware startup order while preserving inventory membership."""
    rank = {service_id: index for index, service_id in enumerate(STARTUP_ORDER_IDS)}
    default_rank = len(rank)
    return sorted(
        SERVICE_INVENTORY,
        key=lambda service: (rank.get(service["id"], default_rank), SERVICE_INVENTORY.index(service)),
    )


def selected_service_ids(group_or_service: str) -> list[str]:
    if group_or_service in CHATTER_GROUPS:
        return CHATTER_GROUPS[group_or_service]
    if service_by_id(group_or_service):
        return [group_or_service]
    return []


def tail_lines(path: Path, limit: int) -> list[str]:
    if limit <= 0 or not path.exists():
        return []
    try:
        return path.read_text(errors="replace").splitlines()[-limit:]
    except OSError as exc:
        return [f"<unable to read {path}: {exc}>"]


def print_prefixed(service_id: str, line: str) -> None:
    print(f"[{service_id:<13}] {line}", flush=True)


def selected_log_paths(group_or_service: str) -> list[tuple[str, Path]]:
    paths: list[tuple[str, Path]] = []
    for service_id in selected_service_ids(group_or_service):
        service = service_by_id(service_id)
        if service:
            paths.append((service_id, service_log_path(service)))
    return paths


def cmd_chatter(args: argparse.Namespace) -> int:
    """Show the old foreground-style service chatter without changing lab up."""
    SERVICE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    paths = selected_log_paths(args.group)
    if not paths:
        print(f"Unknown service/group: {args.group}", file=sys.stderr)
        return 2

    print(f"lab chatter: group={args.group} logs={SERVICE_LOG_DIR}")
    printed = 0
    if args.lines > 0:
        for service_id, path in paths:
            for line in tail_lines(path, args.lines):
                print_prefixed(service_id, line)
                printed += 1

    if printed == 0:
        print("No lab-captured chatter lines found for this selection yet.")
        print("Run ./lab up first, or trigger traffic with ./lab scenario <name>.")

    print("Note: services marked with * by ./lab services are external/untracked; service stdout may be elsewhere.")
    print("      ./lab scenario also appends SCENARIO request/response transcript lines here for those services.")
    if not args.follow:
        print("Use --follow for a live merged tail; press Ctrl-C to stop.")
        return 0

    print("Following service logs; press Ctrl-C to stop.")
    positions: dict[Path, int] = {}
    for _, path in paths:
        try:
            positions[path] = path.stat().st_size if path.exists() else 0
        except OSError:
            positions[path] = 0

    started = time.time()
    try:
        while True:
            for service_id, path in paths:
                if not path.exists():
                    continue
                try:
                    with path.open("r", errors="replace") as fh:
                        fh.seek(positions.get(path, 0))
                        for line in fh:
                            print_prefixed(service_id, line.rstrip("\n"))
                        positions[path] = fh.tell()
                except OSError as exc:
                    print_prefixed(service_id, f"<unable to follow {path}: {exc}>")
                    positions[path] = positions.get(path, 0)

            if args.duration is not None and time.time() - started >= args.duration:
                print(f"Stopped after --duration {args.duration:g}s.")
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped chatter follow.")
        return 0


def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 5.0) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    request = Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - local lab scenario traffic only
            body = response.read().decode("utf-8", errors="replace")
            parsed: Any
            try:
                parsed = json.loads(body) if body else None
            except json.JSONDecodeError:
                parsed = None
            return {
                "ok": 200 <= response.status < 400,
                "status_code": response.status,
                "json": parsed,
                "body": body,
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body) if body else None
        except json.JSONDecodeError:
            parsed = None
        return {"ok": False, "status_code": exc.code, "json": parsed, "body": body, "error": str(exc)}
    except URLError as exc:
        return {"ok": False, "status_code": None, "json": None, "body": "", "error": str(exc.reason)}
    except Exception as exc:
        return {"ok": False, "status_code": None, "json": None, "body": "", "error": str(exc)}


def service_for_url(url: str) -> dict[str, Any] | None:
    try:
        port = urlparse(url).port
    except ValueError:
        return None
    if port is None:
        return None
    return next((service for service in SERVICE_INVENTORY if int(service["port"]) == int(port)), None)


def append_scenario_log(step: dict[str, Any]) -> None:
    """Record the operator-triggered request/response transcript beside service logs.

    This is intentionally labeled SCENARIO so it is not confused with service
    stdout.  It gives external/untracked services visible chatter in
    ``./lab chatter`` even when their original stdout is owned by another
    terminal.
    """
    service = service_for_url(str(step.get("url", "")))
    if not service:
        return
    SERVICE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    status = step.get("status_code") if step.get("status_code") is not None else "-"
    ok = "OK" if step.get("ok") else "FAIL"
    detail = ""
    data = step.get("json")
    if isinstance(data, dict):
        summary = {key: data.get(key) for key in ["status", "message", "cause", "ueIpAddress", "count", "source"] if key in data}
        if summary:
            detail = f" response={json.dumps(summary, sort_keys=True)}"
    elif step.get("error"):
        detail = f" error={step['error']}"
    line = f"{now()} SCENARIO {ok} {step.get('name')} {step.get('method')} {step.get('url')} status={status}{detail}\n"
    try:
        with service_log_path(service).open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        return


def request_step(name: str, method: str, url: str, payload: dict[str, Any] | None, args: argparse.Namespace) -> dict[str, Any]:
    step = {"name": name, "method": method.upper(), "url": url, "payload": payload}
    if args.dry_run:
        step.update({"ok": True, "dry_run": True})
        return step
    result = http_json(method, url, payload, timeout=args.timeout)
    step.update(result)
    append_scenario_log(step)
    return step


def ue_context_payload(args: argparse.Namespace, session_id: int) -> dict[str, Any]:
    return {
        "supi": args.supi,
        "imsi": args.supi.removeprefix("imsi-"),
        "pduSessionId": session_id,
        "ranUeNgapId": 1,
        "amfUeNgapId": 1001,
        "dnn": "internet",
        "sNssai": {"sst": 1, "sd": "010203"},
    }


def sm_context_payload(args: argparse.Namespace, session_id: int) -> dict[str, Any]:
    return {
        "supi": args.supi,
        "pduSessionId": session_id,
        "dnn": "internet",
        "sNssai": {"sst": 1, "sd": "010203"},
        "anType": "3GPP_ACCESS",
        "ratType": "NR",
    }


def pfcp_session_payload(session_id: int) -> dict[str, Any]:
    return {
        "messageType": "PFCP_SESSION_ESTABLISHMENT_REQUEST",
        "seid": f"lab-direct-seid-{session_id}",
        "createPDR": [
            {
                "pdrId": 1,
                "precedence": 200,
                "pdi": {"sourceInterface": "ACCESS", "ueIpAddress": "10.0.0.1", "networkInstance": "internet"},
                "farId": 1,
            }
        ],
        "createFAR": [
            {
                "farId": 1,
                "applyAction": "FORWARD",
                "forwardingParameters": {
                    "destinationInterface": "CORE",
                    "outerHeaderCreation": {"description": "GTP-U/UDP/IPv4", "teid": "1001"},
                },
            }
        ],
        "createQER": [{"qerId": 1, "qfi": 9, "uplinkMBR": 100000000, "downlinkMBR": 100000000}],
    }


def traffic_payload(args: argparse.Namespace) -> dict[str, Any]:
    return {"src_ip": args.ue_ip, "dest_ip": "8.8.8.8", "packet_size": 1200}


def print_scenario_steps(title: str, steps: list[dict[str, Any]], args: argparse.Namespace) -> None:
    print(f"lab scenario: {title}")
    for step in steps:
        if step.get("dry_run"):
            print(f"  DRY {step['name']:<28} {step['method']:<4} {step['url']}")
            if step.get("payload") is not None:
                print(f"      payload={json.dumps(step['payload'], sort_keys=True)}")
            continue
        marker = "OK" if step.get("ok") else "!!"
        status = step.get("status_code") if step.get("status_code") is not None else "-"
        print(f"  {marker} {step['name']:<28} {step['method']:<4} status={status} {step['url']}")
        if not step.get("ok") and step.get("error"):
            print(f"      error={step['error']}")
        detail = step.get("json")
        if isinstance(detail, dict):
            important = {
                key: detail.get(key)
                for key in ["status", "message", "cause", "ueIpAddress", "activeRules", "activeSessions", "count", "source"]
                if key in detail
            }
            if important:
                print(f"      {json.dumps(important, sort_keys=True)}")
        elif step.get("body") and args.verbose:
            print(f"      body={step['body'][:300]}")
    print("After this, run: ./lab chatter core --lines 80  (or ./lab chatter all --follow)")


def scenario_pdu_session(args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    steps: list[dict[str, Any]] = []
    success = False
    for index in range(args.count):
        session_id = args.pdu_session_id + index
        ue_id = args.ue_id if args.count == 1 else f"{args.ue_id}-{index + 1}"
        context = ue_context_payload(args, session_id)
        steps.append(request_step("AMF create UE context", "POST", f"http://127.0.0.1:9000/amf/ue/{ue_id}", context, args))
        amf_step = request_step("AMF trigger PDU session", "POST", "http://127.0.0.1:9000/amf/pdu-session/create", {"ue_id": ue_id}, args)
        steps.append(amf_step)
        if args.dry_run:
            steps.append(request_step("SMF direct fallback", "POST", "http://127.0.0.1:9001/nsmf-pdusession/v1/sm-contexts", sm_context_payload(args, session_id), args))
            steps.append(request_step("UPF direct PFCP fallback", "POST", "http://127.0.0.1:9002/n4/sessions", pfcp_session_payload(session_id), args))
            steps.append(request_step("UPF simulate user traffic", "POST", "http://127.0.0.1:9002/upf/simulate-traffic", traffic_payload(args), args))
            success = True
            continue
        if amf_step.get("ok"):
            success = True
        else:
            smf_step = request_step("SMF direct fallback", "POST", "http://127.0.0.1:9001/nsmf-pdusession/v1/sm-contexts", sm_context_payload(args, session_id), args)
            steps.append(smf_step)
            success = success or bool(smf_step.get("ok"))
            if not smf_step.get("ok"):
                upf_step = request_step("UPF direct PFCP fallback", "POST", "http://127.0.0.1:9002/n4/sessions", pfcp_session_payload(session_id), args)
                steps.append(upf_step)
                success = success or bool(upf_step.get("ok"))
        traffic_step = request_step("UPF simulate user traffic", "POST", "http://127.0.0.1:9002/upf/simulate-traffic", traffic_payload(args), args)
        steps.append(traffic_step)
        success = success or bool(traffic_step.get("ok") and isinstance(traffic_step.get("json"), dict) and traffic_step["json"].get("status") == "FORWARDED")
    return steps, success


def scenario_radio(args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    steps: list[dict[str, Any]] = []
    success = False
    for _ in range(args.count):
        tick = request_step("NTN radio tick", "POST", "http://127.0.0.1:8132/ntn/tick", None, args)
        steps.append(tick)
        success = success or bool(tick.get("ok"))
    logs = request_step("NTN radio logs", "GET", "http://127.0.0.1:8132/ntn/logs?limit=12", None, args)
    steps.append(logs)
    success = success or bool(logs.get("ok"))
    return steps, success


def scenario_oran_overview(args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    steps = [request_step("O-RAN gateway overview", "GET", "http://127.0.0.1:8088/api/oran/overview", None, args)]
    return steps, bool(steps[0].get("ok"))


def scenario_cu_du(args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    payload = {"ue_id": args.ue_id, "procedure": "cu-to-du-demo", "message": "lab scenario CU->DU test traffic"}
    steps = [request_step("CU to DU transfer", "POST", "http://127.0.0.1:9008/cu_to_du", payload, args)]
    return steps, bool(steps[0].get("ok"))


def cmd_scenario(args: argparse.Namespace) -> int:
    if args.dry_run:
        print("Dry run only; no service endpoints will be called.")

    scenario_map = {
        "pdu-session": scenario_pdu_session,
        "radio": scenario_radio,
        "oran-overview": scenario_oran_overview,
        "cu-du": scenario_cu_du,
    }

    scenarios = ["oran-overview", "radio", "cu-du", "pdu-session"] if args.name == "all" else [args.name]
    all_steps: list[dict[str, Any]] = []
    successes: list[bool] = []
    for scenario_name in scenarios:
        steps, ok = scenario_map[scenario_name](args)
        all_steps.extend(steps)
        successes.append(ok)

    print_scenario_steps(args.name, all_steps, args)

    if args.name == "radio" and not args.dry_run:
        for step in all_steps:
            data = step.get("json")
            if step["name"] == "NTN radio logs" and isinstance(data, dict):
                for line in data.get("lines", [])[-8:]:
                    print_prefixed("ntn_radio", line)

    if args.dry_run:
        return 0
    return 0 if all(successes) else 2


def wait_for_services(timeout_seconds: float) -> dict[str, Any]:
    deadline = time.time() + max(timeout_seconds, 0)
    report = services_report()
    while time.time() < deadline:
        if report["all_ready"] or report["failed"]:
            return report
        time.sleep(0.5)
        report = services_report()
    return report


def terminate_pid(pid: int, record: dict[str, Any], timeout: float = 4.0) -> dict[str, Any]:
    if not pid_alive(pid):
        return {"pid": pid, "stopped": True, "detail": "already exited"}
    safe, detail = safe_to_terminate(pid, record)
    if not safe:
        return {"pid": pid, "stopped": False, "detail": detail}
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return {"pid": pid, "stopped": True, "detail": "already exited"}
    except PermissionError as exc:
        return {"pid": pid, "stopped": False, "detail": f"permission denied: {exc}"}

    deadline = time.time() + timeout
    while time.time() < deadline:
        if not pid_alive(pid):
            return {"pid": pid, "stopped": True, "detail": "terminated"}
        time.sleep(0.2)

    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return {"pid": pid, "stopped": True, "detail": "terminated"}
    except PermissionError as exc:
        return {"pid": pid, "stopped": False, "detail": f"kill permission denied: {exc}"}

    for _ in range(10):
        if not pid_alive(pid):
            return {"pid": pid, "stopped": True, "detail": "killed"}
        time.sleep(0.1)
    return {"pid": pid, "stopped": False, "detail": "still alive after SIGKILL"}


def stop_tracked_services() -> dict[str, Any]:
    state = load_services_state()
    records = state.get("services", {}) if isinstance(state.get("services"), dict) else {}
    stopped: dict[str, Any] = {}
    for service in SERVICE_INVENTORY:
        record = records.get(service["id"], {})
        pid = record.get("pid")
        if isinstance(pid, str) and pid.isdigit():
            pid = int(pid)
        if isinstance(pid, int):
            stopped[service["id"]] = terminate_pid(pid, record)
    all_stopped = all(item.get("stopped") for item in stopped.values())
    if all_stopped:
        archive_services_state()
    elif stopped:
        state["last_stop_attempt"] = {"recorded_at": now(), "stopped": stopped}
        write_services_state(state)
    return {"recorded_at": now(), "stopped": stopped, "caveat": CAVEAT}


def cmd_up(args: argparse.Namespace) -> int:
    BUILD_LOGS.mkdir(exist_ok=True)
    SERVICE_LOG_DIR.mkdir(exist_ok=True)
    if not BF3_API_ROOT.exists():
        print(f"BF3 API root not found: {BF3_API_ROOT}", file=sys.stderr)
        return 2

    if args.dry_run:
        print("lab up would start managed BF3 5G/RAN/O-RAN services in the background")
        print("Launcher: lab-owned direct service inventory (no monolithic launcher, no psutil)")
        print(f"Working directory: {BF3_API_ROOT}")
        print(f"Python: {bf3_python()}")
        print("Startup order: dependency-aware NRF -> UPF -> SMF -> AMF, then remaining services")
        for service in service_start_sequence():
            cmd = service_cmd(service, args.protocol_mode)
            print(f"  {service['id']:<13} port={service['port']:<5} log={service_log_path(service)}")
            print(f"    {' '.join(cmd)}")
        print(f"PID state: {SERVICES_STATE}")
        print(f"Evidence copy: {SERVICES_EVIDENCE}")
        return 0

    if args.replace:
        stop_tracked_services()

    previous = load_services_state()
    previous_records = previous.get("services", {}) if isinstance(previous.get("services"), dict) else {}
    new_state: dict[str, Any] = {
        "owner": LAB_OWNER,
        "started_at": now(),
        "bf3_api_root": str(BF3_API_ROOT),
        "python": bf3_python(),
        "protocol_mode": args.protocol_mode,
        "services": {},
        "caveat": CAVEAT,
    }

    for service in service_start_sequence():
        service_id = service["id"]
        cmd = service_cmd(service, args.protocol_mode)
        log_path = service_log_path(service)
        record: dict[str, Any] = {
            "owner": LAB_OWNER,
            "path": service["path"],
            "port": service["port"],
            "marker": service_marker(service),
            "command": cmd,
            "log": str(log_path),
            "started_at": now(),
        }

        if not service_path(service).exists():
            record.update({"state": "missing_entrypoint", "error": str(service_path(service))})
            put_service_record(new_state, service, record)
            continue

        previous_pid = previous_records.get(service_id, {}).get("pid") if isinstance(previous_records.get(service_id), dict) else None
        if isinstance(previous_pid, str) and previous_pid.isdigit():
            previous_pid = int(previous_pid)
        if isinstance(previous_pid, int) and pid_alive(previous_pid):
            previous_record = previous_records[service_id]
            safe, _ = safe_to_terminate(previous_pid, previous_record)
            if safe:
                record.update(previous_record)
                record["state"] = "already_running_tracked"
                put_service_record(new_state, service, record)
                continue

        if service.get("process_only"):
            process_pids = process_pids_for_service(service)
            if process_pids:
                record.update({"state": "external_process_running", "pid": None, "external_pids": process_pids, "note": "Matching process is already running; lab did not kill untracked processes."})
                put_service_record(new_state, service, record)
                continue
        elif tcp_listening(int(service["port"])):
            record.update({"state": "external_port_listening", "pid": None, "external_pids": listening_pids(int(service["port"])), "note": "Port is already listening; lab did not kill untracked processes."})
            put_service_record(new_state, service, record)
            continue

        with log_path.open("ab") as log_file:
            header = f"\n--- lab up {now()} service={service_id} port={service['port']} ---\n$ {' '.join(cmd)}\n"
            log_file.write(header.encode())
            log_file.flush()
            try:
                proc = subprocess.Popen(cmd, cwd=BF3_API_ROOT, env=bf3_env(), stdout=log_file, stderr=subprocess.STDOUT, start_new_session=True)
            except Exception as exc:
                record.update({"state": "failed_to_start", "error": str(exc)})
                put_service_record(new_state, service, record)
                continue

        time.sleep(0.15)
        record.update({
            "pid": proc.pid,
            "pgid": process_group(proc.pid),
            "process_start_signature": process_start_signature(proc.pid),
        })
        if proc.poll() is not None:
            record.update({"state": "failed_to_start", "returncode": proc.returncode})
        else:
            record.update({"state": "started"})
        put_service_record(new_state, service, record)

    write_services_state(new_state)
    report = wait_for_services(args.wait_seconds)
    print("lab up: managed BF3 5G/RAN/O-RAN stack")
    print_services_table(report)
    if report["all_ready"]:
        external_count = len(report.get("external", []))
        suffix = f" ({external_count} external/untracked already-running)" if external_count else ""
        print(f"Result: all required service endpoints/processes are ready{suffix}.")
        return 0
    print("Result: stack is not fully ready yet; inspect failed states/logs above.")
    return 2


def cmd_down(args: argparse.Namespace) -> int:
    result = stop_tracked_services()
    stopped = result["stopped"]
    print("lab down: stopped tracked lab-owned services")
    if not stopped:
        print("  No tracked PIDs found.")
    for service_id, item in stopped.items():
        marker = "OK" if item.get("stopped") else "!!"
        print(f"  {marker} {service_id:<13} pid={item.get('pid')} {item.get('detail')}")
    print("External/untracked processes were not touched.")
    print(f"Caveat: {CAVEAT}")
    return 0 if all(item.get("stopped") for item in stopped.values()) else 2


def cmd_services(args: argparse.Namespace) -> int:
    report = services_report()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_services_table(report)
    return 0 if report["all_ready"] else 2


def cmd_smoke(args: argparse.Namespace) -> int:
    BUILD_LOGS.mkdir(exist_ok=True)
    ensure_venv()
    proc = run([str(PY), "scripts/mock_service_smoke.py"], capture=True)
    SMOKE_LOG.write_text(proc.stdout)
    if proc.stderr:
        (BUILD_LOGS / "lab_smoke_runtime.stderr.log").write_text(proc.stderr)
    try:
        data = extract_json(proc.stdout)
    except Exception as exc:
        print(f"lab smoke: FAILED to parse smoke output: {exc}")
        return 2
    print(f"lab smoke: {data.get('status')}")
    print(f"  AST files: {data.get('ast', {}).get('count')}")
    print(f"  Imported modules: {len(data.get('imports', {}).get('imported', []))}")
    print(f"  Missing deps: {len(data.get('imports', {}).get('missing_dependencies', []))}")
    print(f"  Evidence: {SMOKE_LOG}")
    print(f"  Caveat: {CAVEAT}")
    return 0 if proc.returncode == 0 and data.get("status") == "pass" else 2


def cmd_test(args: argparse.Namespace) -> int:
    BUILD_LOGS.mkdir(exist_ok=True)
    ensure_venv()
    proc = run([str(PY), "-m", "pytest", "-q", "tests"], capture=True)
    TEST_LOG.write_text(proc.stdout + ("\n--- stderr ---\n" + proc.stderr if proc.stderr else ""))
    print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
    print(f"Evidence: {TEST_LOG}")
    print(f"Caveat: {CAVEAT}")
    return proc.returncode


def read_latest() -> dict[str, Any]:
    smoke: dict[str, Any] | None = None
    if SMOKE_LOG.exists():
        try:
            smoke = extract_json(SMOKE_LOG.read_text())
        except Exception:
            smoke = {"status": "unreadable"}
    tests = TEST_LOG.read_text().strip() if TEST_LOG.exists() else "not run"
    service_report = services_report()
    status = {
        "recorded_at": now(),
        "runtime_smoke": {
            "status": smoke.get("status") if smoke else "not run",
            "ast_count": smoke.get("ast", {}).get("count") if smoke else None,
            "imported_count": len(smoke.get("imports", {}).get("imported", [])) if smoke else 0,
            "missing_dependencies": smoke.get("imports", {}).get("missing_dependencies", []) if smoke else [],
            "errors": smoke.get("imports", {}).get("errors", []) if smoke else [],
        },
        "pytest": tests.splitlines()[-1] if tests != "not run" and tests.splitlines() else tests,
        "services": {
            "ready": service_report["ready"],
            "total": service_report["total"],
            "all_ready": service_report["all_ready"],
            "external": service_report["external"],
            "failed": service_report["failed"],
            "state_file": service_report["state_file"],
            "evidence_file": service_report["evidence_file"],
            "log_dir": service_report["log_dir"],
        },
        "evidence": {
            "smoke": str(SMOKE_LOG) if SMOKE_LOG.exists() else None,
            "test": str(TEST_LOG) if TEST_LOG.exists() else None,
            "services": str(SERVICES_EVIDENCE) if SERVICES_EVIDENCE.exists() else None,
        },
        "caveat": CAVEAT,
    }
    STATUS_LOG.write_text(json.dumps(status, indent=2))
    return status


def cmd_status(args: argparse.Namespace) -> int:
    status = read_latest()
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("Telco Lab Status")
        print(f"  Runtime smoke: {status['runtime_smoke']['status']}")
        print(f"  AST files: {status['runtime_smoke']['ast_count']}")
        print(f"  Imported modules: {status['runtime_smoke']['imported_count']}")
        print(f"  Pytest: {status['pytest']}")
        print(f"  Services: {status['services']['ready']}/{status['services']['total']} ready")
        print(f"  Evidence: {STATUS_LOG}")
        print(f"  Caveat: {status['caveat']}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    status = read_latest()
    runtime_ok = status["runtime_smoke"]["status"] == "pass"
    tests_ok = "passed" in status["pytest"]
    services_ok = bool(status["services"]["all_ready"])
    print("Telco Systems Integration Lab Demo Readiness")
    print("================================================")
    print(f"Managed BF3 services up:   {'YES' if services_ok else 'NO'} ({status['services']['ready']}/{status['services']['total']})")
    print(f"Runtime-ready mock imports: {'YES' if runtime_ok else 'NO'}")
    print(f"Regression tests passing:   {'YES' if tests_ok else 'NO'}")
    print(f"Copied AST/import scope:    {status['runtime_smoke']['ast_count']} Python files / {status['runtime_smoke']['imported_count']} imports")
    print("What this demonstrates: lab-managed BF3 service lifecycle plus copied mock 5G core/RAN/O-RAN code readiness evidence.")
    print(f"What it does not claim: {CAVEAT}")
    return 0 if runtime_ok and tests_ok and services_ok else 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Telco Systems Integration Lab operator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    up = sub.add_parser("up", help="start the BF3 5G/RAN/O-RAN stack in the background")
    up.add_argument("--protocol-mode", choices=["rest", "real"], default="rest")
    up.add_argument("--dry-run", action="store_true", help="print the managed service commands without starting services")
    up.add_argument("--replace", action="store_true", help="stop tracked lab-owned services before starting")
    up.add_argument("--wait-seconds", type=float, default=10.0, help="seconds to wait for health/readiness checks")
    up.set_defaults(func=cmd_up)

    sub.add_parser("down", help="stop tracked lab-owned BF3 services").set_defaults(func=cmd_down)

    services = sub.add_parser("services", help="show managed BF3 service status")
    services.add_argument("--json", action="store_true")
    services.set_defaults(func=cmd_services)

    chatter = sub.add_parser("chatter", help="show recent or live merged service log chatter")
    chatter.add_argument(
        "group",
        nargs="?",
        default="all",
        choices=sorted(set(CHATTER_GROUPS) | {service["id"] for service in SERVICE_INVENTORY}),
        help="service group or individual service log to view",
    )
    chatter.add_argument("--lines", type=int, default=40, help="recent lines to show from each selected service log")
    chatter.add_argument("--follow", action="store_true", help="keep following selected service logs")
    chatter.add_argument("--duration", type=float, default=None, help="optional seconds to follow before exiting")
    chatter.add_argument("--interval", type=float, default=0.35, help="poll interval while following")
    chatter.set_defaults(func=cmd_chatter)

    scenario = sub.add_parser("scenario", help="trigger service-to-service demo traffic/chatter")
    scenario.add_argument("name", choices=SCENARIO_CHOICES, help="scenario to trigger")
    scenario.add_argument("--dry-run", action="store_true", help="print planned endpoint calls without making them")
    scenario.add_argument("--count", type=int, default=1, help="number of ticks/sessions/messages to trigger")
    scenario.add_argument("--timeout", type=float, default=5.0, help="per-request timeout in seconds")
    scenario.add_argument("--ue-id", default="ue-demo-001", help="UE identifier used by demo procedures")
    scenario.add_argument("--supi", default="imsi-001010000000001", help="SUPI used by PDU-session scenarios")
    scenario.add_argument("--pdu-session-id", type=int, default=10, help="starting PDU session ID")
    scenario.add_argument("--ue-ip", default="10.0.0.1", help="UE IP used by UPF traffic simulation")
    scenario.add_argument("--verbose", action="store_true", help="print fuller response bodies")
    scenario.set_defaults(func=cmd_scenario)

    sub.add_parser("smoke", help="prepare disposable runtime and run non-daemon smoke readiness").set_defaults(func=cmd_smoke)
    sub.add_parser("test", help="run pytest suite in disposable runtime").set_defaults(func=cmd_test)

    status = sub.add_parser("status", help="show latest readiness evidence")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_status)

    sub.add_parser("demo", help="print concise demo readiness summary").set_defaults(func=cmd_demo)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
