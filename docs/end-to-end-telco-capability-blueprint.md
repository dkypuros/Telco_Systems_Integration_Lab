# End-to-End Telco Capability Blueprint

Status: Planning consensus draft

## Purpose

This blueprint defines what “complete end-to-end telco lab” means for the Telco Systems Integration Lab before we create GitHub issues or copy more code.

The target is not a pile of telco source trees. The target is a **standards-traceable telco digital twin**: a runnable, inspectable, evidence-producing lab that connects customer intent, TM Forum OSS/BSS, service orchestration, network domains, O-RAN control/management, assurance, charging, and conformance boundaries.

This document is capability-first. External implementations such as free5GC, Open5GS, OpenAirInterface/OAI, BF3-derived services, TM Forum learning assets, and future vendor systems are treated as **external implementation profiles** or **interoperability targets**, per [ADR 0001](adr/0001-external-implementation-profiles.md). They are not blindly absorbed as source trees, and they never become standards evidence merely because they exist in the repository or in local staging.

## Planning decision

Use a **profile-driven digital twin** approach:

1. define the capability slice first;
2. map standards and release baselines through `traceability/`;
3. define lab-owned service, adapter, profile, and test boundaries;
4. run the smallest executable vertical slice;
5. promote evidence only through the claim labels allowed by [Claim Hygiene Policy](../traceability/claim_hygiene_policy.md).

Do not create implementation issues that instruct agents to copy full upstream projects. Issue sets should be generated from capability slices, profile decisions, adapter boundaries, standards mappings, and test ladders.

## RALPLAN-DR summary

### Principles

1. **Capability before code** — define the telco capability domain before selecting a mock, external implementation profile, or new lab-owned service.
2. **Traceability before claims** — map standards body, release/version, implementation path, test evidence, and gap before using strong standards language.
3. **Profiles before vendoring** — external systems are pinned profiles and interoperability targets, not full source imports.
4. **Thin vertical slices first** — prove one customer-to-network flow end-to-end before expanding breadth.
5. **Evidence as a product feature** — every meaningful action should leave traceable evidence for review, testing, and later conformance work.

### Decision drivers

1. **Public-safe maintainability** — the repo is public, so it must avoid secrets, private paths, nested repos, raw standards bundles, generated binaries, and large unmanaged upstream trees.
2. **Standards-traceable completeness** — the lab must cover customer/OSS/BSS/network/O-RAN/assurance domains without pretending any single external profile provides the whole telco.
3. **Incremental executable value** — each slice should produce runnable behavior and test/evidence artifacts, not just architecture diagrams.
4. **Independent work chunks** — future GitHub issues should be separable enough that agents can work in parallel without conflicting over the same files.

### Viable options considered

| Option | Description | Pros | Cons | Verdict |
|---|---|---|---|---|
| A. Bulk source absorption | Copy full upstream projects into repo buckets and wire them together later. | Fast apparent progress; lots of code present. | Violates ADR/security rules; creates license and size risk; confuses source presence with standards evidence; delays actual integration boundaries. | Rejected. |
| B. Profile-driven digital twin | Keep external implementations outside the repo, define profiles/adapters/tests, and build lab-owned orchestration/evidence. | Public-safe; standards-traceable; supports many implementations; creates real integration boundaries. | Requires more design and harness work before visible breadth. | Chosen. |
| C. Mock-only demo lab | Use only lab-owned mocks and avoid external runtime profiles. | Fastest demo path; simplest local runtime. | Does not prove interoperability; limits credibility as an integration lab. | Useful for MVP baseline, insufficient as final strategy. |
| D. Standards-documentation-first only | Build matrices and docs before runtime slices. | Strong claim hygiene; low security risk. | Can become non-executable paperwork; weak demo value. | Use as guardrail, not sole strategy. |

## Target operating model

The lab should act as the **integration brain and evidence system** for a telco:

