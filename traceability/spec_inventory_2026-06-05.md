# Local standards spec inventory (derived)

Generated on 2026-06-05 from local, untracked standards folders in the leader working tree. This artifact records filenames, counts, and candidate coverage only; it does not copy raw standards text and is not formal conformance evidence.

## Source folders

| Source | Read-only status | Derived count | Raw artifact policy |
|---|---:|---:|---|
| `specs/3gpp/Rel-19` | local untracked reference | 1355 files | Do not commit raw `.doc`, `.docx`, generated annex/data files, or other standards bundle contents. |
| `specs/oran/Latest_Versions` | local untracked reference | 335 files | Do not commit raw PDFs/DOCX/ZIPs or `Codex.dmg`; use derived mapping artifacts only. |

## 3GPP Rel-19 local filename inventory

| Series prefix | File count | Candidate interpretation |
|---:|---:|---|
| `21` | 8 | 21-series reference/support specs present |
| `22` | 132 | 22-series service requirements present |
| `23` | 168 | 23-series system architecture/procedure specs present |
| `24` | 145 | 24-series UE/NAS protocol specs present |
| `25` | 103 | 25-series UTRAN/legacy support specs present |
| `26` | 202 | 26-series codec/media specs present |
| `29` | 0 | missing locally; do not make PFCP/GTP-U/security/NGAP/RAN protocol claims without external evidence and tests |
| `33` | 0 | missing locally; do not make PFCP/GTP-U/security/NGAP/RAN protocol claims without external evidence and tests |
| `38` | 0 | missing locally; do not make PFCP/GTP-U/security/NGAP/RAN protocol claims without external evidence and tests |

### Target 3GPP spec shortlist

| Candidate spec | Local filename evidence | Readiness status | Notes |
|---|---|---|---|
| TS 23.501 | `23_series/23501-j60.docx` | local reference present; needs clause/test mapping | System architecture for the 5G System (5GS) |
| TS 23.502 | `23_series/23502-j60.docx` | local reference present; needs clause/test mapping | Procedures for the 5G System (5GS) |
| TS 23.503 | `23_series/23503-j60.docx` | local reference present; needs clause/test mapping | Policy and charging control framework |
| TS 24.501 | `24_series/24501-j40.docx` | local reference present; needs clause/test mapping | NAS protocol for 5GS |
| TS 29.244 | not found in local Rel-19 folder | gap: local raw reference missing | PFCP / N4 control plane |
| TS 29.281 | not found in local Rel-19 folder | gap: local raw reference missing | GTP-U / N3 user plane |
| TS 33.501 | not found in local Rel-19 folder | gap: local raw reference missing | Security architecture and procedures for 5GS |
| TS 38.412 | not found in local Rel-19 folder | gap: local raw reference missing | NG signalling transport |
| TS 38.413 | not found in local Rel-19 folder | gap: local raw reference missing | NGAP |

## O-RAN local bundle hygiene snapshot

| Extension | File count | Commit policy |
|---|---:|---|
| `.dmg` | 1 | exclude raw bundle asset; create derived matrices instead |
| `.docx` | 61 | exclude raw bundle asset; create derived matrices instead |
| `.json` | 2 | review before adding; prefer generated summaries only |
| `.md` | 1 | review before adding; prefer generated summaries only |
| `.mmd` | 1 | review before adding; prefer generated summaries only |
| `.pdf` | 91 | exclude raw bundle asset; create derived matrices instead |
| `.txt` | 166 | review before adding; prefer generated summaries only |
| `.xlsx` | 1 | review before adding; prefer generated summaries only |
| `.zip` | 11 | exclude raw bundle asset; create derived matrices instead |

## Issue coverage

- Issue #2: derived inventory and ignore-policy basis for raw standards bundles.
- Issues #4, #5, #6: identifies present 3GPP Rel-19 23/24-series references and missing 29/33/38-series references before implementation claims.

## Safe-use rule

Use this inventory for candidate mapping and readiness planning only. A filename match is not clause coverage, protocol conformance, or executable proof.
