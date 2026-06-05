# Core Network

The current core-network code is copied under [`services/mock_5g_core/`](../services/mock_5g_core/) and tracked by the copy manifest. It is useful for lab runtime, API exploration, and future standards mapping. It is not, by itself, formal 3GPP conformance proof.

## Copied service inventory

| Function | Path | Current interpretation |
|---|---|---|
| AMF | [`services/mock_5g_core/core_network/amf.py`](../services/mock_5g_core/core_network/amf.py) | Mock access/mobility service with REST behavior and real-mode NGAP-like TCP hook. |
| SMF | [`services/mock_5g_core/core_network/smf.py`](../services/mock_5g_core/core_network/smf.py) | Mock session management service with REST behavior and real-mode PFCP-like UDP hook. |
| UPF | [`services/mock_5g_core/core_network/upf.py`](../services/mock_5g_core/core_network/upf.py) | Mock user-plane service with GTP-U/PFCP helpers and best-effort TUN behavior. |
| UDR | [`services/mock_5g_core/core_network/udr.py`](../services/mock_5g_core/core_network/udr.py) | Mock data repository service. |
| UDM | [`services/mock_5g_core/core_network/udm.py`](../services/mock_5g_core/core_network/udm.py) | Mock data management service. |
| AUSF | [`services/mock_5g_core/core_network/ausf.py`](../services/mock_5g_core/core_network/ausf.py) | Mock authentication service. |
| NRF | [`services/mock_5g_core/core_network/nrf.py`](../services/mock_5g_core/core_network/nrf.py) | Mock network repository/service discovery service. |
| NSSF | [`services/mock_5g_core/core_network/nssf.py`](../services/mock_5g_core/core_network/nssf.py) | Mock slicing selection function. |
| Transport helpers | [`services/mock_5g_core/core_network/transport.py`](../services/mock_5g_core/core_network/transport.py) | Standards-inspired GTP-U/PFCP/NGAP-like transport scaffolding. |
| Ports/config | [`services/mock_5g_core/config/ports.py`](../services/mock_5g_core/config/ports.py) | Local mock service port declarations. |

## Real-mode transport hooks

The copied mock core contains a `PROTOCOL_MODE=real` path in several services. Current
safe wording:

> The copied mock 5G core includes real-mode socket hooks for standards-inspired GTP-U,
> PFCP, and NGAP-like signaling, but the implementation is not a complete 3GPP protocol
> stack.

Important caveats:

- GTP-U helpers build/parse a minimal G-PDU header and can bind UDP, but complete
  end-to-end tunnel forwarding is not proven.
- PFCP helpers build/parse minimal headers/message types; complete IE-level session rule
  handling is not proven.
- NGAP-like messages are JSON over length-prefixed TCP, not ASN.1/PER NGAP over SCTP.
- Linux TUN can be attempted when permissions and `/dev/net/tun` exist; macOS behavior is
  simulated by the copied code.

## Runtime evidence

- Runtime plan: [Runtime Integration Plan](runtime_integration_plan.md)
- Runtime caveat: [`traceability/evidence_batch_010_runtime_integration_caveats.md`](../traceability/evidence_batch_010_runtime_integration_caveats.md)
- Runtime report: [`traceability/evidence_batch_010_runtime_integration_report.json`](../traceability/evidence_batch_010_runtime_integration_report.json)
- Test report: [`build_logs/stage15_test_report.json`](../build_logs/stage15_test_report.json)

Runtime evidence can support local readiness/demo claims. It does not establish formal
3GPP conformance.
