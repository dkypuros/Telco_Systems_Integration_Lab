"""Telemetry summarization with a real cuDF -> pandas -> stdlib backend ladder.

The detected dataframe backend is not cosmetic: window aggregates are computed on
whichever backend ``detect_dataframe_backend()`` selects. When ``cudf`` is present the
groupby/reduction runs on the GPU; otherwise pandas does the same vectorized work on
CPU; if neither is importable a standard-library path produces identical numbers. Any
runtime error in the dataframe path falls back to stdlib so the public lab never breaks
on a laptop or in CI.
"""

from __future__ import annotations

import importlib
import importlib.util
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from statistics import fmean
from typing import Iterable

from .models import AgentContextPayload, EventType, SummarizationPolicy, TelemetryRecord, WindowSummary

CLAIM_BOUNDARY = (
    "Compact lab perception payload for the Agent Harness; aggregation runs on the "
    "detected cuDF/pandas/stdlib backend, not NVIDIA or O-RAN conformance evidence."
)

_LATENCY_KPI = "cell_latency_ms"
_THROUGHPUT_KPI = "downlink_throughput_mbps"
_SGNB_ATTEMPTS_KPI = "sgnb_addition_attempts"
_SGNB_SUCCESSES_KPI = "sgnb_addition_successes"


@dataclass(frozen=True)
class DataFrameBackend:
    """Detected dataframe execution option."""

    name: str
    gpu_accelerated: bool
    reason: str


@dataclass(frozen=True)
class _WindowStats:
    """Numeric aggregates for one window, produced by the active backend."""

    latency_mean_ms: float | None
    throughput_mean_mbps: float | None
    sgnb_attempts: float
    sgnb_successes: float

    @property
    def sgnb_success_rate(self) -> float | None:
        if self.sgnb_attempts <= 0:
            return None
        return round(self.sgnb_successes / self.sgnb_attempts, 4)


def detect_dataframe_backend() -> DataFrameBackend:
    """Detect the best available dataframe backend without importing heavy deps."""

    if importlib.util.find_spec("cudf") is not None:
        return DataFrameBackend(
            name="cudf",
            gpu_accelerated=True,
            reason="RAPIDS cuDF is import-discoverable; GPU aggregation with CPU fallback.",
        )
    if importlib.util.find_spec("pandas") is not None:
        return DataFrameBackend(
            name="pandas-compatible-cpu",
            gpu_accelerated=False,
            reason="pandas is import-discoverable; vectorized CPU aggregation with stdlib fallback.",
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
    how many older events were dropped from LLM context. The per-window numeric
    aggregates are computed on ``backend`` (GPU cuDF, CPU pandas, or stdlib).

    Note: latency/throughput/SgNB aggregates are computed over *retained* events
    only, so a dropped burst can bias them; the ``backpressure_applied`` flag and
    the dropped-event counts make that loss explicit to the agent.
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

        stats = _window_stats(retained, backend)
        alarm_counts = Counter(
            record.severity.value for record in retained if record.event_type is EventType.FAULT and record.severity
        )
        if stats.latency_mean_ms is not None:
            moving_latency_means.append(stats.latency_mean_ms)
        moving_average = _mean_or_none(moving_latency_means[-policy.moving_average_windows :])
        success_rate = stats.sgnb_success_rate
        flags = _anomaly_flags(stats.latency_mean_ms, success_rate, alarm_counts, dropped, policy)
        summaries.append(
            WindowSummary(
                window_start=window_start,
                window_end=window_start + timedelta(seconds=policy.tumbling_window_seconds),
                event_count=len(events),
                retained_event_count=len(retained),
                dropped_event_count=dropped,
                latency_mean_ms=stats.latency_mean_ms,
                latency_moving_average_ms=moving_average,
                throughput_mean_mbps=stats.throughput_mean_mbps,
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
        topology_context=_topology_context(ordered),
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


def _window_stats(records: Iterable[TelemetryRecord], backend: DataFrameBackend) -> _WindowStats:
    """Compute window aggregates on the active backend, falling back to stdlib."""

    rows = [dict(record.kpis) for record in records if record.kpis]
    if backend.name in {"cudf", "pandas-compatible-cpu"}:
        accelerated = _dataframe_window_stats(rows, backend.name)
        if accelerated is not None:
            return accelerated
    return _stdlib_window_stats(rows)


def _dataframe_window_stats(rows: list[dict[str, float]], backend_name: str) -> _WindowStats | None:
    """Vectorized aggregation on cuDF (GPU) or pandas (CPU).

    Returns ``None`` to signal a safe stdlib fallback if the library is missing or
    raises. NaN handling matches the stdlib path: ``mean`` skips missing values and
    ``sum`` treats missing as zero, so results are backend-independent.
    """

    module_name = "cudf" if backend_name == "cudf" else "pandas"
    try:
        frame_lib = importlib.import_module(module_name)
    except Exception:
        return None
    try:
        if not rows:
            return _WindowStats(None, None, 0.0, 0.0)
        frame = frame_lib.DataFrame(rows)

        def mean(column: str) -> float | None:
            if column not in frame.columns:
                return None
            value = frame[column].mean()
            if value is None or value != value:  # NaN guard
                return None
            return round(float(value), 4)

        def total(column: str) -> float:
            if column not in frame.columns:
                return 0.0
            value = frame[column].sum()
            if value is None or value != value:
                return 0.0
            return float(value)

        return _WindowStats(
            latency_mean_ms=mean(_LATENCY_KPI),
            throughput_mean_mbps=mean(_THROUGHPUT_KPI),
            sgnb_attempts=total(_SGNB_ATTEMPTS_KPI),
            sgnb_successes=total(_SGNB_SUCCESSES_KPI),
        )
    except Exception:
        return None


def _stdlib_window_stats(rows: list[dict[str, float]]) -> _WindowStats:
    return _WindowStats(
        latency_mean_ms=_mean_or_none(_column_values(rows, _LATENCY_KPI)),
        throughput_mean_mbps=_mean_or_none(_column_values(rows, _THROUGHPUT_KPI)),
        sgnb_attempts=_column_sum(rows, _SGNB_ATTEMPTS_KPI),
        sgnb_successes=_column_sum(rows, _SGNB_SUCCESSES_KPI),
    )


def _column_values(rows: Iterable[dict[str, float]], key: str) -> list[float]:
    return [float(row[key]) for row in rows if key in row and row[key] is not None]


def _column_sum(rows: Iterable[dict[str, float]], key: str) -> float:
    return float(sum(float(row.get(key, 0.0) or 0.0) for row in rows))


def _mean_or_none(values: Iterable[float]) -> float | None:
    values = list(values)
    if not values:
        return None
    return round(float(fmean(values)), 4)


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


def _topology_context(records: Iterable[TelemetryRecord]) -> dict[str, dict[str, str]]:
    context: dict[str, dict[str, str]] = {}
    for record in records:
        if record.topology:
            context.setdefault(record.cell_id, dict(record.topology))
    return context
