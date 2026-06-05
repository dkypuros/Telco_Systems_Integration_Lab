# Evidence Batch 009 Code Intake Caveats

Date: 2026-06-05  
Batch: `evidence-batch-009`  
Recorded at: `2026-06-05T02:42:58Z`

## Purpose

Batch 009 continues source-code intake after batch 008 by copying remaining mock core functions, RIC modules, E2SM support modules, fronthaul/slicing support, and an O-RAN gateway/spec-map pair.

## Interpretation rule

The copied code is:

- byte-identical source intake,
- suitable for AST/static inspection,
- useful for organizing future mock core/RAN/O-RAN service boundaries.

The copied code is **not yet**:

- runtime-integrated into the new lab,
- dependency-managed by this lab,
- import-path normalized,
- executed as services from this lab,
- formal 3GPP or O-RAN conformance proof.

## Runtime dependency caveats

Some copied files import external packages such as FastAPI, Uvicorn, Pydantic, requests/httpx, OpenTelemetry, prometheus_client, jwt, and package-context modules. Batch 009 intentionally does not install dependencies or refactor imports.

A later integration batch should define package layout, PYTHONPATH, service launch commands, dependency lock strategy, and executable tests.

## Handling instruction

Do not claim formal 3GPP/O-RAN conformance from AST-clean copied code. Do not run these as production services until runtime integration is planned and tested.
