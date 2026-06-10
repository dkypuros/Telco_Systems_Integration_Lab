from adapters.agent_harness import AgentHarnessBoundary, SkillSpec, create_default_server


RAW_WIRE_WORDS = ("ssh", "netconf", "gnmi", "restconf", "snmp")


def payloads_by_type(result):
    return {payload["payload_type"]: payload for payload in result["payloads"]}


def assert_no_executable_wire_command(result):
    for payload in result.get("payloads", []):
        assert payload["contains_executable_wire_command"] is False
        assert "command" not in payload["body"]
        assert "raw_payload" not in payload["body"]


def test_get_cell_telemetry_builds_r1_dme_and_tmf628_queries():
    result = create_default_server().call_tool(
        "get_cell_telemetry",
        {"cell_id": "NRCellDU=cell-1", "kpis": ["RRU.PrbUsedDl", "DRB.UEThpDl"]},
    )

    assert result["decision"]["status"] == "ALLOW"
    payloads = payloads_by_type(result)
    assert payloads["telemetry_subscription"]["target_interface"] == "R1_DME"
    assert payloads["telemetry_subscription"]["execution_owner"] == "HARNESS"
    assert payloads["telemetry_query"]["target_interface"] == "TMF628_QUERY_MODEL"
    assert "not formal O-RAN, TM Forum, or MCP conformance" in payloads["telemetry_query"]["claim_boundary"]
    assert payloads["telemetry_query"]["body"]["execution"] == "query_payload_only_no_network_egress"
    assert_no_executable_wire_command(result)


def test_correlate_cell_alarm_builds_tmf642_query():
    result = create_default_server().call_tool(
        "correlate_cell_alarm",
        {"cell_id": "NRCellDU=cell-1", "service_id": "svc-private-5g", "severity": "MAJOR"},
    )

    assert result["decision"]["status"] == "ALLOW"
    payload = result["payloads"][0]
    assert payload["target_interface"] == "TMF642_QUERY_MODEL"
    assert payload["execution_owner"] == "NONE"
    assert payload["body"]["filters"] == {
        "cell_id": "NRCellDU=cell-1",
        "service_id": "svc-private-5g",
        "severity": "MAJOR",
    }
    assert payload["body"]["service_impact_context"]["impact_scope"] == "candidate_service_impact_context"
    assert_no_executable_wire_command(result)


def test_mitigate_cell_interference_returns_r1_sme_intent_and_preflight():
    args = {
        "cell_id": "NRCellDU=cell-1",
        "adjustment": {"pci_conflict_mitigation": "reduce_power_1db"},
        "adjacent_cells": ["NRCellDU=cell-2"],
    }
    first = create_default_server().call_tool("mitigate_cell_interference", args)
    second = create_default_server().call_tool("mitigate_cell_interference", args)

    assert first["decision"]["status"] == "ALLOW"
    payloads = payloads_by_type(first)
    intent = payloads["remediation_intent"]
    preflight = payloads["preflight_evidence"]
    assert intent["target_interface"] == "R1_SME"
    assert intent["execution_owner"] == "SMO"
    assert intent["body"]["execution_boundary"] == "harness_stops_at_smo_boundary_smo_owns_o1_a1_execution"
    assert preflight["target_interface"] == "HARNESS_PREFLIGHT"
    assert preflight["body"]["blast_radius"] == {
        "target_cell": "NRCellDU=cell-1",
        "adjacent_cells": ["NRCellDU=cell-2"],
        "max_cells_touched": 2,
    }
    assert preflight["body"]["idempotency_key"] == payloads_by_type(second)["preflight_evidence"]["body"]["idempotency_key"]
    assert preflight["body"]["policy"]["direct_wire_protocols_denied"] == list(RAW_WIRE_WORDS)
    assert_no_executable_wire_command(first)


def test_boundary_denies_direct_wire_skill_spec():
    decision = AgentHarnessBoundary().evaluate_skill_spec(
        SkillSpec(
            name="unsafe_low_level_config",
            tool_name="mitigate_cell_interference",
            egress_protocols=("R1", "NETCONF"),
        )
    )

    assert decision.status.value == "DENY"
    assert decision.allowed is False
    assert "direct_wire_protocol_denied:netconf" in decision.reasons


def test_boundary_enforces_declared_target_interfaces():
    boundary = AgentHarnessBoundary()

    safe = boundary.evaluate_skill_spec(
        SkillSpec(
            name="safe_telemetry",
            tool_name="get_cell_telemetry",
            target_interfaces=("R1_DME", "TMF628_QUERY_MODEL"),
        )
    )
    unsafe = boundary.evaluate_skill_spec(
        SkillSpec(
            name="unsafe_target",
            tool_name="mitigate_cell_interference",
            target_interfaces=("NETCONF",),
        )
    )

    assert safe.status.value == "ALLOW"
    assert unsafe.status.value == "DENY"
    assert "unsupported_target_interface:netconf" in unsafe.reasons


def test_unknown_tool_and_missing_arguments_are_rejected():
    server = create_default_server()

    unknown = server.call_tool("open_ssh_session", {"cell_id": "NRCellDU=cell-1"})
    missing = server.call_tool("get_cell_telemetry", {"cell_id": "NRCellDU=cell-1"})

    assert unknown["decision"]["status"] == "DENY"
    assert "unknown_tool:open_ssh_session" in unknown["decision"]["reasons"]
    assert missing["decision"]["status"] == "INVALID"
    assert "missing_required_argument:kpis" in missing["decision"]["reasons"]


def test_tool_call_denies_direct_wire_protocol_arguments():
    result = create_default_server().call_tool(
        "mitigate_cell_interference",
        {
            "cell_id": "NRCellDU=cell-1",
            "adjustment": {"protocol": "gNMI", "set": "power"},
        },
    )

    assert result["decision"]["status"] == "DENY"
    assert "direct_wire_protocol_denied:gnmi" in result["decision"]["reasons"]
    assert result["payloads"] == []
