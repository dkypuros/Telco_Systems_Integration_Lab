import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE_SOURCE_DIRS = [
    ROOT / "services" / "mock_5g_core",
    ROOT / "adapters" / "mock_ran",
]

UNSAFE_PATTERNS = [
    re.compile(r"100%\s+Compliant", re.IGNORECASE),
    re.compile(r"3GPP[- ]compliant", re.IGNORECASE),
    re.compile(r"O-RAN\s+complete", re.IGNORECASE),
    re.compile(r"TMF\s+compliant", re.IGNORECASE),
    re.compile(r"compliant\s+implementation", re.IGNORECASE),
    re.compile(r"\"compliance\"\s*:"),
    re.compile(r"\bconformant\b", re.IGNORECASE),
]


def iter_live_source_files():
    for base in LIVE_SOURCE_DIRS:
        for path in base.rglob("*.py"):
            if "__pycache__" not in path.parts:
                yield path


def test_live_mock_source_uses_bounded_standards_wording():
    findings = []
    for path in iter_live_source_files():
        text = path.read_text(encoding="utf-8")
        for pattern in UNSAFE_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: {match.group(0)}")
    assert not findings, "Unsupported standards-claim wording found:\n" + "\n".join(findings)
