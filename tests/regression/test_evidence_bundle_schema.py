import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "traceability" / "evidence_bundle.schema.json"
EXAMPLE_PATH = ROOT / "traceability" / "evidence_snapshots" / "example-mvp-evidence-bundle.json"
DOC_PATH = ROOT / "docs" / "evidence-bundles.md"

REQUIRED_FIELDS = [
    "schema_version",
    "correlation_id",
    "recorded_at",
    "scenario",
    "capability_slice",
    "evidence_label",
    "claim_boundary",
    "inputs",
    "touched_components",
    "standards_rows",
    "artifact_paths",
    "known_gaps",
    "next_validation_step",
]

ALLOWED_LABELS = {
    "reference_only",
    "planned",
    "partial",
    "functional_smoke",
    "demo_evidence",
    "formal_conformance_missing",
    "conformance_candidate",
    "formal_conformance_evidence",
}

PRIVATE_PATH_RE = re.compile(r"/(Users|home)/[^\s\"']+")
UNSAFE_CLAIM_RE = re.compile(r"\b(production-ready|certified|release-complete)\b", re.IGNORECASE)


def flatten_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from flatten_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from flatten_strings(v)


def test_evidence_bundle_schema_and_example_exist_with_required_fields():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    assert DOC_PATH.exists()

    assert schema["required"] == REQUIRED_FIELDS
    for field in REQUIRED_FIELDS:
        assert field in example
    assert example["evidence_label"] in ALLOWED_LABELS
    assert example["correlation_id"].startswith("corr-")
    assert example["standards_rows"]


def test_evidence_bundle_example_is_public_safe_and_bounded():
    example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    text_values = "\n".join(flatten_strings(example))
    assert not PRIVATE_PATH_RE.search(text_values)
    assert not UNSAFE_CLAIM_RE.search(text_values)
    assert "not formal" in example["claim_boundary"].lower()
    assert all(not path.startswith("/") for path in example["artifact_paths"])


def test_evidence_docs_define_correlation_id_and_claim_boundary():
    docs = DOC_PATH.read_text(encoding="utf-8").lower()
    for phrase in [
        "correlation_id",
        "functional_smoke",
        "demo_evidence",
        "do not prove formal",
        "private local paths",
    ]:
        assert phrase in docs
