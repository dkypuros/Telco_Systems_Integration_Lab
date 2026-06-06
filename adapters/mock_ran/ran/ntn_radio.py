#!/usr/bin/env python3
"""NTN radio mock service for lab-managed radio scenarios.

This small service is intentionally native to the clean lab environment. It
keeps the operator demo path runnable without depending on an old standalone
source tree. Evidence label: functional smoke only, not formal NTN conformance.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Telco Lab NTN Radio Mock", version="0.1.0")
_EVENTS: list[str] = []


class RadioTick(BaseModel):
    beam_id: str = Field(default="beam-demo-001")
    carrier_hz: int = Field(default=2_000_000_000, ge=1)
    doppler_hz: float = Field(default=120.0)


def _record(message: str) -> str:
    line = f"{datetime.now(timezone.utc).isoformat()} {message}"
    _EVENTS.append(line)
    del _EVENTS[:-200]
    return line


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "NTN Radio",
        "evidence_label": "functional_smoke",
        "claim_boundary": "runtime/demo readiness only; not formal NTN conformance",
    }


@app.post("/ntn/tick")
def tick(payload: RadioTick | None = None) -> dict[str, Any]:
    payload = payload or RadioTick()
    line = _record(
        f"NTN_TICK beam={payload.beam_id} carrier_hz={payload.carrier_hz} doppler_hz={payload.doppler_hz}"
    )
    return {"status": "OK", "message": "radio tick accepted", "event": line}


@app.get("/ntn/logs")
def logs(limit: int = 20) -> dict[str, Any]:
    return {"status": "OK", "count": len(_EVENTS[-limit:]), "lines": _EVENTS[-limit:]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telco Lab NTN Radio Mock")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8132)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
