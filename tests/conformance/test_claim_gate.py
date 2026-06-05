from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PROMOTION_FIELDS = [
    "standards body",
    "release or asset version",
    "implementation path",
    "executable test path",
    "conformance level",
    "known gap",
    "next validation step",
]

POLICY_PATHS = [
    ROOT / "traceability" / "claim_hygiene_policy.md",
    ROOT / "traceability" / "evidence_artifact_policy.md",
    ROOT / "docs" / "conformance-boundary.md",
    ROOT / "docs" / "testing.md",
    ROOT / "tests" / "conformance" / "README.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_conformance_scaffold_policy_files_exist():
    for path in POLICY_PATHS:
        assert path.exists(), f"missing conformance policy artifact: {path.relative_to(ROOT)}"


def test_evidence_policy_contains_required_promotion_fields():
    policy = read(ROOT / "traceability" / "evidence_artifact_policy.md").lower()
    for field in REQUIRED_PROMOTION_FIELDS:
        assert field in policy, field


def test_claim_gate_preserves_candidate_readiness_language():
    combined = "\n".join(read(path).lower() for path in POLICY_PATHS)
    for term in ["candidate", "reference", "readiness", "not formal", "known gap"]:
        assert term in combined, term
    policy = read(ROOT / "traceability" / "evidence_artifact_policy.md").lower()
    assert "avoid unless the gate is complete" in policy
    for unsafe in ["production-ready", "certified", "release-complete"]:
        assert unsafe in policy, unsafe


def test_gitignore_recommendations_cover_sensitive_evidence_categories():
    policy = read(ROOT / "traceability" / "evidence_artifact_policy.md").lower()
    for pattern in ["*.pem", "*.key", "*.db", "*.pcap", "specs/**/*.pdf", "logs/"]:
        assert pattern in policy, pattern
