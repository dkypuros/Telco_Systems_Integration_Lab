# Evidence Batch 008 Code Intake Caveats

Date: 2026-06-05  
Batch: `evidence-batch-008`  
Recorded at: `2026-06-05T02:24:48Z`

## Purpose

Batch 008 is the first intentional source-code intake batch for mock 5G core and RAN simulator code. The copied files are preserved byte-identically from the source workspace.

## Interpretation rule

The copied code is:

- mock/simulator source intake,
- useful for later service/adapters organization,
- suitable for AST/static inspection,
- evidence of implementation shape.

The copied code is **not yet**:

- runtime-integrated into the new lab,
- dependency-managed by this lab,
- import-path normalized,
- executed as services from this lab,
- formal 3GPP or O-RAN conformance proof.

## Runtime dependency caveats

Several copied files import packages or modules that are not resolved by copy-only intake alone, including FastAPI, Uvicorn, Pydantic, requests/httpx, OpenTelemetry, prometheus_client, and package-context imports such as `config` and `core_network`.

Batch 008 includes `config/__init__.py`, `config/ports.py`, and `core_network/transport.py` to preserve key local support files, but a later runtime integration batch must define PYTHONPATH/package layout, dependency installation, service launch commands, and tests.

## Handling instruction

Do not treat these files as runnable production services until a later integration batch adds dependency and import-path planning. Do not claim formal 3GPP/O-RAN conformance from AST-clean copied code.
