"""Scoped verified references do not invent method execution or native lineage."""

import json

import ackredit
import pytest

import sabueso
from sabueso.core.card import Card
from sabueso.core.comparative_bibliography import GNOMAD, GTEX, PEXT
from sabueso.core.errors import ConnectorError
from sabueso.core.source_assertion_store import make_source_assertion
from sabueso.tools.db import _http, gnomad, gtex

GENE = "ENSG00000111669"
TRANSCRIPT = "ENST00000396705"
REGIONS = "annotations.exon_usage_by_tissue"


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Bibliography must not fetch papers or scientific data")

    monkeypatch.setattr(_http, "_urlopen", forbidden)
    with ackredit.session("bounded comparative references"):
        yield


@pytest.mark.parametrize(
    "kind", ["variants", "transcript", "consequences", "pext", "tissues"]
)
def test_real_source_credit_scopes_method_description_without_revision_or_study_claim(
    kind,
):
    client = gnomad.FixtureGnomADClient("temp_data")
    with sabueso.attribution() as run, ackredit.capture("fixture source") as workflow:
        if kind == "variants":
            client.variants(GENE)
        elif kind == "transcript":
            client.transcript_variants(TRANSCRIPT)
        elif kind == "consequences":
            client.consequences([])
        elif kind == "pext":
            client.pext(GENE)
        else:
            gtex.FixtureGTExClient("temp_data").tissues("gtex_v10")
    (record,) = run.acquisitions
    assert record["source_version"] == {"value": None, "basis": "not_stated"}
    assert record["network_attempts"] == 0
    assert record["provider"]["status"] == "available"
    ids = {item["id"] for item in record["bibliography"]}
    assert (GTEX if kind == "tissues" else GNOMAD)["id"] in ids
    assert (PEXT["id"] in ids) == (kind == "pext")
    methods = [
        use
        for use in record["provider"]["attribution"]["uses"]
        if "method_description" in use["roles"]
    ]
    if kind == "pext":
        assert len(methods) == 1 and methods[0]["item_id"] == PEXT["id"]
        scope = methods[0]["context"]["method_reference_scope"]
        assert scope["operation"] == "gnomad_pext" and scope["field_path"] is None
        assert scope["method_execution"] == "not_performed"
        assert scope["native_method_revision"]["value"] is None
        assert scope["native_dataset_revision_binding"] == "not_inferred"
        assert scope["entry_publication_membership"] == "not_established"
    else:
        assert not methods and "method_reference_scope" not in record
    assert {
        json.dumps(use, sort_keys=True)
        for use in record["provider"]["attribution"]["uses"]
    } <= {
        json.dumps(use, sort_keys=True)
        for use in workflow.attribution.to_dict()["uses"]
    }


@pytest.mark.parametrize("missing", [True, False])
def test_unavailable_or_failed_pext_has_no_completed_method_credit(tmp_path, missing):
    client = gnomad.FixtureGnomADClient(
        tmp_path, failing=() if missing else {"pext_" + GENE}
    )
    with (
        sabueso.attribution() as run,
        ackredit.capture("incomplete source") as workflow,
    ):
        with pytest.raises(ConnectorError):
            client.pext(GENE)
    (record,) = run.acquisitions
    assert record["outcome"] == ("unavailable" if missing else "failed")
    assert record["provider"]["status"] == "not_attempted"
    assert not workflow.attribution.to_dict()["uses"]


@pytest.mark.parametrize(
    "kind", ["valid", "missing", "misbound", "foreign", "variant_only"]
)
def test_stored_input_method_credit_requires_valid_pext_support(kind):
    from sabueso.core.comparative_operations import _support

    card = Card(meta={"card_id": "sabueso:protein:uniprot:P60174"})
    path = "annotations.population_variants" if kind == "variant_only" else REGIONS
    value = [{"start": 1, "stop": 2, "tissues": {"Brain": 0.5}}]
    assertion = make_source_assertion(
        path,
        value,
        "Custom source" if kind == "foreign" else "gnomAD",
        "synthetic",
        "original",
    )
    assertion["source"]["version"] = "unverified client label"
    if kind == "misbound":
        assertion["field_path"] = "other.field"
    if kind != "missing":
        card.source_assertion_store.add(assertion)
    card.set(path, value, [assertion["id"]])
    support = _support([("subject", card, [path])])
    method_ids = {
        i
        for r in support["resources"]
        for i in r.get("method_description_citation_ids", [])
    }
    assert (PEXT["id"] in method_ids) == (kind == "valid")
    if kind == "valid":
        resource = support["resources"][0]
        scope = resource["uses"][0]["method_reference_scope"]
        assert scope["field_path"] == REGIONS and scope["operation"] is None
        assert scope["native_method_revision"]["value"] is None
        assert resource["source"]["version"] == "unverified client label"
    else:
        assert not any(
            u.get("method_reference_scope")
            for r in support["resources"]
            for u in r["uses"]
        )


def test_original_full_authors_collectives_and_publication_coordinates_export_without_enrichment():
    from sabueso.core.attribution_bibliography import descriptions

    with ackredit.capture("original publications") as capture:
        for item in [*descriptions("gnomAD"), *descriptions("GTEx"), PEXT]:
            ackredit.register_item(**item)
            ackredit.track_item(
                item["id"],
                roles=[
                    "method_description"
                    if item["id"] == PEXT["id"]
                    else "resource_description"
                ],
            )
    original = capture.attribution.to_dict()
    exported = json.loads(capture.attribution.report(format="csl-json"))
    by_doi = {row.get("DOI"): row for row in exported}
    assert len(by_doi[GNOMAD["doi"]]["author"]) == 47
    assert len(by_doi[PEXT["doi"]]["author"]) == 18
    assert by_doi[GTEX["doi"]]["author"] == [{"literal": "GTEx Consortium"}]
    assert by_doi[PEXT["doi"]]["author"][14] == {
        "literal": "Genome Aggregation Database Production Team"
    }
    assert by_doi[PEXT["doi"]]["page"] == "452-458"
    assert by_doi[GNOMAD["doi"]]["page"] == "92-100"
    assert ackredit.Attribution.from_dict(original).to_dict() == original
    assert "10.1038/s41586-020-2329-2" in capture.attribution.report(format="bibtex")
