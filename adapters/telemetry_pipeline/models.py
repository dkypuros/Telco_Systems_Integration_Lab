"""Typed models for the lab telemetry perception pipeline.

The models are intentionally small, deterministic, and standard-library only.
They describe a public-safe O1/VES-inspired lab shape plus an R1 DME-style
query boundary; they are not formal O-RAN, Ericsson EIAP, NVIDIA, or TM Forum
conformance models.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Mapping


class EventType(str, Enum):
    """Telemetry event families used by the lab pipeline."""

    FAULT = "fault"
    PERFORMANCE = "performance"


class AlarmSeverity(str, Enum):
    """Small severity vocabulary for public-safe sample alarms."""

    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    WARNING = "WARNING"
    NORMAL = "NORMAL"


@dataclass(frozen=True)
class TelemetryRecord:
    """Normalized telemetry record persisted by the local data-layer mock."""

    event_id: str
    cell_id: str
    event_type: EventType
    observed_at: datetime
    kpis: Mapping[str, float] = field(default_factory=dict)
    severity: AlarmSeverity | None = None
    alarm_condition: str | None = None
    source_interface: str = "O1/VES-inspired"
    source_event: Mapping[str, Any] = field(default_factory=dict)
    topology: Mapping[str, str] = field(default_factory=dict)

    @property
    def index_name(self) -> str:
        """Deterministic index name mirroring a telemetry search-store partition."""

        return f"telemetry-{self.observed_at.astimezone(UTC):%Y%m%d}"

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class TelemetryQuery:
    """R1 DME-style query constraints over normalized telemetry."""

    cell_id: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    event_type: EventType | None = None
    severity: AlarmSeverity | None = None
    kpi_names: tuple[str, ...] = ()
    limit: int = 500


@dataclass(frozen=True)
class DmeDataType:
    """Registered data type exposed by the mock R1 DME facade."""

    data_type_id: str
    description: str
    source_interface: str
    claim_boundary: str


@dataclass(frozen=True)
class DmeDataRequest:
    """One-time data request created through the mock R1 DME facade."""

    request_id: str
    data_type_id: str
    query: TelemetryQuery
    created_at: datetime

    @property
    def job_id(self) -> str:
        """Compatibility alias for older lab code; prefer request_id."""

        return self.request_id


# R1AP includes data-job information in registration/subscription contexts.
# Keep the older lab name as a compatibility alias while documentation leads
# with data request/subscription terminology.
DmeDataJob = DmeDataRequest


@dataclass(frozen=True)
class DmeQueryResult:
    """Query result returned by the R1 DME-style facade."""

    request: DmeDataRequest
    records: tuple[TelemetryRecord, ...]
    compact: bool = True

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class SummarizationPolicy:
    """Bounded windowing/backpressure policy for firehose-shaped telemetry."""

    tumbling_window_seconds: int = 60
    max_events_per_window: int = 1_000
    overflow_strategy: str = "keep_latest"
    latency_threshold_ms: float = 50.0
    sgnb_success_rate_floor: float = 0.95
    moving_average_windows: int = 3


@dataclass(frozen=True)
class WindowSummary:
    """A compact per-window telemetry summary suitable for LLM context."""

    window_start: datetime
    window_end: datetime
    event_count: int
    retained_event_count: int
    dropped_event_count: int
    latency_mean_ms: float | None = None
    latency_moving_average_ms: float | None = None
    throughput_mean_mbps: float | None = None
    sgnb_addition_success_rate: float | None = None
    alarm_counts: Mapping[str, int] = field(default_factory=dict)
    anomaly_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentContextPayload:
    """Perception payload handed to the agent harness, not raw store access."""

    payload_type: str
    backend: str
    claim_boundary: str
    policy: SummarizationPolicy
    windows: tuple[WindowSummary, ...]
    total_events_seen: int
    total_events_retained: int
    total_events_dropped: int
    topology_context: Mapping[str, Mapping[str, str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


def _to_plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if is_dataclass(value):
        return {item.name: _to_plain(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _to_plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_plain(item) for item in value]
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    return value
