"""Independent disease readers preserve stated identity and expose support gaps."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path("examples/user_journeys/disease_entities.py").resolve()
DATA = Path("temp_data").resolve()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def invoke(action, output):
    command = [sys.executable, str(SCRIPT)]
    if action == "read":
        command = [sys.executable, "-c", """
import runpy, sys
from pathlib import Path
import ackredit, sabueso
from sabueso.core.card import Card
from sabueso.core.deck import Deck
def forbidden(*args, **kwargs):
    raise RuntimeError('A historical reader cannot acquire, derive or generate credit')
ackredit.register_item = ackredit.track_item = forbidden
sabueso.resolve = sabueso.disease_targets = sabueso.disease_drugs = forbidden
Card.diseases = Card.explain_disease = Card.knowledge_state = forbidden
Deck.explain = forbidden
sabueso.__version__ = '999.reader'
script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).parent))
runpy.run_path(script, run_name='__main__')
""", str(SCRIPT)]  # fmt: skip
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [*command, action, "--output", str(output), "--fixtures",
         str(DATA if action != "read" else output / "no-fixtures")],
        cwd=output.parent, env=env, capture_output=True, text=True,
        timeout=180, check=False,
    )  # fmt: skip


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    output = tmp_path_factory.mktemp("disease-entities") / "bundle"
    for action in ("produce", "read", "reacquire", "read"):
        result = invoke(action, output)
        assert result.returncode == 0, result.stdout + result.stderr
    return output


def test_saved_disease_identity_membership_grouping_and_partial_credit(bundle):
    original, later = [
        load(bundle / f"{s}.manifest.json") for s in ("original", "later")
    ]
    assert all(original["cards"][r] != later["cards"][r] for r in original["cards"])
    assert all(original["decks"][r] != later["decks"][r] for r in original["decks"])
    report = load(bundle / "original.report.json")
    reader = load(bundle / "original.reader.json")
    assert reader["original_report"] == report and reader["observed_acquisitions"] == 0
    identity = report["resolutions"]["target_disease"]["decision"]["identity"]
    assert (
        identity["rule"] == "mondo_equivalence@1"
        and identity["release"] == "2026-09-01"
    )
    assert identity["equivalent_id"] == "Orphanet:868"
    unresolved = report["resolutions"]["unresolved"]
    assert unresolved["status"] == "not_found"
    assert unresolved["decision"]["rules"] == ["no_stated_equivalence"]
    targets = report["decks_report"]["targets"]
    assert targets["built_count"] == 1
    assert {e["reason"] for e in targets["meta"]["excluded"]} >= {
        "limit",
        "card_not_built",
    }
    basis = targets["explanations"][0]["basis"]
    assert basis["rule"] == "disease_targets@2"
    assert targets["explanations"][0]["support"]["status"] == "recorded"
    assert all(
        e["support"]["status"] == "recorded" for e in targets["excluded_explanations"]
    )
    assert {s["source"] for s in basis["statements"]} == {"Open Targets", "Orphanet"}
    ot = next(s for s in basis["statements"] if s["source"] == "Open Targets")
    assert ot["version"] == "26.09" and ot["score"] == pytest.approx(0.7826557233644024)
    # Source rows, attempted candidates and successfully built cards differ.
    source = next(
        s for s in targets["meta"]["sources"] if s["source"] == "Open Targets"
    )
    assert (
        source["count"] == 20 and source["total_count"] == 252 and source["truncated"]
    )
    drugs = report["decks_report"]["drugs"]
    indications = drugs["explanations"][0]["basis"]["indications"]
    assert drugs["built_count"] == 1 and len(indications) == 2
    assert {i["max_phase_for_ind"] for i in indications} == {"4.0"}
    assert {i["efo_id"] for i in indications} == {"EFO:0008559", "MONDO:0001444"}
    assert (
        report["scope"]["trials"] == "not_queried"
        and report["scope"]["efficacy"] == "not_assessed"
    )
    group = report["group_explanation"]
    assert group["rule"]["rule"] == "disease_group_explanation@3"
    assert group["grouping_rule"]["rule"] == "disease_grouping@3"
    assert group["group"]["sources"] == [
        "ClinVar",
        "DISEASES",
        "Open Targets",
        "Orphanet",
        "UniProt",
    ]
    assert {u["reason"] for u in report["groups"]["ungrouped"]} >= {
        "no_stated_equivalence",
        "no_id_stated",
        "condition_not_provided",
        "incomplete_identity",
    }
    assert (
        report["gaps"]["membership_source_assertion_pins"]
        == "recorded_by_disease_deck_rules@2"
    )
    observed = load(bundle / "original.observations.json")["acquisitions"]
    assert all(r["network_attempts"] == 0 for r in observed)
    assert {r["source"] for r in observed} == {
        "UniProt",
        "ChEMBL",
        "UniChem",
        "MONDO",
        "Open Targets",
        "Orphanet",
        "DISEASES",
        "ClinVar",
        "MedGen",
    }
    assert "MONDO" not in report["gaps"]["observation"]
    assert report["gaps"]["observation"] == []
    assert any(
        r["source"] == "MONDO"
        and r["operation"] == "equivalent"
        and r["outcome"] == "empty"
        for r in observed
    )
    assert any(
        r["source"] == "UniProt" and r["outcome"] == "unavailable" for r in observed
    )
    assert any(r["operation"] == "indications_for" for r in observed)
    assert all(r["producer"]["version"] != "999.reader" for r in observed)
    assert load(bundle / "original.references.csl.json")
    assert (bundle / "original.references.bib").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "defect",
    [
        "missing",
        "trace",
        "deck_trace",
        "membership",
        "disease",
        "group",
        "item",
        "coverage",
    ],
)
def test_reader_refuses_changed_or_misbound_support_before_export(
    bundle, tmp_path, defect
):
    output = tmp_path / "copy"
    shutil.copytree(bundle, output)
    manifest_path = output / "original.manifest.json"
    manifest = load(manifest_path)
    if defect == "missing":
        (output / "original.workflow.json").unlink()
    elif defect == "item":
        manifest["assertions"]["target_disease"] = manifest["assertions"][
            "drug_disease"
        ]
    else:
        filename = (
            "original.traces.json"
            if defect in ("trace", "deck_trace")
            else "original.report.json"
        )
        path = output / filename
        value = load(path)
        if defect == "trace":
            value["cards"]["target"]["card_ref"] = manifest["cards"]["target_context"]
        elif defect == "deck_trace":
            value["decks"]["targets"]["input_card_refs"] = [
                manifest["cards"]["drug_disease"]
            ]
        elif defect == "membership":
            value["decks_report"]["targets"]["explanations"][0]["basis"]["statements"][
                0
            ]["score"] = 1.0
        elif defect == "disease":
            value["decks_report"]["targets"]["members"] = [manifest["cards"]["drug"]]
        elif defect == "coverage":
            value["gaps"]["membership_source_assertion_pins"] = "complete"
        else:
            value["group_explanation"]["statements"][0]["input"]["source_assertions"][
                0
            ]["asserted_value"] = {"different": "disease statement"}
        path.write_text(json.dumps(value), encoding="utf-8")
        manifest["files"][filename] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    references = output / "original.references.csl.json"
    references.unlink()
    result = invoke("read", output)
    assert result.returncode == 2 and "FAIL:" in result.stderr, (
        result.stdout + result.stderr
    )
    assert not references.exists()


def test_completed_stages_cannot_be_overwritten(bundle):
    before = (bundle / "original.manifest.json").read_bytes()
    assert invoke("produce", bundle).returncode == 2
    assert invoke("reacquire", bundle).returncode == 2
    assert (bundle / "original.manifest.json").read_bytes() == before
