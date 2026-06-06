"""Minimal product order lifecycle for the MVP service-order-to-activation slice.

The output is TMF622/TMF641-referenced functional-smoke evidence only. It creates
an activation plan for downstream orchestration without claiming formal TM Forum
conformance.
"""

from __future__ import annotations

import hashlib
from typing import Any

from services.catalog_api import ProductNotFound, lookup_product

ORDER_EVIDENCE_LABEL = "functional_smoke"
CLAIM_BOUNDARY = "Functional smoke order lifecycle only; not formal TM Forum conformance."


class InvalidProductOrder(ValueError):
    """Raised when the MVP order request cannot be accepted."""


def _stable_suffix(*values: str, length: int = 12) -> str:
    digest = hashlib.sha256("|".join(values).encode("utf-8")).hexdigest()
    return digest[:length]


def _require_non_empty(name: str, value: str) -> str:
    if not value or not value.strip():
        raise InvalidProductOrder(f"{name} is required")
    return value.strip()


def _state_history(correlation_id: str, order_id: str) -> list[dict[str, str]]:
    return [
        {
            "state": "acknowledged",
            "reason": "Catalog product accepted for MVP order processing.",
            "correlation_id": correlation_id,
            "order_id": order_id,
        },
        {
            "state": "activation_requested",
            "reason": "Activation plan derived for downstream orchestration.",
            "correlation_id": correlation_id,
            "order_id": order_id,
        },
    ]


def _standards_reference() -> dict[str, str]:
    return {
        "standards_body": "TM Forum",
        "spec_id": "TMF622",
        "service_order_spec_id": "TMF641",
        "release_register_path": "traceability/standards_release_register.yaml",
        "evidence_label": ORDER_EVIDENCE_LABEL,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def create_product_order(*, product_id: str, correlation_id: str, customer_id: str) -> dict[str, Any]:
    """Accept a basic product order and return lifecycle plus activation plan."""

    product_id = _require_non_empty("product_id", product_id)
    correlation_id = _require_non_empty("correlation_id", correlation_id)
    customer_id = _require_non_empty("customer_id", customer_id)

    try:
        catalog_response = lookup_product(product_id, correlation_id=correlation_id)
    except ProductNotFound as exc:
        raise InvalidProductOrder(f"unknown product_id: {product_id}") from exc

    product = catalog_response["product"]
    suffix = _stable_suffix(correlation_id, customer_id, product_id)
    order_id = f"order-{suffix}"
    service_id = f"svc-{suffix}"
    standards_reference = _standards_reference()
    activation_defaults = product["mvp_activation_defaults"]

    order = {
        "id": order_id,
        "href": f"/tmf-api/productOrderingManagement/v5/productOrder/{order_id}",
        "state": "activation_requested",
        "product_id": product_id,
        "customer_id": customer_id,
        "correlation_id": correlation_id,
        "requested_action": "add",
        "state_history": _state_history(correlation_id, order_id),
        "@type": "ProductOrder",
    }

    activation_plan = {
        "id": f"activation-plan-{suffix}",
        "correlation_id": correlation_id,
        "order_id": order_id,
        "service_id": service_id,
        "product_id": product_id,
        "customer_id": customer_id,
        "network_action": "activate_mock_5g_data_service",
        "subscriber_intent": activation_defaults["subscriber_intent"],
        "session_intent": activation_defaults["session_intent"],
        "handoff": {
            "service_order_mapping": "services/orchestration/ issue #23",
            "service_inventory_mapping": "future services/service_inventory/ or TMF640 facade",
            "mock_core_adapter": "adapters/3gpp/ issue #24",
        },
        "standards_reference": {
            "standards_body": "TM Forum",
            "product_order_spec_id": "TMF622",
            "service_order_spec_id": "TMF641",
            "release_register_path": "traceability/standards_release_register.yaml",
            "evidence_label": ORDER_EVIDENCE_LABEL,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }

    return {
        "correlation_id": correlation_id,
        "order": order,
        "activation_plan": activation_plan,
        "order_metadata": {
            "evidence_label": ORDER_EVIDENCE_LABEL,
            "claim_boundary": CLAIM_BOUNDARY,
            "standards_reference": standards_reference,
            "source_catalog_product_id": product_id,
            "next_validation_step": "Issue #23 maps activation_plan into orchestration intent.",
        },
    }
