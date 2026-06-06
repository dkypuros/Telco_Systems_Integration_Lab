# Stage 1 Verification — legacy standalone 5G Core on macOS Darwin 24.5.0

**Date**: 2026-05-18
**Verifier**: Claude Code (Executor agent)
**Code location**: `components/legacy-standalone-5g-emulator/open-digital-platform-2_0/clean_5g_emulator_api/`
**Python**: 3.14.4 (Homebrew arm64)

---

## What I Did

Commands run in order:

1. Read `main.py`, `requirements.txt`, `start_3gpp_services.sh` to understand entry points and dependencies.
2. Inspected `core_network/nrf.py`, `amf.py`, `smf.py`, `upf.py`, `ptp/ptp.py`, `ran/rru/rru.py`, `service_assurance/assurance_api.py`, `ran/cu/cu.py` for structure and import patterns.
3. Created a fresh venv: `python3 -m venv venv_verify` inside `clean_5g_emulator_api/`.
4. Installed all requirements: `pip install -r requirements.txt` — succeeded (thrift built from source, all packages installed cleanly on Python 3.14.4).
5. Tested NRF standalone: `python core_network/nrf.py --host 0.0.0.0 --port 8000` — confirmed `/health` returned 200.
6. Attempted `python main.py` — crashed immediately (see "What failed" section).
7. Bypassed `main.py` and launched NFs directly in dependency order:
   - NRF (8000) started first, 4s sleep
   - AMF (9000), SMF (9001), UPF (9002), AUSF (9003), UDM (9004), UDR (9005), UDSF (9006) started together
   - CU (9008), DU (9007), RRU (9009), service_assurance (9011) started as second wave
   - `service_assurance` launched as `python -m service_assurance.assurance_api` (module mode, required for relative imports)
8. Probed all ports with `curl` after 10s startup window.
9. Discovered SMF had cached `upf_url = None` (race condition — UPF wasn't registered when SMF started).
10. Restarted SMF after UPF was confirmed registered in NRF.
11. Ran `test_3gpp_compliance.py` — 6/6 passed.
12. Killed all spawned processes; verified all ports clear.

---

## What Worked

- **pip install**: All 47 packages installed cleanly on Python 3.14.4 arm64. Thrift built from source without error.
- **NRF (port 8000)**: Starts and serves `/health`, `/discover/{nf_type}`, `/register`. OAuth2-protected 3GPP endpoints also present. Returned healthy with 3 registered NFs after core startup.
- **AMF (port 9000)**: Starts cleanly, registers with NRF, serves `/metrics`, `/amf/ue/{ue_id}`, `/amf/pdu-session/create`.
- **SMF (port 9001)**: Starts, registers with NRF, discovers UPF (when UPF is already registered), handles `POST /nsmf-pdusession/v1/sm-contexts`.
- **UPF (port 9002)**: Starts, registers with NRF, serves `/upf_service`, `/upf/forwarding-rules`, `/upf/simulate-traffic`.
- **AUSF (port 9003)**: Starts cleanly, serves `/nausf-auth/v1/ue-authentications`.
- **UDM (port 9004)**: Starts cleanly.
- **UDR (port 9005)**: Starts cleanly.
- **UDSF (port 9006)**: Starts cleanly (SQLite-backed).
- **CU (port 9008)**: Starts, serves HTTP. NRF registration fails (see below) but HTTP layer is functional.
- **DU (port 9007)**: Starts, serves HTTP. Same NRF registration issue.
- **service_assurance (port 9011)**: Starts as module, registers KQI/SLA/anomaly monitoring, serves REST API.
- **3GPP compliance test**: **6/6 tests passed, 100% pass rate.** Full PDU session establishment chain (AMF -> SMF N11 -> UPF N4 PFCP) working end-to-end.

---

## What Failed and Why

### Failure 1 — `main.py` crashes on launch (BLOCKING)

**Error**:
```
psutil.AccessDenied: (pid=81869)
  File "main.py", line 26, in kill_process_on_port
    for conn in psutil.net_connections():
```

**Root cause**: `main.py`'s `kill_process_on_port()` calls `psutil.net_connections()` which on macOS 14/15 iterates all PIDs' file descriptors. This requires `proc_pidinfo(PROC_PIDLISTFDS)` on other processes, which is blocked by macOS SIP/process privacy restrictions for non-root users. The call raises `AccessDenied` before a single NF is spawned.

**Impact**: `main.py` is completely non-functional as the primary launch method on macOS without `sudo`. The NFs themselves are fine — this is purely an orchestration-layer bug.

**Affected file**: `main.py` lines 25-35 (`kill_process_on_port` function).

---

### Failure 2 — SMF fails PDU session if started before UPF registers (race condition)

**Error** (SMF log):
```
ERROR - UPF discovery failed: UPF not found
ERROR - UPF URL not available - service discovery failed
POST /nsmf-pdusession/v1/sm-contexts HTTP/1.1 502 Bad Gateway
```

**Root cause**: `smf.py` discovers UPF once at startup via `GET /discover/UPF`. If UPF hasn't registered with NRF yet, `upf_url` is set to `None` and never retried. Subsequent PDU session requests immediately return 502. This is a startup-ordering race condition — there is no retry or lazy discovery.

**Impact**: PDU session establishment fails if SMF starts before or simultaneously with UPF.

---

### Failure 3 — CU, DU, SERVICE_ASSURANCE cannot register with NRF

**Error** (NRF log):
```
ERROR - Legacy registration failed: 'CU' is not a valid NFType
ERROR - Legacy registration failed: 'DU' is not a valid NFType
ERROR - Legacy registration failed: 'SERVICE_ASSURANCE' is not a valid NFType
POST /register HTTP/1.1 500 Internal Server Error
```

**Root cause**: NRF's `NFType` enum (`nrf.py` line 39) follows strict 3GPP TS 29.510 and only includes 3GPP-defined NF types (`AMF`, `SMF`, `UPF`, `NRF`, `AUSF`, `UDM`, `UDR`, `GNODEB`, etc.). The RAN split components (`CU`, `DU`) and `SERVICE_ASSURANCE` are simulation-specific types not in the 3GPP enum. NRF rejects them.

**Impact**: CU, DU, and service_assurance run and serve HTTP correctly but are not discoverable via NRF. This is a simulation completeness gap, not a functional failure for the 5G core compliance tests.

---

### Failure 4 — RRU (port 9009) is a stub with no HTTP server

**Root cause**: `ran/rru/rru.py` contains only a `while True: time.sleep(60)` loop with no FastAPI app and no port binding. `main.py` passes `--host`/`--port` args to it but rru.py ignores them. Port 9009 never responds.

**Impact**: RRU is not a functional component — it is a placeholder. No HTTP endpoint, no NRF registration.

---

### Failure 5 — ptp.py is also a stub

**Root cause**: `ptp/ptp.py` is `while True: time.sleep(60)`. No HTTP server. `main.py` would pass `--host 0.0.0.0 --port 9010` to it; args are ignored.

**Impact**: No PTP service on port 9010. PTP synchronization is simulated only by print statements.

---

### Failure 6 — `main.py` blocking `process.wait()` design

**Root cause**: `main.py` calls `process.wait()` for each process in sequence at lines 104-106. The first process (NRF, which runs indefinitely) will block forever before AMF's `wait()` is ever called. This means `main.py` would hang on NRF even if the `psutil` issue were fixed.

**Impact**: `main.py` cannot be used to orchestrate a multi-NF start as written. The correct pattern would be to wait for all processes with `process.wait()` in parallel or catch `KeyboardInterrupt`.

---

## Recommended Fix

### Fix 1 — main.py psutil crash (required to use main.py at all)

Replace `kill_process_on_port()` with a safer implementation that only checks ports for processes the current user owns, or skip it entirely since the NFs handle port conflicts themselves via uvicorn:

```python
# Sidecar override: replace kill_process_on_port in main.py
def kill_process_on_port(port):
    """Safe port-kill that does not require root on macOS."""
    try:
        for proc in psutil.process_iter(['pid', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        proc.terminate()
                        logger.info(f"Terminated process {proc.pid} on port {port}")
                        return True
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
    except Exception:
        pass
    return False
```

This catches `AccessDenied` per-process rather than letting it propagate from the global `psutil.net_connections()` call.

### Fix 2 — SMF startup ordering / UPF discovery race condition

Two options (either works):

**Option A** (simplest): In the start script / main.py, start NRF, wait 3s, start UPF, wait 3s, then start SMF. This ensures UPF is registered before SMF's lifespan runs.

**Option B** (robust): Add lazy UPF re-discovery in SMF's PDU session handler. If `upf_url is None`, retry `GET /discover/UPF` once before returning 502.

### Fix 3 — NRF NFType enum missing RAN types

Add `CU`, `DU`, `RRU`, `SERVICE_ASSURANCE` to NRF's `NFType` enum (or add them to the legacy `/register` handler's accepted types) if RAN component NRF registration is desired. This is cosmetic for 3GPP core tests but matters for full simulation fidelity.

