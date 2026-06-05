# Quickstart

## Start the lab services

From this lab root:

```bash
cd <USER_HOME>/Documents/Git_Offline/active/9.LABS_Telco_Systems_Integration_Lab

./lab up
./lab services
```

What happens:

- Starts the BF3 5G core, RAN, O-RAN enhancement, NTN radio, and gateway services in the background.
- Avoids the original macOS-fragile `psutil` port-kill path.
- Starts a cold lab-owned core in dependency order: `NRF -> UPF -> SMF -> AMF`, then the remaining services.
- Tracks only lab-owned PIDs in `.lab/state/lab_services.json` and mirrors operator evidence to `build_logs/lab_services.json`.
- Writes logs under `build_logs/services/`.
- Leaves external/untracked processes alone.
- Shows external/untracked listener PIDs with a `*`; `./lab down` will not kill those.

Dry-run the exact commands without starting anything:

```bash
./lab up --dry-run
```

## See the service chatter

Keep `./lab up` as the stable background launcher, then use a second terminal for the old foreground-style stream:

```bash
./lab chatter core              # recent AMF/SMF/UPF/NRF logs
./lab chatter all --follow      # live merged tail; Ctrl-C to stop
./lab chatter radio --lines 80  # NTN radio/PHY-style trace lines
```

Trigger chatter on demand:

```bash
./lab scenario pdu-session      # AMF -> SMF -> UPF, then simulated UPF traffic
./lab scenario radio --count 3  # NTN satellite delay/Doppler/MAC/RRC/PHY ticks
./lab scenario cu-du            # CU calls DU
./lab scenario oran-overview    # gateway probes the O-RAN overview
./lab scenario all              # run the demo triggers together
```

Dry-run a scenario before it calls services:

```bash
./lab scenario pdu-session --dry-run
```

Note: if `./lab services` shows a PID with `*`, that service is external/untracked and its original stdout may be in another terminal. `./lab scenario` still appends clearly labeled `SCENARIO` request/response transcript lines into the relevant logs so `./lab chatter` can show the operator-triggered back-and-forth.

Restart tracked services cleanly:

```bash
./lab up --replace
```

Stop tracked services:

```bash
./lab down
```

## Useful checks

```bash
./lab services
./lab services --json
curl http://localhost:8000/health    # NRF
curl http://localhost:9000/health    # AMF
curl http://localhost:9001/health    # SMF
curl http://localhost:9002/health    # UPF
curl http://localhost:8088/health    # O-RAN gateway
curl http://localhost:8088/api/oran/overview
```

## Test/readiness loop

```bash
./lab smoke   # non-daemon import/AST smoke for copied mock services
./lab test    # pytest suite
./lab status  # combined evidence summary
./lab demo    # demo-readiness wording
```

## Claim boundary

This lab command surface is for local runtime/demo readiness and repeatable evidence. It does **not** claim formal 3GPP, O-RAN, or TM Forum conformance.
