# Test spec: Issue #36 O-RAN Agent Harness boundary slice

## Unit tests
1. `test_get_cell_telemetry_builds_r1_dme_and_tmf628_queries`
   - Calls harness tool with `cell_id` and KPI list.
   - Expects ALLOW, R1 DME payload, TMF628 query model, and no direct wire execution owner.
2. `test_correlate_cell_alarm_builds_tmf642_query`
   - Calls alarm tool with cell/service/severity.
   - Expects TMF642 query model and service-impact context.
3. `test_mitigate_cell_interference_returns_r1_sme_intent_and_preflight`
   - Calls mitigation tool.
   - Expects R1 SME target, SMO-owned execution boundary, deterministic idempotency key, and blast-radius summary.
4. `test_boundary_denies_direct_wire_skill_spec`
   - Constructs a skill spec declaring forbidden protocol egress.
   - Expects DENY with direct-wire reason.
5. `test_unknown_tool_and_missing_arguments_are_denied_or_invalid`
   - Unknown tool raises/returns denied invalid result.
   - Missing target cell fails validation.
6. `test_safe_outputs_do_not_expose_executable_wire_commands`
   - Allowed tool outputs do not include executable command fields for SSH/NETCONF/gNMI/RESTCONF/SNMP.

## Integration / smoke checks
- Run `python3 -m pytest tests/unit/test_agent_harness_boundary.py`.
- Run broader relevant tests: `python3 -m pytest tests/unit/test_nanda_harness_commerce.py tests/unit/test_oran_spec_map_validation.py tests/unit/test_agent_harness_boundary.py`.
- Run `git diff --check`.
- Run public-safety path grep from AGENTS guidance on changed files.

## Documentation verification
- `docs/README.md` links `docs/agent-harness-boundary.md`.
- Boundary doc states the implementation is a deterministic harness/model slice, not formal O-RAN/TMF/MCP conformance.
