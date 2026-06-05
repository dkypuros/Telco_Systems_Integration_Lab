# Next Copy-Only Batch Recommendation: Evidence Batch 007

Date: 2026-06-05  
Target lab: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_Telco_Systems_Integration_Lab`  
Source umbrella: `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator`  
Status: recommendation only; no batch-007 files copied.

## Selection rule

Batch 007 should continue with small, safe documentation/reference artifacts that have no local Markdown link fan-out. Avoid bulk docs directories and files that require large recursive link-fix closures.

## Ready source-to-destination candidates

All source files below were checked for existence on 2026-06-05, are not already copied in `traceability/copy_manifest.csv`, and have no local relative Markdown links in pre-scan.

| Priority | Source | Recommended destination | Standards domain | Reason | Risk / label |
|---:|---|---|---|---|---|
| 1 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/docs/components/ai_observer.md` | `traceability/requirements/techco-ai-observer-component.md` | O-RAN/AI operations adjacency | Component doc for AI observer/closed-loop context. | Documentation evidence only. |
| 2 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/docs/development.md` | `traceability/requirements/techco-development.md` | TM Forum; 3GPP; O-RAN development context | Development workflow reference for traceability/testing context. | Reference doc only. |
| 3 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/docs/roadmap.md` | `traceability/requirements/techco-roadmap.md` | TM Forum; 3GPP; O-RAN planning context | Roadmap context for future gap planning. | Planning doc; not implementation evidence. |
| 4 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/Tech-Co/docs/components/storefront.md` | `traceability/requirements/techco-storefront-component.md` | TM Forum northbound UX/API context | Storefront component context for TMF-facing flows. | UX/component documentation only. |
| 5 | `<USER_HOME>/Documents/Git_Offline/active/9.LABS_5G_lab_simulator/BF3-5G-Demo/open-digital-platform-2_0/5G_Emulator_API/docs/GETTING_STARTED.txt` | `references/bf3/5g-emulator-getting-started.txt` | 3GPP/O-RAN emulator reference | Lightweight emulator usage context. | Reference-only; not conformance proof. |

## Excluded from this recommendation

- `BF3-5G-Demo/docs/README.md` and `BF3-5G-Demo/docs/architecture.md` need link-closure planning before copying.
- `Tech-Co/docs/build_history.md` links to many build logs and should not be copied until a deliberate link-preservation plan exists.
- Whole directories remain excluded.
