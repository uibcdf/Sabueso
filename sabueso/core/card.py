"""Card core implementation (minimal)."""

from __future__ import annotations

from typing import Any, Dict, List

from sabueso._private.argdigest import arg_digest

from .quantities import field_node, quantity_columns, seal, to_quantity, verify
from .relationship_store import Relationship, RelationshipStore
from .source_assertion_store import SourceAssertionStore

CARD_SCHEMA_VERSION = "0.3.14"


def make_card_id(entity_type: str, subject_ref: str) -> str:
    """Stable, location-independent card reference, e.g. ``sabueso:protein:uniprot:P52789``.

    The syntax is provisional: MOLI Architecture 1.0 freezes stable referencability,
    not the identifier format.
    """
    return f"sabueso:{entity_type or 'entity'}:{subject_ref}"


class Card:
    """Resolved knowledge about a single entity, linked to its SourceAssertions."""

    def __init__(
        self,
        meta: Dict[str, Any] | None = None,
        sections: Dict[str, Any] | None = None,
        source_assertion_store: SourceAssertionStore
        | List[Dict[str, Any]]
        | None = None,
        selection_rules: Dict[str, Any] | None = None,
        quality: Dict[str, Any] | None = None,
        relationship_store: RelationshipStore | List[Dict[str, Any]] | None = None,
        entities: Dict[str, Any] | None = None,
    ) -> None:
        self.meta = meta or {}
        # A card always states its schema; a stored card keeps the one it was written with.
        self.meta.setdefault("schema_version", CARD_SCHEMA_VERSION)
        self.sections = sections or {}
        # Top-level keys of a newer schema this version does not know: kept, never
        # dropped, so saving the card again does not lose them (#42).
        self.unknown_stored: Dict[str, Any] = {}
        # Resolved identities (anchor -> records), the stored part of the glossary of
        # entities; the rest of the glossary is derived from relationships (#52).
        self.entity_identities: Dict[str, Dict[str, Any]] = {
            key: {
                "entity_type": entry.get("entity_type"),
                "records": list(entry.get("records") or []),
                "resolved": entry["identity"],
            }
            for key, entry in (entities or {}).items()
            if entry.get("identity")
        }
        if not isinstance(source_assertion_store, SourceAssertionStore):
            source_assertion_store = SourceAssertionStore(source_assertion_store)
        self.source_assertion_store = source_assertion_store
        if not isinstance(relationship_store, RelationshipStore):
            relationship_store = RelationshipStore(relationship_store)
        self.relationship_store = relationship_store
        self.selection_rules = selection_rules or {}
        self.quality = quality or {}
        self._acquisition_trace = None
        self._literature_intake_traces = []

    @property
    def literature_intake_traces(self) -> List[Dict[str, Any]]:
        """Original intake/reuse events, detached from scientific serialization.

        Save separately, or retain original results in an ExtractionStore. Readers
        return an empty list; stored support alone cannot recreate execution credit.
        """
        from copy import deepcopy

        return deepcopy(self._literature_intake_traces)

    @arg_digest()
    def add_literature_extraction(
        self, extraction: Dict[str, Any], skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """Intake an original literal-rule result for this exact UniProt subject.

        Original assertions, occurrence offsets and tool/configuration are retained.
        The returned runtime event reuses original attribution without re-extraction.
        Migrate an older card explicitly first. This is never human curation.
        """
        from .literature_extraction import add_extraction

        return add_extraction(self, extraction)

    @property
    def acquisition_trace(self) -> Dict[str, Any] | None:
        """Original runtime source access, detached from the scientific card payload.

        Save it beside the card. Payload-only readers return None and perform no
        acquisition or attribution. Coverage is explicit in the trace.
        """
        from copy import deepcopy

        return deepcopy(self._acquisition_trace)

    @property
    def id(self) -> str | None:
        """Stable card reference (``meta.card_id``), independent of storage location."""
        return self.meta.get("card_id")

    def snapshot_id(self) -> str:
        """Content address of this exact card state, ``sha256:<hex>`` (#7).

        Any change to what the card stores changes it; see ``sabueso.core.snapshot``.
        """
        from .snapshot import snapshot_id

        return snapshot_id(self.to_dict())

    def pinned_ref(self) -> str:
        """``<card_id>@<snapshot_id>``: a reference to this exact state (provisional form,
        uibcdf/moli#3)."""
        from .errors import StorageError
        from .snapshot import pinned_ref

        if not self.id:
            raise StorageError("A card without meta.card_id cannot be referenced.")
        return pinned_ref(self.id, self.snapshot_id())

    def relationships(
        self, predicate: str | None = None, object_ref: str | None = None
    ) -> List[Relationship]:
        """Relationships carried by this card, optionally filtered."""
        return self.relationship_store.find(predicate=predicate, object_ref=object_ref)

    @arg_digest()
    def get_residue(
        self,
        position: int,
        *,
        sequence: str = "canonical",
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Read stored annotations at a 1-based canonical sequence position.

        Each item retains its actual SourceAssertions. No sequence alignment,
        structure projection, acquisition or prediction is performed.
        """
        from .residues import residue_view

        return residue_view(self, position)

    @arg_digest()
    def get_residues(
        self, *, sequence: str = "canonical", skip_digestion: bool = False
    ) -> List[Dict[str, Any]]:
        """Read every position of the stored canonical sequence."""
        from .residues import residues_view

        return residues_view(self)

    @arg_digest()
    def residue_knowledge(
        self,
        position: int,
        *,
        sequence_ref: str = "canonical",
        source_assertions: List[Dict[str, Any]] | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Read supported type references, positional tracks and source regions.

        ``residue_knowledge@1`` retains independent values, source sequence scope
        and exact input support. Supplied assertions are read without card intake,
        acquisition or prediction. Noncanonical sequences must be explicitly
        declared in the original assertion metadata; no alignment is performed.
        """
        from .residue_knowledge import residue_knowledge

        return residue_knowledge(self, position, sequence_ref, source_assertions)

    @arg_digest()
    def residue_composition(
        self,
        residues: List[int],
        *,
        sequence_ref: str = "canonical",
        source_assertions: List[Dict[str, Any]] | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Summarize an explicit set of positions on one identified sequence axis.

        ``residue_set_composition@1`` counts each position once and retains
        ambiguous types in the denominator. Original sequence support and input
        revisions remain explicit. Selection is caller-declared, not a cavity
        membership assertion; no geometry, alignment or source query is performed.
        """
        from .residue_composition import residue_composition

        return residue_composition(self, residues, sequence_ref, source_assertions)

    @arg_digest()
    def structures(
        self,
        include_fragments: bool = False,
        region: Any = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Protein-centric view of this card's experimental structures.

        ``region`` (UniProt positions and ``[begin, end]`` ranges) adds, per chain, the
        region's residues without coordinates.
        """
        from .structures import structures_view

        return structures_view(self, include_fragments=include_fragments, region=region)

    @arg_digest()
    def bioactivities(
        self,
        include_indirect: bool = False,
        thresholds: Dict[str, Any] | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Molecule-centric view of this card's measured bioactivities."""
        from .bioactivities import bioactivities_view

        return bioactivities_view(
            self, include_indirect=include_indirect, thresholds=thresholds
        )

    @arg_digest()
    def explain_measurement(
        self, measurement_ref: str, skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """Explain a stored ``REL_`` record's group or an ``MG_`` group at this card pin.

        ``measurement_group_explanation@1`` retains the grouping rule, actual joins,
        ambiguity and exact source support. It reads without acquisition or mutation.
        """
        from .bioactivity_explanation import explain_measurement

        return explain_measurement(self, measurement_ref)

    @arg_digest()
    def explain_bioactivity(
        self,
        molecule_ref: str,
        include_indirect: bool = False,
        thresholds: Dict[str, Any] | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Explain an exact molecule item from ``bioactivities()`` at this card pin.

        ``bioactivity_explanation@1`` retains units, thresholds, group voters and
        stored source support. Use the same options as the view being explained.
        This does not resolve another identifier or explain a ligand deck/site.
        """
        from .bioactivity_explanation import explain_bioactivity

        return explain_bioactivity(self, molecule_ref, include_indirect, thresholds)

    @arg_digest()
    def add_literature_assertion(
        self,
        field_path: str,
        value: Any,
        publication: str,
        curator: str,
        locator: str | None = None,
        quote: str | None = None,
        method: str | None = None,
        eco_code: str | None = None,
        curated_at: str | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Record what a publication states about one of this card's fields.

        ``publication`` is ``pubmed:<id>`` or ``doi:<doi>``; ``locator`` says where
        (figure, table, page) and ``quote`` is an optional short excerpt. The assertion
        is compared with what other sources state, never given priority, and never
        discarded; a difference is recorded in ``quality.conflicts`` and warned about.
        Returns the curation record (``outcome``: new, corroborates, differs,
        not_comparable or not_compared). See ``sabueso.core.curation``.
        """
        from sabueso._private.smonitor.outcomes import report_curated_disagreement

        from .curation import add_literature_assertion

        record = add_literature_assertion(
            self,
            field_path,
            value,
            publication,
            curator,
            locator=locator,
            quote=quote,
            method=method,
            eco_code=eco_code,
            curated_at=curated_at,
        )
        if record["outcome"] == "differs":
            report_curated_disagreement(self.id or "", field_path, publication)
        return record

    @arg_digest()
    def add_literature_relationship(
        self,
        predicate: str,
        object_ref: str,
        qualifiers: Dict[str, Any] | None,
        publication: str,
        curator: str,
        locator: str | None = None,
        quote: str | None = None,
        eco_code: str | None = None,
        curated_at: str | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Record a relationship a publication states, e.g. an interaction or the
        residues at an interface. It merges with the same relationship from other
        sources; qualifiers it states differently are kept as conflicts and warned
        about. See ``sabueso.core.curation``."""
        from sabueso._private.smonitor.outcomes import report_curated_disagreement

        from .curation import add_literature_relationship

        record = add_literature_relationship(
            self,
            predicate,
            object_ref,
            qualifiers,
            publication,
            curator,
            locator=locator,
            quote=quote,
            eco_code=eco_code,
            curated_at=curated_at,
        )
        if record["outcome"] == "differs":
            report_curated_disagreement(self.id or "", record["field"], publication)
        return record

    @arg_digest()
    def add_literature_bioactivity(
        self,
        molecule: Any,
        measurement_type: str,
        value: Any,
        publication: str,
        curator: str,
        target_assignment: str,
        relation: str = "=",
        assay_description: str | None = None,
        locator: str | None = None,
        quote: str | None = None,
        eco_code: str | None = None,
        curated_at: str | None = None,
        upper_value: Any = None,
        uncertainty: Dict[str, Any] | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Record a bioactivity a publication reports, e.g. an IC50 read in a table.

        ``molecule`` is a small-molecule card, an identifier Sabueso resolves
        (``chembl:``, ``pubchem:``, ``pdb.ligand:``, ``inchikey:``) or a recorded identity
        ``{"inchikey", "records"}``; the measurement keeps the InChIKey and every linked
        record. ``value`` has its unit (``"33 uM"``, ``"45 %"``, a quantity).
        ``target_assignment`` says whether it was measured on this protein ("direct") or
        an ortholog ("homology"). It is compared with ChEMBL's measurements of the same
        publication, never given priority. See ``sabueso.core.curation``.

        A range ("10-20 uM") is ``value="10 uM", upper_value="20 uM"``. A stated
        uncertainty is ``uncertainty={"kind": "sd", "value": "3 nM", "n": 3}`` (also
        ``"sem"`` or ``"unspecified"`` for a bare "±"), or ``{"kind": "ci", "lower": ...,
        "upper": ..., "level": 0.95}`` (#37).
        """
        from sabueso._private.smonitor.outcomes import report_curated_disagreement

        from .curation import add_literature_bioactivity

        record = add_literature_bioactivity(
            self,
            molecule,
            measurement_type,
            value,
            publication,
            curator,
            target_assignment,
            relation=relation,
            assay_description=assay_description,
            locator=locator,
            quote=quote,
            eco_code=eco_code,
            curated_at=curated_at,
            upper_value=upper_value,
            uncertainty=uncertainty,
        )
        if record["outcome"] == "differs":
            report_curated_disagreement(self.id or "", record["field"], publication)
        return record

    @arg_digest()
    def add_literature_claim(
        self,
        topic: str,
        text: str,
        publication: str,
        curator: str,
        about: List[str] | None = None,
        locator: str | None = None,
        quote: str | None = None,
        eco_code: str | None = None,
        curated_at: str | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Record a claim a publication makes that fits no structured field (#43).

        ``topic`` is one of ``curation.CLAIM_TOPICS``; ``about`` lists what the claim
        is about (``"chembl:CHEMBL123"``, ``"pdb:1SUX"``, ``"residues:14,96"``). A
        claim is kept with its provenance and listed by topic, but never compared:
        whether two texts agree needs a reader. Its outcome is ``not_compared``.
        """
        item = {"topic": topic, "text": text}
        if about:
            item["about"] = list(about)
        return self.add_literature_assertion(
            "literature.claims",
            item,
            publication,
            curator,
            locator=locator,
            quote=quote,
            eco_code=eco_code,
            curated_at=curated_at,
        )

    @arg_digest()
    def claims(
        self, topic: str | None = None, skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """Curated free-text claims, by topic, with their provenance (#43)."""
        node = self.get("literature.claims") or {}
        items = []
        for sa_id in node.get("source_assertion_ids") or []:
            sa = self.source_assertion_store.get(sa_id) or {}
            value = sa.get("asserted_value") or {}
            if topic is not None and value.get("topic") != topic:
                continue
            curation = (sa.get("source_metadata") or {}).get("curation") or {}
            items.append(
                {
                    "topic": value.get("topic"),
                    "text": value.get("text"),
                    "about": value.get("about") or [],
                    "publication": (sa.get("source") or {}).get("record_id"),
                    "locator": curation.get("locator"),
                    "quote": curation.get("quote"),
                    "curator": curation.get("curator"),
                    "curated_at": curation.get("curated_at"),
                    "source_assertion_id": sa_id,
                    "outcome": "not_compared",
                }
            )
        by_topic: Dict[str, int] = {}
        for item in items:
            by_topic[item["topic"]] = by_topic.get(item["topic"], 0) + 1
        return {"items": items, "topics": dict(sorted(by_topic.items()))}

    @arg_digest()
    def add_literature_engagement(
        self,
        molecule: Any,
        residues: Any,
        mechanism: str,
        publication: str,
        curator: str,
        covalent_residue: int | None = None,
        method: str | None = None,
        locator: str | None = None,
        quote: str | None = None,
        eco_code: str | None = None,
        curated_at: str | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Record the residues a publication says a compound acts on, and how (#61).

        ``residues`` are UniProt positions of this entry, or ``{"position", "residue"}``
        checked against its sequence. ``mechanism`` is one of ``curation.MECHANISMS``;
        a covalent engagement names its ``covalent_residue``. ``method`` says how the
        paper showed it (e.g. "mass spectrometry", "mutagenesis"). It is compared with
        the ligand sites observed in structures; see ``sabueso.core.curation``.
        """
        from .curation import add_literature_engagement

        return add_literature_engagement(
            self,
            molecule,
            residues,
            mechanism,
            publication,
            curator,
            covalent_residue=covalent_residue,
            method=method,
            locator=locator,
            quote=quote,
            eco_code=eco_code,
            curated_at=curated_at,
        )

    @arg_digest()
    def table(
        self, view: str, skip_digestion: bool = False, **options: Any
    ) -> List[Dict[str, Any]]:
        """A view as flat rows (#46): ``structures``, ``bioactivities``, ``ligands``,
        ``ligand_sites``, ``interfaces``, ``literature`` or ``entities``. ``options`` go
        to the view, e.g. ``card.table("bioactivities", include_indirect=True)`` or
        ``card.table("ligands", deck=deck)``. Quantities stay quantities;
        ``sabueso.to_dataframe`` makes a DataFrame."""
        from .tables import card_table

        return card_table(self, view, **options)

    def predicted_structures(self) -> Dict[str, Any]:
        """Predicted models (AlphaFold DB), apart from experimental structures (#57)."""
        from .structures import predicted_structures_view

        return predicted_structures_view(self)

    def knowledge_state(self) -> Dict[str, Any]:
        """Per area and source: known, conflicting, not stated, not queried or
        unavailable (#56). See ``sabueso.core.knowledge_state``."""
        from .knowledge_state import knowledge_state

        return knowledge_state(self)

    @arg_digest()
    def explain_knowledge_state(
        self,
        knowledge_area: str | None = None,
        knowledge_source: str | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """Explain stored state rows at this card's pin (``knowledge_state_explanation@1``).

        Optional selectors match exact area/source names. Preserve classification
        inputs, selected and alternative support, conflicts and query outcomes.
        Reports of absence or unqueried areas never become negative assertions.
        No acquisition, card mutation or new execution credit occurs.
        """
        from .knowledge_state_explanation import explain_knowledge_state

        return explain_knowledge_state(self, knowledge_area, knowledge_source)

    def entities(self) -> Dict[str, Any]:
        """The glossary of molecular entities this card mentions, each once (#52)."""
        from .entities import build_entities

        return build_entities(self)

    def entity(self, ref: str) -> Dict[str, Any] | None:
        """The glossary entry of the entity a record belongs to, with its key."""
        from .entities import resolve_ref

        key, entry = resolve_ref(self, ref)
        return None if entry is None else {"key": key, **entry}

    def register_identity(
        self,
        anchor: str,
        records: List[str],
        entity_type: str,
        resolved: Dict[str, Any],
    ) -> None:
        """Record that ``records`` name the entity anchored at ``anchor``."""
        known = self.entity_identities.setdefault(
            anchor, {"entity_type": entity_type, "records": [], "resolved": resolved}
        )
        known["records"] = sorted(set(known["records"]) | set(records))

    def literature(self) -> Dict[str, Any]:
        """The publications that support statements on this card, and what for."""
        from .literature import literature_view

        return literature_view(self)

    def clinical(self) -> Dict[str, Any]:
        """A molecule's indications (ChEMBL) and the trials they cite
        (ClinicalTrials.gov), as the sources state them (#81)."""
        from .clinical import clinical_view

        return clinical_view(self)

    @arg_digest()
    def explain(
        self, source_assertion_ids: Any, skip_digestion: bool = False
    ) -> List[Dict[str, Any]]:
        """Where each SourceAssertion comes from (#91): the source, its record, release
        and retrieval, what it asserts and about which subject, and how it entered
        (``acquisition``, #92; curation metadata, when curated). The end of every "why
        is this here?"."""
        from .source_assertion_store import acquisition_of

        # Built with a retrieval archive (#100): the answers each source gave this build.
        answers: Dict[str, List[str]] = {}
        for record in (self.quality.get("retrievals") or {}).get("records") or []:
            answers.setdefault(record.get("source"), []).append(record["ref"])
        out = []
        for sa_id in source_assertion_ids:
            sa = self.source_assertion_store.get(sa_id)
            if sa is None:
                out.append({"id": sa_id, "found": False})
                continue
            source = sa.get("source") or {}
            out.append(
                {
                    "id": sa_id,
                    "found": True,
                    "field_path": sa.get("field_path"),
                    "subject_ref": sa.get("subject_ref"),
                    "source": source.get("name"),
                    "record": source.get("record_id"),
                    "version": source.get("version"),
                    "retrieved_at": sa.get("retrieved_at"),
                    "asserted_value": sa.get("asserted_value"),
                    "acquisition": acquisition_of(sa),
                    **(
                        {
                            "retrievals": {
                                "basis": "source_in_build",
                                "refs": answers.get(source.get("name"), []),
                            }
                        }
                        if answers
                        else {}
                    ),
                    **(
                        {"source_metadata": sa["source_metadata"]}
                        if sa.get("source_metadata")
                        else {}
                    ),
                }
            )
        return out

    @arg_digest()
    def explain_literature(
        self, publication_ref: str, skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """Explain a publication's stored links, statement support and structure
        context (``literature_explanation@1``). Read a historical card from the store
        first to explain its pin. Missing links are ``not_on_card``, never absence
        in the article. This operation does not fetch or select knowledge."""
        from .literature_explanation import explain_literature

        return explain_literature(self, publication_ref)

    def acquisition(self) -> Dict[str, Any]:
        """How the card's statements entered (#92), counted by method and source:
        imported from a database, curated from a publication, or extracted from a text
        by a named tool or model. A database that states how it obtained its record
        (e.g. DISEASES's text-mining channel) is counted under ``origins`` too.
        Statements stored before acquisition was recorded are ``not_recorded``."""
        from .source_assertion_store import acquisition_of

        methods: Dict[str, Dict[str, int]] = {}
        origins: Dict[str, Dict[str, int]] = {}
        extractors: Dict[tuple, int] = {}
        for sa in self.source_assertion_store.to_list():
            record = acquisition_of(sa)
            source = (sa.get("source") or {}).get("name") or "unknown"
            by_source = methods.setdefault(record["method"], {})
            by_source[source] = by_source.get(source, 0) + 1
            if record.get("origin"):
                by_origin = origins.setdefault(record["origin"], {})
                by_origin[source] = by_origin.get(source, 0) + 1
            if record.get("tool"):
                key = (
                    record["method"],
                    record["tool"],
                    record.get("version"),
                    bool(record.get("validated_by")),
                )
                extractors[key] = extractors.get(key, 0) + 1
        return {
            "methods": {m: dict(sorted(s.items())) for m, s in sorted(methods.items())},
            "origins": {o: dict(sorted(s.items())) for o, s in sorted(origins.items())},
            "extractions": [
                {
                    "method": m,
                    "tool": t,
                    "version": v,
                    "validated": validated,
                    "count": n,
                }
                for (m, t, v, validated), n in sorted(extractors.items())
            ],
        }

    @arg_digest()
    def terms(self, use: str, skip_digestion: bool = False) -> Dict[str, Any]:
        """What the sources of this card's knowledge state about ``use``: verdicts,
        obligations, attribution, and what remains without restricted or unknown
        sources (``terms_propagation@1``, #29). Not legal advice."""
        from .terms import terms_report

        return terms_report([self], use)

    @arg_digest()
    def diseases(
        self, grouping_rule: str = "disease_grouping@3", skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """The diseases every source states for this protein, grouped by MONDO term
        through every stored identity path (``disease_grouping@3``), with explicit
        identifier coverage (``disease_identity_coverage@1``). Conflicting targets
        remain ungrouped. Explicit ``grouping_rule`` selectors ``@1`` and ``@2``
        retain the historical lookup and path rules, including their limitations.
        """
        from .diseases import diseases_view

        return diseases_view(self, grouping_rule)

    @arg_digest()
    def explain_disease(
        self,
        disease_ref: str,
        skip_digestion: bool = False,
        *,
        grouping_rule: str = "disease_grouping@3",
    ) -> Dict[str, Any]:
        """Explain a MONDO disease group through its pinned statements and stored
        identity/hierarchy support and exact request-record context
        (``disease_group_explanation@3``). Explicit grouping rules ``@1`` and
        ``@2`` retain their historical explanations. Reads the
        current card or a loaded historical pin, without acquisition or mutation.
        Ungrouped statements are whole-card context, never inferred absence.
        """
        from .disease_explanation import explain_disease

        return explain_disease(self, disease_ref, grouping_rule)

    def interface_mutations(self) -> Dict[str, Any]:
        """Mutations at the interfaces of this protein's complexes and their binding
        changes, as SKEMPI states them, each with ΔΔG under ``binding_ddg@1`` (#83)."""
        from .interface_mutations import interface_mutations_view

        return interface_mutations_view(self)

    @arg_digest()
    def variant_tissue_usage(
        self,
        threshold: float = 0.1,
        skip_digestion: bool = False,
        *,
        usage_rule: str = "pext_at_variant@2",
    ) -> Dict[str, Any]:
        """Each population variant with the share of its gene's expression, per GTEx
        tissue, that includes its position (gnomAD's pext), under ``pext_at_variant@2``
        (#102). Build the card with ``gnomad={}`` and ``exon_usage=True``; with
        ``gtex=True`` too, each tissue's ontology term (``tissue_terms``).
        Inside ``sabueso.attribution()``, the execution is retained separately in
        ``run.operations``; scientific output and plain readers stay unchanged."""
        from .scoped_tissue_usage import check_arguments, variant_view
        from .tissue_usage import variant_tissue_usage_view

        check_arguments(threshold, usage_rule, kind="variant")
        from .comparative_operations import run
        from .tissue_usage import REGIONS, TERMS, VARIANTS

        view = (
            variant_tissue_usage_view
            if usage_rule == "pext_at_variant@1"
            else variant_view
        )
        return run(
            "variant_tissue_usage",
            lambda: view(self, threshold),
            [("subject", self, [VARIANTS, REGIONS, TERMS])],
            {"threshold": threshold, "usage_rule": usage_rule},
        )

    def sequence_differences(self, other: "Card") -> Dict[str, Any]:
        """The positions where this card's sequence and ``other``'s differ, when both
        have the same length, under ``equal_length_positions@1`` (#103). Nothing is
        aligned, and no identity follows from it. An explicit attribution context
        retains this execution in ``run.operations`` without changing the output."""
        from .comparative_operations import run
        from .sequences import sequence_differences_view

        return run(
            "sequence_differences",
            lambda: sequence_differences_view(self, other),
            [
                ("subject", self, ["sequence.primary"]),
                ("comparator", other, ["sequence.primary"]),
            ],
        )

    @arg_digest()
    def isoform_tissue_usage(
        self,
        threshold: float = 0.1,
        skip_digestion: bool = False,
        *,
        usage_rule: str = "isoform_exon_usage@3",
    ) -> Dict[str, Any]:
        """Per UniProt isoform: UniProt's tissue-specificity statements restricted to
        it, and the tissues expressing its own coding bases (gnomAD's pext), under
        ``isoform_exon_usage@3`` (#138). An isoform without known exons says why, and
        own bases say whether every isoform's exons were known. Build the card with
        ``exon_usage=True``; with ``gtex=True`` too, each tissue's ontology term.
        An explicit attribution context retains this execution in ``run.operations``;
        stored tissue-specificity statements remain separate from selected fields."""
        from .scoped_tissue_usage import check_arguments, isoform_view
        from .tissue_usage import isoform_tissue_usage_view

        check_arguments(threshold, usage_rule, kind="isoform")
        from .comparative_operations import run
        from .tissue_usage import (
            EXONS,
            ISOFORMS,
            REGIONS,
            TERMS,
            TISSUE_TEXT,
            TRANSCRIPTS,
        )

        view = (
            isoform_tissue_usage_view
            if usage_rule == "isoform_exon_usage@2"
            else isoform_view
        )
        return run(
            "isoform_tissue_usage",
            lambda: view(self, threshold),
            [
                (
                    "subject",
                    self,
                    [ISOFORMS, EXONS, REGIONS, TRANSCRIPTS, TISSUE_TEXT, TERMS],
                )
            ],
            {"threshold": threshold, "usage_rule": usage_rule},
        )

    @arg_digest()
    def explain_sequence_differences(
        self, other: "Card", skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """Explain the existing sequence comparison at both exact card pins.

        Preserve selected sequences, alternatives and source support under
        ``sequence_differences_explanation@1``. Equal integer positions establish
        neither residue correspondence nor entity identity; no alignment occurs.
        """
        from .comparative_explanation import explain_sequence_differences

        return explain_sequence_differences(self, other)

    @arg_digest()
    def explain_variant_tissue_usage(
        self,
        threshold: float = 0.1,
        skip_digestion: bool = False,
        *,
        usage_rule: str = "pext_at_variant@2",
    ) -> Dict[str, Any]:
        """Explain genomic variant/pext joins at this pin, with original support.

        ``variant_tissue_usage_explanation@2`` records genomic scope, every
        intersecting input, conflicts and missing tissue values. Explicit historical
        ``usage_rule="pext_at_variant@1"`` retains explanation @1. The cutoff is in [0, 1]
        and says nothing about pathogenicity. No source access or credit occurs.
        """
        from .comparative_explanation import explain_variant_tissue_usage

        return explain_variant_tissue_usage(self, threshold, usage_rule)

    @arg_digest()
    def explain_isoform_tissue_usage(
        self,
        threshold: float = 0.1,
        skip_digestion: bool = False,
        *,
        usage_rule: str = "isoform_exon_usage@3",
    ) -> Dict[str, Any]:
        """Explain isoform CDS subtraction and pext inputs at this exact card pin.

        ``isoform_tissue_usage_explanation@2`` retains missing transcript/exon
        support and incomplete own-base coverage. Source labels are preserved
        separately from verified native release identity and runtime attribution.
        """
        from .comparative_explanation import explain_isoform_tissue_usage

        return explain_isoform_tissue_usage(self, threshold, usage_rule)

    @arg_digest()
    def oligomer(
        self,
        skip_digestion: bool = False,
        *,
        agreement_rule: str = "interface_site_agreement@2",
    ) -> Dict[str, Any]:
        """Source-stated assemblies/interfaces and a versioned position comparison.

        Default agreement ``@2`` requires the card's UniProt subject, confirmed
        numbering and located 1-based positions. Explicit ``@1`` reproduces the
        historical integer-only comparison at the same stored card pin.
        """
        from .oligomer import oligomer_view

        return oligomer_view(self, agreement_rule)

    @arg_digest()
    def explain_oligomer(
        self,
        skip_digestion: bool = False,
        *,
        agreement_rule: str = "interface_site_agreement@2",
    ) -> Dict[str, Any]:
        """Explain the complete oligomer view at this exact card pin.

        ``oligomer_explanation@2`` retains the actual partner and agreement rules,
        source assemblies, selected/competing support and missing inputs. Readers
        fetch nothing, change no stored knowledge and add no acquisition credit.
        """
        from .oligomer_explanation import explain_oligomer

        return explain_oligomer(self, agreement_rule)

    def ligand_sites(self) -> Dict[str, Any]:
        """Residues each ligand contacts, next to the protein's annotated sites."""
        from .ligand_sites import ligand_sites_view

        return ligand_sites_view(self)

    @arg_digest()
    def explain_ligand_site(
        self, ligand_site_ref: str, skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """Explain a native site relationship's class and contacts at this card pin.

        ``ligand_site_explanation@1`` retains selected annotations, their support
        and structure-instance context without acquisition, mutation or new credit.
        """
        from .ligand_explanation import explain_ligand_site

        return explain_ligand_site(self, ligand_site_ref)

    @arg_digest()
    def ligands(
        self,
        deck: Any,
        include_indirect: bool = False,
        thresholds: Dict[str, Any] | None = None,
        skip_digestion: bool = False,
        *,
        counting_rule: str = "ligand_measurement_count@2",
    ) -> Dict[str, Any]:
        """This protein crossed with a deck of SmallMoleculeCards (``ligand_deck``).

        ``bioactivity.measurements`` counts distinct included groups and ``records``
        counts source records. Explicit ``counting_rule="ligand_measurement_count@1"``
        reproduces the legacy measurement counter; the stored cards stay unchanged.
        """
        from .ligands import ligands_view

        return ligands_view(
            self, deck, include_indirect, thresholds, counting_rule=counting_rule
        )

    @arg_digest()
    def explain_ligand(
        self,
        molecule_ref: str,
        deck: Any,
        include_indirect: bool = False,
        thresholds: Dict[str, Any] | None = None,
        skip_digestion: bool = False,
        *,
        counting_rule: str = "ligand_measurement_count@2",
    ) -> Dict[str, Any]:
        """Explain this protein's crossing with an exact molecule card id in a deck.

        ``ligand_deck_explanation@2`` retains protein/molecule pins, source-stated
        identities, measured classes, structural/site support and deck membership.
        It records exact counted group/record ids and the selected counting rule.
        Duplicate members remain explicit; no identifier resolution or acquisition occurs.
        """
        from .ligand_explanation import explain_ligand

        return explain_ligand(
            self,
            molecule_ref,
            deck,
            include_indirect,
            thresholds,
            counting_rule=counting_rule,
        )

    @arg_digest()
    def compare_ligands(
        self,
        deck: Any,
        other: "Card",
        other_deck: Any,
        include_indirect: bool = False,
        thresholds: Dict[str, Any] | None = None,
        skip_digestion: bool = False,
        *,
        counting_rule: str = "ligand_measurement_count@2",
    ) -> Dict[str, Any]:
        """Molecules related to this protein and to ``other``, side by side."""
        from .ligands import compare_ligands

        return compare_ligands(
            self,
            deck,
            other,
            other_deck,
            include_indirect,
            thresholds,
            counting_rule=counting_rule,
        )

    @arg_digest()
    def compare_knowledge(
        self,
        other: "Card",
        residue_map: Dict[int, int] | None = None,
        skip_digestion: bool = False,
    ) -> Dict[str, Any]:
        """What this card and ``other`` both state, what only one states, and what they
        state differently (#59). Positional features are compared only through
        ``residue_map`` ({position here: position in other}, e.g. from a MolSysMT
        alignment). See ``sabueso.core.card_diff``."""
        from .card_diff import compare_knowledge

        return compare_knowledge(self, other, residue_map)

    def get(self, field_path: str) -> Any:
        cur = self.sections
        for key in field_path.split("."):
            if not isinstance(cur, dict) or key not in cur:
                return None
            cur = cur[key]
        return cur

    def set(self, field_path: str, value: Any, source_assertion_ids: List[str]) -> None:
        cur = self.sections
        parts = field_path.split(".")
        for key in parts[:-1]:
            if key not in cur or not isinstance(cur[key], dict):
                cur[key] = {}
            cur = cur[key]
        cur[parts[-1]] = field_node(field_path, value, source_assertion_ids)

    def quantity(self, field_path: str) -> Any:
        """The field's value as a PyUnitWizard quantity (session's default form).

        Raises SchemaError when the field holds no quantity.
        """
        return to_quantity(self.get(field_path))

    def quantity_columns(self, template: str) -> Dict[str, Any]:
        """Every quantity at ``template`` as array quantities, one per stored unit.

        ``template`` names a column as the seal does, without list indices, e.g.
        ``relationships.has_structure.resolution`` or
        ``relationships.has_bioactivity.measurement.normalized``. Values keep their stored
        order (relationships by id). Units are never mixed or converted: a column holding
        nanomolar and percent returns both, keyed by unit.
        """
        return quantity_columns(
            {
                "sections": self.sections,
                "relationship_store": self.relationship_store.to_list(),
            },
            template,
        )

    @arg_digest()
    def extract(
        self, field_paths: List[str], skip_digestion: bool = False
    ) -> Dict[str, Any]:
        """``{field_path: node}``; a single path is one field, not its characters."""
        return {fp: self.get(fp) for fp in field_paths}

    def list_fields(self) -> List[str]:
        out: List[str] = []

        def walk(prefix: str, obj: Any) -> None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    path = f"{prefix}.{k}" if prefix else k
                    out.append(path)
                    walk(path, v)

        walk("", self.sections)
        return out

    def to_dict(self) -> Dict[str, Any]:
        """The stored form: every quantity node sealed by ``quantities`` (#32).

        It is independent of the card: changing one never changes the other.
        """
        import copy

        data = {
            "meta": self.meta,
            "sections": self.sections,
            "source_assertion_store": self.source_assertion_store.to_list(),
            "relationship_store": self.relationship_store.to_list(),
            "selection_rules": self.selection_rules,
            "quality": self.quality,
            "entities": self.entities(),
            **self.unknown_stored,
        }
        data = copy.deepcopy(data)
        data["quantities"] = seal(data)
        return data

    def to_json(self, path: str) -> None:
        from sabueso.tools.card.storage import save_card_json

        save_card_json(self, path)

    @arg_digest()
    def to_notebook(
        self,
        path=".",
        *,
        title=None,
        mode="full",
        language="en",
        include_code=True,
        include_card_snapshot=False,
        skip_digestion=False,
    ):
        """Write an offline notebook report of this exact card snapshot."""
        from sabueso.tools.card.notebook import write_notebook

        return write_notebook(
            self,
            path,
            title=title,
            mode=mode,
            language=language,
            include_code=include_code,
            include_card_snapshot=include_card_snapshot,
        )

    def to_sqlite(
        self, path: str, table: str = "cards", id_field: str | None = None
    ) -> None:
        from sabueso.tools.card.storage import save_card_sqlite

        save_card_sqlite(self, path, table=table, id_field=id_field)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        """Rebuild a Card, including its SourceAssertionStore, from ``to_dict()`` output.

        The card's schema version is checked first (``sabueso.core.schema_version``): a
        card of another schema line is refused, and one of a newer version of this line is
        read with a warning. Then the quantities seal is verified; a card whose quantities
        were changed outside Sabueso is refused (StorageError).
        """
        import copy

        from .schema_version import check_card_schema

        # The card owns its content: later changes to ``data`` do not reach it.
        data = copy.deepcopy(dict(data))
        newer = check_card_schema(data.get("meta"), CARD_SCHEMA_VERSION)
        verify(data, data.pop("quantities", None))
        known = {
            "meta",
            "sections",
            "source_assertion_store",
            "relationship_store",
            "selection_rules",
            "quality",
            "entities",
        }
        card = cls(**{k: v for k, v in data.items() if k in known})
        card.unknown_stored = {k: v for k, v in data.items() if k not in known}
        if newer:
            from sabueso._private.smonitor.outcomes import report_newer_schema

            report_newer_schema(card.id or "", card.meta["schema_version"])
        return card

    @classmethod
    def from_json(cls, path: str) -> "Card":
        from sabueso.tools.card.storage import _read_card_json

        return cls.from_dict(_read_card_json(path))

    @classmethod
    def from_sqlite(
        cls, path: str, table: str = "cards", card_id: str | None = None
    ) -> "Card | None":
        from sabueso.tools.card.storage import _read_card_sqlite

        data = _read_card_sqlite(path, table=table, card_id=card_id)
        if data is None:
            return None
        return cls.from_dict(data)

    def to_deck(self) -> Any:
        from .deck import Deck

        return Deck([self])

    def compare(self, other: "Card", fields: List[str] | None = None) -> Dict[str, Any]:
        """``{field_path: {"self": node, "other": node}}``; ``fields`` as in ``extract``."""
        mine = self.extract([] if fields is None else fields)
        theirs = other.extract(list(mine))
        return {fp: {"self": mine[fp], "other": theirs[fp]} for fp in mine}

    @arg_digest()
    def expand(
        self,
        predicate: Any,
        limit: int = 50,
        options: Dict[str, Dict[str, Any]] | None = None,
        terms: str | None = None,
        skip_digestion: bool = False,
    ) -> Any:
        """Deck of the entities this card relates to by ``predicate``
        (``relationship_expansion@1``, #91); see ``sabueso.expand``."""
        from sabueso.tools.navigate import _expand

        return _expand([self], predicate, limit, options or {}, terms)
