import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.order_engine.order_service import create_product_order
from services.orchestration import orchestration_service
from services.orchestration.api import create_app


def activation_plan(correlation_id="corr-orch-unit-0001"):
    return create_product_order(
        product_id="prod-5g-data-basic",
        correlation_id=correlation_id,
        customer_id="customer-demo-001",
    )["activation_plan"]


def test_orchestration_maps_activation_plan_to_mock_core_adapter_request():
    plan = activation_plan()
    adapter_requests = []

    def mock_adapter(request):
        adapter_requests.append(request)
        return {
            "correlation_id": request["correlation_id"],
            "service_id": request["service_id"],
            "mock_activation_result": "accepted",
            "adapter_contract_version": "mvp-0.1",
        }

    result = orchestration_service.orchestrate_activation(plan, mock_core_adapter=mock_adapter)

    assert len(adapter_requests) == 1
    request = adapter_requests[0]
    assert request["correlation_id"] == "corr-orch-unit-0001"
    assert request["order_id"] == plan["order_id"]
    assert request["service_id"] == plan["service_id"]
    assert request["subscriber_intent"] == "subscriber=demo-enterprise-001; access=5g-data"
    assert request["session_intent"] == "dnn=internet; slice=sst-1; qos=best-effort"
    assert request["adapter_contract_path"] == "adapters/3gpp/ issue #24"
    assert result["adapter_response"]["mock_activation_result"] == "accepted"


def test_orchestration_emits_state_transitions_and_correlation_ids():
    result = orchestration_service.orchestrate_activation(
        activation_plan("corr-orch-unit-0002"),
        mock_core_adapter=lambda request: {
            "correlation_id": request["correlation_id"],
            "service_id": request["service_id"],
            "mock_activation_result": "accepted",
        },
    )

    assert result["correlation_id"] == "corr-orch-unit-0002"
    assert [event["state"] for event in result["state_history"]] == [
        "activation_plan_received",
        "subscriber_session_intent_mapped",
        "mock_core_adapter_invoked",
        "mock_core_adapter_acknowledged",
    ]
    assert all(event["correlation_id"] == "corr-orch-unit-0002" for event in result["state_history"])
    assert result["orchestration_metadata"]["evidence_label"] == "functional_smoke"
    assert "not formal" in result["orchestration_metadata"]["claim_boundary"].lower()


def test_orchestration_rejects_incomplete_activation_plan_before_adapter_call():
    plan = activation_plan("corr-orch-unit-0003")
    del plan["session_intent"]

    def adapter_should_not_run(request):
        raise AssertionError("adapter should not be called for invalid activation plan")

    with pytest.raises(orchestration_service.InvalidActivationPlan):
        orchestration_service.orchestrate_activation(plan, mock_core_adapter=adapter_should_not_run)


def test_orchestration_does_not_import_mock_core_internals():
    source = (ROOT / "services" / "orchestration" / "orchestration_service.py").read_text(encoding="utf-8")

    assert "services.mock_5g_core" not in source
    assert "core_network" not in source


def test_orchestration_api_accepts_activation_plan_with_default_contract_adapter():
    client = TestClient(create_app())
    plan = activation_plan("corr-orch-api-0001")

    response = client.post("/orchestration/v1/service-order-to-activation", json={"activation_plan": plan})

    assert response.status_code == 200
    payload = response.json()
    assert payload["correlation_id"] == "corr-orch-api-0001"
    assert payload["adapter_response"]["mock_activation_result"] == "contract_pending"
    assert payload["adapter_response"]["adapter_contract_path"] == "adapters/3gpp/ issue #24"
