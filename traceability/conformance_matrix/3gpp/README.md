# 3GPP conformance-candidate matrix

This directory contains derived 3GPP traceability artifacts for issues #4, #5, and #6.
The artifacts are intentionally **not** raw standards files and do not assert formal
3GPP conformance.

## Claim boundary

These files may be used for release-register support, gap tracking, and readiness
planning only. A candidate row is not evidence that the lab satisfies a 3GPP TS.
Formal claims remain blocked until a row links all of the following:

- authorized spec/release metadata,
- implementation path,
- executable evidence path,
- retained artifact or test output,
- claim level,
- known gap, and
- next evidence step.

Use the project policy in [`traceability/claim_hygiene_policy.md`](../../claim_hygiene_policy.md)
and the boundary statement in [`docs/conformance-boundary.md`](../../../docs/conformance-boundary.md)
when promoting or citing these rows.

## Files

| File | Issues | Purpose |
|---|---:|---|
| [`release_row_candidates.yaml`](release_row_candidates.yaml) | #4, #5 | Candidate release-register rows for the local 3GPP Rel-19 23/24-series specs and a missing-spec checklist for 29/33/38/SBI/security work. |
| [`transport_gap_matrix.md`](transport_gap_matrix.md) | #6 | Gap matrix for the copied GTP-U, PFCP, and NGAP/NG-C helper behavior versus the evidence required before stronger protocol claims. |

## Raw standards storage rule

Do not add raw 3GPP PDFs/DOCX/ZIPs or private standards bundles to git from this
lane. Record metadata and local/private path references only when access and storage
policy allow it.
