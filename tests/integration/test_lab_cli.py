import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_lab(*args):
    return subprocess.run([str(ROOT / "lab"), *args], cwd=ROOT, text=True, capture_output=True, check=False)


def test_lab_status_json_has_caveat():
    result = run_lab("status", "--json")
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert "Runtime/demo readiness only" in data["caveat"]
    assert "runtime_smoke" in data


def test_lab_demo_prints_readiness_language():
    # demo may return 2 before up/test evidence exists; it still must articulate status clearly.
    result = run_lab("demo")
    assert "Telco Systems Integration Lab Demo Readiness" in result.stdout
    assert "What it does not claim" in result.stdout


def test_lab_up_dry_run_lists_managed_services():
    result = run_lab("up", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "managed BF3 5G/RAN/O-RAN services" in result.stdout
    assert "core_network/nrf.py" in result.stdout
    assert "api_gateway/oran_gateway.py" in result.stdout
    assert "--protocol-mode rest" in result.stdout
    assert "5G_Emulator_API/main.py" not in result.stdout
    assert "foreground" not in result.stdout.lower()


def test_lab_services_json_shape():
    result = run_lab("services", "--json")
    # services exits non-zero when the stack is not up; the JSON still must be diagnostic.
    data = json.loads(result.stdout)
    assert data["total"] >= 20
    assert "services" in data
    assert "caveat" in data


def test_lab_chatter_snapshot_exits_without_services():
    result = run_lab("chatter", "radio", "--lines", "0")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "lab chatter" in result.stdout
    assert "Use --follow" in result.stdout


def test_lab_scenario_dry_run_describes_pdu_chain():
    result = run_lab("scenario", "pdu-session", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "AMF trigger PDU session" in result.stdout
    assert "SMF direct fallback" in result.stdout
    assert "UPF simulate user traffic" in result.stdout
