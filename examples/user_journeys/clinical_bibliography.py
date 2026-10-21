"""Follow one source-cited trial and three explicitly selected publication IDs."""

import argparse
import json
from pathlib import Path

import ackredit
import molecule_target
from protein_comparison import digest, offline, read_json, require, write_json

import sabueso
from sabueso.core.errors import SabuesoError
from sabueso.core.snapshot import canonical_json
from sabueso.core.snapshot import digest as value_digest
from sabueso.tools.db import clinicaltrials, europepmc

FORMAT = "sabueso.clinical_bibliography_example@1"
NCT = "NCT00123916"
PMIDS = ["18585495", "26323937", "19753491"]
SCOPE = {
    "molecule": "chembl:CHEMBL110",
    "registry_references": [NCT],
    "article_metadata": ["pubmed:" + pmid for pmid in PMIDS],
    "selection": "explicit caller selection; each identifier requires an upstream source statement",
    "other_trials": "not_queried",
    "other_reference_targets": "not_queried",
    "trial_status_design_results": "not_queried",
    "full_text": "not_queried",
    "efficacy_and_protocol_curation": "not_assessed",
}
SUFFIXES = (
    "results.json",
    "observations.json",
    "workflow.json",
    "report.json",
    "report.md",
    "references.csl.json",
    "references.bib",
)


def upstream(output):
    """Keep all source links distinct, pinned to the unchanged molecule journey."""
    manifest, report, _ = molecule_target.read_stage(output / "molecules", "original")
    support = report["support"]["benznidazole"]
    links = [
        row
        for row in support["relationships"]
        if row["predicate"] == "investigated_for"
    ]
    selected = [row for row in links if NCT in row["qualifiers"].get("trials", [])]
    require(selected, "Selected NCT has no source-stated indication link")
    ids = {item for row in selected for item in row["source_assertion_ids"]}
    return {
        "manifest_sha256": digest(output / "molecules/original.manifest.json"),
        "card_ref": manifest["cards"]["benznidazole"],
        "relationships": selected,
        "assertions": [row for row in support["assertions"] if row["id"] in ids],
        "other_cited_trials_not_queried": sorted(
            {item for row in links for item in row["qualifiers"].get("trials", [])}
            - {NCT}
        ),
    }


def registry_references(result):
    if result is None:
        return None
    study = result["record"]["studies"].get(NCT)
    if study is None:
        return None
    protocol = study["protocolSection"]
    require(
        protocol["identificationModule"]["nctId"] == NCT, "Registry identity differs"
    )
    # The absence of a referencesModule is not an assertion that no articles exist.
    return protocol.get("referencesModule")


def project_report(binding, operations):
    """Frozen example-local linkage rule; never stored as a SourceAssertion."""
    registry = operations["registry"]
    module = registry_references(registry["result"])
    references = (module or {}).get("references", [])
    selected = {}
    for pmid in PMIDS:
        operation = operations["pubmed:" + pmid]
        selected[pmid] = {
            "registry_occurrences": [
                row for row in references if row.get("pmid") == pmid
            ],
            "status": operation["status"],
            "not_queried_reason": operation.get("not_queried_reason"),
            "metadata": operation["result"]["record"] if operation["result"] else None,
        }
    return {
        "rule": "explicit_clinical_bibliography_links@1",
        "scope": SCOPE,
        "upstream": binding,
        "registry_status": registry["status"],
        "registry_record": registry["result"]["record"] if registry["result"] else None,
        "reference_module_status": "returned"
        if module is not None
        else "not_available_in_result",
        "articles": selected,
        "other_reference_forms_not_followed": {
            key: value for key, value in (module or {}).items() if key != "references"
        },
        "unselected_references_not_followed": [
            row for row in references if row.get("pmid") not in PMIDS
        ],
        "limits": [
            "Links follow explicit ChEMBL NCT and registry PMID statements, never intervention names or citation parsing.",
            "Each indication and each native reference occurrence retains its own original support.",
            "Reference modules and publication metadata do not establish trial outcomes, efficacy or comparable protocols.",
            "No full text, abstract interpretation, curation, project Evidence or clinical recommendation is produced.",
            "This local linkage rule is not a runtime-observed scientific derivation.",
            "Fixture access does not establish current online availability; missing local files are not source absence.",
            "The original molecular card still records its original unqueried trial scope.",
        ],
    }


def markdown(report):
    lines = [
        "# Explicit clinical bibliography",
        "",
        f"Registry references: {NCT} — {report['registry_status']}",
        "",
        "| PMID | Metadata access | Registry occurrences |",
        "| --- | --- | --- |",
    ]
    lines += [
        f"| {pmid} | {row['status']} | {len(row['registry_occurrences'])} |"
        for pmid, row in report["articles"].items()
    ]
    lines += ["", "## Scope and limits", ""]
    lines += ["- " + item for item in report["limits"]]
    lines += [
        "",
        "Other cited trials not queried: "
        + ", ".join(report["upstream"]["other_cited_trials_not_queried"]),
        "",
    ]
    return "\n".join(lines)


