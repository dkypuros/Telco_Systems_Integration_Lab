# O-RAN Components

O-RAN-related mock code and evidence are split across RIC modules, E2/E2SM support,
fronthaul/slicing artifacts, and an O-RAN gateway/spec-map pair.

## Copied O-RAN inventory

| Component | Path | Current interpretation |
|---|---|---|
| Near-RT RIC | [`adapters/mock_ran/ran/ric/near_rt_ric.py`](../adapters/mock_ran/ran/ric/near_rt_ric.py) | Mock near-real-time RIC behavior. |
| Non-RT RIC | [`adapters/mock_ran/ran/ric/non_rt_ric.py`](../adapters/mock_ran/ran/ric/non_rt_ric.py) | Mock non-real-time RIC behavior. |
| E2AP | [`adapters/mock_ran/ran/ric/e2ap.py`](../adapters/mock_ran/ran/ric/e2ap.py) | E2AP-oriented support evidence. |
| E2SM CCC | [`adapters/mock_ran/ran/ric/e2sm_ccc.py`](../adapters/mock_ran/ran/ric/e2sm_ccc.py) | E2 service model support evidence. |
| E2SM LLC | [`adapters/mock_ran/ran/ric/e2sm_llc.py`](../adapters/mock_ran/ran/ric/e2sm_llc.py) | E2 service model support evidence. |
| E2SM NI | [`adapters/mock_ran/ran/ric/e2sm_ni.py`](../adapters/mock_ran/ran/ric/e2sm_ni.py) | E2 service model support evidence. |
| Fronthaul C/U/S plane | [`adapters/mock_ran/ran/fronthaul/cus_plane.py`](../adapters/mock_ran/ran/fronthaul/cus_plane.py) | O-RAN fronthaul-oriented support evidence. |
| O-RAN slicing | [`adapters/mock_ran/ran/slicing/oran_slicing.py`](../adapters/mock_ran/ran/slicing/oran_slicing.py) | O-RAN slicing-oriented support evidence. |
| O-RAN gateway | [`adapters/mock_oran/api_gateway/oran_gateway.py`](../adapters/mock_oran/api_gateway/oran_gateway.py) | Mock O-RAN gateway/API surface. |
| O-RAN spec map | [`adapters/mock_oran/oran/o_ran_spec_map.py`](../adapters/mock_oran/oran/o_ran_spec_map.py) | Local mapping helper. |

## Tracking rule

O-RAN must be tracked by WG/spec/interface. Do not treat O-RAN as one global version. A
future O-RAN claim should identify the relevant interface or work group, the release or
asset baseline, the implementation path, and the executable evidence path.

## Supporting evidence

- [`traceability/requirements/legacy_5g_emulator-oran-compliance-matrix.md`](../traceability/requirements/legacy_5g_emulator-oran-compliance-matrix.md)
- [`traceability/requirements/oran-compliance.md`](../traceability/requirements/oran-compliance.md)
- [`traceability/requirements/oran-fronthaul.md`](../traceability/requirements/oran-fronthaul.md)
- [`traceability/requirements/ric-architecture.md`](../traceability/requirements/ric-architecture.md)
- [`traceability/evidence_snapshots/oran-spec-coverage.json`](../traceability/evidence_snapshots/oran-spec-coverage.json)

## Current caveats

- HTTP/gateway demos and RIC control-loop behavior are useful integration evidence, not
  formal O-RAN conformance evidence.
- E2/E2SM modules need official release/asset baselines and executable tests before
  promotion.
- O-RAN fronthaul and slicing evidence must be kept separate from 3GPP RAN evidence.
