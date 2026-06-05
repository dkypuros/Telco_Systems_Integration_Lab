# Evidence Batch 010 Runtime Integration Caveats

Date: 2026-06-05
Batch: `evidence-batch-010`

## Purpose

Batch 010 adds runtime-integration wrappers and smoke checks for copied mock 5G core/RAN/O-RAN service code.

## Interpretation rule

Batch 010 may show that copied mock code has a defined Python path, dependency declaration, and import/AST smoke checks.

Batch 010 does **not** prove:

- formal 3GPP conformance,
- formal O-RAN conformance,
- production runtime readiness,
- interoperability with external network elements,
- dependency lock reproducibility beyond `config/requirements.txt`.

## Copy-only preservation

Copied source files under `services/mock_5g_core/`, `adapters/mock_ran/`, and `adapters/mock_oran/` remain unmodified by this batch. Runtime support is provided by wrapper scripts and documentation only.
