# Architecture

The Telco Systems Integration Lab is organized around domain separation first, then
implementation. The goal is to keep standards, copied source, adapters, services,
tests, and evidence distinct enough that future work can be mapped to releases and
verified without overstating claims.

## Repository buckets

| Bucket | Responsibility | Source of truth? |
|---|---|---|
| `specs/` | Official standards and versioned reference material. | Standards references only. |
| `traceability/` | Release register, copy manifest, source inventory, evidence snapshots, and claim policy. | Yes for release/evidence state. |
| `models/` | Canonical and standard-native models. | Yes for model boundaries once populated. |
| `procedures/` | Standards-based flows, state machines, and release tracking process. | Yes for process. |
| `services/` | Deployable service implementations and copied mock core services. | Implementation source, not conformance proof by itself. |
| `adapters/` | Protocol/API/simulator/hardware connectors and copied RAN/O-RAN adapters. | Integration source, not conformance proof by itself. |
| `capabilities/` | End-to-end telco slices connecting standards, services, adapters, and tests. | Planning and traceability hub. |
| `tests/` | Unit, integration, interoperability, conformance, regression, and fixtures. | Evidence only when tied to a release/register row. |
| `docs/` | Human-readable architecture, runbooks, and documentation index. | Derived view. |
| `build_logs/` | Curated run evidence. | Runtime/demo evidence only unless explicitly promoted. |
| `references/` | Learning/source workspace references. | Reference material. |
| `experimental/` | Non-authoritative experiments. | No. |
| `vendor_profiles/` | Vendor-specific profiles and deviations. | Vendor-scoped evidence. |

## Flow of authority

```text
official standard / source artifact
        |
        v
traceability/source_inventory.csv
        |
        v
traceability/copy_manifest.csv  --> copied file under services/ or adapters/
        |
        v
traceability/standards_release_register.yaml
        |
        v
tests + curated evidence + docs
```

Documentation summarizes the above flow; it does not replace it. When a doc mentions a
standard, the release/test/gap state should be checked in the release register.

## Service and adapter boundary

- `services/` contains service-side implementations such as copied mock 5G core network
  functions.
- `adapters/` contains edge/interface components such as copied mock RAN, RIC, E2SM,
  O-RAN gateway, and future protocol/API adapters.
- UI/dashboard work belongs under `apps/` or `services/`, but should not become the
  source of truth for standards behavior.

## Current runnable surface

The root [`lab`](../lab) command provides the operator loop. The current commands are
summarized in the top-level [README](../README.md) and [Quickstart](../QUICKSTART.md).
Runtime integration is wrapper-driven so copied source files can remain byte-preserved.
See [Runtime Integration Plan](runtime_integration_plan.md).

## Design rules

1. Preserve copied source identity unless a later issue explicitly authorizes source
   changes.
2. Keep release tracking separate from runtime readiness.
3. Use `traceability/standards_release_register.yaml` before making or upgrading any
   standards claim.
4. Treat `tests/conformance/` as the gate for formal conformance evidence, not ordinary
   smoke/demo logs.
5. Track O-RAN by WG/spec/interface rather than a single global version.
