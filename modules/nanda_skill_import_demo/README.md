# NANDA Skill Import Demo

Local no-dependency browser module that makes the NANDA/Harness idea visible. It runs the deterministic offline simulator from `experimental/nanda_harness_commerce/` and renders the control-plane flow:

```text
human intent -> NANDA-style discovery -> AgentFacts-like verification -> harness governance gate -> disabled skill import -> human approval required
```

## Dependencies

Required:

- Python 3 from the local development environment.
- Repository root as the working directory.
- Registered module port `8768` from `modules/index.json`.
- Existing offline experiment files:
  - `experimental/nanda_harness_commerce/simulator.py`
  - `experimental/nanda_harness_commerce/fixtures/intent.json`
  - `experimental/nanda_harness_commerce/fixtures/nanda_index.json`
  - `experimental/nanda_harness_commerce/fixtures/harness_policy.json`

Recommended module stack:

```bash
./lab up
python3 modules/dashboard_service/server.py
python3 modules/nanda_skill_import_demo/server.py
./lab down
```

This module does not require live NANDA services, live telco services, remote agents, credentials, containers, or payment rails.

## Run

From the repository root:

```bash
python3 modules/nanda_skill_import_demo/server.py
```

Then open:

```text
http://127.0.0.1:8768/
```

Useful JSON endpoints:

```text
http://127.0.0.1:8768/api/module
http://127.0.0.1:8768/api/ports
http://127.0.0.1:8768/api/demo-plan
POST http://127.0.0.1:8768/api/run-demo
```

Optional host/port override:

```bash
python3 modules/nanda_skill_import_demo/server.py --host 127.0.0.1 --port 8768
```

## Stop

Press `Ctrl-C` in the terminal running the module, or use the Modules Dashboard Stop button if the dashboard started it.

This module does not own the telco services. Use the normal lab lifecycle to stop runtime services when finished:

```bash
./lab down
```

## Special commands

Run the simulator directly to compare the module output with the CLI artifact:

```bash
python3 experimental/nanda_harness_commerce/simulator.py \
  --intent experimental/nanda_harness_commerce/fixtures/intent.json \
  --index experimental/nanda_harness_commerce/fixtures/nanda_index.json \
  --policy experimental/nanda_harness_commerce/fixtures/harness_policy.json
```

Use with the module dashboard:

```bash
python3 modules/dashboard_service/server.py
# activate NANDA Skill Import Demo from the dashboard
```

## Boundary

This module is a local offline NANDA-style skill import demo. It can show the harness reading a human intent, evaluating AgentFacts-like records, rejecting unsafe candidates, and preparing one disabled skill import that remains in `awaiting_human_approval` state.

It does **not** prove live NANDA interoperability, live NANDA Index lookup, real cryptographic signature verification, payment settlement, remote skill execution, production authorization, production security posture, formal O-RAN behavior, or formal standards conformance.
