# AI Observer

Telemetry-driven active control plane for the Tech-Co 5G lab.

**Port:** 8090
**Framework:** FastAPI (Python, async)
**Persistence:** In-memory ring buffer (`ObservationStore`, deque-backed)
**Source root:** `src/ai_observer/`
**Version:** 0.2.0 (Phase 2)

---

## Purpose

The AI observer continuously collects telemetry from the order engine and the legacy standalone 5G
network functions, runs analyzers to detect failure and latency patterns, and (in
Phase 2) proposes or executes remediation actions via a safety-gated `ActionEngine`.

Phase 1 (stage 10) established passive observation: collectors poll, analyzers fire
alerts, data is surfaced via REST. Phase 2 (stage 17) added the `ActionEngine` with
three actuators and three safety gates. Auto-execute is OFF by default.

---

## Endpoints

All routes are served on port 8090.

### Health and root

| Method | Path    | Description                                                        |
|--------|---------|--------------------------------------------------------------------|
| GET    | /health | Returns status, version, phase=2, and current auto-execute setting |
| GET    | /       | Service root with full endpoint index                              |

### Observations (`app/api/observations.py`)

| Method | Path                    | Description                                                                      |
|--------|-------------------------|----------------------------------------------------------------------------------|
| GET    | /observations           | List recent observations. `?type=` filter, `?limit=` (1-500, default 50).       |
| GET    | /observations/{type}    | Shortcut: filter by observation type directly in the path. `?limit=`             |
| GET    | /alerts                 | List recent alerts. `?limit=` (1-200, default 50).                               |
| GET    | /summary                | Aggregate: observation types, latest value per type, recent alert count.         |

### Actions (`app/api/actions.py`)

| Method | Path                         | Description                                                                 |
|--------|------------------------------|-----------------------------------------------------------------------------|
| GET    | /proposed-actions            | List all pending (and previously pending) action proposals from ActionEngine.|
| GET    | /actions                     | List all executed actions from ActionEngine.                                 |
| POST   | /actions/{id}/approve        | Manually approve a pending proposal by ID. Triggers async execution.        |
| GET    | /auto-execute                | Return current auto-execute mode (true/false).                              |
| PATCH  | /auto-execute                | Toggle auto-execute. Body: `{"enabled": true}` or `{"enabled": false}`.    |

---

## Architecture

```
src/ai_observer/app/
  main.py                     FastAPI app, CORS, lifespan (starts collectors/analyzers/engine)
  collectors/
    base.py                   TelemetryCollector ABC: start(), stop(), collect()
    order_engine_collector.py Polls TMF622 /productOrder, emits "order_stats" observations
    legacy_5g_emulator_nf_collector.py       Polls legacy standalone 5G emulator NF /health endpoints, emits "nf_health" observations
    otel_log_collector.py     Scans OTel log outputs, emits "otel_log" observations (6x interval)
  analyzers/
    base.py                   BaseAnalyzer ABC
    order_failure_analyzer.py Fires "order_failure" alerts when failed_count exceeds threshold
    latency_analyzer.py       Fires "nf_latency" alerts when p99 latency exceeds threshold
  actuators/
    base.py                   Actuator ABC + ActionPlan + ActionResult Pydantic models
    order_retry_actuator.py   Posts retry order to order engine on order_failure alerts
    nf_restart_actuator.py    Dry-run only: logs "would restart NF" -- never actually restarts
    playbook_actuator.py      Runs diagnose_nf playbook (GET /health + GET /docs) on latency alerts
  control/
    action_engine.py          ActionEngine: 3-gate safety + proposal/execution lifecycle
  api/
    observations.py           /observations, /alerts, /summary routes
    actions.py                /proposed-actions, /actions, /approve, /auto-execute routes
  storage/
    observation_store.py      ObservationStore: deque ring buffer, 500 obs / 200 alerts
```

---

## Collectors

Three collectors run as asyncio background tasks, polling at `POLL_INTERVAL_SECONDS`
intervals (default: 5s). The OTel log collector runs at 6x the base interval (30s by
default) because log scans are more expensive.

| Collector                | Source polled                              | Observation type  |
|--------------------------|--------------------------------------------|-------------------|
| `OrderEngineCollector`   | TMF622 GET /productOrder                   | `order_stats`     |
| `legacy standalone 5G emulatorNfCollector`         | legacy standalone 5G emulator NF /health endpoints (AMF, SMF, UDR, UDM, NSSF) | `nf_health` |
| `OtelLogCollector`       | OTel log outputs from the lab              | `otel_log`        |

