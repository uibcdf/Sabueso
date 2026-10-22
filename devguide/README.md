# Sabueso — Developer Guide

The developer guide is the repository's memory: what Sabueso is, how it is built, what
was decided and why, and what comes next. Start with `CHECKPOINT.md` and `ROADMAP.md`.
Contributors and agents also read `../AGENTS.md`.

To resume after a pause, read [CHECKPOINT.md, Resume here](CHECKPOINT.md#resume-here),
then [ROADMAP.md, Immediate resumption sequence](ROADMAP.md#immediate-resumption-sequence).
These separate published behavior, accumulated local work, latest qualification
and the next implementation/design steps. Detailed receipts remain linked; neither
a previous test count nor a diagnostic local wheel establishes a public release.

Every document is one of four kinds:
- **normative**: rules and contracts that code must follow;
- **living**: the current state, kept true;
- **design**: vision and architecture;
- **historical**: kept, not maintained.

The public [HK2 test system](HK2_TEST_SYSTEM.md) complements TcTIM/HsTIM with
current-source rebuilding and an integrated saved-card/report regression.

## Where to start

| Document | Kind | What it holds |
|---|---|---|
| `CHECKPOINT.md` | living | The current state: release, schema, layout, quality baseline, open work |
| `ROADMAP.md` | living | Both routes, objective status, and the approved next roadmap after 0.13.0: user journeys, query/traceability guarantees, peptides and parallel consumer contracts |
| `DECISIONS.md` | living (log) | Every design decision, dated, with its reason |
| `RISKS_AND_OPEN_QUESTIONS.md` | living | Risks for the future, and decisions to re-evaluate |

Release preparation and receipts live in `../devtools/conda-build/`: the committed
plan, route checklist, `release_notes_0.14.0.md` and the verified exact-artifact
publication receipt for the staged release (#134),
with immutable `release_notes_0.13.0.md` and its publication receipt (#121), plus the
immutable 0.12.0 notes/publication receipt (#110). Published state stays in `CHECKPOINT.md`; a preparation plan is
not a release receipt.
For future public GitHub Releases, the visible title is exactly the `X.Y.Z`
version, matching the tag and package version; descriptive text belongs in the
notes. The linked publication route includes this pre-publication check.

At task and release closeout, review the temporary environments, test output,
build trees and downloaded copies created for the work. Remove owned disposable
resources after their last needed use; retain exact release artifacts and
useful evidence with an owner and review trigger. Follow
`../MOLI_GUIDE.md#temporary-development-resources` and the local test/release
routes.

Published receiving correction: [compact comparative credit](pending_proposals/comparative_credit_compaction.md)
emits component operation `@2` with a versioned/hash-bound input-scope reference,
retaining every original pin/assertion and historical `@1` context. Four new
regressions, 172 selected and all 6,266 local-original cases pass. This later
source is qualified at `792bd0d`: [CI 15/15 and governance 1/1](pending_proposals/comparative_credit_compaction_checkpoint.json).
MOLI owns the separate [Recorda receiving PR #67](https://github.com/uibcdf/moli/pull/67)
and shared acceptance (#36); 19 public receiving cases and applicable governance pass
with this producer, and the PR is ready for owner review. Continue
[scientific usefulness review](pending_proposals/consumer_scientific_acceptance.md)
and the [proposed substantial release](pending_proposals/release_consolidation_0150.md)
through their separate acceptance routes.

The [support-provider receiving checkpoint](pending_proposals/support_provider_receiving_20261013.md)
qualifies updated editable DepDigest 0.15.1 and SMonitor 0.20.0 in the existing
Python 3.14 environment: 112 selected, all 6,266 local-original and 19 MOLI
receiving cases pass. Their new opt-in capabilities are not adopted by Sabueso;
runtime floors and installed-package qualification remain separate.

## Design

Current design work: [human exploration of Card](pending_proposals/card_human_exploration_api.md)
(#148) defines intuitive progressive navigation, complete access to retained content
and source-grounded decision assistance. Existing scientific engines and public
methods are the foundation; proposed names/types and human usability remain to be
validated. Bounded implementation is now authorized, with the
[human/agent access distinction](pending_proposals/card_human_exploration_api.md#human-and-agent-access-to-the-same-knowledge)
recorded before API integration. The documents themselves deliver no API or release.
The [agent access contract](pending_proposals/card_agent_access_v1_contract.md)
specifies direct technical access over the same captures/adapters, with exact
selection/projection, bounded pages, original support and explicit completeness.
Human usability, machine conformance and cost remain separate acceptance routes.
The [initial implementation](pending_proposals/card_access_literal.md) now adds
validated capture, literal discovery/read, bounded pages, typed locations/cursors
and raw export. Its initial literal capabilities excluded scientific selection and
saved exploration; the structural continuation below adds the first scientific
route. The [human literal slice](pending_proposals/card_exploration_literal.md)
adds `card.explore()` with labeled discovery/inspection, original support, local
search and bounded text/HTML previews over that same capture. The
[first structural adapter](pending_proposals/card_structures_exploration.md) now
shares the existing inventory/explanation with projected machine selection.
The [first human protein journey](pending_proposals/card_protein_exploration.md)
adds the scientific opening, function fields, explicit function/region questions and
direct original-source/return navigation. Broader nature-specific routes, shared
scientific coverage, portable saved exploration and researcher acceptance remain pending.
The [detailed proposal](pending_proposals/card_exploration_detailed_design.md)
recommends one additive exploration entry with distinct protein, small-molecule
and disease experiences, candidate calls, scientific routes and saved-result
contracts. The [v1 contract](pending_proposals/card_exploration_v1_contract.md)
resolves the five pre-implementation findings with concrete types, selection,
context, saved reading and bounded initial adapters. Public paper walkthroughs
use verified existing inputs; API implementation, interactive prototypes and
researcher validation remain open. The architectural direction remains unchanged.

The [saved-consumer usefulness review](pending_proposals/pilot_usefulness_review_20261021.md)
verifies original retained support with the current reader and prepares a private
assay/source-document queue. Complete methods and human scientific acceptance
remain open. Human exploration is the matter now being addressed during the
maintainer-requested pause before 0.15.0 consolidation; see the current checkpoint
before resuming implementation or consolidation.

The [bounded clinical bibliography journey](pending_proposals/clinical_bibliography_journey.md)
links one source-cited NCT and three explicit PMID selections to the original
molecular input, with separate source/workflow sidecars, inert saved reading and
clinical-only reacquisition. Its [source receipt](pending_proposals/clinical_bibliography_journey_checkpoint.json)
qualifies `2d294d8` with 6,326 local-original tests, CI 15/15 and governance 1/1.
Broader clinical coverage and scientific acceptance
remain under #108/#112.

The [criterion-integrity correction #146](archive/scientific_dossier_criterion_integrity.md)
binds saved dossier checks to their original inputs, including complete check
membership, expectations and unknown reasons. It closes a demonstrated coherent
report-editing gap without changing the original rules, cards or SDK API.

The [public scientific dossier](pending_proposals/scientific_dossier.md) supplies
an inspectable structure/assay/located-mention review using existing APIs. Sixteen
new independent-process cases and all 6,282 local-original cases pass;
[source CI 15/15 and governance 1/1](pending_proposals/scientific_dossier_checkpoint.json)
qualify `6e35c1d` with nine public lanes and four installed public-Ackredit lanes.
Exact historical support, original
units, explicit unknown/partial scope and preserved credit are technical acceptance,
with human usefulness and scientific interpretation still open.

The [bounded usefulness review](pending_proposals/scientific_usefulness_review.md)
now adds native assay/target/document inspection in dossier `@2`, with explicit
missing saved qualifiers and historical `@1` compatibility. Twenty selected and
all 6,286 local-original cases pass;
[source CI 15/15 and governance 1/1](pending_proposals/scientific_usefulness_checkpoint.json)
qualify `1bd8c05`, including nine public and four installed public-Ackredit lanes.
The [located primary-source review](pending_proposals/located_source_review.md)
now prepares two structural readings with original native text/support, separate
from card knowledge. Codex is the agent preparer; scientist review is pending.
Corrected `@2` refuses initial `@1` agent-curation bundles.
[Exact-source CI 15/15 and governance 1/1](pending_proposals/located_source_review_checkpoint.json)
qualify `4e513da`, including all public and installed public-Ackredit lanes.
The assay audit found incomplete protocol metadata; experimental comparability
and proposed installed delivery remain separate acceptance.
The subsequent [primary assay-method access review](pending_proposals/primary_assay_methods_review.md)
verifies the three shared document identities and their 497 stored activity rows
across twelve assays. No complete methods were obtained; the institutional PDF
was a library notice. It records the access gap without adding curated knowledge
or changing the qualified SDK source.

| Document | Kind | What it holds |
|---|---|---|
| `VISION.md` | design | Definition, mission, scope, platform context, non-goals |
| `ARCHITECTURE.md` | design | Layers, core objects, principles, what is planned but not built |
| `DATA_FLOW.md` | design | One resolution, end to end, and its invariants |
| `USE_CASES.md` | design | Use cases of both routes (status in `ROADMAP.md`) |
| `SCIENTIFIC_POTENTIAL.md` | design | Long-term scientific direction (non-binding) |
| `GLOSSARY.md` | design | Terms |

## Contracts and conventions

| Document | Kind | What it holds |
|---|---|---|
| `SCHEMA.md` | normative | Card schema, SourceAssertion and relationship contracts, versioning policy |
| `FIELD_PATHS.md` | normative | Canonical field paths (checked against the schema) |
| `PUBLIC_API.md` | normative | The public surface |
| `API_CONVENTIONS.md` | normative | Naming, inputs, view conventions |
| `INTERFACES_MINIMAL.md` | normative | Core interfaces: Card, Deck, stores, resolvers |
| `RESOLVER.md` | normative | FieldResolver contract and selection rules |
| `SELECTION_RULES_EXAMPLES.md` | normative | Selection rules, field by field |
| `SOURCE_ACCESS.md` | normative | Source clients, `get_*` functions and required acquisition traceability |
| `ARGUMENT_CONTRACTS.md` | normative | ArgDigest: one digester per argument |
| `DIAGNOSTICS.md` | normative | SMonitor codes and outcomes |
| `LICENSING_AND_COMPLIANCE.md` | normative | Source licences and obligations |
| `TESTS.md` | normative | Test kinds, fixtures, local gates |
| `LOCATION_EXAMPLES.md`, `UNIPROT_ENUMS.md` | reference | Verified examples and source enumerations |

## Sources, storage and size

| Document | Kind | What it holds |
|---|---|---|
| `sources/registry.yaml` | living (source of truth) | Every resource: in use, evaluating, queued, deferred, rejected, retired, out of scope |
| `sources/README.md` | normative | How sources are proposed, triaged and decided |
| `DATA_SOURCES_STATUS.md` | living | Technical detail of each source in use |
| `SOURCE_COVERAGE.md` | living | Knowledge areas, the source rubric, and evaluations by wave (#83) |
| `SOURCE_ARCHITECTURE.md` | living | Declared enrichers, the runner and shared services for many sources (#86) |
| `sources/FIXTURE_DELIVERY.md` | normative | Reviewed recovery file delivery, protected local originals and explicit public/local pytest scopes |
| `sources/NATIVE_ACCESS_REFERENCE.md` | living | Source-specific native protocols, fields, observation and qualification limits |
| `sources/DEVELOPMENT_API.md` | living | Unpublished recovered source reader/mapping APIs |
| `STORAGE_LAYOUT.md` | living | Knowledge store, files, recommended project layout |
| `CACHE_POLICY.md` | living | What is stored and what is not, and open questions |
| `CARD_SIZE_RISKS.md` | living | Card growth, measurements, mitigations |
| `DOCS_GAPS.md` | living | What the user guide lacks |

## Working folders

- `pending_proposals/private_consumer_revalidation.md`: bounded live/editable
  consumer execution, exact saved readers and original-answer replay (#132),
  measured costs, implemented NCBI Taxonomy operation observation (#108) and the
  correction separating a pre-import memory counter from actual process sampling.
  Original content/results stay private; broader consumer acceptance remains open.
- `pending_proposals/comparative_response_contracts_checkpoint.json`: qualified
  source correction for malformed OMA/UniRef/gnomAD/GTEx responses (#137), public
  regressions, exact-SHA CI and shared editable-environment verification. This does
  not qualify a new installed artifact or complete comparative operation coverage.
- `pending_proposals/post_recovery_public_checkpoint.md`: authorized code delivery,
  exact-SHA CI and private-consumer revalidation scheduling (#112/#132), with its
  [machine-readable receipt](pending_proposals/post_recovery_public_checkpoint.json).
- `pending_proposals/post_recovery_consolidation.md`: implemented input-delivery
  boundaries, guide restructuring, generated capability scope, protein residue
  integration, measured costs and owner-local consumer coordination (#112).
- `pending_proposals/post_recovery_global_audit.md`: architectural alignment,
  measured source expansion and the proposed consolidation/delivery acceptance
  after stash closure (#112). This distinguishes useful native access from complete
  scientific journeys and preserves the approved development order.
- `pending_proposals/historical_provider_reactivation.md`: seven recovered sources
  deferred after complete actionability review (#83/#95). Each has an explicit
  reactivation trigger and native requirements preserved independently of the stash.
  This does not add active implementation work without new input/access.
- `pending_bugs/`, `pending_proposals/`: analyses of active issues, each tied to its
  issue.
  `pending_proposals/design_implementation_review.md` compares original design,
  scientific capabilities and current implementation, with concrete gaps and owning
  acceptance criteria (#112). Its
  [quality completion proposal](pending_proposals/design_implementation_review.md#quality-completion-proposal-2026-10-09-112)
  records the accepted bounded inspection, explanation, literature, cost and delivery acceptance
  within the approved roadmap.
  Development comparative explanations and their standalone public
  `examples/user_journeys/comparative_support.py` reader retain exact sequence and
  tissue support (#91). Development scoped tissue rules correct historical limits under #138;
  [their scope](pending_proposals/comparative_tissue_scope.md) preserves explicit legacy rules and reports;
  operation/bibliography coverage is still #108.
  The [scoped tissue source receipt](pending_proposals/comparative_tissue_scope_checkpoint.json)
  records code `3bc1c53`, 5,819 local-original cases, explicit legacy reproduction,
  schema 0.3.14 migration/refresh and 15/15 exact-SHA CI jobs. Broader declared-source
  refresh routing now uses the declarations and preserves recorded request arguments
  under #139; [its scope](pending_proposals/refresh_request_scope.md) and
  [source receipt](pending_proposals/refresh_request_scope_checkpoint.json) record
  code `ff32cb6`, 5,896 local-original cases and 15/15 exact-SHA CI jobs.
  Comparative observation/bibliography #108 follows this correction.
  The [development GTEx slice](pending_proposals/gtex_observation.md) adds actual
  tissue access, requested-label/revision distinctions and original portable
  resource credit; 34 new regressions and 5,930 local-original cases pass at
  `2b5db53`, with 15/15 exact-SHA CI and governance. The
  [source receipt](pending_proposals/gtex_observation_checkpoint.json) also records
  4,377 cases per public offline lane and 1,015 per public-Ackredit lane.
  [Development UniRef observation](pending_proposals/uniref_observation.md) now
  retains page releases, caps, partial failures and portable resource credit;
  code `c6cb0e3` passes 5,963 local-original cases and 15/15 exact-SHA CI.
  [Its source receipt](pending_proposals/uniref_observation_checkpoint.json) preserves
  public/installed compatibility scopes. The [pagination correction #140](archive/uniref_pagination.md) is
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
  is locally verified at `31b6255` for three explicit-context Card views, with
  separate execution records, input-field support and inert saved readers. Full
  bibliography and broader result/consumer scope remain open under #108/#132.
  The block is published and source-qualified at `25f6163`: CI 15/15 and governance
  1/1 pass; the [block receipt](pending_proposals/comparative_block_checkpoint.json)
  verifies complete receptor captures and all exact-source test scopes.
  [TESTS.md](TESTS.md#recovering-deferred-ci) records the approved batching policy
  and manual recovery of all applicable CI/governance jobs on the exact final SHA.
  [Persisted comparative journey attribution](pending_proposals/comparative_journey_attribution.md)
  connects those records to example `@3`, with original results, inert reading,
  bibliography export and retained historical execution gaps. Local selected checks
  pass; publication and exact-source qualification are complete at `25f6163`.
  [Verified comparative bibliography](pending_proposals/comparative_bibliography.md)
  supplies scoped gnomAD/GTEx resource and pext method descriptions; actual native
  revisions and entry-study bindings remain unknown. Original readers retain old
  references. 278 selected and all 6,262 local-original cases pass. The later block
  receipt qualifies every CI/governance gate at `25f6163`; the earlier publication
  snapshot retains its original pending state.
  The [comparative explanation receipt](pending_proposals/comparative_explanations_checkpoint.json)
  records code `3fa2fdf`, 5,768 local-original cases, 45 new regressions and
  15/15 exact-SHA CI jobs. It qualifies development source, with installed delivery
  and human usefulness review remaining separate.
  `pending_proposals/independent_user_journeys.md` scopes the three standalone SDK
  journeys, the implemented protein comparison, molecule/target and bounded disease
  examples, exact disease membership support, conservative whole-context admission
  and remaining filtering by terms of use, clinical, query and observation gaps
  (#112, #29/#91/#71/#108). The source-state
  correction is delivered in qualified 0.14.0 under versioned rules (#122).
  `pending_proposals/ackredit_knowledge_pipeline_attribution.md` records the required
  pipeline attribution plan (#108, moli#36), its automatic composition and bounded
  acquisition adapters (including development ClinicalTrials.gov native references
  and explicit Europe PMC bibliography), and remaining coverage/publication gates.
- `templates/report.md`: the report template (MOLI reporting protocol).
- `archive/`: resolved reports and superseded documents, indexed in
  `archive/README.md`. The original plans are there, and `ROADMAP.md` still tracks them.

## Keeping the guide true

- A change that makes a line false updates it in the same commit. This applies to
  `CHECKPOINT.md`, `PUBLIC_API.md`, `FIELD_PATHS.md`, `SCHEMA.md`, `TESTS.md` and the
  registry.
- A decision goes to `DECISIONS.md`. A possible future problem goes to
  `RISKS_AND_OPEN_QUESTIONS.md`, with an issue when it needs a decision later.
- Each release reviews `ROADMAP.md` against both routes, and updates `CHECKPOINT.md`.
- A superseded document is archived with a note that says what replaced it, never
  deleted.
- Public documents never carry confidential pilot content; pilot needs are phrased
  generically.
