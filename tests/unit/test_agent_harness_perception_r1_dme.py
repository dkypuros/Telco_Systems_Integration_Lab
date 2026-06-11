import pytest

from adapters.agent_harness.perception import DmeDataType, R1DmeQueryFacade


class FakeTelemetryStore:
    def __init__(self, records):
        self._records = list(records)

    def list_records(self):
        return list(self._records)


def make_store():
    return FakeTelemetryStore(
        [
            {
                "timestamp": "2026-06-10T19:58:00Z",
                "cell_id": "NRCellDU=cell-1",
                "data_type_id": "dme.telemetry.pm.cell-kpi",
                "source": "ves_pm",
                "kpis": {"latency_ms": 14.0, "throughput_mbps": 122.0},
            },
            {
                "timestamp": "2026-06-10T20:00:00Z",
                "cell_id": "NRCellDU=cell-1",
                "data_type_id": "dme.telemetry.pm.cell-kpi",
                "source": "ves_pm",
                "kpis": {"latency_ms": 17.0, "throughput_mbps": 118.0},
            },
            {
                "timestamp": "2026-06-10T20:02:00Z",
                "cell_id": "NRCellDU=cell-2",
                "data_type_id": "dme.telemetry.pm.cell-kpi",
                "source": "ves_pm",
                "kpis": {"latency_ms": 11.0, "throughput_mbps": 140.0},
            },
            {
                "timestamp": "2026-06-10T20:03:00Z",
                "cell_id": "NRCellDU=cell-1",
                "data_type_id": "dme.telemetry.fm.cell-alarms",
                "source": "ves_fm",
                "severity": "major",
                "kpis": {"alarm_count": 1},
            },
        ]
    )


def test_r1_dme_facade_discovers_default_and_custom_data_types():
    facade = R1DmeQueryFacade(make_store())

    facade.register_data_type(
        DmeDataType(
            data_type_id="dme.telemetry.custom.packet-loss",
            name="Packet loss telemetry",
            keywords=("custom", "packet-loss"),
        )
    )

    data_types = facade.discover_data_types(keyword="telemetry")
    packet_loss = facade.discover_data_types(keyword="packet-loss")

    assert any(item["data_type_id"] == "dme.telemetry.pm.cell-kpi" for item in data_types)
    assert packet_loss == [
        {
            "data_type_id": "dme.telemetry.custom.packet-loss",
            "name": "Packet loss telemetry",
            "description": "",
            "keywords": ["custom", "packet-loss"],
            "claim_boundary": "repo-local R1 DME-style telemetry facade; not formal O-RAN, EIAP, or TM Forum conformance",
            "registered_at": packet_loss[0]["registered_at"],
        }
    ]


def test_r1_dme_facade_creates_data_job_and_queries_compact_response():
    facade = R1DmeQueryFacade(make_store())

    job = facade.create_data_request(
        data_type_id="dme.telemetry.pm.cell-kpi",
        consumer_id="rapp-perception-1",
        query={
            "data_type_id": "dme.telemetry.pm.cell-kpi",
            "cell_id": "NRCellDU=cell-1",
            "kpis": ["latency_ms", "throughput_mbps"],
            "start_time": "2026-06-10T19:57:00Z",
            "end_time": "2026-06-10T20:01:00Z",
        },
        target_uri="memory://agent-context",
    )

    result = facade.query_telemetry(job["job_definition"])

    assert job["status"] == "ACTIVE"
    assert job["data_request_id"] == job["data_job_id"]
    assert job["data_type_id"] == "dme.telemetry.pm.cell-kpi"
    assert job["job_definition"]["cell_id"] == "NRCellDU=cell-1"
    assert result["target_interface"] == "R1_DME"
    assert result["total_events"] == 2
    assert result["severity_counts"] == {}
    assert result["filters"]["kpis"] == ["latency_ms", "throughput_mbps"]
    assert result["kpi_summaries"][0]["kpi"] == "latency_ms"
    assert result["kpi_summaries"][0]["average"] == 15.5
    assert result["kpi_summaries"][0]["latest"] == 17.0
    assert result["agent_context"]["event_count"] == 2
    assert "latency_ms: avg=15.5 latest=17.0 max=17.0" in result["agent_context"]["highlights"]


def test_r1_dme_facade_filters_alarm_queries_by_severity():
    facade = R1DmeQueryFacade(make_store())

    result = facade.query_telemetry(
        {
            "data_type_id": "dme.telemetry.fm.cell-alarms",
            "cell_id": "NRCellDU=cell-1",
            "severities": ["major"],
            "limit": 5,
        }
    )

    assert result["total_events"] == 1
    assert result["severity_counts"] == {"MAJOR": 1}
    assert result["samples"][0]["severity"] == "MAJOR"
    assert result["samples"][0]["source"] == "ves_fm"


def test_r1_dme_facade_lists_data_requests_with_job_compatibility_alias():
    facade = R1DmeQueryFacade(make_store())

    request = facade.create_data_request(
        data_type_id="dme.telemetry.pm.cell-kpi",
        consumer_id="rapp-perception-1",
        query={"data_type_id": "dme.telemetry.pm.cell-kpi"},
    )

    assert facade.list_data_requests(consumer_id="rapp-perception-1") == [request]
    assert facade.list_data_jobs(consumer_id="rapp-perception-1") == [request]


def test_r1_dme_facade_rejects_job_query_data_type_mismatch():
    facade = R1DmeQueryFacade(make_store())

    with pytest.raises(ValueError, match="query_data_type_mismatch:dme.telemetry.fm.cell-alarms"):
        facade.create_data_request(
            data_type_id="dme.telemetry.pm.cell-kpi",
            consumer_id="rapp-perception-1",
            query={"data_type_id": "dme.telemetry.fm.cell-alarms"},
        )
