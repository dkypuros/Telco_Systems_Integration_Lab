# Standards Mapping

This lab tracks 3GPP, TM Forum, and O-RAN as separate standards families. The
authoritative release state is [`traceability/standards_release_register.yaml`](../traceability/standards_release_register.yaml).

## Mapping by standards family

| Family | What it covers here | Primary repo areas | Evidence/register path |
|---|---|---|---|
| 3GPP | 5G core, RAN, NGAP/N2, PFCP/N4, GTP-U/N3, subscriber/session flows. | `services/mock_5g_core/`, `adapters/mock_ran/`, `procedures/3gpp/`, `tests/conformance/` | `traceability/standards_release_register.yaml`, `traceability/requirements/bf3-3gpp-compliance.md` |
| TM Forum | Open API evidence and CTK baselines for catalog/order/service APIs. | `adapters/tmforum/`, `services/catalog_api/`, `services/order_engine/`, `traceability/evidence_snapshots/` | `traceability/requirements/tmf-specs-guide.md`, CTK snapshots, release register rows. |
| O-RAN | RIC, E2/E2SM, O-RAN gateway, fronthaul/slicing evidence. | `adapters/mock_ran/ran/ric/`, `adapters/mock_oran/`, `adapters/oran/`, `procedures/oran/` | `traceability/requirements/oran-compliance.md`, `traceability/requirements/bf3-oran-compliance-matrix.md` |

## 3GPP transport references used by the copied mock services

| Interface/protocol | Standards mapping | Port/reference | Current lab status |
|---|---|---|---|
| GTP-U / N3 user plane | 3GPP TS 29.281 | UDP `2152` | Minimal G-PDU header handling and UDP socket helper exist in copied code. Full end-to-end forwarding is not proven. |
| PFCP / N4 | 3GPP TS 29.244 | UDP `8805` | Header/message-type helper and real-mode UDP startup hooks exist. Complete IE/PDR/FAR/QER processing is not proven. |
| NG-C transport | 3GPP TS 38.412 | SCTP over IP | Specs require SCTP; copied lab code uses a TCP fallback for local mock signaling. |
| NGAP | 3GPP TS 38.413 | default NG control-plane SCTP port `38412` | Copied lab code sends JSON-modeled NGAP messages over length-prefixed TCP, not ASN.1/PER NGAP over SCTP. |

## Release tracking rule

For every standards-related implementation or test, record all of the following before
claiming progress against a release:

- standards body and spec/API ID,
- latest open/active release,
- latest frozen/stable release,
- local tested-against baseline,
- implementation path,
- evidence path,
- conformance level,
- known gap to latest,
- next step.

The detailed step mechanism is in [Standards Release Tracking Procedure](../procedures/standards_release_tracking.md).

## Claim rule

A folder name, protocol port, mock endpoint, or runtime smoke test is not enough to make
a formal conformance claim. See [Conformance Boundary](conformance-boundary.md) and the
[Claim Hygiene Policy](../traceability/claim_hygiene_policy.md).
