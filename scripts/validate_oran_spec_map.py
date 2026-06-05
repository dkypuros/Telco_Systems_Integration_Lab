#!/usr/bin/env python3
"""Validate O-RAN spec-map references against repo paths and a local catalog.

This is a traceability/readiness validator only. It checks whether each row in
``adapters/mock_oran/oran/o_ran_spec_map.py`` points at an implementation file
that exists in this repository and, when a local O-RAN catalog is supplied,
whether the referenced specification filename stem exists in that catalog.
It does not parse or redistribute raw standards documents and does not assert
formal O-RAN conformance.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
SPEC_MAP_PATH = ROOT / "adapters" / "mock_oran" / "oran" / "o_ran_spec_map.py"
DEFAULT_SPEC_DIRS = (
    ROOT / "specs" / "oran" / "Latest_Versions",
    ROOT.parent.parent.parent.parent / "specs" / "oran" / "Latest_Versions",
)
IMPLEMENTATION_PREFIXES = (
    Path(""),
    Path("adapters/mock_oran"),
    Path("adapters/mock_ran"),
    Path("services/mock_5g_core"),
    Path("tests"),
)
SPEC_EXTENSIONS = (".pdf", ".docx", ".zip")


def load_spec_map(path: Path = SPEC_MAP_PATH) -> List[Dict[str, Any]]:
    """Load SPEC_MAP from the copied O-RAN mapping module without importing packages."""
    spec = importlib.util.spec_from_file_location("_oran_spec_map_for_validation", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load spec map from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    rows = getattr(module, "SPEC_MAP", None)
    if not isinstance(rows, list):
        raise RuntimeError(f"{path} does not expose a list named SPEC_MAP")
    return [dict(row) for row in rows]


def default_spec_dir() -> Optional[Path]:
    """Return the first available local O-RAN catalog directory, if any."""
    env_dir = os.environ.get("ORAN_SPEC_CATALOG_DIR")
    candidates = [Path(env_dir).expanduser()] if env_dir else []
    candidates.extend(DEFAULT_SPEC_DIRS)
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    return None


def catalog_index(spec_dir: Optional[Path]) -> Dict[str, Path]:
    """Build a filename-stem index for local raw spec files without reading them."""
    if spec_dir is None or not spec_dir.is_dir():
        return {}
    indexed: Dict[str, Path] = {}
    for path in sorted(spec_dir.iterdir()):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in SPEC_EXTENSIONS:
            continue
        stem = path.stem.strip()
        indexed.setdefault(stem, path)
    return indexed


def candidate_module_paths(module_path: str) -> Iterable[Path]:
    raw = Path(module_path)
    for prefix in IMPLEMENTATION_PREFIXES:
        yield (ROOT / prefix / raw).resolve()


def resolve_module_path(module_path: str) -> Optional[Path]:
    """Resolve a mapped module path against known copied-code roots."""
    for candidate in candidate_module_paths(module_path):
        if candidate.is_file():
            return candidate
    return None


def relative_or_none(path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def display_catalog_path(path: Optional[Path]) -> Optional[str]:
    """Return a public-safe catalog path for reports."""
    if path is None:
        return None
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return "<external O-RAN spec catalog>"


def validate_rows(rows: Sequence[Mapping[str, Any]], spec_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Validate mapped implementation paths and optional local catalog filenames."""
    index = catalog_index(spec_dir)
    row_results: List[Dict[str, Any]] = []
    seen_specs: Dict[str, int] = {}
    seen_modules: Dict[str, int] = {}

    for row in rows:
        spec_name = str(row.get("spec", ""))
        module_name = str(row.get("module", ""))
        seen_specs[spec_name] = seen_specs.get(spec_name, 0) + 1
        seen_modules[module_name] = seen_modules.get(module_name, 0) + 1
        resolved_module = resolve_module_path(module_name)
        matched_spec = index.get(spec_name)
        row_results.append(
            {
                "wg": row.get("wg"),
                "spec": spec_name,
                "title": row.get("title"),
                "status": row.get("status"),
                "module": module_name,
                "module_exists": resolved_module is not None,
                "resolved_module_path": relative_or_none(resolved_module),
                "spec_file_exists": matched_spec is not None if spec_dir else None,
                "resolved_spec_file": matched_spec.name if matched_spec else None,
            }
        )

    module_existing = sum(1 for item in row_results if item["module_exists"])
    spec_checked = spec_dir is not None
    spec_existing = sum(1 for item in row_results if item["spec_file_exists"] is True)
    duplicate_specs = sorted(name for name, count in seen_specs.items() if count > 1)
    duplicate_modules = sorted(name for name, count in seen_modules.items() if count > 1)

    return {
        "summary": {
            "claim_boundary": "candidate/readiness validation only; not formal O-RAN conformance evidence",
            "spec_map_path": relative_or_none(SPEC_MAP_PATH),
            "rows_total": len(row_results),
            "module_paths_existing": module_existing,
            "module_paths_missing": len(row_results) - module_existing,
            "local_spec_catalog_checked": spec_checked,
            "local_spec_catalog_dir": display_catalog_path(spec_dir),
            "local_spec_files_indexed": len(index),
            "spec_files_existing": spec_existing if spec_checked else None,
            "spec_files_missing": (len(row_results) - spec_existing) if spec_checked else None,
            "duplicate_specs": duplicate_specs,
            "duplicate_modules": duplicate_modules,
        },
        "rows": row_results,
    }


