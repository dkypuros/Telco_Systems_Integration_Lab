"""CPU-safe telemetry summarization with optional GPU backend detection."""

from __future__ import annotations

import importlib.util
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from statistics import fmean
from typing import Iterable

from .models import AgentContextPayload, EventType, SummarizationPolicy, TelemetryRecord, WindowSummary

CLAIM_BOUNDARY = (
    "Compact lab perception payload for the Agent Harness; optional cuDF/Morpheus-ready "
    "backend detection only, not NVIDIA or O-RAN conformance evidence."
)


@dataclass(frozen=True)
class DataFrameBackend:
    """Detected dataframe execution option."""

    name: str
    gpu_accelerated: bool
    reason: str


def detect_dataframe_backend() -> DataFrameBackend:
    """Detect optional GPU dataframe support without importing heavy dependencies."""

    if importlib.util.find_spec("cudf") is not None:
        return DataFrameBackend(
            name="cudf",
            gpu_accelerated=True,
            reason="RAPIDS cuDF is import-discoverable; CPU fallback remains available.",
        )
    if importlib.util.find_spec("pandas") is not None:
        return DataFrameBackend(
            name="pandas-compatible-cpu",
            gpu_accelerated=False,
            reason="pandas is import-discoverable; summarizer still uses stdlib-safe CPU code.",
        )
    return DataFrameBackend(
        name="stdlib-cpu",
        gpu_accelerated=False,
        reason="No optional dataframe package detected; using standard-library summarization.",
    )


def summarize_for_agent(
    records: Iterable[TelemetryRecord],
    *,
    policy: SummarizationPolicy | None = None,
    backend: DataFrameBackend | None = None,
) -> AgentContextPayload:
    """Summarize telemetry into bounded tumbling windows.

    Backpressure is explicit: when a window contains more events than
    ``max_events_per_window``, the summarizer keeps the newest events and records
    how many older events were dropped from LLM context.
    """

    policy = policy or SummarizationPolicy()
    backend = backend or detect_dataframe_backend()
    ordered = sorted(records, key=lambda record: (record.observed_at, record.event_id))
    windows = _group_tumbling_windows(ordered, policy.tumbling_window_seconds)
    summaries: list[WindowSummary] = []
    moving_latency_means: list[float] = []
    total_retained = 0
    total_dropped = 0

    for window_start in sorted(windows):
        events = windows[window_start]
        retained = _apply_backpressure(events, policy)
        dropped = len(events) - len(retained)
        total_retained += len(retained)
        total_dropped += dropped
        latencies = _kpi_values(retained, "cell_latency_ms")
        throughputs = _kpi_values(retained, "downlink_throughput_mbps")
        alarm_counts = Counter(
            record.severity.value for record in retained if record.event_type is EventType.FAULT and record.severity
        )
        latency_mean = _mean_or_none(latencies)
        if latency_mean is not None:
            moving_latency_means.append(latency_mean)
        moving_average = _mean_or_none(moving_latency_means[-3:])
        success_rate = _sgnb_success_rate(retained)
        flags = _anomaly_flags(latency_mean, success_rate, alarm_counts, dropped, policy)
        summaries.append(
            WindowSummary(
                window_start=window_start,
                window_end=window_start + timedelta(seconds=policy.tumbling_window_seconds),
                event_count=len(events),
                retained_event_count=len(retained),
                dropped_event_count=dropped,
                latency_mean_ms=latency_mean,
                latency_moving_average_ms=moving_average,
                throughput_mean_mbps=_mean_or_none(throughputs),
                sgnb_addition_success_rate=success_rate,
                alarm_counts=dict(sorted(alarm_counts.items())),
                anomaly_flags=flags,
            )
        )

    return AgentContextPayload(
        payload_type="agent.telemetry-context.v1",
        backend=backend.name,
        claim_boundary=CLAIM_BOUNDARY,
        policy=policy,
        windows=tuple(summaries),
        total_events_seen=len(ordered),
        total_events_retained=total_retained,
        total_events_dropped=total_dropped,
    )


def _group_tumbling_windows(
    records: list[TelemetryRecord], window_seconds: int
) -> dict[datetime, list[TelemetryRecord]]:
    if window_seconds <= 0:
        raise ValueError("tumbling_window_seconds must be positive")
    grouped: dict[datetime, list[TelemetryRecord]] = defaultdict(list)
    for record in records:
        observed = record.observed_at.astimezone(UTC)
        epoch = int(observed.timestamp())
        window_start_epoch = epoch - (epoch % window_seconds)
        grouped[datetime.fromtimestamp(window_start_epoch, tz=UTC)].append(record)
    return grouped


def _apply_backpressure(
    records: list[TelemetryRecord], policy: SummarizationPolicy
) -> tuple[TelemetryRecord, ...]:
    if policy.max_events_per_window <= 0:
        raise ValueError("max_events_per_window must be positive")
    if len(records) <= policy.max_events_per_window:
        return tuple(records)
    if policy.overflow_strategy != "keep_latest":
        raise ValueError("only keep_latest overflow_strategy is supported")
    return tuple(records[-policy.max_events_per_window :])


def _kpi_values(records: Iterable[TelemetryRecord], key: str) -> list[float]:
    return [float(record.kpis[key]) for record in records if key in record.kpis]


def _mean_or_none(values: Iterable[float]) -> float | None:
    values = list(values)
    if not values:
        return None
    return round(float(fmean(values)), 4)


def _sgnb_success_rate(records: Iterable[TelemetryRecord]) -> float | None:
    attempts = sum(record.kpis.get("sgnb_addition_attempts", 0.0) for record in records)
    successes = sum(record.kpis.get("sgnb_addition_successes", 0.0) for record in records)
    if attempts <= 0:
        return None
    return round(float(successes / attempts), 4)


def _anomaly_flags(
    latency_mean: float | None,
    success_rate: float | None,
    alarm_counts: Counter[str],
    dropped: int,
    policy: SummarizationPolicy,
) -> tuple[str, ...]:
    flags: list[str] = []
    if latency_mean is not None and latency_mean > policy.latency_threshold_ms:
        flags.append("latency_threshold_exceeded")
    if success_rate is not None and success_rate < policy.sgnb_success_rate_floor:
        flags.append("sgnb_success_rate_below_floor")
    if alarm_counts.get("CRITICAL", 0) or alarm_counts.get("MAJOR", 0):
        flags.append("high_severity_alarm_present")
    if dropped:
        flags.append("backpressure_applied")
    return tuple(flags)