```text
Customer / Operator Intent
        |
        v
Storefront / Portal
        |
        v
TM Forum OSS/BSS APIs
        |
        v
Service Orchestration and Policy
        |
        v
Domain Adapters and External Profiles
        |
        +--> Mock 5G Core / EPC / IMS
        +--> free5GC profile
        +--> Open5GS profile
        +--> OAI RAN profile
        +--> O-RAN RIC/O1/O2/E2 profile
        |
        v
Assurance, Charging, Evidence, Traceability
```

The repo owns the intent translation, adapters, profiles, runbooks, evidence capture, and tests. External runtimes remain external unless a small curated file is justified, licensed, sanitized, and manifest-tracked.

## Cross-cutting governance

These rules apply to every slice and issue:

| Governance area | Source of truth | Rule |
|---|---|---|
| External implementation intake | [ADR 0001](adr/0001-external-implementation-profiles.md) | Treat upstream systems as profiles/interop targets. Do not bulk-copy full projects. |
| Standards release and gap tracking | [`traceability/standards_release_register.yaml`](../traceability/standards_release_register.yaml) | No standards claim without release, tested-against, evidence, conformance level, gap, and next step. |
| Claim labels | [Claim Hygiene Policy](../traceability/claim_hygiene_policy.md) | Use only the canonical standards-evidence labels listed below. |
| Source movement | [`traceability/source_inventory.csv`](../traceability/source_inventory.csv) and [`traceability/copy_manifest.csv`](../traceability/copy_manifest.csv) | Any copied/derived asset needs source, license, checksum, destination, and exclusion rationale. |
| Public repo hygiene | [`AGENTS.md`](../AGENTS.md) | No secrets, private paths, raw standards bundles, nested repos, generated binaries, or local runtime state. |
| Capability completeness | [`capabilities/manifest.md`](../capabilities/manifest.md) | A slice is not complete until implementation, tests, evidence, conformance level, gap, and next step are linked. |

### Canonical standards-evidence labels

For standards claims, use only the labels allowed by `traceability/claim_hygiene_policy.md`:

| Label | Use in this lab |
|---|---|
| `reference_only` | Useful source, spec note, profile metadata, or documentation exists; no runtime claim. |
| `planned` | Work is scoped but has no implementation/evidence yet. |
| `partial` | Some implementation exists, but scope and evidence are incomplete. |
| `functional_smoke` | A local smoke test proves a narrow function works, without standards conformance evidence. |
| `demo_evidence` | A repeatable demo produces evidence for a scenario, but it is not formal conformance. |
| `formal_conformance_missing` | The gap to formal conformance is known and explicitly recorded. |
| `conformance_candidate` | Executable evidence is mapped to standards release/spec/clause and is ready for deeper review. |
| `formal_conformance_evidence` | Reserved for strict evidence and any required official/certification process. |

ADR 0001 terms such as “external implementation profile” and “interoperability target” describe runtime roles. They are not standards-conformance labels and must not be used to strengthen a standards claim.

## Capability domains

