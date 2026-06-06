"""FastAPI wrapper for the MVP catalog callable service surface."""

from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException

from .catalog_service import ProductNotFound, list_products, lookup_product

DEFAULT_CORRELATION_ID = "corr-catalog-unspecified"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Telco Systems Integration Lab MVP Catalog API",
        version="0.1.0",
        description="TMF620-referenced functional-smoke catalog API for the service-order-to-activation MVP.",
    )

    @app.get("/tmf-api/productCatalogManagement/v5/productSpecification")
    def get_products(x_correlation_id: str = Header(default=DEFAULT_CORRELATION_ID)):
        return list_products(correlation_id=x_correlation_id)

    @app.get("/tmf-api/productCatalogManagement/v5/productSpecification/{product_id}")
    def get_product(product_id: str, x_correlation_id: str = Header(default=DEFAULT_CORRELATION_ID)):
        try:
            return lookup_product(product_id, correlation_id=x_correlation_id)
        except ProductNotFound as exc:
            raise HTTPException(status_code=404, detail=f"unknown product_id: {product_id}") from exc

    return app


app = create_app()
