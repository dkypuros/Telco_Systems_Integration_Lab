# O-RAN Agent Harness Boundary

Status: deterministic repo-local boundary slice for issue #36.

This document describes the lab-owned Agent Harness pattern that lets an AI agent
request telemetry or remediation while preserving telecom interface boundaries.
It is intentionally a **model and test harness**, not a production MCP server and
not a formal O-RAN or TM Forum conformance claim.

## Boundary principle

The AI-facing skill layer never owns raw network execution. A tool call may ask
for a cell KPI, alarm correlation, or remediation intent, but the harness returns
only typed, standards-aligned model payloads:

- R1 DME-style telemetry subscription payloads for normalized KPI access.
- TMF628-style performance query models for OSS/BSS enrichment context.
- TMF642-style alarm query models for service-impact correlation.
- R1 SME-style action intents for remediation requests.
- Harness preflight evidence for idempotency and blast-radius review.

The harness denies direct-wire protocol egress from skill declarations and tool
arguments. Forbidden direct skill egress includes SSH, NETCONF, gNMI, RESTCONF,
and SNMP. Those protocols may still exist downstream in the telecom stack, but
they are owned by deterministic SMO/RIC/network components, not by the LLM skill.

## Execution flow

```text
LLM tool call
  -> local MCP-compatible AgentHarnessServer.call_tool(...)
  -> AgentHarnessBoundary policy check
  -> IntentTranslator typed payload builder
  -> R1 DME / TMF query / R1 SME intent model
  -> SMO-owned validation and downstream O1/A1/vendor execution outside this slice
```

For remediation, the returned R1 SME intent explicitly states that the harness
stops at the SMO boundary. The SMO or equivalent deterministic controller owns
policy validation, simulation, and any eventual O1/A1/vendor payload generation.

## Repository implementation

- `adapters/agent_harness/models.py` defines safe result, payload, decision, and
  interface enums.
- `adapters/agent_harness/boundary.py` rejects unknown tools, missing required
  arguments, and direct-wire protocols.
- `adapters/agent_harness/intent_translator.py` builds deterministic R1 DME,
  TMF628-style, TMF642-style, R1 SME, and preflight payloads.
- `adapters/agent_harness/mcp_server.py` provides a dependency-free local
  MCP-compatible registry shape with `list_tools()` and `call_tool()`.
- `tests/unit/test_agent_harness_boundary.py` proves allowed and denied paths.

## Claim boundary

This slice demonstrates boundary enforcement semantics inside the lab. It does
not prove live Ericsson EIAP interoperability, live MCP SDK compliance, GPU
RAPIDS/Morpheus streaming ETL, vector-memory persistence, or formal TM Forum /
O-RAN conformance. Those remain follow-on integration and evidence tasks.