def request(function, observed):
    start = len(observed.acquisitions)
    try:
        result = function()
        error = None
    except SabuesoError as exc:
        result, error = None, {"type": type(exc).__name__, "message": str(exc)}
    records = observed.acquisitions[start:]
    require(len(records) == 1, "Expected one explicit source operation")
    return {
        "status": records[0]["outcome"],
        "result": result,
        "error": error,
        "records": records,
    }


def produce(output, fixtures, stage):
    if stage == "original":
        require(
            not output.exists() or not any(output.iterdir()), "Output must be empty"
        )
        output.mkdir(parents=True, exist_ok=True)
        molecule_target.produce(output / "molecules", fixtures, "original")
    else:
        require(not (output / "later.manifest.json").exists(), "Later stage exists")
        read_stage(output, "original")
    binding = upstream(output)
    timestamp = f"{stage} clinical fixture read"
    with offline(), ackredit.session("explicit clinical bibliography"):
        with sabueso.attribution() as observed, ackredit.capture(stage) as workflow:
            operations = {
                "registry": request(
                    lambda: clinicaltrials.get_study_references(
                        [NCT],
                        client=clinicaltrials.FixtureClinicalTrialsClient(
                            fixtures, retrieved_at=timestamp
                        ),
                    ),
                    observed,
                )
            }
            module = registry_references(operations["registry"]["result"])
            references = (module or {}).get("references", [])
            for pmid in PMIDS:
                identifier = "pubmed:" + pmid
                if not any(row.get("pmid") == pmid for row in references):
                    operations[identifier] = {
                        "status": "not_queried",
                        "not_queried_reason": "no_returned_registry_PMID_statement",
                        "result": None,
                        "error": None,
                        "records": [],
                    }
                    continue
                operations[identifier] = request(
                    lambda identifier=identifier: europepmc.get_article(
                        identifier,
                        client=europepmc.FixtureEuropePMCClient(
                            fixtures, retrieved_at=timestamp
                        ),
                    ),
                    observed,
                )
        write_json(output / f"{stage}.observations.json", observed.acquisitions)
        write_json(output / f"{stage}.workflow.json", workflow.attribution.to_dict())
        for format, suffix in (("csl-json", "csl.json"), ("bibtex", "bib")):
            (output / f"{stage}.references.{suffix}").write_text(
                workflow.attribution.report(format=format), encoding="utf-8"
            )
    write_json(output / f"{stage}.results.json", operations)
    report = project_report(binding, operations)
    write_json(output / f"{stage}.report.json", report)
    (output / f"{stage}.report.md").write_text(markdown(report), encoding="utf-8")
    manifest = {
        "format": FORMAT,
        "stage": stage,
        "scope": SCOPE,
        "producer": {
            "sdk": sabueso.__version__,
            "example_sha256": digest(Path(__file__)),
        },
        "upstream": binding,
        "files": {
            f"{stage}.{suffix}": digest(output / f"{stage}.{suffix}")
            for suffix in SUFFIXES
        },
    }
    if stage == "later":
        manifest["original_manifest_sha256"] = digest(output / "original.manifest.json")
    write_json(output / f"{stage}.manifest.json", manifest)
    # Validate the actual saved artifact before declaring successful production.
    read_stage(output, stage)
    return manifest


def check_operation(operation, source, kind, query, producer):
    records, result = operation["records"], operation["result"]
    if operation["status"] == "not_queried":
        require(
            not records and result is None and operation["error"] is None,
            "Unqueried operation has a result or execution",
        )
        return
    require(len(records) == 1, "Missing original operation")
    record = records[0]
    require(
        record["source"] == source
        and record["operation"] == kind
        and record["query"] == query,
        "Operation belongs to another request",
    )
    require(
        record["producer"]["version"] == producer["sdk"], "Producer version differs"
    )
    require(
        operation["status"] == record["outcome"] and record["network_attempts"] == 0,
        "Wrong operation outcome or access scope",
    )
    if result is None:
        require(
            operation["error"] is not None
            and record["outcome"]
            in {
                "failed",
                "unavailable",
                "partial",
            },
            "Missing result presented as a source answer",
        )
        return
    require(
        operation["error"] is None
        and result["source"] == source
        and result["kind"] == kind
        and result["query"] == query,
        "Result belongs to another source or query",
    )
    require(result["acquisition_trace"]["records"] == records, "Original trace differs")
    require(
        result["version"] == record["source_version"]["value"]
        and result["retrieved_at"] == record["retrieved_at"],
        "Source version or time differs",
    )
    if kind == "study_references":
        # Native fixture response retains the mapping from requested IDs to studies.
        require(
            record["response_identity"]["hash"]
            == value_digest(canonical_json(result["record"]["studies"])),
            "Registry response identity differs",
        )
        require(
            {
                entry["nct_id"]: entry["study"]
                for entry in record["entries"]
                if entry["outcome"] == "received"
            }
            == result["record"]["studies"],
            "Registry result differs from original entries",
        )
    else:
        require(
            [
                entry["article"]
                for entry in record["entries"]
                if entry["outcome"] == "received"
            ]
            == result["record"]["articles"],
            "Article metadata differs from original entries",
        )
        require(
            result["record"]["requested_identifier"] == query["identifier"],
            "Article identity differs",
        )
        require(
            all(
                article.get("pmid") == query["identifier"].split(":", 1)[1]
                for article in result["record"]["articles"]
            ),
            "Article has no source-stated PMID binding",
        )


