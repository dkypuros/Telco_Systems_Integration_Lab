# GPU-Ready Telemetry Ingestion Pipeline

Status: Issue #37 repo-local perception-layer slice, corrected against the local
O-RAN/TMF spec library on 2026-06-11.

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
2. annotated with O1 NRM-inspired managed-object identity (`ManagedElement`,
   `GNBDUFunction`, `NRCellDU`),
3. normalized into a local queryable data-layer mock,
4. exposed through R1 DME-style DME type registration/discovery plus data
   request/subscription containers,
5. summarized through bounded windows with explicit backpressure, and
6. emitted as a compact `agent.telemetry-context.v1` payload.

## Architecture

```text
Mock O1/VES-inspired FM/PM events
  -> O1 NRM-inspired managed-object references
  -> adapters.telemetry_pipeline.generator
  -> InMemoryTelemetryStore
       (local queryable data-layer mock; not EIAP SDL internals)
  -> R1DmeFacade / R1DmeQueryFacade
       (DME type registration/discovery + data request/subscription boundary)
  -> summarize_for_agent()
       (optional cuDF detection, standard-library CPU summarization)
  -> compact Agent Harness perception input
```

The store is intentionally an in-memory deterministic mock. It mirrors the behavior a
lab needs from a shared telemetry search/persistence layer without claiming that it
replicates Ericsson EIAP SDL, production Kafka, or Elasticsearch internals.

## Local spec grounding

The following local files exist under `specs/oran/Latest_Versions/` and are the
preferred evidence anchors for this slice. Use exact file/version references in
interview notes and issues before relying on rot-prone web URLs.

| Concern | Local spec anchor | How this slice uses it |
|---|---|---|
| O1 management interface | `O-RAN.WG10.TS.O1-Interface.0-R005-v18.00.pdf` | Southbound FM/PM telemetry boundary into SMO-style ingestion. |
| O1 PM | `O-RAN.WG10.TS.O1PMeas-R005-v05.00.pdf` | KPI names such as latency, throughput, and SgNB addition rates stay PM-scoped. |
| O1 NRM/data model fidelity | `O-RAN.WG10.TS.O1NRM.0-R004-v04.00.pdf`; `O-RAN.WG10.TS.Information Model and Data Models.0-R005-v13.00.pdf` | Fixtures now include NRM-inspired `ManagedElement`, `GNBDUFunction`, and `NRCellDU` references instead of anonymous cell strings. |
| SMO placement | `O-RAN.WG1.TS.SMO-ARCH-R005-v02.00.docx` | Grounds the SMO role as the southbound consumer and R1 termination context. |
| Non-RT RIC placement | `O-RAN.WG2.TS.Non-RT-RIC-ARCH-R004-v07.00.docx` | Grounds rApp/Non-RT RIC placement for the perception consumer. |
| R1 DME application protocols | `O-RAN.WG2.TS.R1AP-R005-v10.00.pdf` | Uses Data registration, Data discovery, and Data access API language. R1AP section 7.3 states data jobs can represent one-time data requests or continuous subscriptions, so code treats “job” as the resource container and “request/subscription” as the agent-facing intent. |
| R1 transport/security/types | `O-RAN.WG2.TS.R1TP-R004-v04.03.docx`; `O-RAN.WG2.TS.R1TS-R005-v05.00.pdf`; `O-RAN.WG2.TS.R1TD-R005-v04.02.pdf` | Future hardening anchors for transport, security, and type details; not implemented as conformance. |
| AI/ML rApp workflow | `O-RAN.WG2.AIML-v01.03.pdf` | Grounds the data collection/preparation/training/inference framing for AI/ML consumers. |
| AI/ML security | `O-RAN.WG11.TR.AIML-Security-Analysis.0-R005-v05.00.docx` | Grounds the telemetry poisoning / model-context trust risk. |
| Topology and inventory | `O-RAN.WG10.TS.TE&IV-DM.0-R005-v04.00.pdf`; `O-RAN.WG10.TS.TE&IV-API.0-R005-v04.00.pdf`; `O-RAN.WG10.TS.TE&IV-CIMI.0-R005-v06.00.pdf` | Future source of topology graph context beyond cell KPI summaries; current payload exposes a minimal topology context map. |
| Zero trust throughline | `O-RAN.WG11.TR.ZTA-R005-v05.00.docx` | Connects Issue #36 action-boundary safety to Issue #37 data-trust safety. |

