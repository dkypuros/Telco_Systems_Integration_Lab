"""Deterministic intent translation for safe Agent Harness payloads."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from .models import ExecutionOwner, HarnessPayload, InterfaceTarget

_CLAIM_BOUNDARY = "deterministic harness/query model; not formal O-RAN, TM Forum, or MCP conformance"


class IntentTranslator:
    """Build safe R1/TMF model payloads without direct wire commands."""

    def build_cell_telemetry(self, arguments: Mapping[str, Any]) -> tuple[HarnessPayload, ...]:
        cell_id = str(arguments["cell_id"])
        kpis = self._string_list(arguments["kpis"])
        return (
            HarnessPayload(
                payload_type="telemetry_subscription",
                target_interface=InterfaceTarget.R1_DME,
                model_label="R1 DME telemetry subscription request",
                claim_boundary=_CLAIM_BOUNDARY,
                execution_owner=ExecutionOwner.HARNESS,
                body={
                    "cell_id": cell_id,
                    "kpis": kpis,
                    "subscription": {
                        "data_type": "cell_kpi_measurements",
                        "delivery_mode": "harness_model_only",
                    },
                },
            ),
            HarnessPayload(
                payload_type="telemetry_query",
                target_interface=InterfaceTarget.TMF628_QUERY_MODEL,
                model_label="TMF628-style harness/query model",
                claim_boundary=_CLAIM_BOUNDARY,
                execution_owner=ExecutionOwner.NONE,
                body={
                    "query_model": "tmf628_performance_management_query",
                    "resource_filter": {"cell_id": cell_id},
                    "metric_filter": kpis,
                    "execution": "query_payload_only_no_network_egress",
                },
            ),
        )

    def build_alarm_correlation(self, arguments: Mapping[str, Any]) -> tuple[HarnessPayload, ...]:
        cell_id = str(arguments["cell_id"])
        service_id = str(arguments["service_id"])
        severity = arguments.get("severity")
        filters: dict[str, Any] = {"cell_id": cell_id, "service_id": service_id}
        if severity:
            filters["severity"] = str(severity)
        return (
            HarnessPayload(
                payload_type="alarm_correlation_query",
                target_interface=InterfaceTarget.TMF642_QUERY_MODEL,
                model_label="TMF642-style harness/query model",
                claim_boundary=_CLAIM_BOUNDARY,
                execution_owner=ExecutionOwner.NONE,
                body={
                    "query_model": "tmf642_alarm_management_query",
                    "filters": filters,
                    "service_impact_context": {
                        "service_id": service_id,
                        "cell_id": cell_id,
                        "impact_scope": "candidate_service_impact_context",
                    },
                    "execution": "normalization_request_only_no_network_egress",
                },
            ),
        )

    def build_interference_mitigation(self, arguments: Mapping[str, Any]) -> tuple[HarnessPayload, ...]:
        cell_id = str(arguments["cell_id"])
        adjustment = self._plain_mapping(arguments["adjustment"])
        idempotency_key = self._idempotency_key(cell_id, adjustment)
        blast_radius = {
            "target_cell": cell_id,
            "adjacent_cells": self._string_list(arguments.get("adjacent_cells", ())),
            "max_cells_touched": 1 + len(arguments.get("adjacent_cells", ()) or ()),
        }
        return (
            HarnessPayload(
                payload_type="remediation_intent",
                target_interface=InterfaceTarget.R1_SME,
                model_label="R1 SME action intent",
                claim_boundary=_CLAIM_BOUNDARY,
                execution_owner=ExecutionOwner.SMO,
                body={
                    "cell_id": cell_id,
                    "intent": "mitigate_cell_interference",
                    "adjustment": adjustment,
                    "idempotency_key": idempotency_key,
                    "execution_boundary": "harness_stops_at_smo_boundary_smo_owns_o1_a1_execution",
                },
            ),
            HarnessPayload(
                payload_type="preflight_evidence",
                target_interface=InterfaceTarget.HARNESS_PREFLIGHT,
                model_label="deterministic harness preflight evidence",
                claim_boundary=_CLAIM_BOUNDARY,
                execution_owner=ExecutionOwner.HARNESS,
                body={
                    "idempotency_key": idempotency_key,
                    "blast_radius": blast_radius,
                    "policy": {
                        "direct_wire_protocols_denied": ["ssh", "netconf", "gnmi", "restconf", "snmp"],
                        "downstream_execution_owner": "smo",
                    },
                },
            ),
        )

    @staticmethod
    def _string_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, Sequence):
            return [str(item) for item in value]
        return [str(value)]

    @staticmethod
    def _plain_mapping(value: Any) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return {str(key): value[key] for key in sorted(value)}
        return {"value": value}

    @staticmethod
    def _idempotency_key(cell_id: str, adjustment: Mapping[str, Any]) -> str:
        canonical = json.dumps({"cell_id": cell_id, "adjustment": adjustment}, sort_keys=True, separators=(",", ":"))
        return "agent-harness:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
