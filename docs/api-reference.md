# API Reference

This lab currently has API evidence in two forms:

1. copied source files that expose mock service endpoints, and
2. copied/reference documentation under `traceability/requirements/` and evidence snapshots.

This page is a navigation layer. It does not assert formal API conformance.

## Mock 5G core and RAN APIs

| Area | Source paths | Notes |
|---|---|---|
| Core services | [`services/mock_5g_core/core_network/`](../services/mock_5g_core/core_network/) | FastAPI-style mock service files for AMF, SMF, UPF, UDR, UDM, AUSF, NRF, NSSF. |
| RAN services | [`adapters/mock_ran/ran/`](../adapters/mock_ran/ran/) | Mock gNB/CU/DU and RAN-side adapters. |
| O-RAN gateway | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../adapters/mock_oran/api_gateway/oran_gateway.py) | Mock O-RAN API gateway surface. |
| Runtime command surface | [`lab`](../lab), [`scripts/lab_cli.py`](../scripts/lab_cli.py) | Local operator CLI for service launch/status/chatter/scenarios/smoke/tests. |

## Reference API docs and evidence

| Reference | Path |
|---|---|
| legacy standalone 5G emulator API reference snapshot | [`traceability/requirements/legacy_5g_emulator-api-reference.md`](../traceability/requirements/legacy_5g_emulator-api-reference.md) |
| Tech-Co API reference snapshot | [`traceability/requirements/techco-api-reference.md`](../traceability/requirements/techco-api-reference.md) |
| TMF specs guide | [`traceability/requirements/tmf-specs-guide.md`](../traceability/requirements/tmf-specs-guide.md) |
| Runtime integration report | [`traceability/evidence_batch_010_runtime_integration_report.json`](../traceability/evidence_batch_010_runtime_integration_report.json) |
| Runtime smoke logs | [`build_logs/`](../build_logs/) |

## Endpoint documentation rule

When adding endpoint-level documentation, include:

- service/function name,
- local endpoint path and method,
- implementation file path,
- standards/API mapping if applicable,
- local tested-against evidence,
- known caveat or gap.

If a standards/API mapping is not tied to a release-register row, mark it as
`standards-mapped candidate`, not conformance evidence.
