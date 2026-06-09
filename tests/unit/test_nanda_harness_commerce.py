import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experimental" / "nanda_harness_commerce"


def load_fixture(name: str):
    return json.loads((EXP / "fixtures" / name).read_text(encoding="utf-8"))


def test_nanda_harness_commerce_plan_matches_golden_fixture():
    sys.path.insert(0, str(EXP))
    from simulator import build_plan

    plan = build_plan(
        load_fixture("intent.json"),
        load_fixture("nanda_index.json"),
        load_fixture("harness_policy.json"),
    )
    assert plan == load_fixture("expected_plan.json")


def test_verified_import_is_disabled_until_human_approval():
    expected = load_fixture("expected_plan.json")
    assert expected["status"] == "awaiting_human_approval"
    assert len(expected["verified_imports"]) == 1
    verified = expected["verified_imports"][0]
    assert verified["enabled"] is False
    assert verified["human_approval_required"] is True
    assert "human_approval_required" in verified["governance_checks"]


def test_rejected_candidates_capture_trust_quality_governance_and_capability_failures():
    rejected = {
        item["agent_id"]: item["reasons"] for item in load_fixture("expected_plan.json")["rejected_candidates"]
    }
    cheap = rejected["did:web:unknown-market.example:agent:cheap-audit"]
    for reason in [
        "issuer_not_allowed",
        "quality_below_threshold",
        "risk_exceeds_policy",
        "audit_or_revocation_missing",
        "human_approval_not_required_by_candidate",
    ]:
        assert reason in cheap
    assert any(reason.startswith("required_evidence_missing:") for reason in cheap)
    assert rejected["did:web:trusted-nanda-lab.example:agent:edge-token-broker"] == [
        "capability_mismatch"
    ]


def test_cli_emits_same_plan_as_library():
    result = subprocess.run(
        [
            sys.executable,
            str(EXP / "simulator.py"),
            "--intent",
            str(EXP / "fixtures" / "intent.json"),
            "--index",
            str(EXP / "fixtures" / "nanda_index.json"),
            "--policy",
            str(EXP / "fixtures" / "harness_policy.json"),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    assert json.loads(result.stdout) == load_fixture("expected_plan.json")


def test_docs_index_links_nanda_harness_concept_and_preserves_claim_boundary():
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    concept = (ROOT / "docs" / "nanda-harness-agentic-commerce.md").read_text(encoding="utf-8")
    readme = (EXP / "README.md").read_text(encoding="utf-8")

    assert "nanda-harness-agentic-commerce.md" in docs_index
    for phrase in [
        "not a live NANDA integration",
        "not a payment rail",
        "not a formal standards conformance claim",
    ]:
        assert phrase in concept
    assert "does not call a live NANDA Index" in readme
    assert "awaiting_human_approval" in readme
