"""Review public structure, assay and located-literature support at original pins."""

import argparse
import json
from copy import deepcopy
from pathlib import Path

import ackredit
import pyunitwizard as puw
from protein_comparison import digest, offline, read_json, require, write_json

import sabueso
from sabueso.resolver import EntityResolver, FixtureUniProtClient
from sabueso.tools.db.bindingdb import FixtureBindingDBClient
from sabueso.tools.db.chembl import FixtureChEMBLClient
from sabueso.tools.db.europepmc import FixtureEuropePMCClient
from sabueso.tools.db.rcsb import FixtureRCSBClient
from sabueso.tools.db.unichem import FixtureUniChemClient

FORMAT = "sabueso.scientific_dossier_example@2"
LEGACY_FORMAT = "sabueso.scientific_dossier_example@1"
ROLES = {"subject": "P52270", "comparator": "P60174"}
STRUCTURES = {
    "subject": ["1TCD", "1SUX", "2V5B", "1IIG"],
    "comparator": ["1HTI", "1KLG", "2VOM", "4UNK"],
}
ARTICLES = {"subject": "MED:18562316", "comparator": "PMC:PMC12400196"}
STRUCTURE_CRITERIA = {
    "rule": "public_structure_review_criteria@1",
    "maximum_resolution": {"value": 3.0, "unit": "angstrom"},
    "minimum_coverage": 0.9,
    "sequence": "reference",
    "oligomer": "Homo 2-mer",
    "oligomer_basis": "author",
    "region": "completely_supported_source_active_site_positions",
}
ASSAY_CRITERIA = {
    "rule": "public_assay_record_review_criteria@1",
    "target_assignment": "D",
    "measurement_type": "IC50",
    "relation": "=",
    "require_normalized_concentration": True,
    "comparability": "requires_review_of_actual_assay_conditions",
}
CONTEXT_FIELDS = (
    "target",
    "assay.id",
    "assay.type",
    "assay.description",
    "assay.organism",
    "assay.tax_id",
    "assay.confidence_score",
    "assay.variant_mutation",
    "document.id",
    "document.pubmed",
    "document.doi",
)


def context_value(qualifiers, path):
    value = qualifiers
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def stored_context_review(qualifiers):
    """Describe stored fields only; missing qualifiers are not source absence."""
    return {
        "rule": "stored_assay_context_review@1",
        "basis": "original_saved_qualifiers_only",
        "fields": {
            path: "not_in_saved_qualifiers"
            if context_value(qualifiers, path) in (None, "")
            else "stored"
            for path in CONTEXT_FIELDS
        },
        "experimental_protocol": "not_curated",
        "experimental_comparability": "not_established",
        "same_assay_assignment": "not_performed",
    }


def binding(card, relationship, pin=None):
    pin = pin or card.pinned_ref()
    return {
        "relationship_ref": pin + "#" + relationship["id"],
        "source_assertion_refs": [
            pin + "#" + identifier
            for identifier in relationship.get("source_assertion_ids", [])
        ],
        "support_basis": "relationship_not_individual_qualifier_lineage",
    }


def check(value, expected, *, unknown=None):
    return {
        "value": value,
        "expected": expected,
        "status": "unknown"
        if value is None
        else "met"
        if value == expected
        else "not_met",
        "unknown_reason": unknown if value is None else None,
    }


def decision(checks):
    return (
        "does_not_meet_recorded_criteria"
        if any(node["status"] == "not_met" for node in checks.values())
        else "insufficient_information"
        if any(node["status"] == "unknown" for node in checks.values())
        else "meets_recorded_criteria"
    )


