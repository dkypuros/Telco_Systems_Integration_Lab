# Modules Dashboard

Local no-dependency dashboard for the module ecosystem. It reads
`modules/index.json`, renders cards for registered modules, detects whether each
module's registered localhost port is active, links active modules in a new
tab, and can activate registered module entrypoints.

## Dependencies

Required:

- Python 3 from the local development environment.
- Repository root as the working directory.
- Registered module port `8764` from `modules/index.json`.
- A valid `modules/index.json` where each module has a `module.json` file.
- Write access to `.lab/state/` and `build_logs/modules/` when using Activate/Stop.

Optional lab lifecycle:

```bash
./lab up
python3 modules/dashboard_service/server.py
# start any module you want to view, such as the chatter service
./lab down
```

The dashboard does not require `./lab up` to render module cards, but runtime
modules such as the chatter service are more useful after the lab is up.

## Run

From the repository root:

```bash
python3 modules/dashboard_service/server.py
```

Then open:

```text
http://127.0.0.1:8764/
```

Useful JSON endpoints:

```text
http://127.0.0.1:8764/api/module
http://127.0.0.1:8764/api/modules
http://127.0.0.1:8764/api/ports
POST http://127.0.0.1:8764/api/modules/{module_id}/activate
POST http://127.0.0.1:8764/api/modules/{module_id}/stop
```

Optional host/port override:

```bash
python3 modules/dashboard_service/server.py --host 127.0.0.1 --port 8764
```

## Stop

Press `Ctrl-C` in the terminal running the dashboard.

This module does not own the telco services. Use the normal lab lifecycle to stop
the runtime services when finished:

```bash
./lab down
```

## Special commands

Start the dashboard and use it to activate the base lab runtime plus other modules, or start another module manually in a separate terminal:

```bash
python3 modules/dashboard_service/server.py
# click Activate on Lab Runtime, then on Lab Chatter Service
python3 modules/lab_chatter_service/server.py
```

Use the dashboard card Activate button to start a registered module. For the Lab Runtime card, Activate runs `./lab up` and Stop runs `./lab down`. The
chatter card should show an activated green chiclet and open the chatter service
in a new tab. If the dashboard started the module, a Stop button is also shown.

## Boundary

Activation means a registered localhost port accepted a TCP connection. The
Activate button starts only entrypoints listed in `modules/index.json`, without
shell execution. Stop only targets PIDs recorded by this dashboard under
`.lab/state/`; it must not kill arbitrary processes already listening on a port.
Activation does not prove module health, production readiness, or formal
standards conformance. The dashboard is navigation and discovery glue for local
modules only.
