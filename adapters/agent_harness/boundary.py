"""Zero-trust boundary checks for the repo-local Agent Harness."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .models import (
    BoundaryDecision,
    BoundaryStatus,
    FORBIDDEN_DIRECT_WIRE_PROTOCOLS,
    HarnessTool,
    InterfaceTarget,
    SkillSpec,
    ToolCall,
)


_REQUIRED_ARGUMENTS: dict[HarnessTool, tuple[str, ...]] = {
    HarnessTool.GET_CELL_TELEMETRY: ("cell_id", "kpis"),
    HarnessTool.CORRELATE_CELL_ALARM: ("cell_id", "service_id"),
    HarnessTool.MITIGATE_CELL_INTERFERENCE: ("cell_id", "adjustment"),
}


class AgentHarnessBoundary:
    """Policy gate for MCP-compatible local tool exposure.

    The gate allows only typed R1/TMF-style model payloads and rejects direct
    raw egress protocols such as SSH, NETCONF, gNMI, RESTCONF, and SNMP.
    """

    forbidden_direct_wire_protocols = FORBIDDEN_DIRECT_WIRE_PROTOCOLS
    allowed_tools = frozenset(tool.value for tool in HarnessTool)

    def evaluate_skill_spec(self, spec: SkillSpec | Mapping[str, Any]) -> BoundaryDecision:
        skill = self._coerce_skill_spec(spec)
        protocols = tuple(protocol.lower() for protocol in skill.egress_protocols)
        denied = [protocol for protocol in protocols if protocol in self.forbidden_direct_wire_protocols]
        if denied:
            return BoundaryDecision(
                BoundaryStatus.DENY,
                tuple(f"direct_wire_protocol_denied:{protocol}" for protocol in denied),
                skill.tool_name,
            )
        if skill.tool_name and skill.tool_name not in self.allowed_tools:
            return BoundaryDecision(
                BoundaryStatus.DENY,
                (f"unknown_tool:{skill.tool_name}",),
                skill.tool_name,
            )

        unsupported_targets = self._unsupported_target_interfaces(skill.target_interfaces)
        if unsupported_targets:
            return BoundaryDecision(
                BoundaryStatus.DENY,
                tuple(f"unsupported_target_interface:{target}" for target in unsupported_targets),
                skill.tool_name,
            )

        return BoundaryDecision(BoundaryStatus.ALLOW, ("r1_tmf_model_boundary_only",), skill.tool_name)

    def evaluate_tool_call(self, call: ToolCall | Mapping[str, Any]) -> BoundaryDecision:
        tool_call = self._coerce_tool_call(call)
        if tool_call.name not in self.allowed_tools:
            return BoundaryDecision(BoundaryStatus.DENY, (f"unknown_tool:{tool_call.name}",), tool_call.name)

        try:
            tool = HarnessTool(tool_call.name)
        except ValueError:
            return BoundaryDecision(BoundaryStatus.DENY, (f"unknown_tool:{tool_call.name}",), tool_call.name)

        missing = [name for name in _REQUIRED_ARGUMENTS[tool] if not self._has_argument(tool_call.arguments, name)]
        if missing:
            return BoundaryDecision(
                BoundaryStatus.INVALID,
                tuple(f"missing_required_argument:{name}" for name in missing),
                tool_call.name,
            )

        direct_protocols = self._find_direct_wire_protocols(tool_call.arguments)
        if direct_protocols:
            return BoundaryDecision(
                BoundaryStatus.DENY,
                tuple(f"direct_wire_protocol_denied:{protocol}" for protocol in direct_protocols),
                tool_call.name,
            )

        return BoundaryDecision(BoundaryStatus.ALLOW, ("allowed_r1_tmf_model_payload",), tool_call.name)

    @staticmethod
    def _coerce_tool_call(call: ToolCall | Mapping[str, Any]) -> ToolCall:
        if isinstance(call, ToolCall):
            return call
        return ToolCall(name=str(call.get("name", "")), arguments=call.get("arguments", {}) or {})

    @staticmethod
    def _coerce_skill_spec(spec: SkillSpec | Mapping[str, Any]) -> SkillSpec:
        if isinstance(spec, SkillSpec):
            return spec
        protocols = spec.get("egress_protocols", ()) or spec.get("protocols", ()) or ()
        interfaces = spec.get("target_interfaces", ()) or ()
        return SkillSpec(
            name=str(spec.get("name", "")),
            tool_name=spec.get("tool_name"),
            egress_protocols=tuple(str(protocol) for protocol in protocols),
            target_interfaces=tuple(str(interface) for interface in interfaces),
            description=str(spec.get("description", "")),
        )

    def _unsupported_target_interfaces(self, targets: Sequence[str]) -> tuple[str, ...]:
        allowed = {target.value.lower() for target in InterfaceTarget}
        unsupported: list[str] = []
        for target in targets:
            normalized = str(target).strip().lower()
            if not normalized:
                continue
            if normalized in self.forbidden_direct_wire_protocols:
                unsupported.append(normalized)
            elif normalized not in allowed:
                unsupported.append(normalized)
        return tuple(unsupported)

    @staticmethod
    def _has_argument(arguments: Mapping[str, Any], name: str) -> bool:
        value = arguments.get(name)
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
            return False
        return True

    def _find_direct_wire_protocols(self, value: Any) -> tuple[str, ...]:
        found: set[str] = set()

        def visit(item: Any) -> None:
            if isinstance(item, Mapping):
                for key, nested in item.items():
                    key_text = str(key).lower()
                    if key_text in {"protocol", "egress_protocol", "egress_protocols", "wire_protocol"}:
                        visit(nested)
                    elif key_text in self.forbidden_direct_wire_protocols:
                        found.add(key_text)
                    else:
                        visit(nested)
            elif isinstance(item, str):
                text = item.lower()
                if text in self.forbidden_direct_wire_protocols:
                    found.add(text)
            elif isinstance(item, Sequence) and not isinstance(item, (bytes, bytearray)):
                for nested in item:
                    visit(nested)

        visit(value)
        return tuple(sorted(found))
