"""Dependency-free MCP-compatible local Agent Harness registry.

The class in this module intentionally does not claim MCP SDK conformance.  It
provides a small local ``call_tool`` surface that mirrors the shape an MCP tool
adapter would need while preserving the repo-local policy boundary.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .boundary import AgentHarnessBoundary
from .intent_translator import IntentTranslator
from .models import BoundaryDecision, HarnessResult, HarnessTool, ToolCall


class AgentHarnessServer:
    """Local tool registry for safe agent/harness calls."""

    def __init__(self, boundary: AgentHarnessBoundary | None = None, translator: IntentTranslator | None = None) -> None:
        self.boundary = boundary or AgentHarnessBoundary()
        self.translator = translator or IntentTranslator()
        self._builders: dict[str, Callable[[Mapping[str, Any]], tuple[Any, ...]]] = {
            HarnessTool.GET_CELL_TELEMETRY.value: self.translator.build_cell_telemetry,
            HarnessTool.CORRELATE_CELL_ALARM.value: self.translator.build_alarm_correlation,
            HarnessTool.MITIGATE_CELL_INTERFERENCE.value: self.translator.build_interference_mitigation,
        }

    def list_tools(self) -> list[dict[str, Any]]:
        """Return the local registry metadata exposed to callers."""
        return [
            {
                "name": HarnessTool.GET_CELL_TELEMETRY.value,
                "required_arguments": ["cell_id", "kpis"],
                "boundary": "R1 DME + TMF628-style query model only",
            },
            {
                "name": HarnessTool.CORRELATE_CELL_ALARM.value,
                "required_arguments": ["cell_id", "service_id"],
                "boundary": "TMF642-style alarm query model only",
            },
            {
                "name": HarnessTool.MITIGATE_CELL_INTERFERENCE.value,
                "required_arguments": ["cell_id", "adjustment"],
                "boundary": "R1 SME intent; SMO-owned downstream execution",
            },
        ]

    def call_tool(self, name: str, arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Evaluate policy and return deterministic safe payloads for a tool."""
        tool_call = ToolCall(name=name, arguments=arguments or {})
        decision = self.boundary.evaluate_tool_call(tool_call)
        if not decision.allowed:
            return HarnessResult(decision=decision).to_dict()

        builder = self._builders.get(name)
        if builder is None:
            return HarnessResult(decision=BoundaryDecision(decision.status, (f"unknown_tool:{name}",), name)).to_dict()
        return HarnessResult(decision=decision, payloads=builder(tool_call.arguments)).to_dict()


def create_default_server() -> AgentHarnessServer:
    """Create the default repo-local Agent Harness server."""
    return AgentHarnessServer()
