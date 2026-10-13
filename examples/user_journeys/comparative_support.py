"""Save public comparisons, explanations and original credit; read them inertly."""

import argparse
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path

import ackredit
from protein_comparison import digest, offline, read_json, require, write_json

import sabueso
from sabueso.core.errors import SabuesoError
from sabueso.core.snapshot import canonical_json
from sabueso.core.snapshot import digest as result_digest
from sabueso.core.source_assertion_store import acquisition_of
from sabueso.core.tissue_usage import TISSUE_TEXT
from sabueso.resolver import EntityResolver, FixtureUniProtClient
from sabueso.tools.db.gnomad import FixtureGnomADClient
from sabueso.tools.db.gtex import FixtureGTExClient
from sabueso.tools.db.uniref import FixtureUniRefClient

FORMAT = "sabueso.comparative_support_example@3"
UNOBSERVED_FORMAT = "sabueso.comparative_support_example@2"
LEGACY_FORMAT = "sabueso.comparative_support_example@1"
RUNTIME_FORMAT = "sabueso.comparative_support_runtime@1"
ACCESSIONS = {"subject": "P52270", "strain": "Q4DV43", "human": "P60174"}
RULES = {
    "sequence": ("sequence_differences_explanation@1", "equal_length_positions@1"),
    "variants": ("variant_tissue_usage_explanation@1", "pext_at_variant@1"),
    "isoforms": ("isoform_tissue_usage_explanation@1", "isoform_exon_usage@2"),
}
CURRENT_RULES = {
    "sequence": RULES["sequence"],
    "variants": ("variant_tissue_usage_explanation@2", "pext_at_variant@2"),
    "isoforms": ("isoform_tissue_usage_explanation@2", "isoform_exon_usage@3"),
}
OPERATIONS = {
    "sequence": "sequence_differences",
    "variants": "variant_tissue_usage",
    "isoforms": "isoform_tissue_usage",
}


def produce(output, fixtures, stage, *, legacy=False, unobserved=False):
    selected_format = (
        LEGACY_FORMAT if legacy else UNOBSERVED_FORMAT if unobserved else FORMAT
    )
    if stage == "original":
        require(
            not output.exists() or not any(output.iterdir()), "Output must be empty"
        )
        output.mkdir(parents=True, exist_ok=True)
    else:
        require(not (output / "later.manifest.json").exists(), "Later stage exists")
        original, _, _ = read_stage(output, "original")
        selected_format = original["format"]
    rules = RULES if selected_format == LEGACY_FORMAT else CURRENT_RULES
    observed = selected_format == FORMAT
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    timestamp = f"{stage} public fixture read"
    cards = {}
    with (
        offline(),
        ackredit.session("public comparative support"),
        sabueso.attribution() if observed else nullcontext() as run,
        ackredit.capture(stage) if observed else nullcontext() as workflow,
    ):
        resolver = EntityResolver(
            FixtureUniProtClient(fixtures, retrieved_at=timestamp)
        )
        for role, accession in ACCESSIONS.items():
            options = {}
            if role == "subject":
                options = {
                    "uniref": True,
                    "uniref_client": FixtureUniRefClient(
                        fixtures, retrieved_at=timestamp
                    ),
                }
            elif role == "human":
                options = {
                    "gnomad": {},
                    "exon_usage": True,
                    "gtex": True,
                    "gnomad_client": FixtureGnomADClient(
                        fixtures, retrieved_at=timestamp
                    ),
                    "gtex_client": FixtureGTExClient(fixtures, retrieved_at=timestamp),
                }
            cards[role] = sabueso.resolve(accession, resolver=resolver, **options)[0]
        pins = {role: store.save(card) for role, card in cards.items()}
        report = {
            "cards": pins,
            "sequence": cards["subject"].explain_sequence_differences(cards["strain"]),
            "variants": cards["human"].explain_variant_tissue_usage(
                usage_rule=rules["variants"][1]
            ),
            "isoforms": cards["human"].explain_isoform_tissue_usage(
                usage_rule=rules["isoforms"][1]
            ),
            "execution_observation": {
                "status": "not_observed",
                "scope": "comparative_operations",
                "reason": "dedicated_comparative_operation_sidecars_are_separate_work",
            },
        }
        if observed:
            report["views"] = {
                "sequence": cards["subject"].sequence_differences(cards["strain"]),
                "variants": cards["human"].variant_tissue_usage(
                    usage_rule=rules["variants"][1]
                ),
                "isoforms": cards["human"].isoform_tissue_usage(
                    usage_rule=rules["isoforms"][1]
                ),
            }
            report["execution_observation"] = {
                "status": "observed",
                "scope": "comparative_operations",
                "runtime_file": f"{stage}.runtime.json",
                "operation_record_count": len(run.operations),
            }
    filename = f"{stage}.report.json"
    write_json(output / filename, report)
    files = {filename: digest(output / filename)}
    if observed:
        runtime_file = f"{stage}.runtime.json"
        write_json(
            output / runtime_file,
            {
                "format": RUNTIME_FORMAT,
                "stage": stage,
                "cards": pins,
                "producer": {
                    "sabueso": sabueso.__version__,
                    "ackredit": ackredit.__version__,
                },
                "report_sha256": files[filename],
                "operations": run.operations,
                "acquisitions": run.acquisitions,
                "workflow": workflow.attribution.to_dict(),
            },
        )
        files[runtime_file] = digest(output / runtime_file)
    manifest = {
        "format": selected_format,
        "stage": stage,
        "cards": pins,
        "files": files,
        "scope": "public_frozen_responses_not_live_or_installed_artifact_qualification",
    }
    if stage == "later":
        manifest["original_manifest_sha256"] = digest(output / "original.manifest.json")
    write_json(output / f"{stage}.manifest.json", manifest)


