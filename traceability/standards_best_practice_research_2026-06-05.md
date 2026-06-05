# Best-Practice Research: Standards Release Tracking

Checked at: 2026-06-05

## Direct recommendation

Track three separate things for every standards-linked source module:

1. **Official latest open/active release** — useful for future roadmap awareness.
2. **Official latest frozen/stable release** — safest target for near-term conformance planning.
3. **Local tested-against baseline** — what the current source code/tests actually prove today.

Never treat a folder named `3gpp`, `tmforum`, or `oran` as proof of conformance. A claim needs a standard version, implementation path, test evidence path, and gap-to-latest status.

## Evidence used

### 3GPP

Official/upstream:
- https://portal.3gpp.org/Releases?SubTB=385&tbid=375 — official release portal used for current release status.
- https://www.3gpp.org/specifications-technologies/releases/release-20 — public Release 20 context page.

Current snapshot recorded in this lab:
- Rel-21 Open
- Rel-20 Open
- Rel-19 Frozen

Planning implication:
- Use `latest_open_or_active` for roadmap awareness.
- Use `latest_frozen_or_stable` for stable conformance planning unless a specific spec requires another baseline.
- Current local source evidence is mixed and must not be upgraded by documentation wording alone.

### TM Forum

Official/upstream:
- TMF620 Product Catalog Management API v5.0: https://www.tmforum.org/open-digital-architecture/open-apis/product-catalog-management-api-TMF620/v5.0
- TMF622 Product Ordering Management API v5.0: https://www.tmforum.org/oda/open-apis/directory/TMF622
- TMF641 Service Ordering Management API v5.0: https://www.tmforum.org/open-digital-architecture/open-apis/service-ordering-management-api-TMF641/v5.0
- TMF638 Service Inventory Management API page: https://www.tmforum.org/oda/open-apis/directory/service-inventory-management-api-TMF638/v5.0.0E
- TMF921 Intent Management API v5.0: https://www.tmforum.org/oda/open-apis/directory/intent-management-api-TMF921/v5.0

Repo-local evidence already recorded:
- Tech-Co reports TMF620 CTK 100% using local v4 baseline evidence.
- Tech-Co reports TMF622 CTK 100% using local v4 baseline evidence.
- TMF641 is partial in local Tech-Co docs.
- TMF638 is not implemented in local Tech-Co architecture docs.

Planning implication:
- Track API spec version separately from CTK/RI asset version.
- Preserve local v4 evidence but do not claim v5 conformance until v5 CTK/contract tests are run.

### O-RAN

Official/upstream:
- O-RAN specifications portal: https://www.o-ran.org/specifications
- O-RAN security update 2026: https://www.o-ran.org/blog/o-ran-alliance-security-update-2026

Planning implication:
- O-RAN has no single global release baseline for this lab.
- Track per working group, spec, interface, and artifact, for example A1, E2AP, E2SM, O1, O2, Open Fronthaul.
- Local HTTP-mock demos and closed-loop scripts are functional evidence, not formal O-RAN conformance.

## Repo-local context

The current lab already has:
- `traceability/standards_release_register.yaml`
- `traceability/source_inventory.csv`
- `procedures/standards_release_tracking.md`
- `traceability/evidence_snapshots/2026-06-05-standards-release-baseline.md`

## Boundaries / non-goals

- This research does not update source code.
- This research does not copy bulk source material.
- This research does not certify conformance.
- It establishes the tracking mechanism for future conformance work.

## Handoff

Next work should update source inventory rows with:
- `official_latest_open_or_active`
- `official_latest_frozen_or_stable`
- `local_tested_against`
- `local_test_evidence_path`
- `known_gap_to_latest`
- `next_step`

Authoritative release/conformance status lives in `traceability/standards_release_register.yaml`; this file is a derived view.
