# Sabueso — Tests and Quality Gates

Select verification by changed behavior and state its scope. Detailed provider
cases are in [the native test reference](sources/NATIVE_TEST_REFERENCE.md); dated
receipts remain [archived](archive/consolidation_2026-10-08/TESTS.md). A passing
source test does not complete a scientific journey, consumer contract or release.

## Running the tests

Use Python 3.14 in the existing editable `molsyssuite@uibcdf_3.14` environment.
Install Sabueso and participating installable workspace packages from their local
checkouts with `python -m pip install --no-deps --editable .`. Verify editable
metadata and import paths outside the checkout. Keep installed-artifact
qualification separate from workspace development.

Public/repository-input offline suite:

```bash
python -m pytest -n 12 -m "not online" --receptor=llm
```

Full local suite including verified unshared native originals:

```bash
python -m pytest -n 12 -m "not online" --receptor=llm --local-source-inputs
```

The default excludes 25 native-only modules before import and explicitly skips
ten mixed native cases. Synthetic binding/malformed-input and public sequence-axis
tests remain active. The local option verifies original digests and includes that
coverage; unavailable or changed originals fail before collection. See the exact
[fixture delivery scope](sources/FIXTURE_DELIVERY.md). Test counts must identify
which command ran. Historical 5,554-case receipts precede this separation.

For a smaller changed scope, append its individual test paths. A private pilot
execution, an online test and a public fixture replay are different acceptance
routes. Run online tests only for an authorized concrete source/use scope; a
fixture does not establish current live availability.

## Test kinds

- Unit/contract tests verify errors, identities, assertion support, quantities and
  transformations, including deliberately synthetic parser inputs.
- Native response tests preserve qualified original wire/file content and scopes.
- Integration tests combine resolution, cards/decks, packets, persistence and
  original runtime/bibliography sidecars.
- Independent-user tests exercise separate producer, inert reader and reacquisition
  processes outside the checkout with exact original support.
- Installed-artifact tests establish the behavior and complete dependency closure
  of the exact built/published package, independent of workspace imports.

## Behavior-based gate selection

