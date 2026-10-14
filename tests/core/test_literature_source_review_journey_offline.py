"""Located proposals preserve source support without inventing human curation."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path("examples/user_journeys/literature_source_review.py").resolve()
DATA = Path("temp_data").resolve()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def invoke(action, output):
    prefix = [sys.executable, str(SCRIPT)]
    if action == "read":
        prefix = [
            sys.executable,
            "-c",
            """
import runpy, sys
from pathlib import Path
import ackredit, sabueso
from sabueso.core.card import Card
from sabueso.core.curation_store import CurationStore

def forbidden(*a, **k): raise AssertionError('Reader cannot acquire, derive, curate or create credit')
ackredit.register_item = ackredit.track_item = forbidden
for name in ('resolve', 'refresh_card', 'compose_packet', 'knowledge_packet'):
    setattr(sabueso, name, forbidden)
for name in ('claims', 'literature', 'add_literature_claim', 'add_literature_assertion', 'explain_literature'):
    setattr(Card, name, forbidden)
CurationStore.save = CurationStore.apply = forbidden
sabueso.__version__ = '999.reader'
script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).parent))
runpy.run_path(script, run_name='__main__')
""",
            str(SCRIPT),
        ]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [
            *prefix,
            action,
            "--output",
            str(output),
            "--fixtures",
            str(DATA if action == "produce" else output / "no-fixtures"),
        ],
        cwd=output.parent,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    output = tmp_path_factory.mktemp("located-source") / "bundle"
    for action in ("produce", "read", "read"):
        result = invoke(action, output)
        assert result.returncode == 0, result.stdout + result.stderr
    return output


def test_native_locations_and_agent_draft_survive_inert_read_without_intake(bundle):
    report = load(bundle / "report.json")
    assert report["format"] == "sabueso.located_source_review_example@2"
    assert report["review"] == {
        "preparer": "Codex",
        "kind": "agent",
        "scientist_review": "pending",
        "status": "draft_only",
    }
    assert (
        report["source"]["native_xml_sha256"]
        == "eff2c488e4b17ded8e30530b98ff949fdada1294329c957d26e6ab71945abfef"
    )
    assert len(report["proposals"]) == 2
    assert report["scope"]["literature_SourceAssertions_created"] is False
    assert report["scope"]["human_curation"] == "not_performed"
    assert set(report["cards"]) == {"baseline"}
    assert not (bundle / "curations.jsonl").exists()
    assert report["scope"]["other_organism_findings_transferred"] is False
    assert report["scope"]["inhibition_or_selectivity"] == "not_established"
    runtime = load(bundle / "runtime.json")
    assert runtime["draft_preparation_observation"] == "not_observed"
    assert all(
        item["access"] == "fixture" and item["network_attempts"] == 0
        for item in runtime["acquisitions"]
    )
    assert report["producer"]["sabueso"] != "999.reader"
    assert (bundle / "original.references.csl.json").is_file()
    assert (bundle / "original.references.bib").is_file()


@pytest.mark.parametrize(
    "change",
    [
        "quote",
        "source_bytes",
        "claim",
        "subject",
        "identity_support",
        "human_acceptance",
        "scientific_scope",
        "draft_sidecar",
        "runtime_credit",
        "human_output",
    ],
)
def test_rehashed_scientific_or_provenance_changes_are_rejected(
    bundle, tmp_path, change
):
    output = tmp_path / "bundle"
    shutil.copytree(bundle, output)
    report = load(output / "report.json")
    if change == "source_bytes":
        path = output / "source.xml"
        path.write_bytes(path.read_bytes() + b"\n")
        report["source"]["native_xml_sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    elif change == "quote":
        report["proposals"][0]["quote"] = "Invented source quotation."
    elif change == "claim":
        report["proposals"][0]["text"] = "The source proves inhibition in humans."
    elif change == "subject":
        report["subject"] = "uniprot:P52270"
    elif change == "identity_support":
        report["identity_basis"]["source_assertion_refs"] = []
    elif change == "human_acceptance":
        report["review"]["scientist_review"] = "accepted"
    elif change == "scientific_scope":
        report["scope"]["other_organism_findings_transferred"] = True
    elif change == "draft_sidecar":
        path = output / "proposals.json"
        draft = load(path)
        draft["review"]["status"] = "accepted_knowledge"
        path.write_text(json.dumps(draft))
    elif change == "runtime_credit":
        runtime = load(output / "runtime.json")
        runtime["workflow"]["uses"] = []
        (output / "runtime.json").write_text(json.dumps(runtime))
    else:
        (output / "review.md").write_text("Scientist reviewed and approved inhibition.")
    (output / "report.json").write_text(json.dumps(report))
    manifest = load(output / "manifest.json")
    for name in manifest["files"]:
        manifest["files"][name] = hashlib.sha256(
            (output / name).read_bytes()
        ).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest))
    result = invoke("read", output)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "PASS:" not in result.stdout


def test_missing_original_store_fails_without_creating_a_replacement(bundle, tmp_path):
    output = tmp_path / "bundle"
    shutil.copytree(bundle, output)
    (output / "knowledge.db").unlink()
    result = invoke("read", output)
    assert result.returncode != 0
    assert not (output / "knowledge.db").exists()


def test_altered_original_bibliography_is_rejected_and_not_overwritten(
    bundle, tmp_path
):
    output = tmp_path / "bundle"
    shutil.copytree(bundle, output)
    target = output / "original.references.bib"
    target.write_text("altered original bibliography")
    result = invoke("read", output)
    assert result.returncode != 0
    assert target.read_text() == "altered original bibliography"


def test_agent_curation_format_is_rejected_as_unqualified(bundle, tmp_path):
    output = tmp_path / "bundle"
    shutil.copytree(bundle, output)
    manifest = load(output / "manifest.json")
    manifest["format"] = "sabueso.located_source_review_example@1"
    (output / "manifest.json").write_text(json.dumps(manifest))
    result = invoke("read", output)
    assert result.returncode != 0
    assert "does not qualify agent readings as human curation" in result.stderr
