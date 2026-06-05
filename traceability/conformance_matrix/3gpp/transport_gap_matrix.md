# 3GPP transport gap matrix

Issue coverage: #6, with dependencies on #4 and #5.

This matrix records current mock/readiness behavior and the evidence gap before any
stronger 3GPP protocol claim. It is not an implementation plan for a production protocol
stack and it does not assert formal conformance.

## Matrix

| Interface / protocol | Spec reference | Current repo behavior | Protocol/evidence required before stronger claim | Current claim level | Next executable evidence step | Safe wording |
|---|---|---|---|---|---|---|
| GTP-U / N3 user plane | TS 29.281 (local spec missing; see `release_row_candidates.yaml`) | `services/mock_5g_core/core_network/transport.py` builds/parses an 8-byte G-PDU-style header and sends UDP on port `2152`. | Authorized TS metadata; packet captures; decoder validation; negative tests for malformed flags/length/version; evidence for extension headers/sequence/N-PDU behavior if claimed. | `mapped_candidate` | Add PCAP/decoder tests for current helper behavior and keep failures explicit for unsupported features. | Minimal GTP-U G-PDU header readiness over UDP/2152; full TS 29.281 behavior is not established. |
| PFCP / N4 | TS 29.244 (local spec missing; see `release_row_candidates.yaml`) | `transport.py` builds/parses a subset of PFCP headers, message types, sequence numbers, and heartbeat response behavior over UDP `8805`. | Authorized TS metadata; IE-level parser/validator evidence; PDR/FAR/QER/session tests; negative tests; PCAP/decoder output. | `mapped_candidate` | Add gap tests proving unsupported IE/session semantics remain blocked from stronger claim levels. | Minimal PFCP header/message-type readiness over UDP/8805; IE/PDR/FAR/QER behavior is not established. |
| NG-C transport / N2 | TS 38.412 (local spec missing; see `release_row_candidates.yaml`) | `transport.py` provides length-prefixed TCP framing on port `38412`; comments call this an SCTP/TCP fallback. | Authorized TS metadata; SCTP transport evidence; PPID handling evidence; association lifecycle evidence; negative tests for framing/transport failures. | `mapped_candidate` | Add tests that distinguish TCP fallback readiness from SCTP transport evidence. | NG-C local mock signaling uses TCP fallback; SCTP-based TS 38.412 behavior is not established. |
| NGAP payloads | TS 38.413 (local spec missing; see `release_row_candidates.yaml`) | `services/mock_5g_core/core_network/amf.py` handles NGAP-like procedure dictionaries and JSON-modeled messages; `transport.py` frames bytes over TCP. | Authorized TS metadata; ASN.1/PER encoder/decoder evidence; procedure vectors; interop/negative tests; retained artifacts. | `mapped_candidate` | Add JSON-vs-ASN.1/PER boundary tests and retained evidence requirements before any stronger row. | NGAP-like JSON procedure readiness only; ASN.1/PER NGAP over SCTP is not established. |

## Cross-cutting blockers

- The leader-local Rel-19 inventory used by this lane contains `23_series` and `24_series`
  target files for TS 23.501, TS 23.502, TS 23.503, and TS 24.501, but the 29/33/38
  target specs for PFCP, GTP-U, NG-C transport, NGAP, SBI, and security were not present
  in the checked local tree.
- Architecture/procedure/NAS references from TS 23.501/23.502/23.503/24.501 do not
  satisfy protocol evidence requirements for PFCP, GTP-U, NGAP, SCTP, SBI contracts, or
  security behavior.
- Raw standards files must stay out of git unless storage/licensing policy explicitly
  authorizes a different path.

## Suggested gap-oriented tests

These are safe test intentions for a future conformance-candidate harness:

1. GTP-U: assert the helper accepts only version 1 packets and rejects too-short packets.
2. PFCP: assert the helper parses the supported header shape while leaving IE/session
   semantics as an explicit evidence gap.
3. NGAP/NG-C: assert the local path is length-prefixed TCP/JSON-modeled readiness, not
   ASN.1/PER over SCTP evidence.
4. Artifact policy: require any promoted row to point to retained PCAP, decoder, vector,
   schema, or interop evidence with tool/version metadata.
