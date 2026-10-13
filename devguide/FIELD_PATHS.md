# Sabueso — Canonical Field Paths

This document defines the **canonical field paths** for Sabueso cards. These are the
paths used by mappings, resolver rules, SourceAssertions, and downstream tools.

Versioning: **x.y.z** (no leading `v`).

Unpublished schema 0.3.14 adds optional gnomAD population-variant assertion metadata
`source_metadata.coordinate_scope` (`assembly`, `basis`, `native_assembly_echo`,
`rule`). This is requested-reference-genome context, not a new biological field,
source value or verified native release. Frozen 0.3.13 remains unchanged; migration
records missing context and refresh obtains it. Development tissue views default
to `pext_at_variant@2` / `isoform_exon_usage@3`, with explicit legacy `usage_rule`.

#139 adds optional quality paths `quality.enrichments[].request_options` (supplied
validated flags/dictionaries, without clients or credentials) and
`quality.migration[].request_restoration` (`rule`, `requests`). Each restoration row
records `source`, `data`, `option`, `record_indices`, `original_statuses`, `status`,
`basis`, `unrecorded_parameters` and `detail`. This records new acquisition scope;
it does not assert exact replay or change scientific fields or SourceAssertions.

Development disease grouping/explanation @3 (#144) adds transient per-identifier
coverage under `disease_identity_coverage@1`; packet mapping @7 retains it. No
canonical card field or schema is added; original @1/@2 views and stored pins remain
explicitly available.

---

## 1) Global Base Paths (all card types)

### meta.*
- `meta.card_id`
- `meta.schema_version`
- `meta.entity_type`
- `meta.created_at`
- `meta.updated_at`
- `meta.sources`

### identifiers.*
- `identifiers.uniprot`
- `identifiers.pdb`
- `identifiers.chembl`
- `identifiers.pubchem`
- `identifiers.drugbank`
- `identifiers.inchi`
- `identifiers.inchikey`
- `identifiers.smiles` (isomeric: keeps stereochemistry where the source defines it)
- `identifiers.smiles_connectivity` (connectivity only, no stereochemistry)
- `identifiers.gene_loci` (list of `{database, id}`: gene loci in organism databases, e.g. `{"database": "TriTrypDB", "id": "TcCLB.508647.200"}` from UniProt's VEuPathDB cross-references, and `{"database": "NCBI Gene", "id": "7167"}`; identity anchors that tell paralogs apart, #54)
- `identifiers.other` (list/dict for rare IDs)

### names.*
- `names.canonical_name` (source-native molecule names include ChEBI and PubChem summary-page `Title` (`source_metadata.pubchem_property: Title`); UniProt's recommended name; an unreviewed entry without one gives its first submission name, with `source_metadata.uniprot_name: submission`)
- `names.synonyms` (list of `{name, kind}`; UniProt's alternative names, `kind: alternative_name`, and the submitter's other names, `submission_name`; curatable as `{name}`: a name a publication uses for the entry, which anchors resolution by name through a curation store, #55. A curated `{name}` that UniProt states corroborates it: `kind` describes the item, it does not state it)
- `names.abbreviations` (list of `{name, of}`; UniProt's short names, with the full name each shortens)
- `names.gene_names` (list of `{name, kind, gene}`; UniProt's gene names, `kind` one of `gene_name`, `synonym`, `ordered_locus`, `orf`; `gene` numbers the gene within the entry, since an entry can be encoded by several)

### properties.*
- `properties.physchem.formula`
- `properties.physchem.molecular_weight` (quantity node, `dalton`)
- `properties.physchem.logp`
- `properties.physchem.tpsa` (quantity node, `angstrom ** 2`)
- `properties.physchem.hbd`
- `properties.physchem.hba`
- `properties.physchem.rotatable_bonds`
- `properties.physchem.aromatic_rings`
- `properties.physchem.molecule_type`

### annotations.*
- `annotations.function`
- `annotations.catalytic_activity` (list of `{reaction, ec_number, rhea_id, molecule?}`)
- `annotations.pathway`
- `annotations.subunit`
- `annotations.subcellular_location` (list of `{location, topology?, orientation?, molecule?}`)
- `annotations.disease` (list of `{name, accession?, acronym?, description?, cross_references?, note?}`; UniProt DISEASE comments, with their evidences in each SourceAssertion's `eco`)
- `annotations.tissue_specificity`
- `annotations.organism`
- `annotations.taxon_id` (NCBI taxonomy id; strain-level when the entry is, #54)
- `annotations.lineage` (list of taxon names from the root down, the organism itself excluded, as UniProt states it, #54)
- `annotations.taxonomy` (`{tax_id, name, rank, ancestors: [{tax_id, name, rank}]}` from NCBI Taxonomy: ranks and ancestor ids, root first; opt-in enrichment `taxonomy=True`, #67)
- `annotations.ptm`
- `annotations.polymorphism`
- `annotations.activity_regulation` (UniProt native activity regulation text; since published schema 0.3.13)
- `annotations.domain_notes` (UniProt native domain notes text; since published schema 0.3.13)
- `annotations.similarity` (UniProt native similarity text; since published schema 0.3.13)
- `annotations.source_cautions` (UniProt native source cautions text; since published schema 0.3.13)
- `annotations.miscellaneous` (UniProt native miscellaneous text; since published schema 0.3.13)
- `annotations.domains` (non-positional summary; reserved, not currently produced)

### literature.*
- `literature.claims` (list of `{topic, text, about?}`; curated free-text claims typed by topic, never compared, #43)

### features_positional.*
- `features_positional.domains` (UniProt positional domains, active in development 0.3.13; independent ECO, original bounds/molecule scope and sequence revision)
- `features_positional.chain` (UniProt native chain feature; since published schema 0.3.13)
- `features_positional.lipidation` (UniProt native lipidation feature; since published schema 0.3.13)
- `features_positional.motif` (UniProt native motif feature; since published schema 0.3.13)
- `features_positional.region` (UniProt native region feature; since published schema 0.3.13)
- `features_positional.sequence_conflict` (UniProt native sequence conflict feature; since published schema 0.3.13)
- `features_positional.topological_domain` (UniProt native topological domain feature; since published schema 0.3.13)
- `features_positional.transmembrane` (UniProt native transmembrane feature; since published schema 0.3.13)
- `features_positional.active_site`
- `features_positional.binding_site`
- `features_positional.family_site` (sites an InterPro member database places on the sequence, e.g. CDD catalytic triad; one item per site, with its signature)
- `features_positional.modified_residue`
- `features_positional.disulfide_bond`
- `features_positional.natural_variant` (a variant observed in a population: substitution, verbatim description, `VAR_` id, dbSNP)
- `features_positional.mutagenesis` (a substitution the authors made, with the effect they report)
- `features_positional.alternative_sequence` (the segment an isoform replaces or lacks: substitution, verbatim description, `VSP_` id, and the `isoform_ids` the entry links to it; #80)
- `features_positional.secondary_structure` (UniProt's helix, strand and turn segments: `element`, and the `structures` each segment was read from, e.g. `pdb:9F69`; #80)
- A `substitution` with `missing: true` is a deletion (UniProt's "Missing"), in variants, mutagenesis and alternative sequences (since 0.3.6).
- `features_positional.glycosylation`

### clinical.*
- `clinical.pharmacology`
- `clinical.pharmacokinetics`
- `clinical.pharmacodynamics`
- `clinical.admet`
- `clinical.clinical_trials`
- `clinical.pharmacovigilance`
- `clinical.adverse_events`
- `clinical.toxicity`
- `clinical.indications`
- `clinical.contraindications`
- `clinical.interactions`
- `clinical.dosing`
- `clinical.regulatory_status`
- `clinical.max_phase` (ChEMBL highest development phase: 4 approved, 3–1 clinical, 0.5 early phase 1, -1 unknown)

### quantities.*
The seal over every quantity node of a stored card (uibcdf/sabueso#32):
- `quantities.*` (PyUnitWizard QuantityRecordBundle; one column per path and unit)

### quality.*
Records of how the card was resolved and enriched, not source-stated fields:
- `quality.conflicts` (disagreements among comparable assertions)
- `quality.alternatives` (values of different methods, representations or sources, not compared)
- `quality.enrichments` (per-source enrichment outcomes)
- `quality.entity_resolution` (resolution trace)
- `quality.literature_extractions` (published 0.3.12: scientific intake identity,
  named intake/extraction rules, subject/publication, locator/input hash, original
  assertion and relationship IDs, and unknown fragment terms; optional
  `article_metadata_source_assertion_ids` and `metadata_binding_rule` name separate
  native bibliographic support under `article_metadata_binding@1`. Metadata assertions
  have `field_path: literature.article_metadata` and publication subject;
  `source_metadata` retains `content_kind`, `requested_identifier`, `publication_ref`,
  `identity_basis`, `service_version` and `version_basis`. Native metadata lives in
  `asserted_value`, not selected card fields. Runtime records remain separate)

---

## 2) ProteinCard Extensions

- `annotations.enzyme_class`
- `annotations.family`
- `annotations.similar_proteins`
- `annotations.isoforms` (list of `{isoform_id, isoform_ids?, name?, synonyms?, sequence_status?, alternative_sequence_ids?, note?}`; UniProt ALTERNATIVE PRODUCTS, #80)
- `annotations.alternative_products` (`{events?, note?}`: what produces the isoforms, and UniProt's note on the list, e.g. "Additional isoforms seem to exist.")
- Biological context of a target, curated from publications only (#60); every value is stated text:
  - `annotations.stage_expression` (`{stage, observation, host?, method?, level?, note?}`)
  - `annotations.essentiality` (`{method, phenotype, stage?, host?, condition?, call?, note?}`; `call` is the authors' own word, e.g. "essential")
  - `annotations.accessibility` (`{compartment, exposure?, stage?, host?, method?, note?}`)
  - `annotations.metabolic_role` (`{pathway, role, stage?, host?, method?, note?}`)
- `annotations.clinical_variants` (ClinVar: `{accession, title, variant_type, transcript?, hgvs_c?, hgvs_p?, classification, review_status, last_evaluated?, conditions, consequences, location?, substitution?, numbering, not_placed?}`; `location` in UniProt numbering only through a canonical transcript UniProt states and a matching residue, or through another isoform's transcript with rule `uniprot_isoform_map@1`, recorded in `placed_via`)
- `annotations.population_variants` (gnomAD: `{variant_id, consequence, transcript, transcript_version?, hgvs_c, hgvs_p, flags?, exome?, genome?, location?, substitution?, placed_via?, numbering, not_placed?, canonical_consequence?}`; `exome`/`genome` are `{ac, an, af}`; the consequence gnomAD states on the canonical transcript UniProt states comes first; otherwise placed by the same rule as ClinVar; `canonical_consequence` is `{transcript, transcript_version, consequence, hgvs_c}` for a change gnomAD states is not coding on the canonical transcript, #85)
- `annotations.kinase_classification` (KLIFS: `{kinase_id, name, group, family, subfamily?, pocket_sequence}`, one per KLIFS kinase whose UniProt accession KLIFS states; since 0.3.8)
- `annotations.kinase_structures` (KLIFS: `{kinase_id, klifs_structure_id, structure, chain, alt?, dfg?, ac_helix?, ligand?, allosteric_ligand?, quality_score?, resolution?, missing_residues?, missing_atoms?}`; `resolution` in angstrom; since 0.3.8)
- `annotations.kinase_pocket` (KLIFS: `{kinase_id, index, klifs_position, residue?, location?, placed_via?, numbering, not_placed?}`, the 85 pocket positions; placed through one structure's author numbering, rules `klifs_pocket_reference@1` and `rcsb_author_numbering@1`; since 0.3.8)
- `annotations.gpcr_classification` (GPCRdb: `{entry_name, name, receptor_class, family, numbering_scheme}`; since 0.3.8)
- `annotations.gpcr_segments` (GPCRdb: `{segment, gpcrdb_start, gpcrdb_end, location?, numbering, not_placed?}`; since 0.3.8)
- `annotations.gpcr_residues` (GPCRdb: `{gpcrdb_position, residue, segment, generic_number, generic_numbers: [{scheme, label}], location?, placed_via?, numbering, not_placed?}`, residues with a generic number; rule `gpcrdb_sequence_numbering@1`; since 0.3.8)
- `annotations.gpcr_structures` (GPCRdb: `{structure, chain, state, method?, resolution?, publication?, publication_date?, ligands?: [{name, pdb_ccd?, type?, function?}], apo?, signalling_protein?: {type, partners}}`; `resolution` in angstrom; since 0.3.8)
- `identifiers.uniref` (UniProt's UniRef clusters: `{uniref100, uniref90, uniref50}`; since 0.3.9, #103)
- `identifiers.ensembl_transcripts` (UniProt's Ensembl cross-references: `{transcript, protein?, gene?, isoform?}`, `transcript` versioned as UniProt states it, `isoform` when UniProt names the isoform it encodes; read by `Card.isoform_tissue_usage()`; since 0.3.10, #102)
- `annotations.tissue_terms` (GTEx, for each tissue the card's pext names: `{gtex_id, name, tissue_site?, ontology_id, ontology_iri?}`, the term UBERON or EFO as GTEx states it; joined to the pext's tissues by `gtex_tissue_key@1`; since 0.3.10, #102)
- `annotations.exon_usage_by_tissue` (gnomAD pext: `{gene, assembly, chromosome, start, end, mean, tissues: [{tissue, value}]}`, per coding region in GRCh38, GTEx v10 tissues; read by `Card.variant_tissue_usage()`, published rule `pext_at_variant@1`, development `@2`; since 0.3.8, #102)
- `annotations.isoform_coding_exons` (gnomAD transcript exons, UniProt isoform per its cross-reference: `{isoform, transcript, transcript_version, assembly, chromosome, strand, cds: [[start, end]]}`; read by `Card.isoform_tissue_usage()`, published rule `isoform_exon_usage@2`, development `@3`; since 0.3.8, #102)
- `annotations.antibody_complexes` (SAbDab: `{structure, model, heavy_chain?, light_chain?, antigen_chains, antigens}`; chains `{chain, entity, type, v_gene_subgroup?}`; antigens `{name, type, entity, chain, this_protein}`; joined through the PDB chains UniProt states; since 0.3.8)
- `annotations.interface_mutations` (SKEMPI 2.0: `{structure, complex, sides, protein_chains, proteins, mutations, affinity, kinetics?, thermodynamics?, temperature?, temperature_assumed?, method?, reference?, reference_stated?, notes?, hold_out_type?, skempi_version?}`; each mutation `{chain, author_residue, original, change, location_class?, on, location?, placed_via?, not_placed?}`; placed through RCSB's author numbering, rule `rcsb_author_numbering@1`; quantities in molar, 1/(M·s), 1/s, kcal/mol, cal/(mol·K) and kelvin; since 0.3.7)
- `annotations.pathogen_phenotypes` (PHI-base: `{annotation_type, phenotype, extensions?, high_level_terms?, genotype, pathogen, host?, diseases?, conditions?, method?, phi_ids?, publication?, curator_comment?}`; the genotype lists every allele, so a double mutant is never read as a single one)
- `disease.associations`
- `sequence.primary`
- `sequence.length`
- `sequence.molecular_weight` (quantity node, `dalton`)
- `sequence.checksums` (`crc64`, `md5`)
- `structure.primary`
- `structure.secondary_structure` (declared, never written: UniProt's statement is `features_positional.secondary_structure`)
- `structure.chains`
- `structure.entities`

---

## 3) PeptideCard Extensions

- Same as ProteinCard, but may omit `structure.*` if not available.

---

## 4) SmallMoleculeCard Extensions

- `identifiers.chebi` (`CHEBI:<n>`, since 0.3.8, #83): the ChEBI entry UniChem links and whose stated InChIKey is the anchor
- `annotations.drug_class`
- `annotations.chemical_classes` (since 0.3.8): list of `{chebi_id, name}`, the classes ChEBI says the molecule is a member of (`is a`)
- `annotations.chemical_roles` (since 0.3.8): list of `{chebi_id, name, direct, biological_role, chemical_role, application}`; `direct` roles are the entry's own `has role` statements, the others ChEBI classifies it with through its classes or parent roles
- `annotations.definition` (since 0.3.8): `{text}`, ChEBI's definition; the assertion keeps its markup, the value is its plain text
- `clinical.*` (same keys as base)

---

## 5) DiseaseCard Extensions (#90, since 0.3.7)

Anchored at a MONDO term (`sabueso:disease:mondo:MONDO:0014221`).

- `identifiers.mondo` (the MONDO id)
- `identifiers.equivalent_ids` (list of the ids MONDO states are the same disease, `MONDO:equivalentTo`, e.g. `DOID:0050884`, `Orphanet:868`, `OMIM:615512`; the only ids that join other sources' diseases to the card)
- `identifiers.related_ids` (list of MONDO's other xrefs: related terms, never identity)
- `annotations.definition` (`{text, references}`, as MONDO states it)
- `annotations.disease_subsets` (list of MONDO subsets the term is in, e.g. `rare`)
- `names.canonical_name` and `names.synonyms` (`{name, kind}`, kind `exact_synonym`, `related_synonym`, `broad_synonym` or `narrow_synonym`) are shared with the base paths.
- Parents are `subclass_of` relationships (disease → `mondo:<id>`).

---

## Notes
- Since card schema 0.3.11 (frozen for the 0.12.0 candidate), `mentioned_in` optionally carries
  `qualifiers.article` (native article identifiers) and `qualifiers.locations[]`
  (`annotation`, unchanged from Europe PMC, and `source_assertion_id`). Each occurrence
  has its own SourceAssertion; its `source_metadata.identity_basis` records the
  printed accession and matching UniProt tag. These are relationship qualifiers,
  not section field paths. `quality.enrichments` records explicit `article_ids`,
  `data: located_accession_annotations`, `annotation_count` and `returned_annotations`.
- The same frozen candidate schema adds derived `structure_mentioned_in` relationships
  (protein → publication, one per `structure_ref`), with `article`, `locations`,
  `structure_ref` and `structure_context` qualifiers. Context records `protein_ref`,
  `structure_ref`, structural `relationship_ids`, supporting `source_assertion_ids`
  and `scope: entry_association`. Raw PDB mention assertions use
  `relationships.mentioned_in` with a PDB subject and `stated_pdb_accession` identity
  basis. Rule `structure_mention_context@1` retains both legs; it never creates an
  assertion for the derived protein link. Enrichment records add
  `mapping: located_accession_mapping@2`, `uniprot_mention_count`,
  `structure_mention_count`, `uniprot_annotation_count`, `pdb_annotation_count`, and
  `unlinked_pdb_mentions[]` (`structure_ref`, native `annotation_id`, `reason`).
  `Card.literature()` adds `structure_mentions` only to publications with these
  links, keeping context, locations, support, derivation and qualifier alternatives.
- GO annotations, family/domain classifications, curated interactions and experimental
  structures are **relationships**, not field paths: `annotated_with`, `classified_in`,
  `interacts_with` and `has_structure` (see the Relationship contract in `SCHEMA.md`).
- `annotations.domains` and `features_positional.domains` are both valid.
- If only positional data exists, populate `features_positional.domains`.
- If only non-positional data exists, populate `annotations.domains`.
- If both exist, keep both.
