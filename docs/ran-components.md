# RAN Components

RAN-side mock code is copied under [`adapters/mock_ran/`](../adapters/mock_ran/) and tracked by the copy manifest. These components provide lab adapters for gNB/CU/DU behavior, fronthaul/slicing support, and RIC-facing examples.

## Copied RAN inventory

| Component | Path | Current interpretation |
|---|---|---|
| gNB | [`adapters/mock_ran/ran/gnb.py`](../adapters/mock_ran/ran/gnb.py) | Mock gNodeB with REST paths and real-mode NGAP-like TCP/GTP-U helper startup. |
| CU | [`adapters/mock_ran/ran/cu.py`](../adapters/mock_ran/ran/cu.py) | Mock centralized-unit component. |
| DU | [`adapters/mock_ran/ran/du.py`](../adapters/mock_ran/ran/du.py) | Mock distributed-unit component. |
| Fronthaul C/U/S plane | [`adapters/mock_ran/ran/fronthaul/cus_plane.py`](../adapters/mock_ran/ran/fronthaul/cus_plane.py) | Fronthaul-oriented adapter evidence. |
| Slicing | [`adapters/mock_ran/ran/slicing/oran_slicing.py`](../adapters/mock_ran/ran/slicing/oran_slicing.py) | Slicing-oriented RAN/O-RAN adapter evidence. |

## Standards mapping

The RAN documentation and copied source refer to NGAP, CU/DU, F1, fronthaul, and radio
stack concepts. Treat those as standards mapping candidates until tied to release rows and
executable evidence.

Useful supporting references:

- [`traceability/requirements/bf3-ran-components.md`](../traceability/requirements/bf3-ran-components.md)
- [`traceability/requirements/bf3-3gpp-compliance.md`](../traceability/requirements/bf3-3gpp-compliance.md)
- [`traceability/requirements/networking-spec-inventory.txt`](../traceability/requirements/networking-spec-inventory.txt)

## Current caveats

- gNB real-mode signaling is NGAP-like JSON over TCP, not formal NGAP over SCTP.
- CU/DU and protocol-stack references need clause-level release mapping before stronger
  claims.
- Fronthaul and slicing evidence should be linked to O-RAN/3GPP rows before promotion.
- Runtime success is local lab evidence, not formal RAN conformance evidence.
