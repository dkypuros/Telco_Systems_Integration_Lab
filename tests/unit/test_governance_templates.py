from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_LABELS = [
    "reference_only",
    "planned",
    "partial",
    "functional_smoke",
    "demo_evidence",
    "formal_conformance_missing",
    "conformance_candidate",
    "formal_conformance_evidence",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_capability_issue_form_requires_standards_evidence_fields():
    form = read(".github/ISSUE_TEMPLATE/capability-slice.yml")
    parsed = yaml.safe_load(form)
    assert parsed["name"] == "Standards-traceable capability issue"
    for field in [
        "capability_slice",
        "standards_scope",
        "current_evidence_label",
        "target_evidence_label",
        "implementation_paths",
        "tests_evidence",
        "known_gap",
        "source_intake_boundary",
        "verification",
    ]:
        assert field in form
    for label in ALLOWED_LABELS:
        assert label in form
    assert "This issue will not copy a full upstream source tree." in form


def test_external_profile_template_blocks_source_tree_absorption():
    template = read("vendor_profiles/TEMPLATE.md")
    readme = read("vendor_profiles/README.md")
    open5gs = read("vendor_profiles/open5gs/profile.yaml")
    combined = "\n".join([template, readme, open5gs]).lower()

    for phrase in [
        "not vendored source trees",
        "full upstream source copied into this repository: **no**".lower(),
        "full_upstream_source_copied: false",
        "copy_manifest.csv",
        "source_inventory.csv",
    ]:
        assert phrase in combined

    for field in [
        "upstream url",
        "tag, commit, release, or image digest",
        "license",
        "standards families touched",
        "current standards-evidence label",
        "known gap to latest/formal conformance",
    ]:
        assert field in template.lower()


def test_adapter_contract_template_separates_lab_boundary_from_external_runtime():
    template = read("adapters/ADAPTER_CONTRACT_TEMPLATE.md").lower()
    for phrase in [
        "lab-owned path",
        "external profile path",
        "correlation id behavior",
        "external-runtime skip behavior",
        "full upstream source remains outside the repository",
        "interoperability tests",
        "no standards-conformance claim",
    ]:
        assert phrase in template
