"""3GPP-referenced mock-core activation adapter for the MVP slice.

The adapter translates orchestration intent into a narrow mock subscriber/session
activation record. It is functional-smoke evidence only; it does not claim formal
3GPP protocol conformance.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ADAPTER_CONTRACT_VERSION = "mvp-0.1"
ADAPTER_EVIDENCE_LABEL = "functional_smoke"
CLAIM_BOUNDARY = "Functional smoke 3GPP mock-core adapter only; not formal 3GPP conformance."

REQUIRED_REQUEST_FIELDS = [
    "correlation_id",
    "order_id",
    "service_id",
    "product_id",
    "network_action",
    "subscriber_intent",
    "session_intent",
]


class InvalidMockCoreActivationRequest(ValueError):
    """Raised when the adapter request cannot be translated."""


MockCoreSurface = Callable[[dict[str, Any]], dict[str, Any]]


def _require_request(request: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_REQUEST_FIELDS if not request.get(field)]
    if missing:
        raise InvalidMockCoreActivationRequest(f"adapter request missing required field(s): {', '.join(missing)}")
    if request["network_action"] != "activate_mock_5g_data_service":
        raise InvalidMockCoreActivationRequest(f"unsupported network_action: {request['network_action']}")


def _parse_intent(intent: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for part in intent.split(";"):
        if not part.strip():
            continue
        if "=" not in part:
            raise InvalidMockCoreActivationRequest(f"intent segment is not key=value: {part.strip()}")
        key, value = part.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def build_mock_core_payload(request: dict[str, Any]) -> dict[str, Any]:
    """Translate orchestration request fields into a mock core activation payload."""

    _require_request(request)
    subscriber_profile = _parse_intent(request["subscriber_intent"])
    session_profile = _parse_intent(request["session_intent"])

    for required in ["subscriber", "access"]:
        if required not in subscriber_profile:
            raise InvalidMockCoreActivationRequest(f"subscriber_intent missing {required}")
    for required in ["dnn", "slice", "qos"]:
        if required not in session_profile:
            raise InvalidMockCoreActivationRequest(f"session_intent missing {required}")

    return {
        "correlation_id": request["correlation_id"],
        "order_id": request["order_id"],
        "service_id": request["service_id"],
        "product_id": request["product_id"],
        "network_action": request["network_action"],
        "subscriber_profile": subscriber_profile,
        "session_profile": session_profile,
        "target_mock_functions": ["UDR", "UDM", "AMF", "SMF", "UPF"],
        "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
    }


def controlled_local_mock_core_surface(payload: dict[str, Any]) -> dict[str, Any]:
    """Controlled local substitute for unavailable runtime mock-core dependencies."""

    return {
        "surface": "controlled_local_stub",
        "status": "accepted",
        "nf_sequence": payload["target_mock_functions"],
        "recorded_service_id": payload["service_id"],
        "recorded_subscriber": payload["subscriber_profile"]["subscriber"],
        "recorded_dnn": payload["session_profile"]["dnn"],
    }


def activate_subscriber_session(
    request: dict[str, Any],
    *,
    mock_core_surface: MockCoreSurface = controlled_local_mock_core_surface,
) -> dict[str, Any]:
    """Activate the MVP subscriber/session intent through a mock-core surface."""

    payload = build_mock_core_payload(request)
    mock_core_response = mock_core_surface(payload)
    surface = mock_core_response.get("surface", "injected_mock_core_surface")
    status = mock_core_response.get("status", "accepted")
    activation_result = "activated" if status == "accepted" else "rejected"

    return {
        "correlation_id": payload["correlation_id"],
        "order_id": payload["order_id"],
        "service_id": payload["service_id"],
        "product_id": payload["product_id"],
        "adapter_contract_version": ADAPTER_CONTRACT_VERSION,
        "mock_activation_result": activation_result,
        "activation_state": "session_activation_recorded" if activation_result == "activated" else "session_activation_rejected",
        "mock_core_surface": surface,
        "subscriber_profile": payload["subscriber_profile"],
        "session_profile": payload["session_profile"],
        "mock_core_response": mock_core_response,
        "evidence_metadata": {
            "evidence_label": ADAPTER_EVIDENCE_LABEL,
            "claim_boundary": CLAIM_BOUNDARY,
            "standards_reference": {
                "standards_body": "3GPP",
                "spec_id": "3GPP release-baseline",
                "release_register_path": "traceability/standards_release_register.yaml",
                "conformance_level": "functional_smoke",
                "known_gap_to_latest": "formal protocol conformance evidence missing",
            },
            "adapter_path": "adapters/3gpp/mock_core_activation_adapter.py",
            "next_validation_step": "Issue #25 records this adapter result in the end-to-end evidence bundle.",
        },
    }
