"""Explicit clinical/publication links survive independent saved reading."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path("examples/user_journeys/clinical_bibliography.py").resolve()
DATA = Path("temp_data").resolve()
NCT = "NCT00123916"
PMIDS = ["18585495", "26323937", "19753491"]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(action, output, fixtures=DATA):
    command = [sys.executable, str(SCRIPT)]
    if action == "read":
        command = [sys.executable, "-c", """
import runpy, sys
from pathlib import Path
import ackredit, sabueso
from sabueso.core.card import Card
from sabueso.tools.db import clinicaltrials, europepmc
def forbidden(*args, **kwargs):
    raise RuntimeError('Saved reading cannot acquire, derive, or add credit')
ackredit.register_item = ackredit.track_item = forbidden
sabueso.resolve = sabueso.compose_packet = sabueso.ligand_deck = forbidden
Card.clinical = Card.bioactivities = Card.ligands = forbidden
Card.explain_ligand = Card.explain_bioactivity = Card.explain_measurement = forbidden
clinicaltrials.get_study_references = europepmc.get_article = forbidden
clinicaltrials.FixtureClinicalTrialsClient = europepmc.FixtureEuropePMCClient = forbidden
sabueso.__version__ = '999.reader'
script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).parent))
runpy.run_path(script, run_name='__main__')
""", str(SCRIPT)]  # fmt: skip
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [*command, action, "--output", str(output), "--fixtures",
         str(fixtures if action != "read" else output / "absent-fixtures")],
        cwd=output.parent, env=env, capture_output=True, text=True,
        timeout=120, check=False,
    )  # fmt: skip


def successful(action, output, fixtures=DATA):
    result = invoke(action, output, fixtures)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    output = tmp_path_factory.mktemp("clinical-bibliography") / "bundle"
    successful("produce", output)
    before = {
        path.relative_to(output): sha(path)
        for path in output.rglob("*")
        if path.is_file()
    }
    successful("read", output)
    successful("reacquire", output)
    successful("read", output)
    assert all(sha(output / name) == checksum for name, checksum in before.items())
    return output


def test_explicit_indication_trial_publication_links_and_original_credit(bundle):
    manifest = load(bundle / "original.manifest.json")
    report = load(bundle / "original.report.json")
    assert manifest["format"] == "sabueso.clinical_bibliography_example@1"
    assert report == load(bundle / "original.reader.json")["original_report"]
    assert report["rule"] == "explicit_clinical_bibliography_links@1"
    assert report["registry_status"] == "received"
    assert len(report["upstream"]["other_cited_trials_not_queried"]) == 15
    for link in report["upstream"]["relationships"]:
        assert NCT in link["qualifiers"]["trials"]
        assert set(link["source_assertion_ids"]) <= {
            row["id"] for row in report["upstream"]["assertions"]
        }
    assert report["upstream"]["relationships"]
    original_molecule = load(bundle / "molecules/original.report.json")
    assert original_molecule["scope"]["trials"] == "not_queried"
    assert (
        len(original_molecule["molecules"]["benznidazole"]["clinical"]["not_fetched"])
        == 16
    )
    diseases = {
        r["object_ref"]
        for r in original_molecule["support"]["benznidazole"]["relationships"]
        if r["predicate"] == "investigated_for"
    }
    assert {"efo:EFO:0008559", "mondo:MONDO:0001444"} <= diseases
    assert len(report["other_reference_forms_not_followed"]["seeAlsoLinks"]) == 2
    assert not report["unselected_references_not_followed"]
    counts = {"18585495": 9, "26323937": 22, "19753491": 9}
    for pmid, row in report["articles"].items():
        assert row["status"] == "received" and len(row["registry_occurrences"]) == 1
        assert row["registry_occurrences"][0]["pmid"] == pmid
        (article,) = row["metadata"]["articles"]
        assert article["pmid"] == pmid and "abstractText" not in article
        authors = article["authorList"]["author"]
        assert len(authors) == counts[pmid]
        assert {"collectiveName": "BENEFIT Investigators"} in authors
    observations = load(bundle / "original.observations.json")
    assert [(r["source"], r["operation"]) for r in observations] == [
        ("ClinicalTrials.gov", "study_references"),
        *[("Europe PMC", "article")] * 3,
    ]
    assert all(row["network_attempts"] == 0 for row in observations)
    assert all(row["producer"]["version"] != "999.reader" for row in observations)
    citations = load(bundle / "original.references.csl.json")
    article = next(
        row
        for row in citations
        if row.get("DOI", "").casefold() == "10.1056/nejmoa1507574"
    )
    assert len(article["author"]) == 22
    assert {"literal": "BENEFIT Investigators"} in article["author"]
    assert (bundle / "original.references.bib").read_text(encoding="utf-8")


def test_reacquisition_is_distinct_but_does_not_refresh_original_molecule(bundle):
    original = load(bundle / "original.manifest.json")
    later = load(bundle / "later.manifest.json")
    assert later["original_manifest_sha256"] == sha(bundle / "original.manifest.json")
    assert later["upstream"] == original["upstream"]
    first = load(bundle / "original.observations.json")
    second = load(bundle / "later.observations.json")
    assert {r["id"] for r in first}.isdisjoint(r["id"] for r in second)
    assert all(r["retrieved_at"] == "later clinical fixture read" for r in second)
    assert load(bundle / "later.reader.json")["observed_acquisitions"] == 0
    assert not (bundle / "molecules/later.manifest.json").exists()


@pytest.mark.parametrize("missing", ["registry", "article"])
def test_missing_local_inputs_never_become_source_absence(tmp_path, missing):
    fixtures = tmp_path / "fixtures"
    shutil.copytree(DATA, fixtures)
    if missing == "registry":
        (fixtures / "clinicaltrials/references.json").unlink()
    else:
        (fixtures / "europepmc/articles/pubmed__26323937.json").unlink()
    output = tmp_path / "bundle"
    successful("produce", output, fixtures)
    successful("read", output)
    report = load(output / "original.report.json")
    observations = load(output / "original.observations.json")
    if missing == "registry":
        assert report["registry_status"] == "unavailable"
        assert report["registry_record"] is None and len(observations) == 1
        assert all(
            row["status"] == "not_queried" and row["metadata"] is None
            for row in report["articles"].values()
        )
    else:
        assert len(observations) == 4 and report["registry_status"] == "received"
        assert report["articles"]["26323937"]["status"] == "unavailable"
        assert report["articles"]["26323937"]["metadata"] is None
        assert all(
            report["articles"][pmid]["status"] == "received"
            for pmid in ("18585495", "19753491")
        )


@pytest.mark.parametrize(
    "defect,error",
    [
        ("missing", "Missing or changed original file"),
        ("membership", "Incomplete original file bindings"),
        ("scope", "Wrong manifest or scope"),
        ("upstream", "Original indication support differs"),
        ("claim", "Clinical report differs from original inputs"),
        ("citation", "Clinical report differs from original inputs"),
        ("authors", "Article metadata differs from original entries"),
        ("query", "Result belongs to another source or query"),
        ("observations", "Observed operations differ from original results"),
        ("workflow", "Workflow items differ from original operations"),
        ("bibliography", "Original bibliography differs"),
        ("prerequisite", "Article lacks its required registry link"),
    ],
)
def test_rehashed_semantic_changes_are_refused_for_their_own_reason(
    bundle, tmp_path, defect, error
):
    output = tmp_path / "copy"
    shutil.copytree(bundle, output)
    # Isolate the original stage; a later manifest hash must not mask a guard.
    for path in output.glob("later.*"):
        path.unlink()
    manifest = load(output / "original.manifest.json")
    report = load(output / "original.report.json")
    results = load(output / "original.results.json")
    if defect == "missing":
        (output / "original.workflow.json").unlink()
    elif defect == "membership":
        manifest["files"].pop("original.results.json")
    elif defect == "scope":
        manifest["scope"]["full_text"] = "reviewed"
    elif defect == "upstream":
        manifest["upstream"]["relationships"] = []
    elif defect == "claim":
        report["scope"]["efficacy_and_protocol_curation"] = "established"
    elif defect == "citation":
        report["articles"]["26323937"]["registry_occurrences"][0]["type"] = "BACKGROUND"
    elif defect == "authors":
        results["pubmed:26323937"]["result"]["record"]["articles"][0]["authorList"][
            "author"
        ] = []
    elif defect == "query":
        results["pubmed:26323937"]["result"]["query"]["identifier"] = "pubmed:18585495"
    elif defect == "prerequisite":
        results["pubmed:26323937"] = {
            "status": "not_queried",
            "not_queried_reason": "invented",
            "result": None,
            "error": None,
            "records": [],
        }
    elif defect == "observations":
        (output / "original.observations.json").write_text("[]", encoding="utf-8")
    elif defect == "workflow":
        workflow = load(output / "original.workflow.json")
        workflow["items"] = []
        workflow["uses"] = []
        workflow["usage_tree"] = {}
        (output / "original.workflow.json").write_text(
            json.dumps(workflow), encoding="utf-8"
        )
    elif defect == "bibliography":
        (output / "original.references.csl.json").write_text("[]", encoding="utf-8")
    (output / "original.results.json").write_text(json.dumps(results), encoding="utf-8")
    (output / "original.report.json").write_text(json.dumps(report), encoding="utf-8")
    # Regenerate the human rendering, so a stale Markdown checksum is not the guard.
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        import clinical_bibliography

        (output / "original.report.md").write_text(
            clinical_bibliography.markdown(report), encoding="utf-8"
        )
    finally:
        sys.path.pop(0)
    for name in manifest["files"]:
        if (output / name).is_file():
            manifest["files"][name] = sha(output / name)
    (output / "original.manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    exports = {
        path.name: path.read_bytes() for path in output.glob("original.references.*")
    }
    result = invoke("read", output)
    assert result.returncode == 2, result.stdout + result.stderr
    assert error in result.stderr, result.stderr
    assert exports == {
        path.name: path.read_bytes() for path in output.glob("original.references.*")
    }


def test_completed_stages_cannot_be_overwritten(bundle):
    for action in ("produce", "reacquire"):
        result = invoke(action, bundle)
        assert result.returncode == 2, result.stdout + result.stderr
        assert (
            "Output must be empty" if action == "produce" else "Later stage exists"
        ) in result.stderr


@pytest.mark.parametrize(
    "change", ["no_pmid", "no_module", "empty_references", "malformed_registry"]
)
def test_only_explicit_returned_identifiers_allow_article_queries(tmp_path, change):
    """Deliberately modified native inputs qualify prerequisite handling only."""
    fixtures = tmp_path / "fixtures"
    shutil.copytree(DATA, fixtures)
    path = fixtures / "clinicaltrials/references.json"
    payload = load(path)
    protocol = payload["studies"][NCT]["protocolSection"]
    if change == "no_pmid":
        protocol["referencesModule"]["references"][1].pop("pmid")
    elif change == "no_module":
        protocol.pop("referencesModule")
    elif change == "empty_references":
        protocol["referencesModule"]["references"] = []
    else:
        payload["studies"] = []
    path.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "bundle"
    successful("produce", output, fixtures)
    successful("read", output)
    report = load(output / "original.report.json")
    observations = load(output / "original.observations.json")
    assert report["articles"]["26323937"]["status"] == "not_queried"
    assert (
        report["articles"]["26323937"]["not_queried_reason"]
        == "no_returned_registry_PMID_statement"
    )
    if change == "no_pmid":
        assert len(observations) == 3
        (unselected,) = report["unselected_references_not_followed"]
        assert "26323937" not in unselected
        assert "Morillo" in unselected["citation"]
        assert report["articles"]["18585495"]["status"] == "received"
    else:
        assert len(observations) == 1
        assert all(
            row["status"] == "not_queried" for row in report["articles"].values()
        )
    assert report["registry_status"] == (
        "failed" if change == "malformed_registry" else "received"
    )
    assert report["reference_module_status"] == (
        "not_available_in_result"
        if change in {"no_module", "malformed_registry"}
        else "returned"
    )
