---
issue: uibcdf/sabueso#112
status: active
---

# Independent-user journey acceptance

The maintainer-approved [next roadmap](../ROADMAP.md#next-roadmap-after-0130)
starts with three scientific journeys. This audit uses existing public SDK routes,
source declarations and public fixtures, without private pilot content. A running
example closes its declared scope, not every source, query or platform contract.
The accumulated implementation is now included in the maintainer-authorized
2026-10-06 code checkpoint. Dated local/uncommitted qualification statements
below describe their original receipt state; current delivery and exact CI
are recorded in `../CHECKPOINT.md`, Resume here.

The 2026-10-08 consolidation adds bounded source-active-site residue/composition
context to protein example `@2`, with pinned source support and an independent
reader that still accepts original `@1` reports. Dedicated derived-operation
observation and cross-protein residue correspondence remain absent. See the
[consolidation report](post_recovery_consolidation.md) for current scoped gates,
cost measurements and consumer-owned acceptance; historical receipts below remain
dated evidence of their original implementation.

## Journey matrix

Development `comparative_support.py` adds an independent public sequence/tissue
support journey (#91). It preserves P52270/Q4DV43 sequence explanations and P60174
variant/isoform/term explanations at exact pins through later fixture reads.
Source access, fresh derivation and credit are disabled in reader regressions.
Development comparative format `@2` includes genomic-scope/coverage correction;
its reader also retains historical `@1`, with explicit legacy production and
format-preserving reacquisition (#138).
Development [format `@3`](comparative_journey_attribution.md) now persists ordinary
results, original source/comparative/workflow records and inert bibliography export
after reacquisition. It preserves original `@1`/`@2` rules and execution gaps.
This changes none of the other three journey formats and does not qualify live
availability or an installed artifact. Publication/remote qualification for this
slice remain pending. See [the explanation scope](comparative_explanations.md).

| Journey | Existing route and support | Initial slice / remaining gap |
| --- | --- | --- |
| Protein and comparator | `resolve(EntityQuery(...))`, `Card.compare_knowledge`, `ligand_deck`, `Card.compare_ligands`, full/index `compose_packet`, pinned `KnowledgeStore` reads; public TcTIM/HsTIM fixtures | `examples/user_journeys/protein_comparison.py` exercises independent producer/reader/reacquisition with original reports, units, support and runtime sidecars. Positions without a residue map remain unaligned. General semantic constraints and other derived explanations remain #71/#91 work. |
| Molecule and activities | `resolve_molecule_card` provides stated identity, physchem and optional indications/cited trials. Activities belong to target-protein `has_bioactivity` relationships; `Card.ligands(deck)` crosses target activity with molecular identity | `examples/user_journeys/molecule_target.py` exercises public BTS/benznidazole against a declared TcTIM target, original assay/identity/indication statements, saved reader and reacquisition. Other targets/trials remain unqueried; general reverse queries remain #71/#83. The #122 source-state correction is local under versioned rules; published delivery is pending. Development ClinicalTrials.gov study/reference observation and explicit Europe PMC bibliography are implemented (#108/#127/#128); clinical breadth remains partial. |
| Disease and related entities | MONDO-anchored `resolve_disease_card`, `disease_targets`, `disease_drugs`, membership/source outcomes, pinned decks; MONDO, Open Targets, Orphanet and ChEMBL public fixtures | Development rules `@2` retain native membership/input/member identity pins. Example `@5` adds DISEASES/ClinVar/MedGen to existing MONDO/Open Targets/Orphanet observations, exact disease-build traces and original workflow credit through readers/reacquisition. Native ChEMBL indication references now contribute portable pointer citations with exact observed occurrence scope. Original `@1`/`@2`/`@3`/`@4` reports keep their gaps. Conservative whole-context admission is local (`disease_deck_admission@1`), with SDK gates independent of example receipts. Complete acceptance still needs full underlying study bibliography (#108), finer filtering by terms of use (#29), and non-protein packets (#71). Unstated EFO identity remains unresolved (#96). |

## Protein comparison acceptance

The example selects four explicit RCSB entries, reads activity fixtures and creates
ligand decks under source-stated identity. It preserves name/organism resolution,
alternative identities, source conflicts and knowledge states. One missing public
RCSB fixture demonstrates unavailability without claiming external absence.

The independent reader needs no fixtures, refuses missing/modified/misbound
original files, and reads both proteins' exact SourceAssertions through saved
index packets. It registers no credit and makes no source calls. The original
producer report is retained rather than recomputed using current reader rules;
physical quantities serialize as `{value, unit}`. Reacquisition advances current
heads while original card/deck/packet support and portable attribution survive.
Representative activity, measurement-group and shared-ligand explanations retain
their named rules and exact pinned inputs alongside the producer's original report.

The example's manifests do not define a shared provenance contract. Broader
observation is #108; packet/query expansion is #71; remaining derived explanations
are #91. Real Nextia Evidence acceptance and platform recording remain with MOLI
#3/#22/#36 and the consumer owners.

## Documentation and next acceptance

- The user guide introduces the comparison and original saved-support workflow in
  `docs/content/user/journeys.md`.
- A dedicated small-molecule page explains identity, physchem, clinical scope and
  the protein/molecule activity crossing without promising a reverse activity search.
- The user-facing coverage table states what the sources in these journeys supply,
  what they do not establish, and which runtime boundaries remain unobserved.
- Next, extend underlying study bibliography beyond the bounded ClinicalTrials.gov/Europe PMC slice (#108); native
  disease membership/input support (#91), disease-deck build traces and
  MONDO/Open Targets/Orphanet observation/integrity (#108/#123/#124)
  are now local. The bounded saved-reader example exists;
  full disease acceptance remains open. The molecule source-state correction (#122)
  remains local with published delivery pending. Report concrete gaps in their
  owning feature issues before changing public APIs.
- The larger live showcase notebook still needs a fresh execution and review;
  this offline example does not establish availability of current online providers.

## Protein-slice validation checkpoint (2026-10-05)

- Primary development: Python 3.14.7 in `molsyssuite@uibcdf_3.14`; outside-checkout
  imports and editable metadata verified for all 14 installed workspace packages;
  pip check passes. The seven journey regressions pass.
- Installed public SDK: copy the unchanged example, tests and declared public
  fixtures outside the repository. All seven regressions pass with Sabueso 0.13.0,
  Ackredit 0.9.0, PyUnitWizard 0.27.0 and published pytest-receptor 1.2.0 on
  Linux/Python 3.14.7. Sabueso/Ackredit imports resolve to installed site-packages.
- Final full offline checkpoint: 1933 passed, 26 online cases deselected, using
  `python -m pytest -m "not online" --receptor=llm` (257.40 seconds). Five expected
  fixture-failure/truncation warnings remain; they are not online-source acceptance.
- Ruff format/check and `git diff --check` pass; Sphinx builds with `-W --keep-going`
  using the existing Python 3.14 documentation environment. Added local Markdown
  links/anchors resolve.
- The first full run exposed the Europe PMC registry access label still saying
  "unreleased" while its generated user page already said "since 0.12.0". Correct
  the canonical registry and regenerate, rather than restore an obsolete label.
  The registry check and its 16 regressions pass; packaged source terms are unchanged.
  The defect/correction is recorded in
  [source coverage #83](https://github.com/uibcdf/sabueso/issues/83#issuecomment-6000844693).
  Query scope inputs are recorded in
  [#71](https://github.com/uibcdf/sabueso/issues/71#issuecomment-6000874207).

This is bounded SDK/example acceptance, not another package build, full OS/minor
matrix, live-provider validation or consumer-owned MOLI contract acceptance.

## Molecule/declared-target acceptance (2026-10-05)

The example selects two explicit molecular identifiers and one protein target.
BTS's source-stated identity connects a ChEMBL measurement and CCD/RCSB structural
context; benznidazole's identity connects its single-point/undetermined measurements
and ChEMBL clinical indications. The selection deck is local application input,
not an inferred molecular class or observed source operation. The broad target-context
index packet remains distinct from the report's narrower two-molecule question.

The producer retains original named explanations, assay/target/quantity/publication
context, original pinned identity and indication support, conflicts, terms and
per-card/operation/workflow attribution. Readers inspect saved support without
rerunning the producer's rules or fetching/crediting sources. Reacquisition keeps
the original report and bibliography readable. Other targets, BindingDB, BTS
indications and clinical studies are explicitly unqueried; benznidazole's missing
UniChem fixture is observed as unavailable. Linked resource ids do not imply access.

The full explanation report is about 30 MB per fixture acquisition, with thousands
of repeated contextual links. Reading each pinned card once avoids repeated
deserialization but establishes no broader performance/export guarantee (#98/#88).
Published `knowledge_state@4` aggregate source-record rows incorrectly count
successful CCD/UniChem molecule enrichment as zero/not-stated. The local #122
correction uses `knowledge_state@5` and `knowledge_state_explanation@2`: native
record/compound counts, explicit unknown counts, missing/partial scopes and
separate indication/study areas. Card payloads and original assertions/acquisition
records stay unchanged; old reports/packets retain their original rules. Published
delivery of the correction remains pending.

Validation: all eight molecule/target regressions pass on primary editable
Python 3.14.7 (55.07 seconds) and unchanged outside the checkout with installed
public Sabueso 0.13.0, Ackredit 0.9.0, PyUnitWizard 0.27.0 and pytest-receptor
1.2.0 (56.27 seconds). Installed imports resolve to site-packages. The full primary
offline checkpoint passes 1941 cases in 342.97 seconds, with 26 online cases
deselected and five expected fixture-failure/truncation warnings. All 14 workspace
packages remain editable from outside the checkout; pip check passes. Ruff checks
690 Python files; warning-failing Sphinx, local links, source registry and dependency
preflight pass. Both journeys are copied unchanged into the public-provider and
staged installed-package workflows; their future remote OS/minor gates remain pending.
The size observation is recorded in
[#98](https://github.com/uibcdf/sabueso/issues/98#issuecomment-6001590290), and runtime
coverage/clinical limits in
[#108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6001590665).

## Source-state correction checkpoint (#122, 2026-10-05)

The corrected classification/explanation passes 131 affected regressions and the
full primary offline checkpoint (1965 passed, 26 online cases deselected, 338.84
seconds; five expected fixture warnings). The unchanged card shape remains schema
0.3.12; no fixture, card payload or frozen packet is rewritten.

A separately installed scratch wheel (`0.13.0+1.gc1bab2d.dirty`, SHA-256
`963d214ffdc46ee0dafba619dc268955cf1e29003668288991829529199e9fb1`)
passes all 73 unchanged molecule-state, knowledge-state explanation and both
independent journey cases outside the checkout. The closure uses public Ackredit
0.9.0, PyUnitWizard 0.27.0 and pytest-receptor 1.2.0 on Linux/Python 3.14.7;
imports resolve to the scratch environment's site-packages and pip check passes.
The installed reader also validates the original pre-correction molecule bundle,
keeping its `knowledge_state@4` report and original attribution rather than deriving
the report again. The frozen previous packet keeps its original rule/hash/support.
Ruff, warning-failing Sphinx, card shape, workflow YAML/bindings, dependency preflight
and 69 route/dependency regressions pass. This is local correction/installed-wheel
acceptance; published replacement and remote OS/minor artifact gates remain pending.

## Initial disease/related-entity scope (`@1`, 2026-10-05)

This section records the initial metadata-only slice. The later `@2` implementation
below closes its native membership/input support gap; the original reports stay readable.

The example asks separate public questions: targets of triosephosphate isomerase
deficiency through Orphanet 868, and drugs whose ChEMBL indications name Chagas
disease through MeSH D014355. Both disease cards retain MONDO's stated equivalence
and release; related EFO:0001360 remains unresolved. Target candidates retain Open
Targets ranks/scores and Orphanet association types/status; the drug retains two
matching indication rows and their native trial/label pointers, without fetching
those resources or assessing efficacy/approval.

An enriched HsTIM card separately preserves original disease groups and the named
`disease_group_explanation@2`/`disease_grouping@2` output, exact pinned native support,
identity/hierarchy paths and ungrouped reasons. Target/drug decks retain original
membership metadata, exclusions and source outcomes. Source rows (20 of 252),
attempted candidates (3) and built cards (1) are distinct fixture scopes. Failed
fixture card builds do not imply absent UniProt entries. The producer report is
about 1.5 MB per acquisition, not a general scale qualification.

Scientific membership support remains incomplete: the disease builders do not
record exact membership SourceAssertions or a pinned disease input. `Deck.explain`
therefore returns original metadata rather than assertion-backed membership. The
example reports that gap instead of manufacturing support from nearby statements.
Next #91 acceptance should bind each retained/excluded membership to its actual
source statement, stated gene/product or disease identity basis and original disease
input, retain all sources/versioned derivation/limits, and preserve support after
heads advance. Schema/card compatibility and old decks must stay readable.

Runtime credit is also partial: UniProt, ChEMBL indication/identity and UniChem
operations are observed; MONDO, Open Targets, Orphanet, DISEASES, ClinVar and MedGen
are not. Original observations include unavailable fixture accesses and operations
for candidates that never yielded a card. Preserve them in the workflow sidecar;
per-card trace subsets alone are not the complete workflow. No bibliography is
generated for unobserved access. Disease/deck observation, empty/failure/reuse scopes
and missing indication-reference metadata remain #108. Non-protein packets remain
#71; the example introduces no new public query or shared recording format.

Independent readers validate exact card items, original membership bases and
original available attribution without source calls, current-rule explanations or
new credit. They reject missing/misbound sidecars, altered statements/membership,
wrong member states and overstated coverage. Reacquisition keeps original card/deck
refs and reports readable. Complete disease journey acceptance remains open until
the support/observation guarantees above are delivered.

The concrete membership/input acceptance is recorded in
[#91](https://github.com/uibcdf/sabueso/issues/91#issuecomment-6002479814), and
source/deck observation scope in
[#108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6002480177).

Local validation: the final nine journey cases pass in the primary editable
Python 3.14.7 environment (44.78 seconds), alongside 63 existing disease identity/
group-explanation cases and 69 release-route/staging/dependency cases. Reusing
each verified loaded card's item store avoids hundreds of repeated card decodes;
native item pins are also checked per role. The final reader also validates the
original bundle made before this example-local performance change. No scientific
SDK/card/schema/fixture change was made in this slice. All 14 installed workspace
packages remain editable with checkout import origins, Sabueso source/distribution
versions agree and pip check passes. Ruff checks/formats all 693 Python files;
workflow YAML/copy/execution bindings and dependency preflight pass.

All nine final cases also pass unchanged outside the checkout (43.40 seconds) with
installed public Sabueso 0.13.0, Ackredit 0.9.0, PyUnitWizard 0.27.0 and pytest-receptor
1.2.0 on Linux/Python 3.14.7; imports resolve to site-packages and pip check passes.
Warning-failing Sphinx and `git diff --check` pass. Remote CI and
the full OS/minor matrix remain pending; prior full offline/code-change receipts
above are separate from this example/workflow slice's selected gates.

## Exact disease membership support (`@2`, 2026-10-05)

The next bounded #91 slice is implemented locally: `disease_targets@2` and
`disease_drugs@2` import native association/indication statements and derive
membership separately. Open Targets' full returned record preserves disease scope,
row order and returned/total counts alongside individual rows. Orphanet rows and
ChEMBL indications keep every native field/reference, original source version and
retrieval time; no new source call or bibliography is inferred from stored science.

The input MONDO card stays unchanged. A separate assertion-bearing revision holds
the new raw statements as scoped context. Deck `meta.support` embeds both card
snapshots/pins (`sabueso.disease_deck_support@1`); kept/unbuilt/capped/unsupported
candidates bind native statement pins and original MONDO identity. Kept members
also pin their actual card state and identity assertions. Membership/ranking remains
a named derivation, never a SourceAssertion. No selected disease field, card key,
predicate, schema version or SQL table is added.

`disease_deck_explanation@1` reports missing or misbound statements/identity,
metadata versus native score/order disagreement and wrong member states. Saving
the deck alone atomically persists support and members; malformed or rewritten
embedded input stores nothing. A disease head may advance to the support revision;
the original input/items remain readable. JSONL/SQLite export/reimport into an empty
store retains exact support. Ordinary filtering retains embedded statements;
subsequent operations that do not record candidate bases report support gaps.

`disease_deck_terms@1` reports members and all embedded native-source content,
including unbuilt candidate statements. Member-only admission cannot safely claim
to filter that support, so `Deck.admissible` refuses the format pending #29.
The example is versioned as `@2`; its reader still accepts original `@1` bundles
and preserves their original reports/gaps without rerunning rules or generating
credit. Required disease source/deck-operation observation is next (#108), with
non-protein packets still #71. Complete disease acceptance/public delivery remain open.

Final local checkpoint: all 2000 offline cases pass in the primary editable
Python 3.14.7 environment (443.12 seconds, 26 online cases deselected; six expected
fixture warnings). The final 46 support/terms cases and 69 release-route/staging/
dependency cases also pass independently. All 14 installed workspace packages are
editable and import from their local checkouts outside this repository; Sabueso
runtime/distribution versions agree and pip check passes.

The final diagnostic wheel (`0.13.0+1.gc1bab2d.dirty`, SHA-256
`5f8f9fda2ce9a306d3408b22171d83baf42de6f3a8df7a21fa46510649b8ba65`)
contains 384 Python/JSON files identical to the checkout, excluding generated
`_version.py`. Its unchanged support/journey/disease/deck/store/terms tests pass
133 cases outside the checkout (89.38 seconds, one expected fixture failure
warning), with public Ackredit 0.9.0, PyUnitWizard 0.27.0 and pytest-receptor 1.2.0
on Linux/Python 3.14.7. Imports resolve to the scratch environment's site-packages
and pip check passes. Its reader also accepts the real original metadata-only
`@1` bundle, preserving original gaps without acquisition or new credit.

Ruff check/format (696 Python files), schema/card shape 0.3.12, source registry,
governance, dependency preflight, workflow YAML/copy/execution bindings,
warning-failing Sphinx and `git diff --check` pass. Installed-provider and future
staged workflows include the unchanged new support file alongside all three
journeys. These are local development/installed-wheel receipts; remote CI, the
OS/minor installed-artifact matrix and public delivery remain pending. The former
Codecov incident (#119) is closed and is not a blocker for this slice.

Completion and remaining scope are cross-linked in
[#91](https://github.com/uibcdf/sabueso/issues/91#issuecomment-6003164939),
[#112](https://github.com/uibcdf/sabueso/issues/112#issuecomment-6003174931),
[#108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6003175535) and
[#29](https://github.com/uibcdf/sabueso/issues/29#issuecomment-6003107144).

## MONDO identity observation (`@3`, 2026-10-05)

The next bounded #108 slice observes built-in MONDO term/equivalence queries,
including normal disease resolution and protein enrichment. Native stated
equivalence/definition references, raw/normalized query, OBO version, file/lookup
identities, release asset/checksum and original index/download receipt are retained.
Current requests remain distinct from reused index origin; memory and archive reuse
preserve the original response time, source version and wire/archive identities.
Fixture subset/no-equivalence/missing-term scopes remain explicit, as do
unavailable/unqueried/failed/unobserved outcomes and incomplete term bibliography.

The same work corrects the existing #123 client defects: original scientific times
survive memory/archive reuse, non-OBO/invalid UTF-8 documents are connector failures,
and missing fixture files become unavailable connector failures. Native partial
term-stanza fixtures and the public parser utility remain supported; no complete
OBO-validation claim is made. A pre-existing index without a receipt cannot recover
its original time and retains an explicitly identified legacy fallback. Stored
cards, schema 0.3.12, identity/mappings and default persistence remain unchanged.

The example now uses `@3` with MONDO removed from its current observation gaps.
Original `@1`/`@2` reports remain readable with their original gaps; readers acquire
and credit nothing. Complete MONDO resource-description metadata is compiled from
the official resource/primary public publication metadata, separately from missing
definition/imported-terminology citations and without runtime article lookup.
Direct disease resolution retains exact card/resolution pins and trace copies.

At that checkpoint, Open Targets/Orphanet and disease-deck observation were next. Other disease
sources, indication-reference bibliography, support-aware admission (#29), non-protein
packets (#71) and shared recording/consumer contracts remain pending. The implementation
and #123 correction are local and unpublished; complete journey acceptance stays open.

Final local checkpoint: all 2031 offline cases pass in the primary editable
Python 3.14.7 environment (492.30 seconds, 26 online cases deselected; six expected
fixture warnings). The 84 MONDO/public-source-envelope cases, 66 MONDO/disease
regressions and 69 release-route/staging/dependency cases also pass independently.
All 14 installed workspace packages remain editable and import from their local
checkouts outside this repository; Sabueso runtime/distribution versions agree
and pip check passes.

The final diagnostic wheel (`0.13.0+1.gc1bab2d.dirty`, SHA-256
`35b52408faba5d4c55416bc90a34b231e0cc7b39ca30888f9f01d0706d41a926`)
contains 385 Python/JSON files identical to the checkout, excluding generated
`_version.py`. Its unchanged MONDO/source-envelope/support/journey/disease/deck/
store/terms cases pass 217 tests outside the checkout (84.98 seconds, one expected
fixture failure warning), with public Ackredit 0.9.0, PyUnitWizard 0.27.0 and
pytest-receptor 1.2.0 on Linux/Python 3.14.7. Imports resolve to the scratch
environment's site-packages and pip check passes. The final installed `@3` reader
also accepts genuine original `@1` and `@2` bundles, preserving their original
reports/gaps without acquisition or new credit.

Ruff check/format (698 Python files), schema/card shape 0.3.12, source registry,
governance, dependency preflight, workflow YAML/copy/execution bindings,
warning-failing Sphinx and `git diff --check` pass. Installed-provider and future
staged workflows include the unchanged MONDO test file. These are local
development/installed-wheel receipts; remote CI, the OS/minor installed-artifact
matrix and public delivery remain pending. The closed Codecov incident (#119)
does not block this slice. #123 remains open for delivery of the integrity fixes.

Final scope and qualification are cross-linked in
[#108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6003825596),
[#123](https://github.com/uibcdf/sabueso/issues/123#issuecomment-6003827645) and
[#112](https://github.com/uibcdf/sabueso/issues/112#issuecomment-6003828250).

## Association sources and disease-build observation (`@4`, 2026-10-05)

The next #108 slice observes native Open Targets association pages in both
directions and Orphadata's indexed SwissProt associations/genes. Raw/normalized
queries, source versions/order/counts, file/page/lookup identities, original time
and actual attempts survive memory/archive reuse. Explicit null/empty answers,
fixture subsets, unavailable/unqueried access and malformed/failed responses have
separate scopes. Open Targets page failures retain completed intake; changing
count/version or disappearing entities abort scientific merges with partial traces.
Resource descriptions contribute to host Ackredit capture; underlying studies stay
unfetched and incompletely described.

Existing Orphadata timestamp/document and Open Targets answer/fixture integrity
defects are corrected locally under #124. Original Orphadata XML receipts travel
with the exact existing cache tuple; old bare indexes keep unknown origins/time and
an explicitly scoped legacy fallback. No new persistence/cache is added. Public
parser utilities, valid mappings/identity/membership rules, stored cards and schema
0.3.12 remain fixed.

Disease-build traces preserve original input/support pins, final deck/member pins,
executing version/times, rule/limit, source statuses and exclusions. Stored disease
input creates no fresh MONDO access, and custom clients remain unobserved. Saved
readers add no trace, acquisition or credit. Example `@4` binds these sidecars;
genuine `@1`/`@2`/`@3` bundles retain their original reports/gaps. This is local
application bookkeeping, not a shared MOLI recording format.

At that checkpoint, DISEASES/ClinVar/MedGen observation, full study bibliography, support-aware admission
(#29), non-protein packets (#71), shared consumer contracts and public/remote
qualification remain pending. Complete disease journey acceptance stays open.

The final 47 acquisition/build regressions and 53 public-source-envelope cases
pass together (100 tests, 4.88 seconds). The 69 release-route/staging/dependency
cases pass independently. All 14 workspace distributions remain editable and
import from local checkouts outside this repository in Python 3.14.7;
Sabueso runtime/distribution versions agree and pip check passes.

Final diagnostic wheel `0.13.0+1.gc1bab2d.dirty`, SHA-256
`83eb742a92eb9bfdd5655e7d167985dd721aea38769e240f1a5c941a2ae54ac8`,
contains 387 checkout-identical non-version Python/JSON files. Its unchanged
disease-source/MONDO/source-envelope/support/journey/disease/deck/store/terms tests
pass 265 cases outside the checkout (95.52 seconds, one expected fixture failure
warning), with public Ackredit 0.9.0, PyUnitWizard 0.27.0 and pytest-receptor 1.2.0
on Linux/Python 3.14.7. Site-packages imports and pip check pass. The installed `@4`
reader also accepts genuine original `@1`, `@2` and `@3` bundles, preserving original
reports/gaps without acquisition or new credit.

Ruff check/format (701 Python files), schema/card shape 0.3.12, source registry,
governance, dependency preflight, workflow YAML/copy/execution bindings and
warning-failing Sphinx pass. These are local/installed diagnostic receipts; remote
CI, the OS/minor installed-artifact matrix and public delivery remain pending.
#124 remains open for delivery of the integrity fixes.

Final full offline checkpoint: 2079 tests pass in the primary editable Python 3.14.7
environment (420.50 seconds, 26 online deselected; eight expected fixture warnings).
The source/build changes and diagnostic wheel above were frozen before that run.
`git diff --check` also passes. No remote CI, release or OS/minor qualification
is inferred from this local checkpoint; Codecov #119 remains resolved.

Scope, integrity fixes and final qualification are cross-linked in
[#108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6010225480),
[#124](https://github.com/uibcdf/sabueso/issues/124#issuecomment-6010226640) and
[#112](https://github.com/uibcdf/sabueso/issues/112#issuecomment-6010226869).


## Disease channel/variant/identity observation (`@5`, 2026-10-06)

The built-in DISEASES, ClinVar and MedGen clients now observe their own acquisition
instead of borrowing access history from nearby card statements (#108/#125).
DISEASES retains each filtered channel's publication date, original TSV identity,
selected native row order and memory-index receipt. Current header checks are
separate accesses, not new scientific retrieval dates. Older disk/bare caches have
unknown origins/times and a declared legacy client-clock fallback. Knowledge,
experiments and text-mining scores/pointers remain separate.

NCBI lookups retain EInfo/ESearch/ESummary queries, decoded/wire/archive identities,
native row/UID order, per-gene or batch counts/caps, completed subsets and terminal
failures. ClinVar database builds and variant accession versions differ from MedGen
database `lastupdate`; no global release or record revision is invented. Overlapping
ClinVar genes keep native repeated UIDs. Missing result fields, incomplete/malformed
summaries and missing/mixed fixtures cannot turn into evaluated absence. MedGen
refuses capped or ambiguous concept-to-UID identity, preserving original pairs in
the failed trace rather than selecting by response order. Credentials are excluded
from recorded transport request identities; native response bytes remain unchanged.

Resource descriptions use primary verified DISEASES/ClinVar metadata and MedGen's
recommended website citation. They contribute to host captures; underlying channel
studies, ClinVar submissions and terminology publications remain unfetched bibliography
gaps. No Ackredit provider workaround or new cross-component contract is introduced.
Example `@5` exposes the exercised disease-source observation closure and retains
original `@1`–`@4` reports/gaps. Existing support/deck traces stay independently pinned;
readers acquire, derive and credit nothing. Schema 0.3.12 remains frozen.

Local gates: 64 new lookup regressions; 74 acquisition/journey cases; 109 common
transport/archive/installed-release/dependency cases. The exact diagnostic wheel is
`/tmp/sabueso-disease-lookups-wheel/sabueso-0.13.0+1.gc1bab2d.dirty-py3-none-any.whl`,
SHA-256 `005315ab0fb2be630475808bd73aebbb87fa6b6ddd7008e5d928718ba5d7a859`.
All 389 non-version Python/JSON files equal the checkout. Its unchanged lookup,
association, MONDO, support, source-access, storage, terms and all three journey
tests pass 344 cases outside both repositories (178.96 seconds; one expected fixture
failure warning) with public Ackredit 0.9.0, PyUnitWizard 0.27.0 and pytest-receptor
1.2.0 on Linux/Python 3.14.7. Site-packages origins and pip check pass.

Genuine original `@1`, `@2`, `@3` and `@4` bundles, produced with their earlier
implementations, pass the installed `@5` reader with acquisition, derivation and
new-credit entry points forbidden; original receipt files stay byte-identical.
The `@4` bundle was produced before upgrading the installed qualification package.
All 14 primary workspace packages retain editable metadata and checkout imports;
runtime/distribution versions and pip check agree. Ruff, schema/card shape, source
registry, governance/preflight, installed-workflow YAML bindings and warning-failing
Sphinx pass. Full offline checkpoint: 2143 cases pass in 399.12 seconds, with 26 online cases deselected and six expected fixture warnings.

Code and artifact qualification are local, with no push/remote matrix or public
replacement claim. #125 remains open for delivery. Complete study bibliography,
support-aware admission (#29), non-protein packets (#71) and shared consumer/record
acceptance remain pending. Owning issue receipts:
[traceability #108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6010597169),
[integrity #125](https://github.com/uibcdf/sabueso/issues/125#issuecomment-6010597485),
[roadmap #112](https://github.com/uibcdf/sabueso/issues/112#issuecomment-6010597748).

## Conservative disease-deck admission checkpoint (2026-10-06, #29)

Development `disease_deck_admission@1` validates exact input/member/native support,
then requires all shared embedded context to allow the requested use. Unknown or
restricted shared terms refuse with a detached item-level `admission_report` on
`ArgumentError`; broken support refuses with `StorageError`. Whole source pruning
is deliberately pending rather than inferred from surviving cards.

All raw member SourceAssertions are checked independently, including unused and
alternative statements. An allowed resolved alternative does not license another
raw copy. Raw per-record rights remain unknown when undeclared, even if a projected
relationship has known depositor terms. Whole non-admissible members are excluded
with exact reasons and historical identity references; the retained native/input
candidate basis stays self-contained. Original deck/member/support pins, obligations
and current registry declarations remain in the separate derived deck. Existing
ordinary and legacy admission semantics are unchanged.

JSONL/SQLite exports, empty-store reimports and reads through advanced heads retain
those decisions without acquiring or adding credit. Original acquisition/attribution
sidecars remain original; admission creates no fake runtime receipt. The example
keeps its `@5` format; separate SDK cases exercise admission. Genuine original
`@1`–`@5` bundles read with acquisition, derivation, admission and new credit forbidden;
their original receipt files remain byte-identical.

Diagnostic wheel:
the initial `/tmp/sabueso-disease-admission-wheel/` wheel (SHA-256
`6897e4142b96ca36544a3ab5c2b4d4dac75400bae23564f3d3241a7974133119`) passes
381 installed cases and 2180 full offline cases, but is superseded by the #126
identity integrity fix. Those initial receipts do not qualify the final code.

The review reproduced a different candidate's valid native basis attached to HsTIM
(`uniprot:P60174` versus `uniprot:Q9UQD0`). Existing pin checks accepted it despite
missing source-stated equivalence. The unpublished explanation now verifies that
native candidate identifiers are stated by the actual member's bound identity
assertions and agree with the resolved fields. Both substituted native bases and
changed resolved identifiers with unrelated original statements become partial;
admission refuses. Sixty-five admission/support cases pass after the correction.
The fix adds no identity inference or stored field and leaves original saved reports
unchanged. [#126](https://github.com/uibcdf/sabueso/issues/126) owns the correction.

Final diagnostic wheel:
`/tmp/sabueso-disease-admission-fixed-wheel/sabueso-0.13.0+1.gc1bab2d.dirty-py3-none-any.whl`,
SHA-256 `a852a09d0333914f5d938d59fba66bde5fe61b0346275fb5f0897195430690a0`.
All 390 non-version Python/JSON files match both the checkout and exact installed
bytes. With public Ackredit 0.9.0, PyUnitWizard 0.27.0 and pytest-receptor 1.2.0,
383 unchanged admission/support/source/journey/storage/terms cases pass in
371.81 seconds outside the checkout (one expected unavailable-fixture warning).
All 14 primary workspace packages remain editable with verified outside-checkout
origins in `molsyssuite@uibcdf_3.14`; primary/installed pip check passes.

Final full offline checkpoint: 2182 cases pass in 706.53 seconds, with 26 online
cases deselected and eight expected fixture warnings. Ruff check/format, card shape
and schema 0.3.12, registry, governance/dependency preflight, installed-workflow
bindings, import origins/pip check and warning-failing Sphinx pass. The final code
and original `@1`–`@5` readers are qualified separately from the superseded wheel.
Delivery is local, uncommitted/unpushed; no remote matrix or public replacement is
claimed. #29 remains open for finer source pruning, raw per-record rights, historical
registry semantics and wider packet scopes. Complete underlying study bibliography
remains #108; non-protein packets remain #71. No Ackredit contract/workaround is added.

Owning implementation receipts:
[admission #29](https://github.com/uibcdf/sabueso/issues/29#issuecomment-6011111335),
[identity integrity #126](https://github.com/uibcdf/sabueso/issues/126#issuecomment-6011118841).

## Native ChEMBL indication-reference checkpoint (2026-10-06, #108)

`chembl_indication_references@1` projects the source's native reference pointers
into portable attribution, with exact indication/molecule/disease row identity,
received page/query/hash or original decoded fixture-result basis. Every occurrence
is retained, including overlapping EFO/MeSH queries whose scientific return contains
one deduplicated row. Bibliography deduplicates equal native forms, while preserving
alternative forms and grouped identifiers.

The distinct role `source_cited_reference` credits a reference declared by ChEMBL,
without claiming direct access to its trial registry, regulatory label or
classification. HTTP(S) pointers are incomplete web citations; identifier-only
forms retain their native form as `other`. Missing title/authors/year, malformed or
absent reference forms and unfetched targets remain explicit gaps. Received pages
remain creditable before later failures. Original retrieval/release bases and
references survive archive reuse/replay and saved exports without requests or
new credit. SourceAssertions, scientific returns and frozen schema 0.3.12 are fixed.

The example keeps `@5`: native pointers do not fill its missing study metadata or
fetch cited studies. Genuine original `@1`–`@5` bundles remain readable with
source/derivation/admission/credit functions forbidden and original receipt bytes
unchanged. This slice introduces no new Ackredit contract or provider workaround.
ClinicalTrials.gov observation and linked study/publication metadata remain #108.
Finer #29 **filtering by terms of use** remains separate work; it must preserve the
original deck and provenance while stating support changes in a derived result.

Diagnostic wheel:
`/tmp/sabueso-indication-bibliography-wheel/sabueso-0.13.0+1.gc1bab2d.dirty-py3-none-any.whl`,
SHA-256 `de9559d1c24dbda66670b9ae8f857067ee480efb66b35ea4a7755b7f4fcab956`.
All 391 non-version Python/JSON package files equal checkout and installed bytes.
The installed environment uses public Ackredit 0.9.0, PyUnitWizard 0.27.0 and
pytest-receptor 1.2.0, with imports outside the checkout and pip check passing.
All 14 development distributions remain editable in `molsyssuite@uibcdf_3.14`.

The first targeted gate passed 60 reference/ChEMBL/molecule/disease journey cases
(161.07 seconds). An installed export test initially required development-only
BibTeX citation-key spelling; the test now checks native reference/link retention
and portable citation identity independently of renderer-specific keys. The final
29 new reference cases pass in both development (23.97 seconds) and the unchanged
installed lane with public Ackredit (24.29 seconds). No package implementation was
changed by that test correction. Full offline/installed checkpoints are recorded
after their final gates below. Delivery remains local, uncommitted/unpushed;
there is no new public release or remote-matrix claim.

Final offline code checkpoint: 2211 cases pass in 593.50 seconds, with 26 online
cases deselected and eight expected fixture warnings. The independently corrected
export-test predicate also passes in both final 29-case reference gates above.
Ruff check/format, frozen card shape/schema, source registry, governance/dependency
preflight, YAML copy/execution bindings, import origins, both pip checks and
warning-failing Sphinx pass. The final unchanged installed gate passes all 425 cases
in 267.37 seconds, with two expected fixture warnings, using the exact diagnostic
wheel and public Ackredit 0.9.0 outside the checkout. Original `@1`–`@5` bundle
readers preserve receipt bytes without acquiring, deriving, admitting or adding credit.

Owning implementation receipt:
[traceability #108](https://github.com/uibcdf/sabueso/issues/108#issuecomment-6011536313).

## Clinical registry/reference checkpoint (2026-10-06, #108/#127/#128)

Built-in study and explicit reference queries now retain native page/entry/version,
reuse, evaluated-empty, unavailable and partial/failure scope. Native NCT identity
is never inferred from intervention names. Pagination, contradictory duplicates and
false absence are fixed locally (#127). The separate reference endpoint preserves
PMID/type/free citation, see-also/IPD and retraction declarations without following
targets. The public NCT00123916 fixture and three separately frozen Europe PMC
articles exercise original registry citations plus explicit metadata acquisition.
The BENEFIT article retains all 22 returned authors, including the collective
author as a literal name (#128). No article terms, efficacy or project Evidence is
inferred. Frozen schema 0.3.12 and clinical SourceAssertions stay unchanged.

This bounded source-layer exercise does not revise the genuine disease `@1`–`@5`
reports or automatically augment the disease example's bibliography. It establishes
explicit source access and original workflow credit. Historical saved readers remain
inert. Full bibliography across other providers, precise query/result scopes,
finer terms filtering (#29), non-protein packets (#71) and consumer-owned MOLI
recording remain pending. That qualification preceded commit/push; current delivery is in `CHECKPOINT.md`.

Final qualification for this slice is recorded in
[the clinical checkpoint](clinical_registry_checkpoint.md): 2272 offline cases
pass (693.93 seconds), and the corrected 178-case installed clinical/reference/
article gate passes with public Ackredit 0.9.0 (19.50 seconds). The initial broader
installed-client run passed 546 cases and failed four because its fixture/document
copy was incomplete; all four pass in the corrected affected gate. All 393
non-version package files match checkout, exact wheel and installed bytes.
Original disease `@1`–`@5` readers remain inert, docs/format/schema/registry gates
pass, and no remote/public delivery is claimed. The checkpoint also records current
shared-environment dependency conflicts and the ordered resumption route.

## Upstream code checkpoint completed (2026-10-06)

The accumulated development and corrected UTF-8 regression are committed and
pushed in `413cdf6` and `74c8c3d`. [Exact-head CI](https://github.com/uibcdf/sabueso/actions/runs/37438528677) passes 15/15
jobs and [MOLI governance](https://github.com/uibcdf/sabueso/actions/runs/37438528644) passes. Current resumption no longer
needs committing the accumulated changes: start at immediate roadmap step 2.
The following documentation-only receipt is locally checked and has no executable
effect. Public 0.13.0 is unchanged; release/staged qualification remains separate.
Original dated local receipts, wheel hashes and genuine historical reports stay
unchanged. The clinical checkpoint holds complete delivery and environment details.
