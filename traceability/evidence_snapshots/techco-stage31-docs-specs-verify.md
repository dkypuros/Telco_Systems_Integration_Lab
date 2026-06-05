# Stage 31: Docs and Specs Verification Pass

**Date**: 2026-05-18
**Scope**: Closing documentation pass. Created `docs/specs_guide.md`, updated
`docs/README.md` to index all 18 docs, added a Documentation section to the
top-level `README.md`, and verified consistency across all docs in the `docs/`
tree.

---

## Deliverables

### specs_guide.md created

`docs/specs_guide.md` is a new 8-section standards library guide covering:

1. Overview table of 5 standards bodies (TM Forum, 3GPP, O-RAN/ETSI ISG, ETSI, AI-RAN)
2. TM Forum specs: conformance table per API, CTK achieved results
3. 3GPP specs: 14 5G Core NFs (spec mappings sourced from actual `.py.spec.txt` sidecar
   files), IMS NFs, and 4G EPC NFs
4. O-RAN specs: interface-to-ETSI-TS mapping with implementation status, all `.tex` files
5. IMS spec summary cross-referencing TS 24.229, TS 29.228, TS 29.229, TS 33.203
6. ETSI specs (NFV, MEC, ZSM): referenced not implemented
7. AI-RAN Alliance: all `.tex` files listed, ai_observer alignment noted
8. CTK runner instructions: prerequisites, npm install, bash runner, result files,
   target URLs, achieved conformance table

Spec corrections applied (prompt suggestions vs actual sidecar data):

| NF | Prompt said (primary) | Actual sidecar (primary) |
|---|---|---|
| SEPP | TS 33.501 | TS 29.573 (N32-c/N32-f) |
| BSF | TS 29.513 | TS 29.521 (Nbsf_Management) |
| AMF | TS 23.501 | TS 29.518 + TS 38.413 + TS 23.502 + TS 24.501 |

---

### docs/README.md updated

Previously the index listed 9 rows, referenced two files that did not exist
(`api_reference.md`, `roadmap.md`), and described the components directory with a
single vague row.

After this pass: 18 rows, one per actual file in the `docs/` tree. All entries
verified to correspond to files that exist on disk.

| Previously missing from index | Now added |
|---|---|
| specs_guide.md | Added with status: Complete |
| components/5g_core.md | Added with status: Complete |
| components/ims.md | Added with status: Complete |
| components/epc.md | Added with status: Complete |
| components/ran.md | Added with status: Complete |
| components/ai_observer.md | Added with status: Complete |
| components/oran_o2ims.md | Added with status: Complete |
| api_reference.md | Added with status: Complete |

Previously listed but not existing on disk:

| Removed from index | Reason |
|---|---|
| roadmap.md | File does not exist |

Quick Orientation section updated: stale "(to be written)" note removed from
`development.md` reference; `specs_guide.md` added as a navigation entry for
standards and conformance questions.

---

### Top-level README.md updated

A "Documentation" section was added between "Where Things Live" and "Ports Quick
Reference". It links to `docs/README.md` as the entry point and provides a 7-row
table of key docs with one-line descriptions.

---

## Consistency Issues Found and Fixed

| Issue | Fix applied |
|---|---|
| docs/README.md listed api_reference.md and roadmap.md which do not exist | Removed roadmap.md entry; api_reference.md verified to exist and re-added correctly |
| docs/README.md "To be populated" status on operations.md, development.md, testing.md even though files exist with real content | Status updated to Complete for all three |
| docs/README.md Quick Orientation section said development.md "(to be written)" | Fixed to reflect that development.md is complete |
| components/ listed as a single row with no individual file entries | Replaced with 8 individual component doc rows |

---

## Em-Dash Scan

```
grep -rn $'\u2014' docs/    -> 0 matches
grep -rn $'\u2013' docs/    -> 0 matches
```

All docs are clean. No em dashes, no en dashes found.

---

## Final docs/ Tree (18 files)

```
docs/
  README.md                   Index of all docs (this stage updated)
  architecture.md             Layered architecture deep dive
  build_history.md            25-stage chronological build summary
  development.md              Developer guide (adapter pattern, rules.yaml)
  operations.md               Bring-up, tear-down, troubleshooting runbook
  reference.md                All ports, env vars, file paths in one place
  specs_guide.md              Standards library guide (created this stage)
  testing.md                  Test suite map and CTK runner instructions
  api_reference.md            OpenAPI endpoint reference for all FastAPI services
  components/
    5g_core.md                BF3 5G Core NFs (14 NFs, flows, test suite)
    ai_observer.md            AI Observer: KPI scraping, anomaly detection
    catalog_api.md            TMF620 Catalog API (68/68 tests, 1421/1421 CTK)
    epc.md                    4G EPC subsystem (MME, SGW, PGW, HSS)
    ims.md                    IMS subsystem (P/I/S-CSCF, HSS, MRF, VoNR)
    oran_o2ims.md             O-RAN O2IMS Go binary (O-Cloud inventory)
    order_engine.md           TMF622/641 Order Engine (43/43 tests)
    ran.md                    RAN layer (O-DU, O-RU, xApp, RIC, A1/E2/O1)
    storefront.md             Next.js storefront (product browse, order submit)
```

---

## Conformance Summary (carried forward from stage 18 and stage 13)

| API | CTK assertions | Pass | Conformance |
|---|---|---|---|
| TMF620 Product Catalog Management v4 | 1421 | 1421 | 100% |
| TMF622 Product Ordering Management v4 | 63 | 63 | 100% |
| TMF641 Service Ordering Management v4 | (not CTK-tested; endpoints implemented) | n/a | partial |

---

## Previous Stage Reference

- Stage 29: `build_logs/stage29_docs_guides.md` (development.md, testing.md, operations.md)
- Stage 28: `build_logs/stage28_docs_ossbss_ai.md`
- Stage 26: `build_logs/stage26_docs_top_level.md`
- Stage 18: `build_logs/stage18_tmf620_lift.md` (TMF620 100% CTK)
- Stage 13: `build_logs/stage13_tmf_ctk_conformance.md` (TMF622 100% CTK)
