"""
Real southbound adapter for BF3/Python 5G NF integration.

Provisions a real subscriber and slice by calling live 5G core NFs.
All endpoints verified against the running stack (bring_up.sh).

NF endpoints discovered and used
---------------------------------
provision_subscriber:
  ACTIVATE : UDR  POST /register_user               (port 9005, SQLite-persisted)
             UDM  GET  /nudm-sdm/v1/{supi}/am-data  (port 9004, verify subscription)
  ROLLBACK : UDR has no DELETE endpoint. Sidecar approach: the adapter opens
             udr.db directly with sqlite3 and executes DELETE FROM users WHERE
             imsi=?. This is functionally equivalent to a DELETE API because
             UDR reads from the same SQLite file at query time. The DB path is
             read from env var BF3_UDR_DB_PATH (default: Tech-Co root udr.db).

allocate_slice:
  ACTIVATE : NSSF GET  /nnssf-nsselection/v1/network-slice-information (port 9010)
                       Query: nf-type=AMF, nf-id, slice-info-request-for-registration
                       Response: AuthorizedNetworkSliceInfo with allowedNssaiList
             UDM  POST /nudm-sdm/v1/{supi}/am-data/nssai-update        (port 9004)
                       Body: {sst, sd} to write into subscriber allowed-NSSAI
                       (In-memory patch: subscription_data_storage key {supi}_am)
  ROLLBACK : NSSF no persistent slice state to delete (stateless selection)
             UDM  POST /nudm-sdm/v1/{supi}/am-data/nssai-update with empty nssai
                       to remove the S-NSSAI from the subscriber record

register_with_amf:
  ACTIVATE : AMF  POST /amf/ue/{supi}               (port 9000, stores UE context)
             AMF  GET  /amf/ue/{supi}               (verify)
  NOTE     : /amf/ue/register is shadowed by /amf/ue/{ue_id} in FastAPI routing;
             POST /amf/ue/{supi} with a context body is the reachable path.
  ROLLBACK : AMF  POST /amf/ue/{supi}/deregister    (removes UE context)

establish_pdu_session:
  ACTIVATE : SMF  POST /nsmf-pdusession/v1/sm-contexts  (port 9001)
  ROLLBACK : SMF holds session state in an in-memory dict (session_contexts).
             smf.py exposes GET /smf/sessions (list keys) but no DELETE endpoint,
             and we do not modify NF code. Rollback is therefore best-effort:
             the adapter calls GET /smf/sessions to record whether the session
             key is still active, logs the orphaned key for operator awareness,
             and completes without error. The lab accepts that ungraceful order
             failures may leave stale in-memory sessions until the SMF restarts.
             Session key format used by smf.py: "{supi}:{pdu_session_id}".

Sidecar rollback rationale
--------------------------
UDR rollback bypasses the NF API by directly modifying udr.db SQLite. This is
acceptable because UDR is a local SQLite-backed NF without a DELETE endpoint;
modifying the same store the NF reads from is functionally equivalent to calling
a DELETE API. The rollback is idempotent: if the row is already gone the DELETE
is a no-op and no error is raised.

SMF rollback is best-effort because SMF holds session state in-memory only.
The lab accepts that ungraceful order failures may leave stale sessions until
the SMF restarts. This is documented honestly so operators are not misled.
"""
import logging
import os
import secrets
from datetime import datetime, timezone
from typing import Any

import httpx

from app.adapters.base import SouthboundAdapter

logger = logging.getLogger(__name__)

# NF base URLs - read from environment variables so Docker/K8s deployments can
# override them without touching source code.  Defaults preserve existing
# localhost behaviour for bare-metal and development runs.
UDR_BASE  = os.getenv("BF3_UDR_URL",  "http://localhost:9005")
UDM_BASE  = os.getenv("BF3_UDM_URL",  "http://localhost:9004")
AMF_BASE  = os.getenv("BF3_AMF_URL",  "http://localhost:9000")
SMF_BASE  = os.getenv("BF3_SMF_URL",  "http://localhost:9001")
NSSF_BASE = os.getenv("BF3_NSSF_URL", "http://localhost:9010")

