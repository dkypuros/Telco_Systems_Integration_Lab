# ADR 0001: External implementation profiles, not vendored source trees

Status: Accepted

## Context

The lab goal is to become a complete end-to-end, standards-traceable telco integration environment across OSS/BSS, orchestration, core network, RAN, O-RAN, and test evidence.

Candidate upstream implementations such as free5GC, Open5GS, OpenAirInterface/OAI, BF3-derived simulators, TM Forum learning assets, and other vendor or open-source systems are valuable because they can act as realistic implementations or references.

However, complete upstream repositories are not themselves traceability, conformance evidence, or lab-owned source. Bulk importing them would create public-repository safety risk, license risk, maintenance risk, nested repository risk, generated/binary artifact risk, and standards-claim confusion.

No single external implementation should be treated as the end-to-end telco architecture. Some 5G core projects do not provide IMS/VoNR, OSS/BSS, TM Forum APIs, storefront flows, O-RAN management, assurance, charging/billing, or a customer/order experience. A complete lab must be capability-driven, not vendor-tree-driven.

## Decision

This repository treats third-party/open-source/vendor telco systems as **external implementation profiles** and **interoperability targets**, not as source trees to blindly absorb.

The repo owns:

- standards release tracking;
- source inventory and copy manifests;
- vendor/reference profile metadata;
- adapter contracts and boundary code;
- orchestration and runbooks that locate or fetch external runtimes;
- interoperability tests and evidence capture;
- conformance-boundary language and claim hygiene.

The repo does **not** own full upstream implementation trees by default.

The repo also does **not** infer end-to-end completeness from any single implementation profile.

## Practical rule

Do not copy full upstream projects such as free5GC, Open5GS, OpenAirInterface/OAI, or similar products into `external/`, `services/`, or `adapters/` simply because they exist in local staging.

Instead, for each candidate implementation:

1. Create or update a profile under `vendor_profiles/<implementation>/`.
2. Record upstream URL, commit/tag/digest, license, intended role, excluded artifacts, local runtime expectations, and standards areas touched.
3. Add or update traceability rows in `traceability/source_inventory.csv`, `traceability/copy_manifest.csv`, and `traceability/standards_release_register.yaml` only for derived, public-safe evidence.
4. Keep large upstream source trees outside the public repo or in ignored local staging.
5. Write adapter contracts in `adapters/` only for the boundary this lab controls.
6. Put runnable interop checks in `tests/interoperability/` and label them by implementation profile and version.
7. Promote anything toward `tests/conformance/` only after clause-level standards mapping and executable evidence exist.

## Bucket policy

| Bucket | Role for external implementations |
|---|---|
| `vendor_profiles/` | Public-safe metadata about an external implementation profile. |
| `references/open_source_cores/` | Derived summaries, not full source drops. |
| `external/` | Lightweight integration shims or pointers only; not a dump bucket for full upstream repos. |
| `adapters/` | Lab-owned boundary contracts and translation code. |
| `tests/interoperability/` | Tests proving this lab can talk to a specific external profile/version. |
| `tests/conformance/` | Only standards-clause-backed tests with explicit evidence and claim gates. |
| `traceability/` | Release/register/source/evidence facts used to justify claims. |

## Capability-domain policy

Design the lab by capability domains first, then decide which implementation profile, mock, adapter, or new lab-owned service participates in that domain.

| Capability domain | Examples | Profile implication |
|---|---|---|
| Customer and storefront | Sample e-commerce store, operator dashboard, product browsing, order placement | Usually lab-owned app; not provided by 5G core projects. |
| TM Forum OSS/BSS | Product catalog, product order, service inventory, service activation, trouble/assurance APIs | Requires TMF-specific services, models, CTK evidence, and mappings. |
| Service orchestration | Translate commercial/service intent into network/service actions | Lab-owned orchestration layer and adapter contracts. |
| Subscriber and identity | Subscriber provisioning, authentication profile, UDM/HSS/HSS-like data | May target mock core, free5GC, Open5GS, or IMS/EPC profiles. |
| 5G packet core | AMF, SMF, UPF, NRF, NSSF, AUSF, UDM, UDR, PCF | Candidate fit for free5GC/Open5GS/mock 5GC profiles. |
| EPC and legacy interop | MME, SGW, PGW, HSS, PCRF, LTE attach, VoLTE adjacency | Candidate fit for Open5GS/EPC or mock EPC profiles. |
| IMS and voice | P-CSCF, I-CSCF, S-CSCF, IMS-HSS, MRF, VoLTE/VoNR call flow | Must be treated as a separate capability; not implied by a 5G core profile. |
| RAN and radio | gNB, UE simulator, CU/DU/RU, F1/E1/NGAP, PHY/MAC/RLC/PDCP | Candidate fit for OAI/RAN profiles or mock RAN adapters. |
| O-RAN management/control | Near-RT RIC, Non-RT RIC, E2, O1, O2, A1, fronthaul | Requires O-RAN-specific profiles, adapters, and release tracking. |
| Assurance/observability | Metrics, alarms, closed-loop policy, service quality | Lab-owned assurance plus O-RAN/TMF mappings. |
| Charging and billing | CHF, CDRs, usage, billing/settlement flows | Separate domain; do not infer from packet-core presence. |

When planning issues, start from this capability map. External profiles answer “what runtime can we interoperate with for this domain?” They do not answer “what domains does a complete telco lab need?”

## Claim ladder

Use these labels consistently:

1. `reference_only` — useful for study or design comparison; no runtime claim.
2. `implementation_profile` — pinned external runtime candidate with metadata.
3. `interop_target` — external runtime the lab can talk to through a defined adapter.
4. `interop_verified` — repeatable test evidence proves the lab interacts with the profile/version.
5. `conformance_candidate` — test is mapped to standards clauses and release baseline.
6. `formal_conformance` — reserved for strict evidence and any required official/certification process.

Never infer `formal_conformance` from the presence of upstream code.

## When source may be copied

Small copied source snippets or files are allowed only when all of these are true:

- the file is necessary for a lab-owned adapter, fixture, or traceability artifact;
- the license is compatible and recorded;
- the copy is listed in `traceability/copy_manifest.csv` with checksum evidence;
- private paths, secrets, certs/keys, generated outputs, nested repositories, binaries, raw standards bundles, and runtime state are excluded;
- the destination bucket matches the role of the artifact;
- the claim boundary remains explicit.

## OMX and issue policy

An OMX plan may sequence work that implements this ADR, but the ADR and `AGENTS.md` are the durable source of truth.

Do not create batches of GitHub issues for upstream integration until the relevant external implementation profile and adapter boundary are understood well enough to avoid blind source absorption.

Issue sets should be generated from profile decisions, adapter boundaries, standards mappings, and test ladders — not from a generic instruction to copy a repository.

## Consequences

Benefits:

- keeps the public repo small, safe, and standards-traceable;
- avoids nested repositories, keys/certs, local paths, binaries, and license surprises;
- makes interoperability claims reproducible by implementation profile/version;
- preserves room to support multiple implementations without making any one upstream project the lab's source of truth.

Costs:

- requires more design up front;
- integration starts with metadata, adapters, and harnesses rather than a large code copy;
- some runtime work must happen through external checkouts, containers, or operator-provided paths.
