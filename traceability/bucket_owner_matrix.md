# Bucket Owner Matrix

Purpose: make bucket ownership explicit so copied artifacts do not become an ungoverned second source of truth.

`traceability/standards_release_register.yaml` is the authoritative source for release status, tested-against baseline, conformance level, and gap-to-latest. Narrative docs are derived views.

| Bucket | Owner role | Allowed artifact classes | Claim authority | Notes |
|---|---|---|---|---|
| `specs/` | Standards curator | Official specs, extracted standard references, CTK/RI assets, spec snapshots | No implementation claim by itself | Must link to `traceability/standards_release_register.yaml`. |
| `traceability/` | Conformance lead | Release register, source inventory, copy manifest, evidence snapshots, conformance matrix, coverage maps | Highest authority for release/test/gap claims | This is the source of truth for what is latest, stable, tested, copied, and gapped. |
| `models/canonical/` | Domain model owner | Internal normalized lab models and invariants | No standards conformance claim without mapping | Canonical models cannot erase standard-native differences. |
| `models/standard_native/` | Standards model owner | Standard-shaped schemas/types/models from 3GPP, TM Forum, O-RAN | Can claim standard alignment only through register + tests | Keep per-family and version-labeled. |
| `models/mappings/` | Model mapping owner | Canonical-to-standard and standard-to-standard mappings | Mapping claim only | Must identify loss, transformation, and version assumptions. |
| `procedures/` | Procedure owner | State machines, release tracking procedures, call flows | Procedure claim only with tests/conformance evidence | Procedures do not own protocol adapters. |
| `adapters/` | Integration owner | Protocol/API/simulator/hardware connectors | Adapter behavior claim only | External-system coupling lives here. |
| `services/` | Service owner | Deployable APIs/services and service composition | Runtime behavior claim only | Services consume models/procedures/adapters; they do not define standards truth. |
| `capabilities/` | Capability owner | Vertical slices linking models, procedures, adapters, services, tests | End-to-end capability claim only with traceability and test evidence | Capabilities are the product-facing integration map. |
| `tests/conformance/` | Test/conformance owner | Standards claim gates and conformance harnesses | Required for conformance claims | Must reference register row, spec/release, expected verdict, and evidence. |
| `tests/integration/` | Integration test owner | End-to-end runtime and API tests | Integration claim only | Not standards conformance unless promoted and mapped. |
| `tests/interoperability/` | Interop test owner | Tests against external/reference implementations | Interop claim only | Must name implementation/version. |
| `tests/regression/` | Regression owner | Existing behavior regression tests | Regression claim only | Protects lab behavior, not standard compliance. |
| `tests/unit/` | Component test owner | Unit tests | Unit correctness claim only | Does not prove conformance. |
| `build_logs/` | Evidence curator | Curated run evidence and accepted logs | Evidence only | Raw logs stay out unless curated. |
| `docs/` | Documentation owner | Architecture, runbooks, migration plans, ADRs | Derived narrative only | Must defer release/conformance claims to `traceability/`. |
| `apps/` | UX/app owner | Dashboards and frontends | Display/UI claim only | UI is never source of standards truth. |
| `config/` | Operations owner | Environment and service config | Config claim only | Version and environment must be explicit. |
| `scripts/` | Operations owner | Safe scripts and run harnesses | Operational behavior claim only | Must not mutate originals during copy-only phase. |
| `references/` | Reference curator | Learning assets and source workspace references | Reference only | Do not imply adoption/conformance. |
| `external/` | External integration owner | Third-party integrations | External integration claim only | Pin source/version before use. |
| `experimental/` | Experiment owner | Non-authoritative experiments | No conformance claim | Must be promoted through traceability before production use. |
| `vendor_profiles/` | Vendor profile owner | Vendor-specific profiles/deviations | Vendor profile claim only | Must label deviation vs standard. |