`OrderEngineCollector` (`app/collectors/order_engine_collector.py`) tracks state counts
per cycle and maintains a rolling 60-second window to compute an orders/minute rate.
When the order engine is unreachable it emits an `order_stats` observation with
`"error": "upstream_unavailable"`.

---

## Analyzers

Two analyzers also run as asyncio background tasks at `POLL_INTERVAL_SECONDS` intervals.
Analyzers read from `ObservationStore` and call `store.add_alert()` when thresholds are
exceeded.

| Analyzer                 | Watches            | Alert source           | Fires when                              |
|--------------------------|--------------------|------------------------|-----------------------------------------|
| `OrderFailureAnalyzer`   | `order_stats` obs  | `OrderFailureAnalyzer` | `failed_count` exceeds configured threshold |
| `LatencyAnalyzer`        | `nf_health` obs    | `LatencyAnalyzer`      | NF p99 latency exceeds threshold (ms)   |

---

## Actuators

Three actuators are registered with the `ActionEngine` at startup (`app/main.py`
lines 66-73).

### OrderRetryActuator (`app/actuators/order_retry_actuator.py`)

- Responds to alerts from `OrderFailureAnalyzer`.
- Confidence: **0.85** (above the 0.7 threshold, eligible for auto-execute if enabled).
- Execute: POSTs a synthetic retry `ProductOrder` to the order engine at
  `{ORDER_ENGINE_URL}/tmf-api/productOrderingManagement/v4/productOrder`.
- Idempotency guard: tracks `_retried_orders` set per process lifetime; skips if
  the same `order_id` has already been retried.

### NfRestartActuator (`app/actuators/nf_restart_actuator.py`)

- Responds to alerts from `LatencyAnalyzer`.
- Confidence: **0.65** (below the 0.7 default threshold).
- **Execute always returns `success=False`** with `"dry_run": True`. No NF is ever
  actually restarted in Phase 2. The low confidence (0.65) ensures this actuator
  never auto-executes even if `AI_AUTO_EXECUTE=true` is set, because it will not
  pass Gate 1 (confidence threshold). The docstring at the top of the file states
  this explicitly: "NEVER actually restarts anything."
- Rationale: NF restarts are high-impact destructive operations. Real restart
  capability is deferred to Phase 3.

### PlaybookActuator (`app/actuators/playbook_actuator.py`)

- Responds to alerts from `LatencyAnalyzer` when `alert.details["nf"]` is present.
- Confidence: **0.80** (above threshold, eligible for auto-execute if enabled).
- Execute: runs the `diagnose_nf` playbook: `GET /health` then `GET /docs` against
  the affected NF's base URL. Returns structured step results. No mutations occur;
  this is a diagnostic-only runbook.
- Pattern mirrors `Tech-Co/external/ericsson_secops_orchestrator/telco_playbook.py`.
  The future direction is to add playbook steps that call Ansible Automation Platform
  for real remediation.

---

## ActionEngine (`app/control/action_engine.py`)

Module-level singleton: `engine = ActionEngine(actuators=[])` (line 274). Actuators
are wired in at startup in `main.py`.

The engine polls `ObservationStore` for new alerts every `poll_interval_seconds`.
For each new alert it iterates registered actuators that `can_act(alert)` and applies
three safety gates in order:

### Gate 1: Confidence threshold

Default: **0.70** (overridable via `ACTION_CONFIDENCE_THRESHOLD` env var). Plans below
the threshold are recorded as `proposed_action` with `reason: "low_confidence"` and
never executed automatically.

### Gate 2: Dedupe window

**60 seconds**. If the same `(actuator_name, action_type, alert_source)` triple was
acted on within the last 60 seconds, the current alert is silently suppressed. Prevents
rapid-fire repeated actions on a sustained failure condition.

### Gate 3: Auto-execute flag

Default: **OFF** (`AI_AUTO_EXECUTE=false`). When OFF, all plans that pass Gates 1 and 2
are recorded as `proposed_action` with `reason: "auto_execute_off"` and appear at
`GET /proposed-actions`. When ON, the plan is executed immediately and recorded at
`GET /actions`.