| Changed behavior | Select these test files / gates |
| --- | --- |
| Public arguments/diagnostics | `tests/core/test_argument_contracts_offline.py`; owning API cases; SMonitor/diagnostic cases |
| Captured contextual navigation | `test_card_context_navigation_offline.py`, human/access/argument and native structural/coverage cases; exact return/profile transitions, original source and endpoint links, missing/ambiguous context, supported identity graphs, duplicate/revision/pin handling, mutation/cycle/cache isolation and bounded escaped display (#148) |
| Initial nature profiles and coverage | `test_card_nature_exploration_offline.py`, human/access/argument, native knowledge-state/explanation and quantity cases; exact source/quantity/method support, hierarchy/identity separation, typed literal keys, unrecognized shapes, original state/count parity, lazy capture/explanation cache, no new attribution and bounded escaped previews (#148) |
| Human protein journey | `test_card_protein_exploration_offline.py`, human/access/argument and native structural cases; supported field values, original assertions/back navigation, explicit canonical region/identity guards, shared cache, preserved unknowns and bounded escaped previews (#148) |
| Shared structural exploration | `test_card_structures_exploration_offline.py`, original structures/inventory/explanation/knowledge-state and human/access/argument cases; exact existing outputs, original support/rules/exclusions, scope gaps, shared cache, typed units, projected byte limits, complete deferral and navigation (#148) |
| Human literal Card exploration | `test_card_exploration_offline.py`, literal access and argument contracts; shared one-time capture, full typed locations, complete item sequences, original support/conflicts, navigation/selection identities, Unicode search, bounded escaped rendering and preserved quantity units (#148) |
| Bounded literal Card access | `test_card_access_offline.py`, argument, quantity, knowledge-store and Card schema/policy cases; exact reconstruction and snapshot locations, fixed byte/record limits, foreign/retry cursors, Unicode/large-key deferral, quantity codec/seal, no scientific/source calls and atomic export (#148) |
| Source/assertion identity and acquisition | `test_source_assertions_offline.py`, `test_source_acquisition_offline.py`, `test_source_access_offline.py`; owning source/mapping cases |
| gnomAD operation observation / prerequisites | `test_gnomad_acquisition_offline.py`, source/acquisition/refresh and comparative journeys; actual GraphQL aliases/revisions/count bases, unavailable fixtures, partial failure, exact pins, inert readers and no source client without gene identity (#108/#141) |
| Open Targets upstream prerequisite | `test_disease_source_acquisition_offline.py`, disease associations, enrichers, knowledge-state and refresh cases; forbidden constructors/calls, no operation/resource credit, actual native non-binding outcomes, exact valid-gene science and historical pinned refresh (#142) |
| Source-local upstream prerequisites | `test_source_prerequisites_offline.py`, owning DISEASES/ClinVar/SKEMPI/SAbDab/disease-card, enrichers, knowledge-state and refresh cases; forbidden clients, unknown counts, actual empty/missing/failing outcomes, retained source credit and original/corrected pins (#143) |
| Derived disease identity coverage | `test_disease_identity_coverage_offline.py`, disease-card/explanation/journey, packet and packet-terms cases; exact identifier diagnostics, blocked/failed/unknown/mixed scope, MedGen UID prerequisites, historical @1/@2 rules and @6 packets, inert readers and original pins (#144) |
| Comparative native response contracts | `test_comparative_response_contracts_offline.py`, OMA/UniRef/gnomAD/GTEx cases; malformed and unanswered envelopes stay connector failures, while explicit empty/null answers preserve absence (#137) |
| Comparative genomic scope | `test_scoped_tissue_usage_offline.py`, gnomAD and migration cases; wrong/missing assemblies and chromosomes, transcript versions, union coverage, overlapping conflicts, nullable tissue values, explicit legacy behavior and both independent report formats (#138) |
| Comparative explanations | `test_comparative_explanation_offline.py`, `test_comparative_support_journey_offline.py`; exact sequence/tissue pins, selected/alternative support, actual genomic intersections, term joins, incomplete/foreign scope, historical rules and inert independent readers (#91/#138) |
| Comparative execution observation | `test_comparative_operations_offline.py`, comparative/explanation/scoped-tissue, attribution and packet cases; exact ordinary-view science, explicit-context execution, reused input support, historical rules, genuine provider absence/failure, changed/misbound pins and independent inert saved bibliography (#108) |
| Persisted comparative journey | `test_comparative_support_journey_offline.py`, comparative operation/explanation/scoped-tissue, attribution and packet cases; `@3` result/support/credit bindings, workflow union, partial support, immutable original exports, distinct reacquired executions, historical `@1`/`@2` compatibility and refusal of rehashed/misbound sidecars (#108/#112) |
| Comparative bibliography | `test_comparative_bibliography_offline.py`, comparative/journey, gnomAD/GTEx/source acquisition, attribution and packet cases; complete verified collective-author exports, pext-only real method-description credit, unknown native revisions/entry studies, unavailable/failed access and invalid support, inert original readers and misbound method scope/citations (#108/#112) |
| Native supplied files | `tests/tools/test_source_snapshot_offline.py`, `test_bound_native_snapshots_offline.py`; affected source tests with applicable public/local scope |
| Source registration/card contribution | `test_source_registry_offline.py`, `test_enrichers_offline.py`, knowledge-state and packet coverage; `tools/source_registry.py --check` |
| Fixture delivery | `test_fixture_delivery_offline.py`, `test_fixture_licensing_offline.py`; `tools/fixture_delivery.py --check`; prove public tests with local inputs absent |
| Identity/relationships/selection | Owning resolver/mapping/aggregation/conflict tests; no sequence/name/number similarity merge |
| Card/schema/migration | Card, migration and frozen-card tests; `tools/card_shape.py`, `tools/validate_schema.py`; unpublished additive changes only |
| Refresh request scope | `test_refresh_scope_offline.py`, enricher/migration/source-acquisition and owning fixture cases; every declared selector, failed/blocked/excluded requests, nondefault parameters, historical gaps, conflicts before acquisition, caller overrides and exact original pins (#139) |
| Quantities | Quantity/measurement/native-unit tests, seals and non-default unit policy across serialization and consumers |
| Pinned persistence/packets | `test_knowledge_store_offline.py`, `test_knowledge_packets_offline.py`; historical pins, tampering, foreign/missing states, migration |
| SQLite connection lifetime | `test_sqlite_lifetime_offline.py`, `test_storage_offline.py`, `test_deck_meta_offline.py`; explicit closure on success, empty reads and failures, committed round trips and rollback of failed deck replacement (#133) |
| Derived residue knowledge | `test_residue_knowledge_offline.py`, `test_residue_tracks_offline.py`, `test_residue_composition_offline.py`; declared axes, support and ambiguous denominator |
| Terms/admission | `test_terms_offline.py`, `test_packet_terms_offline.py`, `test_disease_deck_admission_offline.py`; original kept/excluded support |
| Attribution/literature/clinical | Source acquisition and relevant attribution/extraction/article/reference tests; original portable sidecars and bibliography gaps |
| GTEx access observation | `test_gtex_acquisition_offline.py`, owning GTEx/acquisition/attribution/refresh cases; requested dataset versus unknown revision, returned versus selected rows, fixture unavailable/failed/empty states, archive replay/retries and an independent inert pinned reader (#108) |
| UniRef page observation | `test_uniref_acquisition_offline.py`, owning UniRef/acquisition/attribution/refresh cases; individual page releases, caps, continuation, partial failure, fixture availability, replay/retries, scientific equivalence and independent inert pinned reading (#108) |
| UniRef pagination termination | `test_uniref_acquisition_offline.py`; empty/nonempty cycles, distinct empty chains, logical-page versus nested transport retry budgets, exact boundary exhaustion, row-ceiling precedence, failed card support and original archive reuse/replay (#140) |
| OMA operation observation | `test_oma_acquisition_offline.py`, owning OMA/acquisition/refresh/comparative cases; OMA versus UniProt name-resolution sources, native revision gaps, batch ambiguity/partial failure, local input availability, selected-row scope, retries/replay, exact scientific equivalence and independent inert reading (#108) |
| Independent scientific journeys | `test_user_journeys_offline.py`, `test_molecule_target_journey_offline.py`, `test_disease_entities_journey_offline.py`, `test_clinical_bibliography_journey_offline.py`; public examples and original readers |
| Scientific review dossier | `test_scientific_dossier_journey_offline.py`; explicit structural/assay criteria, native quantities/context, located-mention scope, exact support and original credit, independent inert reading and reacquisition, historical `@1` and native-context `@2`, missing qualifiers versus source absence, complete criterion inputs/outcomes/unknown reasons, refusal of coherently edited and rehashed artifacts with regenerated Markdown and original-stage isolation (#146) |
| Located primary-source review draft | `test_literature_source_review_journey_offline.py`, literature/curation-store/article and fixture-delivery cases; native publication/subject/rights, agent preparation with pending scientist review, drafts outside card knowledge, refusal of imported curations and unqualified @1, inert separate reader, rehashed semantic/provenance changes and preserved exports |
| HK2/notebook reports | `test_hk2_test_system_offline.py`, `tests/tools/test_card_notebook_offline.py`; exact saved card/report regeneration |

Core filenames in the table are relative to `tests/core/` unless another directory
is stated. Broaden the selected scope when changes affect shared contracts, schemas
or multiple routes. The full offline suite is a code checkpoint; it is not required
for every documentation-only or exploratory change.

## Clinical registry and bibliography guards in development

Native ClinicalTrials.gov study/reference observation, exact integrity, explicit
Europe PMC bibliography and collective authors preserve separate requested scopes,
original sidecars, missing/failed/unqueried states and publication pointers. The
[clinical report](pending_proposals/clinical_registry_checkpoint.md) records its
receipts; complete clinical breadth and bibliography remain #108 work. The separate `clinical_bibliography_example@1` journey selects one native NCT
and three PMID from the unchanged molecule input. Its independent subprocess
tests cover original pins/exports, distinct clinical-only reacquisition, absent
local files, failed registry access, missing PMID/module versus explicit empty
references, no citation parsing and refusal of coherently rehashed edits. The
saved reader forbids source clients, SDK scientific views and new credit.
These fixture checks do not establish live availability or clinical usefulness.

## Traceability and extraction guards delivered in 0.13.0

Per-source acquisition cases cover native bytes, query/time/version bases,
empty/failure/reuse/retries/cuts and detached traces. Attribution, extraction,
article metadata, pinned explanation and persisted-pipeline cases retain original
scientific support separately from observed execution and bibliography. Saved
readers forbid source access, derivation and new credit. Source-specific coverage
and the detailed delivered cases remain in the archived test descriptions and
[SOURCE_ACCESS.md](SOURCE_ACCESS.md).

## Independent-user journey acceptance (#112, after 0.13.0)

The [journey acceptance report](pending_proposals/independent_user_journeys.md)
records protein/comparator, molecule/activity and bounded disease/entity behavior.
Examples live in `examples/user_journeys/`; regression tests run producers/readers/
reacquisition in independent processes and reject modified or misbound artifacts.
Original reports preserve their named format/rules and gaps. A current reader must
not silently recompute an old report under new rules.

Public TcTIM/HsTIM/HK2 inputs provide generic acceptance without private program
content. Real consumer-owned Evidence, modeling and shared Recorda interpretation
remain independent owner-local integration work; stand-in consumers cannot close
those contracts.

## Fixtures

Frozen public source responses keep their own declarations in `temp_data/NOTICE.md`.
No private/pilot data enters fixtures. Preserve source, date, applicable licence,
native revision basis and modifications. Code MIT does not license source data.

The reviewed recovery inventory records repository versus local-only file delivery.
Local-only originals are ignored and rejected from the Git index by the delivery
gate; they remain available for explicit local native qualification. New fixtures
need reviewed file decisions; changed bytes or source terms invalidate an old
receipt. Unknown permission never becomes permission through a successful test.

## Local checks and CI checkpoints

Run each applicable gate separately and read its result:

```bash
ruff format --check .
ruff check .
python tools/fixture_delivery.py --check
python -m pytest -n 12 -m "not online" --receptor=llm
python tools/card_shape.py
python tools/source_registry.py --check
python tools/validate_schema.py
python devtools/moli_governance.py
python devtools/dependency_preflight.py
```

When local native source code changes, include its explicit qualification selectors
and a full local checkpoint as appropriate. Public CI validates its available
repository-input scope; retain local-original receipts separately. Do not pipe a
gate through `tail`/`grep` or chain a commit after a command whose exit code does not
reflect the gate.

Linux Python 3.14 CI promotes unclosed-database ResourceWarnings and pytest
unraisable-exception warnings to errors (#133). The connection context manages
transactions, not lifetime: SQLite readers/writers use `closing` around it, and
direct test queries also close their handles. For a local checkpoint use
`-W "error:unclosed database:ResourceWarning"` and
`-W error::pytest.PytestUnraisableExceptionWarning`; unrelated ResourceWarnings
are not suppressed or promoted by the database-specific filter.

Documentation/evidence changes need applicable link/example/generated-content
checks. When `docs/` or a docstring changes, build with warnings fatal:

```bash
sphinx-build -W --keep-going -b html docs <output directory>
```

Use the provisioned docs dependencies with the checkout installed. Nitpicky `-n`
is additional qualification; unresolved references from that run are not a passing
nitpicky receipt. Source shape and published frozen-card gates remain separate.

Batch short exploratory commits locally when remote visibility is unnecessary.
The maintainer-approved direct-push policy also permits `[skip ci]` on intermediate
tested code when no immediate remote gate is needed. Run the applicable local
checks first; a full offline checkpoint can cover several short commits while
its code, inputs, environment and scope remain applicable. Repeat affected tests
when subsequent changes invalidate that result. Use twelve pytest-receptor workers
for routine local pytest. Passing Linux editable tests does not qualify the other
supported OS/minors or the installed public dependency route.

Record every deferred code block's actual head SHA, changed/tested scope, missing
remote gates, owning issue and recovery route in its issue and checkpoint record.
The [current deferred block](pending_proposals/deferred_ci.md) is locally verified,
with remote qualification pending. A skipped or older run is never current passing
evidence. Required PR checks and immediate security, dependency, packaging,
migration or integration gates cannot be deferred with this marker. Published
release candidates and installed-artifact admission retain every mandatory gate.

### Recovering deferred CI

Finish a block with an unskipped push and inspect the resulting exact-head CI and
governance runs. Alternatively, after explicit authorization, dispatch both
workflows against the published `main` head. Both support `workflow_dispatch`;
CI includes default-branch coverage publication on manual `main` runs, as on pushes.
The weekly scheduled run alone does not cover governance or coverage publication.
For the manual route, record the candidate before dispatch:

```bash
candidate_sha=$(gh api repos/uibcdf/sabueso/git/ref/heads/main --jq '.object.sha')
test "$(git rev-parse HEAD)" = "$candidate_sha"
gh workflow run ci.yml --repo uibcdf/sabueso --ref main
gh workflow run moli-governance.yml --repo uibcdf/sabueso --ref main
gh run list --repo uibcdf/sabueso --workflow ci.yml --event workflow_dispatch \
  --commit "$candidate_sha" --json databaseId,headSha,status,conclusion,createdAt,url
gh run list --repo uibcdf/sabueso --workflow moli-governance.yml --event workflow_dispatch \
  --commit "$candidate_sha" --json databaseId,headSha,status,conclusion,createdAt,url
```

Run each command separately and inspect its result; stop on failure or a changed
head. Identify the newly dispatched run IDs by workflow, event, SHA and creation
time. Follow each through gh-run-receptor with full captures:

```bash
gh-run-receptor watch <run-id> --repo uibcdf/sabueso --profile ci \
  --capture full --interval 30 --max-interval 30 \
  --output <checkpoint-directory> --receptor llm
```

Verify both runs' `headSha` against the recorded candidate. Check every job's
conclusion and full test summary, not just the workflow's overall green status.
The current matrix has thirteen test lanes (nine public OS/Python lanes and four
installed public-Ackredit lanes), Ruff and coverage publication, plus the separate
governance job. A missing, skipped, cancelled or failing applicable job leaves
qualification pending. Record run URLs and retained captures in the owning issue
and checkpoint receipt. If `main` has advanced, these results qualify only the
recorded candidate; the newer head still needs its own applicable checks.

GitHub's conclusions remain authoritative; native `gh run view` is the fallback.
Source/data delivery must pass before claiming a public qualified code checkpoint,
then [staged installed-package gates](../devtools/conda-build/README.md) qualify
releases across the required OS/minor matrix. Direct development publication with
deferred CI must be labelled as such and never presented as a qualified checkpoint.

## Quality rules for knowledge

- Every selected value retains supporting SourceAssertions; selection preserves
  alternatives and conflicts. Relationships retain their exact assertion support.
- Physical quantities keep `{value, unit}` and verified seals through boundaries.
- Derived classes/groups/states/findings carry named versioned rules and are never
  stored as SourceAssertions.
- Identity merging requires source-stated correspondence; equal names, sequences
  or residue numbers are insufficient.
- Missing, failed, unasked, unavailable and source-stated absence remain distinct.
- Every pin returns its original verified state or fails; it never falls back to
  a newer state. Independent saved readers add no acquisition or credit.
- Each receipt identifies code/artifact, input scope, environment and applicable
  limits; a local diagnostic wheel is not a public release.


Compact comparative credit qualification includes
`tests/core/test_comparative_credit_size_offline.py` together with comparative
operation and saved-journey readers: proportional host/workflow serialization,
exact owner/scope hashes and historical full contexts. This protects serialization
scale; it does not qualify whole-workflow memory, scientific algorithm complexity,
consumer routing or installed artifacts.
