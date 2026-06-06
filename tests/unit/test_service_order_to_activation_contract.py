import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "capabilities" / "service_order_to_activation" / "flow-contract.yaml"
README_PATH = ROOT / "capabilities" / "service_order_to_activation" / "README.md"
PLANNED_BUNDLE_PATH = ROOT / "traceability" / "evidence_snapshots" / "service-order-to-activation-planned-evidence-bundle.json"

REQUIRED_IDENTIFIERS = {
    "correlation_id",
    "product_id",
    "order_id",
    "service_id",
    "subscriber_intent",
    "session_intent",
}

REQUIRED_STEPS = [
    "01_catalog_product_lookup",
    "02_product_order_create",
    "03_service_activation_plan",
    "04_orchestration_intent_mapping",
    "05_mock_core_activation_adapter",
    "06_evidence_bundle_record",
]


def load_contract():
    return yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_mvp_contract_names_required_identifiers_and_flow_order():
    contract = load_contract()
    identifiers = {item["name"] for item in contract["identifiers"]}
    assert REQUIRED_IDENTIFIERS <= identifiers
    assert [step["step_id"] for step in contract["flow_steps"]] == REQUIRED_STEPS

    for step in contract["flow_steps"]:
        assert "correlation_id" in step["input_identifiers"]
        assert "correlation_id" in step["output_identifiers"]


def test_mvp_contract_stays_planned_and_blocks_upstream_absorption():
    contract = load_contract()
    assert contract["capability_slice"] == "service_order_to_activation/"
    assert contract["current_evidence_label"] == "planned"
    assert contract["target_evidence_label"] == "planned"
    assert contract["future_promotion_label_after_implementation"] == "demo_evidence"
    assert contract["external_upstream_required"] is False
    assert "No full external upstream repository" in contract["source_intake_boundary"]
    assert "not formal" in contract["claim_boundary"].lower()


def test_mvp_contract_maps_expected_standards_and_implementation_scopes():
    contract = load_contract()
    standards = {row for step in contract["flow_steps"] for row in step["standards_rows"]}
    for expected in ["TMF620", "TMF622", "TMF641", "TMF640", "3GPP release-baseline"]:
        assert expected in standards

    paths = {step["planned_path"] for step in contract["flow_steps"]}
    for expected_path in [
        "services/catalog_api/",
        "services/order_engine/",
        "services/orchestration/",
        "adapters/3gpp/",
        "traceability/evidence_snapshots/",
    ]:
        assert expected_path in paths


def test_readme_documents_the_api_first_mvp_path_and_acceptance_gate():
    readme = README_PATH.read_text(encoding="utf-8").lower()
    for phrase in [
        "product/catalog -> product order -> activation/orchestration -> mock 5g core adapter -> evidence bundle",
        "correlation_id",
        "subscriber_intent",
        "session_intent",
        "does not prove formal standards conformance",
        "tests that run without external upstream repositories",
    ]:
        assert phrase in readme


def test_planned_evidence_bundle_records_contract_inputs_and_known_gaps():
    bundle = json.loads(PLANNED_BUNDLE_PATH.read_text(encoding="utf-8"))
    assert bundle["capability_slice"] == "service_order_to_activation/"
    assert bundle["evidence_label"] == "planned"
    assert "not formal" in bundle["claim_boundary"].lower()
    assert bundle["correlation_id"].startswith("corr-soa-")
    assert (REQUIRED_IDENTIFIERS - {"correlation_id"}) <= set(bundle["inputs"])
    assert all(not path.startswith("/") for path in bundle["artifact_paths"])
    assert any("No external implementation profile" in gap for gap in bundle["known_gaps"])
