# Sabueso — Roadmap

Sabueso's work follows two routes, and this roadmap integrates both. Neither replaces the
other.

1. **The foundational plan** (2026-01 → 2026-09-23). The original design:
   - the vision, architecture and use cases;
   - a roadmap in phases (`archive/ROADMAP_original_2026-01.md`) and a source plan
     (`archive/SOURCES_original_plan.md`);
   - the long-term directions written on 2026-09-23 (`SCIENTIFIC_POTENTIAL.md`,
     `archive/future_direction_2026-09-23.md`).
2. **The pilot-driven route** (since 2026-09-23). Real discovery programs, the MOLI
   vertical pilots, pull platform development: a pilot needs something, Sabueso builds
   the smallest useful slice, and real use shows what is missing. Pilots are private.
   Their needs enter this public repository phrased generically, with public test
   systems (TcTIM, HsTIM and HK2, public data only).

The pilot route decided the *order* of the work since 2026-09-23, not its *scope*. The
objectives of the foundational plan stay objectives. This document tracks each one's
status, so that none is lost because a pilot has not asked for it yet.

## How the two routes are integrated

- **A pilot blocker comes first.** When a pilot cannot advance without Sabueso, that
  work goes first, in its smallest useful form.
- **Foundations are not postponed until they are expensive.** Some objectives get
  costlier the longer they wait: identity, references, schema, stores, query
  interfaces. They are scheduled before a pilot forces them, when the design they
  constrain is being built.
- **Every slice is built toward the foundational design.** A pilot-driven slice uses the
  general model (relationships, SourceAssertions, named derivation rules, pinned
  references), never a pilot-shaped shortcut. The pilot is its acceptance test, not its
  boundary.
- **Each release is reviewed against both routes.** Its notes and `CHECKPOINT.md` say
  what it advanced in each. When this table is out of date, updating it is part of the
  release.
- **Maintainers may schedule a foundational objective on its own.** The pilots do not
  own the plan.

## Latest release: 0.14.0 (#134)

Published 2026-10-09 from qualified `78623d0`: exact-SHA CI/governance,
independently verified staging, all twelve installed OS/Python lanes, exact-file
promotion, clean public installation and identical-tag Zenodo archival pass.
Each installed lane passes 1,277 receiving cases, one intentional local-only input
exclusion and the public workflow. Complete receipt:
`devtools/conda-build/receipts/sabueso_0.14.0_public_2026-10-09.json`.

