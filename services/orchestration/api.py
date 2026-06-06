"""FastAPI wrapper for the MVP orchestration graph."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .orchestration_service import InvalidActivationPlan, orchestrate_activation


class OrchestrationRequest(BaseModel):
    activation_plan: dict[str, Any] = Field(..., description="Activation plan emitted by services/order_engine.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telco Systems Integration Lab MVP Orchestration API",
        version="0.1.0",
        description="Functional-smoke orchestration graph for the service-order-to-activation MVP.",
    )

    @app.post("/orchestration/v1/service-order-to-activation")
    def post_orchestration(request: OrchestrationRequest) -> dict[str, Any]:
        try:
            return orchestrate_activation(request.activation_plan)
        except InvalidActivationPlan as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