def check_support(value, cards):
    """Verify saved locators and complete assertion envelopes without deriving anew."""
    if isinstance(value, list):
        for item in value:
            check_support(item, cards)
    elif isinstance(value, dict):
        if "source_assertion_ref" in value:
            pin, item_id = value["source_assertion_ref"].rsplit("#", 1)
            require(pin in cards, "Assertion belongs to another card")
            assertion = cards[pin].source_assertion_store.get(item_id)
            if not value.get("found"):
                require(
                    assertion is None,
                    "Recorded missing assertion now exists at original pin",
                )
            else:
                require(assertion is not None, "Missing original assertion")
                source = assertion.get("source") or {}
                expected = {
                    "id": item_id,
                    "field_path": assertion.get("field_path"),
                    "subject_ref": assertion.get("subject_ref"),
                    "source": source.get("name"),
                    "record": source.get("record_id"),
                    "version": source.get("version"),
                    "retrieved_at": assertion.get("retrieved_at"),
                    "asserted_value": assertion.get("asserted_value"),
                    "acquisition": acquisition_of(assertion),
                }
                require(
                    all(value.get(k) == v for k, v in expected.items()),
                    "Original assertion differs",
                )
                require(
                    value.get("source_metadata")
                    == (assertion.get("source_metadata") or None),
                    "Assertion metadata differs",
                )
        if "relationship_ref" in value:
            pin, item_id = value["relationship_ref"].rsplit("#", 1)
            require(
                pin in cards
                and cards[pin].relationship_store.get(item_id) == value["relationship"],
                "Original relationship differs",
            )
        if "stored" in value and "field_path" in value and "card_ref" in value:
            require(value["card_ref"] in cards, "Field belongs to another card")
            node = cards[value["card_ref"]].get(value["field_path"])
            require(
                (node is not None) == value["stored"], "Stored field presence differs"
            )
            if node is not None:
                require(node == value["node"], "Original selected field differs")
                require(
                    value["selection_rules"]
                    == cards[value["card_ref"]].selection_rules,
                    "Selection rules differ",
                )
        if "locator" in value:
            locator = value["locator"]
            require(locator["card_ref"] in cards, "Locator belongs to another card")
            card = cards[locator["card_ref"]]
            path = locator["field_path"]
            if path == "quality.enrichments":
                rows = card.quality.get("enrichments") or []
                key = "record"
            else:
                rows = (card.get(path) or {}).get("value") or []
                key = "value"
            require(
                0 <= locator["index"] < len(rows), "Original input locator is absent"
            )
            if key in value:
                require(
                    rows[locator["index"]] == value[key],
                    "Original input locator differs",
                )
        for item in value.values():
            check_support(item, cards)


