"""Record two located source statements with explicit agent curation and scope."""

import argparse
import json
from pathlib import Path
from shutil import copyfile
from xml.etree import ElementTree as ET

import ackredit
from protein_comparison import digest, offline, read_json, require, write_json

import sabueso
from sabueso.resolver import EntityResolver, FixtureUniProtClient
from sabueso.tools.db.europepmc import FixtureEuropePMCClient, get_article

FORMAT = "sabueso.located_source_review_example@1"
PUBLICATION = "pubmed:40832834"
SOURCE = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12400196/fullTextXML"
CURATOR = "Codex"
NATIVE_SHA256 = "eff2c488e4b17ded8e30530b98ff949fdada1294329c957d26e6ab71945abfef"
SPECS = [
    {
        "topic": "structure",
        "text": "The study used human TPI structure PDB 2JK2 as the MoRDa molecular-replacement template for FhTPI.",
        "about": ["pdb:2JK2"],
        "locator": "PMC12400196:sec2.4/p[1]",
        "quote": "The model template chosen by MoRDa was the dimeric triosephosphate isomerase model from Homo sapiens",
    },
    {
        "topic": "other",
        "text": "Figure 4 includes human TPI accession P60174 in a published multiple sequence alignment performed with Clustal Omega.",
        "about": ["uniprot:P60174"],
        "locator": "PMC12400196:fig4/caption",
        "quote": "Alignment was performed with Clustal Omega",
    },
]


def fragments(path):
    require(digest(path) == NATIVE_SHA256, "Original native article bytes differ")
    root = ET.fromstring(path.read_bytes())
    ids = {node.get("pub-id-type"): node.text for node in root.findall(".//article-id")}
    require(ids.get("pmid") == "40832834", "Wrong native publication")
    require(ids.get("doi") == "10.1107/S2053230X25006454", "Wrong native DOI")
    licenses = [node.text for node in root.iter() if node.tag.endswith("license_ref")]
    require(
        "https://creativecommons.org/licenses/by/4.0/" in licenses,
        "Required article rights not stated",
    )
    nodes = [root.find(".//*[@id='sec2.4']/p"), root.find(".//*[@id='fig4']/caption")]
    require(
        all(node is not None for node in nodes), "Original source locations missing"
    )
    texts = ["".join(node.itertext()) for node in nodes]
    require(
        "Homo sapiens" in texts[0] and "2jk2" in texts[0],
        "Source does not state the human template",
    )
    require(
        "H. sapiens" in texts[1] and "Swiss-Prot entry P60174" in texts[1],
        "Source accession binding missing",
    )
    require(
        all(spec["quote"] in text for spec, text in zip(SPECS, texts, strict=True)),
        "Quote absent from its original location",
    )
    return texts


