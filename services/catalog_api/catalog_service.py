"""Small catalog service surface for the MVP service-order-to-activation slice.

The fixture is TMF620-referenced and intentionally bounded to functional-smoke
behavior. It is not formal TM Forum conformance evidence.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_MODEL_PATH = REPO_ROOT / "models" / "standard_native" / "tmf" / "product_catalog" / "basic_5g_data_service.json"
CATALOG_MODEL_RELATIVE_PATH = "models/standard_native/tmf/product_catalog/basic_5g_data_service.json"
DEFAULT_PRODUCT_ID = "prod-5g-data-basic"


class ProductNotFound(KeyError):
    """Raised when the MVP catalog has no product for the requested ID."""


def _load_product_fixture() -> dict[str, Any]:
    return json.loads(CATALOG_MODEL_PATH.read_text(encoding="utf-8"))


def _metadata(correlation_id: str, product: dict[str, Any]) -> dict[str, Any]:
    standards_reference = copy.deepcopy(product["standards_reference"])
    return {
        "correlation_id": correlation_id,
        "source_model_path": CATALOG_MODEL_RELATIVE_PATH,
        "evidence_label": standards_reference["evidence_label"],
        "claim_boundary": standards_reference["claim_boundary"],
        "standards_reference": standards_reference,
        "next_validation_step": "Use this product_id in issue #22 order lifecycle tests.",
    }


def lookup_product(product_id: str, *, correlation_id: str) -> dict[str, Any]:
    """Return the basic 5G data product plus downstream correlation metadata."""

    if not correlation_id or not correlation_id.strip():
        raise ValueError("correlation_id is required for catalog lookups")

    product = _load_product_fixture()
    if product_id != product["id"]:
        raise ProductNotFound(product_id)

    product = copy.deepcopy(product)
    return {
        "correlation_id": correlation_id,
        "product_id": product["id"],
        "product": product,
        "catalog_metadata": _metadata(correlation_id, product),
    }


def list_products(*, correlation_id: str) -> dict[str, Any]:
    """Return the MVP catalog product list with the same correlation metadata."""

    product = _load_product_fixture()
    return {
        "correlation_id": correlation_id,
        "products": [product],
        "catalog_metadata": _metadata(correlation_id, product),
    }
