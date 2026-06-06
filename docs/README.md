# Documentation Index

This documentation set is the public-facing map for the Telco Systems Integration Lab.
It explains what is present, where evidence lives, and which claims are intentionally
bounded.

## Start here

| Document | Use it for |
|---|---|
| [End-to-End Telco Capability Blueprint](end-to-end-telco-capability-blueprint.md) | Slice-first plan for building the complete standards-traceable telco lab without blind upstream source absorption. |
| [Architecture](architecture.md) | Lab buckets, source boundaries, and how services/adapters/tests/evidence fit together. |
| [Standards Mapping](standards-mapping.md) | How 3GPP, TM Forum, and O-RAN references map to repo folders and release tracking. |
| [Core Network](core-network.md) | Mock 5G core service inventory, runtime hooks, and caveats. |
| [RAN Components](ran-components.md) | gNB, CU, DU, fronthaul, slicing, and RAN-side caveats. |
| [O-RAN Components](oran-components.md) | RIC, E2/E2SM, O-RAN gateway, and O-RAN tracking caveats. |
| [TM Forum Components](tmforum-components.md) | TMF API evidence, CTK baselines, and promotion path. |
| [API Reference](api-reference.md) | Current API and endpoint evidence sources. |
| [Testing](testing.md) | Unit, integration, runtime smoke, regression, interoperability, and conformance boundaries. |
| [Conformance Boundary](conformance-boundary.md) | What is proven, what is not proven, and what evidence is required before stronger claims. |
| [Issue Authoring](issue-authoring.md) | Required standards-evidence fields for GitHub issues and agent work chunks. |
| [Evidence Bundles](evidence-bundles.md) | Correlation ID and evidence bundle format for traceable demos/tests. |

## Architecture decisions

| Decision | Use it for |
|---|---|
| [ADR 0001: External implementation profiles](adr/0001-external-implementation-profiles.md) | Why third-party telco systems are profiles/interop targets, not vendored source trees, and how capability domains drive the end-to-end lab. |

## Supporting project records

| Record | Purpose |
|---|---|
| [Standards release register](../traceability/standards_release_register.yaml) | Authoritative release/tested-against/gap register. |
| [Claim hygiene policy](../traceability/claim_hygiene_policy.md) | Required evidence before using standards-conformance language. |
| [Standards release procedure](../procedures/standards_release_tracking.md) | Step mechanism for refreshing latest, tested-against, gaps, and next actions. |
| [Copy manifest](../traceability/copy_manifest.csv) | Source-to-destination copy identity and checksum record. |
| [Source inventory](../traceability/source_inventory.csv) | Inventory of source artifacts and their standards/evidence metadata. |
| [Runtime integration plan](runtime_integration_plan.md) | Wrapper-driven runtime approach for copied mock services. |
| [Migration plan](migration_plan.md) | Copy-only intake rules and exclusions. |

## Claim boundary

This lab is a standards-traceable integration workspace with copied evidence, runnable
mock services, release tracking, and explicit conformance boundaries. Runtime smoke
evidence supports local demo/readiness claims only; it does **not** prove formal 3GPP,
O-RAN, or TM Forum conformance.
