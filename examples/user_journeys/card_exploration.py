"""Walk three public Cards through the initial human exploration API, offline."""

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import sabueso


def show(question, view):
    print(f"\n{question}\n{view}")
    return view


def choose(view, column, value):
    selected = view.filter(column, equals=value)
    if len(selected.items()) != 1:
        raise ValueError(f"Expected one public example item for {column}={value!r}")
    return selected


def source_and_return(selected):
    support = show("What supports this selection?", selected.items()[0].explain())
    if support.back() is not selected:
        raise ValueError("The explanation lost its originating selection")
    sources = selected.items()[0].related().filter("role", equals="source")
    if not len(sources.items()):
        raise ValueError("The public example has no retained source link")
    record = show("Follow an original source link:", sources.items()[0].open())
    if record.back() is not sources or "source" not in record.native_payload:
        raise ValueError("The source link did not retain its record and return path")


def empty_and_return(view):
    empty = show(
        "What happens when my display filter matches nothing?",
        view.filter("label", equals="Deliberately unmatched example label"),
    )
    if len(empty.items()) or empty.back() is not view:
        raise ValueError("The empty filter lost its original view")
    show("Return to the original view:", empty.back())


def protein(fixtures):
    from sabueso.core.card import Card

    card = Card.from_dict(
        json.loads(
            (fixtures / "frozen_cards/schema_0.3.9__P52270.json").read_text(
                encoding="utf-8"
            )
        )
    )
    explorer = card.explore()
    show("TcTIM: what is this system, and where can I explore?", explorer.overview())
    show("Which questions can I ask?", explorer.questions())
    function = show(
        "What do sources state about function?", explorer.answer("function")
    )
    catalytic = choose(function, "label", "Catalytic activity")
    source_and_return(catalytic)
    print("A reaction annotation does not supply a missing prose function description.")
    sequence = show(
        "Which sequence and source annotations are retained?",
        explorer.answer("sequence_annotations"),
    )
    source_and_return(choose(sequence, "label", "Active sites"))
    models = show(
        "Which predicted models and source metrics are retained?",
        explorer.answer("predicted_models"),
    )
    if len(models.items()):
        source_and_return(models)
    show(
        "Which source sites and contact statements are retained?",
        explorer.answer("retained_sites"),
    )
    instances = show(
        "Which original ligand instances and contacts are retained in structures?",
        explorer.answer("structure_ligands"),
    )
    source_and_return(
        choose(
            instances.filter("structure_ref", equals="pdb:1SUX"), "component_id", "BTS"
        )
    )
    print(
        "Instance contacts retain separate position and seq_id values; no PDBe aggregate or assembly join is inferred."
    )
    structures = show(
        "Which experimental structures are retained?", explorer.view("structures")
    )
    selected = choose(structures, "structure_ref", "pdb:1SUX")
    show("Inspect one structural option:", selected.items()[0].open())
    source_and_return(selected)
    empty_and_return(selected)
    print("This example inspects a structural option; it does not recommend a model.")
    return selected


def molecule(fixtures):
    from sabueso.tools.card.small_molecule import single_molecule_card
    from sabueso.tools.db.chembl import FixtureChEMBLClient

    card = single_molecule_card(
        chembl=FixtureChEMBLClient(fixtures).molecules(["CHEMBL110"])
    )
    explorer = card.explore()
    show("Benznidazole: which chemical entity is retained?", explorer.overview())
    show("Inspect identity and representations:", explorer.answer("chemical_identity"))
    properties = show(
        "What properties and source methods are retained?",
        explorer.answer("property_context"),
    )
    selected = choose(properties, "label", "Molecular weight")
    show(
        "Open the complete property, including its original unit:",
        selected.items()[0].open(),
    )
    source_and_return(selected)
    logp = choose(properties, "label", "logP")
    source_and_return(logp)
    empty_and_return(selected)
    print(
        "The source reports ALogP; no experimental method is invented for molecular weight."
    )
    show("What source coverage is actually recorded?", explorer.view("coverage"))
    print(
        "This property reading establishes neither target activity nor clinical efficacy."
    )
    return selected


def disease(fixtures):
    from sabueso.tools.card.disease import resolve_disease_card
    from sabueso.tools.db.mondo import FixtureMONDOClient

    card = resolve_disease_card(
        "MONDO:0014221", mondo_client=FixtureMONDOClient(fixtures)
    )[0]
    explorer = card.explore()
    show("MONDO:0014221: what does the term mean?", explorer.overview())
    show("Inspect the definition and scoped synonyms:", explorer.answer("meaning"))
    parents = show(
        "Which broader terms are retained?", explorer.answer("classification")
    )
    show(
        "Keep equivalence and related identifiers separate:", explorer.view("identity")
    )
    selected = choose(parents, "object_ref", "mondo:MONDO:0002908")
    source_and_return(selected)
    links = show("Where does this relationship lead?", selected.items()[0].related())
    destination = choose(links, "role", "object").items()[0].open()
    show("The parent Card was not supplied:", destination)
    if destination.outcome["status"] != "context_not_supplied":
        raise ValueError("Missing related context was not reported explicitly")
    if links.back().back() is not selected:
        raise ValueError("Relationship navigation lost the original selection")
    empty_and_return(selected)
    print("A broader ontology term is not an equivalent identifier or a diagnosis.")
    return selected


def produce(output, fixtures):
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Choose an empty output directory")
    output.mkdir(parents=True, exist_ok=True)
    receipts = {}
    for name, journey in (
        ("protein", protein),
        ("molecule", molecule),
        ("disease", disease),
    ):
        view = journey(fixtures)
        path = output / f"{name}.json"
        receipt = view.save(path)
        receipts[name] = {
            "bundle_digest": receipt["bundle_digest"],
            "view_ref": view.view_ref,
        }
        print(f"Saved the original selection and support to {path}")
    (output / "receipts.json").write_text(
        json.dumps(receipts, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "\nTechnical walkthrough complete. Researcher usability has not been measured."
    )


def read(output):
    receipts = json.loads((output / "receipts.json").read_text(encoding="utf-8"))
    for name in ("protein", "molecule", "disease"):
        receipt = receipts[name]
        saved = sabueso.read_exploration(
            output / f"{name}.json", expected_digest=receipt["bundle_digest"]
        )
        if saved.view_ref != receipt["view_ref"] or saved.explorer.mode != "saved":
            raise ValueError("The original saved selection was not retained")
        show(f"{name}: reopen the original selection without the input files:", saved)
        source_and_return(saved)
        empty_and_return(saved)
        if name == "protein":
            for topic in (
                "sequence",
                "predicted_structures",
                "sites",
                "ligand_instances",
            ):
                show(
                    f"Original retained protein context ({topic}); an unsaved variant stays not_saved:",
                    saved.explorer.view(topic),
                )
    print("\nAll three original selections reopened; no source requests were made.")


def forbidden(*args, **kwargs):
    raise RuntimeError("This public fixture walkthrough must remain offline")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser(
        "produce", help="Walk through three frozen public inputs"
    )
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--fixtures", type=Path, default=Path("temp_data"))
    reopen = commands.add_parser("read", help="Reopen without reading fixtures")
    reopen.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with (
        patch("socket.create_connection", forbidden),
        patch("socket.socket.connect", forbidden),
    ):
        if args.command == "produce":
            produce(args.output, args.fixtures)
        else:
            read(args.output)


if __name__ == "__main__":
    main()