# Fixed AMF NF instance ID used when querying NSSF (must be a valid UUID string)
_AMF_NF_ID = "amf-techco-order-engine-001"

# HTTP timeout in seconds
_TIMEOUT = 10.0


def _make_supi(payload: dict[str, Any]) -> str:
    """Derive SUPI from payload or generate a unique one."""
    if supi := payload.get("supi"):
        return supi
    # 6 random hex chars -> unique IMSI in 001-01 range
    suffix = secrets.token_hex(3)
    return f"imsi-001010{suffix}"


def _make_imsi(supi: str) -> str:
    """Strip 'imsi-' prefix to get the raw IMSI digit string."""
    return supi.replace("imsi-", "")


class BF3PythonAdapter(SouthboundAdapter):
    """Real adapter: hits live 5G core NFs to provision subscribers and slices."""

    # -------------------------------------------------------------------------
    # provision_subscriber
    # -------------------------------------------------------------------------

    async def _activate_provision_subscriber(self, payload: dict[str, Any]) -> dict:
        supi = _make_supi(payload)
        imsi = _make_imsi(supi)
        subscriber_profile = payload.get("subscriber_profile", "default")

        # 1. Register subscriber in UDR (SQLite-persistent store, TS 29.504)
        udr_body = {
            "imsi": imsi,
            "key": secrets.token_hex(16),
        }
        logger.info(
            "[BF3Adapter] provision_subscriber -> UDR POST /register_user imsi=%s profile=%s",
            imsi, subscriber_profile,
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            udr_resp = await client.post(f"{UDR_BASE}/register_user", json=udr_body)

        udr_status = udr_resp.status_code
        udr_json = udr_resp.json() if udr_resp.content else {}
        logger.info("[BF3Adapter] UDR response HTTP %d: %s", udr_status, udr_json)

        if udr_status not in (200, 201):
            raise RuntimeError(
                f"UDR /register_user failed HTTP {udr_status}: {udr_json}"
            )

        # 2. Verify via UDM access and mobility data (TS 29.505)
        logger.info(
            "[BF3Adapter] provision_subscriber -> UDM GET /nudm-sdm/v1/%s/am-data", supi
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            udm_resp = await client.get(f"{UDM_BASE}/nudm-sdm/v1/{supi}/am-data")

        udm_status = udm_resp.status_code
        udm_json = udm_resp.json() if udm_resp.content else {}
        # 404 is expected for SUPIs outside UDM's pre-seeded default range;
        # the subscriber IS registered in UDR regardless.
        logger.info(
            "[BF3Adapter] UDM /am-data HTTP %d (404 expected for IMSI outside default range)",
            udm_status,
        )

        return {
            "status": "provisioned",
            "supi": supi,
            "imsi": imsi,
            "subscriber_profile": subscriber_profile,
            "udr_register_response": udr_json,
            "udm_am_data_http_status": udm_status,
            "udm_am_data": udm_json if udm_status == 200 else None,
        }

    async def _rollback_provision_subscriber(self, payload: dict[str, Any]) -> None:
        supi = _make_supi(payload)
        imsi = _make_imsi(supi)

        # Sidecar approach: UDR has no DELETE endpoint so we go directly to the
        # SQLite database it reads from. This is functionally equivalent because
        # UDR performs a fresh sqlite3.connect() on every query. The path is
        # controlled by BF3_UDR_DB_PATH; the default resolves to the Tech-Co
        # root udr.db that bring_up.sh creates alongside udr.py.
        _default_db = os.path.join(
            os.path.dirname(  # Tech-Co root
                os.path.dirname(  # src/
                    os.path.dirname(  # order_engine/
                        os.path.dirname(  # app/
                            os.path.dirname(  # adapters/
                                os.path.abspath(__file__)
                            )
                        )
                    )
                )
            ),
            "udr.db",
        )
        db_path = os.getenv("BF3_UDR_DB_PATH", _default_db)

        logger.info(
            "[BF3Adapter] ROLLBACK provision_subscriber: deleting imsi=%s from %s",
            imsi, db_path,
        )
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM users WHERE imsi=?", (imsi,))
                conn.commit()
                rows_deleted = cur.rowcount
            finally:
                conn.close()
            logger.info(
                "[BF3Adapter] ROLLBACK provision_subscriber: DELETE FROM users WHERE imsi=%s "
                "-> %d row(s) removed (0 means already absent, idempotent).",
                imsi, rows_deleted,
            )
        except Exception as exc:
            # Non-fatal: log and continue so the saga rollback chain is not
            # interrupted. Operators can inspect udr.db manually if needed.
            logger.warning(
                "[BF3Adapter] ROLLBACK provision_subscriber: SQLite delete failed "
                "(non-fatal, idempotent): imsi=%s db=%s error=%s",
                imsi, db_path, exc,
            )

    # -------------------------------------------------------------------------
    # allocate_slice
    # -------------------------------------------------------------------------

    async def _activate_allocate_slice(self, payload: dict[str, Any]) -> dict:
        supi = _make_supi(payload)
        sst = int(payload.get("sst", 2))
        sd = str(payload.get("sd", "010203"))
        slice_type = payload.get("slice_type", "URLLC")

        # Step 1: Query NSSF for authorized network slice info (TS 29.531).
        # Build a SliceInfoForRegistration that both requests and subscribes to the
        # target S-NSSAI. NSSF ns_selection_for_registration only allows an S-NSSAI
        # that also appears in subscribedNssai; including it in both lists satisfies
        # that check and returns it in allowedNssaiList.
        import json as _json
        slice_info_for_registration = _json.dumps({
            "subscribedNssai": [
                {"subscribedSnssai": {"sst": sst, "sd": sd}, "defaultIndication": True}
            ],
            "requestedNssai": [{"sst": sst, "sd": sd}],
            "defaultConfiguredSnssaiInd": False,
        })
        nssf_params = {
            "nf-type": "AMF",
            "nf-id": _AMF_NF_ID,
            "slice-info-request-for-registration": slice_info_for_registration,
        }
        logger.info(
            "[BF3Adapter] allocate_slice -> NSSF GET /nnssf-nsselection/v1/network-slice-information "
            "sst=%d sd=%s slice_type=%s supi=%s",
            sst, sd, slice_type, supi,
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            nssf_resp = await client.get(
                f"{NSSF_BASE}/nnssf-nsselection/v1/network-slice-information",
                params=nssf_params,
            )

        nssf_status = nssf_resp.status_code
        nssf_json = nssf_resp.json() if nssf_resp.content else {}
        logger.info("[BF3Adapter] NSSF response HTTP %d: %s", nssf_status, nssf_json)

        # If NSSF returns a non-2xx status, raise so the saga rolls back.
        if nssf_status not in (200, 201):
            raise RuntimeError(
                f"NSSF slice selection failed HTTP {nssf_status}: {nssf_json}"
            )
        # A 200 with an empty allowedNssaiList and non-empty rejectedNssaiInPlmn
        # means the slice is not supported in this PLMN. Raise to trigger rollback.
        rejected = nssf_json.get("rejectedNssaiInPlmn") or []
        allowed_check = nssf_json.get("allowedNssaiList") or []
        if rejected and not allowed_check:
            raise RuntimeError(
                f"NSSF rejected slice sst={sst} sd={sd} in PLMN: {rejected}"
            )

        # Extract the authorized S-NSSAI from the NSSF response.
        # Prefer the first entry of allowedNssaiList if present; fall back to requested.
        authorized_snssai = {"sst": sst, "sd": sd}
        allowed_list = nssf_json.get("allowedNssaiList", [])
        if allowed_list:
            inner = allowed_list[0].get("allowedSnssaiList", [])
            if inner:
                authorized_snssai = inner[0].get("allowedSnssai", authorized_snssai)

        auth_sst = int(authorized_snssai.get("sst", sst))
        auth_sd = str(authorized_snssai.get("sd", sd)) if authorized_snssai.get("sd") else sd

        # Step 2: Write the authorized S-NSSAI into UDM for this subscriber.
        # UDM exposes /nudm-sdm/v1/{supi}/am-data/nssai-update as a custom POST
        # that appends a single S-NSSAI into the subscriber's allowed-NSSAI list
        # held in subscription_data_storage[{supi}_am]. This is an in-band write
        # path that avoids modifying any NF code.
        udm_nssai_body = {
            "sst": auth_sst,
            "sd": auth_sd,
            "sliceType": slice_type,
        }
        logger.info(
            "[BF3Adapter] allocate_slice -> UDM POST /nudm-sdm/v1/%s/am-data/nssai-update "
            "sst=%d sd=%s",
            supi, auth_sst, auth_sd,
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            udm_resp = await client.post(
                f"{UDM_BASE}/nudm-sdm/v1/{supi}/am-data/nssai-update",
                json=udm_nssai_body,
            )

        udm_status = udm_resp.status_code
        udm_json = udm_resp.json() if udm_resp.content else {}
        logger.info("[BF3Adapter] UDM nssai-update HTTP %d: %s", udm_status, udm_json)

        # UDM returns 404 for SUPIs outside its pre-seeded range; that is expected
        # for dynamically provisioned subscribers. Log and continue -- the S-NSSAI
        # is still recorded in the saga step result for downstream steps.
        if udm_status not in (200, 201, 404):
            raise RuntimeError(
                f"UDM nssai-update failed HTTP {udm_status}: {udm_json}"
            )

        return {
            "status": "allocated",
            "supi": supi,
            "sst": auth_sst,
            "sd": auth_sd,
            "slice_type": slice_type,
            "nssf_http_status": nssf_status,
            "nssf_authorized_nssai": nssf_json.get("allowedNssaiList"),
            "udm_nssai_update_http_status": udm_status,
            "udm_nssai_update_response": udm_json,
        }

    async def _rollback_allocate_slice(self, payload: dict[str, Any]) -> None:
        supi = _make_supi(payload)
        sst = payload.get("sst", 2)
        sd = payload.get("sd", "010203")

        # Remove the S-NSSAI from UDM by calling nssai-update with an empty body.
        # NSSF is stateless (selection only, no persistent slice record), so no
        # NSSF DELETE is needed.
        logger.info(
            "[BF3Adapter] ROLLBACK allocate_slice -> UDM POST "
            "/nudm-sdm/v1/%s/am-data/nssai-update (remove sst=%s sd=%s)",
            supi, sst, sd,
        )
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                resp = await client.post(
                    f"{UDM_BASE}/nudm-sdm/v1/{supi}/am-data/nssai-update",
                    json={"remove": True, "sst": sst, "sd": sd},
                )
            logger.info(
                "[BF3Adapter] ROLLBACK UDM nssai-update HTTP %d: %s",
                resp.status_code,
                resp.json() if resp.content else {},
            )
        except Exception as exc:
            logger.warning(
                "[BF3Adapter] ROLLBACK allocate_slice: UDM nssai-update error (non-fatal): %s",
                exc,
            )

    # -------------------------------------------------------------------------
    # register_with_amf
    # -------------------------------------------------------------------------

    async def _activate_register_with_amf(self, payload: dict[str, Any]) -> dict:
        supi = _make_supi(payload)

        # POST /amf/ue/{supi} stores the UE context dict directly.
        # NOTE: /amf/ue/register is shadowed in FastAPI routing by /amf/ue/{ue_id}
        # so we use the generic context creation endpoint which IS reachable.
        ue_context = {
            "supi": supi,
            "rmState": "RM-REGISTERED",
            "cmState": "CM-CONNECTED",
            "registrationSource": "order_engine",
            "allowedNssai": [{"sst": payload.get("sst", 1), "sd": payload.get("sd", "010203")}],
            "registeredAt": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "[BF3Adapter] register_with_amf -> AMF POST /amf/ue/%s", supi
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            amf_resp = await client.post(
                f"{AMF_BASE}/amf/ue/{supi}",
                json=ue_context,
            )

        amf_status = amf_resp.status_code
        amf_json = amf_resp.json() if amf_resp.content else {}
        logger.info("[BF3Adapter] AMF POST response HTTP %d: %s", amf_status, amf_json)

        if amf_status not in (200, 201):
            raise RuntimeError(
                f"AMF /amf/ue/{supi} failed HTTP {amf_status}: {amf_json}"
            )

        # Verify context was stored
        logger.info("[BF3Adapter] register_with_amf -> AMF GET /amf/ue/%s (verify)", supi)
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            verify_resp = await client.get(f"{AMF_BASE}/amf/ue/{supi}")

        verify_status = verify_resp.status_code
        verify_json = verify_resp.json() if verify_resp.content else {}
        logger.info(
            "[BF3Adapter] AMF GET verify HTTP %d: %s", verify_status, verify_json
        )

        return {
            "status": "registered",
            "supi": supi,
            "amf_create_response": amf_json,
            "amf_verify_http_status": verify_status,
            "amf_context": verify_json if verify_status == 200 else None,
        }

    async def _rollback_register_with_amf(self, payload: dict[str, Any]) -> None:
        supi = _make_supi(payload)

        logger.info(
            "[BF3Adapter] ROLLBACK register_with_amf -> AMF POST /amf/ue/%s/deregister", supi
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            dereg_resp = await client.post(
                f"{AMF_BASE}/amf/ue/{supi}/deregister",
                json={"deregistrationType": "switchOff"},
            )

        logger.info(
            "[BF3Adapter] AMF deregister HTTP %d: %s",
            dereg_resp.status_code,
            dereg_resp.json() if dereg_resp.content else {},
        )

    # -------------------------------------------------------------------------
    # establish_pdu_session
    # -------------------------------------------------------------------------

    async def _activate_establish_pdu_session(self, payload: dict[str, Any]) -> dict:
        supi = _make_supi(payload)
        sst = int(payload.get("sst", 1))
        sd = str(payload.get("sd", "010203"))
        pdu_session_id = int(payload.get("pdu_session_id", 1))

        sm_body = {
            "supi": supi,
            "pduSessionId": pdu_session_id,
            "dnn": "internet",
            "sNssai": {"sst": sst, "sd": sd},
            "anType": "3GPP_ACCESS",
        }

        logger.info(
            "[BF3Adapter] establish_pdu_session -> SMF POST /nsmf-pdusession/v1/sm-contexts "
            "supi=%s pduSessionId=%d",
            supi, pdu_session_id,
        )
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            smf_resp = await client.post(
                f"{SMF_BASE}/nsmf-pdusession/v1/sm-contexts", json=sm_body
            )

        smf_status = smf_resp.status_code
        smf_json = smf_resp.json() if smf_resp.content else {}
        logger.info("[BF3Adapter] SMF response HTTP %d: %s", smf_status, smf_json)

        if smf_status not in (200, 201):
            raise RuntimeError(
                f"SMF /nsmf-pdusession/v1/sm-contexts failed HTTP {smf_status}: {smf_json}"
            )

        return {
            "status": "pdu_session_established",
            "supi": supi,
            "pdu_session_id": pdu_session_id,
            "ue_ip_address": smf_json.get("ueIpAddress"),
            "smf_response": smf_json,
        }

    async def _rollback_establish_pdu_session(self, payload: dict[str, Any]) -> None:
        supi = _make_supi(payload)
        pdu_session_id = int(payload.get("pdu_session_id", 1))
        session_key = f"{supi}:{pdu_session_id}"

        # Best-effort rollback: smf.py holds session state in an in-memory dict
        # (session_contexts) and exposes no DELETE endpoint. We do not modify NF
        # code. Instead, we call GET /smf/sessions to confirm whether the session
        # key is still alive, log the result for operator awareness, and complete
        # without raising an error so the saga rollback chain continues cleanly.
        # Stale sessions will be cleaned up when the SMF process restarts.
        logger.warning(
            "[BF3Adapter] ROLLBACK establish_pdu_session: SMF has no DELETE "
            "sm-contexts endpoint (best-effort rollback). Checking session "
            "key=%s via GET /smf/sessions.",
            session_key,
        )
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                sessions_resp = await client.get(f"{SMF_BASE}/smf/sessions")
            if sessions_resp.status_code == 200:
                sessions_data = sessions_resp.json()
                active_keys = sessions_data.get("sessions", [])
                if session_key in active_keys:
                    logger.warning(
                        "[BF3Adapter] ROLLBACK establish_pdu_session: session key=%s "
                        "is still ACTIVE in SMF memory. No DELETE endpoint available; "
                        "session will be orphaned until SMF restarts. "
                        "Operator action required if persistent cleanup is needed.",
                        session_key,
                    )
                else:
                    logger.info(
                        "[BF3Adapter] ROLLBACK establish_pdu_session: session key=%s "
                        "not found in SMF active sessions (already absent or never created).",
                        session_key,
                    )
            else:
                logger.warning(
                    "[BF3Adapter] ROLLBACK establish_pdu_session: GET /smf/sessions "
                    "returned HTTP %d; SMF may be unreachable. session key=%s status unknown.",
                    sessions_resp.status_code, session_key,
                )
        except Exception as exc:
            # SMF unreachable during rollback: log and continue. The session key
            # is recorded above for operator reference.
            logger.warning(
                "[BF3Adapter] ROLLBACK establish_pdu_session: could not reach SMF "
                "to verify session status (non-fatal): key=%s error=%s",
                session_key, exc,
            )

    # -------------------------------------------------------------------------
    # Public SouthboundAdapter interface
    # -------------------------------------------------------------------------

    async def activate(self, step_name: str, payload: dict[str, Any]) -> dict:
        logger.info(
            "[BF3Adapter] ACTIVATE step='%s' payload=%s", step_name, payload
        )

        if step_name == "provision_subscriber":
            return await self._activate_provision_subscriber(payload)

        if step_name == "allocate_slice":
            return await self._activate_allocate_slice(payload)

        if step_name == "register_with_amf":
            return await self._activate_register_with_amf(payload)

        if step_name == "establish_pdu_session":
            return await self._activate_establish_pdu_session(payload)

        logger.warning(
            "[BF3Adapter] ACTIVATE: unknown step '%s' - returning stub success. "
            "Add a real handler for this step.",
            step_name,
        )
        return {
            "status": "stub_success",
            "adapter": "bf3_python",
            "step": step_name,
            "note": "No real NF call implemented for this step",
        }

    async def rollback(self, step_name: str, payload: dict[str, Any]) -> None:
        logger.info(
            "[BF3Adapter] ROLLBACK step='%s' payload=%s", step_name, payload
        )

        if step_name == "provision_subscriber":
            await self._rollback_provision_subscriber(payload)
            return

        if step_name == "allocate_slice":
            await self._rollback_allocate_slice(payload)
            return

        if step_name == "register_with_amf":
            await self._rollback_register_with_amf(payload)
            return

        if step_name == "establish_pdu_session":
            await self._rollback_establish_pdu_session(payload)
            return

        logger.warning(
            "[BF3Adapter] ROLLBACK: unknown step '%s' - no rollback action taken.",
            step_name,
        )