def structure_review(card):
    pin = card.pinned_ref()
    residues = card.get_residues()
    positions = [
        row["position"]
        for row in residues
        if any(
            annotation["field_path"] == "features_positional.active_site"
            and annotation["support_status"] == "complete"
            for annotation in row["annotations"]
        )
    ]
    view = card.structures(include_fragments=True, region=positions or None)
    rows = []
    for item in view["items"]:
        relationship = card.relationship_store.get(item["relationship_id"])
        resolution = item["resolution"]
        coverage = item["coverage"]
        maximum = STRUCTURE_CRITERIA["maximum_resolution"]
        checks = {
            "resolution": check(
                None
                if resolution is None
                else puw.get_value(
                    resolution, to_unit=maximum["unit"], value_type=float
                )
                <= maximum["value"],
                True,
                unknown="resolution_not_stored",
            ),
            "coverage": check(
                None
                if coverage is None
                else coverage >= STRUCTURE_CRITERIA["minimum_coverage"],
                True,
                unknown="coverage_not_stored",
            ),
            "sequence": check(
                item["state"]["sequence"],
                STRUCTURE_CRITERIA["sequence"],
                unknown="sequence_state_not_stored",
            ),
            "oligomer": check(
                item["state"]["oligomer"],
                STRUCTURE_CRITERIA["oligomer"],
                unknown="assembly_state_not_stored",
            ),
            "assembly_basis": check(
                item["oligomer_basis"],
                STRUCTURE_CRITERIA["oligomer_basis"],
                unknown="assembly_basis_not_stored",
            ),
            "region_coordinates": check(
                None
                if not positions or item["complete_chains"] is None
                else bool(item["complete_chains"]),
                True,
                unknown="source_active_sites_or_observed_region_not_stored",
            ),
        }
        rows.append(
            {
                **binding(card, relationship, pin),
                "item": item,
                "checks": checks,
                "status": decision(checks),
                "qualifier_conflicts": relationship.get("qualifier_conflicts") or {},
                "project_model_selection": "not_performed",
            }
        )
    return {
        "rule": deepcopy(STRUCTURE_CRITERIA),
        "card_ref": pin,
        "positions": positions,
        "active_site_input": card.get("features_positional.active_site"),
        "sequence_input": card.get("sequence.primary"),
        "position_axis": "this_card_UniProt_canonical_sequence",
        "cross_protein_correspondence": "not_supplied",
        "view_rules": {"coverage": view["classification"], "state": view["state_rule"]},
        "rows": rows,
        "source_outcomes": [
            record
            for record in card.quality.get("enrichments", [])
            if record.get("source") == "RCSB PDB"
        ],
    }


def assay_review(card, *, report_format=FORMAT):
    pin = card.pinned_ref()
    rows = []
    for relationship in card.relationships("has_bioactivity"):
        qualifiers = relationship.get("qualifiers") or {}
        measurement = qualifiers.get("measurement") or {}
        assay = qualifiers.get("assay") or {}
        normalized = measurement.get("normalized")
        concentration = None
        if normalized is not None:
            concentration = puw.get_dimensionality(
                puw.quantity(normalized["value"], normalized["unit"])
            ) == puw.get_dimensionality(puw.quantity(1, "nanomolar"))
        checks = {
            "target_assignment": check(
                assay.get("relationship_type"),
                "D",
                unknown="target_assignment_not_stored",
            ),
            "measurement_type": check(
                measurement.get("type"), "IC50", unknown="measurement_type_not_stored"
            ),
            "relation": check(
                measurement.get("relation"),
                "=",
                unknown="measurement_relation_not_stored",
            ),
            "concentration": check(
                concentration, True, unknown="normalized_concentration_not_stored"
            ),
        }
        rows.append(
            {
                **binding(card, relationship, pin),
                "molecule_ref": relationship["object_ref"],
                "qualifiers": qualifiers,
                "checks": checks,
                "status": decision(checks),
                "experimental_comparability": "requires_human_review",
            }
        )
        if report_format == FORMAT:
            rows[-1]["context_review"] = stored_context_review(qualifiers)
    return {
        "rule": deepcopy(ASSAY_CRITERIA),
        "card_ref": pin,
        "rows": rows,
    }


def literature_review(card, role):
    pin = card.pinned_ref()
    rows = []
    for relationship in card.relationships("mentioned_in"):
        if relationship.get("qualifiers", {}).get("locations"):
            rows.append(
                {
                    **binding(card, relationship, pin),
                    "publication_ref": relationship["object_ref"],
                    "qualifiers": relationship["qualifiers"],
                    "interpretation": "located_accession_mention_only",
                }
            )
    return {
        "card_ref": pin,
        "requested_article": ARTICLES[role],
        "located_mentions": rows,
        "publications": card.literature(),
        "coverage": "located_mentions_returned"
        if rows
        else "no_located_match_in_requested_response",
        "curated_mechanistic_claims": "not_performed",
        "project_Evidence": "not_created",
        "scope": "annotations_and_database_citation_context_not_full_article_curation",
    }