def read_stage(output, stage):
    manifest = read_json(output / f"{stage}.manifest.json")
    require(
        manifest["format"] == FORMAT
        and manifest["stage"] == stage
        and manifest["scope"] == SCOPE,
        "Wrong manifest or scope",
    )
    require(
        set(manifest["files"]) == {f"{stage}.{suffix}" for suffix in SUFFIXES},
        "Incomplete original file bindings",
    )
    for name, expected in manifest["files"].items():
        require(
            (output / name).is_file() and digest(output / name) == expected,
            f"Missing or changed original file: {name}",
        )
    if stage == "later":
        require(
            manifest["original_manifest_sha256"]
            == digest(output / "original.manifest.json"),
            "Original manifest differs",
        )
    require(
        manifest["upstream"] == upstream(output), "Original indication support differs"
    )
    operations = read_json(output / f"{stage}.results.json")
    require(
        set(operations) == {"registry", *SCOPE["article_metadata"]},
        "Different operation scope",
    )
    check_operation(
        operations["registry"],
        "ClinicalTrials.gov",
        "study_references",
        {"nct_ids": [NCT]},
        manifest["producer"],
    )
    require(
        operations["registry"]["status"] != "not_queried", "Registry was not requested"
    )
    module = registry_references(operations["registry"]["result"])
    for pmid in PMIDS:
        operation = operations["pubmed:" + pmid]
        cited = any(
            row.get("pmid") == pmid for row in (module or {}).get("references", [])
        )
        require(
            cited == (operation["status"] != "not_queried"),
            "Article lacks its required registry link",
        )
        if not cited:
            require(
                operation.get("not_queried_reason")
                == "no_returned_registry_PMID_statement",
                "Wrong unqueried prerequisite",
            )
        check_operation(
            operation,
            "Europe PMC",
            "article",
            {"identifier": "pubmed:" + pmid},
            manifest["producer"],
        )
    observations = read_json(output / f"{stage}.observations.json")
    require(
        observations == [r for op in operations.values() for r in op["records"]],
        "Observed operations differ from original results",
    )
    workflow = ackredit.Attribution.from_dict(
        read_json(output / f"{stage}.workflow.json")
    )
    for key in ("items", "uses"):
        expected = {
            json.dumps(item, sort_keys=True)
            for record in observations
            for item in (record["provider"].get("attribution") or {}).get(key, [])
        }
        require(
            expected
            == {json.dumps(item, sort_keys=True) for item in workflow.to_dict()[key]},
            f"Workflow {key} differ from original operations",
        )
    report = read_json(output / f"{stage}.report.json")
    require(
        report == project_report(manifest["upstream"], operations),
        "Clinical report differs from original inputs",
    )
    require(
        (output / f"{stage}.report.md").read_text(encoding="utf-8") == markdown(report),
        "Readable report differs",
    )
    for format, suffix in (("csl-json", "csl.json"), ("bibtex", "bib")):
        require(
            (output / f"{stage}.references.{suffix}").read_text(encoding="utf-8")
            == workflow.report(format=format),
            "Original bibliography differs",
        )
    return manifest, report


def read(output):
    with offline(), ackredit.session("independent clinical bibliography reader"):
        before = ackredit.get_attribution().to_dict()
        with sabueso.attribution() as observed:
            for stage in ("original", "later"):
                if stage == "later" and not (output / "later.manifest.json").exists():
                    continue
                _, report = read_stage(output, stage)
                write_json(
                    output / f"{stage}.reader.json",
                    {
                        "original_report": report,
                        "observed_acquisitions": 0,
                    },
                )
                print(
                    f"{stage}: {NCT}, three explicit PMID selections; see per-request outcomes; efficacy not assessed"
                )
        require(
            not observed.acquisitions
            and not observed.records
            and not observed.literature,
            "Reader observed a new execution",
        )
        require(ackredit.get_attribution().to_dict() == before, "Reader added credit")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("produce", "read", "reacquire"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, default=Path("temp_data"))
    args = parser.parse_args()
    try:
        if args.action == "read":
            read(args.output)
        else:
            produce(
                args.output,
                args.fixtures,
                "original" if args.action == "produce" else "later",
            )
    except (ValueError, KeyError, OSError, SabuesoError) as exc:
        parser.exit(2, f"FAIL: {exc}\n")


if __name__ == "__main__":
    main()
