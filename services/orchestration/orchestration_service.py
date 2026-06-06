"""Lab-owned orchestration graph for the service-order-to-activation MVP.

This module maps an order activation plan into subscriber/session intent and
calls a 3GPP mock-core adapter contract. It intentionally avoids importing mock
network internals; issue #24 owns the concrete adapter implementation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ORCHESTRATION_EVIDENCE_LABEL = "functional_smoke"
CLAIM_BOUNDARY = "Functional smoke orchestration graph only; not formal 3GPP, O-RAN, or TM Forum conformance."
ADAPTER_CONTRACT_PATH = "adapters/3gpp/ issue #24"

REQUIRED_PLAN_FIELDS = [
    "correlation_id",
    "order_id",
    "service_id",
    "product_id",
    "network_action",
    "subscriber_intent",
    "session_intent",
]


class InvalidActivationPlan(ValueError):
    """Raised when the order activation plan cannot be orchestrated."""


MockCoreAdapter = Callable[[dict[str, Any]], dict[str, Any]]


def _require_activation_plan(plan: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_PLAN_FIELDS if not plan.get(field)]
    if missing:
        raise InvalidActivationPlan(f"activation_plan missing required field(s): {', '.join(missing)}")
    if plan["network_action"] != "activate_mock_5g_data_service":
        raise InvalidActivationPlan(f"unsupported network_action: {plan['network_action']}")


def _event(state: str, plan: dict[str, Any], reason: str) -> dict[str, str]:
    return {
        "state": state,
        "reason": reason,
        "correlation_id": plan["correlation_id"],
        "order_id": plan["order_id"],
        "service_id": plan["service_id"],
    }


def build_mock_core_adapter_request(plan: dict[str, Any]) -> dict[str, Any]:
    """Build the adapter-contract payload owned by `adapters/3gpp/` in issue #24."""

    _require_activation_plan(plan)
    return {
        "correlation_id": plan["correlation_id"],
        "order_id": plan["order_id"],
        "service_id": plan["service_id"],
        "product_id": plan["product_id"],
        "network_action": plan["network_action"],
        "subscriber_intent": plan["subscriber_intent"],
        "session_intent": plan["session_intent"],
        "adapter_contract_path": ADAPTER_CONTRACT_PATH,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def default_mock_core_adapter_contract(request: dict[str, Any]) -> dict[str, Any]:
    """Default contract-only adapter response until issue #24 provides execution."""

    return {
        "correlation_id": request["correlation_id"],
        "service_id": request["service_id"],
        "mock_activation_result": "contract_pending",
        "adapter_contract_path": ADAPTER_CONTRACT_PATH,
        "claim_boundary": "Adapter execution is pending issue #24; no network conformance claim.",
    }


def orchestrate_activation(
    activation_plan: dict[str, Any],
    *,
    mock_core_adapter: MockCoreAdapter = default_mock_core_adapter_contract,
) -> dict[str, Any]:
    """Map activation intent, call the adapter contract, and return graph evidence."""

    _require_activation_plan(activation_plan)
    state_history = [
        _event("activation_plan_received", activation_plan, "Order activation plan accepted by orchestration."),
        _event(
            "subscriber_session_intent_mapped",
            activation_plan,
            "Subscriber and session intent mapped for the mock-core adapter contract.",
        ),
    ]

    adapter_request = build_mock_core_adapter_request(activation_plan)
    state_history.append(_event("mock_core_adapter_invoked", activation_plan, "Mock-core adapter contract invoked."))
    adapter_response = mock_core_adapter(adapter_request)
    state_history.append(_event("mock_core_adapter_acknowledged", activation_plan, "Mock-core adapter contract returned a response."))

    return {
        "correlation_id": activation_plan["correlation_id"],
        "order_id": activation_plan["order_id"],
        "service_id": activation_plan["service_id"],
        "product_id": activation_plan["product_id"],
        "subscriber_intent": activation_plan["subscriber_intent"],
        "session_intent": activation_plan["session_intent"],
        "state_history": state_history,
        "adapter_request": adapter_request,
        "adapter_response": adapter_response,
        "orchestration_metadata": {
            "evidence_label": ORCHESTRATION_EVIDENCE_LABEL,
            "claim_boundary": CLAIM_BOUNDARY,
            "standards_reference": {
                "standards_body": "3GPP",
                "spec_id": "release-baseline",
                "release_register_path": "traceability/standards_release_register.yaml",
                "evidence_label": ORCHESTRATION_EVIDENCE_LABEL,
                "known_gap_to_latest": "formal protocol conformance evidence missing",
            },
            "adapter_contract_path": ADAPTER_CONTRACT_PATH,
            "next_validation_step": "Issue #24 implements the adapters/3gpp mock-core activation adapter.",
        },
    }