def produce(output, fixtures, stage, *, legacy=False):
    require(stage in ("original", "later"), "Unknown stage")
    report_format = LEGACY_FORMAT if legacy else FORMAT
    if stage == "original":
        require(
            not output.exists() or not any(output.iterdir()), "Output must be empty"
        )
        output.mkdir(parents=True, exist_ok=True)
    else:
        require(not (output / "later.manifest.json").exists(), "Later stage exists")
        _, original, _ = read_stage(output, "original")
        report_format = original["format"]
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    timestamp = f"{stage} fixture read"
    resolver = EntityResolver(
        FixtureUniProtClient(fixtures, retrieved_at=timestamp),
        rcsb_client=FixtureRCSBClient(fixtures, retrieved_at=timestamp),
    )
    report = {
        "format": report_format,
        "stage": stage,
        "question": "Which stored structures and assay records meet the declared review criteria, and what located literature support is available?",
        "producer": {
            "sabueso": sabueso.__version__,
            "ackredit": ackredit.__version__,
            "example_source_sha256": digest(Path(__file__)),
        },
        "criteria_scope": "illustrative_public_review_not_project_selection_or_selectivity",
        "proteins": {},
    }
    with offline(), ackredit.session("public scientific dossier"):
        with sabueso.attribution() as observed, ackredit.capture(stage) as workflow:
            for role, accession in ROLES.items():
                card, resolution = sabueso.resolve(
                    accession,
                    resolver=resolver,
                    structures=STRUCTURES[role],
                    chembl={"limit": 25},
                    chembl_client=FixtureChEMBLClient(fixtures, retrieved_at=timestamp),
                    bindingdb={"limit": 25},
                    bindingdb_client=FixtureBindingDBClient(
                        fixtures, retrieved_at=timestamp
                    ),
                    europepmc={"article_ids": ARTICLES[role]},
                    europepmc_client=FixtureEuropePMCClient(
                        fixtures, retrieved_at=timestamp
                    ),
                    unichem_client=FixtureUniChemClient(
                        fixtures, retrieved_at=timestamp
                    ),
                )
                require(
                    card is not None and resolution.status == "resolved",
                    "Protein unresolved",
                )
                pin = store.save(card)
                report["proteins"][role] = {
                    "card_ref": pin,
                    "source_scope": {
                        "structures": STRUCTURES[role],
                        "article": ARTICLES[role],
                        "activity_limit_per_source": 25,
                    },
                    "resolution": resolution.to_dict(),
                    "structures": structure_review(card),
                    "assays": assay_review(card, report_format=report_format),
                    "literature": literature_review(card, role),
                    "knowledge_state": card.knowledge_state(),
                    "conflicts": card.quality.get("conflicts", []),
                    "alternatives": card.quality.get("alternatives", {}),
                    "terms": card.terms("redistribution"),
                }
                require(card.pinned_ref() == pin, "Inspection changed its input")
        runtime = {
            "producer": report["producer"],
            "acquisitions": observed.acquisitions,
            "workflow": workflow.attribution.to_dict(),
            "dossier_derivation_observation": "not_observed",
            "rules_and_support_are_separate_from_execution_observation": True,
        }
    write_json(output / f"{stage}.dossier.json", report)
    write_json(output / f"{stage}.runtime.json", runtime)
    (output / f"{stage}.dossier.md").write_text(
        render(read_json(output / f"{stage}.dossier.json")), encoding="utf-8"
    )
    files = [f"{stage}.dossier.json", f"{stage}.runtime.json", f"{stage}.dossier.md"]
    manifest = {
        "format": report_format,
        "stage": stage,
        "cards": {
            role: value["card_ref"] for role, value in report["proteins"].items()
        },
        "files": {name: digest(output / name) for name in files},
        "scope": "declared_public_fixture_subsets_not_online_or_installed_artifact_qualification",
    }
    if stage == "later":
        manifest["original_manifest_sha256"] = digest(output / "original.manifest.json")
    write_json(output / f"{stage}.manifest.json", manifest)