| Domain | Goal | Standards families | Initial implementation posture | Key evidence |
|---|---|---|---|---|
| Storefront / customer portal | Let a customer or operator select a telco product and submit an order. | TM Forum customer/product/order APIs; project UX conventions. | Lab-owned sample app under `apps/`. | UI flow, API calls, order ID, product ID, trace ID. |
| Product catalog | Define sellable products such as 5G data, private network, slice, VoNR/voice package, or enterprise connectivity. | TMF620 and related TMF product model assets. | Lab-owned catalog API or curated TMF learning source, with CTK baseline recorded before strong claims. | Product spec JSON, catalog API response, release/register row. |
| Product/order management | Accept and track customer orders. | TMF622 and TMF order model; later TMF641 service order split. | Lab-owned service in `services/order_engine/`. | Order lifecycle events, validation, service order mapping. |
| Service inventory and activation | Track services and activate network-facing actions. | TMF638, TMF640, TMF641. | Lab-owned inventory/activation facade; adapters to network domains. | Service instance ID, activation state, adapter calls. |
| Service orchestration | Translate commercial intent into subscriber/session/slice/voice/RAN/O-RAN actions. | Cross-domain TM Forum + 3GPP + O-RAN mapping. | Lab-owned orchestration layer. | Orchestration graph, state transitions, evidence bundle. |
| Subscriber and identity | Provision subscriber profiles and authentication context. | 3GPP UDM/UDR/AUSF/HSS/IMS-HSS areas. | Mock first; Open5GS/free5GC profile adapters later. | Subscriber record, profile version, auth/profile mapping. |
| 5G packet core | Model or interoperate with AMF/SMF/UPF/NRF/NSSF/AUSF/UDM/UDR/PCF. | 3GPP 5GC TS family, release register governed. | Existing mock 5G core first; free5GC/Open5GS profiles later. | PDU/session demo, NRF registration, profile/version mapping. |
| EPC / legacy core | Support LTE/EPC and backward compatibility use cases. | 3GPP EPC/MME/SGW/PGW/HSS/PCRF areas. | External Open5GS profile or curated mock EPC later. | Attach/session evidence, EPC profile metadata. |
| IMS / voice / VoNR | Support voice capability separately from data core. | 3GPP IMS, SIP, VoLTE/VoNR related specs. | Separate capability; not implied by 5G core. Mock or external IMS profile needed. | Call flow trace, CSCF/HSS/MRF roles, voice service order mapping. |
| RAN and radio | Model gNB/UE/CU/DU/RU and RAN-facing behavior. | 3GPP RAN, NGAP, F1/E1, PHY/MAC/RLC/PDCP. | Existing mock RAN first; OAI profile later. | Radio scenario output, RAN adapter boundary evidence. |
| O-RAN control and management | Model RIC, E2, O1, O2, A1, fronthaul, closed-loop control. | O-RAN WG/spec-interface release tracking. | Existing mock O-RAN/RIC components first; external profiles later. | O-RAN map validation, control-loop evidence, release gap rows. |
| Assurance and observability | Detect service/network issues and record quality evidence. | TMF assurance APIs, O-RAN observability, project telemetry. | Lab-owned assurance service plus adapters. | Metrics, alarms, trouble/service problem events. |
| Charging, usage, and billing | Capture usage and simulate charge/bill flow. | TMF usage/billing APIs; 3GPP charging concepts. | Lab-owned simulation first; CHF/CDR profile later. | Usage event, charge record, billable product relation. |

## Canonical capability slice mapping

Use the existing slices in [`capabilities/manifest.md`](../capabilities/manifest.md) as the first issue groups. Domains may participate in more than one slice.

| Canonical slice | Primary domains | First outcome |
|---|---|---|
| `service_order_to_activation/` | Storefront, product catalog, product/order management, service inventory, activation, service orchestration, 5G packet core | A customer/order journey produces a network activation intent and evidence bundle. |
| `subscriber_lifecycle/` | Product/order management, service orchestration, subscriber and identity, 5G packet core, EPC/legacy core | A subscriber profile can be created, updated, and mapped to mock or profiled network functions. |
| `slice_provisioning/` | Product catalog, service orchestration, NSSF/slice functions, O-RAN O2/O1 as applicable, assurance | A network slice offer/order/provision path is mapped to TM Forum, 3GPP NSSAI/NSSF, and applicable O-RAN management boundaries. |
| `ran_control_loop/` | RAN and radio, O-RAN control/management, assurance, service orchestration | An assurance or policy event can trigger a modeled RAN/O-RAN control action with evidence. |
| `assurance_to_remediation/` | Assurance, observability, service inventory, service orchestration, O-RAN/TMF assurance interfaces | A detected issue can be correlated to a service and produce a remediation action or trouble/assurance record. |

### Candidate future slices

These domains are required for “complete telco” thinking but should not be forced into the first issue batch unless the boundary is explicitly scoped:

