from datetime import UTC, datetime, timedelta

from adapters.telemetry_pipeline import (
    AlarmSeverity,
    EventType,
    InMemoryTelemetryStore,
    R1DmeFacade,
    SummarizationPolicy,
    TelemetryQuery,
    create_fault_event,
    create_performance_event,
    detect_dataframe_backend,
    generate_sample_events,
    normalize_events,
    summarize_for_agent,
    ves_event_to_record,
)


def test_generator_normalizes_ves_like_pm_and_fm_events():
    observed_at = datetime(2026, 6, 10, 12, 0, tzinfo=UTC)
    pm_payload = create_performance_event(
        cell_id="cell-a",
        observed_at=observed_at,
        latency_ms=32.5,
        throughput_mbps=120.0,
        sgnb_addition_attempts=100,
        sgnb_addition_successes=99,
    )
    fm_payload = create_fault_event(
        cell_id="cell-a",
        observed_at=observed_at + timedelta(seconds=5),
        severity=AlarmSeverity.MAJOR,
        alarm_condition="lab-interference",
    )

    pm_record = ves_event_to_record(pm_payload)
    fm_record = ves_event_to_record(fm_payload)

    assert pm_record.cell_id == "NRCellDU=cell-a"
    assert pm_record.event_type is EventType.PERFORMANCE
    assert pm_record.kpis["cell_latency_ms"] == 32.5
    assert pm_record.topology["managed_element"] == "ManagedElement=lab-smo-managed-element"
    assert pm_record.topology["gnb_du_function"] == "GNBDUFunction=lab-gnbdu-1"
    assert pm_record.topology["nr_cell_du"] == "NRCellDU=cell-a"
    assert fm_record.event_type is EventType.FAULT
    assert fm_record.severity is AlarmSeverity.MAJOR
    assert fm_record.alarm_condition == "lab-interference"
    assert pm_record.index_name == "telemetry-20260610"


def test_store_queries_by_cell_time_kpi_and_severity():
    records = normalize_events(generate_sample_events(cell_id="cell-a"))
    store = InMemoryTelemetryStore()
    store.ingest(records)

    performance = store.query(
        TelemetryQuery(cell_id="cell-a", event_type=EventType.PERFORMANCE, kpi_names=("cell_latency_ms",))
    )
    warnings = store.query(TelemetryQuery(cell_id="cell-a", severity=AlarmSeverity.WARNING))

    assert len(performance) == 6
    assert all(record.cell_id == "NRCellDU=cell-a" for record in performance)
    assert len(warnings) == 1
    assert warnings[0].alarm_condition == "lab-interference-warning"
    assert store.index_counts() == {"telemetry-20260610": 7}


def test_r1_dme_facade_exposes_jobs_without_direct_store_coupling():
    store = InMemoryTelemetryStore()
    store.ingest(normalize_events(generate_sample_events(cell_id="cell-b")))
    facade = R1DmeFacade(store)

    data_types = facade.discover_data_types()
    request = facade.create_data_request(
        data_type_id=data_types[0].data_type_id,
        query=TelemetryQuery(cell_id="cell-b", limit=3),
    )
    result = facade.query_data_request(request.request_id)

    assert data_types[0].source_interface == "O1/VES-inspired"
    assert "not formal" in data_types[0].claim_boundary
    assert len(result.records) == 3
    assert result.to_dict()["request"]["data_type_id"] == "oran.telemetry.cell.pm-fm.v1"


def test_summarizer_outputs_compact_context_with_backpressure_windowing():
    base = datetime(2026, 6, 10, 12, 0, tzinfo=UTC)
    payloads = [
        create_performance_event(
            cell_id="cell-hot",
            observed_at=base + timedelta(seconds=offset),
            latency_ms=20.0 + offset,
            throughput_mbps=100.0 + offset,
            sgnb_addition_attempts=100,
            sgnb_addition_successes=90,
        )
        for offset in range(5)
    ]
    payloads.append(
        create_fault_event(
            cell_id="cell-hot",
            observed_at=base + timedelta(seconds=5),
            severity=AlarmSeverity.CRITICAL,
            alarm_condition="lab-critical-alarm",
        )
    )
    records = normalize_events(payloads)

    context = summarize_for_agent(
        records,
        policy=SummarizationPolicy(
            tumbling_window_seconds=60,
            max_events_per_window=3,
            latency_threshold_ms=22.0,
            sgnb_success_rate_floor=0.95,
        ),
    )

    assert context.payload_type == "agent.telemetry-context.v1"
    assert context.total_events_seen == 6
    assert context.total_events_retained == 3
    assert context.total_events_dropped == 3
    window = context.windows[0]
    assert window.event_count == 6
    assert window.retained_event_count == 3
    assert "backpressure_applied" in window.anomaly_flags
    assert "latency_threshold_exceeded" in window.anomaly_flags
    assert "sgnb_success_rate_below_floor" in window.anomaly_flags
    assert "high_severity_alarm_present" in window.anomaly_flags


def test_backend_detection_is_safe_without_optional_gpu_dependency():
    backend = detect_dataframe_backend()

    assert backend.name in {"cudf", "pandas-compatible-cpu", "stdlib-cpu"}
    assert isinstance(backend.gpu_accelerated, bool)
    assert backend.reason


def test_agent_context_payload_has_claim_boundary_not_conformance_claim():
    store = InMemoryTelemetryStore()
    store.ingest(normalize_events(generate_sample_events()))
    context = summarize_for_agent(store.query())
    payload = context.to_dict()

    assert "not NVIDIA or O-RAN conformance" in payload["claim_boundary"]
    assert payload["policy"]["overflow_strategy"] == "keep_latest"
    assert payload["topology_context"]["NRCellDU=cell-001"]["distinguished_name"].endswith("NRCellDU=cell-001")
    assert payload["windows"]
