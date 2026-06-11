"""Store-facing R1 DME-style facade (the pipeline-internal boundary).

This is one of two R1 DME-style facades in the lab; they are layers, not rivals:

* This ``R1DmeFacade`` is the **pipeline-internal** boundary. It sits directly on a
  typed :class:`InMemoryTelemetryStore`, registers the combined data type
  ``oran.telemetry.cell.pm-fm.v1``, and returns typed :class:`TelemetryRecord`
  objects. Use it inside the pipeline / in tests that want typed results.
* :class:`adapters.agent_harness.perception.r1_dme.R1DmeQueryFacade` is the
  **agent-facing** adapter. It is dependency-free, splits the agent-facing data
  types into ``dme.telemetry.pm.cell-kpi`` / ``dme.telemetry.fm.cell-alarms``, and
  returns compact JSON-able payloads (no raw store handles). It can wrap the records
  this store yields, so the agent layer composes on top of this one.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable
from uuid import uuid5, NAMESPACE_URL

from .models import DmeDataRequest, DmeDataType, DmeQueryResult, TelemetryQuery
from .store import InMemoryTelemetryStore

DEFAULT_CLAIM_BOUNDARY = (
    "Lab R1 DME-style data request/subscription mock; not formal O-RAN, EIAP, or TM Forum conformance."
)


class R1DmeFacade:
    """Expose telemetry by data types and data requests, never direct store handles."""

    def __init__(
        self,
        store: InMemoryTelemetryStore,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = store
        # Injectable clock so request ids/timestamps can be made deterministic in tests.
        self._now = now_provider or (lambda: datetime.now(tz=UTC))
        self._data_types: dict[str, DmeDataType] = {}
        self._requests: dict[str, DmeDataRequest] = {}
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

    def create_data_request(
        self,
        *,
        data_type_id: str = "oran.telemetry.cell.pm-fm.v1",
        query: TelemetryQuery | None = None,
    ) -> DmeDataRequest:
        if data_type_id not in self._data_types:
            raise ValueError(f"unknown data type: {data_type_id}")
        query = query or TelemetryQuery()
        created_at = self._now()
        request_id = str(uuid5(NAMESPACE_URL, f"{data_type_id}:{query!r}:{created_at.isoformat()}"))
        request = DmeDataRequest(
            request_id=request_id,
            data_type_id=data_type_id,
            query=query,
            created_at=created_at,
        )
        self._requests[request_id] = request
        return request

    def create_data_job(self, **kwargs: object) -> DmeDataRequest:
        """Compatibility alias; prefer create_data_request for R1 DME language."""

        return self.create_data_request(**kwargs)

    def query_data_request(self, request_id: str) -> DmeQueryResult:
        if request_id not in self._requests:
            raise ValueError(f"unknown data request: {request_id}")
        request = self._requests[request_id]
        return DmeQueryResult(request=request, records=self._store.query(request.query))

    def query_data_job(self, job_id: str) -> DmeQueryResult:
        """Compatibility alias; prefer query_data_request for R1 DME language."""

        return self.query_data_request(job_id)
