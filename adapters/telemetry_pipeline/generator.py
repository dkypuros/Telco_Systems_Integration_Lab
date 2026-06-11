"""Deterministic O1/VES-inspired telemetry fixture generator."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Iterable, Mapping
from uuid import uuid5, NAMESPACE_URL

from .models import AlarmSeverity, EventType, TelemetryRecord


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _event_id(*parts: object) -> str:
    return str(uuid5(NAMESPACE_URL, ":".join(str(part) for part in parts)))


def create_performance_event(
    *,
    cell_id: str,
    observed_at: datetime,
    latency_ms: float,
    throughput_mbps: float,
    sgnb_addition_attempts: int = 0,
    sgnb_addition_successes: int = 0,
) -> dict[str, Any]:
    """Return a compact VES-like PM event for one cell.

    This is VES/O1-inspired test data, not a verbatim standards payload.
    """

    event_time = _utc(observed_at)
    event_id = _event_id("pm", cell_id, event_time.isoformat())
    return {
        "event": {
            "commonEventHeader": {
                "domain": "measurementsForVfScaling",
                "eventId": event_id,
                "eventName": "o1-ves-lab-pm",
                "sourceName": cell_id,
                "lastEpochMicrosec": int(event_time.timestamp() * 1_000_000),
                "startEpochMicrosec": int(event_time.timestamp() * 1_000_000),
            },
            "measurementsForVfScalingFields": {
                "measurementFieldsVersion": "lab-1",
                "additionalMeasurements": {
                    "cell_latency_ms": latency_ms,
                    "downlink_throughput_mbps": throughput_mbps,
                    "sgnb_addition_attempts": float(sgnb_addition_attempts),
                    "sgnb_addition_successes": float(sgnb_addition_successes),
                },
            },
        }
    }


def create_fault_event(
    *,
    cell_id: str,
    observed_at: datetime,
    severity: AlarmSeverity | str,
    alarm_condition: str,
) -> dict[str, Any]:
    """Return a compact VES-like FM event for one cell."""

    event_time = _utc(observed_at)
    severity_value = severity.value if isinstance(severity, AlarmSeverity) else severity
    event_id = _event_id("fm", cell_id, event_time.isoformat(), alarm_condition)
    return {
        "event": {
            "commonEventHeader": {
                "domain": "fault",
                "eventId": event_id,
                "eventName": "o1-ves-lab-fm",
                "sourceName": cell_id,
                "lastEpochMicrosec": int(event_time.timestamp() * 1_000_000),
                "startEpochMicrosec": int(event_time.timestamp() * 1_000_000),
            },
            "faultFields": {
                "faultFieldsVersion": "lab-1",
                "eventSeverity": severity_value,
                "alarmCondition": alarm_condition,
            },
        }
    }


def ves_event_to_record(payload: Mapping[str, Any]) -> TelemetryRecord:
    """Normalize a VES-like payload into a repo-local telemetry record."""

    event = payload["event"]
    header = event["commonEventHeader"]
    observed_at = datetime.fromtimestamp(header["lastEpochMicrosec"] / 1_000_000, tz=UTC)
    domain = header.get("domain")
    cell_id = str(header["sourceName"])

    if domain == "fault":
        fault = event.get("faultFields", {})
        return TelemetryRecord(
            event_id=str(header["eventId"]),
            cell_id=cell_id,
            event_type=EventType.FAULT,
            observed_at=observed_at,
            severity=AlarmSeverity(str(fault.get("eventSeverity", "WARNING"))),
            alarm_condition=str(fault.get("alarmCondition", "unspecified")),
            source_event=payload,
        )

    measurements = event.get("measurementsForVfScalingFields", {}).get(
        "additionalMeasurements", {}
    )
    return TelemetryRecord(
        event_id=str(header["eventId"]),
        cell_id=cell_id,
        event_type=EventType.PERFORMANCE,
        observed_at=observed_at,
        kpis={str(name): float(value) for name, value in measurements.items()},
        source_event=payload,
    )


def generate_sample_events(
    *,
    cell_id: str = "cell-001",
    start_time: datetime | None = None,
    count: int = 6,
) -> tuple[dict[str, Any], ...]:
    """Generate deterministic public-safe PM events plus one warning alarm."""

    start = _utc(start_time or datetime(2026, 6, 10, 12, 0, tzinfo=UTC))
    events: list[dict[str, Any]] = []
    for offset in range(count):
        events.append(
            create_performance_event(
                cell_id=cell_id,
                observed_at=start + timedelta(seconds=10 * offset),
                latency_ms=20.0 + offset * 4,
                throughput_mbps=110.0 + offset * 5,
                sgnb_addition_attempts=100,
                sgnb_addition_successes=98 - (offset % 2),
            )
        )
    events.append(
        create_fault_event(
            cell_id=cell_id,
            observed_at=start + timedelta(seconds=35),
            severity=AlarmSeverity.WARNING,
            alarm_condition="lab-interference-warning",
        )
    )
    return tuple(events)


def normalize_events(events: Iterable[Mapping[str, Any]]) -> tuple[TelemetryRecord, ...]:
    return tuple(ves_event_to_record(event) for event in events)
