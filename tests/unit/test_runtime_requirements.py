from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_requirements_include_imported_packages():
    requirements = (ROOT / "config" / "requirements.txt").read_text().splitlines()
    normalized = {line.split("[")[0].lower() for line in requirements if line and not line.startswith("#")}
    for package in ["fastapi", "uvicorn", "httpx", "requests", "opentelemetry-api", "prometheus_client", "pytest", "pyjwt"]:
        assert package.lower() in normalized


def test_runtime_plan_carries_no_conformance_claim():
    plan = (ROOT / "docs" / "runtime_integration_plan.md").read_text().lower()
    assert "not formal" in plan or "not be used as formal" in plan
    assert "conformance" in plan
