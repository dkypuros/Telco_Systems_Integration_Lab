"""FastAPI wrapper for the 3GPP mock-core activation adapter."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


def _load_adapter_module():
    path = Path(__file__).with_name("mock_core_activation_adapter.py")
    spec = importlib.util.spec_from_file_location("mock_core_activation_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load mock_core_activation_adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_adapter = _load_adapter_module()


class AdapterActivationRequest(BaseModel):
    correlation_id: str
    order_id: str
    service_id: str
    product_id: str
    network_action: str
    subscriber_intent: str
    session_intent: str
    adapter_contract_path: str | None = Field(default=None)
    claim_boundary: str | None = Field(default=None)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telco Systems Integration Lab 3GPP Mock-Core Adapter",
        version="0.1.0",
        description="Functional-smoke 3GPP mock-core activation adapter for the service-order-to-activation MVP.",
    )

    @app.post("/adapters/3gpp/v1/mock-core/activate")
    def post_activate(request: AdapterActivationRequest) -> dict[str, Any]:
        try:
            return _adapter.activate_subscriber_session(request.model_dump())
        except _adapter.InvalidMockCoreActivationRequest as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