### Fix 4 — main.py process.wait() blocking design

Replace the sequential `wait()` loop with a `KeyboardInterrupt`-aware join:

```python
try:
    for process in processes:
        if process:
            process.wait()
except KeyboardInterrupt:
    logger.info("Shutting down all NFs...")
    for process in processes:
        if process:
            process.terminate()
```

### Practical workaround (no code changes needed)

Use the direct-launch approach verified here: start NRF first (4s sleep), then UPF + other core NFs, then SMF last (to ensure UPF is registered). Use `python -m service_assurance.assurance_api` for service_assurance.

---

## Compliance Test Result

**Test file**: `open-digital-platform-2_0/test_3gpp_compliance.py`
**Run timestamp**: 2026-05-18 21:28:48

| Test | Result |
|------|--------|
| service_health | PASS |
| ue_context_creation | PASS |
| pdu_session_establishment | PASS |
| n4_session_verification | PASS |
| smf_session_verification | PASS |
| traffic_simulation | PASS |

**Pass rate: 6/6 — 100%**

Full PDU session chain verified:
- AMF received UE context and routed to SMF via N11
- SMF allocated UE IP `10.2.0.1`, created SM context, notified UPF via N4/PFCP
- UPF installed 1 forwarding rule, 1 active PFCP session
- SMF shows 1 active session `imsi-001010000000001:1`
- Traffic simulation returned DROPPED (no active bearer to forward — expected in emulation mode)

---

## Ready to Proceed to Stage 2: YES (with caveats)

The 5G core NFs (NRF, AMF, SMF, UPF, AUSF, UDM, UDR, UDSF) start correctly and pass 100% of 3GPP compliance tests when launched with proper startup ordering. The core logic is sound.

**Caveats before stage 2**:

1. `main.py` must not be used as-is on macOS — it crashes before spawning any NF. Either apply Fix 1 or use the direct-launch script approach.
2. Startup ordering matters: NRF first, UPF before SMF. Without this, PDU session establishment fails.
3. RRU and PTP are stubs — no functional implementation. If stage 2 depends on them, they need to be built out.
4. CU/DU NRF registration fails — they run but are invisible to service discovery.

**Minimum action required**: Apply Fix 1 (psutil per-process iteration) and Fix 2 (startup ordering) before any automated or scripted launch.
