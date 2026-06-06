import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "modules" / "index.json"


def test_modules_index_reserves_unique_ports_and_existing_paths():
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    ports = [item["port"] for item in index["reserved_ports"]]

    assert len(ports) == len(set(ports))
    assert 8765 in ports
    for item in index["reserved_ports"]:
        assert (ROOT / item["path"]).exists()


def test_modules_index_matches_module_metadata():
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    for module in index["modules"]:
        metadata_path = ROOT / module["path"] / "module.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["id"] == module["id"]
        assert metadata["default_port"] == module["default_port"]
        assert metadata["entrypoint"] == module["entrypoint"]
        assert "not formal" in metadata["claim_boundary"].lower()



def test_each_module_readme_declares_dependencies_lifecycle_and_boundary():
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    required_headings = ["## Dependencies", "## Run", "## Stop", "## Special commands", "## Boundary"]

    for module in index["modules"]:
        readme = (ROOT / module["path"] / "README.md").read_text(encoding="utf-8")
        for heading in required_headings:
            assert heading in readme, f"{module['id']} missing {heading}"
        assert "./lab up" in readme
        assert "./lab down" in readme


def test_module_dependency_references_point_to_registered_modules():
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    module_ids = {module["id"] for module in index["modules"]}

    for module in index["modules"]:
        for field in ["depends_on", "recommended_with"]:
            for referenced_id in module.get(field, []):
                assert referenced_id in module_ids, f"{module['id']} {field} references unknown module {referenced_id}"


def test_chatter_recommends_scenario_generator_and_runtime_dependency():
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    chatter = next(module for module in index["modules"] if module["id"] == "lab-chatter-service")
    generator = next(module for module in index["modules"] if module["id"] == "ue-scenario-generator")

    assert chatter["depends_on"] == ["lab-runtime"]
    assert "ue-scenario-generator" in chatter["recommended_with"]
    assert generator["depends_on"] == ["lab-runtime"]
    assert "lab-chatter-service" in generator["recommended_with"]