def produce(output, fixtures):
    require(not output.exists() or not any(output.iterdir()), "Output must be empty")
    output.mkdir(parents=True, exist_ok=True)
    copyfile(fixtures / "europepmc/fulltext/PMC12400196.xml", output / "source.xml")
    texts = fragments(output / "source.xml")
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    curations = sabueso.CurationStore(output / "curations.jsonl")
    resolver = EntityResolver(FixtureUniProtClient(fixtures))
    with offline(), ackredit.session("located public source review"):
        with (
            sabueso.attribution() as observed,
            ackredit.capture("source review") as workflow,
        ):
            card, resolution = sabueso.resolve("P60174", resolver=resolver)
            require(resolution.status == "resolved", "Subject unresolved")
            baseline = store.save(card)
            (relationship,) = [
                rel
                for rel in card.relationships("has_structure")
                if rel["object_ref"] == "pdb:2JK2"
            ]
            require(
                relationship["source_assertion_ids"],
                "Native structure identity support missing",
            )
            article = get_article(PUBLICATION, client=FixtureEuropePMCClient(fixtures))
            records = [
                card.add_literature_claim(
                    publication=PUBLICATION, curator=CURATOR, **spec
                )
                for spec in SPECS
            ]
            require(
                all(record["outcome"] == "not_compared" for record in records),
                "Unexpected claim comparison",
            )
            curations.save(card)
            curated = store.save(card)
            claims = card.claims()
            publication = next(
                row
                for row in card.literature()["publications"]
                if row["publication_ref"] == PUBLICATION
            )
            rebuilt, _ = sabueso.resolve(
                "P60174", resolver=resolver, curations=curations
            )
            require(
                rebuilt.claims() == claims,
                "Original source statements lost during rebuild",
            )
            rebuilt_pin = store.save(rebuilt)
        runtime = {
            "acquisitions": observed.acquisitions,
            "workflow": workflow.attribution.to_dict(),
            "curation_execution_observation": "not_observed",
            "native_fulltext_origin": "supplied_original_public_XML_not_SDK_fulltext_acquisition",
        }
    report = {
        "format": FORMAT,
        "producer": {
            "sabueso": sabueso.__version__,
            "ackredit": ackredit.__version__,
            "example_source_sha256": digest(Path(__file__)),
        },
        "curator": {"name": CURATOR, "kind": "agent", "scientist_review": "pending"},
        "source": {
            "url": SOURCE,
            "publication": PUBLICATION,
            "article_licence": "CC-BY-4.0",
            "native_xml_sha256": digest(output / "source.xml"),
            "article_metadata": article,
        },
        "subject": "uniprot:P60174",
        "cards": {"baseline": baseline, "curated": curated, "rebuilt": rebuilt_pin},
        "identity_basis": {
            "rule": "located_publication_subject_binding@1",
            "paper_accession_location": "fig4/caption",
            "native_structure_relationship_ref": baseline + "#" + relationship["id"],
            "source_assertion_refs": [
                baseline + "#" + identifier
                for identifier in relationship["source_assertion_ids"]
            ],
        },
        "statements": [
            {
                **spec,
                "source_assertion_ref": curated + "#" + record["source_assertion_id"],
                "source_fragment": text,
            }
            for spec, record, text in zip(SPECS, records, texts, strict=True)
        ],
        "claims": claims,
        "literature": publication,
        "scope": {
            "reported_template_use": "source_statement",
            "published_alignment_membership": "source_statement",
            "new_alignment_or_modeling": "not_performed",
            "inhibition_or_selectivity": "not_established",
            "other_organism_findings_transferred": False,
            "project_Evidence": "not_created",
        },
    }
    write_json(output / "report.json", report)
    write_json(output / "runtime.json", {**runtime, "producer": report["producer"]})
    (output / "review.md").write_text(render(report), encoding="utf-8")
    members = (
        "source.xml",
        "report.json",
        "runtime.json",
        "curations.jsonl",
        "review.md",
    )
    write_json(
        output / "manifest.json",
        {
            "format": FORMAT,
            "files": {name: digest(output / name) for name in members},
            "cards": report["cards"],
        },
    )


def render(report):
    lines = [
        "# Located source review",
        "",
        "Two statements recorded from Kontellas et al. (2025), DOI 10.1107/S2053230X25006454, article CC BY 4.0.",
        "",
        "Curator: Codex (agent). Scientist review: pending.",
        "",
    ]
    for statement in report["statements"]:
        lines += [
            statement["text"],
            "",
            f"Source location: `{statement['locator']}`. Support: `{statement['source_assertion_ref']}`.",
            "",
        ]
    lines += [
        "These are source-reported template/alignment facts. They do not establish inhibition or selectivity, transfer findings from another organism, execute modeling or create project Evidence.",
        "",
    ]
    return "\n".join(lines)


