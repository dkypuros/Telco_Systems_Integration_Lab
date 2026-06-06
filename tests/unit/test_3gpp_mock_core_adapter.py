import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.order_engine.order_service import create_product_order
from services.orchestration.orchestration_service import build_mock_core_adapter_request, orchestrate_activation

ADAPTER_PATH = ROOT / "adapters" / "3gpp" / "mock_core_activation_adapter.py"
API_PATH = ROOT / "adapters" / "3gpp" / "api.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


adapter = load_module("mock_core_activation_adapter", ADAPTER_PATH)
adapter_api = load_module("mock_core_activation_adapter_api", API_PATH)


def adapter_request(correlation_id="corr-adapter-unit-0001"):
    plan = create_product_order(
        product_id="prod-5g-data-basic",
        correlation_id=correlation_id,
        customer_id="customer-demo-001",
    )["activation_plan"]
    return build_mock_core_adapter_request(plan)


def test_adapter_activates_subscriber_session_with_controlled_local_stub():
    result = adapter.activate_subscriber_session(adapter_request())

    assert result["correlation_id"] == "corr-adapter-unit-0001"
    assert result["service_id"].startswith("svc-")
    assert result["mock_activation_result"] == "activated"
    assert result["activation_state"] == "session_activation_recorded"
    assert result["mock_core_surface"] == "controlled_local_stub"
    assert result["subscriber_profile"]["access"] == "5g-data"
    assert result["session_profile"]["dnn"] == "internet"
    assert result["session_profile"]["slice"] == "sst-1"
    assert result["evidence_metadata"]["evidence_label"] == "functional_smoke"
    assert result["evidence_metadata"]["standards_reference"]["spec_id"] == "3GPP release-baseline"
    assert "not formal" in result["evidence_metadata"]["claim_boundary"].lower()


def test_adapter_accepts_injected_mock_core_surface_without_external_runtime():
    calls = []

    def fake_mock_core_surface(payload):
        calls.append(payload)
        return {
            "surface": "injected_test_double",
            "status": "accepted",
            "nf_sequence": ["UDR", "UDM", "AMF", "SMF", "UPF"],
        }

    result = adapter.activate_subscriber_session(
        adapter_request("corr-adapter-unit-0002"),
        mock_core_surface=fake_mock_core_surface,
    )

    assert len(calls) == 1
    assert calls[0]["correlation_id"] == "corr-adapter-unit-0002"
    assert calls[0]["network_action"] == "activate_mock_5g_data_service"
    assert result["mock_core_surface"] == "injected_test_double"
    assert result["mock_core_response"]["nf_sequence"] == ["UDR", "UDM", "AMF", "SMF", "UPF"]


def test_adapter_rejects_missing_required_fields_before_surface_call():
    request = adapter_request("corr-adapter-unit-0003")
    del request["subscriber_intent"]

    def should_not_run(payload):
        raise AssertionError("mock core surface should not be called for invalid adapter request")

    with pytest.raises(adapter.InvalidMockCoreActivationRequest):
        adapter.activate_subscriber_session(request, mock_core_surface=should_not_run)


def test_adapter_integrates_with_orchestration_as_concrete_callable():
    plan = create_product_order(
        product_id="prod-5g-data-basic",
        correlation_id="corr-adapter-orch-0001",
        customer_id="customer-demo-001",
    )["activation_plan"]

    result = orchestrate_activation(plan, mock_core_adapter=adapter.activate_subscriber_session)

    assert result["adapter_response"]["mock_activation_result"] == "activated"
    assert result["adapter_response"]["correlation_id"] == "corr-adapter-orch-0001"
    assert result["adapter_response"]["adapter_contract_version"] == "mvp-0.1"


def test_adapter_api_exposes_activation_route():
    client = TestClient(adapter_api.create_app())

    response = client.post("/adapters/3gpp/v1/mock-core/activate", json=adapter_request("corr-adapter-api-0001"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["correlation_id"] == "corr-adapter-api-0001"
    assert payload["mock_activation_result"] == "activated"


def test_adapter_source_does_not_import_external_upstream_repos_or_rewrite_mock_core():
    source = ADAPTER_PATH.read_text(encoding="utf-8")

    for forbidden in ["open5gs", "free5gc", "openairinterface", "subprocess", "services.mock_5g_core"]:
        assert forbidden not in source.lower()
