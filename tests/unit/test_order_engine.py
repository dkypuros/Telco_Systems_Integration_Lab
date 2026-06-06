import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.order_engine import order_service
from services.order_engine.api import create_app


def test_order_engine_creates_basic_5g_order_with_lifecycle_and_correlation_metadata():
    result = order_service.create_product_order(
        product_id="prod-5g-data-basic",
        correlation_id="corr-order-unit-0001",
        customer_id="customer-demo-001",
    )

    assert result["correlation_id"] == "corr-order-unit-0001"
    assert result["order"]["id"].startswith("order-")
    assert result["order"]["product_id"] == "prod-5g-data-basic"
    assert [event["state"] for event in result["order"]["state_history"]] == [
        "acknowledged",
        "activation_requested",
    ]
    assert result["order_metadata"]["evidence_label"] == "functional_smoke"
    assert result["order_metadata"]["standards_reference"]["spec_id"] == "TMF622"


def test_order_engine_rejects_unknown_product_before_activation_plan():
    with pytest.raises(order_service.InvalidProductOrder):
        order_service.create_product_order(
            product_id="prod-does-not-exist",
            correlation_id="corr-order-unit-0002",
            customer_id="customer-demo-001",
        )


def test_order_engine_activation_plan_carries_service_and_network_intent_shape():
    result = order_service.create_product_order(
        product_id="prod-5g-data-basic",
        correlation_id="corr-order-unit-0003",
        customer_id="customer-demo-001",
    )
    plan = result["activation_plan"]

    assert plan["correlation_id"] == "corr-order-unit-0003"
    assert plan["service_id"].startswith("svc-")
    assert plan["network_action"] == "activate_mock_5g_data_service"
    assert plan["subscriber_intent"] == "subscriber=demo-enterprise-001; access=5g-data"
    assert plan["session_intent"] == "dnn=internet; slice=sst-1; qos=best-effort"
    assert plan["handoff"]["service_order_mapping"] == "services/orchestration/ issue #23"
    assert plan["handoff"]["mock_core_adapter"] == "adapters/3gpp/ issue #24"
    assert plan["standards_reference"]["service_order_spec_id"] == "TMF641"
    assert "not formal" in plan["claim_boundary"].lower()


def test_product_order_api_accepts_basic_order_and_returns_activation_plan():
    client = TestClient(create_app())

    response = client.post(
        "/tmf-api/productOrderingManagement/v5/productOrder",
        json={"product_id": "prod-5g-data-basic", "customer_id": "customer-demo-001"},
        headers={"x-correlation-id": "corr-order-api-0001"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["correlation_id"] == "corr-order-api-0001"
    assert payload["order"]["state"] == "activation_requested"
    assert payload["activation_plan"]["product_id"] == "prod-5g-data-basic"
    assert payload["activation_plan"]["service_id"].startswith("svc-")


def test_product_order_api_rejects_unknown_product_with_400():
    client = TestClient(create_app())

    response = client.post(
        "/tmf-api/productOrderingManagement/v5/productOrder",
        json={"product_id": "prod-does-not-exist", "customer_id": "customer-demo-001"},
        headers={"x-correlation-id": "corr-order-api-0002"},
    )

    assert response.status_code == 400
    assert "unknown product_id" in response.json()["detail"]
