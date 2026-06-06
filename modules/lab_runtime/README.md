# Lab Runtime

Base lifecycle module for the Telco Systems Integration Lab runtime. This module
represents the normal `./lab up` / `./lab down` process inside the modules
dashboard so other visual modules can depend on the lab being active.

## Dependencies

Required:

- Python 3 from the local development environment.
- Repository root as the working directory.
- The root [`lab`](../../lab) command.
- Write access to `.lab/state/` and `build_logs/` for normal lab runtime state
  and evidence.

Normal lifecycle:

```bash
./lab up
# run module-specific command or activate modules from the dashboard
./lab down
```

## Run

From the repository root, use the dashboard Activate button or run:

```bash
./lab up
```

Status command:

```bash
./lab services --json
```

## Stop

Use the dashboard Stop button or run:

```bash
./lab down
```

## Special commands

Useful commands after the runtime is active:

```bash
./lab services
./lab chatter all --follow
./lab scenario pdu-session
./lab scenario radio
./lab demo
```

## Boundary

This module does not replace the `./lab` CLI. It only exposes the fixed lab
lifecycle commands through the dashboard. Runtime readiness is local demo
readiness only; it is not production readiness and not formal 3GPP, O-RAN, or
TM Forum conformance.
