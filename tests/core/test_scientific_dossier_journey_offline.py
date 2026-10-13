"""A scientist-facing dossier retains exact support and truthful review scope."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path("examples/user_journeys/scientific_dossier.py").resolve()
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
import runpy,sys
import ackredit,sabueso
from sabueso.core.card import Card
from sabueso.core.deck import Deck
def forbidden(*a,**k):raise AssertionError('Reader cannot acquire, derive or create credit')
ackredit.register_item=ackredit.track_item=forbidden
for name in ('resolve','refresh_card','ligand_deck','compose_packet','knowledge_packet'):
    setattr(sabueso,name,forbidden)
for name in ('structures','bioactivities','literature','get_residues','explain_literature','explain_bioactivity','knowledge_state'):
    setattr(Card,name,forbidden)
Deck.structure_inventory=forbidden
sabueso.__version__='999.reader'
script=sys.argv.pop(1)
sys.path.insert(0,str(__import__('pathlib').Path(script).parent))
runpy.run_path(script,run_name='__main__')
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
            str(DATA if action != "read" else output / "no-fixtures"),
        ],
        env=env,
        cwd=output.parent,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    output = tmp_path_factory.mktemp("scientific-dossier") / "bundle"
    for action in ("produce", "read", "reacquire", "read"):
        result = invoke(action, output)
        assert result.returncode == 0, result.stdout + result.stderr
    return output


def test_declared_structure_criteria_keep_reference_mutant_fragment_and_unknown_scope(
    bundle,
):
    report = load(bundle / "original.dossier.json")
    subject = report["proteins"]["subject"]
    comparator = report["proteins"]["comparator"]
    rows = {
        row["item"]["structure_ref"]: row
        for row in subject["structures"]["rows"] + comparator["structures"]["rows"]
    }
    assert (
        rows["pdb:1SUX"]["status"]
        == rows["pdb:1HTI"]["status"]
        == "meets_recorded_criteria"
    )
    assert rows["pdb:2V5B"]["item"]["oligomer_disagreement"] is True
    assert rows["pdb:2V5B"]["item"]["state"]["oligomer"] == "Monomer"
    assert rows["pdb:2V5B"]["checks"]["oligomer"]["status"] == "not_met"
    assert rows["pdb:2VOM"]["checks"]["sequence"]["status"] == "not_met"
    assert rows["pdb:1KLG"]["checks"]["coverage"]["status"] == "not_met"
    assert any(row["status"] == "insufficient_information" for row in rows.values())
    assert all(
        row["project_model_selection"] == "not_performed" for row in rows.values()
    )
    assert subject["structures"]["cross_protein_correspondence"] == "not_supplied"
    assert subject["source_scope"]["activity_limit_per_source"] == 25
    assert any(
        row.get("state") == "partial" and row.get("basis", {}).get("truncated_for")
        for row in subject["knowledge_state"]["rows"]
    )


def test_assay_eligibility_is_separate_from_comparability_and_source_quantities(bundle):
    report = load(bundle / "original.dossier.json")
    rows = [
        row
        for protein in report["proteins"].values()
        for row in protein["assays"]["rows"]
    ]
    assert any(row["status"] == "meets_recorded_criteria" for row in rows)
    assert any(row["checks"]["measurement_type"]["status"] == "not_met" for row in rows)
    assert all(
        row["experimental_comparability"] == "requires_human_review" for row in rows
    )
    assert all(row["source_assertion_refs"] for row in rows)
    assert any(
        row["qualifiers"]["measurement"].get("normalized", {}).get("unit")
        == "nanomolar"
        for row in rows
    )


def test_real_located_article_mention_does_not_become_a_mechanistic_claim(bundle):
    report = load(bundle / "original.dossier.json")
    literature = report["proteins"]["comparator"]["literature"]
    (mention,) = literature["located_mentions"]
    assert mention["publication_ref"] == "pubmed:40832834"
    assert mention["qualifiers"]["locations"][0]["annotation"]["exact"] == "P60174"
    assert literature["curated_mechanistic_claims"] == "not_performed"
    assert literature["project_Evidence"] == "not_created"
    assert (
        report["proteins"]["subject"]["literature"]["coverage"]
        == "no_located_match_in_requested_response"
    )


def test_independent_reader_retains_original_producer_results_pins_and_credit_after_reacquisition(
    bundle,
):
    original = load(bundle / "original.manifest.json")
    later = load(bundle / "later.manifest.json")
    assert all(
        original["cards"][role] != later["cards"][role] for role in original["cards"]
    )
    report = load(bundle / "original.dossier.json")
    retained = load(bundle / "original.reader.json")
    assert retained["original_report"] == report
    assert report["producer"]["sabueso"] != "999.reader"
    assert (
        retained["new_acquisitions"],
        retained["new_derivations"],
        retained["new_credit"],
    ) == (0, 0, 0)
    assert len(report["producer"]["example_source_sha256"]) == 64
    runtime = load(bundle / "original.runtime.json")
    assert all(
        operation["network_attempts"] == 0 for operation in runtime["acquisitions"]
    )
    assert (bundle / "original.references.bib").read_text(encoding="utf-8")
    assert {row["id"] for row in load(bundle / "original.references.csl.json")} == {
        row["id"] for row in runtime["workflow"]["items"]
    }
    for filename, expected in original["files"].items():
        assert hashlib.sha256((bundle / filename).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize(
    "damage",
    [
        "quantity",
        "assay",
        "article",
        "criteria",
        "model_selection",
        "comparability",
        "producer",
        "missing",
        "binding",
        "source_scope",
        "curation",
        "status",
    ],
)
def test_reader_refuses_changed_science_or_overstated_scope_even_when_manifest_is_rehashed(
    bundle, tmp_path, damage
):
    output = tmp_path / "damaged"
    shutil.copytree(bundle, output)
    report_path = output / "original.dossier.json"
    report = load(report_path)
    subject = report["proteins"]["subject"]
    comparator = report["proteins"]["comparator"]
    if damage == "quantity":
        row = next(
            row
            for row in subject["structures"]["rows"]
            if row["item"]["resolution"] is not None
        )
        row["item"]["resolution"]["unit"] = "nanometer"
    elif damage == "assay":
        subject["assays"]["rows"][0]["qualifiers"]["assay"]["relationship_type"] = (
            "invented"
        )
    elif damage == "article":
        comparator["literature"]["located_mentions"][0]["qualifiers"]["locations"][0][
            "annotation"
        ]["exact"] = "P52270"
    elif damage == "criteria":
        subject["structures"]["rule"]["maximum_resolution"]["value"] = 1000
    elif damage == "model_selection":
        subject["structures"]["rows"][0]["project_model_selection"] = "approved"
    elif damage == "comparability":
        subject["assays"]["rows"][0]["experimental_comparability"] = "established"
    elif damage == "binding":
        subject["structures"]["rows"][0]["source_assertion_refs"] = []
    elif damage == "source_scope":
        subject["source_scope"]["activity_limit_per_source"] = 5000
    elif damage == "curation":
        comparator["literature"]["publications"]["publications"][0]["curated"] = [
            {"claim": "invented mechanism"}
        ]
    elif damage == "status":
        row = next(
            row
            for row in subject["structures"]["rows"]
            if row["status"] != "meets_recorded_criteria"
        )
        row["status"] = "meets_recorded_criteria"
    elif damage == "producer":
        report["producer"]["sabueso"] = "999.reader"
    else:
        (output / "original.runtime.json").unlink()
    report_path.write_text(json.dumps(report), encoding="utf-8")
    manifest_path = output / "original.manifest.json"
    manifest = load(manifest_path)
    manifest["files"]["original.dossier.json"] = hashlib.sha256(
        report_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = invoke("read", output)
    assert result.returncode != 0, result.stdout + result.stderr
