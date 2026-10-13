"""Portable original support must not be copied into every bibliographic use."""

import json

import ackredit

import sabueso
from sabueso.core.card import Card
from sabueso.core.source_assertion_store import make_source_assertion


def observed(size):
    card = Card(meta={"card_id": "sabueso:protein:uniprot:P60174"})
    values = [{"variant_id": f"synthetic_{i:04d}"} for i in range(size)]
    ids = []
    for index, value in enumerate(values):
        assertion = make_source_assertion(
            "annotations.population_variants",
            value,
            "gnomAD",
            f"synthetic_variant_{index:04d}",
            "public synthetic observation",
        )
        card.source_assertion_store.add(assertion)
        ids.append(assertion["id"])
    card.set("annotations.population_variants", values, ids)
    with (
        ackredit.session("public bounded scaling"),
        sabueso.attribution() as run,
        ackredit.capture("comparison") as workflow,
    ):
        view = card.variant_tissue_usage()
    (record,) = run.operations
    assert view["rule"] == record["rule"] and not run.acquisitions
    assert len(record["inputs"][0]["fields"][0]["source_assertion_refs"]) == size
    assert len(record["resources"]) == size
    return record, workflow.attribution.to_dict()


def test_serialized_record_and_workflow_credit_grow_with_support_not_its_square():
    small, small_workflow = observed(64)
    large, large_workflow = observed(128)

    def size(record, workflow):
        return len(
            json.dumps(
                {"record": record, "workflow": workflow}, sort_keys=True
            ).encode()
        )

    assert size(large, large_workflow) < 2.7 * size(small, small_workflow)
    assert all(
        "inputs" not in use["context"]
        for use in large["provider"]["attribution"]["uses"]
    )
