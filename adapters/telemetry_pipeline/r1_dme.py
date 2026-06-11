"""Mock R1 DME-style facade over the local telemetry store."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid5, NAMESPACE_URL

from .models import DmeDataJob, DmeDataType, DmeQueryResult, TelemetryQuery
from .store import InMemoryTelemetryStore

DEFAULT_CLAIM_BOUNDARY = (
    "Lab R1 DME-style data exposure mock; not formal O-RAN, EIAP, or TM Forum conformance."
)


class R1DmeFacade:
    """Expose telemetry by data types and data jobs, never direct store handles."""

    def __init__(self, store: InMemoryTelemetryStore) -> None:
        self._store = store
        self._data_types: dict[str, DmeDataType] = {}
        self._jobs: dict[str, DmeDataJob] = {}
        self.register_data_type(
            "oran.telemetry.cell.pm-fm.v1",
            "O1/VES-inspired cell performance and fault telemetry for lab agents.",
        )

    def register_data_type(self, data_type_id: str, description: str) -> DmeDataType:
        data_type = DmeDataType(
            data_type_id=data_type_id,
            description=description,
            source_interface="O1/VES-inspired",
            claim_boundary=DEFAULT_CLAIM_BOUNDARY,
        )
        self._data_types[data_type_id] = data_type
        return data_type

    def discover_data_types(self) -> tuple[DmeDataType, ...]:
        return tuple(self._data_types[key] for key in sorted(self._data_types))

    def create_data_job(
        self,
        *,
        data_type_id: str = "oran.telemetry.cell.pm-fm.v1",
        query: TelemetryQuery | None = None,
    ) -> DmeDataJob:
        if data_type_id not in self._data_types:
            raise ValueError(f"unknown data type: {data_type_id}")
        query = query or TelemetryQuery()
        created_at = datetime.now(tz=UTC)
        job_id = str(uuid5(NAMESPACE_URL, f"{data_type_id}:{query!r}:{created_at.isoformat()}"))
        job = DmeDataJob(
            job_id=job_id,
            data_type_id=data_type_id,
            query=query,
            created_at=created_at,
        )
        self._jobs[job_id] = job
        return job

    def query_data_job(self, job_id: str) -> DmeQueryResult:
        if job_id not in self._jobs:
            raise ValueError(f"unknown data job: {job_id}")
        job = self._jobs[job_id]
        return DmeQueryResult(job=job, records=self._store.query(job.query))
