import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.catalog_api.catalog_service import lookup_product
from services.order_engine.order_service import create_product_order
from services.orchestration.orchestration_service import orchestrate_activation

ADAPTER_PATH = ROOT / "adapters" / "3gpp" / "mock_core_activation_adapter.py"
SNAPSHOT_PATH = ROOT / "traceability" / "evidence_snapshots" / "service-order-to-activation-demo-evidence-bundle.json"
PRIVATE_PATH_RE = re.compile(r"/(Users|home)/[^\s\"']+")
UNSAFE_CLAIM_RE = re.compile(r"\b(production-ready|certified|release-complete)\b", re.IGNORECASE)


def load_adapter_module():
    spec = importlib.util.spec_from_file_location("mock_core_activation_adapter", ADAPTER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from flatten_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from flatten_strings(item)


def assert_public_safe(bundle: dict[str, Any]) -> None:
    text_values = "\n".join(flatten_strings(bundle))
    assert not PRIVATE_PATH_RE.search(text_values)
    assert not UNSAFE_CLAIM_RE.search(text_values)
    assert all(not path.startswith("/") for path in bundle["artifact_paths"])
    assert "not formal" in bundle["claim_boundary"].lower()


def assert_minimal_schema(bundle: dict[str, Any]) -> None:
    required_fields = [
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
    assert list(bundle) == required_fields
    assert bundle["schema_version"] == "1.0"
    assert bundle["evidence_label"] == "demo_evidence"
    assert bundle["capability_slice"] == "service_order_to_activation/"
    assert bundle["correlation_id"].startswith("corr-")
    assert bundle["touched_components"]
    assert bundle["standards_rows"]
    assert bundle["known_gaps"]


def build_service_order_to_activation_demo_evidence() -> tuple[dict[str, Any], dict[str, Any]]:
    correlation_id = "corr-soa-demo-0001"
    product_id = "prod-5g-data-basic"
    customer_id = "customer-demo-001"
    adapter = load_adapter_module()

    catalog = lookup_product(product_id, correlation_id=correlation_id)
    order_result = create_product_order(
        product_id=catalog["product_id"],
        correlation_id=correlation_id,
        customer_id=customer_id,
    )
    orchestration = orchestrate_activation(
        order_result["activation_plan"],
        mock_core_adapter=adapter.activate_subscriber_session,
    )
    adapter_response = orchestration["adapter_response"]

    order = order_result["order"]
    activation_plan = order_result["activation_plan"]
    all_correlation_ids = {
        catalog["correlation_id"],
        catalog["catalog_metadata"]["correlation_id"],
        order_result["correlation_id"],
        order["correlation_id"],
        activation_plan["correlation_id"],
        orchestration["correlation_id"],
        orchestration["adapter_request"]["correlation_id"],
        adapter_response["correlation_id"],
        *{event["correlation_id"] for event in order["state_history"]},
        *{event["correlation_id"] for event in orchestration["state_history"]},
    }

    bundle = {
        "schema_version": "1.0",
        "correlation_id": correlation_id,
        "recorded_at": "2026-06-06T00:00:00Z",
        "scenario": "service_order_to_activation_mvp_demo",
        "capability_slice": "service_order_to_activation/",
        "evidence_label": "demo_evidence",
        "claim_boundary": "Repeatable local MVP demo evidence only; not formal 3GPP, O-RAN, or TM Forum conformance.",
        "inputs": {
            "product_id": product_id,
            "order_id": order["id"],
            "service_id": activation_plan["service_id"],
            "subscriber_id": adapter_response["subscriber_profile"]["subscriber"],
            "subscriber_intent": activation_plan["subscriber_intent"],
            "session_intent": activation_plan["session_intent"],
            "customer_id": customer_id,
            "network_action": activation_plan["network_action"],
            "mock_activation_result": adapter_response["mock_activation_result"],
        },
        "touched_components": [
            {
                "path": "services/catalog_api/",
                "role": "TMF620-referenced product lookup",
                "evidence_note": "Returned the basic 5G data product with the shared correlation_id.",
            },
            {
                "path": "services/order_engine/",
                "role": "TMF622/TMF641-referenced product order lifecycle and activation-plan output",
                "evidence_note": "Created acknowledged -> activation_requested order state and activation plan.",
            },
            {
                "path": "services/orchestration/",
                "role": "Lab-owned orchestration graph",
                "evidence_note": "Mapped the activation plan to subscriber/session intent and invoked the adapter contract.",
            },
            {
                "path": "adapters/3gpp/mock_core_activation_adapter.py",
                "role": "3GPP-referenced mock-core activation adapter",
                "evidence_note": "Recorded a controlled local mock-core subscriber/session activation result.",
            },
            {
                "path": "tests/integration/test_service_order_to_activation_evidence.py",
                "role": "Repeatable MVP integration test",
                "evidence_note": "Asserts the shared correlation_id and public-safe evidence bundle shape.",
            },
        ],
        "standards_rows": [
            {
                "standards_body": "TM Forum",
                "spec_id": "TMF620",
                "release_register_path": "traceability/standards_release_register.yaml",
                "conformance_level": "demo_evidence for local MVP product lookup only",
                "known_gap_to_latest": "formal TM Forum CTK evidence missing for this MVP path",
            },
            {
                "standards_body": "TM Forum",
                "spec_id": "TMF622",
                "release_register_path": "traceability/standards_release_register.yaml",
                "conformance_level": "demo_evidence for local MVP order lifecycle only",
                "known_gap_to_latest": "formal TM Forum CTK evidence missing for this MVP path",
            },
            {
                "standards_body": "TM Forum",
                "spec_id": "TMF641",
                "release_register_path": "traceability/standards_release_register.yaml",
                "conformance_level": "demo_evidence for activation-plan handoff only",
                "known_gap_to_latest": "formal service-order conformance evidence missing",
            },
            {
                "standards_body": "3GPP",
                "spec_id": "release-baseline",
                "release_register_path": "traceability/standards_release_register.yaml",
                "conformance_level": "functional mock activation evidence only",
                "known_gap_to_latest": "formal 3GPP protocol conformance evidence missing",
            },
        ],
        "artifact_paths": [
            "tests/integration/test_service_order_to_activation_evidence.py",
            "traceability/evidence_snapshots/service-order-to-activation-demo-evidence-bundle.json",
            "capabilities/service_order_to_activation/flow-contract.yaml",
        ],
        "known_gaps": [
            "No external implementation profile is exercised by this MVP demo evidence.",
            "No formal TM Forum CTK result is produced by this MVP demo evidence.",
            "No formal 3GPP protocol conformance evidence is produced by this MVP demo evidence.",
            "No O-RAN behavior is exercised by this first service-order-to-activation MVP path.",
        ],
        "next_validation_step": "Use this repeatable MVP evidence as the baseline before adding subscriber lifecycle, slice provisioning, RAN/O-RAN control-loop, or ODA/O2/OCP architecture slices.",
    }

    execution = {
        "catalog": catalog,
        "order_result": order_result,
        "orchestration": orchestration,
        "adapter_response": adapter_response,
        "all_correlation_ids": all_correlation_ids,
    }
    return bundle, execution


def test_service_order_to_activation_path_records_one_correlation_id_and_activation_result():
    bundle, execution = build_service_order_to_activation_demo_evidence()

    assert execution["all_correlation_ids"] == {bundle["correlation_id"]}
    assert execution["order_result"]["order"]["state"] == "activation_requested"
    assert execution["orchestration"]["adapter_response"]["mock_activation_result"] == "activated"
    assert execution["orchestration"]["adapter_response"]["mock_core_surface"] == "controlled_local_stub"
    assert [event["state"] for event in execution["orchestration"]["state_history"]] == [
        "activation_plan_received",
        "subscriber_session_intent_mapped",
        "mock_core_adapter_invoked",
        "mock_core_adapter_acknowledged",
    ]


def test_service_order_to_activation_demo_evidence_snapshot_is_public_safe_and_current():
    expected_bundle, execution = build_service_order_to_activation_demo_evidence()
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert snapshot == expected_bundle
    assert_minimal_schema(snapshot)
    assert_public_safe(snapshot)
    assert snapshot["inputs"]["order_id"] == execution["order_result"]["order"]["id"]
    assert snapshot["inputs"]["service_id"] == execution["order_result"]["activation_plan"]["service_id"]
    assert snapshot["inputs"]["mock_activation_result"] == "activated"
    assert len({row["spec_id"] for row in snapshot["standards_rows"]}) == 4
