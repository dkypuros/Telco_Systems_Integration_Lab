import ast
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


TRACKED_COPY_STATUSES = {"copied", "copied_remediated"}


def tracked_manifest_rows():
    with (ROOT / "traceability" / "copy_manifest.csv").open(newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("status") in TRACKED_COPY_STATUSES:
                yield row


def test_copied_manifest_destinations_match_recorded_checksums():
    rows = list(tracked_manifest_rows())
    assert len(rows) >= 85
    for row in rows:
        destination = ROOT / row["destination_path"]
        assert destination.exists(), row
        actual = sha256(destination)
        assert actual == row["checksum_destination"], row["destination_path"]
        assert row["verified"] == "true", row["destination_path"]
        if row["status"] == "copied":
            assert row["checksum_source"] == row["checksum_destination"], row["destination_path"]
        else:
            assert row["checksum_source"] != row["checksum_destination"], row["destination_path"]
            assert "claim-hygiene remediation" in row["notes"], row["destination_path"]


def test_copied_python_files_parse():
    py_files = sorted((ROOT / "services" / "mock_5g_core").rglob("*.py"))
    py_files += sorted((ROOT / "adapters" / "mock_ran").rglob("*.py"))
    py_files += sorted((ROOT / "adapters" / "mock_oran").rglob("*.py"))
    assert len(py_files) >= 25
    for path in py_files:
        ast.parse(path.read_text())
