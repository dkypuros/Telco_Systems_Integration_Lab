# Local Visual and Service Modules

Modules are optional localhost surfaces that make the lab easier to observe,
demonstrate, and extend without changing the core telco runtime. They are the
right place for lightweight dashboards, report viewers, scenario launchers, and
other visual examples that sit on top of `./lab`, `build_logs/`, and the
repository's traceability surfaces.

The module system is intentionally small:

- the canonical registry is [`modules/index.json`](../modules/index.json);
- module source lives under [`modules/`](../modules/);
- every module owns its own `README.md` and `module.json`;
- localhost ports are reserved before a module is added;
- activation is local developer/operator convenience, not production service
  discovery.

## Current module stack

| Module | Port | Role |
| --- | ---: | --- |
| [`lab_runtime`](../modules/lab_runtime/) | n/a | Base lifecycle card for `./lab up`, `./lab services --json`, and `./lab down`. |
| [`dashboard_service`](../modules/dashboard_service/) | `8764` | Module card dashboard for discovery, activation, stop, and navigation. |
| [`ue_scenario_generator`](../modules/ue_scenario_generator/) | `8766` | Fixed scenario buttons that generate UE/session/RAN/O-RAN lab activity. |
| [`lab_chatter_service`](../modules/lab_chatter_service/) | `8765` | Browser/API view over `./lab chatter` service logs. |

The first useful visual loop is:

```bash
python3 modules/dashboard_service/server.py
```

Then open:

```text
http://127.0.0.1:8764/
```

From the dashboard:

1. Activate **Lab Runtime**.
2. Activate **UE / Scenario Generator**.
3. Activate **Lab Chatter Service**.
4. Open the UE generator and run a scenario.
5. Open the chatter service to watch the resulting service transcript.

Manual equivalent:

```bash
./lab up
python3 modules/ue_scenario_generator/server.py
python3 modules/lab_chatter_service/server.py
./lab down
```

## What modules are for

Use modules for:

- local HTML/API views over existing lab evidence;
- scenario buttons that call fixed, repository-owned commands;
- report viewers that map code, specs, tests, and evidence;
- small dashboards that help operators navigate the lab;
- examples other people can copy to build their own visual surfaces.

Do not use modules for:

- production service discovery;
- arbitrary shell execution;
- hidden runtime state outside `.lab/state/` or `build_logs/`;
- stronger conformance claims than the underlying evidence supports;
- vendoring external telco projects into this repository.

## Registry contract

Before adding a module, reserve its identity and port in
[`modules/index.json`](../modules/index.json). A module entry should describe:

- stable `id`;
- human-readable `name`;
- relative `path`;
- `default_port` when it exposes HTTP locally;
- fixed `entrypoint`;
- `surface`, such as `local_http` or `lab_lifecycle`;
- dependencies and recommended companion modules.

Port registration lets the dashboard, future harness agents, and module authors
avoid accidental collisions.

## Required module files

Each module should include:

```text
modules/<module_name>/
├── README.md
├── module.json
└── server.py or equivalent local entrypoint
```

The module README must document:

- `Dependencies` — lab state, commands, ports, and optional tools;
- `Run` — exact local command;
- `Stop` — how to stop the module and whether `./lab down` is also needed;
- `Special commands` — scenarios, reports, smoke tests, or refresh commands;
- `Boundary` — what the module does not control or prove.

## Activation model

The dashboard starts only registered module entrypoints from
[`modules/index.json`](../modules/index.json). It does not accept arbitrary shell
commands.

For normal HTTP modules:

- activation starts the registered entrypoint;
- readiness means the registered localhost port accepts a connection;
- stop only targets the PID recorded by the dashboard.

For the Lab Runtime module:

- activation runs `./lab up`;
- stop runs `./lab down`;
- status is derived from `./lab services --json`.

## Claim boundary

Modules are local operator/reviewer surfaces. They can make evidence easier to
see and demos easier to run, but they do not create formal 3GPP, O-RAN, or TM
Forum conformance by themselves. Any stronger claim must point to the underlying
tests, traceability records, evidence bundles, and claim gates.