TM Forum anchors present in the repo:

| Concern | Local TMF anchor | How to use it |
|---|---|---|
| AI component management | `specs/tmforum/CTK-TMF915-AI/` | TMF-side counterpart for agentic AI lifecycle/management claims. |
| Alarm bridge | `specs/tmforum/CTK-TMF642-Alarm/` | TMF-side equivalent to O1 FM alarm exposure. |
| Service-quality bridge | `specs/tmforum/CTK-TMF657-ServiceQualityManagement-R18-0/` | TMF-side equivalent for service-quality/KQI/KPI exposure. |

## Source boundaries and nitpicks resolved

- The implemented generator is scoped to FM/PM VES-like events. NetFlow/IPFIX is not
  modeled as O1 telemetry here. If flow records are introduced later, document them as
  non-O1 enrichment sources that are joined after the SMO-style perception boundary.
- The original local issue draft cited exact O-RAN versions that exist in the local
  spec library. The GitHub issue body also included web URLs; prefer local
  spec+version anchors for durable technical review.
- Firehose behavior is explicit: `SummarizationPolicy` uses tumbling windows and a
  `max_events_per_window` cap. The current overflow strategy is `keep_latest`, and
  summaries report dropped counts plus a `backpressure_applied` anomaly flag.

## Implemented modules

| Path | Purpose |
|---|---|
| `adapters/telemetry_pipeline/generator.py` | Builds deterministic VES-like FM/PM fixtures and adds O1 NRM-inspired topology references. |
| `adapters/telemetry_pipeline/store.py` | Provides `InMemoryTelemetryStore` query behavior and deterministic index naming. |
| `adapters/telemetry_pipeline/r1_dme.py` | Exposes DME type registration/discovery and data-request APIs through `R1DmeFacade`; keeps data-job aliases only for R1AP compatibility. |
| `adapters/telemetry_pipeline/summarizer.py` | Produces compact agent context with safe backend detection, CPU fallback, windowing, backpressure, and topology context. |
| `adapters/telemetry_pipeline/models.py` | Defines typed records, queries, DME request containers, summaries, and policies. |
| `adapters/agent_harness/perception/r1_dme.py` | Provides an Agent Harness-facing R1 DME query facade with data request terminology and data-job compatibility aliases. |
| `tests/unit/test_telemetry_pipeline.py` | Proves deterministic generation, query, DME request, windowing, backpressure, topology context, and claim boundaries. |
| `tests/unit/test_agent_harness_perception_r1_dme.py` | Proves Agent Harness-facing DME registration/discovery/request/query behavior. |

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
store.ingest(normalize_events(generate_sample_events(cell_id="NRCellDU=cell-001")))

facade = R1DmeFacade(store)
request = facade.create_data_request(query=TelemetryQuery(cell_id="NRCellDU=cell-001"))
records = facade.query_data_request(request.request_id).records
context = summarize_for_agent(records).to_dict()
```

The returned context contains window summaries, event-retention counts, anomaly flags,
backend information, NRM-inspired topology context, and claim-boundary text. It does
not contain raw credentials, private paths, direct network-element commands, or direct
database handles.

## Optional GPU story

`detect_dataframe_backend()` safely detects whether `cudf` is import-discoverable. The
current summarizer remains standard-library CPU-safe so tests pass on laptops and CI.
This keeps the architecture RAPIDS/Morpheus-ready without adding mandatory heavyweight
dependencies or requiring CUDA for the public lab.

Future GPU work can swap the internal aggregation implementation behind the same typed
`AgentContextPayload` contract once a CUDA environment and performance tests are part
of the lab profile.

## Claim boundary

This slice supports a careful claim:

> The lab models a safe O1/VES-inspired telemetry perception path with O1
> NRM-inspired identifiers and R1 DME-style exposure that can feed compact context into
> an agent harness, with optional GPU-backend detection and CPU-safe deterministic
> tests.

It does **not** prove:

- formal O-RAN O1, R1, TE&IV, or VES conformance,
- real Ericsson EIAP internal behavior,
- production data-layer scale,
- NVIDIA Morpheus/RAPIDS acceleration in this checkout, or
- end-to-end integration with live network elements.
