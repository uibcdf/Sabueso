"""A scientist-facing dossier retains exact support and truthful review scope."""

import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path("examples/user_journeys/scientific_dossier.py").resolve()
DATA = Path("temp_data").resolve()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def invoke(action, output, *extra):
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
            *extra,
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


def test_native_assay_and_document_context_is_visible_without_promoting_comparability(
    bundle,
):
    report = load(bundle / "original.dossier.json")
    human = (bundle / "original.dossier.md").read_text(encoding="utf-8")
    assert report["format"] == "sabueso.scientific_dossier_example@2"
    rows = [
        row
        for protein in report["proteins"].values()
        for row in protein["assays"]["rows"]
    ]
    chembl = next(
        row for row in rows if row["qualifiers"].get("activity_id") == 3011871
    )
    assert chembl["qualifiers"]["target"] == "CHEMBL5834"
    assert chembl["qualifiers"]["assay"]["id"] == "CHEMBL1049665"
    assert chembl["context_review"]["fields"]["assay.id"] == "stored"
    assert "CHEMBL1049665" in human and "CHEMBL5834" in human
    assert "19733070" in human and "10.1016/j.bmcl.2009.08.055" in human
    assert "confidence_score=9" in human
    bindingdb = next(
        row
        for row in rows
        if row["qualifiers"].get("source") == "BindingDB"
        and row["status"] == "meets_recorded_criteria"
    )
    review = bindingdb["context_review"]
    assert review["rule"] == "stored_assay_context_review@1"
    assert review["fields"]["assay.id"] == "not_in_saved_qualifiers"
    assert review["fields"]["target"] == "not_in_saved_qualifiers"
    assert bindingdb["qualifiers"]["measurement"]["stated_value"] in human
    assert "potential_duplicate=False" in human
    assert all(
        row["context_review"]["experimental_comparability"] == "not_established"
        for row in rows
    )
    assert all(
        row["context_review"]["experimental_protocol"] == "not_curated" for row in rows
    )
    assert "matching assay identifiers" in human.lower()
    assert "missing variant annotation does not establish a wild-type target" in human


def test_historical_dossier_and_reacquisition_keep_original_format_and_eligibility(
    tmp_path,
):
    output = tmp_path / "legacy"
    for action, options in (
        ("produce", ("--legacy",)),
        ("read", ()),
        ("reacquire", ()),
        ("read", ()),
    ):
        result = invoke(action, output, *options)
        assert result.returncode == 0, result.stdout + result.stderr
    original = load(output / "original.dossier.json")
    later = load(output / "later.dossier.json")
    assert (
        original["format"] == later["format"] == "sabueso.scientific_dossier_example@1"
    )
    assert load(output / "original.reader.json")["original_report"] == original
    assert (
        "Stored assay and document context"
        not in (output / "original.dossier.md").read_text()
    )
    for protein in original["proteins"].values():
        assert all("context_review" not in row for row in protein["assays"]["rows"])
    for role in original["proteins"]:
        rows = original["proteins"][role]["assays"]["rows"]
        new_rows = later["proteins"][role]["assays"]["rows"]
        assert [(row["qualifiers"], row["checks"], row["status"]) for row in rows] == [
            (row["qualifiers"], row["checks"], row["status"]) for row in new_rows
        ]


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
        "context_review",
        "protocol_claim",
        "empty_assay_checks",
        "coherent_assay_checks",
        "assay_expected",
        "assay_unknown_reason",
        "coherent_structure_checks",
    ],
)
def test_reader_refuses_changed_science_or_overstated_scope_even_when_manifest_is_rehashed(
    bundle, tmp_path, damage
):
    output = tmp_path / "damaged"
    shutil.copytree(bundle, output)
    # Exercise the original stage alone. Its rejection must not be masked by
    # the later manifest's hash of the original manifest.
    (output / "later.manifest.json").unlink()
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
    elif damage == "context_review":
        row = next(
            row
            for row in subject["assays"]["rows"]
            if row["context_review"]["fields"]["assay.id"] == "not_in_saved_qualifiers"
        )
        row["context_review"]["fields"]["assay.id"] = "stored"
    elif damage == "protocol_claim":
        subject["assays"]["rows"][0]["context_review"]["experimental_protocol"] = (
            "curated"
        )
    elif damage in ("empty_assay_checks", "coherent_assay_checks"):
        row = next(
            row
            for row in comparator["assays"]["rows"]
            if row["checks"]["target_assignment"]["status"] == "not_met"
        )
        if damage == "empty_assay_checks":
            row["checks"] = {}
        else:
            for node in row["checks"].values():
                node.update(value=node["expected"], status="met", unknown_reason=None)
        row["status"] = "meets_recorded_criteria"
    elif damage == "assay_expected":
        comparator["assays"]["rows"][0]["checks"]["measurement_type"]["expected"] = "Ki"
    elif damage == "assay_unknown_reason":
        row = next(
            row
            for row in comparator["assays"]["rows"]
            if row["checks"]["relation"]["status"] == "unknown"
        )
        row["checks"]["relation"]["unknown_reason"] = "source_proved_absence"
    elif damage == "coherent_structure_checks":
        row = next(
            row
            for row in comparator["structures"]["rows"]
            if row["item"]["structure_ref"] == "pdb:1KLG"
        )
        for node in row["checks"].values():
            node.update(value=node["expected"], status="met", unknown_reason=None)
        row["status"] = "meets_recorded_criteria"
    elif damage == "producer":
        report["producer"]["sabueso"] = "999.reader"
    else:
        (output / "original.runtime.json").unlink()
    report_path.write_text(json.dumps(report), encoding="utf-8")
    # Keep the display and manifest consistent so the scientific guard, rather
    # than a stale Markdown digest, must reject the changed decision.
    script_parent = str(SCRIPT.parent)
    sys.path.insert(0, script_parent)
    try:
        render = runpy.run_path(str(SCRIPT))["render"]
        (output / "original.dossier.md").write_text(render(report), encoding="utf-8")
    finally:
        sys.path.remove(script_parent)
    manifest_path = output / "original.manifest.json"
    manifest = load(manifest_path)
    manifest["files"]["original.dossier.json"] = hashlib.sha256(
        report_path.read_bytes()
    ).hexdigest()
    manifest["files"]["original.dossier.md"] = hashlib.sha256(
        (output / "original.dossier.md").read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = invoke("read", output)
    assert result.returncode != 0, result.stdout + result.stderr
    if damage in {
        "empty_assay_checks",
        "coherent_assay_checks",
        "assay_expected",
        "assay_unknown_reason",
        "coherent_structure_checks",
    }:
        area = "structures" if damage == "coherent_structure_checks" else "assays"
        assert (
            f"Recorded {area} criterion inputs or outcomes differ" in result.stderr
        ), result.stdout + result.stderr
