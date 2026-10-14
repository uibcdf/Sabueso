"""Prepare located primary-source readings without claiming human curation."""

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

FORMAT = "sabueso.located_source_review_example@2"
PUBLICATION = "pubmed:40832834"
SOURCE = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12400196/fullTextXML"
NATIVE_SHA256 = "eff2c488e4b17ded8e30530b98ff949fdada1294329c957d26e6ab71945abfef"
REVIEW = {
    "preparer": "Codex",
    "kind": "agent",
    "scientist_review": "pending",
    "status": "draft_only",
}
SCOPE = {
    "reported_template_use": "proposed_reading",
    "published_alignment_membership": "proposed_reading",
    "new_alignment_or_modeling": "not_performed",
    "inhibition_or_selectivity": "not_established",
    "other_organism_findings_transferred": False,
    "project_Evidence": "not_created",
    "literature_SourceAssertions_created": False,
    "human_curation": "not_performed",
}
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


def render(report):
    lines = [
        "# Located source review draft",
        "",
        "Two proposed readings from Kontellas et al. (2025), DOI 10.1107/S2053230X25006454, article CC BY 4.0.",
        "",
        "Preparer: Codex (agent). Scientist review: pending. No human curation or new literature SourceAssertions.",
        "",
    ]
    for statement in report["proposals"]:
        lines += [
            statement["text"],
            "",
            f"Source location: `{statement['locator']}`. Original article SHA-256: `{NATIVE_SHA256}`.",
            "",
        ]
    lines += [
        "These proposals do not establish inhibition or selectivity, transfer findings from another organism, execute modeling or create project Evidence.",
        "",
    ]
    return "\n".join(lines)


def produce(output, fixtures):
    require(not output.exists() or not any(output.iterdir()), "Output must be empty")
    output.mkdir(parents=True, exist_ok=True)
    copyfile(fixtures / "europepmc/fulltext/PMC12400196.xml", output / "source.xml")
    texts = fragments(output / "source.xml")
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    resolver = EntityResolver(FixtureUniProtClient(fixtures))
    with offline(), ackredit.session("located public source review draft"):
        with (
            sabueso.attribution() as observed,
            ackredit.capture("source review draft") as workflow,
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
        runtime = {
            "acquisitions": observed.acquisitions,
            "workflow": workflow.attribution.to_dict(),
            "draft_preparation_observation": "not_observed",
            "native_fulltext_origin": "supplied_original_public_XML_not_SDK_fulltext_acquisition",
        }
    report = {
        "format": FORMAT,
        "producer": {
            "sabueso": sabueso.__version__,
            "ackredit": ackredit.__version__,
            "example_source_sha256": digest(Path(__file__)),
        },
        "review": REVIEW,
        "source": {
            "url": SOURCE,
            "publication": PUBLICATION,
            "article_licence": "CC-BY-4.0",
            "native_xml_sha256": NATIVE_SHA256,
            "article_metadata": article,
        },
        "subject": "uniprot:P60174",
        "cards": {"baseline": baseline},
        "baseline_assertion_ids": sorted(
            a["id"] for a in card.source_assertion_store.to_list()
        ),
        "identity_basis": {
            "rule": "located_publication_subject_binding@1",
            "paper_accession_location": "fig4/caption",
            "native_structure_relationship_ref": baseline + "#" + relationship["id"],
            "source_assertion_refs": [
                baseline + "#" + sid for sid in relationship["source_assertion_ids"]
            ],
        },
        "proposals": [
            {**spec, "source_fragment": text}
            for spec, text in zip(SPECS, texts, strict=True)
        ],
        "scope": SCOPE,
    }
    write_json(output / "report.json", report)
    write_json(
        output / "proposals.json",
        {"format": FORMAT, "review": REVIEW, "proposals": report["proposals"]},
    )
    write_json(output / "runtime.json", {**runtime, "producer": report["producer"]})
    (output / "review.md").write_text(render(report), encoding="utf-8")
    write_json(
        output / "manifest.json",
        {
            "format": FORMAT,
            "files": {
                name: digest(output / name)
                for name in (
                    "source.xml",
                    "report.json",
                    "runtime.json",
                    "proposals.json",
                    "review.md",
                )
            },
            "cards": report["cards"],
        },
    )


def read(output):
    manifest = read_json(output / "manifest.json")
    require(
        manifest["format"] == FORMAT,
        "Unsupported source review; @1 does not qualify agent readings as human curation",
    )
    require(
        set(manifest["files"])
        == {"source.xml", "report.json", "runtime.json", "proposals.json", "review.md"},
        "Incomplete source review draft",
    )
    for name, fingerprint in manifest["files"].items():
        require(digest(output / name) == fingerprint, "Original member differs")
    report = read_json(output / "report.json")
    require(
        report["format"] == FORMAT and report["cards"] == manifest["cards"],
        "Report binding differs",
    )
    require(report["review"] == REVIEW, "Draft preparer or acceptance differs")
    texts = fragments(output / "source.xml")
    require(
        report["source"]["native_xml_sha256"] == NATIVE_SHA256
        and report["source"]["url"] == SOURCE
        and report["source"]["publication"] == PUBLICATION
        and report["source"]["article_licence"] == "CC-BY-4.0",
        "Wrong original publication or rights",
    )
    require(report["subject"] == "uniprot:P60174", "Wrong source subject")
    require(report["scope"] == SCOPE, "Overstated scientific scope")
    require(
        report["proposals"]
        == [
            {**spec, "source_fragment": text}
            for spec, text in zip(SPECS, texts, strict=True)
        ],
        "Original proposed readings differ",
    )
    require(
        read_json(output / "proposals.json")
        == {"format": FORMAT, "review": REVIEW, "proposals": report["proposals"]},
        "Draft sidecar differs",
    )
    require(
        (output / "review.md").read_text(encoding="utf-8") == render(report),
        "Human draft differs from original report",
    )
    require((output / "knowledge.db").is_file(), "Original store missing")
    require(set(report["cards"]) == {"baseline"}, "Wrong original card membership")
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    with offline(), ackredit.session("independent located source draft reader"):
        before = ackredit.get_attribution().to_dict()
        with sabueso.attribution() as observed:
            pin = report["cards"]["baseline"]
            card = store.load(pin)
            require(card.pinned_ref() == pin, "Original pin differs")
            require(
                sorted(a["id"] for a in card.source_assertion_store.to_list())
                == report["baseline_assertion_ids"],
                "Original baseline source assertions differ",
            )
            require(
                not card.source_assertion_store.find_by_field("literature.claims")
                and not card.quality.get("curation"),
                "Draft was imported as curated knowledge",
            )
            identity = report["identity_basis"]
            require(
                identity["native_structure_relationship_ref"].startswith(pin + "#"),
                "Foreign identity support",
            )
            rel = card.relationship_store.get(
                identity["native_structure_relationship_ref"].rsplit("#", 1)[1]
            )
            require(
                rel["object_ref"] == "pdb:2JK2" and rel["predicate"] == "has_structure",
                "Wrong source representation",
            )
            require(
                identity["rule"] == "located_publication_subject_binding@1"
                and identity["paper_accession_location"] == "fig4/caption"
                and identity["source_assertion_refs"]
                == [pin + "#" + sid for sid in rel["source_assertion_ids"]],
                "Wrong original identity basis",
            )
            runtime = read_json(output / "runtime.json")
            require(runtime["producer"] == report["producer"], "Producer differs")
            require(
                runtime["draft_preparation_observation"] == "not_observed"
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
        "PASS: located draft and original support retained; no curated assertions; scientist review remains pending."
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
