# GPU-Ready Telemetry Ingestion Pipeline

Status: Issue #37 repo-local perception-layer slice.

This document describes the lab implementation for turning O1/VES-inspired telemetry
into compact agent context. It is a deterministic mock/readiness slice for interviews,
architecture demos, and tests. It is **not** formal O-RAN, Ericsson EIAP, NVIDIA
Morpheus/RAPIDS, TM Forum, or 3GPP conformance evidence.

## Why this exists

Issue #36 added the safe action boundary for AI tools: the Agent Harness can produce
R1/TMF-style intents without letting the model touch direct-wire protocols such as SSH,
NETCONF, gNMI, RESTCONF, or SNMP.

Issue #37 adds the complementary perception boundary. The agent still should not read
raw firehose telemetry or query persistence internals directly. Instead, telemetry is:

1. generated as public-safe O1/VES-inspired FM/PM events,
2. normalized into a local queryable data-layer mock,
3. exposed through an R1 DME-style data type and data job facade,
4. summarized through bounded windows with explicit backpressure, and
5. emitted as a compact `agent.telemetry-context.v1` payload.

## Architecture

```text
Mock O1/VES-inspired FM/PM events
  -> adapters.telemetry_pipeline.generator
  -> InMemoryTelemetryStore
       (local queryable data-layer mock; not EIAP SDL internals)
  -> R1DmeFacade
       (data type discovery + data job query boundary)
  -> summarize_for_agent()
       (optional cuDF detection, standard-library CPU summarization)
  -> compact Agent Harness perception input
```

The store is intentionally an in-memory deterministic mock. It mirrors the behavior a
lab needs from a shared telemetry search/persistence layer without claiming that it
replicates Ericsson EIAP SDL, production Kafka, or Elasticsearch internals.

## Source boundaries and nitpicks resolved

- The implemented generator is scoped to FM/PM VES-like events. NetFlow/IPFIX is not
  modeled as O1 telemetry here. If flow records are introduced later, document them as
  non-O1 enrichment sources that are joined after the SMO-style perception boundary.
- The O1 and O-RAN reference URLs used in Issue #37 were spot-checked on 2026-06-10:
  the ETSI TS 104 043 PDF returned HTTP 200 and the O-RAN release-note URL returned
  HTTP 200.
- Firehose behavior is explicit: `SummarizationPolicy` uses tumbling windows and a
  `max_events_per_window` cap. The current overflow strategy is `keep_latest`, and
  summaries report dropped counts plus a `backpressure_applied` anomaly flag.

## Implemented modules

| Path | Purpose |
|---|---|
| `adapters/telemetry_pipeline/generator.py` | Builds deterministic VES-like FM/PM fixtures and normalizes them into records. |
| `adapters/telemetry_pipeline/store.py` | Provides `InMemoryTelemetryStore` query behavior and deterministic index naming. |
| `adapters/telemetry_pipeline/r1_dme.py` | Exposes data type discovery and data jobs through `R1DmeFacade`. |
| `adapters/telemetry_pipeline/summarizer.py` | Produces compact agent context with safe backend detection and CPU fallback. |
| `adapters/telemetry_pipeline/models.py` | Defines typed records, queries, DME jobs, summaries, and policies. |
| `tests/unit/test_telemetry_pipeline.py` | Proves deterministic generation, query, DME, windowing, backpressure, and claim boundaries. |

## Example usage

```python
from adapters.telemetry_pipeline import (
    InMemoryTelemetryStore,
    R1DmeFacade,
    TelemetryQuery,
    generate_sample_events,
    normalize_events,
    summarize_for_agent,
)

store = InMemoryTelemetryStore()
store.ingest(normalize_events(generate_sample_events(cell_id="cell-001")))

facade = R1DmeFacade(store)
job = facade.create_data_job(query=TelemetryQuery(cell_id="cell-001"))
records = facade.query_data_job(job.job_id).records
context = summarize_for_agent(records).to_dict()
```

The returned context contains window summaries, event-retention counts, anomaly flags,
backend information, and claim-boundary text. It does not contain raw credentials,
private paths, direct network-element commands, or direct database handles.

## Optional GPU story

`detect_dataframe_backend()` safely detects whether `cudf` is import-discoverable. The
current summarizer remains standard-library CPU-safe so tests pass on laptops and CI.
This keeps the architecture RAPIDS/Morpheus-ready without adding mandatory heavyweight
dependencies or requiring CUDA for the public lab.

Future GPU work can swap the internal aggregation implementation behind the same typed
`AgentContextPayload` contract once a CUDA environment and performance tests are part
of the lab profile.

## Standards and platform references

Primary references used for the Issue #37 assessment and docs:

- Ericsson EIAP overview: <https://www.ericsson.com/en/ran/intelligent-ran-automation/intelligent-automation-platform>
- Ericsson SMO/RAN automation architecture: <https://www.ericsson.com/en/reports-and-papers/white-papers/smo-enabling-intelligent-ran-operations>
- ETSI O1 Interface Specification: <https://www.etsi.org/deliver/etsi_ts/104000_104099/104043/11.00.00_60/ts_104043v110000p.pdf>
- O-RAN R1/DME release-note evidence: <https://www.o-ran.org/blog/60-new-or-updated-o-ran-technical-documents-released-since-march-2025>
- NVIDIA Morpheus: <https://developer.nvidia.com/morpheus-cybersecurity>
- RAPIDS `cudf.pandas`: <https://docs.rapids.ai/api/cudf/stable/cudf_pandas/>

## Claim boundary

This slice supports a careful claim:

> The lab models a safe O1/VES-inspired telemetry perception path and R1 DME-style
> exposure boundary that can feed compact context into an agent harness, with optional
> GPU-backend detection and CPU-safe deterministic tests.

It does **not** prove:

- formal O-RAN O1, R1, or VES conformance,
- real Ericsson EIAP internal behavior,
- production data-layer scale,
- NVIDIA Morpheus/RAPIDS acceleration in this checkout, or
- end-to-end integration with live network elements.
