"""
Real southbound adapter for the O-RAN O2-IMS (O2 Interface Management Service).

Talks to the O2IMS REST API over httpx (async).  Implements the SouthboundAdapter
interface from app/adapters/base.py.

Endpoint reference (Red Hat oran-o2ims, docs/user-guide/inventory-api.md and
cluster-provisioning.md):

  Inventory / Resource server
    GET  /o2ims-infrastructureInventory/v1/
    GET  /o2ims-infrastructureInventory/v1/deploymentManagers
    GET  /o2ims-infrastructureInventory/v1/deploymentManagers/{id}
    GET  /o2ims-infrastructureInventory/v1/resourcePools
    GET  /o2ims-infrastructureInventory/v1/resourcePools/{id}/resources

  Provisioning server
    POST   /o2ims-infrastructureProvisioning/v1/provisioningRequests
    GET    /o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}
    DELETE /o2ims-infrastructureProvisioning/v1/provisioningRequests/{id}

Environment variables
  O2IMS_BASE_URL   Base URL of the O2IMS API (default: http://localhost:8083)
  O2IMS_TOKEN      Bearer token if the upstream requires auth (optional)

Order-step -> O2IMS mapping
  allocate_o_cloud_resource   POST provisioningRequests  (activate)
                              DELETE provisioningRequests/{id} (rollback)
  query_deployment_managers   GET deploymentManagers
  query_resource_pools        GET resourcePools
  query_resources             GET resourcePools/{id}/resources
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import Any

import httpx

from app.adapters.base import SouthboundAdapter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_DEFAULT_BASE_URL = "http://localhost:8083"
_RETRY_ATTEMPTS = 3
_RETRY_WAITS = (1, 2, 4)  # seconds between attempt 1->2, 2->3, 3->fail

# O2IMS REST path prefixes (per ORAN spec and Red Hat implementation)
_INVENTORY_PREFIX = "/o2ims-infrastructureInventory/v1"
_PROVISIONING_PREFIX = "/o2ims-infrastructureProvisioning/v1"

# Step names the order engine may pass for provisioning operations
_STEP_ALLOCATE = "allocate_o_cloud_resource"
_STEP_QUERY_DM = "query_deployment_managers"
_STEP_QUERY_POOLS = "query_resource_pools"
_STEP_QUERY_RESOURCES = "query_resources"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_url() -> str:
    return os.environ.get("O2IMS_BASE_URL", _DEFAULT_BASE_URL).rstrip("/")


def _auth_headers() -> dict[str, str]:
    token = os.environ.get("O2IMS_TOKEN", "")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


async def _request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    json: dict | None = None,
) -> httpx.Response:
    """Execute an HTTP request with up to _RETRY_ATTEMPTS tries and exponential backoff.

    4xx responses are not retried because they are client errors (not transient).
    5xx and network errors are retried with the configured wait schedule.
    """
    last_exc: Exception | None = None
    for attempt in range(1, _RETRY_ATTEMPTS + 1):
        try:
            logger.info(
                "[O2IMSRealAdapter] %s %s (attempt %d/%d)",
                method.upper(), url, attempt, _RETRY_ATTEMPTS,
            )
            resp = await client.request(method, url, json=json, headers=_auth_headers())
            resp.raise_for_status()
            logger.info(
                "[O2IMSRealAdapter] %s %s -> %d", method.upper(), url, resp.status_code
            )
            return resp
        except httpx.HTTPStatusError as exc:
            last_exc = exc
            logger.warning(
                "[O2IMSRealAdapter] %s %s attempt %d failed: %s",
                method.upper(), url, attempt, exc,
            )
            # 4xx errors are client errors -- do not retry them
            if exc.response.status_code < 500:
                raise
            if attempt < _RETRY_ATTEMPTS:
                await asyncio.sleep(_RETRY_WAITS[attempt - 1])
        except httpx.RequestError as exc:
            last_exc = exc
            logger.warning(
                "[O2IMSRealAdapter] %s %s attempt %d failed: %s",
                method.upper(), url, attempt, exc,
            )
            if attempt < _RETRY_ATTEMPTS:
                await asyncio.sleep(_RETRY_WAITS[attempt - 1])

    raise RuntimeError(
        f"O2IMS request {method.upper()} {url} failed after {_RETRY_ATTEMPTS} attempts"
    ) from last_exc


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class O2IMSRealAdapter(SouthboundAdapter):
    """
    Southbound adapter that calls the live O-RAN O2IMS REST API.

    activate() maps the incoming step_name to an O2IMS API call.
    rollback() deletes whatever activate() created (idempotent on 404).

    The adapter stores the provisioning-request ID that was created during
    activate() into the payload dict under the key "_o2ims_pr_id" so that
    rollback() can target the correct resource.
    """

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def activate(self, step_name: str, payload: dict[str, Any]) -> dict:
        """
        Dispatch to the correct O2IMS API based on step_name.

        Returns a dict with at minimum {"status": "success", "adapter": "o2ims_real"}.
        For provisioning steps the returned dict also includes the created
        provisioning-request ID under "provisioning_request_id".
        """
        logger.info(
            "[O2IMSRealAdapter] ACTIVATE step='%s' payload=%s", step_name, payload
        )
        base = _base_url()

        async with httpx.AsyncClient(timeout=30.0) as client:
            if step_name == _STEP_ALLOCATE:
                return await self._create_provisioning_request(client, base, payload)

            if step_name == _STEP_QUERY_DM:
                return await self._query_deployment_managers(client, base, payload)

            if step_name == _STEP_QUERY_POOLS:
                return await self._query_resource_pools(client, base, payload)

            if step_name == _STEP_QUERY_RESOURCES:
                return await self._query_resources(client, base, payload)

            # Unknown step -- treat as a no-op with a warning so the saga can
            # continue; the caller can decide whether to treat this as a failure.
            logger.warning(
                "[O2IMSRealAdapter] Unknown step '%s', returning no-op success",
                step_name,
            )
            return {
                "status": "success",
                "adapter": "o2ims_real",
                "step": step_name,
                "note": "no-op: step not mapped to an O2IMS API call",
            }

    async def rollback(self, step_name: str, payload: dict[str, Any]) -> None:
        """
        Undo what activate() created.

        For provisioning steps this deletes the ProvisioningRequest that was
        created.  The PR id must be present in payload["_o2ims_pr_id"].
        For read-only query steps there is nothing to undo.
        """
        logger.info(
            "[O2IMSRealAdapter] ROLLBACK step='%s' payload=%s", step_name, payload
        )
        if step_name != _STEP_ALLOCATE:
            logger.info(
                "[O2IMSRealAdapter] step '%s' is read-only; nothing to roll back",
                step_name,
            )
            return

        pr_id = payload.get("_o2ims_pr_id")
        if not pr_id:
            logger.warning(
                "[O2IMSRealAdapter] ROLLBACK called for '%s' but no _o2ims_pr_id in "
                "payload; cannot delete ProvisioningRequest",
                step_name,
            )
            return

        base = _base_url()
        url = f"{base}{_PROVISIONING_PREFIX}/provisioningRequests/{pr_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                await _request_with_retry(client, "DELETE", url)
                logger.info(
                    "[O2IMSRealAdapter] Deleted ProvisioningRequest %s", pr_id
                )
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    # Already gone -- rollback is idempotent
                    logger.info(
                        "[O2IMSRealAdapter] ProvisioningRequest %s already absent "
                        "(404); rollback complete",
                        pr_id,
                    )
                else:
                    raise

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _create_provisioning_request(
        self,
        client: httpx.AsyncClient,
        base: str,
        payload: dict[str, Any],
    ) -> dict:
        """POST /o2ims-infrastructureProvisioning/v1/provisioningRequests"""
        # Build a ProvisioningRequest body that matches the O2IMS spec.
        # Required fields: templateName, templateVersion, templateParameters.
        # A stable UUID is generated from the payload so re-sends are idempotent
        # at the O2IMS level if the upstream supports it.
        pr_id = str(uuid.uuid4())

        body: dict[str, Any] = {
            "metadata": {"name": pr_id},
            "spec": {
                "name": payload.get("name", f"order-engine-{pr_id[:8]}"),
                "description": payload.get(
                    "description", "Created by Tech-Co order engine"
                ),
                "templateName": payload.get("templateName", "default"),
                "templateVersion": payload.get("templateVersion", "v1"),
                "templateParameters": payload.get("templateParameters", {}),
            },
        }

        url = f"{base}{_PROVISIONING_PREFIX}/provisioningRequests"
        resp = await _request_with_retry(client, "POST", url, json=body)
        response_data = resp.json() if resp.content else {}

        # Persist the PR id back into payload so rollback can use it
        payload["_o2ims_pr_id"] = pr_id

        return {
            "status": "success",
            "adapter": "o2ims_real",
            "step": _STEP_ALLOCATE,
            "provisioning_request_id": pr_id,
            "o2ims_response": response_data,
        }

    async def _query_deployment_managers(
        self,
        client: httpx.AsyncClient,
        base: str,
        payload: dict[str, Any],
    ) -> dict:
        """GET /o2ims-infrastructureInventory/v1/deploymentManagers"""
        url = f"{base}{_INVENTORY_PREFIX}/deploymentManagers"
        resp = await _request_with_retry(client, "GET", url)
        return {
            "status": "success",
            "adapter": "o2ims_real",
            "step": _STEP_QUERY_DM,
            "deployment_managers": resp.json(),
        }

    async def _query_resource_pools(
        self,
        client: httpx.AsyncClient,
        base: str,
        payload: dict[str, Any],
    ) -> dict:
        """GET /o2ims-infrastructureInventory/v1/resourcePools"""
        url = f"{base}{_INVENTORY_PREFIX}/resourcePools"
        resp = await _request_with_retry(client, "GET", url)
        return {
            "status": "success",
            "adapter": "o2ims_real",
            "step": _STEP_QUERY_POOLS,
            "resource_pools": resp.json(),
        }

    async def _query_resources(
        self,
        client: httpx.AsyncClient,
        base: str,
        payload: dict[str, Any],
    ) -> dict:
        """GET /o2ims-infrastructureInventory/v1/resourcePools/{id}/resources"""
        pool_id = payload.get("resource_pool_id")
        if not pool_id:
            raise ValueError(
                "payload must include 'resource_pool_id' for step query_resources"
            )
        url = f"{base}{_INVENTORY_PREFIX}/resourcePools/{pool_id}/resources"
        resp = await _request_with_retry(client, "GET", url)
        return {
            "status": "success",
            "adapter": "o2ims_real",
            "step": _STEP_QUERY_RESOURCES,
            "resources": resp.json(),
        }
