import json
import subprocess
import sys
from pathlib import Path


def test_mock_service_smoke_passes_with_runtime_dependencies():
    result = subprocess.run(
        [sys.executable, "scripts/mock_service_smoke.py"],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout[result.stdout.index("{"):])
    assert data["status"] == "pass"
    assert data["ast"]["count"] >= 25
    assert data["ast"]["errors"] == []
    assert data["imports"]["missing_dependencies"] == []
    assert data["imports"]["errors"] == []
    assert "core_network.amf" in data["imports"]["imported"]
    assert "api_gateway.oran_gateway" in data["imports"]["imported"]
