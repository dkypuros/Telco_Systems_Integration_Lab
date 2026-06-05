# PRD: Lab Runnable Experience

## Objective
Make the Telco Systems Integration Lab immediately usable with one obvious command surface while preserving traceability, copy identity, and claim hygiene.

## Requirements
1. Provide an executable `./lab` command at the lab root.
2. Support `./lab up` to create/use a disposable runtime venv, install `config/requirements.txt`, run runtime smoke, and write evidence.
3. Support `./lab test` to run `pytest -q tests` in the disposable runtime venv and write evidence.
4. Support `./lab status` to summarize latest runtime/test evidence and key caveats.
5. Support `./lab demo` to produce a concise human-readable readiness/demo summary.
6. Do not edit copied source files.
7. Preserve explicit caveat that smoke/tests are not formal conformance proof.
8. Add/adjust tests for the command surface.

## Non-goals
- No daemon orchestration yet.
- No production service launch.
- No formal conformance testing.
- No full BF3 source copy in this task.
