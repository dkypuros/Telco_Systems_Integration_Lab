import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("lab_cli", ROOT / "scripts" / "lab_cli.py")
assert SPEC and SPEC.loader
lab_cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab_cli)


def tracked_record(service, command):
    return {
        "owner": lab_cli.LAB_OWNER,
        "command": command,
        "marker": lab_cli.service_marker(service),
        "pgid": 777,
        "process_start_signature": "Fri Jun  5 09:00:00 2026",
    }


def patch_live_process(monkeypatch, command, *, cwd=""):
    monkeypatch.setattr(lab_cli, "pid_alive", lambda pid: True)
    monkeypatch.setattr(lab_cli, "process_group", lambda pid: 777)
    monkeypatch.setattr(lab_cli, "process_start_signature", lambda pid: "Fri Jun  5 09:00:00 2026")
    monkeypatch.setattr(lab_cli, "pid_command", lambda pid: command)
    monkeypatch.setattr(lab_cli, "pid_cwd", lambda pid: cwd)


def test_managed_inventory_uses_clean_domain_service_roots():
    commands = [" ".join(lab_cli.service_cmd(service, "rest")) for service in lab_cli.SERVICE_INVENTORY]
    paths = [str(lab_cli.service_path(service)) for service in lab_cli.SERVICE_INVENTORY]
    assert commands
    assert all("main.py" not in command for command in commands)
    assert any("core_network/nrf.py" in path for path in paths)
    assert any("api_gateway/oran_gateway.py" in path for path in paths)
    assert {service["root"] for service in lab_cli.SERVICE_INVENTORY} <= set(lab_cli.RUNTIME_ROOTS)


def test_safe_to_terminate_requires_lab_owner(monkeypatch):
    service = lab_cli.SERVICE_INVENTORY[0]
    command = lab_cli.service_cmd(service, "rest")
    patch_live_process(monkeypatch, " ".join(command))

    safe, detail = lab_cli.safe_to_terminate(12345, {"command": command, "marker": lab_cli.service_marker(service)})

    assert safe is False
    assert "owner" in detail


def test_safe_to_terminate_rejects_stale_pid_command(monkeypatch):
    service = lab_cli.SERVICE_INVENTORY[0]
    command = lab_cli.service_cmd(service, "rest")
    record = tracked_record(service, command)
    patch_live_process(monkeypatch, "/usr/bin/python unrelated_server.py")

    safe, detail = lab_cli.safe_to_terminate(12345, record)

    assert safe is False
    assert "did not match" in detail


def test_safe_to_terminate_rejects_pid_reuse_signature(monkeypatch):
    service = lab_cli.SERVICE_INVENTORY[0]
    command = lab_cli.service_cmd(service, "rest")
    record = tracked_record(service, command)
    patch_live_process(monkeypatch, " ".join(command))
    monkeypatch.setattr(lab_cli, "process_start_signature", lambda pid: "Fri Jun  5 10:00:00 2026")

    safe, detail = lab_cli.safe_to_terminate(12345, record)

    assert safe is False
    assert "signature" in detail


def test_safe_to_terminate_accepts_recorded_service_command(monkeypatch):
    service = lab_cli.SERVICE_INVENTORY[0]
    command = lab_cli.service_cmd(service, "rest")
    record = tracked_record(service, command)
    patch_live_process(monkeypatch, " ".join(command))

    safe, detail = lab_cli.safe_to_terminate(12345, record)

    assert safe is True
    assert "verified" in detail


def test_safe_to_terminate_accepts_module_service_when_cwd_matches(monkeypatch):
    service = next(item for item in lab_cli.SERVICE_INVENTORY if item["id"] == "assurance")
    command = lab_cli.service_cmd(service, "rest")
    record = tracked_record(service, command)
    patch_live_process(
        monkeypatch,
        "/opt/homebrew/bin/python -m service_assurance.assurance_api --host 0.0.0.0 --port 9011",
        cwd=str(lab_cli.RUNTIME_ROOTS["assurance"]),
    )

    safe, detail = lab_cli.safe_to_terminate(12345, record)

    assert safe is True
    assert "verified" in detail


def test_service_paths_resolve_inside_clean_domain_buckets():
    for service in lab_cli.SERVICE_INVENTORY:
        path = lab_cli.service_path(service)
        assert path.is_relative_to(lab_cli.RUNTIME_ROOTS[service["root"]])


def test_demo_marks_missing_smoke_and_test_evidence_as_not_run(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(lab_cli, "SMOKE_LOG", tmp_path / "missing-smoke.json")
    monkeypatch.setattr(lab_cli, "TEST_LOG", tmp_path / "missing-pytest.log")
    monkeypatch.setattr(lab_cli, "STATUS_LOG", tmp_path / "status.json")
    monkeypatch.setattr(
        lab_cli,
        "services_report",
        lambda: {
            "ready": 26,
            "total": 26,
            "all_ready": True,
            "external": [],
            "failed": [],
            "state_file": "<state>",
            "evidence_file": "<evidence>",
            "log_dir": "<logs>",
        },
    )

    result = lab_cli.cmd_demo(object())

    output = capsys.readouterr().out
    assert result == 2
    assert "Managed lab services up:   YES (26/26)" in output
    assert "Runtime-ready mock imports: NOT RUN" in output
    assert "Regression tests passing:   NOT RUN" in output
    assert "Copied AST/import scope:    NOT RUN (run ./lab smoke)" in output
    assert "Next: run ./lab smoke && ./lab test" in output
