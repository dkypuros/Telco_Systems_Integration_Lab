# Runtime Integration Plan: Mock 5G Core/RAN/O-RAN Services

Date: 2026-06-05

## Scope

This plan makes the copied mock service code runnable from the Telco Systems Integration Lab **without editing the copied source files**. It is an integration-readiness step, not a conformance claim.

## Constraints

- Preserve byte identity of copied files under `services/mock_5g_core/` and `adapters/mock_*`.
- Do not refactor imports inside copied files.
- Do not claim 3GPP, O-RAN, or TM Forum conformance from runtime smoke tests.
- Runtime launch must be wrapper-driven via PYTHONPATH and dependency declaration.

## Runtime package layout

Copied files retain their original import assumptions. The wrapper sets:

```text
services/mock_5g_core
adapters/mock_ran
adapters/mock_ran/ran/ric
adapters/mock_oran
```

This supports original imports such as:

- `config.*`
- `core_network.*`
- `ran.*`
- top-level `e2sm_*`
- `oran.*`
- `api_gateway.*`

## Dependency declaration

`config/requirements.txt` declares runtime/test dependencies for copied mock services. `PyJWT` is required because `services/mock_5g_core/core_network/nrf.py` imports `jwt`.

## Smoke test command

```bash
python3 scripts/mock_service_smoke.py
```

A passing result means:

- copied Python files parse with `ast.parse`,
- wrapper import paths are sufficient,
- declared/imported dependencies are available in the active Python environment.

A blocked result with `missing_dependencies` means install the listed dependencies from `config/requirements.txt` in a disposable environment before runtime launch.

## Launch approach

Future service launch scripts should import `scripts/mock_runtime_env.py` and run copied files as subprocesses with the wrapper `PYTHONPATH`. Launchers should write curated evidence to `build_logs/`, not raw long-running logs.

## Claim hygiene

Runtime smoke evidence may support a claim that the mock services are importable/runnable in this lab environment. It must not be used as formal standards conformance evidence. Formal conformance claims remain gated to `tests/conformance/` and official CTK/spec evidence.