The flag is checked at call time via `os.getenv("AI_AUTO_EXECUTE", "false")`, so
`PATCH /auto-execute {"enabled": true}` takes effect on the next evaluation cycle
without restarting the service.

### Manual approval

`POST /actions/{id}/approve` flips a pending proposal to `approved` status and
schedules `_execute_approved()` via `asyncio.create_task()`. This path bypasses
Gate 3 (auto-execute) but not Gates 1 or 2 (the plan was already evaluated against
those when it was first proposed).

---

## ObservationStore (`app/storage/observation_store.py`)

Ring buffer backed by `collections.deque`:

- Max **500 observations** (`deque(maxlen=500)`)
- Max **200 alerts** (`deque(maxlen=200)`)

`Observation` fields: `id`, `ts` (UTC), `source`, `type`, `data` (dict).
`Alert` fields: `id`, `ts`, `severity` (`warning` | `critical`), `source`, `message`, `details`.

`store.observation_types()` returns the set of distinct `type` values currently in the
buffer. Used by `GET /summary` to enumerate active data streams.

Module-level singleton: `store = ObservationStore()` at line 84.

---

## Phase Progression

| Phase   | Stage | Behavior                                              |
|---------|-------|-------------------------------------------------------|
| Phase 1 | 10    | Passive: collectors poll, analyzers fire alerts, REST surfaces data |
| Phase 2 | 17    | Active: ActionEngine with 3 actuators, 3 safety gates, auto-execute OFF by default |
| Phase 3 | (future) | Wire `NfRestartActuator` to call `start_3gpp_services.sh` for a single NF, raise confidence threshold, demonstrate closed-loop remediation |

---

## Tests

**37/37 pytest pass**. Run from `src/ai_observer/`:

```bash
cd src/ai_observer
source .venv/bin/activate   # or activate the venv if created
pytest
```

---

## Environment Variables

| Variable                    | Default                                          | Description                                              |
|-----------------------------|--------------------------------------------------|----------------------------------------------------------|
| `ORDER_ENGINE_URL`          | `http://localhost:8080`                          | Order engine base URL (used by collector and retry actuator) |
| `legacy standalone 5G emulator_NRF_URL`               | `http://localhost:9000`                          | legacy standalone 5G emulator NRF URL for NF discovery (used by legacy_5g_emulator_nf_collector)  |
| `POLL_INTERVAL_SECONDS`     | `5`                                              | Base poll interval for collectors and analyzers          |
| `AI_AUTO_EXECUTE`           | `false`                                          | Enable automatic action execution (`true` / `false`)     |
| `ACTION_CONFIDENCE_THRESHOLD` | `0.7`                                          | Minimum confidence for a plan to pass Gate 1             |
| `AI_OBSERVER_CORS_ORIGINS`  | `http://localhost:8095,http://127.0.0.1:8095`   | Comma-separated allowed CORS origins                     |

---

## Running Standalone

```bash
cd src/ai_observer
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --port 8090 --reload
```

Interactive docs: http://localhost:8090/docs

---

## Integration with Ericsson Playbook Orchestrator

`PlaybookActuator` mirrors the pattern established in
`Tech-Co/external/ericsson_secops_orchestrator/telco_playbook.py`. Each playbook is a
named dict of steps that produce structured evidence without mutating NF state. The
current `diagnose_nf` playbook (`GET /health`, `GET /docs`) is diagnostic only.

The intended Phase 3 direction is to add playbook steps that call Ansible Automation
Platform (AAP) via its REST API, enabling the observer to trigger real remediation
runbooks in the same way Ericsson's SecOps orchestrator calls Ansible for network
security responses.

---

## Phase 3 Roadmap

To complete the closed-loop remediation loop:

1. In `NfRestartActuator.execute()`, replace the dry-run log with a call to
   `start_3gpp_services.sh` (already present in the lab scripts) for a single NF.
   Target a low-impact NF (e.g., NSSF) first.
2. Raise `CONFIDENCE = 0.65` to above the `ACTION_CONFIDENCE_THRESHOLD` (0.7) so the
   actuator can pass Gate 1.
3. Set `AI_AUTO_EXECUTE=true` in a controlled test environment.
4. Observe the full cycle: LatencyAnalyzer alert -> NfRestartActuator proposes ->
   Gate passes -> NF restarts -> LatencyAnalyzer clears alert.
