"""FastAPI wrapper for the MVP product order engine."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from .order_service import InvalidProductOrder, create_product_order

DEFAULT_CORRELATION_ID = "corr-order-unspecified"


class ProductOrderRequest(BaseModel):
    product_id: str = Field(..., description="Catalog product identifier, e.g. prod-5g-data-basic")
    customer_id: str = Field(..., description="Public-safe demo customer identifier")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telco Systems Integration Lab MVP Product Order API",
        version="0.1.0",
        description="TMF622/TMF641-referenced functional-smoke product ordering API for the service-order-to-activation MVP.",
    )

    @app.post("/tmf-api/productOrderingManagement/v5/productOrder", status_code=status.HTTP_201_CREATED)
    def post_product_order(
        request: ProductOrderRequest,
        x_correlation_id: str = Header(default=DEFAULT_CORRELATION_ID),
    ) -> dict[str, Any]:
        try:
            return create_product_order(
                product_id=request.product_id,
                customer_id=request.customer_id,
                correlation_id=x_correlation_id,
            )
        except InvalidProductOrder as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
