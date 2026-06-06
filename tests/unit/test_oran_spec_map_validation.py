import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_oran_spec_map", ROOT / "scripts" / "validate_oran_spec_map.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def test_validator_resolves_copied_ran_paths_and_reports_missing_paths(tmp_path):
    rows = [
        {"wg": "WG3", "spec": "O-RAN.WG3.TS.E2AP-R004-v08.00", "module": "ran/ric/e2ap.py", "status": "implemented"},
        {"wg": "WG2", "spec": "O-RAN.WG2.TS.R1AP-R005-v10.00", "module": "smo/r1.py", "status": "implemented"},
    ]
    result = validator.validate_rows(rows, spec_dir=None)

    assert result["summary"]["rows_total"] == 2
    assert result["summary"]["module_paths_existing"] == 2
    assert result["summary"]["module_paths_missing"] == 0
    resolved = {row["module"]: row["resolved_module_path"] for row in result["rows"]}
    assert resolved["ran/ric/e2ap.py"] == "adapters/mock_ran/ran/ric/e2ap.py"
    assert resolved["smo/r1.py"] == "adapters/mock_oran/smo/r1.py"
    assert result["summary"]["claim_boundary"].startswith("candidate/readiness")


def test_validator_matches_spec_filename_stems_without_reading_raw_docs(tmp_path):
    (tmp_path / "O-RAN.WG2.TS.A1AP-R005-v06.00.pdf").write_bytes(b"not read by validator")
    (tmp_path / "Codex.dmg").write_bytes(b"ignored non-spec artifact")
    rows = [
        {"wg": "WG2", "spec": "O-RAN.WG2.TS.A1AP-R005-v06.00", "module": "ran/ric/non_rt_ric.py"},
        {"wg": "WG2", "spec": "O-RAN.WG2.TS.MISSING-v00.00", "module": "ran/ric/non_rt_ric.py"},
    ]

    result = validator.validate_rows(rows, spec_dir=tmp_path)

    assert result["summary"]["local_spec_catalog_checked"] is True
    assert result["summary"]["local_spec_files_indexed"] == 1
    assert result["summary"]["spec_files_existing"] == 1
    assert result["summary"]["spec_files_missing"] == 1
    matched = {row["spec"]: row["resolved_spec_file"] for row in result["rows"]}
    assert matched["O-RAN.WG2.TS.A1AP-R005-v06.00"] == "O-RAN.WG2.TS.A1AP-R005-v06.00.pdf"
    assert matched["O-RAN.WG2.TS.MISSING-v00.00"] is None


def test_markdown_report_keeps_validation_boundary_language():
    result = validator.validate_rows([], spec_dir=None)
    report = validator.markdown_report(result)

    assert "not a formal O-RAN conformance claim" in report
    assert "Rows checked: 0" in report
