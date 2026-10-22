# Sabueso — Public API

This document records the public surface of release 0.14.0 and explicitly labelled
future development additions. Anything not listed here, or not exported by `sabueso`, is internal.
Tools, views, stores and source access check their arguments through ArgDigest.
Plain accessors (`get`, `set`, `sort`…) do not, and fail loudly on wrong types
(`ARGUMENT_CONTRACTS.md` lists which is which). The user guide (`docs/`) shows how
to use them. Development entries do not establish public delivery, automatic card
enrichment or live-service qualification.

## Development recovery after 0.13.0

This historical section records the recovery delivered in 0.14.0 (#134).
Native routes retain their individual fixture, terms and live-access limits.

`sabueso.tools.sources.get_catalog()` reads detached, packaged registry metadata
without source access. Its `capabilities` inventory names native function/client
declarations, declared card contributions and reviewed new fixture delivery under
`source_capability_inventory@1`. This development surface does not assess live
health, consumer acceptance or scientific completeness; absence of a declared
enricher also does not characterize established bespoke card routes.

The [development native-source API](sources/DEVELOPMENT_API.md) lists recovered
`get_*` functions, independent mapping subjects and their exact scientific scope.
These are standalone unless a card contribution is explicitly declared. Supplied
snapshots, sequence/isoform candidates, notebook reports and residue views retain
their separate public interfaces below and in the user guide. Source `in_use` does
not promise card enrichment, live availability or public-package delivery.

## Entry point

- Since 0.13.0: `sabueso.extract_literature_mentions(text, identifier, publication, locator)`
  runs `literal_uniprot_mention@1` on supplied text with an explicit canonical UniProt
  accession and publication reference. It returns detached per-occurrence
  `source_assertions`, supported `relationships` and original `extraction_trace` with
  portable Ackredit attribution. Explicit namespace/official URL, case-sensitive
  token boundaries and Unicode offsets are required. It makes no card intake,
  curation, identity merge, article fetch or biological inference (#92).

- `sabueso.resolve(query, entity_type=None, profile=None, curations=None, extractions=None, **options)`
  returns `(card | None, resolution)`.
  - Since 0.13.0: `extractions` accepts an `ExtractionStore` or its path. It explicitly
    applies original literal-rule results for the exact UniProt subject and records
    reuse. It does not execute extraction; fragment terms remain unknown.
  - `query` is an identifier (UniProt accession, `pdb:`, `pubchem:`, `chembl:`,
    `pdb.ligand:`, `inchikey:`, a structure (`smiles:`, `inchi:`, matched by PubChem,
    #93), a disease id: `mondo:`, `doid:`, `orphanet:`, `omim:`,
    `mesh:`, `efo:`… (#90)) or an `EntityQuery(name=..., organism=...,
    include_subtaxa=...)`. `entity_type` is `protein`, `small_molecule` or `disease`.
  - Options go to the card tool. For proteins:
    - `structures`, `interfaces`, `ligand_sites`, `family_sites`;
    - `chembl`, `bindingdb` (`{"cutoff", "limit"}`), `pubchem_bioassay` (`True` or
      `{"limit"}`), `string`;
    - `predicted_structures`, `taxonomy`, `ncbi_gene`;
    - `phi_base` (pathogen phenotypes, #83), `diseases`, `open_targets` and
      `orphadata` (disease associations, #82), `reactome` (pathways, #83), `clinvar`
      and `gnomad` (variants, #83), `skempi` (interface mutations, #83), `klifs`
      (kinase classification, structures and pocket, #83), `gpcrdb` (GPCR numbering
      and structure states, #83), `sabdab` (antibody complexes, #83), `oma` (orthologs, #83), `uniref` (sequence
      clusters, #103),
      `medgen` and `disease_identity` (identity of the card's diseases through MedGen
      and MONDO, #90), `europepmc` (publications whose text states the accession,
      #92);
      `europepmc={"article_ids": "PMC:PMC12400196"}` instead adds located accession
      mentions from explicit articles, with native locators and per-occurrence support
      (since 0.12.0). One MED/PMC id or a non-empty list is accepted; `limit` is not
      accepted with `article_ids`. It does not read names or scientific claims.
      Direct UniProt mentions remain `mentioned_in`. PDB mentions supported by
      source-stated structural associations add derived `structure_mentioned_in`
      relationships and conditional `literature().publications[].structure_mentions`,
      with both identity and occurrence support retained (since 0.12.0).
    - each source's `*_client`, and `resolver`.
  - For small molecules: `unichem`, `pubchem`, `chebi` (#83), `indications` and
    `trials` (#81).
    Optional ChEBI enrichment retains native name and formula as independent
    SourceAssertions; names and formulas do not establish chemical identity.
  - For diseases: `mondo_client`.
  - Every card tool takes `terms` (`"commercial"` or `"non_commercial"`): only sources
    whose stated terms allow that use are asked (#94).
  - An option the tool does not take is refused, never ignored.
- `sabueso.resolve_protein_card`, `sabueso.resolve_molecule_card`: the card tools behind
  `resolve`; diseases through `sabueso.resolve_disease_card` (#90).
- `Card.acquisition_trace`, `EntityResolution.acquisition_trace` and
  `KnowledgePacket.acquisition_trace` (since 0.12.0, #108): detached runtime source
  events for declared built-in UniProt/Europe PMC/RCSB boundaries. Resolution failures
  returning no card retain their trace; escaping exceptions also carry it.
  `knowledge_packet` retains its intake, while composition from existing cards
  creates no new acquisition trace. Independent copies preserve original versions,
  routes, response identities, empty answers and failures. Saved scientific payloads
  return `None`; retain original JSON sidecars. Other sources/custom clients are
  explicitly unobserved. `SOURCE_ACCESS.md` defines the coverage and local formats.
  Since 0.13.0, chemical identity access adds CCD batches and both UniChem lookup
  methods, alongside ChEMBL/PubChem/BindingDB observation. `resolve_molecule_card`
  retains card/resolution traces; `ligand_deck` exposes `Deck.acquisition_trace`,
  including its native snapshot id, output card pins and input protein pin.
  The trace is detached from deck metadata/hashes. Saved or ordinarily derived
  decks have no new trace; preserve original sidecars explicitly.
  Development NCBI Taxonomy online/fixture `taxa` and public `get_taxon` now retain
  original batch/query/response identities, missing or unavailable scope and
  failure/reuse/replay observation. `get_taxon` adds a detached `acquisition_trace`
  envelope; native records and card serialization remain unchanged. A fixture
  omitted locally is unavailable, not source-stated absence. API route version
  and taxonomy record revision remain distinct; unreported revisions stay unknown.
  An unavailable organism fixture produces a connector failure and card knowledge
  state `unavailable`; a source-stated empty online answer remains not found.
  Since 0.13.0, PDBe-KB ligand-site and interface-residue access also retains
  separate aggregate query traces, native structural references and unknown versions.
  Listed providers/structures do not claim additional direct source access.
  Since 0.13.0, AlphaFold DB `prediction` access keeps native model identities,
  per-model versions, declared tool/provider/URL context and original source receipts.
  It downloads no linked artifact and claims no local model-generation execution.
  Since 0.13.0, InterPro `site_residues` access retains native signature/site context,
  header/fixture releases, original archive receipts, empty and failed outcomes.
  It runs no alignment/InterProScan and claims no direct member-database access.
  Development MONDO `term`/`equivalent` access retains normalized queries, native
  OBO versions, original index/file origins, memory/archive reuse and bibliography.
  `tools.db.mondo.get_term` adds the usual detached envelope trace; direct
  `resolve_disease_card` retains its card/resolution traces. Scientific retrieval
  times now preserve the original response and invalid documents are connector
  failures (#123). No card field/schema or signature changes are introduced.
  Development Open Targets `associations`/`targets` and Orphadata
  `associations`/`genes` also retain native query/page/file versions, original
  retrieval/reuse, scoped absence/failures and resource citations (#108/#124).
  Their public association envelopes add detached acquisition traces.
- Development DISEASES `associations`, ClinVar `variants` and MedGen `concepts`
  retain detached channel/page/identity acquisition records, including original
  version/time origins, reuse, caps and completed subsets on failure (#108/#125).
  Their public source envelopes add `acquisition_trace`. Native protocol omissions,
  invalid summaries and ambiguous/capped MedGen identity are connector failures;
  missing fixtures are unavailable. Valid scientific records and signatures stay
  fixed. Resource citations do not replace underlying study/submission metadata.
- Development GTEx `tissues` and public `tools.db.gtex.get_tissues` retain detached
  acquisition traces and portable resource credit (#108). Requested dataset labels
  remain separate from unknown native revisions; returned row counts are separate
  from card-selected terms and do not prove full-dataset coverage. Missing local
  files raise `ConnectorError` with `unavailable` observation. Blocked prerequisites
  create no GTEx operation; original sidecars and exact pins have an inert reader.
  Successful scientific returns and source assertion identities remain unchanged.
  See [the GTEx scope](pending_proposals/gtex_observation.md).
- Development UniRef `clusters`/`members` retain detached `UniProt` acquisition
  records; public `tools.db.uniref.get_clusters` attaches its trace. Individual
  page releases, continuation, received/kept counts and partial failures remain
  explicit; client version labels do not prove coherent pages. Missing fixtures
  raise `ConnectorError` with an unavailable observation. Successful scientific
  returns and pins stay fixed. Online members allow at most 100 logical pages,
  including empty pages; repeated request URLs or an exhausted page budget raise
  `ConnectorError` without returning partial knowledge. The 5,000-member ceiling
  remains successful explicit truncation. See [the UniRef scope](pending_proposals/uniref_observation.md)
  and [pagination policy](archive/uniref_pagination.md).
- Development OMA `xrefs`/`protein`/`orthologs` retain detached OMA observations;
  entry-name `accessions` is a separate UniProt operation. Public
  `tools.db.oma.get_orthologs` attaches its trace. Revision gaps, unasked continuation,
  received/client-selected counts and partial batch failure remain explicit. Missing
  local files are unavailable; failed name resolution installs no partial ortholog
  support. Normal scientific values and pins stay fixed.
  [Scope](pending_proposals/oma_observation.md).
- Development gnomAD `variants`/`transcript_variants`/`consequences`/`pext`
  retain GraphQL request/response scope under `gnomAD`; public `get_variants`,
  `get_transcript_variants` and `get_pext` attach their traces. Client dataset/GTEx
  labels never become native revisions. Received/client/card counts, null aliases,
  partial failures and unavailable local inputs remain distinct. Missing upstream
  gene identity is unqueried before client construction (#141). Normal supplied-gene
  scientific pins stay fixed. [Scope](pending_proposals/gnomad_observation.md).
- `sabueso.ambiguity_deck(resolution)`: the candidates of an ambiguous resolution as a
  Deck.
- `sabueso.resolve_disease_card(identifier)`, `sabueso.disease_targets(disease,
  limit=50)` and `sabueso.disease_drugs(disease, limit=50)`: a disease card, and decks
  of its targets and of the drugs whose indications name it (#90).
  Development after 0.13.0 (#91): rules `disease_targets@2` / `disease_drugs@2`
  additionally pin native membership assertions, source row order, original MONDO
  input and member identity, including exclusions. `Deck.explain` exposes original
  `disease_deck_explanation@1` support or explicit gaps. Saving/exporting the deck
  preserves its embedded scientific support. `Deck.terms` includes embedded sources;
  `Deck.admissible` now uses development `disease_deck_admission@1`: whole embedded
  support must allow the use; unknown/restricted members are excluded with historical
  references. Finer filtering by terms of use remains #29 work. No signature changes
  or complete source-observation/bibliography guarantees are introduced.
  The local #126 correction rejects another candidate's valid native basis when
  the actual member's bound identifier assertions do not state that candidate.
  Development (#108): both disease builders expose `Deck.acquisition_trace`
  with executing version/times, original disease input/support pins, final
  deck/member pins, rule/limit, source outcomes and exclusions. Reading stored
  payloads creates no new trace or credit; retain original sidecars.
- `sabueso.ligand_deck(protein_card, ...)`: the small-molecule cards of a protein's
  ligands and measured molecules.
- `sabueso.expand(card, predicate, limit=50, options=None, terms=None)`: a deck of the
  cards of the entities a card relates to by a predicate, or several
  (`relationship_expansion@1`, #91). Also `Card.expand` and `Deck.expand`.

## Knowledge packets (prototype, #71; contract in uibcdf/moli#22)

- `KnowledgePacket.attribution` (since 0.12.0, #108) automatically retains a detached
  composition record outside the scientific payload and hashes. Its accessor returns
  an independent copy; payload-only saved readers return `None` and add no credit.
  Save the original JSON sidecar alongside the scientific packet.
  `sabueso.attribution()` yields an `AttributionRun`; its
  `records` accessor returns detached JSON records for completed packet composition.
  Its separate `acquisitions` accessor retains observed source operations, including
  failures. Collection is optional; runtime attachment is automatic.
  Development (#108): `operations` separately retains the execution of
  `sequence_differences`, `variant_tissue_usage` and `isoform_tissue_usage` called
  inside this explicit context (`sabueso.comparative_operation@2`). Exact pins,
  original rules/parameters, result digests and input-field support survive as
  application-owned sidecars. Plain views and all explanations remain inert;
  missing bibliography stays separate from scientific support gaps. No card,
  query or packet payload is changed. See [scope](pending_proposals/comparative_operations.md).
  Since 0.13.0, `literature` separately collects original literal-extraction execution
  and intake/reuse events, including stored-support-only refresh gaps.
  Applications own Ackredit sessions. The required lazy adapter preserves per-result
  reused resources and contributes to enclosing captures/workflows; provider failures
  preserves knowledge and host records. Records carry source-record versions and
  exact support pins, separately from packets/terms. Acquisition uses the separate
  bounded source adapter described above. Ackredit is required in runtime
  metadata/recipe; public Ackredit 0.9.0 satisfies the qualified API floor.
  See the user attribution page and
  `examples/ackredit_pilot/`.

- `sabueso.KnowledgeQuery(subject, comparator=None, aspects=None, constraints=None,
  detail="full")`: `to_dict()`, `from_dict(data)`, `options()`. `detail="index"` gives,
  per aspect, what the cards hold and the reference of every item, without values
  (`packet_index@1`, #88).
- `sabueso.knowledge_packet(knowledge_query, store=None, packet_name=None, note=None,
  curations=None, **clients)` resolves, composes, and optionally stores.
- `sabueso.compose_packet(knowledge_query, subject, comparator=None)` composes from
  existing cards.
  In published `packet_aspects@6`, the literature aspect includes direct UniProt
  mentions and derived PDB mention context in both the index and unknowns. Automatic
  `knowledge_packet` acquisition requests bibliography only (`europepmc={}`);
  located annotations enter via explicit article intake on prebuilt cards, then
  `compose_packet`. The index cites separate relationships and names the structure
  mention rule; it does not copy fragments. Earlier packets keep their stored mapping.
- `KnowledgePacket`: `entities`, `facts`, `conflicts`, `unknowns`, `provenance`,
  `query`, `ref`, `format`, `detail`; `snapshot_id()`, `content_id()`,
  `same_knowledge(other)` (None across formats, aspect mappings and levels of detail),
  `cite(role, item_id)`, `item(role, item_id, store)`, `to_dict()`.
  `terms(use, store)` reads exact saved card pins and reports represented statement
  support, conflicts and stored dependencies (`packet_terms@1`, since 0.12.0).
  Full/index support `packet_aspects@6/@7`; @6 reconstructs historical disease
  grouping @2, while development @7 retains coverage @1/grouping @3. Other mappings
  need an adapter.
  It uses the current packaged terms registry with review dates, without changing
  packet hashes/payloads or reconstructing a historical terms-registry snapshot.

## Card

- **Development literal access (#148).** `access(related_cards=())` captures
  detached validated Card data. The returned `CardAccess` provides `catalog`,
  `read`, `selection`, `export_card`, `root_location`, `context`, `profile` and
  `capabilities`. `AccessSelection.page(limit=32, max_bytes=65536, cursor=None)`
  returns bounded canonical-JSON data, explicit item/value completeness and
  snapshot/session-bound continuation. This first slice offers literal content
  only; the [structural continuation](pending_proposals/card_structures_exploration.md)
  now adds `select("structures", fields=None, options=None)` and
  `explain(item_ref)` over the same capture. Supported literal selections share portable saved reading; saved scientific selections remain pending. See the [implemented scope](pending_proposals/card_access_literal.md).
- **Development human exploration (#148).** `explore(related_cards=())` returns
  `CardExplorer`: `overview`, `topics`, `questions`, `inspect(field_path=None,
  locator=None)`, `search(text)`, `view(topic)` and `answer(question, options=None)`. `explorer.access` shares its
  exact capture. Read-only `CardView`/`CardItems`/`CardItem`/`Cell` provide complete
  literal inspection, original support, selected-item navigation and bounded safe
  text/HTML previews. Literal selection uses `label`/`kind`;
  `view("structures", options=None)` adds typed protein inventory columns, original
  explanations, exclusions and source scope. Resolution sorting takes `unit=None`.
  Protein `overview()` now opens readable scientific routes; `view("function")`
  shows retained field values with direct original assertions through `explain()`.
  `questions()` advertises `function` and `region_coverage`; the latter requires
  explicit canonical `sequence_ref` and `region` options before using the existing
  structural result. `CardView.request` retains the effective question binding.
  See the [protein journey](pending_proposals/card_protein_exploration.md).
  Molecule `chemistry`/`properties` and disease `definition`/`classification`/`identity`
  now have distinct field/relationship views and their initial question aliases.
  `view("coverage")` shares the existing knowledge-state result and lazy exact scoped
  explanations; `view("quality")` retains raw quality records. All new item payloads
  are readable through the same bounded literal access. The specialized machine
  selector still supports structures only. See the [nature continuation](pending_proposals/card_nature_exploration.md).
  `item.related()` now returns declared source/subject/object/entity links;
  `link.open()` or `links.follow(item_ref)` opens an exact retained destination.
  Supplied Cards switch to their own profile; missing context has `explorer=None`,
  and multiple supported captures require explicit candidate selection. Every
  transition retains its originating detail and selected view. See the
  [contextual navigation scope](pending_proposals/card_context_navigation.md).
  Supported literal/field views and literal `AccessSelection`s now offer
  `save(path, overwrite=False)`, reopened as a saved `CardView` through
  `sabueso.read_exploration(path, expected_digest=None)`. Captured values, units,
  original support, selections and navigation remain bound to verified inputs.
  `view.validation` reports the actual verification scope; `explorer.start_new()`
  explicitly starts a new local interpretation. Saved scientific classification
  persistence remains pending and unsupported saves are explicit. See the
  [first persistence scope](pending_proposals/card_saved_exploration.md).
- **Read.** `get(field_path)`, `extract(field_paths)`, `list_fields()`,
  `quantity(field_path)`, `quantity_columns(template)`,
  `relationships(predicate=None, object_ref=None)`.
- **Views.** Each derives knowledge with a named rule:
  - `structures(include_fragments=False, region=None)` and `predicted_structures()`;
  - `oligomer(*, agreement_rule="interface_site_agreement@2")` and `ligand_sites()`;
  - `interface_mutations()` (SKEMPI, with ΔΔG under `binding_ddg@1`, #83);
  - `variant_tissue_usage(threshold=0.1, *, usage_rule="pext_at_variant@2")`
    and `isoform_tissue_usage(threshold=0.1, *, usage_rule="isoform_exon_usage@3")`
    derive tissue pext from explicit equal genomic scopes (#138). All overlapping
    records must state the same tissue value; bases count once and missing/conflicting
    coverage is separate. Means use resolved bases per tissue. Explicit
    `usage_rule="pext_at_variant@1"` / `"isoform_exon_usage@2"` retain published
    historical behavior. With `gtex=True`, each tissue retains its UBERON/EFO term
    under `gtex_tissue_key@1`; shared ontology terms never merge tissues;
  - Development `explain_sequence_differences(other)`,
    `explain_variant_tissue_usage(threshold=0.1, *, usage_rule="pext_at_variant@2")`
    and `explain_isoform_tissue_usage(threshold=0.1, *, usage_rule="isoform_exon_usage@3")`
    retain the selected versioned views plus
    exact input pins, selected/alternative assertions, locators, rule parameters,
    source labels and gaps. Their explanation rules are respectively
    `sequence_differences_explanation@1`, `variant_tissue_usage_explanation@2`
    and `isoform_tissue_usage_explanation@2`; explicit legacy usage rules retain
    historical explanation `@1`. Cutoffs are finite dimensionless
    numbers in [0, 1]. They neither acquire data nor reconstruct attribution.
    Equal sequence positions establish no residue correspondence or identity.
    Tissue views report genomic scope, rejected inputs and per-tissue coverage;
    they make no pathogenicity or source-completeness claim.
  - `sequence_differences(other)` (the positions where two equal-length sequences
    differ, nothing aligned, `equal_length_positions@1`, #103);
  - `diseases(grouping_rule="disease_grouping@3")` (development: stored identity
    paths plus identifier-scoped coverage, #144). Explicit `@1` and `@2` retain
    historical lookup/path behavior; published 0.14.0 defaults to `@2`;
  - `terms(use)` (what the sources state about a use of the card's knowledge,
    `terms_propagation@1`, #29; also `Deck.terms(use)` and `Deck.admissible(use)`);
  - `bioactivities(include_indirect=False, thresholds=None)`;
  - `ligands(deck, ...)` and `compare_ligands(deck, other, other_deck, ...)`;
    since 0.13.0, keyword-only `counting_rule="ligand_measurement_count@2"` counts
    distinct included groups across matched molecule items; explicit `@1` retains
    the published source-record counter. `bioactivity.records` reports distinct
    included source relationships under either rule. `measurement_counting` records
    the rule, original input pins and counting bases (per side for comparisons);
  - `literature()` and `claims(topic=None)`;
  - `clinical()` (molecules: indications and trials, #81);
  - `knowledge_state()`;
  - `acquisition()` (how the card's statements entered: database, curation,
    extraction, #92);
  - `entities()` and `entity(ref)`;
  - `compare(other, fields=None)` and `compare_knowledge(other, residue_map=None)`.
- **Tables.** `table(view, **options)` gives flat rows; `sabueso.to_dataframe(rows,
  units=None)` needs pandas.
- **Literal extraction (since 0.13.0).**
  - Since 0.13.0, `Card.add_literature_extraction(extraction)` preserves delivered
    literal-rule support and returns a detached reuse event. An older card must be
    explicitly migrated first; different subjects and inconsistent support are refused.
    `Card.literature_intake_traces` returns copies of original runtime events and is
    empty for payload-only readers. Unknown fragment terms cannot enter a terms-profile
    card. `ExtractionStore(path).save(extraction)` preserves the exact original result;
    `records()` reads without credit and `apply(card)` explicitly reuses matching
    records. Neither API uses `CurationStore`.
- **Curation.**
  - `add_literature_assertion(field_path, value, publication, curator, ...)`;
  - `add_literature_relationship(...)`;
  - `add_literature_bioactivity(...)`;
  - `add_literature_engagement(...)`;
  - `add_literature_claim(topic, text, publication, curator, ...)`.
- **Identity and references.** `id`, `snapshot_id()`, `pinned_ref()`.
- **Serialization.**
  - `to_dict()`, `to_json(path)`, `to_sqlite(path, ...)`;
  - `Card.from_dict(data)`, `Card.from_json(path)`, `Card.from_sqlite(path, ...)`.
- **Provenance.** `explain(source_assertion_ids)`: each SourceAssertion's field,
  subject, source, record, version, retrieval and asserted value (#91).
  `explain_literature(publication_ref)` explains the publication's links and both
  legs of structural mention context, with pinned references, qualifier alternatives
  and recorded unlinked PDB mentions (`literature_explanation@1`, since 0.12.0).
  Missing links are `not_on_card`; missing stored support is `partial`.
  Since 0.13.0, `explain_disease(disease_ref)` explains a MONDO disease group at the
  exact card pin (`disease_group_explanation@3` in development; `@2` in 0.14.0),
  following stored association and
  selected annotation-member support, MedGen/MONDO identity and hierarchy steps.
  Stored alternatives/conflicts and whole-card ungrouped context remain visible;
  missing support is `partial`; contradictory targets are ungrouped. Keyword-only
  `grouping_rule="disease_grouping@1"` explicitly uses the historical view and
  `disease_group_explanation@1`, including its exposed lookup ambiguity. No source
  is asked. Explicit grouping `@2` keeps explanation `@2`; development `@3` adds
  `coverage_context` at the exact card pin with original enrichment indexes.
  `MONDO:<seven-digit id>` and `mondo:MONDO:<seven-digit id>`
  select groups, never names or cross-ontology aliases.
  Since 0.13.0, `explain_knowledge_state(knowledge_area=None, knowledge_source=None)`
  explains all state rows or an exact area/source selection at the current or
  loaded historical card pin (`knowledge_state_explanation@1`). Selected fields,
  alternatives/conflicts and counted UniProt relationships have original support;
  absence/curation coverage and matched enrichment reports are classification
  inputs, not negative assertions. Report locators use the pin, field path and
  index; load that card to read them. Related scientific knowledge is separate
  context with per-request membership explicitly `not_recorded`.
  Missing support is `partial`, including fields/relationships whose source can
  no longer be identified. A missing row is `not_on_card`, never evidence of absence.
  No source is asked, mappings rerun, card changed or execution credit added.
  Since 0.13.0, `explain_measurement(measurement_ref)` selects an exact native `REL_`
  record or `MG_` group at this card pin (`measurement_group_explanation@1`). It
  retains actual grouping joins, publication/molecule keys, precision quantities,
  provenance selectors, ambiguity, unresolved-copy and review diagnostics.
  Since 0.13.0, `explain_bioactivity(molecule_ref, include_indirect=False, thresholds=None)`
  selects the exact namespaced item key returned by `bioactivities()`
  (`bioactivity_explanation@1`). Pass the same options as the explained view. Each
  group retains included records, voters, voter classes and copy-only fallback;
  strongest-class selection and discordance remain explicit. Original measurement
  units, ranges, single-point concentrations, thresholds and consistency checks survive.
  Both readers retain exact relationship/assertion pins and original source versions.
  Whole-card grouping/glossary inputs are separate context because candidate
  uniqueness depends on them. Stored identity records have card/field/key locators,
  never invented SourceAssertion membership or identity paths. Missing input support
  is `partial`; a missing item is `not_on_card`, never inactivity. These readers fetch
  nothing, change no card or credit and do not resolve aliases or explain ligand
  deck/site aggregation. The existing scientific rules and stored schema are unchanged.
  Since 0.13.0, `explain_ligand_site(ligand_site_ref)` selects the native `REL_` id
  from `ligand_sites()` (`ligand_site_explanation@1`). It retains the actual
  `annotated_site_overlap@2` result, selected annotation fields, alternatives,
  conflicts, original support, numbering and stored structural-instance context.
  No stored annotation/overlap is not external absence; absent instance data keeps
  `spans_chains=None`, and source relevance statements remain separate.
  Since 0.13.0, `explain_oligomer(*, agreement_rule="interface_site_agreement@2")`
  explains the complete matching `oligomer()` view under `oligomer_explanation@2`:
  actual partner-class and agreement rules, the card
  anchor, source assembly alternatives/methods, interfaces and exact family-site
  members. Relationships/assertions and field/index locators retain the original
  pin, versions and bibliography; selected, competing and conflicting support
  stay separate. Structural support is relationship-level, not invented mapping
  lineage for individual qualifiers. Source aggregate residues are not allocated
  to individual assemblies. Missing/empty assembly data and original source
  request outcomes remain distinct. Missing support is partial; no stored input
  is `not_on_card`, never external absence. Default agreement `@2` requires
  declared UniProt numbering, the exact family sequence reference and 1-based
  indexing, with no conflicting interface numbering/positions (#120).
  The interface must state the card's exact subject; missing positions and
  nonpositive indices prevent comparison even with a numbering declaration.
  A row is `comparable`, `undetermined` or `not_comparable`, with original context
  and reasons. Uncomputed `both`/`family_only`/`observed_only` are None; a computed
  empty set is an empty list. `agreement_state` distinguishes missing inputs,
  no comparable site, partial and fully computed views. Unconfirmed comparisons
  keep the explanation partial. Explicit `agreement_rule="interface_site_agreement@1"`
  in either reader reproduces the legacy integer-only view and
  `oligomer_explanation@1`, including at historical pins. No
  acquisition, credit, alias resolution, schema change or local method execution
  occurs; saved scientific payloads cannot recreate original runtime attribution.
  Since 0.13.0, `explain_ligand(molecule_ref, deck, include_indirect=False, thresholds=None, *, counting_rule="ligand_measurement_count@2")`
  selects the exact SmallMoleculeCard id from `ligands(deck)`
  (`ligand_deck_explanation@2`). Protein and molecule inputs keep distinct pins.
  Actual identity links, class selection, names, measured groups, sites, structure
  flags and deck membership remain visible. Duplicate deck members are retained
  as multiple `items` with partial status, never selected by snapshot/order.
  The deck's native snapshot id and metadata locate its supplied contents; they
  are not invented KnowledgeStore deck references. Load a saved named/pinned deck
  separately for historical reads. Missing support is partial, missing items are
  not absence, and readers acquire nothing or add credit.
  The #118 correction counts distinct included group ids in `bioactivity.measurements`
  and source relationship ids in `bioactivity.records`. Crossing inputs retain both
  sorted id lists, including groups spanning matched molecule/parent items.
  Explicit `counting_rule="ligand_measurement_count@1"` reproduces the published
  numeric counter, including at historical pins; it still adds the new `records`
  field and counting metadata. Neither historical views nor saved cards are rewritten.
  The explanation records its selected count policy alongside nested support;
  measurement identity, class/voter, assay-scope and site policies are unchanged.
  Missing activity-only originals retain the exact `copy_of` pointer with
  `original_not_on_card` in unresolved-copy diagnostics (#117, released in 0.13.0).
  A later provenance or statement join removes that singleton diagnostic. This
  describes final local grouping, not external absence or proof that a named
  original was acquired; original pointers remain in pinned relationship support.
- **Other.** `to_deck()`, `expand(predicate, ...)` (see `sabueso.expand`).

## Deck

- **Build.** `Deck(cards)`, `add(card, basis=None)`, `extend(cards)`,
  `exclude(candidate, reason, by=None)`, `basis(card_id)`.
- **Explain.** `explain(card_id)`: why a card is in the deck, or why it was left out,
  and the operations that produced the deck (#91).
  With `structure_ref="pdb:1SUX"` and the keyword options of `structure_inventory`,
  explains that protein's inventory item, its group or exclusion, named rules and
  relationship-level SourceAssertion support for all group members. Card and item
  references are pinned; no source is asked (`structure_inventory_explanation@1`).
- **Derive.** Each derived deck records the operation that produced it:
  - `filter(predicate)`, `sort(key, reverse=False)`;
  - `intersect(other)`, `difference(other)`;
  - `in_lineage(taxon)`;
  - `group_by(field_path)`, `group_by_rank(rank)`;
  - `expand(predicate, limit=50, options=None, terms=None)` (#91).
- **Views.**
  - `identity_audit()`;
  - `structure_inventory(regions=None, include_fragments=False, group_by=None,
    residue_maps=None, reference=None)`;
  - `unique_names(return_cards=False)`;
  - `summarize(fields)`, `compare(other, key_fields)`, `map(fn)`.
- **Identity and serialization.**
  - `ids()`, `snapshot_id()`, `to_list()`;
  - `to_jsonl(path)`, `to_sqlite(path, ...)`;
  - `Deck.from_jsonl(path)`, `Deck.from_sqlite(path, ...)`.

## Stores

- `sabueso.KnowledgeStore(path)`:
  - `save(card, note=None)` returns a pinned reference, and `load(ref)` reads it;
  - `history(card_id)`, `card_ids()`;
  - `source_assertion(ref)`, `relationship(ref)`, `relationships(object_ref=None,
    predicate=None, subject_ref=None, all_revisions=False)`;
  - `save_deck(deck, deck_name, note=None)`, `load_deck(name_or_ref)`,
    `deck_history(name)`, `deck_names()`;
  - `save_packet(packet, packet_name, note=None)`, `load_packet(name_or_ref)`,
    `packet_history(name)`, `packet_names()`;
  - `import_card_table(path, table="cards")`;
  - `as_of(ref, when)` and `revision_as_of(ref, when)`: the card, deck or packet as
    stored by a date, or None; `changed_since(ref, when)` for a card or a packet (#91).
- `sabueso.RetrievalArchive(path)` (#100), three contexts: `recording()` (every answer
  a source client receives is archived), `reusing(max_age)` (answers archived within a
  `datetime.timedelta` are used instead of asking again), `replaying(of=None)` (the
  network is never asked; `of` a card replays its build). A card built inside lists
  its answers in `quality.retrievals`. Also `get(ref)`, `find(method, url,
  request_body, max_age=None)`, `sources()` (answers per source, with what their
  licence allows: `sabueso.core.terms.retention`), `stats()`. `NotArchivedError` when a
  replay meets a request the archive does not hold. `Card.explain` links a statement to
  the answers its source gave the build.
- `sabueso.mirrors` (#100): `install(source, release="latest", mirror_dir=None,
  from_file=None, md5=None)`, `status(mirror_dir=None, check=False)`, `update(source,
  policy="manual"|"notify"|"auto", keep=2)`, `remove(source, release)`,
  `using(mirror_dir=None, mode="mirror_first"|"offline", releases=None)`. Sources:
  `bindingdb`. `OfflineError` when a request is made offline.
- `sabueso.CurationStore(path)`: `save(card)`, `apply(card)`, `records()`,
  `retract(source_assertion_id, reason, curator)`, `entities_named(name)`.
- `sabueso.migrate_card(data, store=None)` and `sabueso.refresh_card(card,
  curations=None, store=None, **options)`.
  Development refresh restores declared source/data requests and their saved
  parameters, including failed/unqueried requests. Explicit options override them;
  `None` disables dictionary options and `False` disables flags. Conflicting or
  missing essential known-route parameters raise `StorageError` before acquisition
  unless overridden. `quality.migration[-1].request_restoration` reports the
  restoration basis, unrecorded historical parameters and unsupported selectors.
  Unsupported routes are reported and omitted; refresh does not claim complete
  source portfolio replay. `store=` saves the original and refreshed states.
- Files: `save_card_json`, `save_card_sqlite`, `save_deck_jsonl`, `save_deck_sqlite`.

## Source access (`sabueso.tools.db`)

Raw records in a provenance envelope, one client per source (`SOURCE_ACCESS.md`):

- `uniprot.get_entry`, `rcsb.get_entry`, `pdb_ccd.get_components`;
- `pdbe_kb.get_ligand_sites`, `pdbe_kb.get_interface_residues`;
- `interpro.get_site_residues`, `alphafold.get_prediction`;
- `chembl.get_bioactivities`, `chembl.get_molecules`;
- `bindingdb.get_affinities`, `pubchem.get_compound`, `pubchem_bioassay.get_assays`;
- `unichem.get_compound`, `stringdb.get_partners`;
- `ncbi_taxonomy.get_taxon`, `ncbi_gene.get_gene`;
- `skempi.get_mutations`, `mondo.get_term`, `medgen.get_concepts`;
- `europepmc.get_mentions(identifier, limit=5000)` and
  `europepmc.get_annotations(article_ids)`: bibliography by explicit accession, or
  located accession annotations for explicit MED/PMC articles. The latter returns
  source-native sections, providers, tags and quote fragments without enriching cards
  or extracting scientific claims; article terms govern fragment storage (#92);
- `gnomad.get_variants`, `gnomad.get_transcript_variants`, `klifs.get_kinases`,
  `klifs.get_structures`, `gpcrdb.get_receptor`, `sabdab.get_complexes`, `oma.get_orthologs`, `uniref.get_clusters`.

Each source also has an `Online<Source>Client` and a `Fixture<Source>Client`. The legacy
`create_*_card_*` builders are deprecated and will be removed before 1.0.

## Errors

Defined in `sabueso/core/errors.py`:
- `SabuesoError`, the base;
- `ResolverError`, `SchemaError`, `StorageError`, `ConnectorError`;
- `RecordNotFoundError`;
- `MissingKeyError`, for a source that answers only with a personal key (#86);
- `ArgumentError`, a `ValueError` for refused arguments.

Diagnostics are SMonitor signals with stable codes (`DIAGNOSTICS.md`).

## Stability

- The package is pre-1.0. A breaking change is announced in the release notes, and
  deprecated names are kept until 1.0 when possible.
- Stored cards follow the card schema's versioning policy (`SCHEMA.md`), and older
  cards are read or migrated (`migrate_card`).
- The reference forms are provisional until uibcdf/moli#3 (#53).

## Explicit article metadata (since 0.13.0, #92/#108)

`tools.db.europepmc.get_article(identifier, client=None)` returns the standard source
envelope for pubmed:/pmc:/doi: identifiers, with a detached acquisition trace. Its core
bibliographic projection excludes abstract/full text, preserves native identifiers,
author records, journal/pages/dates and licence declarations, and exposes matching
alternatives/truncation. `extract_literature_mentions(..., article_metadata=envelope)`
explicitly binds one complete source-stated publication identity with separate database
support under `article_metadata_binding@1`. Original fragment assertions/rule/unknown
rights stay unchanged. ExtractionStore, intake and refresh preserve original support;
literature views/explanations and exact packet support retain alternatives/citations.
`Card.terms` and pinned packet terms expose optional `declared_article_terms`; neither
the native licence literal nor an open-access flag grants supplied-fragment rights.

## Development ClinicalTrials.gov reference access (#108/#127)

`sabueso.tools.db.clinicaltrials.get_study_references(identifiers, client=None)`
accepts one NCT id or a nonempty list through ArgDigest and returns the standard
source envelope (`kind: study_references`, `record: {studies, missing}`). Online and
fixture clients expose `study_references(nct_ids)`. Native reference modules are
returned independently of clinical card fields. Both existing study lookup and
this explicit lookup attach original acquisition/portable attribution sidecars;
no linked target is consulted. Explicit Europe PMC article access can enrich the
enclosing workflow bibliography, retaining collective authors as literal CSL names.
This recovered API is delivered in 0.14.0 (#134), with exact-source and installed
Conda qualification. The historical section anchor remains stable. Native access
remains separate from card enrichment, complete private-consumer acceptance and
current live provider health.

## Development bound native originals

`SnapshotAlphaFillClient`, `SnapshotGlyGenClient`, `SnapshotSIFTSClient` and
`SnapshotLigysisClient` accept `(path, *, source_metadata, expected_sha256=None)`
for the existing public `get_*` reader's `client` argument. They cover metadata,
protein detail, mappings, result-page HTML and structure-mapping JSON respectively.
All support gzip. Source, kind, normalized exact query and unknown scientific
revision are checked before file access; the native reader fixes JSON/HTML format
and validates native identity/shape before output. Declared time/terms are caller
context, not independently observed retrieval or permission. Original file hash
covers compressed bytes before decoding. These clients add no automatic card
admission, schema/enricher, cross-source identity join or provider adoption.

### Native UniProt annotation extension (development 0.3.13)

Existing protein card construction/refresh now retains five additional native text
kinds and eight positional feature kinds, including domains, under the published
0.3.13 schema (release 0.14.0). Public signatures and acquisition routes do not change.
`Card.get_residue` preserves source endpoint modifiers and rejects known UniProt
sequence-revision mismatches for placement; retained original features and ECO
support remain available. Source cautions and similarity do not create quality or
identity findings. Migration records the optional refresh gaps. See `SCHEMA.md`,
`FIELD_PATHS.md` and `tests/core/test_uniprot_domain_recovery_offline.py`.