def cell(value):
    if value is None:
        return "unknown"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_assay_context(rows):
    lines = [
        "### Stored assay and document context",
        "",
        "Rule `stored_assay_context_review@1` describes only the original saved qualifiers. A missing field does not mean the source has no such information. Matching assay identifiers, descriptions or units do not establish equivalent protocols; no cross-record assay identity is inferred. A missing variant annotation does not establish a wild-type target.",
        "",
        "| Source record / native target identifier | Assay identifier / type | Biological context | Original document pointers | Original measurement notes | Fields not in saved qualifiers | Support |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        q = row["qualifiers"]
        assay, document, measurement = (
            q.get(name) or {} for name in ("assay", "document", "measurement")
        )
        notes = (
            "; ".join(
                f"{name}={cell(measurement[name])}"
                for name in (
                    "stated_value",
                    "upper_value",
                    "units",
                    "text_value",
                    "activity_comment",
                    "data_validity_comment",
                    "potential_duplicate",
                    "action_type",
                )
                if measurement.get(name) is not None
            )
            or "no notes in saved measurement"
        )
        biological = "; ".join(
            f"{name}={cell(assay.get(name))}"
            for name in (
                "organism",
                "tax_id",
                "confidence_score",
                "relationship_type",
                "variant_mutation",
            )
        )
        pointers = "; ".join(
            f"{name}={cell(document.get(name))}" for name in ("id", "pubmed", "doi")
        )
        missing = (
            ", ".join(
                path
                for path, state in row["context_review"]["fields"].items()
                if state == "not_in_saved_qualifiers"
            )
            or "none of the declared fields"
        )
        values = [
            f"{cell(q.get('activity_id'))} / {cell(q.get('target'))}",
            f"{cell(assay.get('id'))} / {cell(assay.get('type'))}",
            biological,
            pointers,
            notes,
            missing,
            row["relationship_ref"],
        ]
        lines.append("| " + " | ".join(map(cell, values)) + " |")
    lines += [
        "",
        "Protocol interpretation remains not curated and experimental comparability remains not established. Original source assertions and full qualifiers, including descriptions and normalized bounds, remain in the JSON/store.",
        "",
    ]
    return lines


def render(report):
    lines = [
        "# Public scientific review dossier",
        "",
        report["question"],
        "",
        "Criteria describe this recorded public review. Project model selection, assay comparability, selectivity and Evidence remain separate human work.",
        "",
    ]
    for role, protein in report["proteins"].items():
        criteria = protein["structures"]["rule"]
        maximum = criteria["maximum_resolution"]
        lines += [
            f"## {role}: {ROLES[role]}",
            "",
            f"Original input: `{protein['card_ref']}`",
            "",
            "### Structures",
            "",
            f"Declared rule `{criteria['rule']}`: resolution at most {maximum['value']} {maximum['unit']}, coverage at least {criteria['minimum_coverage']}, reference sequence, author-defined `{criteria['oligomer']}`, and coordinates covering the source-active-site positions in at least one chain.",
            "",
            "| Structure | Status | Resolution | Coverage | Sequence | Assembly / basis | Assembly disagreement | Unmet or unknown criteria | Support |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in protein["structures"]["rows"]:
            item = row["item"]
            resolution = item["resolution"]
            resolution = (
                "unknown"
                if resolution is None
                else f"{resolution['value']} {resolution['unit']}"
            )
            reasons = (
                ", ".join(
                    f"{k}: {v['status']}"
                    for k, v in row["checks"].items()
                    if v["status"] != "met"
                )
                or "all declared criteria met"
            )
            lines.append(
                "| "
                + " | ".join(
                    map(
                        cell,
                        [
                            item["structure_ref"],
                            row["status"],
                            resolution,
                            item["coverage"],
                            item["state"]["sequence"],
                            f"{item['state']['oligomer']} / {item['oligomer_basis']}",
                            item["oligomer_disagreement"],
                            reasons,
                            row["relationship_ref"],
                        ],
                    )
                )
                + " |"
            )
        lines += [
            "",
            "Canonical positions are local to each input. No cross-protein correspondence or geometric alignment is supplied. Author numbering, assembly disagreements, qualifier conflicts and exact source assertions remain in the JSON/store.",
            "",
            "Requested experimental entries: "
            + ", ".join(protein["source_scope"]["structures"])
            + ". A requested entry absent from the rows is not a proof of external absence; inspect its original source outcome.",
            "",
            "### Assay records",
            "",
            "Declared record rule: direct target assignment D, IC50, equality qualifier and a normalized concentration. It does not establish a common assay, identical experimental conditions or selectivity.",
            "",
            "| Molecule | Status | Stated measurement | Normalized quantity | Target assignment | Assay context | Support |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in protein["assays"]["rows"]:
            q = row["qualifiers"]
            m, assay = q.get("measurement") or {}, q.get("assay") or {}
            value = m.get("normalized")
            value = "unknown" if value is None else f"{value['value']} {value['unit']}"
            lines.append(
                "| "
                + " | ".join(
                    map(
                        cell,
                        [
                            row["molecule_ref"],
                            row["status"],
                            f"{cell(m.get('type'))} {cell(m.get('relation'))} {cell(m.get('value'))} {cell(m.get('units'))}",
                            value,
                            assay.get("relationship_type"),
                            assay.get("description"),
                            row["relationship_ref"],
                        ],
                    )
                )
                + " |"
            )
        if report["format"] == FORMAT:
            lines += ["", *render_assay_context(protein["assays"]["rows"])]
        lines += [
            "",
            "Record eligibility does not establish experimental comparability. Review actual assay conditions, target variants, censored/ranged values and original document pointers before comparing potency.",
            "",
            "### Located literature",
            "",
            f"Requested annotation scope: `{protein['literature']['requested_article']}`; `{protein['literature']['coverage']}`.",
            "",
        ]
        for row in protein["literature"]["located_mentions"]:
            for location in row["qualifiers"]["locations"]:
                annotation = location["annotation"]
                lines += [
                    f"- `{row['publication_ref']}`: {cell(annotation.get('section'))}; `{cell(annotation.get('id'))}`; returned fragment: {cell(annotation.get('prefix', '') + annotation.get('exact', '') + annotation.get('postfix', ''))}. Support: `{row['relationship_ref']}`."
                ]
        lines += [
            "",
            "Located mentions are accession occurrences, not curated mechanistic findings. Empty returned annotation scope does not prove absence from an article. Publication/citation context and source support are retained in the JSON; full-text interpretation is not performed.",
            "",
        ]
    lines += [
        "## Coverage and reuse",
        "",
        "Activities are explicitly capped at 25 per requested source. Inspect the saved knowledge-state rows, conflicts, alternatives, original acquisition outcomes and terms before interpreting completeness. Unasked, failed and unavailable scopes remain distinct.",
        "",
        "The JSON/store preserve exact pins and source support; the runtime preserves original credit. Later independent reading formats these saved results without acquisition, scientific re-derivation or fresh credit. File hashes detect inconsistent artifacts and do not authenticate a source or grant reuse permission.",
        "",
    ]
    return "\n".join(lines)


def read_stage(output, stage):
    manifest = read_json(output / f"{stage}.manifest.json")
    require(
        manifest["format"] in (FORMAT, LEGACY_FORMAT) and manifest["stage"] == stage,
        "Unsupported dossier manifest",
    )
    expected = {f"{stage}.dossier.json", f"{stage}.dossier.md", f"{stage}.runtime.json"}
    require(set(manifest["files"]) == expected, "Incomplete dossier files")
    require(set(manifest["cards"]) == set(ROLES), "Expected both protein pins")
    for name, fingerprint in manifest["files"].items():
        require(
            Path(name).name == name and (output / name).is_file(),
            "Missing or nonlocal dossier file",
        )
        require(digest(output / name) == fingerprint, "Original dossier file differs")
    if stage == "later":
        require(
            digest(output / "original.manifest.json")
            == manifest["original_manifest_sha256"],
            "Original manifest differs",
        )
    report = read_json(output / f"{stage}.dossier.json")
    require(
        report["format"] == manifest["format"] and report["stage"] == stage,
        "Report stage differs",
    )
    require(
        report["criteria_scope"]
        == "illustrative_public_review_not_project_selection_or_selectivity",
        "Overstated review scope",
    )
    require(set(report["proteins"]) == set(ROLES), "Report protein roles differ")
    require((output / "knowledge.db").is_file(), "Missing original knowledge store")
    store = sabueso.KnowledgeStore(output / "knowledge.db")
    for role, protein in report["proteins"].items():
        pin = manifest["cards"][role]
        require(protein["card_ref"] == pin, "Report input pin differs")
        card = store.load(pin)
        require(
            card.pinned_ref() == pin and card.acquisition_trace is None,
            "Historical input differs",
        )
        require(
            card.get("identifiers.uniprot")["value"] == ROLES[role],
            "Wrong protein identity",
        )
        require(
            protein["structures"]["rule"] == STRUCTURE_CRITERIA,
            "Unsupported structure criteria",
        )
        require(
            protein["assays"]["rule"] == ASSAY_CRITERIA, "Unsupported assay criteria"
        )
        require(
            protein["structures"]["active_site_input"]
            == card.get("features_positional.active_site")
            and protein["structures"]["sequence_input"] == card.get("sequence.primary"),
            "Original region input differs",
        )
        require(
            protein["source_scope"]
            == {
                "structures": STRUCTURES[role],
                "article": ARTICLES[role],
                "activity_limit_per_source": 25,
            },
            "Declared source scope differs",
        )
        require(
            protein["structures"]["source_outcomes"]
            == [
                record
                for record in card.quality.get("enrichments", [])
                if record.get("source") == "RCSB PDB"
            ],
            "Original structure source outcome differs",
        )
        for area, predicate in (
            ("structures", "has_structure"),
            ("assays", "has_bioactivity"),
        ):
            require(protein[area]["card_ref"] == pin, "Review input differs")
            rows = protein[area]["rows"]
            expected_refs = {
                pin + "#" + rel["id"] for rel in card.relationships(predicate)
            }
            require(
                {row["relationship_ref"] for row in rows} == expected_refs
                and len(rows) == len(expected_refs),
                "Review membership differs",
            )
            for row in rows:
                require(
                    all(
                        node["status"] in {"met", "not_met", "unknown"}
                        for node in row["checks"].values()
                    )
                    and row["status"] == decision(row["checks"]),
                    "Recorded criterion decision differs",
                )
                relationship = card.relationship_store.get(
                    row["relationship_ref"].rsplit("#", 1)[1]
                )
                original_binding = binding(card, relationship, pin)
                require(
                    original_binding == {key: row[key] for key in original_binding},
                    "Review support differs",
                )
                for reference in row["source_assertion_refs"]:
                    require(
                        reference.startswith(pin + "#")
                        and card.source_assertion_store.get(reference.rsplit("#", 1)[1])
                        is not None,
                        "Historical statement absent from exact input",
                    )
                if area == "assays":
                    require(
                        row["qualifiers"] == relationship["qualifiers"]
                        and row["molecule_ref"] == relationship["object_ref"],
                        "Assay values/context differ",
                    )
                    require(
                        row["experimental_comparability"] == "requires_human_review",
                        "Overstated assay comparability",
                    )
                    if report["format"] == FORMAT:
                        require(
                            row["context_review"]
                            == stored_context_review(relationship["qualifiers"]),
                            "Stored assay context review differs",
                        )
                    else:
                        require(
                            "context_review" not in row,
                            "Unexpected context review in historical format",
                        )
                else:
                    item, q = row["item"], relationship.get("qualifiers") or {}
                    require(
                        item["structure_ref"] == relationship["object_ref"]
                        and item["relationship_id"] == relationship["id"],
                        "Structure identity differs",
                    )
                    for field in (
                        "coverage",
                        "author_numbering",
                        "ranges",
                        "observed",
                        "chains",
                        "qualifier_conflicts",
                    ):
                        require(
                            item.get(field)
                            == (
                                relationship.get(field)
                                if field == "qualifier_conflicts"
                                else q.get(field)
                            ),
                            f"Structure {field} differs",
                        )
                    node = item["resolution"]
                    require(node == q.get("resolution"), "Structure quantity differs")
                    require(
                        row["project_model_selection"] == "not_performed",
                        "Overstated model selection",
                    )
        literature = protein["literature"]
        require(
            all(
                not publication.get("curated")
                for publication in literature["publications"]["publications"]
            ),
            "Unsupported curated publication claim",
        )
        require(
            literature["card_ref"] == pin
            and literature["requested_article"] == ARTICLES[role],
            "Literature scope differs",
        )
        require(
            literature["curated_mechanistic_claims"] == "not_performed"
            and literature["project_Evidence"] == "not_created",
            "Overstated article interpretation",
        )
        expected_mentions = [
            rel
            for rel in card.relationships("mentioned_in")
            if rel.get("qualifiers", {}).get("locations")
        ]
        require(
            len(literature["located_mentions"]) == len(expected_mentions),
            "Located mention membership differs",
        )
        for row in literature["located_mentions"]:
            require(
                row["relationship_ref"].startswith(pin + "#"),
                "Article belongs to another card",
            )
            rel = card.relationship_store.get(row["relationship_ref"].rsplit("#", 1)[1])
            require(
                rel in expected_mentions
                and row["qualifiers"] == rel["qualifiers"]
                and row["publication_ref"] == rel["object_ref"],
                "Located article statement differs",
            )
            require(
                row["interpretation"] == "located_accession_mention_only",
                "Overstated mention interpretation",
            )
            original_binding = binding(card, rel, pin)
            require(
                original_binding == {key: row[key] for key in original_binding},
                "Article support differs",
            )
    require(
        (output / f"{stage}.dossier.md").read_text(encoding="utf-8") == render(report),
        "Human dossier differs from saved report",
    )
    runtime = read_json(output / f"{stage}.runtime.json")
    require(runtime["producer"] == report["producer"], "Original producer differs")
    require(
        runtime["dossier_derivation_observation"] == "not_observed",
        "Overstated execution observation",
    )
    workflow = ackredit.Attribution.from_dict(runtime["workflow"])
    for key in ("items", "uses"):
        expected_credit = {
            json.dumps(value, sort_keys=True)
            for record in runtime["acquisitions"]
            for value in (record["provider"].get("attribution") or {}).get(key, [])
        }
        require(
            expected_credit
            == {json.dumps(value, sort_keys=True) for value in workflow.to_dict()[key]},
            "Workflow credit differs from original source operations",
        )
    return manifest, report, workflow


def read(output):
    with offline(), ackredit.session("independent scientific dossier reader"):
        before = ackredit.get_attribution().to_dict()
        with sabueso.attribution() as observed:
            for stage in ("original", "later"):
                if stage == "later" and not (output / "later.manifest.json").exists():
                    continue
                manifest, report, workflow = read_stage(output, stage)
                for format, suffix in (("csl-json", "csl.json"), ("bibtex", "bib")):
                    (output / f"{stage}.references.{suffix}").write_text(
                        workflow.report(format=format), encoding="utf-8"
                    )
                write_json(
                    output / f"{stage}.reader.json",
                    {
                        "original_report": report,
                        "cards": manifest["cards"],
                        "new_acquisitions": 0,
                        "new_derivations": 0,
                        "new_credit": 0,
                    },
                )
        require(
            not observed.acquisitions
            and not observed.records
            and not observed.operations
            and not observed.literature,
            "Reader observed new science",
        )
        require(ackredit.get_attribution().to_dict() == before, "Reader added credit")
    print(
        "Original scientific dossier and support verified; human review remains separate."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("produce", "read", "reacquire"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, default=Path("temp_data"))
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Produce historical @1; reacquisition keeps the original format",
    )
    args = parser.parse_args()
    require(
        not args.legacy or args.action == "produce",
        "Legacy option is only for original production",
    )
    output = args.output.resolve()
    if args.action == "read":
        read(output)
    else:
        produce(
            output,
            args.fixtures.resolve(),
            "original" if args.action == "produce" else "later",
            legacy=args.legacy,
        )


if __name__ == "__main__":
    main()
