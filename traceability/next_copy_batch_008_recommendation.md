# Next Copy-Only Batch Recommendation: Evidence Batch 008 Code Intake

Date: 2026-06-05
Target lab: `<LAB_ROOT>`
Canonical source root: `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api`
Status: recommendation only; **no batch-008 code copied yet**.

## Purpose

Batch 008 is the first intentional source-code intake batch. It should copy actual mock 5G core network functions and RAN simulators into the formal lab buckets while preserving byte identity and clearly labeling them as mock/simulator services, not formal standards conformance proof.

## Recommended source-to-destination rows

| Proposed ID | Source | Recommended destination | Role | Standards domain | Precheck | Reason |
|---|---|---|---|---|---|---|
| `planned-code-061` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/core_network/amf.py` | `services/mock_5g_core/core_network/amf.py` | AMF mock service | 3GPP 5GC AMF | exists=True; AST_OK; sha256=`795e5580ac3a6dd36b738d6d4e755fad6e597bb0602c1f7a1381f1605a07cac1` | Primary access/session control mock core function requested by user. |
| `planned-code-062` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/core_network/smf.py` | `services/mock_5g_core/core_network/smf.py` | SMF mock service | 3GPP 5GC SMF | exists=True; AST_OK; sha256=`e20ad8403cb6d7f9ea860fed08892e8bdddee83ddabd30af1dc946eb3c206ae7` | Primary session management mock core function requested by user. |
| `planned-code-063` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/core_network/udr.py` | `services/mock_5g_core/core_network/udr.py` | UDR mock service | 3GPP 5GC UDR | exists=True; AST_OK; sha256=`1963cb235ae35bf09fb293496d1bb902b572b0d4a08d431b4fce82bf59796044` | Subscriber data repository mock core function requested by user. |
| `planned-code-064` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/core_network/nssf.py` | `services/mock_5g_core/core_network/nssf.py` | NSSF mock service | 3GPP 5GC slicing/NSSF | exists=True; AST_OK; sha256=`87ba797bcd03f05bde0ae206c1ea81d3cbf62a7aa115081112e79bd8e2fac39e` | Network slice selection mock core function requested by user. |
| `planned-code-065` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/config/__init__.py` | `services/mock_5g_core/config/__init__.py` | config package support | runtime support | exists=True; AST_OK; sha256=`b3ebdc87b5d7b6d1f1ea621f8856913d78b1b14147494b05dca8a25e0504820e` | Required because core functions import `config` package. |
| `planned-code-066` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/config/ports.py` | `services/mock_5g_core/config/ports.py` | port/config support | runtime support | exists=True; AST_OK; sha256=`514462af50044fa8225e9f3dcf3bb6775aec1a725db65b558ebec876b331f147` | Required because several services import `config.ports`. |
| `planned-code-067` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/core_network/transport.py` | `services/mock_5g_core/core_network/transport.py` | transport support | 3GPP N4/PFCP transport support | exists=True; AST_OK; sha256=`df4ad22df35200caf66f0056cf3d42fab3afb9bc75a40199acbee7f291742695` | Required by core network services using shared transport helpers. |
| `planned-code-068` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/ran/gnb.py` | `adapters/mock_ran/ran/gnb.py` | gNB simulator | 3GPP RAN / O-RAN adjacency | exists=True; AST_OK; sha256=`e477b3b353365a330efb0e4ba81230c87e4e0c979dc2391bc52293853e4cad51` | Primary RAN simulator entrypoint. |
| `planned-code-069` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/ran/cu.py` | `adapters/mock_ran/ran/cu.py` | CU simulator | 3GPP RAN CU / O-RAN split adjacency | exists=True; AST_OK; sha256=`4d63d259397afe1e5eeef83fbccdc01ea7832be791ae9a9ee9959ab50519271c` | Central Unit simulator entrypoint. |
| `planned-code-070` | `<SOURCE_5G_LAB_SIMULATOR_ROOT>/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/ran/du.py` | `adapters/mock_ran/ran/du.py` | DU simulator | 3GPP RAN DU / O-RAN split adjacency | exists=True; AST_OK; sha256=`d3f8619c3b5ce05ad6ec5b59a6d8f9143b1845c6803218d1a5f78342dda1b275` | Distributed Unit simulator entrypoint. |

## Mapping rule

- Core network functions go under `services/mock_5g_core/core_network/`.
- Shared core/config support goes under `services/mock_5g_core/config/` and `services/mock_5g_core/core_network/`.
- RAN simulator entrypoints go under `adapters/mock_ran/ran/`.
- Preserve byte identity via `shutil.copy2`; do not refactor imports in the copy batch.

## Dependency and runtime caveats

- This recommendation is **code intake**, not runtime integration.
- The copied files import external packages such as FastAPI, Uvicorn, Pydantic, requests/httpx, OpenTelemetry, and prometheus_client. Do not add dependencies in the copy batch unless explicitly requested.
- Several files expect package/import context such as `config` and `core_network`. Batch 008 includes `config/ports.py`, `config/__init__.py`, and `core_network/transport.py`, but an execution wrapper/PYTHONPATH plan is still needed before running these as services.
- Batch 008 intentionally starts with AMF, SMF, UDR, NSSF plus gNB/CU/DU. Suggested later batch: NRF, UPF, UDM, AUSF, RIC files (`near_rt_ric.py`, `non_rt_ric.py`, `e2ap.py`, `e2sm_*`) and O-RAN gateway files.

## Required verification when batch 008 is executed

1. Append rows as `status=planned` first; do not copy until validation passes.
2. Validate all source paths exist and destinations are new under `services/` or `adapters/`.
3. Copy with `shutil.copy2` only.
4. Record source and destination SHA-256 checksums in `traceability/copy_manifest.csv`.
5. Run Python `ast.parse` on every copied `.py` file.
6. Verify no Markdown links are affected; this batch contains Python only.
7. Add a claim caveat: mock core/RAN code is functional simulation/source intake, not 3GPP or O-RAN conformance proof.
8. Do not copy virtualenvs, caches, duplicate `Tech-Co/components/...` mirrors, or whole source directories.

## Explicit exclusions for batch 008

- Do not copy duplicate mirror files under `Tech-Co/components/legacy-standalone-5g-emulator/...`.
- Do not copy virtualenvs (`venv`, `venv_verify`, `test_venv`), `__pycache__`, `.pyc`, logs, DB files, or generated outputs.
- Do not copy entire `core_network/` or `ran/` directories yet; copy only listed files.
- Do not refactor imports or make runtime edits in this batch. Runtime adaptation belongs in a later integration batch.

## Post-copy status

Executed on 2026-06-05. This recommendation is superseded by `traceability/evidence_batch_008_copy_report.json`, `traceability/evidence_batch_008_review_summary.md`, and `.omx/ultragoal/copy-batches/2026-06-05-evidence-batch-008.json`, which record copied, checksum-verified, AST-clean state.