| Candidate slice | Why separate |
|---|---|
| `ims_voice_service/` | IMS/VoNR voice needs CSCF/HSS/MRF/SIP/call-flow modeling and is not implied by 5G packet core presence. |
| `usage_charging_billing/` | Charging and billing need their own usage event, CDR/charge, rating, and bill simulation chain. |
| `storefront_experience/` | A richer e-commerce/operator UI can evolve independently after the first API-first MVP. |

A future issue may add these slices to `capabilities/manifest.md` after their standards, adapter, and evidence boundaries are clear.

## MVP vertical slice

The first meaningful slice should be narrow but complete:

> Storefront or API client → TMF-style product/order API → orchestration → mock subscriber/session provisioning → mock 5G core response → assurance/evidence record → traceability links.

This starts inside `service_order_to_activation/` and touches `subscriber_lifecycle/`. It should not require running external upstream repos.

### MVP acceptance criteria

- A product exists in catalog for a basic 5G data service.
- A storefront or simple UI/API client can place an order for that product.
- The order engine creates a service order or activation plan.
- The orchestrator maps the order to subscriber/profile/session intent.
- The mock 5G core receives or simulates the provisioning/session action.
- Assurance/evidence records show the end-to-end path by correlation ID.
- The release register and source inventory identify which standards are `reference_only`, `planned`, `partial`, `functional_smoke`, or `demo_evidence`.
- Tests prove the local slice works without requiring external upstream repos.

## Expansion slices

After the MVP, add slices independently:

| Slice | Purpose | Likely profile/domain work | Initial standards-evidence label |
|---|---|---|---|
| `subscriber_lifecycle/` interop | Prove subscriber provisioning and updates against a pinned profile. | Open5GS/free5GC profile metadata, adapter contract, interop test. | `planned` until a repeatable test exists. |
| `slice_provisioning/` | Prove slice offer/order/provision path. | TMF product/order models, NSSF/NSSAI mapping, O-RAN O2/O1 boundary. | `planned` until local smoke evidence exists. |
| `ran_control_loop/` | Connect assurance or policy event to RAN/O-RAN action. | RIC/O1/O2/E2 adapter, policy, evidence. | Initial `planned`; target `demo_evidence` only after repeatable demo evidence exists. |
| `assurance_to_remediation/` | Raise and remediate service/network problems. | Alarm, service problem, metrics, remediation workflow. | `planned` until evidence snapshots exist. |
| IMS/VoNR voice candidate | Add voice product and call-flow evidence. | IMS mock/profile, CSCF/HSS/MRF model, VoNR order mapping. | `planned`; create capability slice first. |
| Charging/usage candidate | Generate usage and simulated billing from service activity. | Usage events, charge records, billing facade. | `planned`; create capability slice first. |

## Issue taxonomy to create after consensus

Do not create issues until this blueprint is approved. When ready, create issues in this order so each issue has a clear ownership boundary and does not overclaim standards status.

### 1. Cross-cutting issue gates

- Add/maintain capability issue template with required standards-evidence fields.
- Add/maintain external profile metadata template.
- Add/maintain adapter contract template.
- Add/maintain evidence bundle format and correlation ID convention.
- Seed planned release-register rows for standards referenced by the first issues but not yet individually represented, such as TMF640 or O-RAN A1/E2/O1/O2, before implementation issues claim them.
- Add claim-hygiene remediation guardrails before implementation issues: scan copied/mock source wording such as `100% Compliant`, `3GPP-compliant`, `O-RAN complete`, or equivalent language in `services/mock_5g_core/` and `adapters/mock_ran/`, then either soften the wording or link it to supported release-register evidence and gap language.
- Add/maintain public-repo security and copy-manifest verification checks.

### 2. `service_order_to_activation/`

- Define API-first MVP flow and evidence bundle.
- Create basic product catalog fixture/API for 5G data service.
- Create product order lifecycle and service activation plan.
- Add orchestration graph from order to mock network action.
- Add integration test from order to activation evidence.

