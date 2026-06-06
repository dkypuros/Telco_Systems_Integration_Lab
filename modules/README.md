# Visual/service modules

`modules/` contains optional local visual and service modules that sit on top of
lab runtime/evidence surfaces. They are intentionally separate from core
`services/` so examples can be added without changing the telco runtime itself.

The main module index is [`index.json`](index.json). It reserves local ports so
future harness work can check which module endpoints are already claimed before
adding another example.

Current example:

| Module | Port | Purpose |
| --- | ---: | --- |
| [`dashboard_service/`](dashboard_service/) | `8764` | Card dashboard for registered modules and activation status. |
| [`lab_chatter_service/`](lab_chatter_service/) | `8765` | Local web/API viewer for `./lab chatter` service logs. |

Boundaries:

- Modules are local developer/operator surfaces, not production service discovery.
- Module ports must be registered in `modules/index.json` before use.
- Modules should avoid new dependencies unless an issue explicitly approves them.
- Modules must preserve the repo's public-safe evidence and claim boundaries.


## Required module README sections

Every module must include a `README.md` with these sections so operators and
future harness agents know how to run it safely:

- `Dependencies` — lab state, services, commands, ports, and optional tools the module needs.
- `Run` — exact local command to start the module.
- `Stop` — how to stop the module and whether `./lab down` is also needed.
- `Special commands` — any scenario, smoke, report, or refresh commands that make the module useful.
- `Boundary` — what the module does not claim or control.

Most visual modules should depend on the normal lab lifecycle:

```bash
./lab up
# run module-specific command
./lab down
```
