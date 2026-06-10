"""Typed models for the repo-local O-RAN Agent Harness boundary.

These models intentionally use only the Python standard library.  They describe
safe harness payloads and policy decisions; they are not formal O-RAN, TM Forum,
or MCP conformance models.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any, Mapping


class BoundaryStatus(str, Enum):
    """Boundary policy outcome."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    INVALID = "INVALID"


class HarnessTool(str, Enum):
    """Local MCP-compatible tool names exposed by the harness."""

    GET_CELL_TELEMETRY = "get_cell_telemetry"
    CORRELATE_CELL_ALARM = "correlate_cell_alarm"
    MITIGATE_CELL_INTERFERENCE = "mitigate_cell_interference"


class InterfaceTarget(str, Enum):
    """Allowed abstract interfaces for agent-facing payloads."""

    R1_DME = "R1_DME"
    R1_SME = "R1_SME"
    TMF628_QUERY_MODEL = "TMF628_QUERY_MODEL"
    TMF642_QUERY_MODEL = "TMF642_QUERY_MODEL"
    HARNESS_PREFLIGHT = "HARNESS_PREFLIGHT"


class ExecutionOwner(str, Enum):
    """Execution jurisdiction for a returned payload."""

    HARNESS = "HARNESS"
    SMO = "SMO"
    NONE = "NONE"


FORBIDDEN_DIRECT_WIRE_PROTOCOLS: tuple[str, ...] = (
    "ssh",
    "netconf",
    "gnmi",
    "restconf",
    "snmp",
)


@dataclass(frozen=True)
class ToolCall:
    """A local tool invocation crossing the agent/harness boundary."""

    name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SkillSpec:
    """A proposed agent skill declaration checked before exposure."""

    name: str
    tool_name: str | None = None
    egress_protocols: tuple[str, ...] = ()
    target_interfaces: tuple[str, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class BoundaryDecision:
    """Decision returned by the boundary policy."""

    status: BoundaryStatus
    reasons: tuple[str, ...] = ()
    tool_name: str | None = None

    @property
    def allowed(self) -> bool:
        return self.status is BoundaryStatus.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class HarnessPayload:
    """Safe typed payload returned to an AI tool caller."""

    payload_type: str
    target_interface: InterfaceTarget
    model_label: str
    claim_boundary: str
    execution_owner: ExecutionOwner
    body: Mapping[str, Any]
    contains_executable_wire_command: bool = False

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class HarnessResult:
    """Full result for a local tool call."""

    decision: BoundaryDecision
    payloads: tuple[HarnessPayload, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


def _to_plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {item.name: _to_plain(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _to_plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_plain(item) for item in value]
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    return value