### 3. `subscriber_lifecycle/`

- Define subscriber profile model and standards mapping rows.
- Connect order/activation to mock subscriber provisioning.
- Define Open5GS/free5GC subscriber adapter contracts without vendoring upstream code.
- Add profile-specific interop test harness placeholders gated behind external runtime availability.

### 4. `slice_provisioning/`

- Define slice product and service model.
- Map TM Forum order fields to 3GPP NSSAI/NSSF concepts and O-RAN management boundaries.
- Add mock slice provisioning path.
- Add evidence and gap rows for slice standards claims.

### 5. `ran_control_loop/`

- Define RAN/O-RAN control-loop scenario.
- Map O-RAN A1/E2/O1/O2 boundaries and 3GPP RAN dependencies.
- Add mock control-loop demo path.
- Add OAI/RIC profile metadata and interop runbooks as profile work, not source copies.

### 6. `assurance_to_remediation/`

- Define service assurance event model and correlation strategy.
- Connect mock network/service event to service problem/remediation action.
- Add observability/evidence snapshots.
- Add demo evidence tests for the remediation loop.

### 7. Future slice candidates

- Add `ims_voice_service/` capability manifest entry after IMS standards, profile, and call-flow boundaries are scoped.
- Add `usage_charging_billing/` capability manifest entry after usage, charging, rating, and bill boundaries are scoped.
- Add `storefront_experience/` capability manifest entry only after API-first MVP is stable.

## First-wave MVP issue write scopes

Split the MVP so parallel issue work does not collide. Each issue may add tests and traceability rows required for its own scope, but it should not edit another service/domain unless the issue explicitly says so.

| MVP issue area | Primary write scope | May read/call | Initial evidence label | Target evidence label |
|---|---|---|---|---|
| Product catalog fixture/API | `services/catalog_api/`, `models/standard_native/tmf/`, catalog tests | `traceability/standards_release_register.yaml`, `services/order_engine/` contracts | `planned` | `functional_smoke` |
| Product order lifecycle | `services/order_engine/`, order tests | catalog API/model contracts, orchestration contract | `planned` | `functional_smoke` |
| Activation/orchestration graph | `services/orchestration/` or chosen lab-owned orchestration path, orchestration tests | catalog/order contracts, mock core adapter contract | `planned` | `demo_evidence` only after an end-to-end evidence bundle exists |
| Mock core activation adapter | `adapters/3gpp/`, adapter tests | `services/mock_5g_core/` public API surface; do not rewrite mock core unless issue says so | `partial` or `planned` based on existing evidence row | `functional_smoke` |
| Evidence/correlation bundle | `traceability/evidence_snapshots/`, `build_logs/`, evidence schema/tests | all MVP service outputs by correlation ID | `planned` | `demo_evidence` |
| MVP integration test | `tests/integration/`, optional fixtures | catalog, order, orchestration, adapter, mock core | `planned` | `demo_evidence` for the narrow MVP only |

## Issue-author boundary note

Every standards-related issue must include:

- capability slice name;
- affected standards family and release-register row or planned row;
- current canonical standards-evidence label;
- target evidence label for this issue;
- implementation paths the issue may edit;
- tests/evidence the issue must produce;
- explicit known gap to latest or formal conformance;
- statement that no full upstream project should be copied unless a separate copy-manifest issue approves a small, licensed, sanitized file.

No issue may claim stronger standards language than the release register, conformance boundary, and claim hygiene policy support.

## Pre-mortem

1. **Failure: repo becomes an unmanaged code dump.**
   - Mitigation: enforce ADR 0001, external profile metadata, and copy-manifest gates before any source movement.
2. **Failure: standards claims outrun evidence.**
   - Mitigation: require canonical standards-evidence labels and release register rows in every issue that touches standards language.
3. **Failure: MVP becomes too broad and stalls.**
   - Mitigation: first slice uses mock core only; external profiles wait until the local storefront-to-core path works.