def check_operation(record, key, report, cards, producer):
    """Bind retained execution/support/credit to original inputs without executing."""
    view = report["views"][key]
    require(
        view == report[key]["view"], "Executed view differs from original explanation"
    )
    require(
        record["format"] == "sabueso.comparative_operation@1"
        and record["operation"] == OPERATIONS[key]
        and record["status"] == "completed"
        and record["acquisition"] == "not_performed",
        "Wrong comparative execution",
    )
    require(
        record["producer"]
        == {
            "name": "sabueso",
            "version": producer["sabueso"],
            "version_basis": "runtime_package_metadata",
        }
        and view["rule"]["sabueso_version"] == producer["sabueso"],
        "Original producer differs",
    )
    started, completed = (
        datetime.fromisoformat(record[k]) for k in ("started_at", "completed_at")
    )
    require(
        started.tzinfo is not None
        and completed.tzinfo is not None
        and started <= completed,
        "Invalid original execution times",
    )
    applied = [view["rule"]]
    if (view.get("tissue_terms") or {}).get("rule"):
        applied.append(view["tissue_terms"]["rule"])
    require(
        record["rule"] == view["rule"]
        and record["applied_rules"] == applied
        and record["result_id"] == result_digest(canonical_json(view))
        and record["result_basis"] == view.get("basis"),
        "Execution result binding differs",
    )
    parameters = (
        {}
        if key == "sequence"
        else {
            "threshold": view["rule"]["parameters"]["threshold"],
            "usage_rule": view["rule"]["rule"],
        }
    )
    require(record["parameters"] == parameters, "Executed parameters differ")
    expected_roles = (
        [
            ("subject", report["cards"]["subject"]),
            ("comparator", report["cards"]["strain"]),
        ]
        if key == "sequence"
        else [("subject", report["cards"]["human"])]
    )
    require(
        [(s["role"], s["card_ref"]) for s in record["inputs"]] == expected_roles,
        "Execution input roles differ",
    )
    require(
        record["support_rule"]
        == {
            "rule": "comparative_input_scope@1",
            "inputs": [pin for _, pin in expected_roles],
            "parameters": {},
            "sabueso_version": producer["sabueso"],
        },
        "Original support rule differs",
    )
    expected_resources = {}
    expected_gaps = []
    for scope in record["inputs"]:
        pin = scope["card_ref"]
        card = cards[pin]
        paths = [field["field_path"] for field in scope["fields"]]
        expected_paths = {
            field["field_path"]
            for field in report[key]["fields"]
            if field["card_ref"] == pin
        }
        require(
            len(paths) == len(set(paths)) and set(paths) == expected_paths,
            "Execution fields differ",
        )
        for field in scope["fields"]:
            path = field["field_path"]
            node = card.get(path)
            all_tissue = path == TISSUE_TEXT
            ids = (
                [a["id"] for a in card.source_assertion_store.find_by_field(path)]
                if all_tissue
                else (node or {}).get("source_assertion_ids") or []
            )
            basis = (
                "all_stored_tissue_specificity_statements"
                if all_tissue
                else "selected_input_field"
            )
            if node is None and not ids:
                expected_gaps.append(
                    {
                        "role": scope["role"],
                        "card_ref": pin,
                        "field_path": path,
                        "reason": "input_not_stated",
                    }
                )
            elif not ids:
                expected_gaps.append(
                    {
                        "role": scope["role"],
                        "card_ref": pin,
                        "field_path": path,
                        "reason": "input_support_not_stated",
                    }
                )
            require(
                field["stored"] == (node is not None)
                and field["source_assertion_refs"]
                == [pin + "#" + identifier for identifier in ids]
                and field["support_basis"] == basis,
                "Execution assertion scope differs",
            )
            for identifier in ids:
                assertion = card.source_assertion_store.get(identifier)
                require(
                    assertion is not None and assertion["field_path"] == path,
                    "Original execution support is absent",
                )
                source = assertion["source"]
                identity = {
                    k: source.get(k) for k in ("name", "type", "record_id", "version")
                }
                resource_id = "sabueso:source-record:" + result_digest(
                    canonical_json(identity)
                )
                resource = expected_resources.setdefault(
                    resource_id, {"source": identity, "uses": []}
                )
                resource["uses"].append(
                    {
                        "role": scope["role"],
                        "card_ref": pin,
                        "field_path": path,
                        "source_assertion_ref": pin + "#" + identifier,
                        "support_basis": basis,
                        "retrieved_at": assertion.get("retrieved_at"),
                        "acquisition": acquisition_of(assertion),
                    }
                )
    require(
        record["support_gaps"] == expected_gaps
        and record["support_status"] == ("partial" if expected_gaps else "available"),
        "Original support gaps differ",
    )
    require(
        {r["id"] for r in record["resources"]} == set(expected_resources)
        and len(record["resources"]) == len(expected_resources),
        "Original execution resources differ",
    )
    context = {
        k: record[k]
        for k in (
            "execution_id",
            "producer",
            "result_id",
            "inputs",
            "rule",
            "applied_rules",
        )
    }
    used_by = "sabueso.card." + record["operation"]
    bibliography = {item["id"]: item for item in record["bibliography"]}
    software_id = record["bibliography"][0]["id"]
    require(
        bibliography[software_id]["type"] == "software"
        and bibliography[software_id]["version"] == producer["sabueso"],
        "Original software citation differs",
    )
    expected_uses = [
        {
            "item_id": software_id,
            "used_by": used_by,
            "roles": ["executed_software"],
            "context": context,
        }
    ]
    for resource in record["resources"]:
        expected = expected_resources[resource["id"]]
        require(
            resource["source"] == expected["source"]
            and resource["uses"] == expected["uses"]
            and resource["version_basis"] == "stored_source_assertion_label",
            "Original source-record use differs",
        )
        for usage in resource["uses"]:
            use_context = {**context, **usage, "source_record": resource["source"]}
            expected_uses.append(
                {
                    "item_id": resource["id"],
                    "used_by": used_by,
                    "roles": ["stored_knowledge"],
                    "context": use_context,
                }
            )
            for identifier in resource["description_citation_ids"]:
                require(
                    identifier in bibliography, "Original resource citation is absent"
                )
                expected_uses.append(
                    {
                        "item_id": identifier,
                        "used_by": used_by,
                        "roles": ["resource_description"],
                        "context": use_context,
                    }
                )
    provider = record["provider"]
    require(
        provider["status"] == "available"
        and provider["version"] == producer["ackredit"],
        "Incomplete original execution attribution",
    )
    saved = ackredit.Attribution.from_dict(provider["attribution"]).to_dict()
    require(
        {canonical_json(use) for use in saved["uses"]}
        == {canonical_json(use) for use in expected_uses},
        "Original execution credit differs",
    )
    items = {item["id"]: item for item in saved["items"]}
    require(
        set(items) == set(bibliography) | set(expected_resources)
        and all(items[identifier] == item for identifier, item in bibliography.items()),
        "Original execution bibliography differs",
    )
    for resource in record["resources"]:
        item = items[resource["id"]]
        source = resource["source"]
        require(
            item.get("version") == source["version"]
            and item["title"] == f"{source['name']} record {source['record_id']}"
            and item["type"]
            == ("dataset" if source["type"] == "database" else "other"),
            "Original source-record credit metadata differs",
        )


