"""Local data-layer mock for normalized telemetry records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from .generator import ves_event_to_record
from .models import AlarmSeverity, EventType, TelemetryQuery, TelemetryRecord


class InMemoryTelemetryStore:
    """Small queryable persistence mock.

    This deliberately does not pretend to be Ericsson EIAP SDL or production
    Elasticsearch.  It gives tests and demos deterministic search-store behavior
    while keeping agents behind a typed R1 DME-style facade.
    """

    def __init__(self) -> None:
        self._records: list[TelemetryRecord] = []

    def ingest(self, records: Iterable[TelemetryRecord]) -> tuple[TelemetryRecord, ...]:
        accepted = tuple(records)
        self._records.extend(accepted)
        self._records.sort(key=lambda record: (record.observed_at, record.event_id))
        return accepted

    def ingest_ves(self, payloads: Iterable[Mapping[str, object]]) -> tuple[TelemetryRecord, ...]:
        return self.ingest(ves_event_to_record(payload) for payload in payloads)

    def query(self, query: TelemetryQuery | None = None) -> tuple[TelemetryRecord, ...]:
        query = query or TelemetryQuery()
        matches = [record for record in self._records if _matches(record, query)]
        return tuple(matches[: max(query.limit, 0)])

    def index_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self._records:
            counts[record.index_name] = counts.get(record.index_name, 0) + 1
        return counts

    def dump_jsonl(self, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8") as handle:
            for record in self._records:
                handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")


def _matches(record: TelemetryRecord, query: TelemetryQuery) -> bool:
    if query.cell_id and record.cell_id != query.cell_id:
        return False
    if query.start_time and record.observed_at < query.start_time:
        return False
    if query.end_time and record.observed_at >= query.end_time:
        return False
    if query.event_type and record.event_type is not _coerce_event_type(query.event_type):
        return False
    if query.severity and record.severity is not _coerce_severity(query.severity):
        return False
    if query.kpi_names and not any(name in record.kpis for name in query.kpi_names):
        return False
    return True


def _coerce_event_type(value: EventType | str) -> EventType:
    return value if isinstance(value, EventType) else EventType(value)


def _coerce_severity(value: AlarmSeverity | str) -> AlarmSeverity:
    return value if isinstance(value, AlarmSeverity) else AlarmSeverity(value)