The release consolidates bounded native/supplied-file access, source-sequence and
residue support, notebook reports and public HK2, independent protein/molecule/
disease journeys, clinical bibliography and conservative source-state/taxonomy
integrity. Schema 0.3.13 is frozen. It advances foundational identity/support/
reference integrity and bounded consumer-oriented acceptance together. Native
access remains separate from card contribution and current live health. Full
private consumer routes (#132), broader #108/#91/#92 and
consumer-owned MOLI/Nextia/Recorda acceptance remain open; the next development
order continues below. SQLite lifetime (#133) is corrected and exact-SHA CI
qualified on post-release main; the published 0.14.0 artifact remains unchanged.

## Preceding release: 0.13.0 (#121)

Published 2026-10-05 from qualified `7e78d07`, with unchanged `py_0` promotion,
clean public installation and an identical-tag Zenodo archive. All 12 installed
OS/minor lanes pass 613 receiving cases and the public workflow; receipt:
`devtools/conda-build/receipts/sabueso_0.13.0_public_2026-10-05.json`.

The release adds eight source families to required acquisition observation, original
literal extraction/article bibliography, pinned derived explanations, versioned
integrity corrections and an independent persisted application exercise. It advances
foundational identity/support/schema/reference integrity and receiving-pipeline
traceability. Schema 0.3.12 is frozen. Broader #108/#91/#92 and consumer-owned
Nextia Evidence / MOLI ProjectRecord / Recorda acceptance remain open.

## Current consolidation after recovery (#112)

Approved by the maintainer on 2026-10-08, following the
[global audit](pending_proposals/post_recovery_global_audit.md). Consolidate fixture
delivery and current guidance, expose source maturity, then integrate selected
recovered capabilities into the approved journeys and parallel consumer acceptance.
This serves both routes; it does not replace their objectives or make provider
count a scientific acceptance criterion. Current state: [CHECKPOINT.md](CHECKPOINT.md).
Detailed recovery chronology is [archived](archive/consolidation_2026-10-08/ROADMAP.md).
The local consolidation is implemented and verified in the
[consolidation report](pending_proposals/post_recovery_consolidation.md): protected
inputs, scoped full suites, structured guides, generated capability inventory,
protein residue context, measured costs and a ready MOLI documentation PR.
Public code delivery and real shared consumer-contract acceptance remain separate.

## Previous release: 0.12.0 (#110)

Published 2026-10-04 from qualified `7739317`, with unchanged `py_1` promotion,
clean public installation and an identical-tag Zenodo archive. The 12 installed
OS/minor lanes each pass 56 integration cases and the public three-packet workflow;
receipt: `devtools/conda-build/receipts/sabueso_0.12.0_public_2026-10-04.json`.
The superseded preliminary `py_0` archive/receipt remain immutable.

This release combines located literature and supported structural mention context,
literature explanations, pinned packet terms, required Ackredit attribution and
UniProt/Europe PMC/RCSB acquisition traces. RCSB retains native entry revisions,
primary citations, reuse, empty answers and per-entry failures with every fallback.
It advances foundational support/terms/reference integrity and the pilot-driven
need to retain original source access and per-result/workflow references.
Schema 0.3.11 is frozen; original runtime JSON stays beside scientific payloads.

Other sources/custom clients, further result types, incomplete bibliography and
MOLI ProjectRecord/Recorda integration remain open in #108/#36. Traceability remains
mandatory. The next slices follow observed use and the foundational objectives below.

## Delivered so far (0.1.0 → 0.14.0)

- **Foundations.**
  - Card, Deck, `SourceAssertionStore` and `RelationshipStore`.
  - The FieldResolver with selection rules, and the EntityResolver.
  - Mappings, conflict and knowledge-state reporting.
  - Physical quantities (PyUnitWizard) and argument contracts (ArgDigest).
  - Diagnostics (SMonitor).
- **Storage and references.**
  - Content-addressed card and deck snapshots, and pinned references.
  - The `KnowledgeStore` and the `CurationStore`.
  - Honest migration and refresh of stored cards.
- **Release route.** Staged conda releases:
  - a dependency-contract preflight;
  - inspection of the exact artifact;
  - immutable coordinates, and a recorded public poststate (#76–#78).
- **Sources in use.**
  - UniProt, RCSB PDB, PDB CCD, PDBe-KB, InterPro, AlphaFold DB.
  - ChEMBL, BindingDB, PubChem and PubChem BioAssay, UniChem.
  - STRING, IntAct (through UniProt), NCBI Taxonomy, NCBI Gene.
  - Since 0.6.0: PHI-base, DISEASES, Open Targets, Orphanet, Reactome, ClinVar, gnomAD,
    ChEMBL indications and ClinicalTrials.gov (#81–#83).
  - Since 0.7.0: SKEMPI 2.0 (#83), MONDO and MedGen (#90), Europe PMC (#92).
  - Since 0.8.0: ChEBI, KLIFS, GPCRdb, SAbDab, OMA, OPM and PDBTM segments through RCSB
    (#83), and gnomAD's pext (#102).
  - Since 0.9.0: UniRef clusters, through UniProt (#103).
  - Since 0.10.0: GTEx's tissue terms (#102).
  - The registry, `sources/registry.yaml`, is the index.
- **Knowledge views, each with a named rule:**
  - structures and the structural inventory; predicted models;
  - oligomer and interfaces; ligand sites;
  - bioactivities, with one measurement across sources; ligands;
  - literature and claims; knowledge states;
  - card comparison; identity audit; unique names.
- **Curation.** Literature assertions, bioactivities, engagements, relationships and
  typed claims, compared with the sources, never given priority. Since 0.6.0, the
  biological context of a target (#60).
- **Since 0.6.0.**
  - Variants placed only through stated transcripts and isoform maps (#83, #85).
  - Knowledge packets, a prototype (#71).
  - Declared enrichers with shared network, release-cache and key services (#86).
- **Since 0.7.0.**
  - Diseases as entities, anchored at MONDO; a protein's diseases grouped; a
    disease's targets and drugs (#90).
  - What may be done with the knowledge, and terms profiles (#29, #94).
  - Scientific operations: expand, explain, as of (#91).
  - Molecules given as SMILES or InChI, through PubChem's stated match (#93).
  - How each statement entered, and text-mined literature mentions (#92).
- **Since 0.8.0.**
  - Variants checked against gnomAD's consequence on the canonical transcript; the
    tissues of each variant and isoform (#85, #102).
  - Kinase pockets, GPCR numbering, antibody complexes and orthologs (#83).
  - What was downloaded (a retrieval archive), local mirrors, offline work (#100).
  - Knowledge store format 2, `knowledge_packet@2` and `packet_aspects@3` (#88, #99).
- **Since 0.9.0.**
  - A reference entry and its genome-strain entry related through their UniRef
    clusters, never merged; the positions where two equal-length sequences differ
    (#103, verified in the pilot that asked for it).
  - Unreadable answers and server errors asked again, and every retry recorded on the
    card (`quality.retries`, #97).
  - Validation runs from scratch, with what the sources answered recorded, never
    reused (#100).
- **Since 0.10.0.**
  - Tissues as GTEx's UBERON and EFO terms; isoforms whose exons are unknown say why
    (`isoform_exon_usage@2`, #102).
  - A knowledge packet as an index by reference, with the guarantees agreed in
    uibcdf/moli#22 (`packet_index@1`, #88); `packet_aspects@5`.
- **Since 0.11.0.**
  - Pinned explanations of structural inventory items and all group members
    (`structure_inventory_explanation@1`, #91), without fetching or selecting.
  - Located accession annotations for explicit articles at source access (#92),
    and a public hypothetical review rehearsal that preserves historical support.
  - Curation export preserves extraction acquisition (#105); existing source
    identifiers with spaces are readable by their pins (#104).

## Status of the foundational plan

Status: **done**, **partial** (part delivered, the rest named), **pending**, or
**changed** (replaced by a decision, which is cited).

### Original roadmap (phases 0–5)

| Item | Status | Where / next |
|---|---|---|
| Phase 0 — conceptual schema, repository structure, devguide | done | `schemas/`, this devguide |
| Phase 1 — UniProt, RCSB, ChEMBL, PubChem connectors | done | `sabueso.tools.db.*`, `SOURCE_ACCESS.md` |
| Phase 2 — aggregator, SourceAssertionStore, conflict detection | done | `DATA_FLOW.md` |
| Phase 3 — selection engine with per-field rules | done | `RESOLVER.md`, `SELECTION_RULES_EXAMPLES.md` |
| Phase 4 — eMolecules, ChemSpider, DrugBank | pending | registry: eMolecules and ChemSpider queued; DrugBank deferred (licence) |
| Phase 4 — physchem and bioactivity fields | done | PubChem, ChEMBL physchem; three bioactivity sources (#66, #68) |
| Phase 4 — clinical layer | partial | ChEMBL max phase and indications, ClinicalTrials.gov trials by cited NCT id (#81); DrugBank deferred; ADMET and pharmacovigilance pending |
| Phase 5 — SDK entry points | done | `sabueso.resolve`, views, `PUBLIC_API.md` |
| Phase 5 — CLI | pending | no need has been stated |
| Phase 5 — Sphinx documentation | done | `docs/` |
| Phase 5 — pytest coverage, contract tests, snapshots | done | `TESTS.md`: offline suite, online tests, frozen cards, recorded card shape |

### Original vision and architecture

| Item | Status | Where / next |
|---|---|---|
| Protein cards | done | `resolve_protein_card` |
| Small-molecule cards | done | InChIKey anchor (#25) |
| Peptide cards | pending | `entity_type: peptide` exists in the schema; no peptide source or view (CPPsite queued) |
| Inputs: identifiers, names | done | UniProt, `pdb:`, `pubchem:`, `chembl:`, `pdb.ligand:`, `inchikey:`, name + organism |
| Inputs: SMILES, InChI | done | matched by PubChem, never a computed key (`pubchem_structure_lookup`, #93) |
| Inputs: sequence (FASTA), structure files | partial development | explicit `exact_sequence_candidates@1` accepts raw/FASTA, verifies full archive/current canonical sequences and retains ambiguity, caps, failures and unqueried isoforms. Automatic sequence/structure-file resolution remains pending and needs its own identity rules. |
| Disease associations of a protein | done | `annotations.disease` (#39) |
| Ligands with a role (inhibitor…) | changed | a role is a derived class, never asserted (#25): `bioactivity_class@3`, `ligand_deck` |
| Deck of inhibitors of a protein | done | `ligand_deck(card)` with derived classes |
| Local cache / store | done | `KnowledgeStore` (cards); retrieval archive and local mirrors, opt-in (#100, `CACHE_POLICY.md`) |

### Use cases (`USE_CASES.md`)

| Use case | Status |
|---|---|
| 1. Interactions, ligands, pathways of a protein | done (pathway structure from Reactome, #83) |
| 2. Clinical usage of ligands | partial (max phase and ChEMBL indications, #81; DrugBank clinical content deferred, licence) |
| 3. TopoMT: catalytic residues, mutations as structural features | partial (positional features, ligand and family sites, interface mutations from SKEMPI, #83; no TopoMT contract yet) |
| 4. PharmacophoreMT: deck of ligands | partial (ligand decks; no exchange format agreed) |
| 5. Commercial availability of peptides | pending |
| 6. Tissue-specific isoforms | partial (tissue specificity; UniProt isoforms and alternative sequences, #80; AlphaFold isoform models; the tissues of each variant and isoform from gnomAD's pext, with GTEx's UBERON terms, #102; isoform sequences not fetched) |
| 7. Visualization (MolSysViewer) | partial (interfaces, mutations, sites, secondary structure from UniProt and per chain from RCSB, #80; no contract) |
| 8. Clinical trials of ligands | done for the trials ChEMBL's indications cite (#81); a trial is never matched to a molecule by name |
| 9. Disease associations; targets of a disease | done: protein → diseases from UniProt, DISEASES, Open Targets, Orphanet and ClinVar, grouped through MONDO (#82, #90); disease → targets and → drugs as decks (#90) |
| 10. Knowledge baseline for a target and a comparator (pilot route) | done |
| 11. Curating what the literature states (pilot route) | done (human curation) |
| 12. Citing knowledge from a project (pilot route) | done, provisional reference form (#53, moli#3) |
| 13. Choosing structures to model (pilot route) | done |
| 14. A cohort of related proteins (pilot route) | done |

### Strategic directions (`SCIENTIFIC_POTENTIAL.md`, 2026-09-23)

| Direction | Status | Where / next |
|---|---|---|
| A strong SourceAssertionStore | done | MOLI-aligned fields, curated assertions, provenance |
| Cards that relate (relationships as knowledge) | done | `RelationshipStore`, typed predicates |
| More powerful decks | done | membership, derivation, pinned revisions, lineage, audits, inventory |
| Entity resolution as a central piece | done | EntityResolver, identity audit, curated names; a reference entry related to its genome-strain entry, never merged (#103) |
| Temporal knowledge | partial | snapshots, revisions, source releases; the store's `as_of` and `changed_since` (#91); no source asked as of a past release |
| Knowledge from Nextia not imported automatically | done (as a boundary) | promotion of derived knowledge open in uibcdf/moli#17 |
| Literature as a knowledge source | partial | human curation and literature views; literal rule extraction/intake and explicit article metadata since 0.13.0 (#92); broader extraction/validation pending |
| KnowledgeQuery (semantic queries over sources) | partial | prototype released in 0.6.0 (#71): a protein subject, a fixed aspect mapping (`packet_aspects@5` since 0.10.0; published @6 adds literature mentions and their index/unknowns); contract in uibcdf/moli#22 |
| Knowledge packets (entities, facts, conflicts, unknowns) | partial | prototype released in 0.6.0 (#71): pinned, stored, with a content-equivalence id; since 0.10.0, an index level by reference for size (#88), accepted in uibcdf/moli#22, which closes with a consumer test |
| Unknowns as first-class output | done | `knowledge_state()` (#56) |
| Two levels of access (semantic and raw) | done | `resolve` and views; `tools.db.*.get_*` |
| Patents | deferred | SureChEMBL evaluated 2026-09-30: mentions cannot be restricted to claims |
| Proprietary / internal knowledge | pending | needs its boundary with Nextia (moli#17) and usage terms (#29) |

## Pilot-driven work

Delivered for the first pilot's knowledge baseline and structural inventory:

- organism relations and identity hygiene (#54, #55, #67, #69);
- knowledge states (#56);
- versioned decks and card comparison (#58, #59);
- predicted structures (#57) and curated engagement (#61);
- measurements across sources (#66, #68);
- migration (#51) and claims (#43);
- names, the structural inventory and its grouping (#70);
- what the first live run of the baseline found: the authors' oligomer (#72), author
  numbering (#73), partial source answers (#74), the measurement review (#75);
- the integrity of pinned item reads (#79), a case of the reference contract
  (uibcdf/moli#3);
- the comparative context: orthologs (OMA, #83), the tissues of variants and isoforms
  (#102), and a reference entry related to the genome-strain entry proteome-based
  sources use (#103);
- steadier live runs: unreadable answers and server errors retried and recorded (#97);
  runs from scratch, with what the sources answered recorded (#100).

Open, pilot-related:
- #53, the reference form (waits on uibcdf/moli#3);
- #60, biological context: step 1 (curated fields) released in 0.6.0; step 2
  (VEuPathDB) blocked on access and terms (#84);
- #30, ligand proximity to sites (deferred);
- correspondence of regions across proteins. This one belongs to MolSysMT; Sabueso takes
  its residue maps (`residue_map`, `residue_maps`).

## Design review after 0.12.0

The maintainer-requested [implementation review](pending_proposals/design_implementation_review.md)
(#112, 2026-10-04) compares original phases, conceptual schema, architecture, scientific
potential and use cases against code/tests. The foundations are implemented; complete
runtime coverage, broader literature extraction, derived explanations, consumer acceptance,
peptides/suppliers and much of the clinical layer remain partial or pending. Illustrative
graph/query APIs are directions, not implied delivery obligations. The review retains
the earlier slice sequence; the approved next roadmap below sets the current order
across both routes. #101 remains postponed.

## Next roadmap after 0.13.0

Approved by the maintainer on 2026-10-05 after reviewing the original architecture,
MOLI's Knowledge role and Sabueso's promise to independent scientific users (#112).
This is the next development order. The capability status below remains the record
of what exists and what is incomplete; illustrative long-term APIs remain design
directions until a bounded use and acceptance criteria are agreed.

### Immediate resumption sequence

Scheduling boundary, 2026-10-21: the
[saved-consumer usefulness review](pending_proposals/pilot_usefulness_review_20261021.md)
checks retained results and prepares the primary-method review queue. The
maintainer's separate matter is now the
[human exploration API design](pending_proposals/card_human_exploration_api.md)
(#148): simple progressive access, complete retained-content inspection and
source-grounded decision assistance. Document and review the inventory, interaction
walkthroughs and contracts before agreeing an implementation slice. This design
phase does not commit release scope or resume 0.15.0 consolidation. Retain the
development order below for later resumption; candidate selection, schema freezing,
staging and publication have not started.

Current state: [CHECKPOINT.md, Resume here](CHECKPOINT.md#resume-here).
Detailed acceptance: [global audit](pending_proposals/post_recovery_global_audit.md),
[journey audit](pending_proposals/independent_user_journeys.md) and
[clinical checkpoint](pending_proposals/clinical_registry_checkpoint.md).

The five-step recovery consolidation is locally verified; do not restart native
provider triage or repeat the archived chronology. Resume with:

1. **Public code checkpoint qualified.** The recovered `dc46424` checkpoint and
   taxonomy follow-up `a05e0a3` each pass 15/15 exact-SHA CI jobs and governance.
   The [publication receipt](pending_proposals/post_recovery_public_checkpoint.md)
   and [follow-up receipt](pending_proposals/taxonomy_followup_checkpoint.json)
   retain their own input scopes and qualification. Preserve the reviewed delivery
   boundary: now 51 repository inputs, including the release compatibility card
   and a natively licensed open-article XML,
   and 37 protected originals. Installed-artifact/release gates remain separate.
2. **Continue bounded real consumer use.** Revalidate the applicable
   private MOLI Python/Jupyter workflows under
   [#132](https://github.com/uibcdf/sabueso/issues/132). Keep the pilot checkout
   read-only and all original content/results in a private workspace. Check
   scientific usefulness, support/unknowns/units, saved readers/reacquisition and
   measured cost; expose only generic component findings publicly. Prior pilot
   receipts and public fixtures do not qualify the recovered checkpoint.
   The [bounded development exercise](pending_proposals/private_consumer_revalidation.md)
   now passes 14 original cells, exact saved-result reading and original-answer
   replay. The exercised NCBI Taxonomy acquisition-operation gap (#108) is now
   implemented, rechecked with live/original-answer scope and qualified by exact-SHA
   CI. Extend the original routes with explicit source scope. Full profile/
   packet acquisition and overall #132 acceptance remain open; missing historical
   stores cannot be reconstructed from current cards.
   Fourteen additional original cards/inventory cells pass with explicit
   repository-fixture client injection and zero network attempts. Keep that
   orchestration result separate from the earlier live/local scope: it does not
   qualify full profile acquisition, native answers or source absence. The
   post-release SQLite lifetime fix (#133) passes eight regressions and the
   5,602-case local-original suite. Code `5bbede0` passes 15/15 exact-SHA CI and
   governance; Linux Python 3.14 has only six intentional fixture warnings, with
   no unclosed SQLite group. #133 is complete. Neither slice changes the published
   0.14.0 artifact.
   The subsequent GTEx prerequisite correction (#135) keeps absent tissue keys or
   ambiguous/missing release inputs `not_queried` before constructing a source
   client. Its 113 selected and 5,605 full local-original tests pass; code `b28f8d3`
   passes 15/15 exact-SHA CI and governance, recorded in the
   [technical receipt](pending_proposals/gtex_prerequisite_checkpoint.json).
   Historical reports and the published artifact stay fixed.
   The public registry's shared-source terms collision (#136) is corrected:
   UniRef explicitly shares the `uniprot` resource's terms, whose provider-level
   attribution applies to either route. Export and registry gates reject unintended
   collisions or policy differences independently of row order. The 125 selected
   and 5,627 full local-original cases pass; code `e0b80b2` passes 15/15 exact-SHA
   CI and governance, recorded in the
   [technical receipt](pending_proposals/shared_source_terms_checkpoint.json).
   Historical reports and the published artifact stay fixed.
   Retain biological source identity, frozen fixture bytes and saved reports.
   Subsequent bounded native-answer scopes add comparative context with exact-build
   replay and inert readers. Their payloads/results remain private; passing editable
   SDK routes does not qualify the installed environment or human usefulness.
   Continue with targeted inspection, pinned explanations and operation coverage.
   Public synthetic response guards (#137) keep malformed comparative-source
   envelopes and unanswered consequence aliases separate from explicit absence.
   Code `09cf912` passes 15/15 exact-SHA CI and governance; its
   [receipt](pending_proposals/comparative_response_contracts_checkpoint.json)
   retains public/local input scopes and shared editable-environment verification.
3. **Advance the next bounded scientific slice.** Source-active-site residue context
   and selected composition are now in protein example `@2`, with original `@1`
   readers preserved. Continue the approved molecule/activity and disease/entity
   acceptance. The bounded [clinical bibliography journey](pending_proposals/clinical_bibliography_journey.md)
   (#108/#112) now declares one source-cited NCT and three PMID selections,
   saves original per-result/workflow sidecars and reports all unqueried links.
   Its clinical-only reacquisition preserves the original molecule `@1` and disease
   `@1`–`@5` reports. Code `2d294d8` passes 6,326 local-original cases and
   exact-source CI 15/15 plus governance; retain its own source qualification.
   Continue with explicit missing coverage and real consumer-owned
   scientific acceptance; metadata linkage alone does not establish clinical efficacy.
4. **Coordinate consumer-owned acceptance.** Review MOLI PR #65's evidence correction
   and perform the smallest ready exercise when Nextia's persistent slice exists.
   Shared references (#53/MOLI #3), packets (#71/MOLI #22) and recording
   (#108/MOLI #36) keep their respective owners. Extend the recorded bounded
   time/memory/storage measurements before optimizing larger workloads.

Keep guide/registry/capability freshness and fixture protection as normal gates for
each next slice, rather than separate provider-count milestones.

After these bounded slices, choose one explicit non-protein query/explanation
(#71/#91) or finer use-term filter (#29) before implementation. Filtering produces
a separate declared view/deck with kept/excluded support; it never deletes original
knowledge silently. Continue peptide scoping and foundational work below.
Qualify public code checkpoints and exact CI before staged release work; earlier
`74c8c3d` CI and local receipts do not qualify new recovery changes.

### 1. Complete three independent-user journeys

Define and demonstrate these end-to-end journeys through the existing public SDK
first. Record missing behavior before adding a connector or changing an API.

| Journey | Scientific question and expected output | Acceptance |
| --- | --- | --- |
| Protein and comparator | What is known about each protein, where do sources disagree, and which structures, ligands and measurements can be compared? | Resolve and audit identities; inspect supported values, alternatives, conflicts and unknowns; compare within stated identity/numbering scope; save both states and read their exact support later. |
| Molecule and activities | What do sources state about a molecule, its measured activities and reported clinical context? | Resolve the molecule; retain measurement types, units, assay context, source-supported identity and clinical coverage limits; inspect original statements and citations; save and reopen the result. |
| Disease and related entities | Which targets and drugs do sources associate with a disease, and on what basis? | Resolve a MONDO-anchored disease; build target/drug decks; retain relationship support, grouping rules, ungrouped identity paths and conflicts; save and inspect exact historical items. |

Each journey needs a runnable public example and user-guide instructions that do
not require knowledge of provider endpoints or MOLI internals. Explain source
coverage, limits, terms and partial/unavailable outcomes. Preserve original runtime
JSON beside saved scientific objects, with per-result/workflow citations and explicit
observation gaps. An independent saved reader must recover the cited state without
source access; reacquisition must leave those historical references meaningful.

Refresh the showcase and add a dedicated small-molecule page, user-facing source
coverage tables and examples for comparative/source-specific views where used.
Track the journey audit in #112 and [DOCS_GAPS.md](DOCS_GAPS.md); use #71, #91,
#108 and the relevant source issues for implementation gaps. The SDK is the current
entry point; evaluate a CLI only when a journey demonstrates a need.

Development progress (2026-10-05, #112): the protein/comparator journey is implemented
in `examples/user_journeys/protein_comparison.py`, with separate producer, reader
and reacquisition processes, exact support for both proteins, original reports,
unit-preserving serialization and original runtime/bibliography records. Its scope
is explicit public fixture subsets, without positional alignment or a claim of
current online availability. The user guide now covers this journey, small-molecule
cards and source coverage for the three workflows. The molecule/declared-target
journey now preserves BTS/benznidazole identity, assay measurements and ChEMBL
clinical indications, with a selected molecular deck, target-context packet,
original reports/attribution, separate saved readers and fixture reacquisition.
Other targets and cited clinical studies are explicitly unqueried. Its source-state
counting defect is corrected locally in #122 under `knowledge_state@5` and
`knowledge_state_explanation@2`, with unknown/native counts, missing subsets and
separate clinical areas. Published delivery remains pending; broader molecular
queries and integration of observed clinical bibliography remain #71/#108. The disease journey now has a
bounded producer, independent saved reader and reacquisition example preserving
MONDO/card support, original target/drug membership metadata, disease-group
explanations and partial runtime attribution. Development disease rules `@2` now
preserve exact native membership, original MONDO input and member identity pins,
including excluded/unbuilt candidates, with portable support and atomic saves (#91).
MONDO term/equivalence observation is implemented locally with original index/file
origins, versions, reuse and bibliography. Complete acceptance remains open:
Open Targets/Orphanet and disease-deck build observation are also implemented locally
(#108/#124), including page/file receipts and exact input/result pins.
DISEASES/ClinVar/MedGen observation is also implemented locally (#108/#125).
Conservative `disease_deck_admission@1` is also implemented locally (#29): exact
embedded context must allow the use; all raw member statements are checked, and
excluded member identity pins become explicit historical references. Unknown or
restricted shared context refuses the operation; finer filtering by terms of use
remains pending. Native ChEMBL indication pointers now contribute to workflow
attribution, retaining exact row/page/query occurrences and explicit unfetched-target
and metadata gaps (#108). Development ClinicalTrials.gov observation and explicit
registry-reference/Europe PMC bibliography are implemented (#127/#128); broader
underlying study bibliography remains pending.
Non-protein packets remain
#71 work; see
[the journey audit](pending_proposals/independent_user_journeys.md) for concrete
query/observation gaps. The broader live showcase refresh remains open.

### 2. Extend queries, explanations and required traceability

Use the journey gaps to define a small catalog of precise scientific queries.
Examples to scope include ligands with specified measurements, structures that
represent a requested region, and drugs associated with a disease. Agree identity,
context, constraints, selection, completeness and result support before choosing
public method names.

- **Queries (#71).** Extend beyond the current protein/comparator and fixed aspects
  toward molecule, disease and collection questions in bounded slices. Source
  routing and normalized output belong to Sabueso. Every slice declares its
  supported constraints and reports unsupported requests explicitly; full/index
  results retain exact authoritative references, conflicts, unknowns and terms.
- **Explanations (#91).** Extend the named-rule/pinned-support readers to the derived
  results those journeys expose. Show inputs, parameters, exclusions, alternatives
  and partial support. Historical reads must not acquire data or silently change
  rules. General joins, ranking and graph navigation need separate scientific scopes.
  Development `explain_sequence_differences`, `explain_variant_tissue_usage` and
  `explain_isoform_tissue_usage` now retain exact pins, selected/alternative support,
  actual region choices and weighted intersections, tissue terms and original
  source-version labels. The independent public comparative-support journey keeps
  original reports after reacquisition without re-derivation. Historical genomic
  scope/overlap assumptions remain explicitly selectable. Development correction
  #138 introduces matching genomic scopes, union coverage, per-tissue missingness
  and explanation `@2`; [its scope](pending_proposals/comparative_tissue_scope.md)
  separates new and historical rules. Comparative operation observation remains #108.
  Code `3bc1c53` qualifies the #138 correction with 5,819 local-original cases and
  15/15 exact-SHA CI jobs; [its source receipt](pending_proposals/comparative_tissue_scope_checkpoint.json)
  retains public/local scopes and explicit legacy reproduction. Development #139
  now restores declared-source scope and saved arguments, reporting historical
  missing parameters, overrides and unsupported selectors. Code `ff32cb6` passes
  5,896 local-original cases and 15/15 exact-SHA CI; [qualification](pending_proposals/refresh_request_scope.md)
  retains its [source receipt](pending_proposals/refresh_request_scope_checkpoint.json).
  Continue with comparative operation/bibliography observation in #108.
  The [development GTEx slice](pending_proposals/gtex_observation.md) observes
  existing tissue requests, requested-label/revision distinctions and original
  portable credit; 5,930 local-original cases and 15/15 exact-SHA CI pass at
  `2b5db53`, with [its source receipt](pending_proposals/gtex_observation_checkpoint.json).
  [Development UniRef observation](pending_proposals/uniref_observation.md) follows
  with per-page releases, limits and partial failures under source `UniProt`;
  code `c6cb0e3` passes 5,963 local-original cases and 15/15 exact-SHA CI;
  [its source receipt](pending_proposals/uniref_observation_checkpoint.json) retains
  public/local/installed compatibility scopes. The [pagination correction #140](archive/uniref_pagination.md) is
  source-qualified at `3a47490`: 21 new cases, 5,984 local-original cases and 15/15
  exact-source CI; [its receipt](archive/uniref_pagination_checkpoint.json) retains
  the public/installed compatibility scopes. The [OMA slice](pending_proposals/oma_observation.md)
  is source-qualified at `593ba76`: 47 new cases, 6,031 local-original cases and
  15/15 exact-source CI; [its receipt](pending_proposals/oma_observation_checkpoint.json)
  retains public/installed compatibility and original-answer replay scope.
  The [gnomAD slice](pending_proposals/gnomad_observation.md) is source-qualified
  at `682e226`, including unqueried gene prerequisites (#141): 54 new cases,
  6,085 local-original tests and 15/15 exact-source CI;
  [its receipt](pending_proposals/gnomad_observation_checkpoint.json) retains
  public/installed compatibility and original-answer replay scope.
  [Open Targets prerequisite #142](archive/open_targets_prerequisite.md) is
  source-qualified at `94ad9eb`: seven new cases, 6,092 local-original tests and
  15/15 exact-source CI; [its receipt](archive/open_targets_prerequisite_checkpoint.json)
  preserves public/installed compatibility scope. The
  [six-source prerequisite correction #143](archive/source_prerequisites.md) is
  source-qualified at `c45af44`: 51 new cases, 6,143 local-original tests and 15/15
  exact-source CI; [its receipt](archive/source_prerequisites_checkpoint.json)
  preserves public/installed compatibility and exact historical/corrected pins.
  [Versioned disease identity coverage #144](archive/disease_identity_coverage.md)
  is source-qualified at `cf5900d`: 39 new cases, 6,182 local-original tests and
  15/15 exact-source CI; [its receipt](archive/disease_identity_coverage_checkpoint.json)
  preserves grouping/explanation @3, coverage @1, packet mapping @7, historical
  selectors/pins and unknown request scope. Next: derived comparative operations
  and complete bibliography #108.
  [Comparative operation observation](pending_proposals/comparative_operations.md)
  is locally verified at `31b6255` for three explicit-context Card views;
  original algorithms, source pins and scientific result payloads stay fixed.
  Complete bibliography and broader result/consumer scope remain #108/#132 work.
  The [deferred block](pending_proposals/deferred_ci.md) is recovered at `25f6163`,
  with CI 15/15 and governance 1/1. Subsequent source changes need their own
  [exact-head recovery](TESTS.md#recovering-deferred-ci).
  [Persisted comparative journey attribution](pending_proposals/comparative_journey_attribution.md)
  implements example `@3` results/explanations, original source/comparative/workflow
  records and inert historical reader/export. Local selected checks pass;
  publication and remote qualification pass at `25f6163`. Next: bounded consumer
  revalidation #132. The
  [verified bibliography slice](pending_proposals/comparative_bibliography.md) adds
  source descriptions and scoped pext method credit with 278 selected passes;
  actual entry publications, native revisions and broader bibliography remain gaps.
  All 6,262 local-original offline cases pass. The
  [block receipt](pending_proposals/comparative_block_checkpoint.json) verifies
  final CI 15/15 and governance 1/1 on the exact published source SHA.
  These integrity corrections affect users of published 0.14.0. Propose one
  substantial follow-up release now that #144 is qualified, batching the source fixes
  through the existing candidate CI, staging and installed-package gates. This
  proposal does not authorize publication or replace consumer acceptance #132.
- **Traceability (#108).** Extend observed source/client/operation coverage along
  these exercised paths, including reuse, versions with their actual basis, retries,
  empty answers, caps, partial returns and failures. Keep bibliography and missing
  citations explicit. Scientific support, observed execution and terms retain
  distinct meanings; coverage cannot be inferred from a returned card alone.
- **History and scale (#100/#98/#88).** Measure large journeys and make limits and
  truncation inspectable. Scope coherent replay, historical source access and export
  guarantees separately from local store history. Preserve pins and original
  receipts; local `as_of` is a stored-state date, not a historical database query.

Acceptance for each slice includes a public scientific example, meaningful
regressions, saved historical support after refresh/reacquisition, explicit coverage
and user documentation. New packet mappings/rules are versioned; published cards,
schemas and historical packets retain their meaning.

Published receiving correction: [compact comparative credit](pending_proposals/comparative_credit_compaction.md)
emits component operation `@2` with a versioned/hash-bound input-scope reference,
retaining every original pin/assertion and historical `@1` context. Four new
regressions, 172 selected and all 6,266 local-original cases pass. This later
source is qualified at `792bd0d`: [CI 15/15 and governance 1/1](pending_proposals/comparative_credit_compaction_checkpoint.json).
MOLI owns the separate [Recorda receiving PR #67](https://github.com/uibcdf/moli/pull/67)
and shared acceptance (#36); 19 public receiving cases and applicable governance pass
with this producer, and the PR is ready for owner review. Next:
[question-by-question usefulness review](pending_proposals/consumer_scientific_acceptance.md),
using the [public scientific dossier](pending_proposals/scientific_dossier.md)
for explicit structural/assay criteria and located-mention scope. Its sixteen new
cases and full 6,282 local-original suite pass;
[source CI 15/15 and governance 1/1](pending_proposals/scientific_dossier_checkpoint.json)
qualify `6e35c1d`. Human interpretation and [substantial installed delivery](pending_proposals/release_consolidation_0150.md)
retain separate acceptance.

The [bounded usefulness review](pending_proposals/scientific_usefulness_review.md)
keeps the saved inputs unchanged and fixes readable native assay/target/document
context in dossier `@2` under `stored_assay_context_review@1`, retaining original
`@1` results and rendering. Twenty selected and all 6,286 local-original cases
pass; [source CI 15/15 and governance 1/1](pending_proposals/scientific_usefulness_checkpoint.json)
qualify `1bd8c05`, with full captures/member hashes and every test summary verified. Next: actual
activity-linked primary protocol review, scientist review and accepted installed delivery.
The [located primary-source review](pending_proposals/located_source_review.md)
prepares two structural readings with original text/identity/support and a pinned
baseline card. Corrected `@2` keeps agent drafts outside curated knowledge and
refuses the initial `@1` provenance route; scientist acceptance remains pending.
[Exact-source CI 15/15 and governance 1/1](pending_proposals/located_source_review_checkpoint.json)
qualify `4e513da`; fourteen new, 234 selected and all 6,300 local-original cases
pass. The native assay-parameter audit found
incomplete protocols; those gaps remain open.
The subsequent [primary assay-method access review](pending_proposals/primary_assay_methods_review.md)
verifies all three shared document identities and inventories 497 stored rows
across twelve assays. No complete primary methods were obtained; the institutional
PDF is a library notice. Obtain authorized originals before reviewing actual
protocols. This research evidence changes no SDK behavior, source fixture,
scientific card or earlier qualified receipt.
The [criterion-integrity correction #146](archive/scientific_dossier_criterion_integrity.md)
closes a demonstrated saved-reader gap: coherent changes to criterion records
must be refused even when regenerated Markdown and file hashes agree. The
original criterion rules and genuine historical reports retain their meaning;
25 focused and all 6,305 local-original cases pass. The
[exact-source receipt](archive/scientific_dossier_criterion_integrity_checkpoint.json)
qualifies `fe69ec5` with CI 15/15 and governance 1/1; all capture hashes and
thirteen test summaries are independently verified.

### 3. Scope peptides as the next scientific expansion

Prioritize the original peptide-card promise after the journey and contract work
above. Begin with identity and a bounded scientific use, before adding a source.
Define sequence, modifications, termini/cyclization and source-stated cross-references;
distinguish a peptide from a protein fragment, construct or isoform. Establish how
supplier products and availability relate to the scientific entity without merging
them by name or sequence similarity.

Then select a source whose access and terms fit that use, implement its client,
mapping/enricher and peptide views, and demonstrate a public save/read/cite journey.
Commercial availability must state the provider, product/context and observation
date; missing availability is not proof that a peptide cannot be obtained. Scope
CPPsite/eMolecules/ChemSpider against the actual question rather than adopting all
three automatically. #112/#83/#95 coordinate the initial scope; open a focused
owner issue before peptide implementation starts.

The clinical layer, isoform sequences/additional transcript coverage and broader
literature extraction remain objectives in the capability backlog below. Select
their next slices from a stated need. DrugBank still needs a terms/access decision;
local-mirror work #101 remains postponed until the maintainer reschedules it.

### 4. Close consumer contracts in parallel

- **Nextia and Context Assembly (#53/#71, MOLI #3/#22).** Receive actual consumer
  acceptance: persist an index, read an exact historical item, create consumer-owned
  Evidence with an explicit interpretation, and retain its original citation after
  new acquisition. `examples/persisted_pipeline/` already exercises Sabueso's public
  application side; it does not replace a persistent Nextia consumer test.
- **Platform recording (#108, MOLI #36/#18).** Agree correlation, persistence,
  availability and failure policy with the owners of ProjectRecord/Recorda. Sabueso
  supplies knowledge support and observed use; MOLI owns their platform composition.
- **Modeling exchanges.** Agree adapters with MolSysMT, TopoMT, PharmacophoreMT and
  MolSysViewer for entity references, source-supported residue/construct mappings,
  features and ligand decks. Preserve units, numbering, versions and support across
  exchanges. MOLI owns the Sabueso-to-MolSysSuite boundary; MolSysSuite governs its
  internal member contracts. Modeling and calculation remain with their owners.
  [Reviewed legacy projection requirements](archive/local_work_2026-07/consumer_projection_requirements.md)
  retain concrete receiving cases for owner review, without an accepted exchange
  schema or new exporter claim.

These are coordination tasks, not consumer implementations to add inside Sabueso.
Keep consumer acceptance separate from standalone journey acceptance.

### Decisions to close before broadening the API

| Decision | Questions to settle | Tracking / owner |
| --- | --- | --- |
| Scientific query catalog | Which questions and entity/collection types are supported? What context, constraints and coverage make a response meaningful? | Sabueso #71/#112; shared packet meaning in MOLI #22 |
| Entity and representation scope | Identity for modified peptides, isoforms, constructs, FASTA/structure-file inputs; whether structure-level cards are needed; EFO identity without a MONDO anchor | Sabueso #112/#20/#96; modeling exchanges with their owners |
| Reproducibility and export | Distinguish stored state, source release, downloaded response and execution; decide reference-only versus self-contained exports, retention and missing-target outcomes | Sabueso #100/#53; shared references/retention in MOLI #3 and retrieval boundary in MOLI #33 |
| Literature validation | Rights of supplied fragments; extraction/validation, correction and retraction; trace a statement to its actual source location and retain extraction method/version | Sabueso #92/#29; project-to-knowledge promotion in MOLI #17 |
| Public contract stability | Guarantees for queries, explanations, terms, references and export; version/deprecation policy and historical readers for each new slice | Sabueso #112 and feature issues; shared commitments in MOLI |

Model-generated interpretations do not automatically become SourceAssertions.
Extracted statements need support in the external source; project conclusions need
an explicit curation/promotion boundary. See
[RISKS_AND_OPEN_QUESTIONS.md](RISKS_AND_OPEN_QUESTIONS.md) for the outstanding decisions
and [DECISIONS.md](DECISIONS.md) for adoption of this order.

This roadmap schedules work, not a release date or a frozen new API. Revisit the
order against both routes at each release and when real use exposes a blocker.

## Capability backlog and dependencies

The following entries retain the progress and remaining work from the foundational
review begun on 2026-09-29. Their numbering groups capabilities; the next development
order is the approved roadmap above.

1. **The disease as an entity (#90).** Released in 0.7.0: disease cards anchored at
   MONDO, a protein's diseases grouped through stated identity and MONDO's hierarchy,
   and a disease's targets and drugs. Open: EFO terms MONDO does not map (#96).
2. **What may be done with the knowledge (#29).** Released in 0.7.0: `Card.terms`,
   `Deck.terms`, `Deck.admissible`, depositor terms per PubChem assay, and terms
   profiles (#94). Released in 0.12.0: read-time
   `KnowledgePacket.terms(use, store)` for `packet_aspects@6`, with pinned support,
   separate bibliography/fragment terms and full/index parity. Next: historical
   scope adapters as use asks, and the shared vocabulary with MOLI.
3. **Scientific operations (#91).** Released in 0.7.0: `expand` (relationships into decks),
   `explain` (a deck member and a card's SourceAssertions), and the store's `as_of` and
   `changed_since`. Released in 0.11.0: an inventory item through
   `Deck.explain(card_id, structure_ref=..., ...)`, with the pinned relationship and
   SourceAssertion support of every group member (`structure_inventory_explanation@1`).
   Released in 0.12.0: `Card.explain_literature(publication_ref)`
   traces stored publication links and both legs of structural mention context,
   preserving alternatives and recorded unlinked requests (`literature_explanation@1`).
   Released in 0.13.0 `Card.explain_disease(disease_ref)` now explains MONDO disease
   groups with pinned association/selected-annotation support, identity/hierarchy
   steps, stored alternatives and whole-card ungrouped context. Versioned
   `disease_grouping@2`/`disease_group_explanation@2` (#115) retain all identity
   paths and leave conflicting or unfinished branches ungrouped. Explicit `@1`
   selection preserves historical behavior without replacing stored cards.
   Released in 0.13.0 `Card.explain_knowledge_state` now traces exact classification
   inputs, selected/alternative scientific support, coverage and request reports
   at original pins (`knowledge_state_explanation@1`). Missing support is partial;
   absence and missing queries never become negative assertions. #116 retains
   multiple original UniProt versions without changing the working state rule.
   Released in 0.13.0 measurement-group and molecule bioactivity-class explanations now
   retain actual joins, precision, copy/voter decisions, original quantities and
   exact pinned source support. Whole-card candidate/glossary context remains
   explicit. Released in 0.13.0 `Card.explain_ligand_site` and `Card.explain_ligand` now
   trace actual annotated overlap and protein/molecule crossing support at distinct
   card pins, with native deck snapshot/membership context. Duplicate members,
   absence/numbering/instance limits and original source conflicts remain explicit.
   Released in 0.13.0 `Card.explain_oligomer()` now retains actual partner/agreement rules,
   source assembly alternatives, exact family members, original support and
   historical pins under `oligomer_explanation@2`. The #120 correction defaults to
   agreement `@2`, computing only confirmed UniProt/1-based comparisons; unknown,
   incompatible or conflicted inputs keep explicit reasons and uncomputed sets.
   Explicit agreement `@1` reproduces the legacy view/explanation at historical
   pins. Readers remain inert; stored cards and packet source scope stay fixed.
   Other derived explanations remain open. The #118 correction counts distinct
   included groups across matched molecule items (`ligand_measurement_count@2`),
   retaining explicit source-record counts, selected rules and exact counted ids
   under `ligand_deck_explanation@2`. Explicit `@1` preserves the published numeric
   counter; scientific grouping/classes, stored cards and historical pins stay fixed.
   Missing activity-only copy diagnostics are corrected in #117.
4. **Literature beyond manual curation (#92).**
   - Released in 0.7.0: how each statement entered (`acquisition`: database, curation, rule
     extraction, model extraction, validation).
   - Released in 0.7.0: Europe PMC's text-mined accession mentions (`mentioned_in`). Its gene
     and protein annotations were reviewed and set aside: they ground names without
     the organism.
   - Released in 0.11.0: source access to located accession annotations for
     explicit articles (`get_annotations`), with provider, section and quote
     fragments. A public P60174 mention in a figure verifies the route. These
     fragments are not complete sentences. Released in 0.12.0:
     explicit UniProt accession intake into cards, with native article ids,
     per-occurrence locations and SourceAssertions, terms and refresh through the
     recorded article requests (schema 0.3.11). Supported PDB mentions are now
     derived `structure_mentioned_in` context through source-stated `has_structure`
     links, retaining both statements and separating them from direct UniProt
     mentions. Public 2JK2/Methods verifies it; unsupported 7QON remains unlinked.
     Released in 0.13.0: Sabueso runs `literal_uniprot_mention@1` on identified supplied
     fragments, returning detached per-occurrence SourceAssertions, supported
     relationships and original Ackredit attribution. It requires an explicit
     namespace/official URL; no names, bare accessions or biological findings.
     Explicit intake/replay is implemented for this literal rule through
     `Card.add_literature_extraction` and `ExtractionStore`: original support and
     supplied receipts survive reuse, storage and refresh without human relabeling.
     Payload-only refresh reports the missing original runtime sidecar. New scientific
     intake metadata uses published schema 0.3.12; 0.3.11 stays fixed.
     Explicit article metadata/declared terms are now implemented through
     `europepmc.get_article` and `article_metadata_binding@1`: source-stated identity,
     native authors/bibliography/licence, alternatives, original access/support and
     citations survive stored replay, refresh and pinned packet reads. Service
     version is not article revision; no abstract or full text is projected.
     Next: supplied-fragment rights, broader statement rules and validation; unknown
     fragment terms cannot bypass a source-admissibility profile.
     Literature packet coverage is published in `packet_aspects@6`
     (#71): both mention areas are indexed and their unknowns reported; automatic
     acquisition asks bibliography only, without guessing article ids.
   - Included in 0.11.0: a public review draft and hypothetical curation rehearsal
     (`examples/literature_curation/`), preserving outcomes and historical support on
     rebuild. The draft awaits human review; #105 prevents extraction provenance from
     being replaced with human curation during export/replay.
5. **Continuing, in parallel when a need or a slot appears:**
   - sources of wave 2 (#83), complete, orthology through OMA instead of Ensembl:
     ChEBI, KLIFS, GPCRdb, SAbDab, OMA and membrane segments through RCSB
     in use; the Chemical Probes Portal, SureChEMBL, OPM's own API, ESM Atlas and
     Ensembl deferred with their reasons; #85 closed through gnomAD's canonical transcript
     (follow-up #102). iPPI-DB, VEuPathDB and TDR Targets wait on #84;
   - isoforms and variants by tissue (#102): done in 0.10.0 (gnomAD's pext,
     `pext_at_variant@1`, `isoform_exon_usage@2`, tissues as GTEx's UBERON and EFO
     terms). Isoforms without a stated transcript stay without exons (Sabueso does not
     align); exons from Ensembl for the few transcripts gnomAD lacks, when a use needs
     them;
   - local mirrors in real work (#101): ChEMBL as a mirror, and builds from cached
     sources; postponed by the maintainers on 2026-10-01;
   - knowledge packets: real use decides their aspects (#71); an index level by
     reference since 0.10.0 (`packet_index@1`, #88), accepted in uibcdf/moli#22;
   - the clinical layer: adverse events (openFDA), after a terms review; isoform
     sequences (#80);
   - peptide cards: scope them before any source (use case 5, CPPsite).
6. **Contracts with other MOLI components**, raised in uibcdf/moli when those
   components are ready:
   - the reference form (uibcdf/moli#3, #53) and knowledge packets (uibcdf/moli#22);
   - exchange with TopoMT (positions, interface mutations), MolSysViewer (features to
     show) and PharmacophoreMT (ligand decks). Use cases 3, 4 and 7 are partial for
     want of these.
   - required Ackredit attribution for knowledge pipelines (#108, moli#36): the
     automatic packet-composition adapter and public offline workflow are
     implemented against the accepted portable contract assigned to Ackredit's
     published 0.9.0 provider (ackredit#75). Traceability is mandatory: the first
     source-acquisition slice records built-in UniProt/Europe PMC/RCSB access, including
     fixture/reuse/replay, empty answers, failure and original response identities,
     automatically on cards, resolutions and one-call packets. The public pilot
     saves those detached traces and credits completed access in the workflow.
     Released in 0.13.0 adds ChEMBL bioactivities, assay activities, molecules
     and indication operations: pagination/chunks, source totals/caps, original
     document citations, retries and received-page subsets remain observable even
     when the original exception escapes. Client-reported cached releases are
     explicitly not per-page release proof.
     Released in 0.13.0 also covers PubChem compound properties, structure
     matches and BioAssay target queries, including native per-assay revisions,
     caps/batches, PubMed pointers, declarative depositors, rejected inputs and
     received subsets on later failure. Unstated global versions remain unknown;
     assay summaries do not prove versions of every row or compound property.
     BindingDB REST/fixture/mirror affinity queries are also observed, retaining
     queries/cutoff bases, totals/caps/order, DOI/PubMed forms, declared origins and
     mirror manifests/releases, including empty and failed queries. REST versions
     remain unknown. The source-local #114 fix recognizes documented empty-string
     absence while malformed responses remain failed, retaining wire/archive identity.
     Released in 0.13.0 CCD batches and UniChem InChIKey/source-id
     lookups now retain query/response identities, reuse, retry/empty/failure outcomes
     and completed subsets. Linked databases stay declarative; versions stay unknown.
     Molecular resolution and ligand decks keep detached input/result pins and
     original resource-description citations without changing stored card/deck science.
     PDBe-KB ligand-site/interface aggregates also retain separate queries,
     native structural reference forms, archive reuse, empty answers and failures.
     Versions and missing underlying citations stay unknown; listed providers and
     structures do not become additional direct access.
     AlphaFold DB model queries retain original per-record ids/versions,
     tool/provider/URL declarations, archive reuse, empty lists and failures.
     Model versions do not become database releases or experimental revisions;
     generation and coordinate download are not executed by this access.
     InterPro family-site residue queries retain native signatures, locations,
     header/fixture releases, archive reuse and distinct empty/unavailable/failure
     outcomes. Empty answers cannot establish accession existence. Member-database
     declarations do not claim direct access, alignment or InterProScan execution;
     missing site/signature citations and release versions remain explicit.
     Other sources/custom clients, further result types and complete resource
     bibliography remain coverage work with explicit gaps in the published 0.13.0
     scope (#108). Ackredit 0.9.0 is publicly qualified on Python 3.11–3.14;
     its published minimum and exact public pins replace the source overlay and
     release blocker. Sabueso's own exact `py_1` archive passes all installed
     OS/minor gates, public installation and archival under #110. The provider interpreter contract is delivered under
     ackredit#80, without metadata overrides. The provider corrected explicit
     author-object BibTeX rendering in ackredit#78; the pinned candidate includes it.
     Knowledge support, runtime use and terms retain
     their separate meanings; scientific payloads are unchanged.
     MOLI owns ProjectRecord composition and future Recorda routing; the local trace
     is a receiving experiment, not an implemented platform provenance contract.
     Released in 0.13.0 `examples/persisted_pipeline/` exercises separate producer, reader
     and reuse processes: full/index packets, exact historical item reads, original
     extraction/article support and workflow credit survive reacquisition.
     Missing/changed/misbound sidecars and inconsistent workflow context are refused.
     Consumer-owned Nextia interpretation and shared Recorda/ProjectRecord acceptance
     remain with their owners.

Each is proposed as an issue before work starts, and the order is revisited at each
release.
