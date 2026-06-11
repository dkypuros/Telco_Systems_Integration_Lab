"""Repo-local telemetry perception pipeline for the Agent Harness."""

from .generator import (
    create_fault_event,
    nrm_topology_for_cell,
    create_performance_event,
    generate_sample_events,
    normalize_events,
    ves_event_to_record,
)
from .models import (
    AgentContextPayload,
    AlarmSeverity,
    DmeDataJob,
    DmeDataRequest,
    DmeDataType,
    DmeQueryResult,
    EventType,
    SummarizationPolicy,
    TelemetryQuery,
    TelemetryRecord,
    WindowSummary,
)
from .r1_dme import R1DmeFacade
from .store import InMemoryTelemetryStore
from .summarizer import DataFrameBackend, detect_dataframe_backend, summarize_for_agent

__all__ = [
    "AgentContextPayload",
    "AlarmSeverity",
    "DataFrameBackend",
    "DmeDataJob",
    "DmeDataRequest",
    "DmeDataType",
    "DmeQueryResult",
    "EventType",
    "InMemoryTelemetryStore",
    "R1DmeFacade",
    "SummarizationPolicy",
    "TelemetryQuery",
    "TelemetryRecord",
    "WindowSummary",
    "create_fault_event",
    "nrm_topology_for_cell",
    "create_performance_event",
    "detect_dataframe_backend",
    "generate_sample_events",
    "normalize_events",
    "summarize_for_agent",
    "ves_event_to_record",
]
