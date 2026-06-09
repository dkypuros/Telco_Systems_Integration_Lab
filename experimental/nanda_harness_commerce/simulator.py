"""Deterministic NANDA-style skill import planner for the telco harness.

This module models a control-plane pattern only. It does not call a live NANDA
Index, does not verify real cryptographic signatures, does not pull containers,
and does not execute a remote agent. It validates whether AgentFacts-like records
would be acceptable to the local harness policy and emits a disabled import plan
that still requires human approval.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def select_protocol(record: dict[str, Any], allowed_protocols: list[str]) -> dict[str, str] | None:
    for protocol_name in allowed_protocols:
        for protocol in record.get("protocols", []):
            if protocol.get("type") == protocol_name:
                return {"type": protocol_name, "endpoint": protocol.get("endpoint", "")}
    return None


def reject(reason_list: list[str], reason: str) -> None:
    if reason not in reason_list:
        reason_list.append(reason)


def evaluate_record(
    record: dict[str, Any], intent: dict[str, Any], policy: dict[str, Any]
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    reasons: list[str] = []
    checks: list[str] = []

    agent_id = record.get("agent_id", "<unknown-agent>")
    required_capability = intent["required_capability"]
    capabilities = record.get("capabilities", [])
    if required_capability not in capabilities:
        reject(reasons, "capability_mismatch")
    else:
        checks.append("capability_match")

    if record.get("issuer") not in policy["allowed_issuers"]:
        reject(reasons, "issuer_not_allowed")
    else:
        checks.append("issuer_allowed")

    if policy.get("require_signature", True) and not record.get("signature"):
        reject(reasons, "signature_missing")
    else:
        checks.append("signature_present")

    allowed_protocols = [
        p for p in intent.get("acceptable_protocols", []) if p in policy.get("allowed_protocols", [])
    ]
    selected_protocol = select_protocol(record, allowed_protocols)
    if not selected_protocol:
        reject(reasons, "no_allowed_protocol")
    else:
        checks.append("protocol_allowed")

    evidence = set(record.get("evidence", []))
    required_evidence = set(policy.get("required_evidence", []))
    missing_evidence = sorted(required_evidence - evidence)
    if missing_evidence:
        reject(reasons, "required_evidence_missing:" + ",".join(missing_evidence))
    else:
        checks.append("required_evidence_present")

    quality_score = float(record.get("quality", {}).get("score", 0.0))
    if quality_score < float(policy["minimum_quality_score"]):
        reject(reasons, "quality_below_threshold")
    else:
        checks.append("quality_threshold_met")

    risk = record.get("risk", "critical")
    if RISK_ORDER.get(risk, 99) > RISK_ORDER[policy["maximum_risk"]]:
        reject(reasons, "risk_exceeds_policy")
    else:
        checks.append("risk_within_policy")

    terms = record.get("commercial_terms", {})
    limits = policy.get("commercial_limits", {})
    intent_budget = intent.get("budget", {})
    max_per_invocation = min(
        float(limits.get("max_per_invocation", 0.0)),
        float(intent_budget.get("max_per_invocation", 0.0)),
    )
    if terms.get("currency") != limits.get("currency"):
        reject(reasons, "currency_mismatch")
    elif float(terms.get("price_per_invocation", 999999.0)) > max_per_invocation:
        reject(reasons, "price_exceeds_budget")
    else:
        checks.append("commercial_terms_within_budget")

    governance = record.get("governance", {})
    if not governance.get("supports_audit_log") or not governance.get("supports_revocation"):
        reject(reasons, "audit_or_revocation_missing")
    else:
        checks.append("audit_and_revocation_supported")

    if policy.get("require_human_approval", True) and not governance.get("requires_human_approval"):
        reject(reasons, "human_approval_not_required_by_candidate")
    else:
        checks.append("human_approval_required")

    if reasons:
        return None, {"agent_id": agent_id, "reasons": reasons}

    assert selected_protocol is not None
    accepted = {
        "agent_id": agent_id,
        "agent_name": record.get("agent_name", agent_id),
        "capability": required_capability,
        "selected_protocol": selected_protocol["type"],
        "endpoint": selected_protocol["endpoint"],
        "price_per_invocation": terms["price_per_invocation"],
        "metering_unit": terms["metering_unit"],
        "quality_score": quality_score,
        "risk": risk,
        "enabled": False,
        "human_approval_required": True,
        "governance_checks": checks,
    }
    return accepted, None


def build_plan(intent: dict[str, Any], index: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    verified_imports: list[dict[str, Any]] = []
    rejected_candidates: list[dict[str, Any]] = []

    for record in index.get("records", []):
        accepted, rejected = evaluate_record(record, intent, policy)
        if accepted:
            verified_imports.append(accepted)
        if rejected:
            rejected_candidates.append(rejected)

    return {
        "intent_id": intent["intent_id"],
        "status": "awaiting_human_approval" if verified_imports else "blocked_no_verified_imports",
        "verified_imports": verified_imports,
        "rejected_candidates": rejected_candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intent", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    args = parser.parse_args()

    plan = build_plan(load_json(args.intent), load_json(args.index), load_json(args.policy))
    print(json.dumps(plan, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
