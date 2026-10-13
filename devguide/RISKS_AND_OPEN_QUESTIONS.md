# Sabueso — Risks and Open Questions

Development tissue rules now require explicit coordinate scope and report
per-tissue resolved/missing/conflicting coverage (#138). Explicit legacy rules
retain their known assembly/chromosome and duplicate-count limitations. Old cards
without variant coordinate context remain unknown under the new rule; migrating
never synthesizes context. Conditional means over resolved bases must be read with
coverage, never as complete gene/tissue expression or pathogenicity. Source-side
coordinate/release correctness, installed delivery and human scientific usefulness
remain separate from the bounded regression scope. Code `3bc1c53` passes 15/15
exact-SHA CI; [the receipt](pending_proposals/comparative_tissue_scope_checkpoint.json)
retains the qualified source and limits. Development #139 replaces the incomplete
refresh routing list with declared selectors and saved arguments; code `ff32cb6`
passes 15/15 exact-SHA CI and 5,896 local-original cases under separate
[qualification](pending_proposals/refresh_request_scope.md). Historical missing
parameters and unsupported selectors remain explicit limits; new acquisitions do
not promise exact old requests. See [the correction](pending_proposals/comparative_tissue_scope.md).

## Risks
- **Licensing/Terms**: Some sources (DrugBank, eMolecules, ChemSpider) have licensing constraints that may affect redistribution and caching.
- **API Rate Limits**: Public APIs may rate‑limit or change formats.
- **Data Heterogeneity**: Conflicting values across sources require robust conflict handling.
- **Clinical Data Volatility**: Clinical information changes more frequently than core physchem data.

## Architecture Risks (General)

- **Comparative execution and bibliography scope** (#108): development observes
  three ordinary Card views only inside an explicit attribution context, in
  [separate original execution records](pending_proposals/comparative_operations.md).
  Selected input-field support is not row-level mapping or source-request lineage;
  original record labels are not independently verified database releases. Plain
  views, explanations and saved readers remain inert. Source qualification is in
  progress; full bibliography, other result scopes and installed/human acceptance
  remain separate.

- **Upstream prerequisite classification**
  ([#142](https://github.com/uibcdf/sabueso/issues/142),
  [#143](https://github.com/uibcdf/sabueso/issues/143)): development Open Targets
  uses an unqueried gate before client construction when Ensembl gene identity is
  missing; [source qualification](archive/open_targets_prerequisite.md) passes
  at `94ad9eb` with 6,092 local-original tests and 15/15 CI.
  [Its receipt](archive/open_targets_prerequisite_checkpoint.json) retains the limits.
  The six built-in gates use `RequestPrerequisiteMissing`, with public per-source
  card, native-outcome and historical refresh regressions;
  [source qualification](archive/source_prerequisites.md) passes at `c45af44`
  with 6,143 local-original cases and 15/15 CI.
  [Its receipt](archive/source_prerequisites_checkpoint.json) retains the limits.
  Neither an upstream missing input nor an old saved classification establishes
  native source absence. Actual queried protein-binding
  outcomes and stored historical pins retain their own scope.
- **Derived disease identity coverage**
  ([#144](https://github.com/uibcdf/sabueso/issues/144)): `disease_grouping@1/@2`
  treat any MONDO enrichment record as proof that identity was queried. A synthetic
  blocked MedGen-only condition can be labelled `no_stated_equivalence` despite
  no source query. Development grouping/explanation @3, coverage @1 and packet
  mapping @7 correct that inference while retaining the historical selectors/pins.
  [Source qualification](archive/disease_identity_coverage.md) passes at `cf5900d`
  with 6,182 local-original cases and 15/15 exact-source CI;
  [its receipt](archive/disease_identity_coverage_checkpoint.json) retains the limits.
  Missing historical identifier scope remains unknown. Exact diagnostics describe
  completed source outcomes, and unscoped failed requests describe access context.
  Full installed delivery and consumer-owned usefulness remain separate.
  The #143 source-gate correction remains a separate source checkpoint.
- **Comparative response integrity and revision/operation scope**
  ([#137](https://github.com/uibcdf/sabueso/issues/137), #108/#91): the original
  0.14.0 online OMA/UniRef/gnomAD/GTEx routes can misclassify missing JSON
  envelopes or unanswered fields as empty/absent knowledge. Development guards
  validate the consumed containers and complete requested consequence aliases;
  public synthetic regressions cover failure/absence and card knowledge states.
  Code `09cf912` passes 15/15 exact-SHA CI and governance; the
  [source receipt](pending_proposals/comparative_response_contracts_checkpoint.json)
  preserves both local/public scopes. This is not a complete native field validator
  or new installed delivery.
  [Development OMA observation](pending_proposals/oma_observation.md) is
  source-qualified at `593ba76` with 6,031 local-original cases and 15/15 CI;
  [its receipt](pending_proposals/oma_observation_checkpoint.json) retains the limits.
  It separates OMA statements from UniProt name bindings, exposes revision/selection gaps and retains source-stated match gates.
  [Development gnomAD observation](pending_proposals/gnomad_observation.md) is
  source-qualified at `682e226` with 6,085 local-original tests and 15/15 CI;
  [its receipt](pending_proposals/gnomad_observation_checkpoint.json) retains the limits.
  It records query-versus-native scope
  and completed alias batches; missing local inputs are unavailable, and missing
  gene prerequisites no longer claim source absence (#141). Derived-operation
  observation, complete bibliography and strict cost/deadline limits remain open.
  [Development UniRef observation](pending_proposals/uniref_observation.md)
  exposes individual page releases, caps and partial failures; the client's
  compatibility version is not proof of coherent pages. Code `c6cb0e3` passes
  15/15 source CI; [the source receipt](pending_proposals/uniref_observation_checkpoint.json)
  retains its exact scope. Published 0.14.0 retains the unbounded empty/cyclic
  pagination defect. The subsequent [development correction #140](archive/uniref_pagination.md)
  detects repeated exact URLs and limits member operations to 100 logical pages;
  source `3a47490` passes 5,984 local-original cases and 15/15 exact-source CI.
  [Its receipt](archive/uniref_pagination_checkpoint.json) retains the qualification
  scope. Shared retry limits and per-attempt timeouts
  do not provide a strict wall-clock deadline. [Development GTEx observation](pending_proposals/gtex_observation.md)
  records requested dataset labels separately from unknown native revisions;
  one returned page does not prove complete dataset coverage. Development pinned
  sequence/tissue explanations now have an
  independent public fixture reader; [their scope](pending_proposals/comparative_explanations.md)
  includes the versioned #138 scientific correction; installed/human acceptance remains separate. In particular,
  gnomAD's existing pext release label is client-declared; it must not be presented
  as an independently verified native response revision. Keep query dataset,
  source-reported release and service version bases separate in the next #108 slice.
- **Published SQLite lifetime and post-release integrity delivery**
  ([#133](https://github.com/uibcdf/sabueso/issues/133)): the original 0.14.0
  artifact retains the unclosed legacy card/deck connections reported during its
  qualification. Development main explicitly closes the owning connections;
  eight regressions, full local-original tests and 15/15 exact-SHA CI pass.
  Fatal SQLite/unraisable warning guards remain active. See the
  [qualified receipt](pending_proposals/sqlite_lifetime_checkpoint.json).
  GTEx prerequisite classification (#135) and shared-source attribution (#136)
  are also corrected and exact-SHA qualified on main, outside that published
  artifact. A future installed artifact needs its own staging/platform gates;
  historical receipts and stored reports stay fixed.
- **Recovered capabilities need real consumer revalidation**
  ([#132](https://github.com/uibcdf/sabueso/issues/132)): public fixture tests and
  independent SDK journeys establish bounded support/persistence behavior, but
  not the usefulness or completeness of current private Python/Jupyter workflows.
  Revisit those workflows after exact-SHA CI, with original results/receipts kept
  private and the checkout read-only. Route generic findings to the owning
  component or shared MOLI contract rather than expanding sources by count.
  The bounded follow-up passes original cells, saved readers and answer replay;
  NCBI Taxonomy operation observation is implemented. The earlier 942 MiB counter
  predates SDK imports; matched Linux process sampling, including profiler overhead,
  shows about 132/129 MiB live/replay. This does not establish a 942 MiB SDK allocation
  or complete consumer acceptance. See the
  [bounded report](pending_proposals/private_consumer_revalidation.md#taxonomy-and-memory-follow-up).
- **Disease deck support/observation gaps** (#91/#108/#112): the independent
  disease example retains exact card/group support; published rules `@1`
  store membership as metadata without supporting SourceAssertion/input pins.
  A matching card nearby cannot reconstruct that membership's original support.
  Rules `@2` preserve native rows/order, original input and member
  identity with atomic/portable support; this bounded behavior is delivered in
  qualified 0.14.0. Terms include embedded sources. Published 0.14.0
  `disease_deck_admission@1` supports whole-context
  admission and unchanged member filtering; shared unknown/restricted terms refuse
  rather than filtering native context. Finer filtering by terms of use and per-record raw-content
  licensing remain #29; resolved alternatives never license retained raw copies.
  The #126 integrity fix delivered in 0.14.0 checks native candidates against the actual member's
  source-stated identifiers; resolving pins alone does not establish identity.
  MONDO term/equivalence observation is delivered in 0.14.0, with original index/file
  origins and bibliography. Open Targets/Orphanet and disease-deck build observation
  are also delivered, including DISEASES/ClinVar/MedGen access (#125).
  Native ChEMBL indication references retain exact observed occurrence scope and
  portable pointer citations; linked targets are not separately consulted.
  Complete underlying workflow bibliography remains pending. Source row totals, candidate limits and successfully built cards
  are different counts; fixture-only card failures must not become external absence.
- **MONDO published release integrity** (#123): 0.13.0 can change scientific retrieval
  times during index/archive reuse, and interpret obvious non-OBO input as an absent
  term. Both defects are corrected and delivered in qualified 0.14.0. Existing stored
  times cannot be repaired without original receipts. Pre-existing unobserved indexes
  retain explicit original-time/origin gaps rather than invented history. The client
  document sanity guard is not a complete OBO validator.
- **Disease-source published integrity** (#124): Orphadata 0.13.0 can change
  scientific times during index reuse. Malformed/unrelated XML, incomplete Open
  Targets fields and missing fixtures may be misclassified or leak raw errors.
  Local corrections keep original file time, require native answer fields, refuse
  mixed-version/count page merges, and distinguish invalid/unavailable from absent.
  The corrections are delivered in qualified 0.14.0; stored times require original
  receipts to repair.
  Orphadata lookups cover SwissProt-indexed rows, not every native gene.
- **Disease lookup published integrity** (#125): older DISEASES cached-index
  times, exhausted fixture channel iterables, missing/invalid NCBI result fields,
  skipped ClinVar fixtures and mixed fixture versions can misstate scientific
  scope. MedGen can choose a UID by response order or infer absence from a capped
  search. The guards and acquisition regressions are delivered in qualified 0.14.0.
  Older DISEASES disk caches lack original receipts;
  their history is not reconstructed. Incomplete/ambiguous MedGen lookup now fails
  explicitly, rather than adding unsupported identity to a card.
- **Packet terms scope and registry history** (#29): `packet_terms@1` supports
  `packet_aspects@6` only. Historical mappings need their own scope adapter and are
  refused by that query, without changing packet readability. Terms use the current
  packaged registry and review dates, not a historical registry snapshot. Stored
  statement support is available, but exact mapping/qualifier lineage is not always
  recorded; disease grouping includes broader MONDO/MedGen identity/hierarchy context.
- **Required pipeline attribution / remaining coverage** (#108, moli#36): Ackredit's
  portable API is publicly delivered as 0.9.0/py_0 for Python 3.11–3.14. Metadata,
  environments and recipe adopt `>=0.9.0`; CI uses public Conda, and installed gates
  pin the qualified public file/hash. The public-dependency blocker is resolved.
  Independent receiving tests on all four Linux minors pass with the planned public
  core pins. The current editable satisfies the published minimum; Ackredit #81
  records the earlier mismatch and receiving confirmation. The latest shared
  environment check has unrelated
  Amber/preparation dependency conflicts; see `CHECKPOINT.md`, Resume here.
  Published 0.13.0 adapters observe packet composition and built-in UniProt,
  Europe PMC, RCSB, ChEMBL, PubChem/BioAssay, BindingDB, CCD, UniChem, PDBe-KB,
  AlphaFold DB and InterPro operations within their declared boundaries.
  Other sources/custom clients, further result types and full
  bibliography remain gaps. Original runtime JSON must be explicitly saved;
  payload-only readers cannot reconstruct earlier execution. MOLI ProjectRecord/
  Recorda routing, correlation and strict recording policy remain platform-owned
  work. The 0.13.0 scope (#121) does not claim complete pipeline traceability.
  Failed tracking can leave partial workflow credits; result records retain
  failure status and host support. The published 0.12.0 (#110) and 0.13.0 (#121)
  receipts record qualified archives, unchanged promotion, fresh public installation
  and identical-tag Zenodo archival. RCSB's primary citation fields may be incomplete;
  gaps and different stated metadata forms remain explicit, without runtime enrichment.
- **SourceAssertion growth**: preserving all values can create very large cards and stores.
- **Mapping fragility**: changes in source APIs can break field mappings.
- **Ambiguity**: input resolution may produce multiple valid entities.
- **Ops drift**: unstable ops contracts can break tools and downstream integrations.
- **Schema churn**: frequent schema changes can break cards, tools, and mappings.
- **Recorded Sabueso version in development environments**: `sabueso.__version__`, and
  therefore the `sabueso_version` of derivation records, comes from the installed
  distribution's metadata. If the imported code is another copy (a worktree on
  `PYTHONPATH`, or a stale `sabueso.egg-info` at the repository root), cards record a
  version that did not write them. Published packages are not affected. Frozen cards are
  therefore built from the published package (#42).
- **Concurrent curation stores** (uibcdf/sabueso#48): a `CurationStore` is rewritten
  whole on every save. The write is atomic (temporary file, then replace), but two people
  saving to the same file at the same time lose the first writer's new records: the last
  writer wins. Until the native store (#27) gives records a transactional home, use one
  store per curator or merge through version control.
- **Stored curation values** (#48): records keep the value in its stored form, so
  re-applying gives the same id. If a field's item shape changes in a new schema version,
  re-application raises instead of silently changing the id. Stores then need a
  migration.
- **Previously exported extraction provenance** (#105): before the export guard,
  `CurationStore` could export a rule/model extraction without its acquisition and
  replay it as human curation. Those JSONL records cannot reconstruct the omitted
  provenance automatically. Check the original acquired card state before accepting
  or reapplying such a record; the guard prevents new exports of this kind.
- **Snapshots of rebuilds** (#7): a snapshot id covers everything a card stores,
  `retrieved_at` included. Two builds from unchanged sources on different days are
  therefore two snapshots. That is exact, since what was read on each day is part of the
  record, but it is not "same knowledge, same id". If consumers need that, a second
  digest that leaves out observation times can be added next to the snapshot id. It
  must never replace the snapshot id.
- **Canonical JSON is the snapshot contract** (#7): the id depends on how Python's
  `json` writes numbers and on the stored form of the card. A change to `to_dict()`
  changes the ids of new snapshots, never of stored ones, and it goes with a card
  schema version (#42). Floats use the shortest representation that round-trips, and
  NaN is refused.
- **Retention in the knowledge store** (#27): snapshots and rows are never deleted. A
  store that is saved often grows, although identical rows are stored once. Pruning
  would break pins that consumers may hold, so it needs a retention policy agreed in
  uibcdf/moli#3 before it exists.
- **Queries match references as written** (#27): `KnowledgeStore.relationships` does
  not use the glossary of entities (#52). A molecule stated as `chembl:…` in one card and
  as `pdb.ligand:…` in another is found only under each reference. Resolving through
  the glossary is the next step if cross-source queries become common.
- **Knowledge store format** (#27): the file states its format, 2 since #99, and
  upgrades format 1 in place. A change to its tables needs a new format and an upgrade,
  like the card schema (#42, #51).
- **Deck operations that cannot be recorded** (#58): `Deck.filter(predicate)` records
  the operation but not the Python predicate, and marks it `"reproducible": False`. A
  deck derived that way can be cited through its pinned reference, but not rebuilt from
  its parent. Prefer `in_lineage`, `group_by`, `intersect` and `difference` when the
  derivation must be reproducible.
- **One writer at a time**: SQLite serializes writers, which suits a local knowledge
  store. Many concurrent writers would need another backend.
- **ChEMBL ranges are untested against real data** (#37): ChEMBL_37 states none, so
  the mapping is guarded by a constructed record. If a release starts stating ranges,
  check how it sets `standard_relation` for them, and add a real fixture.
- **Uncertainty on section fields** (#37): only bioactivity measurements can carry
  one. A curated scalar field (for example a stated molecular weight ± error) would
  need the same node shape at its field path, and a schema version.
- **Uncertainty in the classification** (#37): an interval that spans a threshold is
  still classified by its central value. If that is misleading for a project,
  classifying the whole interval, as for ranges, is a new rule version, not a change to
  `@3`.
- **Identity audit thresholds** (#55): the near-identity bound (2% of positions,
  equal lengths, no alignment) is a flag for review, not a biological criterion.
  Proteins with indels, or strain variants above 2%, are not flagged. A position-level
  comparison through a MolSysMT alignment would replace it if needed. `same_gene`
  joins isoforms, fragments and alleles, which a reader must tell apart.
- **Strain relations by name** (#55, #67): cards enriched with NCBI Taxonomy are
  related exactly. Resolver candidates and cards without that enrichment are still
  related through UniProt names, and each finding says so (`organisms: names`). If
  that proves unreliable, enrich candidates with NCBI Taxonomy in the resolver.
- **NCBI Taxonomy has no data release** (#67): the Datasets API states its software
  version, not a taxonomy release, so `annotations.taxonomy` records no source version.
  Taxonomy changes (merged or renamed taxa) show up as a different snapshot, not as a
  new release.
- **Scheme-1 curation records** (#62): a statement dropped by the old collision cannot
  be recovered from a store. Stores stay mixed, with scheme-1 and scheme-2 records,
  until every entity is applied or saved once.
- **Card comparison scope** (#59): `compare_knowledge` takes protein cards, and
  compares relationships by their objects only, not their qualifiers. Comparing
  measured values per molecule is `compare_ligands`. Comparing two small-molecule
  cards needs its own rules (stereochemistry, salts, tautomers) and is not offered.
- **Profiles do not include predicted structures** (#57): `structural_baseline@1` was
  published before models existed, and profiles never change. If a baseline with
  models is wanted, add `structural_baseline@2`, never an edit of `@1`.
- **Model versions change** (#57): AlphaFold DB replaces models (v2 to v6 so far). A
  card records the version it saw, and a snapshot pins it. The coordinates of an older
  version may no longer be served, which MolSysMT consumers should expect.
- **Engagement vocabulary** (#61): the mechanisms (`covalent`, `non_covalent`,
  `allosteric`, `interface_disruption`, `unspecified`) are Sabueso's, not an ontology.
  If Praxis or Nextia need a shared vocabulary, raise it in uibcdf/moli, and map these
  terms onto it with a new schema version.
- **Numbering of engaged residues** (#61): papers often number residues from a
  construct or a structure, not from UniProt. The residue-code check catches most
  slips, but it cannot catch a shift that lands on the same amino acid. Curators
  should give the code whenever the paper does.
- **UniChem lags behind BindingDB** (#66): recent monomers (5 of the HsTIM records,
  from a 2024 paper) are not in UniChem yet, so they cannot be anchored and are
  reported as `molecule_unresolved`. They are not grouped, even when ChEMBL states the
  same values.
- **One UniChem request per monomer** (#66): fine for tens of records, too slow for
  targets with thousands (kinases). Use UniChem's source-to-source mapping files, or
  batch lookups, before enriching such targets by default.
- **BindingDB records state no origin through REST** (#66): the provenance layer cannot
  tell a ChEMBL import from BindingDB's own curation. The bulk download states it. It
  also decides the licence (CC BY-SA 3.0 for imports), so the REST records are treated
  as CC BY-SA 3.0.
- **Censored values are not reviewed** (#66): pairs with `>` or `<` values and
  different molecules are frequent within one paper and are not listed. A real
  discrepancy among censored values goes unnoticed.
- **PubChem standardisation** (#68): a copy's CID can lose the depositor's
  stereochemistry or salt form. Within a named assay, grouping by connectivity is
  accepted only when it leaves one candidate, and it is flagged; seven TcTIM copies find
  no molecule of their assay at all, and stay unresolved.
- **Pointers can be large** (#68): a copy can name an assay with thousands of
  activities, all fetched from ChEMBL. That is fine for curated assays; screening
  assays deposited through ChEMBL may need a limit.
- **Refresh options are rebuilt from enrichment records** (#51): options that leave no
  enrichment record (a resolver preference policy, the name query a card came from)
  are not reproduced. A refresh resolves the card's anchor directly, so the entity
  cannot change, but its options may. `refresh_card(**options)` can override them.
  Development #139 retains supplied protein enrichment arguments and restores
  declared selectors even after failures. Older missing parameters still use
  current defaults and are reported. Unsupported selectors are omitted explicitly;
  conflicting known routes require an override before acquisition. Refresh may
  therefore remain incomplete as a source portfolio even when resolution succeeds.
- **Gaps of qualifier-level additions** (#51): `SCHEMA_CHANGES` names relationship
  qualifiers by their relationship, so an added qualifier (for example `isoform`) is
  reported only when the relationship itself is absent. The exception is a qualifier
  that every relationship fetched with its schema has (`has_structure.construct`,
  marked `qualifier` in `SCHEMA_CHANGES`). Its absence from every relationship of the
  predicate is a gap. A card whose older structures were never re-fetched is still
  counted as holding it once any structure has it.
- **Structural state is only as good as RCSB's annotations.** `structure_state@1` calls a
  structure `mutant` when RCSB states an engineered mutation, and `differs` when the
  sequences differ without one. A mutation the depositor did not annotate, in a region
  the entity alignment does not cover, is invisible. The `subject_of_investigation`
  flag decides `ligand_of_interest`. It is missing for some older entries (`unstated`)
  and can mark a buffer component. The inventory groups by these states; it must never
  be read as a recommendation.
- **Relationship-level support is not qualifier-level lineage** (#91). Inventory
  explanations preserve all supporting SourceAssertions and expose the pinned card's
  sequence context. RCSB mappings did not record which exact selected sequence and
  length they read, or a support list per qualifier. The explanation states this
  boundary; reproducing the original mapping would require recorded mapping inputs.
- **The rank vocabulary is Sabueso's copy of NCBI's.** `group_by_rank` refuses a rank
  outside `NCBI_RANKS` (`_private/argdigest/argument/rank.py`), so that a typo is not
  answered with an empty grouping. A rank NCBI adds later (as "realm" and "cellular
  root" were) is refused until it is added there.
- **The documentation is not built in CI.** A broken page or a malformed docstring is
  caught only by the local docs gate (`TESTS.md`). The user guide had drifted far behind
  the API by 0.4.0: stale selection rules, a wrong release badge, no page for
  `resolve`. A docs job in CI, building with `-W`, would prevent it.
- **A support library can change a behaviour in a minor release.**
  - SMonitor 0.17.0 (2026-09-26) began skipping its own frames in `stacklevel`
    (uibcdf/smonitor#23). Sabueso's frame count then double-skipped, and warnings
    pointed into pytest.
  - Main requires SMonitor >= 0.17.0 and counts accordingly.
  - Published Sabueso 0.4.0 declares `smonitor>=0.16.0`, so a fresh install gets 0.17.0
    and attributes its warnings to the wrong line. This is cosmetic: messages, records
    and results are unchanged. The next release fixes it.
  - Lower bounds alone do not protect a published release from such changes. Upper
    bounds, or a release test against the newest support libraries, would.
- **RCSB answers can change from day to day.** On 2026-09-26, RCSB failed server-side
  on the per-chain data of some entries (1KLG, 2V5B, 1KLU), intermittently. Entries
  are now kept as `partial` (#74). Two runs a day apart can still differ in what they
  hold, and a refreshed fixture can be partial. Fixtures are refreshed only from
  complete answers.
- **One request per PDB entry.** `structures="all"` fetches entries one by one. A
  protein with hundreds of entries (kinases, proteases) will be slow and may meet rate
  limits. RCSB GraphQL accepts `entries(entry_ids: [...])`; batch when that is felt.
- **Claims can hide structure** (#43): free text is easy to add and cannot be
  compared, so claims could pile up where a structured field should exist. Review the
  topics periodically, and promote a recurring topic to a field.
- **Names are not identities.** UniProt's synonyms, abbreviations and gene names are
  recorded per entry as that source states them. Short names are ambiguous across
  proteins ("TIM" names both a triosephosphate isomerase and unrelated protein
  families), and gene symbols repeat across organisms. No rule may join two entities,
  or anchor a resolution, by a shared stated name. Resolution by name stays with the
  source's search and the identity audit. Curated synonyms anchor only through a
  curation store, and a name curated for two entries is ambiguous. If a view of shared
  names across a deck is ever added, it must report the coincidences, never merge them.
- **A deletion is read from an empty field** (#80). UniProt's JSON writes "Missing" as an
  empty `alternativeSequence`, and nothing else says so. If UniProt changes that
  convention, a deletion could again read as an unspecified change, or a change as a
  deletion. It was checked against the text format on 2026-09-27, and
  `test_isoforms_offline.py` holds it on frozen entries. Recheck when fixtures are
  refreshed.
- **Secondary structure out of context.** UniProt reads each segment from one PDB entry,
  and mixes entries along one sequence. A consumer that paints it on another structure,
  another state or an isoform shows what those structures do not state. The item keeps
  `structures`, and each structure now carries its own per-chain assignment (RCSB,
  since 0.3.6). Assignments by different programs (PROMOTIF, DSSP, authors) can
  disagree at segment ends; `assigned_by` says which one a chain has.
- **Packet size** (#71). A packet holds the views' output whole. Measured live on
  2026-09-27 for the HsTIM/TcTIM pair: about 0.8 MB of JSON with ChEMBL bioactivities,
  and about 1.2 MB with ChEMBL, BindingDB and PubChem BioAssay (0.8 MB of it TcTIM's
  bioactivities). A protein with thousands of measurements will be much larger. If that
  is felt (MOLI Agent's context, storage), facts may become summaries with references
  to the full views, in a new packet version.
- **What the content-equivalence id leaves out** (#71). It drops `retrieved_at` and
  `sabueso_version` only. A new field that records when or by what something was built
  would make unchanged knowledge look changed, until it is added to `NOT_KNOWLEDGE`
  (`sabueso/core/packets.py`). On 2026-09-27, cards built live held no other time value
  than `retrieved_at` (dates such as a PDB deposit are knowledge, and stay). Recheck
  when a field is added.
- **The packet contract may change** when uibcdf/moli#22 is agreed. Stored packets
  state their format (`knowledge_packet@2` since #88; `@1` is still read), so a change
  is a new version, and revisions of different formats are never compared.
- **Whole-release sources** (#83). PHI-base's first load parses a 134 MB JSON: about
  30 s and 750 MB of memory once per process without a cache directory. A larger
  release, or several release-based sources, would need streaming parsing or a
  prebuilt index. The cache directory is the mitigation today.
- **Terms not stated** (#84). VEuPathDB and TDR Targets state no reuse terms that were
  found. Until they answer, their data is read live only, never committed as fixtures or
  redistributed.
- **Sources that refuse unnamed clients** (#82). DISEASES's download server and
  Reactome's Content Service answer 403 to Python's default user agent. Since #86 every
  client names Sabueso through one helper (`tools/db/_http.py`), and a test keeps it so.
- **Large default answers** (#88). By default every source is asked for everything, up
  to 5000 items. For heavily studied human genes this means thousands of
  SourceAssertions per card: Open Targets holds 5198 associations for TP53, and ClinVar
  16094 records for BRCA1, about a minute to fetch 5000 of them. Card size, store size
  and packet size may grow past what views and MOLI consumers expect. #88 lists what to
  watch and the options.
- **Heavily studied targets** (#98). Measured live for EGFR on 2026-09-30: ChEMBL
  holds 58,847 activities (~7 s per 1000-row page, server side), BindingDB 32,346
  records of 16,463 monomers (each needing a UniChem lookup), PubChem 6569 assays, RCSB
  393 entries (~175 KB of card each). BindingDB and PubChem BioAssay ignore the 5000
  ceiling. A card with every source would exceed 100 MB and take hours. #98 lists the
  batched queries the sources offer, and the order of work.
- **Store growth across rebuilds** (#99, addressed in 0.8.0). Format 2 keeps
  `retrieved_at` out of a SourceAssertion's row, numbers states and rows with integers,
  and compresses: a card saved again with unchanged knowledge adds about 0.1 MB instead
  of a whole copy. What still grows with each revision is one membership row per
  statement; a retrieval archive (#100), when used, adds the responses (about 23 MB
  compressed for one full pilot run, 2026-10-01).
- **Transcript versions** (#85). gnomAD states the version of the canonical transcript
  it annotates (gnomad_r4 uses GENCODE 39), and UniProt cross-references its own. They
  can differ when either updates, and then the same id may encode another protein.
  The residue check guards each placement, and the item records gnomAD's version; the
  versions are not compared yet.
- **Variants on transcripts UniProt does not state** (#85, closed; follow-up #102). After asking gnomAD for the
  canonical transcript, 1,682 of 52,928 protein changes over 22 human proteins remain
  unplaced for this reason (`transcript_not_canonical`). Checked one by one, none is
  coding on the canonical transcript: they are intronic or in its 3' UTR, or outside
  it. The card still says only that the transcript is not canonical. gnomAD's variant
  query would state which (25 variants per request, within its rate limit), and
  isoform expression by tissue would say where each change matters (#102).
- **KLIFS's terms are a statement, not a licence** (2026-09-30). Its FAQ says all data
  is free and open for academia and industry, and asks for a citation; no licence text
  was found. The registry records it as no restrictions of its own, with that caveat.
  If KLIFS publishes a licence, the terms record is reviewed.
- **One structure places a kinase's pocket.** KLIFS states pocket residues one
  structure per request. If the chosen structure's author numbering disagrees with
  another's at a pocket position, the card shows only the chosen one, and the residue
  check is the guard.
- **GPCRdb's own copy of a sequence** (2026-09-30). GPCRdb numbers residues on the
  sequence its entry states. When UniProt revises the sequence and GPCRdb has not yet,
  the numbers stay in GPCRdb's numbering (`sequence_differs`) until both agree: correct,
  but a card loses its placed residues until then.
- **Annotations RCSB integrates carry their own origin** (2026-09-30). Membrane
  segments (OPM, PDBTM) and secondary structure (PROMOTIF, DSSP) reach cards in RCSB's
  statement, with the resource that assigned them. The statement's terms are RCSB's
  (CC0); the assigning resource's own terms, where it states any, are not recorded
  separately. No licence was found for OPM on its site.
- **OMA answers HTTP 502 to about one request in three** (measured 2026-10-01, however
  spaced). Its client tries a request up to 4 times beyond the general retries (on
  main since 0.8.1); a failure is still recorded as `error`, never as absence.
- **Live sources fail now and then** (#97). In one day of eight full pilot builds,
  BindingDB failed three times (a 200 whose body was not JSON), and ChEMBL (HTTP 500),
  OMA, PHI-base and Reactome once or more. Unreadable answers and HTTP 500 are now
  retried and recorded (`quality.retries`); a failure that persists is still an
  `error`. A user project that repeats builds can reuse what succeeded
  (`reusing(max_age)`, #100); validation runs never do. Retries do not help with an
  outage: later the same day ChEMBL's API answered HTTP 500 to every request,
  including its own status, for a while. The cards recorded an `error` and the
  retries, and the run was repeated once ChEMBL answered again.
- **UniRef clusters change with UniProt's releases** (#103). Members join and leave,
  and a cluster can be renamed after a new representative. `clustered_with` records
  the release it was read from; two cards of different releases may name different
  clusters for the same entry.
- **gnomAD's rate limit.** The service answers HTTP 429 after bursts (about ten
  requests a minute sustained). Sabueso retries with backoff. A build that asks many
  genes in a row may still see errors, recorded as `error`, never as absence.
- **Tissue terms follow the pext's GTEx release** (#102). GTEx is asked for the release
  gnomAD's pext states (`gtex_v10`). If a later pext uses a release whose tissue ids
  change, the join (`gtex_tissue_key@1`) fails for those tissues; they are listed as
  `tissues_not_in_gtex` in the record and `tissues_without_term` in the views, never
  given a term by name.
- **CI depends on the uibcdf channel at anaconda.org.** On 2026-10-01 the CI of two
  commits failed in most cells while installing packages from it (HTTP 503 and
  timeouts for pyunitwizard, smonitor, depdigest, argdigest), and passed on a rerun of
  the failed jobs. A red CI is read before it is trusted or dismissed: an install step
  that fails is infrastructure, a test that fails is not.
- **Sabueso does not authorize what a packet discloses** (uibcdf/moli#22). A packet,
  and even an index without values, reveals what exists, how much and from which
  sources, curated statements included. Sabueso has no notion of a recipient. The
  platform must apply the recipient's disclosure policy before a packet, an index or
  an item leaves, and again before a reasoning backend. Until it does, a packet of
  private cards is as private as the store it came from.

## Open Questions

The maintainer-approved [next roadmap](ROADMAP.md#next-roadmap-after-0130)
(2026-10-05, #112) schedules these decisions before broad API expansion:

- **Scientific query scope** (#71/#112, MOLI #22): agree a small catalog of
  questions, entity/collection types, scientific context, constraints and coverage
  guarantees beyond the protein/comparator prototype.
- **Entity representations** (#112/#20/#96): define modified-peptide identity,
  isoform/construct boundaries, FASTA/structure-file intake and the need for
  structure-level cards. Source-stated identity and scientific similarity remain
  separate; sequence/name matches cannot authorize merging.
- **Reproducibility and export** (#100/#53, MOLI #3/#33): decide what a standalone
  export retains and how historical state, source release, downloaded responses
  and observed execution relate. Address retention and unavailable references
  explicitly; local history does not establish historical source availability.
- **Public contract stability** (#112 and feature issues): identify the guarantees
  to stabilize for queries, explanations, terms, references and export, and their
  version/deprecation and historical-read policies. Shared promises require owner
  agreement in MOLI.

- **Which isoforms, and which variants, are tissue-specific?** (#102; a need the
  maintainers recorded on 2026-09-30. **Variants: answered on 2026-10-01** by gnomAD's
  pext and `Card.variant_tissue_usage()`, `pext_at_variant@1`. Isoforms: answered the
  same day by `Card.isoform_tissue_usage()`, `isoform_exon_usage@1`, with UniProt's
  statements restricted to each isoform. Tissues as GTEx's UBERON terms, and isoforms
  without exons explained, on main (`isoform_exon_usage@2`). What remains: most
  isoforms without exons have no transcript any source states, so their tissues stay
  unknown.) Remaining expansion needs source-stated transcript/exon correspondence,
  isoform sequences and explicit expression scope/releases. No alignment or guessed
  transcript identity can fill these gaps.
- **Literature extraction and validation** (#92/#29/#112): define supplied-fragment
  rights, human validation, correction/retraction and broader statement rules before
  model-assisted extraction. Record method/model/configuration and exact source
  location. An extracted SourceAssertion must state what the external source
  actually says; a model-generated interpretation does not automatically become
  one. Provider/prompt policy remains undecided. Project-derived promotion is a
  separate MOLI #17 boundary, and project Evidence remains Nextia's.
- **Coherent cache/replay and historical source access** (#100): the retrieval
  archive and explicit reuse/replay modes exist. Agree release coherence, rights
  and availability guarantees for heavier workflows and historical queries
  (`CACHE_POLICY.md`); #101 real-mirror work remains postponed.
- Which **reference form** will MOLI agree for cited knowledge (uibcdf/moli#3, #53)?
- How does **derived knowledge promoted by a project** live in Sabueso, if at all
  (uibcdf/moli#17)?

Answered since the first list (2026-01):
- default selection rules: `SELECTION_RULES_EXAMPLES.md` (#10);
- ambiguous inputs: they are reported, never chosen (`DATA_FLOW.md`, #55);
- the schema versioning policy: `SCHEMA.md` (#42), and migration (#51);
- the local store: `CACHE_POLICY.md`, `STORAGE_LAYOUT.md` (#7, #27). Cards are stored
  whole, so the question of partial cards does not arise.

- Local incremental wheel builds can silently retain older modules from versioned generated
  `build/lib` when cached timestamps exceed source timestamps (#113). The observed
  artifact failed fresh import despite passing source tests. Clean/preserve generated
  caches and use `devtools/conda-build/check_local_wheel.py` before installed
  diagnostics. Published Conda receipts verify source bytes separately; no public
  wheel route is claimed.

- Published `interface_site_agreement@1` compares integer positions without
  verifying interface numbering or family sequence/indexing (#120). Default
  agreement `@2` now refuses unconfirmed/conflicted comparisons with explicit
  reasons and uncomputed sets. Explicit legacy selection retains the original
  limitation for reproducibility, and the matching explanation flags its gap.
  Missing original numbering cannot be reconstructed from equal numbers or names.

- **Clinical registry scope and delivery** (#108/#127/#128): development observation
  and explicit native references are implemented, with local false-absence,
  continuation and duplicate-integrity fixes. The registry timestamp is reported
  independently of pages, so coherent per-page revision is unknown. Linked references
  can be incomplete, retracted or permission-restricted; declared links do not prove
  access, article rights or efficacy. Explicit Europe PMC metadata preserves complete
  returned personal/collective authors. Wider clinical semantics and bibliography
  across other providers remain pending; these fixes need a delivery checkpoint.