4. **Failure: external profiles hide missing telco domains.**
   - Mitigation: keep IMS/voice, charging/billing, O-RAN, assurance, and storefront as explicit domains even when a core profile lacks them.
5. **Failure: issue swarm creates conflicts.**
   - Mitigation: make issues slice-owned with explicit write scopes and separate governance/profile/test work from service implementation.

## Verification strategy

| Level | What it verifies | Example location | Claim boundary |
|---|---|---|---|
| Unit | Individual domain service/adapters validate inputs and outputs. | `tests/unit/` | Usually `functional_smoke` at most. |
| Integration | Storefront/API/order/orchestrator/mock core cooperate locally. | `tests/integration/` | `functional_smoke` or `demo_evidence` depending on evidence quality. |
| Interoperability | Lab talks to a pinned external implementation profile. | `tests/interoperability/` | Still not formal conformance unless mapped to standards clauses. |
| Conformance candidate | Behavior is mapped to release/spec/clause with executable evidence. | `tests/conformance/` | `conformance_candidate` only after review. |
| Observability | Evidence, correlation IDs, logs, metrics, and run summaries exist. | `traceability/evidence_snapshots/`, `build_logs/` | Supports other labels but does not prove protocol conformance by itself. |

### Command-level verification gates

Use these commands as the default verification floor for issue batches generated from this blueprint. A narrower issue may justify a subset, but standards, traceability, source-intake, public-safety, or cross-slice issues should run the full set.

```bash
git status --short --branch
git ls-files -o --exclude-standard
git diff --check
git diff --cached --check
python3 -m pytest tests/unit tests/integration tests/regression tests/conformance
python3 scripts/validate_oran_spec_map.py --strict
git grep -n -I -E '/(Users|home)/[^[:space:]]+' -- . ':!.git'
git grep -n -I -E 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|ya29\.[0-9A-Za-z_-]+|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}' -- . ':!.git'
git ls-files | grep -Ei '(^|/)(\.env|.*\.pem|.*\.key|.*id_rsa.*|.*id_dsa.*|.*id_ed25519.*|.*kubeconfig.*|credentials|secrets?|token|private|\.npmrc|\.pypirc|netrc)(\.|$|/)'
git ls-files | grep -Ei '(^specs/(3gpp|oran|tmforum|ETSI|etsi)/.*\.(pdf|docx?|xlsx?|zip|jar|dmg|7z|tar|gz)$)|Codex\.dmg|(^|/)\.git(/|$)'
```

The grep checks should produce no output except documented false positives. Clean no-match grep commands may exit with status 1; treat printed matches as the exposure signal.

Standards issues also need a release-register validation pass before closeout:

1. every referenced standards family/spec has an existing or newly seeded row in `traceability/standards_release_register.yaml`;
2. every row touched by the issue has `local_tested_against`, `local_test_evidence_path`, `conformance_level`, `known_gap_to_latest`, and a next validation step;
3. any promotion toward `conformance_candidate` has an executable test path and preserved evidence snapshot;
4. no issue uses `100%`, `compliant`, `release-complete`, or similar language unless the claim-hygiene gate is satisfied.

## Follow-up staffing guidance

When this blueprint becomes issue-ready:

- Use a `planner` lane to group issues by canonical capability slice and dependency.
- Use an `architect` lane to validate domain boundaries and adapter contracts.
- Use a `critic` lane to challenge overclaims, missing domains, and unsafe source intake.
- Use a `test-engineer` lane to define acceptance tests for each slice.
- Use `executor` lanes only after each issue has a clear owned write scope.
- Use `security-review` after any batch that changes intake rules, external profiles, or public-facing evidence.

## Next planning action

Run architect and critic review on this blueprint. If approved, create GitHub issues from the slice-first taxonomy, starting with cross-cutting issue gates and the `service_order_to_activation/` MVP. Do not create implementation issues that copy full upstream repositories.
