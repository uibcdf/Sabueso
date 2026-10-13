# Sabueso — Card Schema Notes

Development comparative execution records (`sabueso.comparative_operation@1`,
#108) are application-owned sidecars in `AttributionRun.operations`. They add no
Card fields or schema changes; original scientific values/rules and frozen cards
remain unchanged. See [scope](pending_proposals/comparative_operations.md).

## Schema Location
- **Formal schemas, by version** (`schemas/card_schema_<version>.yaml`):
  - `0.3.14` is unpublished development (#138/#139). Optional gnomAD variant assertion
    `source_metadata.coordinate_scope` records `assembly`, `basis`,
    `native_assembly_echo` and `rule`. `gnomad_query_coordinates@1` records GRCh38
    as the current client query/mapping contract; the source does not echo an
    assembly and this is not independent native-release verification. Source values
    and biological card fields are unchanged. Migration records the missing context
    on existing gnomAD variant assertions; refresh acquires it. Empty/unrelated
    cards have no applicable coordinate-context gap. #139 also adds optional
    `quality.enrichments[].request_options` for supplied protein request flags and
    dictionaries, and `quality.migration[].request_restoration` with
    `enrichment_request_restoration@1`. The report distinguishes recorded arguments,
    historical parameters/defaults, overrides, unsupported selectors and dependent
    requests. Unrecorded parameters are never backfilled into old cards. These
    quality keys are explicit-only in `SCHEMA_CHANGES`, not automatic gaps.
    Published schemas stay frozen;
  - `0.3.13` is published/frozen in release 0.14.0 (#134), written by its clean
    installed preliminary Conda package. It adds native UniProt activity
    regulation, domain notes, similarity, source cautions and miscellaneous text;
    additional positional chain, lipidation, motif, region, sequence-conflict,
    topological-domain and transmembrane fields, plus active positional domains.
    Every feature keeps original bounds/modifiers, molecule scope, ECO support and
    sequence revision. Residue views leave uncertain, foreign or revision-mismatched
    intervals unplaced. These optional fields refresh through `SCHEMA_CHANGES`;
    similarity is never identity and source cautions are not quality conclusions;
  - `0.3.12` is published/frozen in release 0.13.0 (#121), generated from clean
    installed local Conda code. Explicit literal extraction
    intake (#92) adds `quality.literature_extractions` and occurrence locations with Unicode
    offsets, locator and input hash. Original rule acquisition/support is retained;
    detached runtime attribution stays in an `ExtractionStore` or sidecar. Explicit
    `article_metadata_binding@1` adds separate native bibliographic assertions and
    optional metadata assertion IDs/rule in the intake record, preserving declared
    licence literals without changing fragment rights;
  - `0.3.11` is the frozen schema of release 0.12.0: explicit Europe PMC article
    annotations add native article ids and per-occurrence locations to `mentioned_in`,
    and source-supported PDB mentions add derived `structure_mentioned_in` context,
    with their SourceAssertions and identity basis. Enrichment records preserve the
    article requests for refresh. These optional locations are not migration gaps;
  - `0.3.10` is the schema of release 0.10.0: `identifiers.ensembl_transcripts` (UniProt's
    Ensembl transcripts per isoform) and `annotations.tissue_terms` (GTEx's ontology
    term for each pext tissue), #102;
    release 0.11.0 continues to write this schema: its views, integrity corrections
    and direct annotation access do not add stored card fields;
  - `0.3.9` is the schema of release 0.9.0: `identifiers.uniref` and `clustered_with`
    (UniProt's UniRef clusters, never identity, #103), and `quality.retries` (#97);
  - `0.3.8` is the schema of release 0.8.0: it records the ordering rule of a capped
    source in its enrichment record (`record_order` for BindingDB, `row_order` for
    PubChem BioAssay, #98), gnomAD's consequence on the canonical transcript
    (`transcript_version`, `canonical_consequence`, #85), KLIFS's kinase
    classification, structures and pocket, and GPCRdb's receptor classification,
    segments, generic residue numbers and structures, SAbDab's antibody complexes,
    and OMA's orthologs (#83), and gnomAD's pext (#102);
  - `0.3.7` is the schema of release 0.7.0: it adds `annotations.interface_mutations`
    (SKEMPI 2.0, #83), disease cards (MONDO, #90), the MONDO and MedGen identity and
    hierarchy relationships on protein cards, `mentioned_in` (Europe PMC, #92),
    `quality.terms_profile` (#94), and `acquisition` on every SourceAssertion (#92);
  - `0.3.6` is the schema of release 0.6.0: it adds UniProt isoforms, alternative
    sequences, secondary structure (UniProt's, and per chain from RCSB) and
    `substitution.missing` (#80), the curated biological context (#60), pathogen
    phenotypes, disease associations, pathways, and clinical and population variants
    (#81–#83);
  - `0.3.5` is the schema of release 0.5.0: it adds `author_numbering` (#73);
  - `0.3.4` is the schema of release 0.4.0;
  - `0.3.3` is the schema of release 0.3.1;
  - `0.3.2` of release 0.3.0;
  - `0.3.1` of release 0.2.0;
  - `0.3.0` of releases 0.1.0 and 0.1.1;
  - `0.2.0` was never released.
  Published versions are fixed. Each has a frozen card and a recorded shape
  (`schemas/card_shape_<version>.json`).
- **The conceptual draft** (`schemas/card_schema.yaml`), kept as the design the formal
  schemas grew from. Some of its sections are still unbuilt, such as the clinical layer
  (`ROADMAP.md`).

## Nested Structure

Disease-deck support in development (#91) adds `meta.support` under the local
`sabueso.disease_deck_support@1` format. It embeds unchanged disease input and a
separate assertion-bearing card revision, using existing SourceAssertion fields
and existing `relationships.associated_with` / `relationships.investigated_for`
assertion paths. Native rows and full returned source records are assertion values;
membership/ranking rules live in deck metadata. No card field, predicate, migration
step or schema version is added; published 0.3.12 remains frozen. Deck metadata and
source-data values are not new card field paths. See `STORAGE_LAYOUT.md` for pins.

Cards are **nested** to preserve hierarchy and order. Each card type (protein, peptide, small molecule) inherits from a shared base.

## Field Path Contract (Approved)
Canonical field paths use **dot‑separated notation**.

Examples:
- `names.canonical_name`
- `properties.physchem.molecular_weight`
- `annotations.catalytic_activity`
- `features_positional.binding_site`
- `sequence.length`

Identifier paths are **direct**:
- `identifiers.uniprot`
- `identifiers.pdb`
- `identifiers.chembl`
- `identifiers.pubchem`
(No `secondary_ids` level.)

## SourceAssertion Mechanism (Critical)
**A SourceAssertion records what an external source asserts about an entity or property.**
All fields in all cards are resolved from SourceAssertions through the same protocol:

1) **Card fields store the resolved value only**
   - Each field has `value` and `source_assertion_ids`.
   - `source_assertion_ids` lists the assertions that support the resolved value.
   - This keeps the card readable and deterministic.

2) **All assertions from all sources live in `source_assertion_store`**
   - One SourceAssertion per value asserted by one source record (see the contract
     below). Alternative and contradictory assertions are kept.
   - The store is serialized with the card.

3) **Selection rules are explicit**
   - `selection_rules` is a map keyed by field path.
   - Rules never delete SourceAssertions.

4) **Conflicts are explicit**
   - `quality.conflicts` lists fields whose SourceAssertions disagree, with the
     competing values and their `source_assertion_ids`.

This mechanism is **homogeneous** across all fields and all card types. It is a core design decision.

### What a SourceAssertion is not
MOLI Platform Architecture 1.0 (`uibcdf/moli`) distinguishes `SourceAssertion ≠ Evidence ≠ Provenance`:
- **Evidence** belongs to Nextia: project-contextual scientific information that
  supports, contradicts or informs a Question or Hypothesis. Sabueso never produces it; a
  DiscoveryProject may cite SourceAssertions as the basis of its own Evidence.
- **Provenance** is cross-cutting: origin, lineage, transformations and production
  context of any object. A SourceAssertion *has* provenance (source, record, version,
  retrieval, mapping); it is not provenance itself.
- Qualifiers a source attaches to its own statements (UniProt ECO codes, cited PubMed
  IDs, ChEMBL assay descriptors) are stored in `source_metadata` under their source-native
  names; Sabueso defines no generic `evidence` field.

## SourceAssertion Contract (Approved)
Field names follow the conceptual contract of MOLI Platform Architecture 1.0
(`uibcdf/moli`, `schemas/sabueso_source_assertion_conceptual_schema.md`).
Every SourceAssertion stored in `source_assertion_store` must include:

**Required**
- `id: string` (deterministic, prefix `SA_`)
- `subject_ref: string | null` — stable reference to what the source record describes,
  `<namespace>:<record_id>` (e.g. `uniprot:P52789`, `pdb:2NZT`); `null` when the source
  record has no identifier
- `field_path: string` (canonical field path)
- `asserted_value: any` (the value as the source asserts it)
- `source: { type: string, name: string, record_id: string, version?: string }`
- `retrieved_at: date`

**Optional**
- `normalized_value: any` (only when Sabueso normalization changes the asserted value;
  the resolver then works on it)
- `source_metadata: dict` (source-native qualifiers such as UniProt ECO codes)
- `provenance_ref: string` (reference to a provenance record, e.g. mapping version)
- `timestamps: { published_at?: date, updated_at?: date }`
- `confidence: float` (only when reported by the source)

**Recorded since card schema 0.3.7** (#92)
- `acquisition: {method, tool?, version?, configuration?, origin?, validated_by?}`:
  how the statement entered, never how true it is. `method` is one of:
  - `database`: imported from a source's record. `origin` records what the source
    states about how it obtained the record, today only `text_mining` (DISEASES's
    text-mining channel, Europe PMC's accession mentions);
  - `curation`: a person read the publication and recorded it
    (`source_metadata.curation` says who, when and where);
  - `rule_extraction` or `model_extraction`: extracted from a text. It names its
    `tool` and `version`, and its `configuration` when there is one. `validated_by`
    (curator and date) records a person's confirmation. These are for extractions
    whose tool and version are known because Sabueso or its user ran them; a source
    that serves text-mined records is `database` with its `origin`. No extraction is
    run automatically during card building. Since 0.13.0,
    `extract_literature_mentions` runs a named literal rule and returns detached
    statements. Explicit `Card.add_literature_extraction` or
    `resolve(..., extractions=ExtractionStore(...))` preserves that original support;
    refresh does not rerun the rule. Broader extraction and article metadata/terms
    remain #92.
  An older SourceAssertion has none, and reads as `not_recorded`
  (`acquisition_of`), until its card is built again.

`source.type` is one of `database`, `literature`, `patent`, `curated`, `other`.

## Card Identity (Provisional)
MOLI Architecture 1.0 requires important scientific objects to be serializable and
referencable independently of process, file, database or service location. Every card
built by the aggregator therefore carries:
- `meta.card_id`: stable reference `sabueso:<entity_type>:<subject_ref>`, e.g.
  `sabueso:protein:uniprot:P52789`, taken from the subject of the primary identifier
  assertion (`identifiers.uniprot`, then `chembl`, `pubchem`, `pdb`) unless given
  explicitly;
- `meta.schema_version`: card schema version (`0.3.4`). Until a formal policy is agreed
  (#42), an additive optional field bumps the patch number, and a change to existing
  fields bumps the minor number.

The identifier syntax is provisional (MOLI freezes referencability, not the format).

## Glossary of entities (uibcdf/sabueso#52)

`entities` lists each molecular entity the card mentions once: proteins, small
molecules (ions, lipids and cofactors included), polymers without a UniProt entry, and
the card's own entity. Structures, publications and terms are not entities.

- **Key.** The anchor when known (`uniprot:<acc>`, `inchikey:<key>`), else the first
  record.
- **Entry.** `entity_type`, `anchor`, `records`, `names`, `stated_types`, `parent_ref`,
  `appears_in` and `identity` (`{by, at}` when the anchor was resolved).
- **Merging.** Records merge only where a source states they are one entity: a
  resolved identity, `same_as` links, or the ChEMBL and DrugBank ids PDBe-KB states for
  a ligand.
- **Derivation.** It is derived from the relationships and the resolved identities, and
  rebuilt deterministically whenever the card is stored. On loading, only the resolved
  identities are taken from it.
- **References.** Relationships keep citing the record their source gave; curated
  bioactivities cite `molecule_ref`. `Card.entity(ref)` finds any record's entity.

## Versioning policy (uibcdf/sabueso#42)

**What a version covers.** The card schema covers the stored form of a card:
- `meta`;
- sections and their fields;
- SourceAssertion keys and `source_metadata`;
- relationship predicates, their qualifiers and derivations;
- `quality` records.

Raw source content (`asserted_value`) and the quantities seal (PyUnitWizard's format) are
not part of it. Views are Python API, not schema.

**Numbering.**
- Before 1.0 (`0.y.z`):
  - `z` grows with an additive, optional field, qualifier, predicate or key, so older cards
    stay valid (0.3.0 → 0.3.1);
  - `y` grows with anything else: a change of meaning, shape or unit, a removal, or a
    required field (0.2.0 → 0.3.0).
- From 1.0: patch for clarifications without a shape change, minor for additive changes,
  major for incompatible ones.
- A version is **fixed once a release publishes it**. Until then, additive changes
  accumulate in the next version. The release notes state the card schema they write.

**Reading** (`sabueso.core.schema_version`, applied by every loader):

| The card states | The reader |
|---|---|
| this version, or an older one of the same `0.y` (same major from 1.0) | reads it as is, without upgrading it |
| a newer one of that line | reads it with `NewerCardSchemaWarning` (`SABUESO-W-SCHEMA-001`), keeping unknown keys and top-level entries for re-saving. A quantity at a path this version did not negotiate is still refused by the seal check. |
| another line | refuses it (`StorageError`) until an explicit migration exists (#51) |
| no version, or an invalid one | refuses it |

**Guards.**
- Frozen cards: `temp_data/frozen_cards/schema_<version>__<entity>.json` holds one card
  per published schema, written by that release's package installed in a clean
  environment. For a new schema, it is the candidate's package (a local conda build of
  the candidate commit with its release version), because the card must be committed
  before tagging. A source checkout is not enough: `sabueso.__version__` may then report
  the metadata of another installed copy. Every one of them must stay readable
  (`tests/core/test_card_schema_policy_offline.py`). **On each release that publishes a
  new schema, add its frozen card.**
- Recorded shape: `schemas/card_shape_<version>.json` records the key paths of the cards
  the code writes from the fixtures (`tools/card_shape.py`), and a test compares them.
  If the shape changes:
  - for an unpublished version, run `python tools/card_shape.py --write`;
  - for a published version (it has a frozen card), bump `CARD_SCHEMA_VERSION`, add
    `schemas/card_schema_<version>.yaml`, and record the new shape. `--write` refuses to
    rewrite a published shape.
Card versions and snapshots, which Nextia needs to pin historical knowledge, exist
since #7 and #27: content-addressed snapshots, pinned references and the
`KnowledgeStore` (`STORAGE_LAYOUT.md`). Cards of older schemas of the same line are
converted by `sabueso.migrate_card`, which records their gaps (#51). No migration
between lines exists yet.

## Relationship Contract (MVP)
Agreed in `devguide/archive/entity_resolver.md` (uibcdf/sabueso#6) and
implemented in `sabueso/core/relationship_store.py`.

A Relationship is first-class, traceable knowledge:
- **Fields:** `id`, `subject_ref`, `predicate`, `object_ref`, `qualifiers`, and, when
  present, `qualifier_conflicts`, `source_assertion_ids` and `derivation`.
- **Predicates (vocabulary):**
  - identity: `same_as`, `possibly_same_as`, `isoform_of`, `superseded_by`. For small
    molecules (#25), `same_as` links a source record (`chembl:<id>`,
    `pdb.ligand:<code>`, `pubchem:<cid>`, `drugbank:<id>`, `chebi:<id>`,
    `bindingdb:<id>`) to the anchor `inchikey:<standard InChIKey>`. It is supported by
    the ChEMBL, PDB CCD or UniChem statement of that key. Qualifiers: `name`, and
    `component_type` for PDB components;
  - structures: `has_structure`;
  - knowledge (added in #21, part 2a):
    - `annotated_with` (protein → GO term). Qualifiers: `aspect`, `term`, `go_code` (GO's
      own annotation code, e.g. IDA, IEA) and `assigned_by`;
    - `classified_in` (protein → family, domain, superfamily or site entry). Qualifiers:
      `classification`, `name` and `match_count`. Object namespaces are `interpro:`,
      `pfam:`, `cath:` (Gene3D), `supfam:`, `panther:`, `prosite:` and `cdd:`;
    - `interacts_with` (protein → protein; physical interactions, e.g. IntAct via
      UniProt). Qualifiers: `partner_gene`, `intact_ids`, `experiments`,
      `organism_differ` and `curated_by`;
    - `functionally_associated_with` (protein → `string:<taxon>.<id>`; STRING functional
      associations, not physical binding). Qualifiers: `partner_name`, `combined_score`,
      `channels` (neighborhood, fusion, cooccurrence, coexpression, experiments,
      databases, textmining), `string_id`, `species` and `required_score`. Supporting
      assertions record the STRING version in `source.version`;
  - bioactivities (added in #23):
    - `has_bioactivity` (protein → `chembl:<molecule>`). There is one relationship per
      measurement, identified by the `activity_id` qualifier. Qualifiers: `activity_id`,
      `target`, `molecule_name`, `parent_molecule`, `measurement` (type, relation, value,
      units, pchembl, comments, flags), `assay` (id, type, description, organism,
      confidence_score, relationship_type, variant_mutation) and `document`.
    - Support: the verbatim activity record (`relationships.has_bioactivity`) and the
      assay record (`relationships.has_bioactivity.assay`). The assay record is stated
      once per assay and shared by that assay's activities.
    - Activity classes are derived by `Card.bioactivities()` (`bioactivity_class@3`), and
      only there.
  - predicted structures (added in #57):
    - `has_predicted_structure` (protein → `alphafold:<entry id>`, e.g.
      `alphafold:AF-P52270-F1`), one relationship per model, from AlphaFold DB.
      Qualifiers: `model_version`, `tool`, `created`, `mean_plddt` (a 0–100 confidence
      score, not a quantity), `plddt_fractions`, `range` (UniProt positions) and
      `sequence_matches`, and `isoform` when the model is of an isoform of the entry
      (schema 0.3.3). Never counted as an experimental structure.
  - curated engagement (added in #61):
    - `engages` (protein → the molecule's record, anchored by `molecule_ref`
      `inchikey:<key>`), one relationship per curated statement (`statement_id`).
      Qualifiers: `residues` (`position`, `residue` from the entry's sequence),
      `mechanism` (`covalent`, `non_covalent`, `allosteric`, `interface_disruption`,
      `unspecified`), `covalent_residue`, `method`, `publication`, `curated`.
      Stated only by curators; compared with PDBe-KB `has_ligand_site` of the same
      molecule.
  - ligand sites (added in #28):
    - `has_ligand_site` (protein → `pdb.ligand:<code>`), one relationship per
      protein–ligand pair, from PDBe-KB. Qualifiers: `ligand_name`, `numbering`
      (`uniprot`), `residues` (`start`, `end`, `residue`, `observed_in` with structure,
      entity and chains), `structures`, and PDBe-KB's own descriptors `is_solvent`,
      `significance`, `num_atoms`, `scaffold_id`, `cofactor_id`, `reaction_id`,
      `chembl_id` and `drugbank_id`. PDBe-KB aggregates ligand copies, so its per-residue
      chains do not say whether one ligand contacts several chains; that reading comes
      from the per-instance contacts of `has_structure`.
    - Overlap with annotated sites (UniProt and InterPro family sites) is derived by
      `Card.ligand_sites()` (`annotated_site_overlap@2`), and only there. Each overlap names
      the annotation, its source and the matched positions.
  - literature (added in #41):
    - `described_in` (protein → `pubmed:<id>`, `doi:<doi>` or
      `uniprot.citation:<id>`), one relationship per publication a source cites. From
      UniProt references. Qualifiers: `citation_type`, `title`, `journal`, `year`,
      `first_author`, `n_authors`, `pubmed`, `doi`, `uniprot_citation`,
      `reference_number`, `scope` (what the source cites it for) and `comments` (e.g.
      strain). The SourceAssertion keeps the reference verbatim.
  - clinical layer of molecules (added in #81, schema 0.3.6):
    - `investigated_for` (molecule record `chembl:<id>` → disease term), one per ChEMBL
      drug indication. The object is `<namespace>:<CURIE>` of ChEMBL's term
      (`efo:EFO:0008559`, `mondo:MONDO:0001444`, `doid:DOID:10113`), or `mesh:<id>`
      when there is none. Two terms that share a MeSH heading stay two relationships.
      Qualifiers:
      - `max_phase` (4 is approval as ChEMBL states it; 1 to 3 are investigational);
      - `disease_term`, `mesh_id`, `mesh_heading`;
      - `trials` (the NCT ids ChEMBL cites);
      - `references` (`type`, `id`: ClinicalTrials, ATC, FDA, EMA, DailyMed…).

      The SourceAssertion keeps the indication record verbatim
      (`drug_indication:<id>`).
    - `tested_in` (molecule record → `nct:<id>`), one per trial an indication cites.
      - Support: the ChEMBL assertions that cite it (the link's basis,
        `basis: chembl_drug_indication`), and the ClinicalTrials.gov record (subject
        `nct:<id>`).
      - Qualifiers: `cited_for` (the disease terms), and what ClinicalTrials.gov states:
        `title`, `status`, `study_type`, `phases`, `enrollment`, `start`, `completion`,
        `last_update`, `conditions`, `interventions` (`type`, `name`, `other_names`, as
        written), `lead_sponsor` and `has_results`.
      - `registry: not_found` when ClinicalTrials.gov does not hold a cited id.

      A trial is never matched to a molecule by its intervention text.
    - `Card.clinical()` lists both, and the cited trials not fetched.
  - disease association (added in #82, schema 0.3.6):
    - `associated_with` (protein → disease term), one per disease, source, channel and
      Ensembl protein or gene (`source`, `channel`, `via_protein`, `via_gene` identify
      it). From Open Targets: `mondo:`/`efo:…` terms, with `score`, `datatype_scores`
      (`datatype`, `score`) and `rank` as stated, through the Ensembl gene UniProt cross-references
      (`via_gene`), only when Open Targets lists the entry among the gene's products
      (`gene_lists_protein`). From DISEASES: `doid:DOID:<id>`, one per disease,
      DISEASES channel and Ensembl protein. From Orphanet: `orphanet:ORPHA:<code>`,
      through the Swiss-Prot accession Orphanet states (basis
      `orphanet_swissprot_xref`), with `association_type`, `association_status`,
      `disorder_type`, `disorder_group` and `validation` (publications). For DISEASES,
      the protein must be one the UniProt entry
      cross-references: `via_protein`, `uniprot_isoform`, basis
      `uniprot_ensembl_xref`. Qualifiers:
      - `channel` (`knowledge`, `experiments`, `textmining`) and `disease_name`;
      - DISEASES's scores as stated: `confidence`; `source_database` and
        `statement_type` (knowledge), `source_score` (experiments), `z_score` (text
        mining).

      Text mining links names, not molecules, and is added only when asked for.
  - clinical variants (added in #83, schema 0.3.6): `annotations.clinical_variants`, one
    item per ClinVar variation record of the gene, as ClinVar states it. `location` and
    `substitution` are in UniProt numbering only when the record's transcript is one
    UniProt states for the canonical isoform (RefSeq cross-references, versions
    included) and its residue matches the UniProt sequence. Otherwise `numbering` names
    ClinVar's transcript and `not_placed` gives the reason.
    - A change on the transcript of another isoform is placed through rule
      `uniprot_isoform_map@1` (`placed_via`: rule, isoform, isoform position). UniProt
      states the transcript's isoform, and the isoform's alternative-sequence edits
      give the map to canonical positions. A position inside an isoform's own segment
      has none (`isoform_specific_position`).
    - Other reasons: `no_protein_change`, `unparsed_protein_change`,
      `transcript_not_canonical`, `not_coding_on_canonical` and
      `no_consequence_on_canonical` (gnomAD), `stop_codon` and `residue_mismatch`.
  - population variants (added in #83, schema 0.3.6): `annotations.population_variants`,
    one item per gnomAD variant with a protein change, with the exome and genome
    `{ac, an, af}` as stated. Placed by the same rule as ClinVar, through an Ensembl
    transcript UniProt states for the canonical isoform. Since schema 0.3.8 (#85)
    gnomAD is also asked for each such transcript, and states each variant's
    consequence on it, with the transcript's version (`transcript_version`); that
    consequence is kept when it is a protein change. A variant gnomAD states changes no
    residue of the canonical transcript keeps its consequence on the other transcript,
    records `canonical_consequence` (`transcript`, `transcript_version`, `consequence`,
    `hgvs_c`) and is not placed (`not_coding_on_canonical`), even where UniProt's
    isoform map would place it. The residue check still applies. A change the isoform
    map would place is first asked of gnomAD variant by variant (#102): it is read on
    the canonical transcript when gnomAD states a protein change there, and otherwise
    not placed (`not_coding_on_canonical`, or `no_consequence_on_canonical` when gnomAD
    states no consequence on it). The enrichment record counts the variants asked
    (`consequences_checked`).
  - disease hierarchy (added in #90, schema 0.3.7): `subclass_of` (disease →
    `mondo:<id>`), one per parent term MONDO states.
  - sequence clusters (added in #103, schema 0.3.9): `identifiers.uniref`
    (`{uniref100, uniref90, uniref50}`), and `clustered_with` (protein →
    `uniprot:<accession>`, or `uniparc:<UPI>` for a sequence without an entry), one per
    other member of the entry's UniRef90 cluster. Qualifiers: `cluster`,
    `identity_level` (0.9), `member_id`, `organism`, `taxon_id`, `sequence_length`,
    `uniref100` and `same_uniref100` (an identical sequence or a fragment of the
    card's). UniProt's statement of similarity, never `same_as`: a reference entry and a
    genome-strain entry of one protein stay two entities. `Card.sequence_differences`
    lists the positions where two cards' sequences differ, for equal lengths only
    (`equal_length_positions@1`); nothing is aligned.
  - orthologs (added in #83, schema 0.3.8): `ortholog_of` (protein → `uniprot:<acc>`,
    or `oma:<OMA id>`), one per OMA protein (`oma_id` is an identity qualifier:
    identical proteins of several strains share a UniProt entry). Only when OMA states
    the card's accession with `seq_match` `exact`; an accession OMA maps to another
    protein (another strain) is `not_found`, naming it. Qualifiers: `rel_type` (1:1, 1:n,
    m:1, m:n), `species`, `taxon_id`, `oma_id`, `oma_group`, `oma_hog_id`,
    `canonical_id` (OMA's: a UniProt accession, a Swiss-Prot entry name UniProt resolves,
    or another database's id), `distance` and `score`, as stated. Options: `limit`,
    `rel_type`, `taxa`.
  - text mentions (added in #92, schema 0.3.7): `mentioned_in` (protein →
    `pubmed:<id>`, else `doi:<doi>`, else `europepmc:<source>:<id>`), one per article
    whose text states the UniProt accession, as Europe PMC found it by text mining.
    Qualifiers: `source` (`Europe PMC`), `mention` (`uniprot_accession`), `title`,
    `journal`, `year`, `open_access`, and `preprint`. Its SourceAssertions record
    `acquisition: {method: database, origin: text_mining}`. A mention says the paper
    names the entry, never what it states about it.
    Schema 0.3.11 (published in 0.12.0) adds optional `article` and `locations` qualifiers
    for explicit article annotations, and a distinct derived predicate:
    `structure_mentioned_in` (protein → publication, one per `structure_ref`).
    A printed legacy PDB code and matching PDBe tag identify the mentioned entry;
    supported source-stated `has_structure` links already on the card supply its
    association with the protein. Qualifiers keep `article`, `locations`,
    `structure_ref` and `structure_context` (`protein_ref`, `structure_ref`, structural
    `relationship_ids`, `source_assertion_ids`, `scope: entry_association`).
    Rule `structure_mention_context@1` records both legs as derivation inputs. Raw
    mention assertions have PDB subjects and `relationships.mentioned_in` paths;
    the derived link's direct support contains only these mention assertions. It
    creates no assertion for the derived protein link and infers no chain, residue,
    whole-entry identity, author focus or scientific claim. Expanded PDB codes and
    name annotations are unhandled. Duplicate occurrences preserve all rule inputs
    and qualifier alternatives. Terms judge attached fragments independently of
    the structural sources' terms.
  - pathways (added in #83, schema 0.3.6):
    - `participates_in` (protein → `reactome:<stId>`), one per Reactome event mapping
      the UniProt accession. Qualifiers: `kind` (`pathway`, lowest level, or
      `reaction`), `name`, `species`, `is_inferred` (inferred by Reactome from
      orthology), and for pathways `ancestors` (each path up to a top-level pathway,
      `id` and `name`).
  - interface mutations (added in #83, schema 0.3.7): `annotations.interface_mutations`,
    one item per SKEMPI 2.0 row whose PDB entry has a chain UniProt states is this
    protein (the entry's PDB cross-reference). Never joined by the protein names SKEMPI
    writes.
    - `structure`, `complex` (SKEMPI's `1BRS_A_D`), `sides` (the chains of each side),
      `protein_chains` (this protein's), `proteins` (as SKEMPI names them).
    - `mutations`: each `{chain, author_residue, original, change, location_class, on}`
      in the entry's author numbering, with `on` `this_protein` or `partner`. Placed in
      UniProt numbering (`location`, `placed_via`, rule `rcsb_author_numbering@1`) only
      through the author numbering RCSB states for that chain of a structure the card
      holds, and a matching residue. Otherwise `not_placed`: `partner_chain`,
      `structure_not_loaded`, `author_residue_not_mapped` or `residue_mismatch`.
    - `affinity` (`mutant`, `wild_type` in molar), `kinetics` (kon in 1/(M·s), koff in
      1/s), `thermodynamics` (ΔH in kcal/mol, ΔS in cal/(mol·K)) and `temperature`
      (kelvin), as stated. A bound keeps `<name>_relation`, "n.b." is
      `<name>_no_binding`, other text is `<name>_stated`, and SKEMPI's assumed 298 K is
      `temperature_assumed`.
    - `method`, `reference` (`pubmed:<id>`, or `reference_stated`), `notes`,
      `hold_out_type` and `skempi_version` (the SKEMPI version the row entered).
    - ΔΔG is not stored. `Card.interface_mutations()` derives it (`binding_ddg@1`).
    - Which statements each publication supports is read by `Card.literature()` from the
      ECO evidence of every SourceAssertion, and only there.
  - kinases (added in #83, schema 0.3.8), from KLIFS, for a kinase whose UniProt
    accession KLIFS states (two items for a protein with two kinase domains):
    - `annotations.kinase_classification`: KLIFS's kinase id and name, `group`,
      `family`, `subfamily`, and `pocket_sequence` (85 residues, `_` for a gap).
    - `annotations.kinase_structures`: per KLIFS structure (PDB entry, `chain`, `alt`),
      the conformation KLIFS assigns (`dfg`, `ac_helix`: `in`, `out`, `out-like`,
      `na`), the orthosteric and allosteric `ligand` (PDB chemical component ids),
      `quality_score`, `resolution` (angstrom), `missing_residues`, `missing_atoms`.
      Up to 5000 per kinase (`klifs={"limit": n}`); a cut is reported.
    - `annotations.kinase_pocket`: the 85 positions (`index`, `klifs_position` such as
      `GK.45`, `hinge.46`, `xDFG.81`, and `residue`). Placed in UniProt numbering
      (`location`, `placed_via`) through one structure's author numbering as RCSB
      states it: the structure is chosen by `klifs_pocket_reference@1`, and the rule
      is `rcsb_author_numbering@1`; the residue must be UniProt's. Otherwise
      `not_placed`: `gap`, `no_structure_loaded`, `missing_in_structure`,
      `author_residue_not_mapped` or `residue_mismatch`.
  - GPCRs (added in #83, schema 0.3.8), from GPCRdb, for a receptor whose UniProt
    accession GPCRdb states:
    - `annotations.gpcr_classification`: `entry_name`, `name`, `receptor_class`,
      `family`, `numbering_scheme`.
    - `annotations.gpcr_segments`: runs of consecutive residues per segment (N-term,
      TM1-7, ICL/ECL, H8, C-term), in GPCRdb's numbering (`gpcrdb_start`,
      `gpcrdb_end`) and in UniProt's (`location`).
    - `annotations.gpcr_residues`: the residues with a generic number, each with its
      `residue`, `segment`, `generic_number` (GPCRdb's display number) and
      `generic_numbers` (`[{scheme, label}]`, every scheme GPCRdb states).
    - Segments and residues are in UniProt numbering only when GPCRdb's sequence is the
      entry's (`gpcrdb_sequence_numbering@1`), and each residue must match; otherwise
      `not_placed` (`sequence_differs`, `residue_mismatch`).
    - `annotations.gpcr_structures`: per structure, `chain`, `state` (Active, Inactive,
      Intermediate), `method`, `resolution` (angstrom), `publication`,
      `publication_date`, `ligands` (`name`, `pdb_ccd`, `type`, `function`), `apo`
      (GPCRdb states no ligand), `signalling_protein` (`type`, `partners`: GPCRdb entry
      names). Up to 5000 (`gpcrdb={"limit": n}`); a cut is reported.
  - exon usage by tissue (added in #102, schema 0.3.8):
    `annotations.exon_usage_by_tissue`, gnomAD's pext of the gene, one item per coding
    region: `gene`, `assembly` (GRCh38), `chromosome`, `start`, `end`, `mean`, and
    `tissues` (`[{tissue, value}]`, the share of the gene's expression in each GTEx v10
    tissue that includes the region). `Card.variant_tissue_usage(threshold=0.1)` joins
    each population variant's genomic position to its region (published
    `pext_at_variant@1`; development `@2` confirms coordinate scope and reports
    conflicting or missing tissue values separately);
    a variant outside every region is `outside_pext_regions` (pext covers coding
    regions only). Nothing derived is stored.
  - isoform coding exons (added in #102, schema 0.3.8):
    `annotations.isoform_coding_exons`, per Ensembl transcript UniProt states an isoform
    for (its cross-reference) and gnomAD annotates: `isoform`, `transcript`,
    `transcript_version`, `assembly`, `chromosome`, `strand`, and `cds` (GRCh38 ranges,
    as gnomAD states them). `Card.isoform_tissue_usage()` (published
    `isoform_exon_usage@2`, development `@3` with explicit scope/coverage) gives
    per isoform UniProt's tissue-specificity statements restricted to it
    (`source_metadata.molecule`), its own coding bases (in no other isoform's
    transcript) and their mean pext per tissue, and the `variable_regions`: runs of
    coding bases not every isoform includes, with the isoforms that include them and
    their pext. An isoform without known exons says why: `no_transcript_stated`
    (UniProt states no Ensembl transcript for it), `transcript_not_in_gnomad`, or
    `transcripts_not_recorded` (a card older than 0.3.10). Own bases are counted
    against the isoforms whose exons are known; `own_bases_complete` and
    `variable_regions_complete` say whether every isoform's were (`@1` did not say).
  - Ensembl transcripts (added in #102, schema 0.3.10): `identifiers.ensembl_transcripts`,
    UniProt's Ensembl cross-references, each `{transcript, protein, gene, isoform}`
    (`isoform` when UniProt names the isoform the transcript encodes).
  - tissue terms (added in #102, schema 0.3.10): `annotations.tissue_terms`, from GTEx
    (`gtex=True`, with `exon_usage=True`), one item per GTEx tissue the card's pext
    names: `gtex_id`, `name`, `tissue_site`, `ontology_id` (UBERON, or EFO for a cell
    line) and `ontology_iri`, as GTEx states them for the release the pext states
    (gtex_v10). The views join them to the pext's tissues by `gtex_tissue_key@1`
    (GTEx's id in lower case, other characters as `_`) and list them as
    `tissue_terms`. A term never replaces a tissue: GTEx gives the cerebellum and the
    cerebellar hemisphere UBERON:0002037.
  - antibody complexes (added in #83, schema 0.3.8): `annotations.antibody_complexes`,
    one item per SAbDab antibody instance with an antigen that is a protein or peptide
    chain UniProt states is this protein in that PDB entry. Never joined by the antigen
    names SAbDab writes; a hapten, sugar or ion never makes a protein an antigen.
    - `structure`, `model`, `heavy_chain` and `light_chain` (`chain` as the PDB names
      it, `entity`, `type`: H, κ, λ, VNAR; `v_gene_subgroup`); a nanobody has no light
      chain, and an scFv names one chain for both.
    - `antigen_chains`: this protein's chains among the antigens.
    - `antigens`: every antigen SAbDab assigns (`name`, `type`, `entity`, `chain`,
      `this_protein`). An antigen is SAbDab's assignment in the structure, not a
      statement that the antibody recognises it: a Fab bound to an arrestin–receptor
      complex lists both.
  - curated literature assertions (added in #41):
    - A SourceAssertion with `source.type = "literature"`, `source.name = "Literature"`
      and the publication as `record_id` (`pubmed:<id>` or `doi:<doi>`). Its
      `source_metadata.curation` holds `curator`, `curated_at`, `locator` and an optional
      short `quote`. It may also hold `method`, `eco` and `stated_decimals`, the stated
      precision expressed in the field's unit. Its id hashes the value and the locator,
      so the same value at another place in the paper is another assertion.
    - Only knowledge fields take them (`sabueso.core.curation.CURATABLE_FIELDS`):
      `annotations.*`, `features_positional.*` (except family sites, alternative
      sequences and secondary structure) and
      `properties.physchem.*`. Identity, sequence and metadata never do.
    - `quality.curation` records each one: `field`, `publication`,
      `source_assertion_id`, `outcome` (`new`, `corroborates`, `differs`,
      `not_comparable`, `not_compared`) and `compared_with`. A `differs` on a list
      field also goes to `quality.conflicts` with `type: "curated_difference"`.
    - Relationships of `CURATABLE_PREDICATES` (`interacts_with`,
      `functionally_associated_with`, `annotated_with`, `classified_in`,
      `has_ligand_site`, `has_interface_with`) can be curated too. The SourceAssertion
      states `{object_ref, qualifiers}` under `relationships.<predicate>`. It merges with
      the same relationship from other sources. Qualifiers stated differently become
      `qualifier_conflicts` and a `curated_difference` with the `relationship_id`.
      `has_bioactivity` has its own curated form (#44). Each curated measurement is a
      `has_bioactivity` relationship with `activity_id = curated:<digest>`, carrying:
      - `molecule_ref`: the molecule's InChIKey anchor. Its linked records live in
        the card's glossary (`entities`, #52), not in the measurement;
      - the measurement, with `curated: true`, its value and unit as written and its
        normalized node;
      - the assay, with `curated: true` and the curator's target assignment (`D` or
        `H`);
      - the document, with the publication's PubMed id or DOI.

      It is compared with the ChEMBL measurements of the same publication, the same
      molecule (any of its records) and the same type.
    - ChEMBL `has_bioactivity` document qualifiers carry `pubmed`, `doi` and `title` as
      ChEMBL states them (#44).
  - interfaces (added in #40):
    - `has_interface_with` (protein → `uniprot:<acc>`, or `pdbe_kb.partner:<label>` for a
      partner without a UniProt entry), one relationship per partner, from PDBe-KB.
      PDBe-KB derives the residues from the structures (PISA). Qualifiers:
      `partner_name`, `partner_type` (PDBe-KB's `UNP`, `AB`...), `numbering`,
      `residues` (as for `has_ligand_site`), and `structures`, the entries where the
      interface is observed.
    - What kind of partner it is (homomeric, heteromeric, a chimera of the protein with
      itself, a peptide in a complex) is derived by `Card.oligomer()`
      (`interface_partner_class@1`), and only there. So is the agreement with family
      interface sites (`interface_site_agreement@1`).

  Any other predicate is rejected, and the vocabulary is extended deliberately. If
  components outside Sabueso (Nextia, MOLI Agent Context Assembly) come to depend on it,
  it becomes a shared contract to raise in `uibcdf/moli`.
- **Identity:** `id = REL_<hash>`, deterministic from subject, predicate, object and the
  predicate's identity qualifiers. `isoform_of` includes `isoform`, and
  `has_bioactivity` includes `activity_id`. `has_structure` is
  identified by the (protein, structure) pair alone: UniProt cross-references do not name
  polymer entities, so entity-level details are qualifiers. This lets UniProt and RCSB
  state the same relationship. The same relationship is therefore recognisable wherever
  it appears.
- **Support:** each relationship is supported by SourceAssertions (asserted by sources),
  by a `derivation` record (inferred by Sabueso: rule, inputs, parameters, Sabueso
  version), or by both. An unsupported relationship is rejected. A derived relationship
  never masquerades as a SourceAssertion.
- **Several sources:** when sources state the same relationship, their support is
  merged. Qualifier values they disagree on are kept in `qualifier_conflicts`, never
  overwritten.
- **SourceAssertions that support a relationship** use
  `field_path = relationships.<predicate>`.
  UniProt binding-site features keep their `ligand` (`name`, ChEBI `id`, and the `label`
  that tells two sites of the same ligand apart).
- **Family sites (#28):** `features_positional.family_site` holds the sites InterPro member
  databases place on the protein's own sequence (e.g. CDD `cd00311`: catalytic triad,
  substrate binding site, dimer interface). Each item has `location.sequence.fragments`,
  the verbatim `description` and its `signature`. They are family-level annotations,
  placed by the source's model, and stay apart from UniProt's `active_site` and
  `binding_site`. Their SourceAssertions have subject `uniprot:<accession>` (InterPro keys
  proteins by UniProt accession), the InterPro release in `source.version`, and the
  member database and signature in `source_metadata`.
- **Explicit SourceAssertion subjects:** a source that keys its records by another
  namespace passes `subject_ref` to `make_source_assertion` (InterPro, PDBe-KB:
  `uniprot:<accession>`). A shared context record uses a sub-path, such as
  `relationships.has_bioactivity.assay` for an assay. Their `asserted_value` is what the source
  states, i.e. the object and qualifiers as given by that source. Source property names
  are kept verbatim (e.g. UniProt's `GoEvidenceType`), while the relationship's
  qualifiers use Sabueso's vocabulary.
- **`has_structure` qualifiers:** `method`, `resolution` (`{value, unit}`, #32), `chains`, `ranges`
  (UniProt numbering, inclusive) and `coverage` (fraction of the canonical sequence).
  From RCSB:
  - `polymer_entities`;
  - `chimeric_with`: other proteins the same entities map to, as in a chimera or fusion
    (#40);
  - `other_entities` (complexes);
  - `primary_citation` (#41): `pubmed`, `doi`, `title`, `journal` and `year` of the
    entry's primary citation, or `null`;
  - since 0.3.4, what choosing a structure needs:
    - `refinement`: per refinement, `method`, `r_free` and `r_work` as stated;
    - `deposited` and `released` (dates);
    - `construct`: per polymer entity, its sample `length`, `expression_host`
      (`{name, taxon_id}`) and `tags`, the segments RCSB marks as artifacts (`name`, entity
      `seq_ids` ranges);
    - `mutations`: the residues RCSB marks as mutations, with entity `seq_id`, UniProt
      `position` through the alignment, the `residue` in the structure, the `reference`
      residue and RCSB's `name` (`engineered mutation`, `modified residue`);
    - `sequence_differences`: every aligned residue that differs from the UniProt
      sequence, stated as a mutation or not (`null` without a reference sequence);
    - `observed`: per chain, the UniProt ranges with coordinates (aligned ranges minus
      RCSB's unobserved residues).
  - since 0.3.5, `author_numbering`: per chain, the author residue numbers of UniProt
    positions (RCSB `auth_to_entity_poly_seq_mapping` through the entity alignment), as
    segments `[uniprot_begin, uniprot_end, author_begin]`, or `[position, position,
    "52A"]` for an author id with an insertion code (#73).
    `sabueso.mappings.rcsb_structures.author_position(segments, position)` reads it.
  - since 0.3.6, `secondary_structure` (#80): per chain, `{assigned_by, helix,
    strand}`. `assigned_by` names the programs RCSB states (e.g. PROMOTIF or DSSP).
    `helix` and `strand` are UniProt ranges from RCSB's `HELIX_P` and `SHEET` instance
    features, placed through the entity alignment and split at its gaps. A strand shared
    by two sheets is listed once, and sheets are not kept. A chain is listed only when
    the entry assigns secondary structure to it; a chain without any is not stated,
    never coil.
  - since 0.3.8, `membrane_segments` (#83): per chain, `[{assigned_by, segments}]`, the
    transmembrane segments each resource RCSB integrates assigns (`MEMBRANE_SEGMENT`
    instance features: OPM, PDBTM), as UniProt ranges placed through the entity
    alignment. Resources differ by a residue or two at the ends, so each keeps its own.
    Set only when stated, and the statement of an entry without segments is unchanged.
  - Chain-keyed qualifiers (`observed`, `author_numbering`, `secondary_structure`,
    `membrane_segments`) are
    recorded in the card shape as `{chain}` since 0.3.5, so a new chain name is not a
    new shape.
    These keys are absent from relationships fetched before 0.3.4, and the state that
    `Card.structures()` derives from them is then unknown (`None`), never assumed.
  - `assemblies` (#40): per biological assembly, `id`, `oligomeric_details`,
    `oligomeric_count`, `defined_by` (author, software or both), `method` (e.g. PISA),
    `oligomeric_state`, `stoichiometry` and `symmetry` as RCSB states them, or `null`
    when the entry was not fetched with assembly data;
  - `ligands` (`comp_id`,
  `description`, `subject_of_investigation`, `subject_of_investigation_provenance`, and
  `instances`: per ligand instance, the residues RCSB states as its neighbours, with
  chain, structure `seq_id`, UniProt `position` mapped through the entity alignment, and
  shortest stated distance). Instances are never merged: two copies of a ligand in two
  chains are not one ligand contacting both (#28). Methods are
  normalized to UniProt's vocabulary (`X-RAY DIFFRACTION` → `X-ray`); raw values stay in
  the SourceAssertions. The coverage
  class (`full_length ≥ 0.9 > partial ≥ 0.3 > fragment_or_peptide`) is derived knowledge,
  computed by `Card.structures()` with its rule and thresholds (`structure_coverage_class@1`).
  It is never stored as a qualifier.
- **Storage:** relationships live in the subject Card's `relationship_store`,
  serialized with the card. The aggregator rejects relationships that cite
  SourceAssertions absent from the card. The storage decision is to be re-evaluated in
  uibcdf/sabueso#19.

## Quantities (#32)
- Every physical quantity is stored as a node `{"value": x, "unit": "<canonical name>"}`
  (PyUnitWizard's long spelling: `"nanomolar"`, `"angstrom ** 2"`). A unit never lives in
  a field name, in metadata only, or in documentation only.
- Section fields that are quantities carry `unit` next to `value`
  (`sequence.molecular_weight`, `properties.physchem.molecular_weight`: `dalton`;
  `properties.physchem.tpsa`: `angstrom ** 2`). Counts (`hbd`, `hba`, `rotatable_bonds`,
  `sequence.length`) and logarithmic scores (`logp`, `pchembl`) are not quantities.
- Item fields that are quantities: `annotations.kinase_structures[].resolution` and
  `annotations.gpcr_structures[].resolution` (`angstrom`, #83); SKEMPI's affinities, kinetics, thermodynamics and temperatures in
  `annotations.interface_mutations` (see above).
- Relationship qualifiers: `has_structure.resolution` and contact `min_distance`
  (`angstrom`); `has_bioactivity.measurement.normalized` (`nanomolar` for concentrations,
  `percent` for percentages, `null` when the source unit cannot be normalized). The
  measurement's `value` and `units` stay as ChEMBL states them.
- Ranges and uncertainty (#37, schema 0.3.2):
  - a range keeps its upper end verbatim (`upper_value`, in `units`) and normalized
    (`normalized_upper`, same units as `normalized`). The normalized key exists only
    for ranges;
  - an uncertainty a publication states is `normalized_uncertainty`: `kind` (`sd`, `sem`,
    `unspecified` for a bare "±", or `ci`), then `half_width`, or `lower` and `upper`, as
    nodes in the measurement's normalized unit, and optional `level` (a fraction, for
    `ci`) and `n` (replicates). As written, it lives in the curated SourceAssertion.
    No database source Sabueso maps states an uncertainty, so today only curated
    measurements have one;
  - a range is classified by its band when both ends share one, and is `inconclusive`
    across a threshold (`bioactivity_class@3`). The uncertainty does not change the
    class. Ranges take no pChEMBL check and no scale comparison.
- `Card.to_dict()` writes `quantities`: one PyUnitWizard `QuantityRecordBundle` whose
  entries are columns `"<path template>|<unit>"`. `Card.from_dict()`, and therefore every
  loader, verifies the bundle and checks every node against its column. A change made
  outside Sabueso is refused with `StorageError`. Details and design:
  `devguide/archive/quantities.md`.
- Paths and units are closed: `quantities.NEGOTIATED_UNITS` lists every quantity path
  template and its negotiated units. Writing a quantity elsewhere raises `SchemaError`.
  Reading one refuses the card, with the reader's expected dimensionalities taken from
  that list.
- `Card.quantity(path)` returns a PyUnitWizard quantity, and `Card.quantity_columns(template)`
  returns `{unit: array quantity}`. Views return quantities
  (`Card.structures()["items"][i]["resolution"]`, `Card.bioactivities()` measurement
  `normalized`).

## Quality records (#10)
- `migration` (#51): one record per migration or refresh. A migration record has
  `rule`, `at`, `original_schema`, `original_snapshot` and `steps` (`from`, `to`,
  `converted`, `gaps`). A refresh record has `refresh_of`, `options`, `completed` and
  `not_stated`.
`card.quality` records how the card was resolved and enriched. Its entries are not fields
stated by a source, so they are not `value`/`source_assertion_ids` nodes:
- `conflicts`: `[{field, type: "disagreement", values, source_assertion_ids}]`,
  disagreements among comparable assertions only;
- `alternatives`: `[{field, type: "not_comparable", compare_within, values: [{within,
  values, source_assertion_ids}]}]`, values of different methods, representations or
  sources, reported and never compared (`devguide/SELECTION_RULES_EXAMPLES.md`);
- `enrichments`: per-source enrichment outcomes;
- `retrievals` (#100, schema 0.3.8, only when built with a `RetrievalArchive`):
  `{archive, mode (record, reuse or replay), max_age_seconds (reuse), records: [{ref,
  source, method, url, request_hash, status, retrieved_at, content_hash, size}]}`, every
  answer (`source` is the SourceAssertion source name of the client that asked)
  the build received, in order, each kept in the archive under its `ref`
  (`sabueso:retrieval:sha256:…`);
- `retries` (#97, schema 0.3.9, only when a request was asked again): `[{source,
  reason, count}]`, per source and reason (`HTTP 429`, `HTTP 500`, `HTTP 502`,
  `HTTP 503`, `HTTP 504`, `connection`, `unreadable_body`, a 200 whose body was not the
  JSON asked for). A retry that ended in an answer is listed here; one that did not is
  also the source's `error` in `enrichments`;
- `entity_resolution`: the resolution trace;
- `terms_profile` (#94, since 0.3.7): the terms profile the card was built under, when
  one was asked: `{profile, use, rule: terms_profile@1, excluded: [{source, reason}]}`.

`card.selection_rules` holds the rules the card was resolved with, the packaged defaults
included.

## SourceAssertion Creation Rules (Approved)
- Each mapped field value must generate **at least one** SourceAssertion.
- SourceAssertion IDs are **deterministic** from `(source, record_id, field_path, asserted_value)`
  (`generate_source_assertion_id`, prefix `SA_`).
- Mappings create SourceAssertions with `make_source_assertion`, **before** any
  selection rules are applied.

## Variants and mutagenesis (#33)
`features_positional.natural_variant` (observed in a population) and
`features_positional.mutagenesis` (a substitution the authors made) are separate fields:
they are different kinds of statement about a position. Each item keeps
`substitution` (`original`, `alternatives` as UniProt lists them), the verbatim
`description`, and for variants the `feature_id` (`VAR_…`) and `cross_references`
(dbSNP). The evidence stays in the item's own SourceAssertion (`source_metadata.eco`).
The description is never parsed into a category.

A deletion, UniProt's "Missing", is `substitution: {missing: true}` since 0.3.6 (#80).
Before, it was kept with no substitution, so it read as an unspecified change. Curation
compares a deletion as a substitution of its own.

## Isoforms and secondary structure (#80)
- `annotations.isoforms` lists the isoforms as UniProt's ALTERNATIVE PRODUCTS comment
  states them (`isoform_id`, `name`, `synonyms`, `sequence_status`,
  `alternative_sequence_ids`, `note`). `annotations.alternative_products` keeps the
  comment's `events` and `note`. An entry with no such comment gives `not_stated`,
  never "one isoform".
- `features_positional.alternative_sequence` holds the `VSP_` segments. `isoform_ids`
  comes from the entry's own isoform list (`Sequence=VSP_…`); nothing is matched by
  sequence or name. Isoform sequences are not built from these segments.
- `features_positional.secondary_structure` holds helix, strand and turn segments, each
  with `element` and the `structures` it was read from (`ECO:0007829`). One entry often
  mixes several structures.
- A free-text comment restricted to one isoform keeps it as
  `source_metadata.molecule` on its SourceAssertion.

## Positional Features (Proteins/Peptides)
The schema includes positional features observed directly in UniProt JSON examples:
- Active site, Binding site, Disulfide bond, Glycosylation, Lipidation, Modified residue, Mutagenesis, Natural variant, Region, Motif, Topological domain, Transmembrane, etc.

These are stored as lists of objects with `location`, `description`, and `source_assertion_ids`.

For the exact, verified enumerations, see:
- `devguide/UNIPROT_ENUMS.md`

## Location Model (Sequence + Structure)
Positional features must support **both**:
- **Sequence‑based locations** (start/end indices, sequence ID, 1‑based indexing)
- **Structure‑based locations** (PDB ID, chain ID, residue numbers, optional atom IDs)

This is required for TopoMT integration and visualization.

Real‑ID validation examples:
- `devguide/LOCATION_EXAMPLES.md`

## Location Contract (Approved)
`location` is a typed container that supports multiple contexts:\n\n```\nlocation:\n  kind: \"sequence\" | \"structure\" | \"atom\" | \"substructure\"\n  sequence?: { sequence_id, start, end, indexing, residue_ids? }\n  structure?: { pdb_id, chain_id, residue_id?, residue_number?, atom_ids? }\n  atom?: { atom_ids, atom_id_type }\n  substructure?: { smiles?, smarts?, atom_ids? }\n```\n\nThe exact atom/residue identifier type must always be specified when relevant (e.g., PDB residue IDs, RDKit atom indices).

## Disease Section (ProteinCard)
Protein cards include a `disease` section with disease associations linked to their SourceAssertions.

## Disease cards (#90, schema 0.3.7)
A disease is an entity of its own (`entity_type: disease`), anchored at a MONDO term:
`sabueso:disease:mondo:MONDO:0014221`.
- **Identity.** An id of another terminology (DOID, Orphanet, OMIM, MeSH, EFO, NCIT…)
  resolves to a disease card only when MONDO states that it is the same disease
  (`MONDO:equivalentTo`, rule `mondo_equivalence@1`). The resolution records the
  statement and the MONDO release. Other xrefs are related terms, kept in
  `identifiers.related_ids`, never read as identity. Nothing is matched by name.
- **Obsolete terms** are not followed: the resolution (`obsolete`) names the
  replacement MONDO states as candidates.
- **Fields:** `identifiers.mondo`, `identifiers.equivalent_ids`,
  `identifiers.related_ids`, `names.canonical_name`, `names.synonyms` (with MONDO's
  scope as `kind`), `annotations.definition` and `annotations.disease_subsets`.
- **Relationships:** `subclass_of` (disease → `mondo:<parent>`), one per parent MONDO
  states.
- **On protein cards** (`disease_identity`): `same_as` (a disease id as MONDO spells it,
  e.g. `DOID:0050884` → `mondo:<term>`), one per id on the card that MONDO states is the
  same disease. Qualifiers: `basis` (`mondo_equivalence@1`), `source` (`MONDO`),
  `mondo_name`. With `medgen`, also `same_as` (`MEDGEN:<concept id>` → `MEDGEN:<uid>`),
  qualifiers `basis` (`medgen_concept@1`) and `source` (`MedGen`). `Card.diseases()`
  groups the card's disease statements through them (published `disease_grouping@1`,
  published default `disease_grouping@2` since 0.13.0; development @3 adds
  `disease_identity_coverage@1` without storing new card fields); a ClinVar
  condition is one statement with all its ids. When the ids of one statement reach
  several terms, also `subclass_of` (`mondo:<term>` → `mondo:<broader term>`) for each
  pair MONDO places one under the other. Qualifiers: `source` (`MONDO`) and `path` (the
  chain of terms). Each `is_a` step is a MONDO SourceAssertion, and a chain of several
  steps carries the derivation `mondo_hierarchy@1`.
  Grouping/explanation views are Python API, not stored schema fields. The `@2`
  rule retains all identity paths, contradictory targets, unfinished MedGen branches,
  alternative labels and hierarchy paths. Explicit `grouping_rule="disease_grouping@1"`
  reproduces historical lookup/explanation without migrating or rewriting a card.

## Ligands (ProteinCard)
Ligands are not a card section (the reserved `ligands.items` field was removed, #25).
They are relationships of the protein:
- `has_bioactivity`: measured molecules, one relationship per measurement (#23);
- the `ligands` qualifier of `has_structure`: the chemical components of each structure,
  with the PDB `subject_of_investigation` flag and its provenance (`Author`, declared by
  the depositor, or `RCSB`, assigned for older entries).

`Card.ligands(deck)` crosses them with a deck of SmallMoleculeCards anchored at the
InChIKey (`ligand_deck`). A role such as "inhibitor" is a derived activity class
(`bioactivity_class@3`), never an asserted attribute. The mechanism ChEMBL curates, when
present, is its `action_type`, kept in the measurement qualifiers.

## Clinical Layer (Small Molecules)
The schema includes a dedicated `clinical` section for:
- pharmacology, ADMET, clinical trials, pharmacovigilance,
- indications, contraindications, interactions.

This is intentionally separated from the core physchem and bioactivity data.
