---
summary: Required automatic result and workflow attribution for knowledge pipelines.
issue: uibcdf/sabueso#108
status: open
opened: 2026-10-02
closed:
verification: local_runtime_tested
area: [attribution, knowledge_packets, source_access]
blocked_by: [uibcdf/moli#36]
supersedes: []
---

# Required attribution for knowledge pipelines

Status: required automatic packet-composition and bounded source-acquisition adapters
implemented; broader pipeline
coverage remains open with explicit gaps in the published 0.13.0 scope (#108).
Public Ackredit 0.9.0 delivery is adopted and Sabueso 0.13.0 is published/qualified.
Unreleased changes require their own validation; the public application exercise
does not replace future exact-artifact release gates.
Owner: [uibcdf/sabueso#108](https://github.com/uibcdf/sabueso/issues/108).
Shared boundary: [uibcdf/moli#36](https://github.com/uibcdf/moli/issues/36).
Provider: [uibcdf/ackredit#75](https://github.com/uibcdf/ackredit/issues/75).
Reviewed: 2026-10-03, published Ackredit 0.9.0/py_0 from source
`598abf993a2409c025de5e912acd7eb45a257ebd`.

## What the consumer needs

A pipeline should retain which sources, datasets and executed software it used,
with citation records for each result and the enclosing application workflow.
Ackredit's accepted `capture`, contextual `track_item`, detached `Attribution`
and `get_attribution` fit this need. Its canonical
[integration guide](https://github.com/uibcdf/ackredit/blob/main/standards/ACKREDIT_GUIDE.md)
owns the provider API; this report records Sabueso's initial use and remaining needs.

Four records have different responsibilities:

| Record | Responsibility |
| --- | --- |
| SourceAssertions and pinned relationships | What sources state and what supports returned knowledge |
| Acquisition trace | Observed source operation, route, response identity and outcome, including failures |
| Runtime attribution | Resources and software actually reached, with bibliography and contextual uses |
| Terms report | Source-stated obligations, restrictions and unknowns for an intended use |

Neither a citation nor an acknowledgement supplies permission to redistribute
article text. A publication mentioned by a database is not automatically that
database's description citation. Nextia Evidence remains separate from all three.

## Proposed integration boundaries

1. **Acquisition:** distinguish attempted requests from successful acquisitions,
   including evaluated-empty responses and local replay. Record the actual route,
   release (unknown when unstated) and outcome. A failed request does not claim a
   completed scientific acquisition; an unqueried source receives no usage credit.
2. **Composition and views:** retain the pinned statements and rules actually used.
   Whole-card source summaries include unrelated knowledge and cannot define a
   result's citation scope. Reading stored knowledge differs from downloading it.
3. **Result and workflow:** each result owns detached original records and versions,
   including resources reused by earlier results. Contribute to the current
   application session; do not create isolated component sessions or infer a
   result's bibliography by subtracting deduplicated session IDs.
4. **Saved readers:** preserve original attribution and render it without new credit,
   backend loading or DOI enrichment. The initial local record is stored beside
   scientific data, with no change to shared knowledge payloads. Shared record
   coordination remains MOLI #36.

Bibliographic declarations must be complete, verified offline against original
works, and versioned where appropriate. Sabueso's registry currently supplies
terms/attribution text, not a complete resource bibliography. Literature records
may supply identifiers and partial metadata; missing authors, dates and releases
must not be invented. The provider owns rendering; Sabueso must not copy its
renderers or inspect its private registry.

## Current pre-release work

`Card.explain_literature(publication_ref)` provides pinned links, both legs of
structure mention context, preserved alternatives and recorded unlinked requests.
`KnowledgePacket.terms(use, store)` provides a detached support manifest and a
terms report for `packet_aspects@6/@7` in development, independently of full/index detail. It reads
exact saved cards and follows represented statements, conflicts and stored
relationship dependencies. Disease identity context is explicitly broader than
exact grouping lineage, which was not recorded.

These read-time operations keep their support/terms meaning. The initial runtime
adapter now follows the same stored-statement closure independently of licence
verdicts, automatically after every completed composition. `packet.attribution` owns
the detached record; `sabueso.attribution()` optionally collects several results.
It records `sabueso.packet_attribution@1` locally, credits selected stored knowledge
and executed software, and contributes per-result references to the application's
Ackredit session/captures. Composition itself observes no source requests or arbitrary card views.
Query, packet, card and store payloads remain unchanged.

Development [comparative operation observation](comparative_operations.md)
records three ordinary Card views inside an explicit attribution context, in a
separate `operations` collection. Original rules, parameters and exact pins bind
the unchanged return to its execution; selected input support and bibliographic
gaps retain separate scopes. Plain calls, explanations and saved readers remain
inert. Qualification is in progress; full bibliography and other result types
remain open under #108.

The [persisted comparative journey](comparative_journey_attribution.md) now connects
those records to example `@3`: ordinary results/explanations, original source/
comparative/workflow credit and independent inert export survive reacquisition.
Older formats retain their execution gaps. Publication/remote qualification for
this slice remain pending under the deferred development block.

Traceability is required by the maintainer and MOLI. The first acquisition slice
automatically observes built-in UniProt entry/search, Europe PMC
mentions/annotations and RCSB single/batch structure lookup. Provisional host records
`sabueso.source_acquisition@1` in a
`sabueso.acquisition_trace@1` retain independent operation identities, actual routes,
original producer/source versions with explicit bases, retrieval times, decoded/raw
response identities and archive references. Empty/not-found, unavailable fixtures,
unqueried offline access, failure and partial transport remain distinguishable.
Supported public envelopes retain the trace separately from raw records. Cards,
resolutions (including no-card failures), refreshed final states and one-call
packets retain independent copies. Exceptions retain their failed trace.

Completed access contributes contextual resource use and bibliography through the
accepted Ackredit API, including empty/local replay access. Failed/unqueried access
remains a host record without completed-access credit. `AttributionRun.acquisitions`
collects these source events separately from packet composition `records`.
Other sources/custom clients are explicitly unobserved. Original JSON sidecars are
saved by the application; payload-only readers have no trace and add no execution
credit. MOLI owns ProjectRecord composition and future Recorda routing/correlation/
reliability policy; the local experiment does not implement that platform boundary.

The public offline pilot in `examples/ackredit_pilot/` composes identity and
literature packets for HsTIM from frozen public responses. Both retain reused UniProt
references; only literature credits Europe PMC. Their enclosing workflow holds the
union of intake and composition references. The pilot saves the original acquisition
trace beside the knowledge store. Saved JSON readers preserve versions and add no credits. Real-provider tests
exercise reused resources, nested scopes, detached ownership, installed failure,
fresh-process missing required provider diagnostics, lazy import and scientific result parity. Recorded
empty source outcomes do not imply a new download. Source regression tests verify
replay/reuse, empty answers, absence/failure, partial batches, retry facts, custom-client
coverage, refresh pins and one-call packet intake independently of composition.

Complete UniProt/Europe PMC/RCSB description citations were verified against primary
publication records; missing descriptions and target article/annotation-provider
bibliography remain gaps. The required candidate includes the correction reported
in [Ackredit #78](https://github.com/uibcdf/ackredit/issues/78): explicit CSL corporate
and personal author objects render correctly in BibTeX. Saved-reader consumer
regressions check original metadata in text, CSL-JSON and BibTeX without new credits.
No renderer is copied.

Consumer CI now obtains Ackredit from public Conda on every runtime lane;
dedicated receiving lanes pin 0.9.0/py_0 on Python 3.11–3.14. Metadata, recipe and
all runtime environments require `ackredit>=0.9.0`; the source overlay and blocker
are removed together. The installed Conda gate retains the delivered public SHA-256
and rejects a different hash, channel, imported version or portable API.

The earlier
[local diagnostic receipt](https://github.com/uibcdf/sabueso/issues/108#issuecomment-5968486124)
is superseded for receiving qualification by the actual staging/public file below.

## Independent exact-staging receiving qualification (2026-10-03)

The provider's [handoff](https://github.com/uibcdf/sabueso/issues/108#issuecomment-5971254953)
supplies `noarch/ackredit-0.9.0-py_0.tar.bz2`, built from
`598abf993a2409c025de5e912acd7eb45a257ebd` in successful producer
[37136075066](https://github.com/uibcdf/ackredit/actions/runs/37136075066).
Independent download SHA-256 is
`37661090f6ad19a74b8155d8a4d4b4a068c9099f4ceba0743b3abfe887e97fe1`.
It matches retained `noarch-artifact.json` and the verified `uibcdf.conda-upload@1`
staging receipt in artifact `noarch-publication-37136075066-1`, including producer
identity, source, label and coordinate. Archive metadata also matches 0.9.0/py_0/noarch.

Sabueso independently repeats the receiving tests with its prepared source
`7352cf4437dca6d0249c3af9777ad123926d2f31`. A disposable clone supplies a normal
local wheel, SHA-256
`2520fd3e07fa6db5c65f66f3087175c7657a3c7b519fbf9a1cf3c4d9ccf38f61`.
All 348 Python modules excluding generated `_version.py`, plus packaged
selection/profile/terms resources, match that source without extra modules.
Cleaning tracked generated build copies in the disposable clone explains its
development suffix; this wheel is compatibility input, not a published artifact.

Four fresh Linux environments use strict public channels and the exact core builds
planned for Sabueso's installed gate: SMonitor 0.17.0/py_0, ArgDigest 0.13.0/py_1,
DepDigest 0.11.0/py_2 and PyUnitWizard 0.27.0/py_0. Public Pytest/Receptor tooling
is installed with Conda. Only the verified Ackredit file comes from staging; the
consumer wheel is installed normally with `pip --no-deps`, not editable.

| Python | Unchanged acquisition/attribution cases | Public workflow | Pip check |
| --- | --- | --- | --- |
| 3.11.16 | 36 passed, no skips | passed | passed |
| 3.12.14 | 36 passed, no skips | passed | passed |
| 3.13.15 | 36 passed, no skips | passed | passed |
| 3.14.7 | 36 passed, no skips | passed | passed |

Tests execute outside both checkouts using only frozen public fixtures. Provider,
consumer and core dependencies import non-editable code from the isolated prefix's
site-packages; runtime and distribution versions agree. Installed package bytes
match their archive/wheel, and the installed Conda record keeps the exact staging
URL/version/build/SHA-256. The pilot verifies the original trace, two result
bibliographies, reused references, workflow union and saved readers without new credit.
The compact durable
[receiving receipt](../../devtools/conda-build/receipts/ackredit_0.9.0_staging_2026-10-03.json)
retains file/source identities, pins and each result. The primary workspace environment
retains editable packages.

This establishes Linux receiving compatibility with the actual staged provider,
including Sabueso's older public core pins. It does not replace Ackredit's hosted
Linux/macOS-arm64 installed matrix or Sabueso's eventual Conda installed matrix.
At that checkpoint, the hosted descriptor/caller needs were MolSysSuite #89/#88
work and public dependency closure remained blocked. Those delivery gates have now
closed through the public handoff below. Repeat qualification if the bytes change;
a version alone is no artifact identity.

## Public delivery adoption (2026-10-03)

The [published handoff](https://github.com/uibcdf/sabueso/issues/108#issuecomment-5973768120)
identifies the first released portable minimum, **Ackredit >=0.9.0**.
[Installed 37152044426](https://github.com/uibcdf/ackredit/actions/runs/37152044426)
passes all eight Linux/macOS-arm64 × Python 3.11–3.14 cells;
[promotion 37152421084](https://github.com/uibcdf/ackredit/actions/runs/37152421084)
preserves the same archive. Independent anonymous public download matches the
staging bytes and digest. Normal clean public-channel receiving installs on all
four Linux minors repeat the 36 tests, public workflow and pip check with the
planned exact public core builds. Ackredit #22/#75/#80 are closed.

Sabueso adopts the published floor in metadata, recipe and environments, pins
0.9.0/py_0 and the qualified digest in installed gates, and removes source overlays
and the public-dependency blocker together. Development and release preflight pass.
This delivery closes the provider dependency gate. Sabueso's preliminary local
Conda candidate now passes all four Linux minors and supplies the clean-installed
frozen 0.3.11 card; receipt:
`devtools/conda-build/receipts/sabueso_0.12.0_local_schema_freeze_2026-10-03.json`.
Its preliminary candidate `4ef9ddc` passed the actual staged archive and all 12
Linux/macOS-arm64/Windows × Python 3.11–3.14 installed lanes, with 36 integration
tests and the public workflow in each. Independent clean Linux 3.14 also verifies
installed bytes, the frozen card and pip check; receipt:
`devtools/conda-build/receipts/sabueso_0.12.0_staged_2026-10-03.json`.
The final RCSB extension is published from `7739317` as `py_1`, after fresh
CI/installed qualification, unchanged promotion, clean public installation and
identical-tag Zenodo archival. Its complete receipt is
`devtools/conda-build/receipts/sabueso_0.12.0_public_2026-10-04.json`.

The maintainer's editable workspace initially exposed a 0.8.0-based Git-version
mismatch, reported in [provider #81](https://github.com/uibcdf/ackredit/issues/81).
On 2026-10-04 the provider's 0.9.0 tag yields editable
`0.9.0+8.ga8219b8.dirty`; runtime/distribution versions agree, the floor is met
  and the primary environment's pip check passed at that checkpoint. All 14 workspace packages remain
editable. Receiving confirmation is reported upstream; #81 is closed through provider #82.
Clean public distributions satisfy the floor; broader trace/result/bibliography
and MOLI record work remain open in #108/#36.

## Adoption gates

The staged 0.12.0 preparation is tracked in #110. Its installed-file matrix now
requires provider import/metadata/API checks, the unchanged acquisition/attribution
regressions and the public workflow on every supported OS/minor, outside both
checkouts. Public delivery and the clean-installed frozen 0.3.11 card are verified. The
preliminary candidate `4ef9ddc` passed its actual staged artifact gates. On
2026-10-04 the maintainer requested RCSB before stable publication: native revisions,
per-entry batch outcomes, all fallback requests and original primary citations.
Final source `7739317` and build `py_1` repeat every gate: all 12 installed lanes
and independent clean public installation pass 56 integration cases and the public
three-packet workflow. Stable publication, unchanged promotion and identical-tag
Zenodo archival are complete under #110. The historical `py_0` receipt/archive stays
immutable. Native primary citations retain different stated metadata forms without
overwriting earlier references; missing fields remain explicit.

- Keep Ackredit required in metadata and the recipe. Lazy required import keeps
  saved readers free of backend loading. Missing/broken installations emit SMonitor
  diagnostics and retain failed attribution alongside completed scientific results.
- Results receive attribution automatically; applications own sessions. Libraries enable no import
  hooks, persistence journals, automatic enrichment or reminders.
- Exercise a real provider with three results reusing sources, an enclosing workflow,
  cached/offline and evaluated-empty requests, genuine absence, failure, fresh-process
  lazy import, detached ownership and saved readers without new credit.
- Published provider/dependency closure is verified and adopted for every supported
  Python minor. The released portable API minimum is 0.9.0; installed gates pin the
  actual public build/hash. Ackredit #22/#75/#80 are resolved. Sabueso's own Conda
  installed matrix passes separately from receiving tests; see its staged receipt.
  The consumer verifies the editable version consistency fix in Ackredit #81.
- Coordinate the attribution/knowledge/terms boundary in MOLI #36; Ackredit and
  MolSysSuite keep ownership of provider/member contracts and rollout.

The maintainer first requested early integration on 2026-10-02, then chose a hard
dependency and automatic attribution. The initial optional decision is superseded.
`dependency_preflight.py --release` now passes public closure on Python 3.11–3.14.
Its generic safeguards still reject stale floors, omitted pins and future unpublished
providers. Required metadata names the delivered minimum 0.9.0.
Next work extends observed acquisition to other sources and result types, expands
verified resource bibliography and coordinates the platform record boundary.
This change makes no release.

## Alternatives

- Use whole-card provenance as a citation list: rejected because it includes unused
  sources and lacks complete bibliography and runtime meaning.
- Use terms reports as usage logs: rejected because permissions/obligations and
  execution usage answer different questions.
- Keep Ackredit optional: superseded by the maintainer's hard-dependency decision.
  Failure tolerance and installation requirements are separate decisions; missing
  a missing public closure blocks release rather than weakening the product contract.

## Acceptance criteria and resolution

Two public offline packet results retain their own original attribution, including
reused resources, and the application's workflow captures both. Unused sources earn
no credit. Saved readers, absence and provider failures preserve result knowledge.
The automatic-composition/acquisition pilot and published receiving compatibility
pass. #108 is kept open for remaining acquisition/further-result coverage, complete
bibliography and the shared record boundary; #110 owns Sabueso release qualification. This is an initial
runtime integration, not a claim of full pipeline coverage or a public installation route.

## ChEMBL development slice after 0.12.0 (#108)

All five built-in online/fixture logical operations are observed. Normalized queries,
page/chunk metadata, raw transport identities, retries, caps, documents and received
subsets survive original failures. Native document citation forms use content-based
identities; missing authors/indication bibliography remain gaps. Empty answers,
unavailable fixture datasets and empty/unqueried batches remain distinct. Existing
client release-cache metadata is explicitly not independent release proof per page.
Scientific returns/exceptions and the frozen card schema remain unchanged.

The first standalone literal extraction in #92 additionally retains detached original
Ackredit attribution without treating it as packet composition, human curation or a
source download. `literal_uniprot_mention@1` names its tool/version/configuration and
input hash. Explicit `Card.add_literature_extraction` and `ExtractionStore` now
preserve original scientific support and supplied runtime receipts through
storage/refresh. Reuse retains original producer/use contexts; readers add no credit.
Payload-only refresh states the missing sidecar instead of reconstructing attribution.
New scientific intake fields use unpublished schema 0.3.12, with all published
schemas/receipts unchanged. Broader rules and article metadata/terms remain #92.

Tests: `test_chembl_acquisition_offline.py` and
`test_rule_literature_extraction_offline.py` join the unchanged installed-provider
CI/release tests, alongside `test_literature_intake_offline.py` for original support
and receipt replay, terms-profile boundaries and honest missing-sidecar refresh.
The current checkpoint passes 1,779 source offline cases and 469 unchanged installed
integration cases. Source and installed diagnostic receiving evidence uses public
Ackredit 0.9.0; this development slice is not a new published Conda package.
All eight read-only public-installed 0.12.0 notebook copies execute. Temporary host
instrumentation preserves 19 observed acquisition records (18 received, one empty)
and two composition records with available attribution, plus original sidecars.
Private content stays outside public reports and repositories; original notebooks
remain unchanged.

The design review (#112) makes further sources/results,
complete bibliography and MOLI record/consumer boundaries explicit remaining work.
Local wheel testing uncovered stale incremental `build/lib` modules (#113); a
source-byte/membership guard rejects them before installed receiving qualification.
Published 0.12.0's independently qualified public Conda artifact is unaffected.

## PubChem development slice after 0.12.0 (#108)

Built-in online/fixture compound, structure-match and BioAssay target operations are
observed. Native per-assay version/revision/date metadata (including zero) is
preserved without inventing global or per-row versions. Source-described depositors
are contextual declarations, not directly consulted providers. Resource-description
citations and original PubMed pointers retain distinct roles; absent publication
metadata and depositor bibliography remain explicit gaps.

Queries, POST-body identities, CSV/summary/property hashes, row totals/caps/order,
chunks, retries and archive reuse/replay retain original retrieval times. Received
subsets survive a later failing batch, with the terminal outcome and counts explicitly
scoped to received target rows before completion. Empty, absent, rejected-input,
unavailable-fixture and offline-unqueried outcomes remain distinct. Rejected input
does not receive completed-data credit. Scientific payloads, exceptions and schema
0.3.12 are unchanged; saved readers add no credit.

`test_pubchem_acquisition_offline.py` is copied unchanged into installed-provider
CI and future staged gates. These component-local traces do not define the shared
MOLI ProjectRecord/Recorda contract.

## BindingDB development slice after 0.12.0 (#108)

Built-in REST, fixture and mirror affinity queries are observed without scientific
payload/exception/schema changes. Queries, cutoff/limit/order, total/kept counts,
original response hashes, DOI/PubMed forms, archive reuse/replay and retries survive.
Resource-description citations and native measurement pointers retain separate
roles; incomplete forms cannot replace fuller host citations. REST versions/origins
and missing bibliography remain unknown. A mirror's declared data origin does not
claim direct access to an imported provider.

Mirror queries retain local access, known manifest release/URL/checksum/installation
time and a manifest hash without network attempts. The manifest does not prove
live REST release or index integrity on every query; its installation-time retrieval
basis and current event times stay distinct. Fixture cutoffs are not reapplied;
their scope is explicit. Installation/update and constructor failures remain outside
query observation.

Decoded-empty, absent-fixture, offline-unqueried, failed and partial-before-processing
outcomes remain distinct. Original HTTP and corrupt-index failures are retained.
The source-local #114 parser fix recognizes the documented empty-string absence
forms (exactly empty HTTP 200 body or JSON empty string), preserving wire hashes,
archive references and retrieval times. Malformed/unexpected responses remain
failed without completed-data credit; other clients keep default JSON retries.
`test_bindingdb_acquisition_offline.py` joins unchanged installed-provider CI and
future staged gates; saved readers add no credit. Other sources/custom clients,
full bibliography and MOLI's shared record/consumer coordination remain open.

`Card.explain_disease` (#91) reads pinned disease groups without acquisition or
new Ackredit credit. Original association/selected-annotation support, stored
identity/hierarchy links, alternatives and whole-card ungrouped outcomes remain
visible. Default `disease_grouping@2`/`disease_group_explanation@2` (#115) retains
all identity paths and leaves contradictory or unfinished branches ungrouped.
Explicit `grouping_rule="disease_grouping@1"` preserves historical lookup and its
partial explanation at the unchanged card pin. Neither rule acquires new credit.

`Card.explain_knowledge_state` (#91/#116) reads exact classification branches,
selected/alternative support, source coverage and matched request reports at the
original card pin. Scientific support is separate from query outcome/count reports;
per-request assertion membership is explicitly not recorded. Missing support remains
partial, and negative assertions are never invented. The reader changes no payload,
fetches no source and adds no credit. Multiple original UniProt versions are retained.

`Card.explain_measurement` and `Card.explain_bioactivity` (#91) retain exact original
relationship/assertion pins, source versions and actual grouping/class-voter decisions.
Copies, ambiguity, precision quantities, thresholds, raw units, ranges, single-point
concentrations, consistency checks and discordance remain visible. Whole-card
candidate/glossary inputs are explicit context; stored identity metadata has locators,
not invented per-assertion membership. These readers add no acquisition or credit and
change no scientific serialization.
The #117 diagnostic fix retains missing activity-only originals and exact pointers;
later provenance/statement resolution removes the singleton diagnostic. Groups,
voters/classes and current/historical source support remain unchanged, without
new acquisition or credit. Local grouping never proves external source absence.

`Card.explain_ligand_site` and `Card.explain_ligand` (#91) extend inert pinned
readers to annotated overlap and the protein/molecule deck crossing. Source-stated
identity, actual class/name choices, annotations/conflicts, structural instances
and native deck snapshot/membership metadata retain distinct support. Duplicate
deck members remain explicit and partial; source absence is never invented.
The #118 correction defaults to distinct included measurement groups across matched
items (`ligand_measurement_count@2`), retaining explicit source-record counts and
counted ids in `ligand_deck_explanation@2`. Explicit `@1` retains the published
numeric policy at current/historical pins. Original grouping/class support survives.
These readers change no scientific schema or attribution and add no execution credit.

## Chemical identity observation (#108)

CCD component batches and UniChem InChIKey/source-id lookups retain normalized
queries, POST/wire/decoded identities, retries, original archive references/times,
native linked source forms and distinct empty/unavailable/unqueried/failed outcomes.
Received components/compound data before later processing or read failures remain
partial; the original exception survives. CCD batches retain per-component outcomes
and completed ids; fixtures cannot establish absence in an external source.

Versions remain unstated. CCD release status/dates and UniChem compound ids are not
database releases. UniChem linked resources are its statements, not direct access;
existing identity/mapping/first-returned-compound policies are unchanged. Verified
CCD/RCSB-distribution and UniChem description bibliography is credited independently.

`resolve_molecule_card` retains card/resolution traces and `ligand_deck` exposes
detached `Deck.acquisition_trace` with native snapshot, result pins and input protein
pin. Payload-only saved or ordinarily derived decks create no trace or credit;
original sidecars remain host-owned. Shared MOLI persistence/correlation contracts
and broader source/result/custom-client observation remain open. The unchanged
chemical identity tests join public-provider CI and future staged receiving gates.

## PDBe-KB aggregate observation (#108)

Built-in ligand-site and interface-residue queries retain separate operation records,
native aggregate/group identities, original wire/archive hashes and retrieval times,
retries, evaluated-empty/HTTP-not-found answers and unqueried/unavailable/failed access.
Group indices and native accession/type/numbering/structural reference forms preserve
source scope. The count is returned aggregate records, not mapped relationships.

Versions remain unstated. Referenced PDB entries and linked providers are declarations,
not additional direct access or source versions. Verified PDBe-KB description credit
does not substitute for missing structure/method/provider citations. Raw returns,
exceptions, maps and card schemas remain unchanged; card/refresh pins and inert
saved-reader behavior survive. Concurrent queries retain original contexts in the
enclosing capture with the public Ackredit floor. The unchanged PDBe-KB regression
file joins installed-provider CI and future staged receiving gates.

## AlphaFold DB model observation (#108)

Built-in model-list queries retain original per-record ids/versions, response/wire/
archive identities, retrieval times, retries, evaluated-empty lists, HTTP absence,
fixture unavailability, unqueried offline access and original failures. Unknown
latest versions and partially invalid lists stay explicit; repeated ids never
collapse distinct indexed versions. Counts refer to source records, not mapped
relationships. Historical versions are not consulted models or database releases.

Native tools/providers, isoform/fragment accessions/ranges and artifact URLs remain
context; no additional source access, coordinate/PAE/MSA download or current model
generation is claimed. The three recommended resource/background references keep
description roles, with explicit gaps for model-specific method/provider citations.
Raw returns, scientific maps, experimental/predicted separation and schema stay fixed.
Card/refresh pins, inert saved reads and concurrent enclosing-capture contexts have
guards. The unchanged regression file joins public-provider and future staged gates.

## InterPro family-site residue observation (#108)

Built-in online/fixture `site_residues` queries retain native signature keys,
accession/name/member forms, locations/fragments and source-scoped counts. Counts
measure returned signatures, not mapped sites. `InterPro-Version` and fixture
`version` have header/fixture release bases; unknown versions are never filled
from signature/member identifiers or independent UniProt metadata.

Original decoded/wire/archive identities, retrieval times, retries and reuse/replay
survive. Empty objects/bodies and HTTP 204, HTTP absence, unavailable fixtures,
unqueried offline access and failures remain distinct. Empty answers cannot
distinguish accession existence from missing site annotation. Unexpected shapes
retain their receipt without completed annotation credit; partial signature maps
retain actual received subsets. Scientific returns/exceptions, mappings, schema,
card/refresh pins and inert saved readers stay unchanged.

Verified InterPro resource-description bibliography has full original author and
publication metadata. Missing member/signature/site citations stay explicit.
Source-supplied positions and declared member resources do not claim local alignment,
InterProScan execution or direct member access. Concurrent capture and installed
public Ackredit receiving tests exercise this slice. Other built-ins/custom clients,
further result types and shared application-record coordination remain open.

## Persisted application exercise (#108/#112)

`examples/persisted_pipeline/` persists public fixture knowledge, original literal
extraction/article support and detached operation/result/workflow attribution.
Separate producer/reader/reuse processes exercise full/index packets and exact item
reads. Reacquisition advances current heads while original pins, native authors/
pages/citations and original use/version context survive. The reader validates
sidecar hashes, semantic bindings and bibliography/contextual-use closure; it
acquires nothing and adds no credit. A missing fixture stays unavailable without
external absence claims; the fragment is synthetic with unknown rights.

Thirteen regressions refuse missing/changed/misbound files and overwrite attempts,
also in unchanged installed-public-provider gates. The manifest is local application
data, not a shared ProjectRecord schema or transactional journal. Nextia Evidence
and MOLI Recorda correlation/reliability acceptance remain with their owners;
broader source/result/bibliographic coverage stays open.

## Explicit article metadata attribution (#92/#108)

Europe PMC article core queries now retain native bibliography/declared licence,
service-version basis, original wire/archive hashes/times, reuse and distinct empty,
partial, unavailable, unqueried and failed outcomes. Full author/page/journal forms
credit the source publication; incomplete metadata retains explicit gaps. Explicit
fragment binding reuses supplied original access attribution without a new lookup.
Independent database metadata assertions and original extraction support survive
stored replay/refresh; pinned packet composition credits only represented stored
article citations. Reader calls remain inert. Service versions are not article
revisions, open access is not permission, and declared article licences grant no
rights to arbitrary supplied fragments. Raw archive retention stays per-publication;
broader bibliography/results and application-record coordination remain open.

## Public 0.13.0 delivery (2026-10-05, #121)

The source-observation, literal intake/article metadata, pinned explanations and
independent persisted application slices above are published in 0.13.0 with
public Ackredit >=0.9.0. Exact CI passes 15/15; all 12 installed OS/minor lanes
and a clean public install pass 613 cases and the public workflow. Promotion
preserves the staged digest; all 960 Zenodo source files equal the qualified tag.
Receipt: `devtools/conda-build/receipts/sabueso_0.13.0_public_2026-10-05.json`.
Broader #108 coverage and the shared MOLI/Nextia/Recorda acceptance remain open;
the dated earlier sections retain their original qualification boundaries.

## MONDO index-query observation (development, #108/#123)

Built-in term/equivalence queries retain normalized identifiers, native equivalence
and definition-reference forms, OBO header versions, exact file/lookup identities,
asset tags/URLs/checksum verification and original index origins. A private indexed
tuple carries its download receipt in the existing process cache; clearing that
cache drops the same index/receipt without a second cache or default persistence.
Subsequent `memory` queries and `mixed` selector/index queries distinguish current
requests/attempts from the original download. Archive replay/reuse keeps original
times, versions, wire hashes and retrieval references.

The #123 client correction preserves the original response time in scientific
results as well as runtime records, and rejects obvious non-OBO/invalid UTF-8 input
as connector failures instead of apparent missing terms. Missing fixture files are
unavailable connector failures. Native partial term-stanza fixtures remain supported;
the public parser utility is unchanged. Pre-existing indexes without receipts state
unknown original origins/times and explicitly identify the legacy source-time fallback.
Valid scientific mappings/identity, card fields/schema and stored states stay fixed.

Received/empty queries contribute the complete MONDO resource-description citation
to the enclosing Ackredit capture; unqueried/failed/unavailable accesses acquire no
completed credit. Definition pointers and imported terminology declarations do not
establish additional access or complete term bibliography. Direct disease resolution
retains exact final card/resolution traces. `get_term` adds the standard detached
envelope trace; raw client records keep their shape. Provider failures stay explicit.

The disease example `@3` saves MONDO observations beside its original scientific
support and workflow. Independent readers also accept genuine original `@1`/`@2`
bundles without changing their coverage gaps or generating credit. Public Ackredit
0.9.0 remains the receiving floor; no provider change is required. At that checkpoint,
Open Targets/Orphanet, other disease sources, deck operations and shared
recording/consumer acceptance remained pending. Local gate receipts are in the independent
journey audit; no new public release or remote matrix qualification is claimed.

## Association intake and disease-build traces (development, #108/#124)

Open Targets now observes both association directions with native GraphQL query/
page/hash/version/order/count and partial completed intake. Changed count/version
or disappearing entities across pages cause connector failure, preventing mixed
scientific source states. Explicit null entities remain evaluated absence; missing
native fields/errors/malformed input and unavailable fixtures stay separate.

Orphadata retains original XML/index receipts, byte hash, header date and indexed
SwissProt scope. Original scientific/runtime times survive memory/archive reuse.
Bare indexes explicitly lack origins; native validation pointers do not establish
consulted publications. These client-integrity corrections belong to #124, without
an upstream Ackredit change or altered public parser/card schema/default persistence.

Disease builders retain detached executing version/time, original input/support
pins, final deck/member pins, rule/limit and source/exclusion outcomes. Existing
science and custom clients do not establish new observed access. The example `@4`
binds these traces and reads genuine `@1`/`@2`/`@3` reports inertly. Completed queries
contribute the full Open Targets resource article and recommended Orphadata dataset
citation to host capture; underlying study bibliography remains incomplete.

At that checkpoint, DISEASES/ClinVar/MedGen observation, full study bibliography, support-aware admission
(#29), non-protein packets (#71), shared consumers and publication/remote matrix
qualification remain pending. Detailed receipts live in the independent journey audit.

## Disease channel, variant and identity observation (2026-10-06, #108/#125)

Development DISEASES, ClinVar and MedGen built-ins now contribute observed access
and verified resource citations to host captures. DISEASES preserves native channel
date/file/index origins and reports unknown older disk-cache history. NCBI preserves
native page queries/hashes/order/counts and completed subsets, separates ClinVar
build/accession versions from MedGen last-update times, and refuses incomplete or
ambiguous identity. Missing fixtures remain unavailable; invalid protocols do not
establish absence. Personal keys are excluded from recorded request identities.

The example `@5` preserves its original workflow credit and reads genuine `@1`–`@4`
bundles without reconstruction or new credit. Scientific serialization, identity
rules and default persistence remain fixed. No new Ackredit provider contract or
provider workaround is needed; #125 owns the Sabueso integrity corrections.
Underlying study/submission/terminology bibliography, finer support admission (#29),
non-protein packets (#71), shared consumer guarantees and qualified public delivery
remain pending. Final artifact and test receipts are in the journey audit.

## Conservative disease-deck admission (2026-10-06, #29)

Development `disease_deck_admission@1` creates a distinct derived deck only when
all embedded native context permits the requested use. It then checks every raw
member statement, rather than using resolved alternatives to license retained
copies. Removed members retain historical identity references and native candidate
bases; unknown/restricted shared terms refuse with an item-level report. Finer
filtering by terms of use and raw per-record rights remain pending.

Admission and saved JSONL/SQLite/store reads acquire nothing and add no runtime
credit. The original deck's acquisition/portable attribution sidecars remain
original, rather than becoming a receipt for the derived deck. No new Ackredit
contract or workaround is needed. Separate SDK tests and installed-artifact
qualification are recorded in the journey audit; existing `@5` example receipts
are unchanged.

## Native ChEMBL indication references (2026-10-06, #108)

`chembl_indication_references@1` preserves native reference forms and all row/page
occurrences in the existing detached source acquisition record and portable host
capture. It distinguishes `source_cited_reference` from executed resource access.
Grouped identifiers remain grouped; native alternative forms have separate
content-based citation IDs and never replace a fuller host citation. Completed
pages remain creditable before later failures; fixture result identity, original
times, source release bases and archive reuse/replay remain explicit.

Valid native URLs become incomplete web citations; identifier-only forms retain
their exact original form as `other`. No title/author/year, target version, article
identity or permission is inferred. Missing/malformed forms and unqueried target
metadata remain explicit gaps. Source scientific returns, frozen schema and
example `@5` reports stay fixed. Linked study/publication metadata and observation
of ClinicalTrials.gov remain a subsequent bounded #108 slice.

## Development clinical registry extension (2026-10-06)

ClinicalTrials.gov `studies` and explicit `study_references` add native registry
page/entry/version, reuse, empty/unavailable and partial/failure observation.
`clinicaltrials_registry_observation@1` distinguishes API protocol, data timestamp
and study update date. Registry records and cited pointers contribute different
roles, with native alternatives and occurrence scope. Explicit Europe PMC lookups
add original article metadata and preserve returned collective authors (#128).
The client integrity fixes are owned by Sabueso #127; author projection by #128.
This uses public Ackredit 0.9.0 APIs without a provider workaround or new shared
contract. Linked-target access, permissions, clinical efficacy, full bibliography
and MOLI/Recorda guarantees are not inferred. The accumulated implementation
is included in the authorized 2026-10-06 code checkpoint; current delivery
and exact remote CI are recorded in `../CHECKPOINT.md`, Resume here.

## Exercised taxonomy observation gap (2026-10-08, #108/#132)

The [bounded consumer revalidation](private_consumer_revalidation.md) at qualified
code `dc46424` preserves eight original raw source responses but observes only
four UniProt operations. The four NCBI Taxonomy responses retain native source/
retrieval metadata; their built-in client is outside the explicitly declared
34-source observation coverage. This is a remaining Sabueso adapter gap, not an
Ackredit defect or permission to claim complete bibliography.

That original report preceded implementation. The follow-up now observes existing
online and fixture `taxa` routes and public `get_taxon`: batch/request scope,
partial and missing results, unavailable fixture IDs, failures, archive reuse/replay
and original scientific retrieval times. Unknown source versions and underlying
bibliographic metadata remain unknown. Regression inputs use public fixtures and
synthetic responses; private consumer outputs stay private. That checkpoint covers 35
declared sources, with other sources/custom clients still unobserved. See the
[follow-up qualification and memory correction](private_consumer_revalidation.md#taxonomy-and-memory-follow-up).
Complete #108 and overall consumer acceptance remain open.

## GTEx tissue observation (development, 2026-10-10, #108)

Existing built-in online/fixture tissue operations and public `get_tissues` now
retain observed query/row/envelope/transport identity, retries, original archive
times and explicit empty/unavailable/failed/unqueried states. Requested dataset
labels stay separate from unknown native revisions; a successful single response
does not prove complete dataset coverage. Card-selected terms do not determine
the acquired row count. The existing prerequisite gate creates no operation when
required pext inputs are absent. Completed access credits the declared GTEx Portal
resource description, with native-revision and underlying-publication gaps.
Detached sidecars remain readable from another process without new acquisition,
derivation or credit. Development coverage becomes 36 declared source families;
UniRef, OMA, gnomAD, derived comparative operations, complete bibliography and
consumer-owned recording/Evidence acceptance remain open.
[Behavior and qualification](gtex_observation.md) /
[source receipt](gtex_observation_checkpoint.json): code `2b5db53`, 34 new cases,
5,930 local-original cases, 15/15 exact-source CI and governance. All nine public
offline lanes pass 4,377 cases; all four installed public-Ackredit lanes pass 1,015.

## UniRef page observation (development, 2026-10-10, #108)

Existing built-in cluster/member operations retain page identities, native release
headers, continuation, received/kept counts and completed scope before failures.
The shared scientific source remains `UniProt`; source-family coverage remains 36.
Conflicting or unstated page releases are explicit, and fixture labels do not prove
native revisions. The actual UniRef API URL is credited alongside UniProt's
description; member publications and sequence revisions remain gaps. Scientific
pins remain equivalent to the same unobserved fixture client; saved readers render
original credit without new operations. [Scope and qualification](uniref_observation.md)
records code `c6cb0e3`, 33 new cases, 5,963 local-original cases and 15/15 exact-source
CI plus governance. The [source receipt](uniref_observation_checkpoint.json) verifies
4,410 cases per public offline lane and 1,048 per installed public-Ackredit lane.
The subsequent [pagination correction #140](../archive/uniref_pagination.md)
is source-qualified at `3a47490`: 21 new cases, 5,984 local-original cases and
15/15 exact-source CI; [its receipt](../archive/uniref_pagination_checkpoint.json)
retains public/installed compatibility scopes. OMA follows in the qualified slice
below; gnomAD follows in its qualified slice below, while derived operations
and complete bibliography stay open.


## OMA operation observation (development, 2026-10-10, #108)

Built-in xrefs/protein/ortholog operations belong to OMA; entry-name resolution
belongs to UniProt. Original response/continuation/revision bases, raw versus
selected counts, per-batch ambiguity and partial failures remain explicit.
Missing local files are unavailable. Source-stated match gates and strain
relationships stay fixed; equivalent unobserved fixture clients produce the same
scientific pins. Resource credit declares the actual OMA REST API and UniProtKB
search API URLs; underlying publications and sequence revisions remain gaps.
[Scope and qualification](oma_observation.md) records `593ba76`, 47 new cases,
323 selected and 6,031 full local-original cases with twelve workers, 82
post-editable cases and 15/15 exact-source CI plus governance. The
[source receipt](oma_observation_checkpoint.json) verifies 4,478 cases per public
offline lane, 1,116 per installed public-Ackredit lane and independently hashed
full receptor captures. Original-answer replay and inert reading pass without
new queries.
No new provider queries or private fixtures; full installed-artifact/human
acceptance and broader derived-operation/bibliography coverage stay open; the
gnomAD slice follows below.

## gnomAD operation observation (development, 2026-10-10, #108/#141)

Variant/transcript/consequence/pext access retains actual GraphQL scope, response
identities and per-batch transcript/variant bindings. Dataset/genome request labels
and client pext/GTEx descriptions do not establish native releases. Received,
returned and card-selected counts remain separate; failed later aliases retain
completed partial scope without a partial scientific return. Missing local files
are unavailable. Missing upstream gene identity is unqueried before source client
construction (#141). Resource bibliography identifies the existing gnomAD GraphQL
API and states publication/revision gaps. Normal supplied-gene scientific pins and
original archive receipts survive independent inert reading. [Scope](gnomad_observation.md).
Source `682e226` passes 54 new cases, 340 selected and 6,085 full local-original
tests with twelve workers, 89 post-editable cases and 15/15 exact-source CI plus
governance. The [source receipt](gnomad_observation_checkpoint.json) verifies
4,532 cases per public offline lane, 1,170 per installed public-Ackredit lane and
independently hashed full receptor captures. Original-answer replay and inert
reading pass with zero new provider queries; detailed artifacts stay private.
No new provider query or private fixture. Derived operations, full bibliography and
installed-artifact/human/consumer acceptance remain separate.