def read_runtime(output, manifest, report, cards):
    stage = manifest["stage"]
    runtime = read_json(output / f"{stage}.runtime.json")
    require(
        runtime["format"] == RUNTIME_FORMAT
        and runtime["stage"] == stage
        and runtime["cards"] == manifest["cards"]
        and runtime["report_sha256"] == manifest["files"][f"{stage}.report.json"],
        "Runtime belongs to another report",
    )
    require(
        report["execution_observation"]
        == {
            "status": "observed",
            "scope": "comparative_operations",
            "runtime_file": f"{stage}.runtime.json",
            "operation_record_count": 3,
        }
        and len(runtime["operations"]) == 3,
        "Incomplete original execution observation",
    )
    require(set(report["views"]) == set(OPERATIONS), "Unbound comparative result")
    ids = [record["execution_id"] for record in runtime["operations"]]
    require(
        len(set(ids)) == 3
        and all(identifier.startswith("sabueso:operation:") for identifier in ids),
        "Repeated or invalid execution identity",
    )
    for key, record in zip(OPERATIONS, runtime["operations"], strict=True):
        check_operation(record, key, report, cards, runtime["producer"])
    workflow = ackredit.Attribution.from_dict(runtime["workflow"])
    for key in ("items", "uses"):
        expected = {
            canonical_json(value)
            for record in runtime["acquisitions"] + runtime["operations"]
            for value in (record["provider"].get("attribution") or {}).get(key, [])
        }
        require(
            expected == {canonical_json(value) for value in workflow.to_dict()[key]},
            "Workflow differs from original observations",
        )
    return runtime


