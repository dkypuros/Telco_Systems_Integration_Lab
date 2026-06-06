import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.catalog_api import catalog_service
from services.catalog_api.api import create_app

FIXTURE_PATH = ROOT / "models" / "standard_native" / "tmf" / "product_catalog" / "basic_5g_data_service.json"


def test_catalog_service_returns_basic_5g_data_product_with_correlation_metadata():
    response = catalog_service.lookup_product(
        "prod-5g-data-basic",
        correlation_id="corr-catalog-unit-0001",
    )

    assert response["correlation_id"] == "corr-catalog-unit-0001"
    assert response["product_id"] == "prod-5g-data-basic"
    assert response["product"]["id"] == "prod-5g-data-basic"
    assert response["catalog_metadata"]["evidence_label"] == "functional_smoke"
    assert response["catalog_metadata"]["source_model_path"] == "models/standard_native/tmf/product_catalog/basic_5g_data_service.json"
    assert response["catalog_metadata"]["standards_reference"]["spec_id"] == "TMF620"


def test_catalog_fixture_preserves_bounded_tmf620_claim_boundary():
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture["id"] == "prod-5g-data-basic"
    assert fixture["lifecycleStatus"] == "Active"
    assert fixture["standards_reference"]["evidence_label"] == "functional_smoke"
    assert "not formal" in fixture["standards_reference"]["claim_boundary"].lower()
    assert fixture["standards_reference"]["release_register_path"] == "traceability/standards_release_register.yaml"


def test_catalog_service_rejects_unknown_product_without_fallback():
    with pytest.raises(catalog_service.ProductNotFound):
        catalog_service.lookup_product("prod-does-not-exist", correlation_id="corr-catalog-unit-0002")


def test_catalog_api_returns_tmf_style_product_with_correlation_header():
    client = TestClient(create_app())

    response = client.get(
        "/tmf-api/productCatalogManagement/v5/productSpecification/prod-5g-data-basic",
        headers={"x-correlation-id": "corr-catalog-api-0001"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["correlation_id"] == "corr-catalog-api-0001"
    assert payload["product"]["id"] == "prod-5g-data-basic"
    assert payload["product"]["@type"] == "ProductSpecification"
    assert payload["catalog_metadata"]["claim_boundary"].startswith("Functional smoke")
