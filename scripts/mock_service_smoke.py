#!/usr/bin/env python3
"""Non-mutating runtime smoke checks for copied mock services.

Checks:
1. Every copied Python file still parses with ast.parse.
2. Runtime import paths are sufficient for import-level checks when optional
   dependencies are installed.
3. Reports missing dependencies explicitly instead of hiding them.

This is an integration readiness smoke, not standards conformance evidence.
"""
from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

LAB_ROOT = Path(__file__).resolve().parents[1]
# Add runtime paths in process; keep copied source files untouched.
for rel in [
    "services/mock_5g_core",
    "services/assurance",
    "adapters/mock_ran",
    "adapters/mock_ran/ran/ric",
    "adapters/mock_oran",
]:
    p = str(LAB_ROOT / rel)
    if p not in sys.path:
        sys.path.insert(0, p)

COPIED_PY_ROOTS = [
    LAB_ROOT / "services" / "mock_5g_core",
    LAB_ROOT / "services" / "assurance",
    LAB_ROOT / "adapters" / "mock_ran",
    LAB_ROOT / "adapters" / "mock_oran",
]
IMPORT_TARGETS = [
    "config.ports",
    "core_network.transport",
    "core_network.nrf",
    "core_network.amf",
    "core_network.smf",
    "core_network.upf",
    "core_network.udm",
    "core_network.udr",
    "core_network.ausf",
    "core_network.nssf",
    "core_network.udsf",
    "ran.gnb",
    "ran.cu",
    "ran.cu.cu",
    "ran.du",
    "ran.du.du",
    "ran.rru.rru",
    "ptp.ptp",
    "e2sm_ni",
    "e2sm_ccc",
    "e2sm_llc",
    "e2ap",
    "ran.ric.near_rt_ric",
    "ran.ric.non_rt_ric",
    "ran.ric.y1",
    "ran.fronthaul.cus_plane",
    "ran.fronthaul.m_plane",
    "ran.fronthaul.o_ru",
    "ran.slicing.oran_slicing",
    "ran.energy.nes",
    "ran.ntn_radio",
    "service_assurance.assurance_api",
    "smo.smo_framework",
    "smo.r1",
    "oam.o1",
    "oam.teiv",
    "etsi.o2.o_cloud_notification",
    "security.security_service",
    "transport.xhaul",
    "oran.o_ran_spec_map",
    "api_gateway.oran_gateway",
]


def ast_check() -> Dict[str, Any]:
    checked: List[str] = []
    errors: List[Dict[str, str]] = []
    for root in COPIED_PY_ROOTS:
        for path in sorted(root.rglob("*.py")):
            rel = str(path.relative_to(LAB_ROOT))
            try:
                ast.parse(path.read_text())
                checked.append(rel)
            except Exception as exc:
                errors.append({"path": rel, "error": repr(exc)})
    return {"checked": checked, "errors": errors}


def import_check() -> Dict[str, Any]:
    imported: List[str] = []
    missing_dependencies: List[Dict[str, str]] = []
    errors: List[Dict[str, str]] = []
    for name in IMPORT_TARGETS:
        try:
            importlib.import_module(name)
            imported.append(name)
        except ModuleNotFoundError as exc:
            missing_dependencies.append({"module": name, "missing": exc.name or "unknown", "error": str(exc)})
        except Exception as exc:
            errors.append({"module": name, "error": repr(exc)})
    return {"imported": imported, "missing_dependencies": missing_dependencies, "errors": errors}


def main() -> int:
    ast_result = ast_check()
    import_result = import_check()
    result = {
        "status": "pass" if not ast_result["errors"] and not import_result["errors"] and not import_result["missing_dependencies"] else "blocked",
        "interpretation": "runtime smoke only; not formal 3GPP/O-RAN conformance",
        "pythonpath_entries": [str(p) for p in sys.path[:4]],
        "ast": {"count": len(ast_result["checked"]), "errors": ast_result["errors"]},
        "imports": import_result,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
