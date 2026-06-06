# UE / Scenario Generator

Local no-dependency module that generates lab activity by running fixed
`./lab scenario ...` commands. It is meant to pair with the Lab Chatter Service:
this module creates UE/session/RAN events, and the chatter module visualizes the
resulting service log lines.

## Dependencies

Required:

- Python 3 from the local development environment.
- Repository root as the working directory.
- Lab Runtime module / `./lab up` before scenarios are useful.
- Registered module port `8766` from `modules/index.json`.

Recommended module stack:

```bash
./lab up
python3 modules/ue_scenario_generator/server.py
python3 modules/lab_chatter_service/server.py
./lab down
```

The module can be activated from the Modules Dashboard after Lab Runtime is
active.

## Run

From the repository root:

```bash
python3 modules/ue_scenario_generator/server.py
```

Then open:

```text
http://127.0.0.1:8766/
```

Useful JSON endpoints:

```text
http://127.0.0.1:8766/api/module
http://127.0.0.1:8766/api/scenarios
POST http://127.0.0.1:8766/api/scenarios/pdu-session
POST http://127.0.0.1:8766/api/scenarios/radio
POST http://127.0.0.1:8766/api/scenarios/all
```

## Stop

Press `Ctrl-C` in the terminal running the module, or use the Modules Dashboard
Stop button if the dashboard started it.

This module does not own the telco services. Use the normal lab lifecycle to stop
the runtime services when finished:

```bash
./lab down
```

## Special commands

The module exposes fixed buttons for:

```bash
./lab scenario pdu-session
./lab scenario radio
./lab scenario oran-overview
./lab scenario cu-du
./lab scenario all
```

Use the Lab Chatter Service at `http://127.0.0.1:8765/` to watch the resulting
`SCENARIO` transcript lines.

## Boundary

This module runs only fixed, registered `./lab scenario` commands. It does not
accept arbitrary shell commands, does not emulate a production UE by itself, and
does not claim formal 3GPP, O-RAN, or TM Forum conformance. Future issues may
profile external UE/RAN emulator options such as free5GC's `ueRanEmulator`, OAI
NR UE simulator assets, or UERANSIM as separate external profiles.
