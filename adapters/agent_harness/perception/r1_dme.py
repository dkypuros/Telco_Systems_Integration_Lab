"""Dependency-free repo-local R1 DME-style telemetry query facade.

This module intentionally models a safe local boundary only. It does not claim
formal O-RAN R1, Ericsson EIAP, Elasticsearch, or TM Forum conformance.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_CLAIM_BOUNDARY = "repo-local R1 DME-style telemetry facade; not formal O-RAN, EIAP, or TM Forum conformance"
_DEFAULT_DATA_TYPES: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    (
        "dme.telemetry.pm.cell-kpi",
        "Cell performance telemetry",
        "Public-safe O1/VES-inspired per-cell KPI measurements exposed through a local DME-style query boundary.",
        ("pm", "kpi", "cell", "telemetry"),
    ),
    (
        "dme.telemetry.fm.cell-alarms",
        "Cell alarm telemetry",
        "Public-safe O1/VES-inspired alarm events exposed through a local DME-style query boundary.",
        ("fm", "alarm", "cell", "telemetry"),
    ),
)


@dataclass(frozen=True)
class DmeDataType:
    """Registered local DME-style data type metadata."""

    data_type_id: str
    name: str
    description: str = ""
    keywords: tuple[str, ...] = ()
    claim_boundary: str = _CLAIM_BOUNDARY
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class TelemetryQuery:
    """Query arguments accepted by the local DME-style facade."""

    data_type_id: str
    cell_id: str | None = None
    start_time: datetime | str | None = None
    end_time: datetime | str | None = None
    kpis: tuple[str, ...] = ()
    severities: tuple[str, ...] = ()
    limit: int = 25

    def normalized(self) -> "TelemetryQuery":
        return TelemetryQuery(
            data_type_id=self.data_type_id,
            cell_id=self.cell_id.strip() if isinstance(self.cell_id, str) and self.cell_id.strip() else None,
            start_time=_coerce_datetime(self.start_time),
            end_time=_coerce_datetime(self.end_time),
            kpis=tuple(str(item) for item in self.kpis if str(item).strip()),
            severities=tuple(str(item).upper() for item in self.severities if str(item).strip()),
            limit=max(1, int(self.limit)),
        )

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class DmeDataJob:
    """Local DME-style data job metadata."""

    data_type_id: str
    job_definition: TelemetryQuery
    consumer_id: str
    data_job_id: str = field(default_factory=lambda: str(uuid4()))
    target_uri: str | None = None
    status: str = "ACTIVE"
    claim_boundary: str = _CLAIM_BOUNDARY
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


@dataclass(frozen=True)
class _NormalizedRecord:
    """Internal normalized telemetry record."""

    timestamp: datetime
    cell_id: str
    data_type_id: str
    severity: str | None
    source: str
    kpis: Mapping[str, float]


@dataclass(frozen=True)
class TelemetryQueryResult:
    """Compact local DME-style response payload for an agent caller."""

    data_type_id: str
    filters: Mapping[str, Any]
    total_events: int
    time_window: Mapping[str, str | None]
    severity_counts: Mapping[str, int]
    kpi_summaries: tuple[Mapping[str, Any], ...]
    samples: tuple[Mapping[str, Any], ...]
    agent_context: Mapping[str, Any]
    target_interface: str = "R1_DME"
    model_label: str = "repo-local R1 DME telemetry query response"
    claim_boundary: str = _CLAIM_BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        return _to_plain(self)


class R1DmeQueryFacade:
    """Expose a local telemetry source through a typed R1 DME-style facade."""

    def __init__(self, telemetry_source: Any, *, now_provider: Any | None = None) -> None:
        self._telemetry_source = telemetry_source
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))
        self._data_types = {
            data_type.data_type_id: data_type
            for data_type in (
                DmeDataType(data_type_id=data_type_id, name=name, description=description, keywords=keywords)
                for data_type_id, name, description, keywords in _DEFAULT_DATA_TYPES
            )
        }
        self._jobs: dict[str, DmeDataJob] = {}

    def register_data_type(self, data_type: DmeDataType | Mapping[str, Any]) -> DmeDataType:
        """Register a local DME-style data type."""
        item = self._coerce_data_type(data_type)
        self._data_types[item.data_type_id] = item
        return item

    def discover_data_types(self, *, keyword: str | None = None) -> list[dict[str, Any]]:
        """List registered local DME-style data types."""
        entries = list(self._data_types.values())
        if keyword and keyword.strip():
            needle = keyword.strip().lower()
            entries = [
                entry
                for entry in entries
                if needle in entry.data_type_id.lower()
                or needle in entry.name.lower()
                or any(needle in item.lower() for item in entry.keywords)
            ]
        return [entry.to_dict() for entry in sorted(entries, key=lambda item: item.data_type_id)]

    def create_data_job(
        self,
        *,
        data_type_id: str,
        consumer_id: str,
        query: TelemetryQuery | Mapping[str, Any],
        target_uri: str | None = None,
    ) -> dict[str, Any]:
        """Create a local DME-style data job for a compact telemetry query."""
        if data_type_id not in self._data_types:
            raise ValueError(f"unknown_data_type:{data_type_id}")
        normalized_query = self._coerce_query(query)
        if normalized_query.data_type_id != data_type_id:
            raise ValueError(f"query_data_type_mismatch:{normalized_query.data_type_id}")
        job = DmeDataJob(
            data_type_id=data_type_id,
            consumer_id=str(consumer_id),
            job_definition=normalized_query,
            target_uri=target_uri,
        )
        self._jobs[job.data_job_id] = job
        return job.to_dict()

    def list_data_jobs(self, *, consumer_id: str | None = None) -> list[dict[str, Any]]:
        """List local data jobs, optionally filtered by consumer."""
        jobs = list(self._jobs.values())
        if consumer_id is not None:
            jobs = [job for job in jobs if job.consumer_id == consumer_id]
        return [job.to_dict() for job in sorted(jobs, key=lambda item: item.created_at)]

    def query_telemetry(self, query: TelemetryQuery | Mapping[str, Any]) -> dict[str, Any]:
        """Run a compact local telemetry query through the DME-style boundary."""
        normalized_query = self._coerce_query(query)
        if normalized_query.data_type_id not in self._data_types:
            raise ValueError(f"unknown_data_type:{normalized_query.data_type_id}")

        matching = [record for record in self._iter_records() if self._matches(record, normalized_query)]
        matching.sort(key=lambda item: item.timestamp, reverse=True)
        limited = matching[: normalized_query.limit]

        result = TelemetryQueryResult(
            data_type_id=normalized_query.data_type_id,
            filters={
                "cell_id": normalized_query.cell_id,
                "start_time": _maybe_iso(normalized_query.start_time),
                "end_time": _maybe_iso(normalized_query.end_time),
                "kpis": list(normalized_query.kpis),
                "severities": list(normalized_query.severities),
                "limit": normalized_query.limit,
            },
            total_events=len(matching),
            time_window={
                "start": _maybe_iso(matching[-1].timestamp if matching else normalized_query.start_time),
                "end": _maybe_iso(matching[0].timestamp if matching else normalized_query.end_time),
            },
            severity_counts=dict(Counter(record.severity for record in matching if record.severity)),
            kpi_summaries=self._summarize_kpis(matching, normalized_query.kpis),
            samples=self._build_samples(limited),
            agent_context=self._build_agent_context(matching, normalized_query),
        )
        return result.to_dict()

    def _iter_records(self) -> Iterable[_NormalizedRecord]:
        source = self._telemetry_source
        if hasattr(source, "query_records"):
            raw_records = source.query_records()
        elif hasattr(source, "list_records"):
            raw_records = source.list_records()
        else:
            raw_records = source
        for raw in raw_records:
            normalized = self._normalize_record(raw)
            if normalized is not None:
                yield normalized

    @staticmethod
    def _coerce_data_type(data_type: DmeDataType | Mapping[str, Any]) -> DmeDataType:
        if isinstance(data_type, DmeDataType):
            return data_type
        return DmeDataType(
            data_type_id=str(data_type["data_type_id"]),
            name=str(data_type["name"]),
            description=str(data_type.get("description", "")),
            keywords=tuple(str(item) for item in data_type.get("keywords", ()) or ()),
        )

    @staticmethod
    def _coerce_query(query: TelemetryQuery | Mapping[str, Any]) -> TelemetryQuery:
        if isinstance(query, TelemetryQuery):
            return query.normalized()
        return TelemetryQuery(
            data_type_id=str(query["data_type_id"]),
            cell_id=query.get("cell_id"),
            start_time=query.get("start_time"),
            end_time=query.get("end_time"),
            kpis=tuple(str(item) for item in query.get("kpis", ()) or ()),
            severities=tuple(str(item) for item in query.get("severities", ()) or ()),
            limit=int(query.get("limit", 25)),
        ).normalized()

    @staticmethod
    def _normalize_record(raw: Any) -> _NormalizedRecord | None:
        payload = _coerce_mapping(raw)
        timestamp = _coerce_datetime(
            payload.get("timestamp") or payload.get("event_time") or payload.get("observed_at") or payload.get("time")
        )
        cell_id = str(payload.get("cell_id") or payload.get("resource_id") or payload.get("managed_object") or "").strip()
        data_type_id = str(payload.get("data_type_id") or payload.get("kind") or "").strip()
        if timestamp is None or not cell_id or not data_type_id:
            return None

        metric_payload = payload.get("kpis") or payload.get("metrics") or {}
        metrics = {
            str(name): float(value)
            for name, value in _coerce_mapping(metric_payload).items()
            if _is_number(value)
        }

        severity = payload.get("severity") or payload.get("alarm_severity")
        return _NormalizedRecord(
            timestamp=timestamp,
            cell_id=cell_id,
            data_type_id=data_type_id,
            severity=str(severity).upper() if severity else None,
            source=str(payload.get("source") or payload.get("event_type") or "telemetry"),
            kpis=metrics,
        )

    @staticmethod
    def _matches(record: _NormalizedRecord, query: TelemetryQuery) -> bool:
        if record.data_type_id != query.data_type_id:
            return False
        if query.cell_id and record.cell_id != query.cell_id:
            return False
        if query.start_time and record.timestamp < query.start_time:
            return False
        if query.end_time and record.timestamp > query.end_time:
            return False
        if query.severities and (record.severity or "") not in query.severities:
            return False
        if query.kpis and not any(kpi in record.kpis for kpi in query.kpis):
            return False
        return True

    @staticmethod
    def _summarize_kpis(records: Sequence[_NormalizedRecord], requested_kpis: Sequence[str]) -> tuple[Mapping[str, Any], ...]:
        requested = tuple(dict.fromkeys(str(item) for item in requested_kpis if str(item).strip()))
        if requested:
            kpis = requested
        else:
            discovered: dict[str, None] = {}
            for record in records:
                for name in record.kpis:
                    discovered.setdefault(name, None)
            kpis = tuple(discovered)

        summaries: list[Mapping[str, Any]] = []
        for kpi in kpis:
            series = [
                {"timestamp": _maybe_iso(record.timestamp), "value": record.kpis[kpi]}
                for record in reversed(records)
                if kpi in record.kpis
            ]
            if not series:
                continue
            values = [point["value"] for point in series]
            summaries.append(
                {
                    "kpi": kpi,
                    "count": len(values),
                    "minimum": min(values),
                    "maximum": max(values),
                    "average": round(sum(values) / len(values), 3),
                    "latest": series[-1]["value"],
                    "samples": series[-5:],
                }
            )
        return tuple(summaries)

    @staticmethod
    def _build_samples(records: Sequence[_NormalizedRecord]) -> tuple[Mapping[str, Any], ...]:
        return tuple(
            {
                "timestamp": _maybe_iso(record.timestamp),
                "cell_id": record.cell_id,
                "severity": record.severity,
                "source": record.source,
                "kpis": dict(record.kpis),
            }
            for record in reversed(records[-5:])
        )

    def _build_agent_context(self, records: Sequence[_NormalizedRecord], query: TelemetryQuery) -> Mapping[str, Any]:
        kpi_summaries = self._summarize_kpis(records, query.kpis)
        highlights = [
            f"{summary['kpi']}: avg={summary['average']} latest={summary['latest']} max={summary['maximum']}"
            for summary in kpi_summaries[:3]
        ]
        if not highlights:
            highlights = ["No matching telemetry records found for the requested filter set."]
        return {
            "cell_id": query.cell_id,
            "data_type_id": query.data_type_id,
            "event_count": len(records),
            "severity_counts": dict(Counter(record.severity for record in records if record.severity)),
            "highlights": highlights,
            "query_window": {
                "start": _maybe_iso(query.start_time),
                "end": _maybe_iso(query.end_time or self._now_provider()),
            },
        }


def _coerce_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value):
        return {item.name: getattr(value, item.name) for item in fields(value)}
    return {}


def _coerce_datetime(value: datetime | str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _maybe_iso(value: datetime | None) -> str | None:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if value else None


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _to_plain(value: Any) -> Any:
    if isinstance(value, datetime):
        return _maybe_iso(value)
    if is_dataclass(value):
        return {item.name: _to_plain(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _to_plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_to_plain(item) for item in value]
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    return value