def markdown_report(result: Mapping[str, Any]) -> str:
    summary = result["summary"]
    rows = result["rows"]
    lines = [
        "# O-RAN spec-map validation report",
        "",
        "This is a derived traceability/readiness artifact. It validates candidate map references; it is not a formal O-RAN conformance claim.",
        "",
        "## Summary",
        "",
        f"- Spec map: `{summary['spec_map_path']}`",
        f"- Rows checked: {summary['rows_total']}",
        f"- Implementation paths existing: {summary['module_paths_existing']}",
        f"- Implementation paths missing: {summary['module_paths_missing']}",
        f"- Local spec catalog checked: {summary['local_spec_catalog_checked']}",
    ]
    if summary["local_spec_catalog_checked"]:
        lines.extend(
            [
                f"- Local spec catalog: `{summary['local_spec_catalog_dir']}`",
                f"- Local spec files indexed: {summary['local_spec_files_indexed']}",
                f"- Spec filename stems existing: {summary['spec_files_existing']}",
                f"- Spec filename stems missing: {summary['spec_files_missing']}",
            ]
        )
    else:
        lines.append("- Local spec catalog: not available; pass `--spec-dir` or set `ORAN_SPEC_CATALOG_DIR` to check spec filenames.")
    lines.extend(
        [
            f"- Duplicate spec keys: {', '.join(summary['duplicate_specs']) if summary['duplicate_specs'] else 'none'}",
            f"- Duplicate mapped module keys: {', '.join(summary['duplicate_modules']) if summary['duplicate_modules'] else 'none'}",
            "",
            "## Missing implementation paths",
            "",
        ]
    )
    missing_modules = [row for row in rows if not row["module_exists"]]
    if missing_modules:
        lines.append("| WG | Spec | Mapped module | Candidate status |")
        lines.append("|---|---|---|---|")
        for row in missing_modules:
            lines.append(f"| {row['wg']} | `{row['spec']}` | `{row['module']}` | missing repo path |")
    else:
        lines.append("No missing mapped implementation paths.")
    lines.extend(["", "## Missing local spec filenames", ""])
    if summary["local_spec_catalog_checked"]:
        missing_specs = [row for row in rows if row["spec_file_exists"] is False]
        if missing_specs:
            lines.append("| WG | Spec stem | Mapped module | Candidate status |")
            lines.append("|---|---|---|---|")
            for row in missing_specs:
                lines.append(f"| {row['wg']} | `{row['spec']}` | `{row['module']}` | missing local spec file |")
        else:
            lines.append("No missing local spec filename stems.")
    else:
        lines.append("Spec filename check skipped because no local catalog directory was available.")
    lines.extend(["", "## Resolved mapped paths", ""])
    lines.append("| WG | Spec | Mapped module | Resolved repo path | Local spec file |")
    lines.append("|---|---|---|---|---|")
    for row in rows:
        resolved = f"`{row['resolved_module_path']}`" if row["resolved_module_path"] else "missing"
        spec_file = f"`{row['resolved_spec_file']}`" if row["resolved_spec_file"] else ("missing" if summary["local_spec_catalog_checked"] else "not checked")
        lines.append(f"| {row['wg']} | `{row['spec']}` | `{row['module']}` | {resolved} | {spec_file} |")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=None, help="Local O-RAN Latest_Versions catalog directory; filenames only are inspected.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path, default=None, help="Optional output file path.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when module or checked spec-file gaps are found.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    spec_dir = args.spec_dir.resolve() if args.spec_dir else default_spec_dir()
    result = validate_rows(load_spec_map(), spec_dir)
    rendered = markdown_report(result) if args.format == "markdown" else json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + ("" if rendered.endswith("\n") else "\n"))
    else:
        print(rendered)

    summary = result["summary"]
    has_module_gaps = bool(summary["module_paths_missing"])
    has_spec_gaps = bool(summary["local_spec_catalog_checked"] and summary["spec_files_missing"])
    return 1 if args.strict and (has_module_gaps or has_spec_gaps) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