def read(output):
    manifest = read_json(output / "manifest.json")
    require(manifest["format"] == FORMAT, "Unsupported source review")
    require(
        set(manifest["files"])
        == {
            "source.xml",
            "report.json",
            "runtime.json",
            "curations.jsonl",
            "review.md",
        },
        "Incomplete source review",
    )
    for name, fingerprint in manifest["files"].items():
        require(digest(output / name) == fingerprint, "Original member differs")
    report = read_json(output / "report.json")
    require(
        report["format"] == FORMAT and report["cards"] == manifest["cards"],
        "Report binding differs",
    )
    require(
        report["curator"]
        == {"name": CURATOR, "kind": "agent", "scientist_review": "pending"},
        "Curator or acceptance differs",
    )
    texts = fragments(output / "source.xml")
    require(
        report["source"]["native_xml_sha256"] == digest(output / "source.xml"),
        "Native input binding differs",
    )
    require(report["subject"] == "uniprot:P60174", "Wrong source subject")
    require(
        report["source"]["url"] == SOURCE
        and report["source"]["publication"] == PUBLICATION
        and report["source"]["article_licence"] == "CC-BY-4.0",
        "Wrong original publication or rights",
    )
    require(
        (output / "review.md").read_text(encoding="utf-8") == render(report),
        "Human review differs from original report",
    )
    require(
        report["scope"]
        == {
            "reported_template_use": "source_statement",
            "published_alignment_membership": "source_statement",
            "new_alignment_or_modeling": "not_performed",
            "inhibition_or_selectivity": "not_established",
            "other_organism_findings_transferred": False,
            "project_Evidence": "not_created",
        },
        "Overstated scientific scope",
    )
    require((output / "knowledge.db").is_file(), "Original store missing")
    require(
        set(report["cards"]) == {"baseline", "curated", "rebuilt"},
        "Wrong original card membership",
    )
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    with offline(), ackredit.session("independent located source reader"):
        before = ackredit.get_attribution().to_dict()
        with sabueso.attribution() as observed:
            cards = {name: store.load(pin) for name, pin in report["cards"].items()}
            require(
                all(
                    card.pinned_ref() == report["cards"][name]
                    for name, card in cards.items()
                ),
                "Original pin differs",
            )
            identity = report["identity_basis"]
            rel = cards["baseline"].relationship_store.get(
                identity["native_structure_relationship_ref"].rsplit("#", 1)[1]
            )
            require(rel["object_ref"] == "pdb:2JK2", "Wrong source representation")
            require(rel["predicate"] == "has_structure", "Wrong identity relationship")
            require(
                identity["rule"] == "located_publication_subject_binding@1"
                and identity["paper_accession_location"] == "fig4/caption"
                and identity["source_assertion_refs"]
                == [
                    report["cards"]["baseline"] + "#" + sid
                    for sid in rel["source_assertion_ids"]
                ],
                "Wrong original identity basis",
            )
            for original in cards["baseline"].source_assertion_store.to_list():
                require(
                    all(
                        card.source_assertion_store.get(original["id"]) == original
                        for name, card in cards.items()
                        if name != "baseline"
                    ),
                    "Baseline source support changed",
                )
            require(
                identity["native_structure_relationship_ref"].startswith(
                    report["cards"]["baseline"] + "#"
                ),
                "Foreign identity support",
            )
            require(
                len(report["statements"]) == len(SPECS), "Wrong statement membership"
            )
            for statement, spec, text in zip(
                report["statements"], SPECS, texts, strict=True
            ):
                require(
                    all(statement[key] == value for key, value in spec.items())
                    and statement["source_fragment"] == text,
                    "Original located statement differs",
                )
                require(
                    statement["source_assertion_ref"].startswith(
                        report["cards"]["curated"] + "#"
                    ),
                    "Foreign statement pin",
                )
                identifier = statement["source_assertion_ref"].rsplit("#", 1)[1]
                assertion = cards["curated"].source_assertion_store.get(identifier)
                require(
                    assertion
                    == cards["rebuilt"].source_assertion_store.get(identifier),
                    "Source statement lost after rebuild",
                )
                require(
                    assertion["subject_ref"] == "uniprot:P60174"
                    and assertion["source"]["record_id"] == PUBLICATION
                    and assertion["acquisition"] == {"method": "curation"}
                    and assertion["field_path"] == "literature.claims",
                    "Wrong assertion subject/publication",
                )
                require(
                    assertion["asserted_value"]
                    == {key: spec[key] for key in ("topic", "text", "about")},
                    "Original assertion value differs",
                )
                require(
                    assertion["source_metadata"]["curation"]["curator"] == CURATOR,
                    "Curator differs",
                )
                require(
                    assertion["source_metadata"]["curation"]["locator"]
                    == spec["locator"]
                    and assertion["source_metadata"]["curation"]["quote"]
                    == spec["quote"],
                    "Statement location or quote differs",
                )
                (claim,) = [
                    item
                    for item in report["claims"]["items"]
                    if item["source_assertion_id"] == identifier
                ]
                metadata = assertion["source_metadata"]["curation"]
                require(
                    claim
                    == {
                        **assertion["asserted_value"],
                        "publication": PUBLICATION,
                        **{
                            key: metadata[key]
                            for key in ("locator", "quote", "curator", "curated_at")
                        },
                        "source_assertion_id": identifier,
                        "outcome": "not_compared",
                    },
                    "Saved claim differs from original assertion",
                )
            require(
                report["claims"]["topics"] == {"other": 1, "structure": 1}
                and len(report["claims"]["items"]) == 2,
                "Wrong claim inventory",
            )
            require(
                report["literature"]["publication_ref"] == PUBLICATION
                and len(report["literature"]["curated"]) == 2,
                "Wrong literature inventory",
            )
            for item in report["literature"]["curated"]:
                (claim,) = [
                    entry
                    for entry in report["claims"]["items"]
                    if entry["source_assertion_id"] == item["source_assertion_id"]
                ]
                require(
                    item
                    == {
                        "field_path": "literature.claims",
                        "value": claim["text"],
                        **{
                            key: claim[key]
                            for key in (
                                "locator",
                                "quote",
                                "curator",
                                "curated_at",
                                "outcome",
                                "source_assertion_id",
                            )
                        },
                    },
                    "Saved literature differs from original claim",
                )
            records = sabueso.CurationStore(output / "curations.jsonl").records()
            require(len(records) == 2, "Wrong original curation inventory")
            for record in records:
                assertion = cards["curated"].source_assertion_store.get(
                    record["source_assertion_id"]
                )
                require(
                    assertion is not None
                    and record["value"] == assertion["asserted_value"]
                    and record["entity"] == report["subject"]
                    and record["curator"] == CURATOR
                    and record["publication"] == PUBLICATION
                    and record["locator"]
                    == assertion["source_metadata"]["curation"]["locator"]
                    and record["quote"]
                    == assertion["source_metadata"]["curation"]["quote"]
                    and record["outcome"] == "not_compared",
                    "Original curation differs",
                )
            runtime = read_json(output / "runtime.json")
            require(runtime["producer"] == report["producer"], "Producer differs")
            require(
                runtime["curation_execution_observation"] == "not_observed"
                and runtime["native_fulltext_origin"]
                == "supplied_original_public_XML_not_SDK_fulltext_acquisition",
                "Overstated original execution observation",
            )
            workflow = ackredit.Attribution.from_dict(runtime["workflow"])
            for key in ("items", "uses"):
                require(
                    {
                        json.dumps(value, sort_keys=True)
                        for record in runtime["acquisitions"]
                        for value in (record["provider"].get("attribution") or {}).get(
                            key, []
                        )
                    }
                    == {
                        json.dumps(value, sort_keys=True)
                        for value in workflow.to_dict()[key]
                    },
                    "Workflow differs from original acquisitions",
                )
            for format, suffix in (("csl-json", "csl.json"), ("bibtex", "bib")):
                target = output / f"original.references.{suffix}"
                value = workflow.report(format=format)
                if target.exists():
                    require(
                        target.read_text(encoding="utf-8") == value,
                        "Original bibliography differs",
                    )
                else:
                    target.write_text(value, encoding="utf-8")
            require(
                not observed.acquisitions
                and not observed.operations
                and not observed.records
                and not observed.literature,
                "Reader produced new execution",
            )
        require(ackredit.get_attribution().to_dict() == before, "Reader created credit")
    print(
        "PASS: original located source statements and agent provenance retained; scientist review remains pending."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("produce", "read"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fixtures", default=Path("temp_data"), type=Path)
    args = parser.parse_args()
    if args.action == "produce":
        produce(args.output.resolve(), args.fixtures.resolve())
    else:
        read(args.output.resolve())


if __name__ == "__main__":
    main()
