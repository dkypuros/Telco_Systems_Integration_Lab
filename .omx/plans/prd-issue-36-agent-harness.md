# PRD: Issue #36 O-RAN Agent Harness boundary slice

## Goal
Deliver a deterministic repo-local Agent Harness slice for issue #36 that lets AI tools express telemetry and remediation intents while preventing direct raw protocol access to telecom network elements.

## Non-goals
- No live Ericsson EIAP integration.
- No GPU RAPIDS/Morpheus runtime.
- No formal TM Forum or O-RAN conformance claim.
- No new third-party MCP SDK dependency.
- No direct NETCONF/gNMI/RESTCONF/SNMP/SSH execution.

## User stories

### US-001: Safe telemetry skill payloads
As an AI agent, I can call `get_cell_telemetry` with a target cell and KPI list so the harness returns typed R1 DME and TMF628-style query payloads rather than raw polling commands.

Acceptance criteria:
- Payload target interface is R1 DME for telemetry subscription.
- TMF628 query is labeled as a harness/query model, not a conformance implementation.
- Payload contains no executable raw wire command.

### US-002: Alarm correlation payloads
As an AI agent, I can call `correlate_cell_alarm` so the harness returns a TMF642-style alarm query with service-impact context fields.

Acceptance criteria:
- Query includes cell/service filters and optional severity.
- Harness marks the payload as a query/normalization request, not direct network access.

### US-003: Safe remediation intent
As an AI agent, I can call `mitigate_cell_interference` with a target cell and intended adjustment so the harness returns a typed R1 SME action intent plus deterministic preflight evidence.

Acceptance criteria:
- Harness output says execution jurisdiction ends at the harness/SMO boundary.
- Downstream execution is represented as SMO-owned, not LLM-owned.
- Direct wire protocols are denied by policy.
- Idempotency key and blast-radius fields are deterministic.

### US-004: Boundary policy enforcement
As a lab maintainer, I can prove the harness denies unsafe skill specs or tool calls that request SSH, NETCONF, gNMI, RESTCONF, or SNMP egress.

Acceptance criteria:
- Unit tests cover denied direct-wire protocols.
- Unit tests cover unknown tools and missing required arguments.
- Unit tests cover allowed R1/TMF-only paths.

### US-005: Documentation and claim hygiene
As a reviewer, I can read a short doc explaining where MCP-like tool exposure ends, where harness policy begins, and why this is not a production conformance claim.

Acceptance criteria:
- Documentation names R1 DME, R1 SME, TMF628/TMF642 query models, SMO-owned O1/A1 execution, and forbidden direct-wire protocols.
- Docs index links the new boundary document.

## Implementation sketch
- `adapters/agent_harness/models.py`: typed dataclasses/enums for tool calls, skill specs, decisions, payloads.
- `adapters/agent_harness/boundary.py`: zero-trust-style boundary policy for safe interface/protocol allowlists.
- `adapters/agent_harness/intent_translator.py`: deterministic builders for R1 DME, TMF628/TMF642 query, R1 SME action intent, and preflight.
- `adapters/agent_harness/mcp_server.py`: dependency-free MCP-compatible local tool registry with `call_tool`.
- `tests/unit/test_agent_harness_boundary.py`: proof of safe paths and denied unsafe paths.
- `docs/agent-harness-boundary.md`: claim-boundary documentation.

## Risks and mitigations
- Risk: readers mistake query payloads for real TMF conformance. Mitigation: explicit claim boundary in models/docs/tests.
- Risk: MCP wording implies SDK compliance. Mitigation: call it MCP-compatible/local registry unless a real MCP SDK is later introduced.
- Risk: direct raw protocol terms appear in docs/tests and confuse grep-based checks. Mitigation: use them as forbidden protocol names only, not secrets/commands.

## Execution lane
Use Ralph persistence and Team/swarm parallelism. Team lanes: core implementation, tests/verification, docs/claim hygiene. Leader integrates, runs tests, deslop/simplification, and architect verification.