def read_stage(output, stage):
    manifest = read_json(output / f"{stage}.manifest.json")
    require(
        manifest["format"] in (FORMAT, UNOBSERVED_FORMAT, LEGACY_FORMAT)
        and manifest["stage"] == stage,
        "Wrong manifest",
    )
    require(set(manifest["cards"]) == set(ACCESSIONS), "Wrong card roles")
    filename = f"{stage}.report.json"
    filenames = (
        {filename, f"{stage}.runtime.json"}
        if manifest["format"] == FORMAT
        else {filename}
    )
    require(set(manifest["files"]) == filenames, "Wrong report membership")
    for name in filenames:
        require(
            digest(output / name) == manifest["files"][name],
            "Changed original report or runtime",
        )
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    cards = {}
    for role, ref in manifest["cards"].items():
        card = store.load(ref)
        require(
            card.pinned_ref() == ref
            and card.id == f"sabueso:protein:uniprot:{ACCESSIONS[role]}",
            "Wrong card binding",
        )
        require(card.acquisition_trace is None, "Saved reader has fresh acquisition")
        cards[ref] = card
    report = read_json(output / filename)
    require(report["cards"] == manifest["cards"], "Report roles differ")
    pins = [manifest["cards"][role] for role in ("subject", "strain")]
    rules = RULES if manifest["format"] == LEGACY_FORMAT else CURRENT_RULES
    for key, (explanation_rule, view_rule) in rules.items():
        explanation = report[key]
        require(
            explanation["rule"]["rule"] == explanation_rule
            and explanation["view"]["rule"]["rule"] == view_rule,
            "Unsupported original rules",
        )
        expected = pins if key == "sequence" else [manifest["cards"]["human"]]
        require(explanation["rule"]["inputs"] == expected, "Explanation pins differ")
        actual = (
            explanation["card_refs"] if key == "sequence" else [explanation["card_ref"]]
        )
        require(actual == expected, "Explanation role differs")
        require(
            {f["card_ref"] for f in explanation["fields"]} == set(expected),
            "Input field pins differ",
        )
        if key != "sequence":
            require(
                [r["item"] for r in explanation["items"]]
                == explanation["view"]["items"],
                "Original view items differ",
            )
            require(
                explanation["rule"]["parameters"]
                == explanation["view"]["rule"]["parameters"],
                "Original parameters differ",
            )
        check_support(explanation, cards)
    runtime = (
        read_runtime(output, manifest, report, cards)
        if manifest["format"] == FORMAT
        else None
    )
    return manifest, report, runtime


def read(output):
    with (
        offline(),
        ackredit.session("inert comparative reader"),
        sabueso.attribution() as observed,
    ):
        before = ackredit.get_attribution().to_dict()
        execution_ids = set()
        for stage in ("original", "later"):
            if not (output / f"{stage}.manifest.json").exists():
                require(stage == "later", "Original stage missing")
                continue
            manifest, report, runtime = read_stage(output, stage)
            if stage == "later":
                require(
                    manifest["original_manifest_sha256"]
                    == digest(output / "original.manifest.json"),
                    "Original manifest changed",
                )
                old = read_json(output / "original.manifest.json")
                require(
                    old["format"] == manifest["format"],
                    "Reacquisition changed the scientific rule generation",
                )
                require(
                    all(old["cards"][r] != manifest["cards"][r] for r in ACCESSIONS),
                    "Reacquisition did not retain distinct revisions",
                )
            receipt = {
                "cards": manifest["cards"],
                "original_report": report,
                "observed_acquisitions": 0,
            }
            if manifest["format"] == FORMAT:
                ids = {record["execution_id"] for record in runtime["operations"]}
                require(
                    not execution_ids.intersection(ids),
                    "Reacquisition reused an earlier execution identity",
                )
                execution_ids.update(ids)
                workflow = ackredit.Attribution.from_dict(runtime["workflow"])
                receipt.update(original_runtime=runtime, observed_operations=0)
                for format, suffix in (("csl-json", "csl.json"), ("bibtex", "bib")):
                    (output / f"{stage}.references.{suffix}").write_text(
                        workflow.report(format=format), encoding="utf-8"
                    )
            write_json(output / f"{stage}.reader.json", receipt)
        require(
            not observed.operations
            and not observed.acquisitions
            and not observed.records
            and not observed.literature,
            "Reader observed a fresh execution",
        )
        require(
            ackredit.get_attribution().to_dict() == before, "Reader generated credit"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("produce", "read", "reacquire"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, default=Path("temp_data"))
    formats = parser.add_mutually_exclusive_group()
    formats.add_argument(
        "--legacy",
        action="store_true",
        help="Produce the explicit historical @1 report format",
    )
    formats.add_argument(
        "--unobserved",
        action="store_true",
        help="Produce historical @2 explanations without execution sidecars",
    )
    args = parser.parse_args()
    try:
        if args.action == "read":
            read(args.output)
        else:
            produce(
                args.output,
                args.fixtures,
                "original" if args.action == "produce" else "later",
                legacy=args.legacy,
                unobserved=args.unobserved,
            )
    except (ValueError, KeyError, TypeError, IndexError, OSError, SabuesoError) as exc:
        parser.exit(2, f"FAIL: {exc}\n")


if __name__ == "__main__":
    main()
