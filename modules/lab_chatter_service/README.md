# Lab Chatter Service

Local no-dependency visual/API module for the same service-log surface used by:

```bash
./lab chatter all --follow
```

It gives operators and reviewers a localhost endpoint without changing the lab
runtime or importing a frontend framework.

## Dependencies

Required:

- Python 3 from the local development environment.
- Repository root as the working directory.
- Registered module port `8765` from `modules/index.json`.

Recommended lab lifecycle:

```bash
./lab up
python3 modules/lab_chatter_service/server.py
# in another terminal, run scenarios or inspect the browser view
./lab down
```

Data surfaces read by this module:

- `build_logs/services/*.log` — lab-owned service chatter logs.
- `.lab/state/lab_services.json` — runtime state when present.
- `build_logs/lab_services.json` — operator evidence copy when present.

The module still runs if the lab is down, but the chatter view may be empty until
`./lab up` or `./lab scenario <name>` produces logs.

## Run

From the repository root:

```bash
python3 modules/lab_chatter_service/server.py
```

Then open:

```text
http://127.0.0.1:8765/
```

Useful JSON endpoints:

```text
http://127.0.0.1:8765/api/module
http://127.0.0.1:8765/api/ports
http://127.0.0.1:8765/api/chatter?group=all&lines=80
http://127.0.0.1:8765/api/chatter?group=core&lines=40
http://127.0.0.1:8765/api/chatter?group=ran&lines=40
http://127.0.0.1:8765/api/chatter?group=oran&lines=40
```

Optional host/port override:

```bash
python3 modules/lab_chatter_service/server.py --host 127.0.0.1 --port 8765
```

## Stop

Press `Ctrl-C` in the terminal running the module.

This module does not own the telco services. Use the normal lab lifecycle to stop
the runtime services when finished:

```bash
./lab down
```

## Special commands

Generate useful chatter in another terminal:

```bash
./lab services
./lab scenario pdu-session
./lab scenario radio
./lab chatter all --follow
```

The web module is meant to mirror and visualize the `./lab chatter` surface; the
CLI command remains the source behavior.

## Boundary

This module is a local operator/reviewer view over curated lab logs. It does not
start or stop telco services, does not mutate network state, and does not
strengthen any standards-conformance claim.
