# Documentation Gaps

What the user guide (`docs/`) lacks. The initial list (2026-01) was reviewed on
2026-09-26; delivery status was reconciled against qualified 0.14.0 on 2026-10-09.
What is covered is noted below; historical checkpoints retain their original scope.

## Covered

- Concepts: `user/concepts.md`.
- Resolution: `user/resolving.md`, covering queries, ambiguity, the identity audit,
  options, profiles and offline clients.
- What a protein card knows:
  - `user/structures.md`;
  - `user/sites_and_interfaces.md`;
  - `user/bioactivities.md`, with three sources and measurement identity;
  - `user/literature_and_curation.md`, covering the curation workflow, claims and the
    curation store.
- Decks: `user/decks.md`, covering membership, derivation, audits, names, inventory
  and citing.
- Storage and upgrades: `user/storage.md`, and `user/upgrading.md` (migration, refresh,
  deprecations).
- Field paths, selection rules (kept identical to the packaged rules by a test), data
  sources (generated from the registry), testing.
- Source access: `user/tools/db/sources.md`, which lists every `get_*`. The deprecated
  pages are marked, each pointing to its replacement.
- The API reference covers every module of `core`, `tools` and `mappings`.
- Since the post-0.13.0 journey slice (#112):
  - `user/journeys.md` and `examples/user_journeys/protein_comparison.py`: the
    independently readable public protein/comparator journey, with saved original
    results/support/attribution and fixture reacquisition;
  - `user/molecules.md`: molecular identity, physchem, clinical scope and the
    target/molecule activity crossing, with the independently readable public
    BTS/benznidazole journey in `examples/user_journeys/molecule_target.py`;
  - `user/source_coverage.md`: source contributions and scientific/runtime limits
    for the three journeys;
  - `user/journeys.md` and `examples/user_journeys/disease_entities.py`: independent
    disease saved-reader/reacquisition demonstration with original membership
    metadata, exact card support and explicit support/observation gaps.

## Open gaps

- **Coherent human exploration:** existing thematic guides and raw access do not
  establish a uniform orientation/topic/item/source experience or complete
  inspectability of retained Card content. The
  [design plan](pending_proposals/card_human_exploration_api.md) (#148) specifies
  progressive access, a generic inspector fallback and researcher walkthroughs.
  New names/types are provisional; do not document them as delivered APIs.

The [approved roadmap after 0.13.0](ROADMAP.md#next-roadmap-after-0130) schedules
documentation around three independent-user journeys: protein/comparator,
molecule/activities and disease/related entities. Each needs a public runnable
example, supported-source/limit/terms explanations, original runtime sidecar
preservation and an independent saved reader. Review closure under #112 alongside
the implementation issues; consumer-owned MOLI contracts remain separate.

- **The showcase notebook** was run on 0.3.0. It lacks:
  - the identity audit with NCBI Gene;
  - measurements across sources;
  - names;
  - the structural inventory.
  Rebuild it (`tools/build_showcase_notebook.py`) during the user-journey work.
- **Per-source coverage tables** for users: which fields and relationships each source
  fills. The journey-level table is now in `user/source_coverage.md`; full field/path
  and relationship coverage for every source remains in `devguide/DATA_SOURCES_STATUS.md`.
- **Integration contracts** with MolSysSuite (MolSysMT, TopoMT, PharmacophoreMT) and with
  Nextia (citing references). Not written, because not agreed yet (uibcdf/moli#3,
  moli#17).
- **Online tests**: keys and environment variables (BioGRID).
- **Sources of wave 2 and the comparative context** (0.8.0, 0.9.0): KLIFS, GPCRdb,
  SAbDab, OMA and UniRef appear only as `resolve` options and on the data sources page.
  No page shows what they state or how to read it: kinase pockets, GPCR numbering,
  antibody complexes, orthologs, a reference entry against its genome-strain entry
  (`clustered_with`, `Card.sequence_differences`).
- **Remaining disease guarantees:** the bounded demonstration and independent
  saved reader and membership assertion/input pins are delivered in 0.14.0 (#112/#91);
  MONDO/Open Targets/Orphanet and disease-deck build observation are delivered; remaining
  full underlying study bibliography (#108) remains required. Conservative
  whole-context admission is delivered (#29); finer filtering by terms of use and raw per-record rights
  remain pending.
  Broad molecular reverse queries and clinical/source-operation observation remain
  #71/#108 work; the molecule example fetches ChEMBL indications, not clinical studies.
  Source-record aggregate knowledge-state counts are corrected under versioned
  rules (#122) in qualified 0.14.0. Full acceptance of the remaining bibliography,
  query and observation scopes is separate.
