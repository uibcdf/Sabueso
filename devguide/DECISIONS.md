# Sabueso — Decision Log

## Bind contact derivation to original source inputs and preserve unresolved identity (2026-10-23, #148)

New RCSB mappings store raw contact/alignment inputs in their source assertion,
keep mapped instances only in qualifiers, and bind `rcsb_ligand_contacts@1` to
that assertion with explicit qualifier/input scope and ambiguity diagnostics.
Do not merge unidentified instances or equal residue labels from different source
contexts; do not select the first ambiguous UniProt alignment or conflicting bound
flag. Native `ligand_instance_scope@1` keeps foreign/unknown-axis contacts unplaced
and does not infer chain spans from unidentified instances. Accumulate optional
lineage in unpublished schema 0.3.14; mark historical gaps without backfilling.
The [integrity scope](pending_proposals/card_contact_mapping_integrity.md) leaves
AlphaFold and broader exploration/acceptance work open before 0.15.0.
New packet mapping `packet_aspects@8` declares the instance rule. Historical `@6`/
`@7` packet facts and terms retain a frozen native projection, rather than silently
reconstructing those scopes with the new interpretation; coordinate consumers in
MOLI #36 without changing the packet envelope format.

## Keep ligand instances scoped to their original structure declarations (2026-10-23, #148)

Present one original ligand instance per typed location, with structure/component/
instance selection, original parent support and inert saved verification. Preserve
contact `position` versus `seq_id`, distance units and unknown/false/empty states.
Do not join instances to aggregated contacts, assemblies or biological relevance.
The mapper's alignment/minimum-selection output is recorded context, not a newly
verified derivation; retain historical gaps and bind actual rule/inputs before
extending derived navigation. Malformed declarations remain stored and inspectable,
while invalid candidates no longer break glossary construction. See the
[scope](pending_proposals/card_protein_source_exploration.md#original-structure-local-ligand-instances).

## Present retained protein source context without inventing derived support (2026-10-23, #148)

Add source-oriented sequence/annotation, predicted-model and site/contact routes
over the shared capture and original saved bindings. Preserve axes, modifiers,
units, exact relationship subjects and field-level versus relationship support.
Do not duplicate model coverage, overlap, residue projection or instance merging.
The AlphaFold mapper's stored match/isoform context is not relabeled as a direct
source statement: show recorded flags and their unestablished derivation/input
basis until the owning integration retains it explicitly. The
[scope](pending_proposals/card_protein_source_exploration.md) keeps derived/agent/
human acceptance open in the full design required before 0.15.0.

## Complete the broad exploration design and human experience before 0.15.0 (2026-10-22, #148/#112)

The maintainer explicitly selected the full nature-specific design, including
activities, clinical context, variants, sites and comparisons, as a prerequisite
for 0.15.0. The initial A–D audit remains an intermediate milestone. Implement and
qualify every broad panel plus shared navigation, source/support inspection,
saved reading and compact agent parity; validate the combined experience with
researchers and declared workload budgets. Technical tests do not establish the
intended exceptional human usefulness. The
[completion inventory](pending_proposals/card_exploration_completion_0150.md)
records the remaining work. Implementation continues, while release consolidation,
candidate selection, schema freezing and publication remain paused.

## Explain original source roles and ontology basis in human wording (2026-10-22, #148)

Label original selected, alternative, unclassified and relationship support in
source explanations. Expose retained source methods/units and missing/conflicting
support without ranking reliability or inventing selection roles. Render readable
synonym scopes and broader-term basis/rules; absent derivation plus retained support
does not independently prove a direct source claim. Keep original cells, schemas,
identities and scientific records intact. Preserve earlier saved labels and label
filters while explaining their original metadata with current previews. The
[scope](pending_proposals/card_human_support_labels.md) retains acceptance limits.

## Deliver complete structural cell support without rewriting original science (2026-10-22, #148)

Make cell field identity and relationship-level support explicit, sharing complete
assertion membership at item level. Do not invent qualifier-level lineage. Defer
values and mandatory interpretation/support atomically, preserving typed scientific
states and exact inspection locations. Let a complete item start the next page
when it fits there. Apply this current transport to live and historical inert
results, preserving their original wire, rules, quantities and identities. Measure
capture, materialization, cached pages and persistence separately; compact output
does not establish cheap computation or compact saved history. The
[scope and bounded measurements](pending_proposals/card_cell_support.md) retain
limits and remaining technical/human acceptance.

## Version structural display selection separately from science (2026-10-22, #148)

Typed machine equality, exact membership and scalar ordering select over the same
captured structural result as human exploration. Keep unrestricted selection @1
identities and original scientific wire schemas unchanged; bind new requests under
selection @2 with the frozen `structure_access_selection@1` policy. Retain exact
criteria, ordered members and inspectable display exclusions without narrowing
source coverage or support. Saved lookup returns exact retained variants, and a
partial machine selection never replaces a complete human topic. Current catalog
capabilities belong to the access layer. See the [scope](pending_proposals/card_agent_selection.md).

## Close HTTP responses at their owning boundary (2026-10-22, #151)

Close discarded transient errors before retry waiting and original archive errors
after reading, including failure paths. Keep final raw transport errors native
and readable for their direct caller, who owns closure. Source clients close
errors they translate or consume, after native body parsing where classification
requires it. Preserve status/retry budgets, original archived bytes and source
absence/failure semantics. The [source-access contract](SOURCE_ACCESS.md#http-response-lifetime-151)
records ownership and the dated regression evidence. This is a resource correction,
not a shared platform rule, warning filter or public release.

## Preserve original scientific exploration with frozen historical checks (2026-10-22, #148)

Keep literal format @1 unchanged and introduce scientific exploration format @2
under the same save/read API. Retain original structural/region/coverage results,
physical predicates, source support and navigation. Restore inert results and
check recorded decisions with versioned historical predicates/catalogs; never
replace them with current scientific views. Expected comparison records are not
new knowledge. Coverage keeps its original classification inputs, catalog and lazy
explanation factory, avoiding classification on save. Exact retained machine
requests are restored per focal capture; unavailable variants stay `not_saved`.
The [scope](pending_proposals/card_saved_science.md) keeps broader conformance,
cost and researcher acceptance open. No schema, acquisition, shared MOLI contract
or release changes are selected; the 0.15.0 pause remains in effect.

## Retain standalone diagnostics and honor caller restrictions before formatting (2026-10-22, #150)

Keep the existing import/bundle bootstrap and detailed defaults. Qualify
application/project precedence and real emissions on capable public providers.
Avoid rejected-value repr and native-error str in the reviewed argument-error
paths before SMonitor collection when a caller forbids them. Preserve codes,
default wording, scientific validation, source outcomes and Python warnings.
Defer pure registration-only setup until a named embedding host needs it;
safe audience maps/identity export have no selected current boundary. The
[receiving decision](DIAGNOSTIC_RECEIVING.md) records exact scope, provider
capabilities, evidence and limits without changing dependency floors.

## Add distinct initial nature profiles and original shared coverage (2026-10-21, #148)

Continue the human-first exploration route with separate molecule chemistry/property
and disease definition/hierarchy/terminology experiences. Share exact retained-field
presentation and source closure, preserving property units/methods/alternatives and
disease hierarchy versus source-stated equivalence. Use the existing knowledge-state
classifier and lazy exact scoped explanation, cached at the focal capture. Preserve
unknown counts and original rules rather than inventing a completeness score or
request-level assertion membership. The [scope report](pending_proposals/card_nature_exploration.md)
keeps contextual navigation, saved reading, specialized machine conformance and
researcher acceptance open. No acquisition, schema change, new scientific engine,
shared MOLI protocol or 0.15.0 release/consolidation is authorized by this slice.

## Prioritize the first complete human protein exploration journey (2026-10-21, #148)

Following the maintainer's review of the incomplete human experience, prioritize
scientific opening, explicit questions, understandable results, original sources
and exact return navigation before broadening machine grammar. The
[protein continuation](pending_proposals/card_protein_exploration.md) selects retained
function/identity fields without inferring function, and delegates explicit
canonical region questions to the same captured structural result/explanation.
Question request metadata is presentation context, separate from scientific result
identity. Other natures need their own scientific profiles; shared coverage,
contextual navigation, saved reading, machine conformance and researcher acceptance
remain open in #148. This is local development during the pre-0.15.0 pause, not a
release or a shared MOLI protocol change.

## Specify bounded agent access over shared exploration results (2026-10-21, #148)

Continue the maintainer's human/agent distinction with a concrete
[machine-access design](pending_proposals/card_agent_access_v1_contract.md).
Select `card.access()` and `explorer.access` over the same capture factory/cache
and scientific adapters; use immutable selections with projected fields, exact
filters/order, bounded page envelopes and session-bound cursors. Preserve original
values/quantities/support/qualifiers, distinguish item enumeration from complete
value delivery, and provide explicit literal traversal or bulk export for large
content. Save through the shared exploration bundle, without portable ephemeral
cursors or new scientific computation during reading. Current Card/packet APIs
and schemas stay unchanged; this local design does not redefine MOLI's shared
query/packet contract. Initial size defaults are engineering choices pending
measurement, not token/performance claims. Implementation and separate human,
machine-conformance and cost acceptance remain open.

## Distinguish human and agent access without duplicating science (2026-10-21, #148)

Following authorization to begin bounded exploration implementation, the
maintainer clarifies that researchers need friendly, intuitive navigation while
agents may use technical access optimized for economy and completeness. Share
scientific readers, values, rules, units, identity, snapshots and source support;
provide different presentation/access affordances. Complete machine access means
selective discovery, exact retrieval, expandable support and exhaustive access
when requested, not a full Card dump for every question. Bounded output must state
coverage/completeness and preserve consequential qualifiers. Existing selective
Card methods and protein-oriented full/index packets are foundations, not proof
of a bounded all-nature agent API. Projection/pagination/continuation contracts
remain to be designed additively; shared packet changes require MOLI #22
coordination. The [plan](pending_proposals/card_human_exploration_api.md#human-and-agent-access-to-the-same-knowledge)
records acceptance for both consumers. No new SDK API or measured savings are
claimed; 0.15.0 consolidation remains paused.

## Resolve the five exploration contracts in a bounded v1 design (2026-10-21, #148)

At the maintainer's request, select a concrete view/item/cell model, stable semantic
identity separate from presentation, labeled object selection, exact captured
cross-Card context and explicit ambiguity, and a versioned inert saved-result
contract with an explicit new-interpretation boundary. Complete literal access
applies to every valid Card; initial rich adapters cover protein function/structures,
molecular identity/properties and disease definition/classification. The broader
scientific catalogs remain planned. The [v1 contract](pending_proposals/card_exploration_v1_contract.md)
records these decisions and public paper walkthroughs whose input facts were
verified offline through existing readers. This resolves the design findings;
it does not implement the API, qualify researcher usefulness or resume 0.15.0.

## Preserve Card nature in human exploration design (2026-10-21, #148)

The maintainer requires an excellent scientific exploration design for each Card
nature rather than a protein interface applied indiscriminately to molecules or
other entities. Share navigation, source tracing and complete-access guarantees;
develop opening content, scientific questions, views and criteria separately for
protein, small-molecule and disease Cards. Future natures need their own reviewed
profiles; generic inspection preserves access without claiming scientific support.
The [detailed proposal](pending_proposals/card_exploration_detailed_design.md)
records candidate interactions and nature-specific walkthroughs. Its proposed
entry/signatures, persistence mechanics and researcher usefulness are still under
review; no API implementation or release resumption is implied.

## Design human exploration for simplicity and complete inspectability (2026-10-21, #148)

The maintainer requests an intuitive Card exploration experience with access to
all retained information and source-grounded assistance for assessing molecular
systems. Accept progressive Card/topic/item/source navigation, complete thematic
or generic access, preserved support/units/unknowns and separate human usability
acceptance as the design direction. Reuse existing scientific engines and preserve
current public contracts. Names, result types, snapshot mechanics and saved formats
remain proposed until walkthrough and contract review. The
[plan](pending_proposals/card_human_exploration_api.md) is design documentation;
it does not implement an API, change shared MOLI contracts or promise release scope.
This is the matter being addressed during the maintainer-directed pause before
0.15.0 consolidation (#112); implementation and resumption require an agreed scope.

## Observe OMA statements separately from UniProt name resolution (2026-10-10, #108)

Observe existing xrefs/protein/ortholog operations under `OMA` and entry-name
resolution under `UniProt`, using `oma_operation_observation@1`. Preserve source
revision gaps, native continuation and received-versus-selected counts. Retain
source-stated sequence-match gates and separate strain relationships; no similarity
or shared-name identity merge is introduced. Partial batch failure preserves
completed access and portable resource credit without a partial scientific result.
Local missing files mean unavailable access. Names with missing consumed accession
answers are connector failures. Scientific pins, schemas and original fixtures stay
fixed; resource citations do not replace method/entry publications.
[Scope and qualification](pending_proposals/oma_observation.md).

## Bound UniRef member pagination independently of row count (2026-10-10, #140)

Use `uniref_member_pagination@1`: stop before requesting an exact URL twice or
requesting more than 100 logical member pages, including empty pages. These
conditions raise `ConnectorError`, retaining completed-page observations and
portable resource credit but returning no partial scientific result. The existing
5,000-member ceiling remains successful explicit truncation and takes precedence
when reached. Transport retries count separately from logical pages; their shared
limits and per-attempt timeout do not constitute a strict wall-clock deadline.
The page ceiling permits sparse responses while bounding arbitrary distinct empty
continuations. Fixtures retain their declared subset semantics. No card schema,
source identity or original response bytes change. [Policy and qualification](archive/uniref_pagination.md).

## Observe UniRef pages under the shared UniProt source (2026-10-10, #108)

Observe existing cluster/member access as separate logical operations, keeping
`UniProt` as scientific source and terms owner. Preserve page releases and unknown
or conflicting revision bases; the client's compatibility version is not proof
of coherent pages. Record continuation, received versus retained rows and partial
failures without returning failed enrichment as scientific knowledge. Local
missing fixtures mean unavailable access. Credit the actual UniRef resource URL
alongside UniProt's description, retaining member-publication and sequence-revision
gaps. No similarity-based identity merge or card-schema change is introduced.
[Scope and verification](pending_proposals/uniref_observation.md).

## Observe GTEx access without upgrading requested labels to revisions (2026-10-10, #108)

Observe the existing built-in tissue operation and public source getter using the
common detached acquisition and Ackredit services. Keep scientific client/mapping
records unchanged while reporting the requested dataset label separately from
unknown native revision, returned rows separately from card-selected terms, and
single-response success separately from dataset completeness. A missing local
fixture is unavailable, not provider-stated absence. Preserve the established
online HTTP 404/422 exception with its client-interpretation basis. Blocked
prerequisites create no fictitious source operation; saved original sidecars and
exact card pins can be read without acquisition, derivation or fresh credit.
Credit only the declared GTEx Portal resource description; underlying publications
and native revisions remain explicit gaps. Broader comparative observation #108
and installed/human acceptance stay open.

## Restore declared enrichment requests and disclose historical gaps (2026-10-10, #139)

Derive protein refresh routing from declared exact source/data selectors. Record
supplied validated `request_options` before acquisition, including failures,
blocked prerequisites and terms exclusions. Restore historical flags and available
parameters through declared record paths; report missing parameters rather than
backfilling old records or promising frozen defaults. Conflicting parameters or
missing essential known-route identifiers require an explicit override before
resolution. Unsupported selectors remain inspectable and unqueried; dependent
PubChem copy pointers are followed only from new source answers. Explicit caller
options, including disabled sources, take precedence. Refresh is a new acquisition;
`store=` keeps the original and refreshed pins. Unpublished schema 0.3.14 adds only
optional quality records under `enrichment_request_restoration@1`; published schemas
and source assertions are not rewritten. Comparative observation/bibliography
#108 and installed/human qualification remain separate.

## Version genomic tissue scope and per-tissue coverage (2026-10-10, #138)

Development Card tissue views default to `pext_at_variant@2` and
`isoform_exon_usage@3`; their explanations use `@2`. Explicit keyword `usage_rule`
retains `pext_at_variant@1` / `isoform_exon_usage@2` and their original explanation
`@1`. Stored reports are read as originally produced, without recomputation.
Require equal explicit assembly/chromosome, source-stated transcript-to-isoform
links with compatible versions, and one consistent CDS axis before subtraction.
Missing or incompatible coordinates do not establish correspondence. Missing
transcripts make own/variable-base support incomplete. Overlapping pext records
must all state the same valid value for each tissue; agreeing bases count once,
disagreement remains conflict, and missing values remain unknown. Each tissue mean
uses its resolved bases and reports missing/conflicting coverage separately.

New gnomAD variant assertions retain requested-reference-genome context in
`source_metadata.coordinate_scope` under `gnomad_query_coordinates@1`. This is
client query/mapping context, not a native assembly echo or verified release.
Schema 0.3.14 is unpublished and additive; published 0.3.13 stays frozen. Migration
records gaps and never invents context from old dataset labels. New example format
`@2` and explicit `--legacy` keep independent reading/reacquisition of both rule
generations. Recorded gnomAD variant/pext options and limits are restored during
refresh; broader declared-source routing is #139. #108 operation/bibliography,
installed delivery and human scientific acceptance remain separate.

## Pin comparative explanations without rewriting historical rules (2026-10-09, #91)

Add sequence, variant-tissue and isoform-tissue explanation envelopes using the
existing Card/KnowledgeStore pins and SourceAssertion readers. Retain actual
region/intersection and tissue-specificity inclusion/exclusion decisions, selected
and alternative inputs, original source labels and missing/incomplete support.
The public saved-reader journey preserves producer envelopes without acquisition,
derivation or credit after later fixture reads. Card schemas and ordinary view
rules remain unchanged. Genomic scope/overlap correction is separately tracked
in #138; operation observation/bibliography is #108, and installed/human acceptance
remains independent. This follows the accepted quality plan #112.

## Keep missing dependent-source inputs unqueried (2026-10-09, #135)

An enricher can be requested while lacking the upstream knowledge needed to
formulate a source query. Introduce the internal `RequestPrerequisiteMissing`
outcome at request planning: record `not_queried` with its input explanation before
constructing or calling the client. Use it for GTEx when pext tissue keys or one
stated GTEx release are unavailable. Do not select among conflicting releases or
turn those missing prerequisites into source-stated absence.

This corrects the recorded request outcome. Existing `knowledge_state@5` already
classifies `not_queried` with an unknown count; its algorithm/version, published
schema, original SourceAssertions and historical stored reports remain unchanged.
Successful release-bound GTEx queries, received empty responses and actual source
failures keep their separate outcomes. Public regressions verify the source is not
called and the generic runner does not construct a blocked client.

## Publish recovered checkpoint and return to real consumers (2026-10-08)

The maintainer authorized publishing the recovery/consolidation checkpoint and
requested a later return to MOLI vertical-pilot use. After exact-SHA CI, revalidate
applicable private consumer workflows under
[#132](https://github.com/uibcdf/sabueso/issues/132), before broadening providers or
APIs. Keep the private checkout read-only, record executions/results privately,
and expose only generic needs and sanitized engineering receipts publicly. Source
outcomes and scientific conclusions remain separate. Existing SDK tests and older
pilot receipts cannot establish acceptance of this recovered checkpoint.


## Consolidate recovery before adding provider breadth (2026-10-08)

The maintainer approved the audit's order: fixture delivery, guide structure,
explicit source capability scope, selected recovered knowledge in scientific
journeys, and consumer coordination with measured costs. Preserve the existing
foundational and pilot-driven routes. Classify exact recovered inputs into 49
repository-delivery files and 37 protected local-only originals; verify public
and opted-in local qualification separately in the existing development environment.
Retain complete historical guide snapshots while keeping current entry documents
focused. Generate access/mapping/enricher/input scope without inferring live health
or consumer acceptance. Integrate source-active-site residue/composition context
in the protein/comparator journey under named rules and pinned support, with
independent legacy readers and explicit correspondence/operation-observation gaps.
Submit ready cross-component documentation fixes for owner review; shared contract
acceptance remains with MOLI and consumers. See the
[consolidation report](pending_proposals/post_recovery_consolidation.md), #112.


## Finish recovered-provider triage with conditional deferrals (2026-10-08)

Review the seven remaining recovered providers together at the maintainer's request.
No qualified original scientific input or authorized access/rights context is
available for immediate native implementation. Mark ASD, GtoPdb, COSMIC, ELM,
BioCyc, OMIM and CASTp `deferred` with individual concrete `revisit_when` triggers;
retain their scientific requirements and earlier receipts. Five primarily await
authorized access/agreements; ELM and CASTp await original native results and their
applicable grant. This is neither a retirement decision nor an access impossibility
claim. Credentials checked by known environment-variable presence only are absent;
that does not audit private files or all possible access held by maintainers.

The expanded 13-resource queue is 6 scoped / 0 active pending / 7 conditional
deferrals; the original 27-list is 21 scoped / 0 active pending / 6 conditional
deferrals. The historical catalog becomes 65 in use / 0 evaluating / 18 deferred /
3 retired / 1 out of scope. These counts are distinct from the whole registry.
Existing source terms, code, published card and original exports stay intact.
Track reactivation in [#83](https://github.com/uibcdf/sabueso/issues/83) and access
needs in [#95](https://github.com/uibcdf/sabueso/issues/95), with
[pending input conditions](pending_proposals/historical_provider_reactivation.md).
Continue the remaining implementation/consumer requirements rather than repeating
failed or gated requests. Keep the stash until the broader recovery is accounted.

## Recover exact native WikiPathways cross-references (2026-10-06)

Follow up five reviewed candidates: WikiPathways, HPO, GWAS Catalog, ECOD and
ChannelsDB. Recover the complete native WikiPathways bulk export with exact
namespaced-token matching across seven original xref fields. Preserve heterogeneous
column content, blank/free-text aliases, original match positions, species, authors,
pathway date labels and independent repeated/conflicting rows. The native template
already uniques/compacts xrefs and shortens descriptions; no GPML-node occurrence
coverage, role, mechanism, experimental class or biological identity is inferred.
Bound JSON/gzip/replay retains original bytes/time and CC0/source attribution.

The other four retain evaluating status: HPO annotation/input terms are unresolved;
GWAS needs bounded exact paging and original-owner/statistical scope; ECOD's newly
accessible version catalog qualifies release pointers and separate axes, not a
native domain export or data licence; ChannelsDB's assembly endpoint declares a
preferred assembly independently of geometry. No blocked endpoint was bypassed,
source prediction/search job submitted or unqualified probe made a fixture.
Historical counts become 45 in use, 27 evaluating, 11 deferred, 3 retired,
1 out of scope, 0 unregistered; 21 reviewed candidates await integration. Preserve
stash and all 87 originals. Details: `archive/local_work_2026-07/followup_01_source_integration.md`.


## Finish historical source triage and recover native EMA designations (2026-10-06)

Review the final FDA Orphan and EMA Orphan candidates together. Recover EMA's
complete native orphan JSON export with validated declared coverage, exact EU-number
selection and independent original page occurrences. Preserve duplicate numbers,
conflicting dates, unresolved references, empty fields, status/product/substance
context, generation versus retrieval times, original bytes and bound snapshot/replay.
Do not infer protein/product identity, modality, efficacy or marketing authorisation.
Keep EMA attribution in each copy and separate third-party/linked-document rights.

One direct FDA GET returned a provider excessive-requests apology with HTTP 404;
no retry/bypass was performed. Its native query/date/approval/page/export and exact
terms remain pending. No FDA fixture/connector or clinical assertions were added.
All 87 source declarations now have registry comparisons: 44 in use, 28 evaluating,
11 deferred, 3 retired, 1 out of scope and 0 unregistered. Twenty-two batch candidates
remain pending integration; review completion does not make them implemented.
Keep the stash and all 87 original exports. Details: `archive/local_work_2026-07/batch_06_source_review.md`.

## Review batch 05 and recover native CIViC profile items (2026-10-06)

Review ChannelsDB, PRIDE, CIViC, CASTp and ProBiS together. Recover CIViC native
monthly accepted-items TSV with exact profile/release selection, full validation,
all literal fields and independent occurrences on complete molecular-profile
subjects. Preserve accepted flags, contradictions, combined profiles/therapies,
original citations/time/byte SHA, source-bound snapshots and CC0. CIViC Evidence
Items are source terminology, not MOLI Evidence. No protein identity transfer,
clinical interpretation, profile expansion, extra linked acquisition or frozen
card intake follows. Read-only live acquisition and replay use the shared environment.

The other four retain concrete format/provenance/access/rights requirements in
`archive/local_work_2026-07/batch_05_source_review.md`. Counts are 43 in use,
27 evaluating, 11 deferred, 3 retired, 1 out of scope and 2 unregistered. Twenty-one
batch candidates await integration; FDA/EMA Orphan remain unreviewed. Preserve the
original stash and 87 exports. No external issue/message or analysis job was sent.

## Review batch 04 and recover native DrugCentral observations (2026-10-06)

Review MetalPDB, ECOD, 3did, DrugCentral and GWAS Catalog together. Recover the
complete native DrugCentral 20-column TSV/gzip through shared transport and exact
local accession-token selection. Preserve independent occurrences, source-native
single/composite target subjects, drug IDs, activity/units/MOA and original support.
Do not expand target groups, guess physical/log scales, merge molecules by name,
interpret clinical indications or change frozen cards. Keep CC BY-SA 4.0, full
text/compressed byte identities, unknown revisions and bound snapshot/replay scope.

The other four retain native format/coverage/axes/access/rights requirements in
`archive/local_work_2026-07/batch_04_source_review.md`. Historical counts are 42
in use, 23 evaluating, 11 deferred, 3 retired, 1 out of scope and 7 unregistered;
seventeen candidates from four reviewed batches await integration. Preserve the
original stash and all 87 original export hashes. No provider messages, accounts,
analysis jobs or separate development environment are introduced.


## Review the third five-source batch without claiming new connectors (2026-10-06)

Review BioCyc, OMIM, Interactome3D, PDBTM and TCDB together and register all five
as evaluating. Preserve current access, native identity/format/coverage and reuse
requirements in `archive/local_work_2026-07/batch_03_source_review.md`. BioCyc
needs a session and database-specific limited/open terms; OMIM needs authorized
native data and current agreement. Correct Interactome3D's historical query
requirements: one protein uses uniprot_ac, an interaction uses queryProt1/queryProt2.
Observed access failure does not establish no-result or retirement.

The public PDBTM XML probe retains separate chain sequence/PDB axes, transforms,
history and an embedded nonprofit/commercial/no-modification agreement. The TCDB
probe is a headerless mixed-namespace assignment table with repeated pairs and
multiple assignments, not a protein-function inference. Keep both bodies outside
package data until applicable representation/redistribution terms and native
contracts are qualified. No credential, form submission, provider contact, data
fixture, analysis job, card mutation or delivered connector is added in this batch.

Historical counts are now 41 in use, 19 evaluating, 11 deferred, 3 retired, 1 out
of scope and 12 unregistered. Thirteen candidates from three reviewed batches
await integration; counts of completed reviews and delivered functionality stay
separate. Preserve the original stash and 87 original file hashes.

## Review a second five-source batch and recover native ClinGen validity (2026-10-06)

Review COSMIC, HPO, ClinGen, OmniPath and ELM together. Recover the public ClinGen
native gene-validity CSV with full preamble/document preservation, validation before
exact HGNC selection and independent native classification/inheritance/SOP/panel/
report/date assertions. Keep legacy report namespaces and unknown timezone;
file/classification dates do not supply scientific revisions. Not listed differs
from an explicit No Known Disease Relationship classification and access failure.
No strongest-class ranking, gene/protein merge, variant/clinical inference or
frozen card change. Curated content retains CC0 and requested attribution.

The other four remain evaluating with concrete requirements: COSMIC authorized
native data and redistribution; HPO exact release and current annotation/input
terms; OmniPath original-resource rights and opposing effects; ELM exact data
agreement and native class/instance/sequence scope. No authenticated or private data,
provider contact, motif-search job or external write. Historical counts are now
41 in use, 14 evaluating, 11 deferred, 3 retired, 1 out of scope and 17 unregistered.
Eight candidates from two completed batches are reviewed and awaiting integration;
review and delivered-connector counts differ. Preserve the original stash and
all 87 original file hashes. See `archive/local_work_2026-07/batch_02_source_review.md`.

## Review historical candidates in batches of five; recover scoped HPA summaries (2026-10-06)

Review HPA, GtoPdb, WikiPathways, Monarch and MEROPS together. Recover the
qualified HPA native single-gene JSON reader and independent literal RNA/protein
categorical assertions with exact gene scope, full raw response, unknown native
revisions and source terms. Do not restore the old gene/total-protein projection,
quantitative shortcuts or automatic enrichment. The other four remain evaluating:
current authorized native GtoPdb access and dual rights; exact WikiPathways
cross-reference selection; Monarch per-source rights and paging; MEROPS precise
native export/release/sequence scope and database licence.

A review outcome is separate from a delivered connector. The historical catalog
now has 40 in-use declarations, 10 evaluating, 11 deferred, 3 retired, 1 out of
scope and 22 unregistered candidates. Four from this batch are reviewed and still
await implementation. Preserve the original stash and all 87 original file hashes.
See `archive/local_work_2026-07/batch_01_source_review.md` for exact native probes,
prototype defects and next qualification steps; no external write was made.

## Recover SIGNOR headerless causal declarations without first-row loss (2026-10-06)

The preserved `fetch_signor` passed a headerless native TSV to `csv.DictReader`,
losing the first interaction and treating its values as keys. Recover the documented
field order with complete native text/column validation and independent standalone
SourceAssertions. Retain regulator A and regulated B, effect/mechanism, DIRECT,
residue/sequence/modification context, score, publication pointers and source
sentences. No query-name join, complex expansion, physical binding claim,
experimental class, principal pathway selection or current sequence projection.
Native TAX_ID can differ from the requested organism, or be blank/in-vitro -1;
do not relabel it. Native `No result found.` remains a query declaration, separate
from HTTP failure and biological absence. Unknown scientific revisions and received
scope remain explicit. Native supplied TSV/gzip readers preserve the original bytes
and bind exact metadata; generic snapshot TSV still requires a header. CC BY 4.0
comes from SIGNOR's own statement; linked publications retain independent rights.
Published release 0.13.0 and frozen card schema 0.3.12 do not change.

## Preserve APPRIS native annotation occurrences without transcript overwrite (2026-10-06)

Recover the historical `protein_drug_discovery.map_appris` requirement through
one qualified explicit-human-gene native exporter and independent standalone
SourceAssertions. The old transcript dictionary combined all rows and overwrote
principal attributes and dropped genomic range context; the actual TPI1 response repeats transcript IDs with
conflicting principal labels, names and genomic coordinates. Keep every native
occurrence and its response/index support. Do not select a principal isoform,
merge protein identity, parse genomic notes into residues or infer experimental
support. Provider-default scope, unknown assembly/dataset/record/sequence revisions,
empty received arrays and failed/missing access remain explicit. Query-bound
JSON/gzip snapshots and original-time archive replay use existing contracts.
APPRIS's own CC BY-NC-SA 4.0 statement is recorded, with both noncommercial and
share-alike flags in the existing terms rule; parent method inputs and publications
retain independent rights. Frozen schema 0.3.12 and release 0.13.0 do not change.

## Recover native Complex Portal declarations and independent participants (2026-10-06)

- The legacy mapper selected guessed search shapes, collapsed participant context
  and assigned predicted/curated classes from a boolean. Its query-protein check only
  read `interactors`. Recover one exact native CPX declaration and its full original
  participant occurrences instead; protein-wide search remains separately unqualified.
- Preserve complex prediction flags, ECO codes and confidence stars literally.
  Native HsTIM-containing CPX-14819 is ML-predicted and has null stoichiometry;
  absence of a flag or a zero/unknown count never establishes experimental support
  or an absent participant. ECO is source context, not Nextia Evidence.
- Keep features, unknown ranges, linked objects and native type/role alternatives.
  Some returned references do not close over the feature array. Do not repair the
  graph, infer binding contacts, expand membership into binary interactions or
  project positions onto current source sequences. Complex species is not imposed
  on every participant, and equal identifiers do not merge entities/occurrences.
- Preserve independent full-response support and exact query identity; native
  release dates do not supply record/sequence revisions or accession versions.
  Query-bound JSON/gzip snapshots retain caller declarations and optional original-
  byte digest verification. Replay retains original acquisition time.
- Official CC0 1.0 applies to the native service data; Apache software/branding and
  linked publication/resource rights remain separate. No card intake/schema change,
  search, secondary ID following, linked acquisition or calculation job is added.

## Recover native CATH domains and query-bound supplied files (2026-10-06)

- The historical CATH prototype retained domain ID/label in a generic protein card.
  Replace that shortcut with one explicit native domain summary and a source-domain
  subject. The historical protein-wide fetch declaration is not a qualified API.
- Require an explicit fixed release route, retaining it as the request declaration.
  Native responses do not state their release, record or sequence revisions.
  Do not fabricate observed versions from the route, hierarchy or retrieval date.
- Preserve independent ATOM/COMBS sequences, null PDB locations, ordered discontinuous
  segments and literal SEQRES/PDB correspondences. Do not infer UniProt identity or
  offsets. Native GO/EC assertions/support stay context, without new function classes.
- Bound supplied JSON/gzip files reuse strict snapshot intake with exact source/kind/
  domain/release checks and optional original-byte SHA-256. Caller metadata does not
  establish original remote access. Online/fixture/archive receipts stay distinct.
- Recover direct access only: no card schema change, source search, coordinate fetch,
  sequence scan or calculation job. Official CATH resource data carry CC BY 4.0;
  attribution and parent resource/publication rights survive separately.

## Complete the recovered isoform reader with explicit native sequence access (2026-10-06)

- The preserved residue tests supplied synthetic isoform sequences. Keep the recovered
  reader and add explicit UniProt parent-declaration/FASTA access, rather than making
  canonical sequence resolution or card creation fetch all isoforms automatically.
- IDs are source-declared, independent of names: P60174 isoform name `2` is ID
  `P60174-3`; suffix `-2` is not declared in the observed parent. Query only the
  explicitly selected `Displayed`/`Described` FASTA after validating all declarations.
- Missing/partial declaration scope, explicit not-listed selection, unknown/external/
  not-described sequences, unavailable files and failures remain separate. Do not
  repair FASTA, substitute canonical sequences or follow external sequence references.
- Keep the native FASTA and parent JSON, independent times/hashes and source-declared
  association. Parent entry/canonical versions and database release do not supply an
  isoform sequence revision. VAR_SEQ pointers remain raw; no variant reconstruction,
  canonical offset, structural mapping or automatic card intake is introduced.
- Independent sequence assertions can supply the existing `residue_knowledge@1`
  reader with original support. The frozen card and current canonical annotations
  remain unchanged; this adds no persisted schema field. UniProt data keep CC BY 4.0.

## Recover full native SWISS-MODEL Repository metadata (2026-10-06)

- Replace the preserved model-only synthetic projection with an unfiltered native
  v2 response and one assertion per occurrence. PDB references and homology models
  retain chains, paired alignments, scores, ligand/complex context and download URLs.
- Validate target sequence length/MD5 and every target alignment. MD5 hashes the
  target sequence, not a model; equal hashes/templates/rows do not merge occurrences.
  CRC64 stays literal. Template numbering is not an author/label mapping.
- Native API/query/creation/release dates do not state record/model/sequence revisions.
  Scores stay literal; no ranking, probability, quality class or current UniProt
  equivalence is inferred. Coordinates/ModelCIF/templates/publications/jobs remain
  unqueried; automatic card intake and frozen schema remain unchanged.
- Record the provider's CC BY-SA 4.0 data grant with attribution/share-alike and
  separate parent-resource/article terms. Resource/method citations describe the
  service, not the primary findings of returned PDB/template entries.

## Recover native AmyPro entries and qualify specialist prototypes (2026-10-06)

- The preserved AmyPro mapper accepted synthetic regions and assigned a default
  amyloidogenic/experimental class. Recover exact native entry access instead:
  one full public JSON export, validated before selection, with independent entry
  context and region assertions on the investigated sequence. Parent UniProt/PDB
  pointers, bounds, mutation strings, categories and prion strings remain literal.
- Individual `.json` downloads currently contain Python literals. Use the valid
  official complete JSON export without evaluating scripts/literals or repairing
  payloads. Received export count is not a native total or current completeness
  claim. Missing selection is export-scoped; empty regions retain entry context.
- Keep every distinct region ID, full sequence and native support hash. Parent
  bounds can disagree with investigated sequence length; preserve the discrepancy
  without applying an offset, merging identities or querying parent sequences.
  Export/entry/sequence revisions, methods and region-specific support are unstated.
  Native publication pointers remain entry-level declarations, not acquired articles.
- AmyPro data reuse stays NOT-STATED; its resource paper's licence is separate.
  ConSurfDB and FireProtDB are explicitly deferred with concrete reuse/native-contract
  triggers after reviewing official terms and v2 documentation. No restricted native
  results or fixtures are acquired for those two providers. Their legacy synthetic
  conservation/ddG rows do not establish a qualified scientific connector.
- The original stash and 87 exported files remain intact. No card intake, schema
  change, analysis job, publication or release is added.

## Recover explicitly selected EPPIC residue detail (2026-10-06)

- The legacy reader included `interfaceResidues` but silently accumulated later
  failures into a largely valid-looking bundle. Add a standalone explicit interface
  API: read full native context, validate the requested interface, then read only
  its residue detail. Preserve independent times/hashes and successful earlier
  acquisition on a later failure; no missing detail becomes an empty table.
- Keep all per-side result occurrences, including zero buried area, quoted NaN
  fractions, unknown region codes, entropy sentinels, null labels and native serials.
  The response includes non-contact residues, so its row count never becomes contact
  membership. ASA/BSA follow the source's square-angstrom convention, retaining raw
  native values. Equal names/numbers on both sides are not merged.
- Provider code documents SEQRES/no-SEQRES numbering ambiguity. Preserve original
  serials and native interface/chain/operator context without canonical, author/
  insertion or label projection. Source sequence/calculation revisions are unknown;
  two GETs do not establish an atomic calculation revision. Other interfaces,
  sequences, coordinates and jobs stay unqueried; no card enrichment or schema change.
- Existing EPPIC data reuse remains NOT-STATED; software/paper rights are separate.
  The public native test response is declared in the fixture notice and remains
  local unreleased recovery. No new redistribution permission is inferred.

## Recover IntAct with native participant and page scope (2026-10-06)

- Replace the 15-column prototype and its assumption that the query must be B
  whenever it is not A. Require exact `uniprotkb` declarations in primary/alternative
  ID cells, preserving all 42 MITAB 2.7 columns, native interaction identifiers
  and result occurrence locators. Parse quoted delimiters only in identifier cells.
- Read one bounded first page, retaining native counts, full observed text, caller
  cap and `intact_mitab_page@1` scope. Query rows are not unique partners or complete
  biological coverage. Validate all supplied rows before selection; failed,
  unavailable and explicitly empty responses remain distinct.
- Map independent `interactions.observations.intact` SourceAssertions. Keep native
  negation, association/proximity, complex expansion, roles, methods, score literals,
  features and parameters. No `interacts_with` relationship, experimental/direct
  class, calibrated probability, parameter unit or canonical placement is guessed.
- Service versions/native dates are context, not record or sequence revisions.
  Archive replay retains original times and count/service headers. Data follows
  the official IntAct CC BY 4.0 statement; software and linked publication rights
  stay separate. Existing UniProt interaction support remains; no enricher is added.

## Recover residue-set composition with explicit selection and denominator (2026-10-06)

- The legacy helper counted repeated residue rows, mixed one-/three-letter labels
  and dropped unnamed rows from its denominator. Recover the counting requirement
  through `Card.residue_composition`, reading concrete positions on one supported
  sequence axis under `residue_set_composition@1`. Sequence characters determine
  types; caller row names do not. Repeated positions count once, while each original
  duplicate occurrence remains visible. Equal numbers on other chains/sequences
  are not identity and are not automatically projected.
- Preserve B/J/X/Z explicitly as unresolved types in the full unique-position
  denominator. U/O remain concrete symbols; infer no biochemical classes or parent
  types. Concrete fractions plus the unresolved fraction cover the denominator.
  Empty selection yields count zero and no invented undefined fraction; missing
  sequence and invalid/out-of-range selections fail instead of yielding emptiness.
- Sequence support keeps the actual source subject, source/retrieval/revision,
  complete assertion snapshot hashes and stored card pin. Noncanonical axes need
  native subject-bound sequence declarations; different content under one sequence
  reference is refused. Invalid matching declarations are reported separately;
  canonical support gaps stay explicit. Identical sequences never imply projection.
- The selected set is caller-declared. This reader does not establish cavity/site
  membership or copy the prototype's remote DoGSite orchestration. Original cavity
  declarations and exact structural mappings remain separate future inputs. No
  geometry, jobs, source acquisition/credit, card mutation, SourceAssertion creation,
  persisted schema field or cross-component exchange contract is added.

## Recover AlphaFill/LIGYSIS with native model and segment scope (2026-10-06)

- AlphaFill metadata describes an existing filled model and independent transplant
  alternatives. Keep the exact AFDB fragment, native compound/analogue labels and
  donor/alignment numbering; do not infer chemical equivalence or observed target
  binding. Keep RMSD and transplant clash score as angstrom quantities, with full
  original PAE/clash/validation context. Software/run date is not record revision.
  Validate the native payload directly because the served schema has misplaced
  properties and names that differ from current responses. No silent schema repair.
- LIGYSIS exposes public result HTML for an explicitly chosen segment. Read the six
  source JSON literals, preserve the entire page and fail on changed/ambiguous
  layouts. Do not evaluate JavaScript, invent a JSON API, fetch linked assets or
  use embedded server paths as downloadable URLs. Map the full site table, not
  the initially selected site's partial residue table. Retain clusters/scores,
  percent RSA, native membership/counts and unknown sequence/revision. No canonical
  projection, reconstructed individual ligand references or functional ranking.
- Both connectors use shared transport, original-time archive replay, source-local
  validation, ArgDigest and detached acquisition. Unknown versus null/zero remains
  explicit. Missing fixtures/HTTP failure never establish biological absence.
  Provider source terms govern data: AlphaFill acknowledgement and parent terms
  remain distinct from BSD software; LIGYSIS data reuse remains NOT-STATED despite
  free/commercial web access, MIT code and an open-access paper.
- This is standalone development source access. Automatic card intake, residue
  projections, downloads/jobs and frozen schema 0.3.12 changes are not implemented.

## Recover GlyGen modification context without guessed PTM status (2026-10-06)

- Replace the preserved parser's assumed exact canonical placement and universal
  curated class with literal native categories, original support pointers and
  explicitly source-scoped sequence coordinates. Keep glycosylation and
  phosphorylation as separate independent assertions, including alternatives.
  Peptide `site_seq` is not a residue name. Provider isoform correspondence remains
  a native comment; no local alignment or current-UniProt coordinate claim follows.
- Use the provider's public GET detail route without pagination. Require native
  accession/sequence/length and exact modification-table totals. Other raw sections
  remain unqualified. Only a positive single site within the source sequence gains
  a normalized location; ranges, missing numbering and out-of-axis values stay raw.
  Local row index/hash locators retain duplicates without claiming provider IDs.
- Keep current record/sequence revisions unknown. Introduction history and Swagger
  version are separate context. Source categories and listed publications/providers
  are not experimental confirmation, automatic curation or separately acquired credit.
- Record reviewed CC BY 4.0 database terms with original-source attribution and
  separate underlying rights. Freeze the full unmodified public HsTIM response.
  Add no automatic card enrichment, residue-view extension or frozen-schema change.
- Register iPTMnet as evaluating: both public substrate checks returned HTTP 503.
  Its preserved parser remains useful but unqualified; failure is not source absence.
  No synthetic replacement is claimed as a native response.

## Recover EPPIC/PDB-REDO without silent structure replacement (2026-10-06)

- EPPIC bundles unchanged entry/interface/assembly responses, preserving separate
  acquisition, source times/hashes and native run parameters. Validate exact entry,
  interface and cluster identities and original numeric domains. Preserve native
  method calls, score sentinels, alternative and unit-cell assemblies. IDs/chains/
  operators stay source-scoped; no residue or current-UniProt projection is inferred.
- Map interface area as a PyUnitWizard quantity in square angstroms, as the official
  EPPIC interface table states. Keep raw source objects/coordinates in metadata;
  calculate no geometry and select no assembly. EPPIC software versions, releaseDate
  and the UniProt run release do not establish a prediction-record revision.
- PDB-REDO reads existing data.json and separately requested versions.json, keeping
  original files intact. Map deposited, baseline, restrained and final R-factors
  independently; preserve null/zero/missing values and native input/software context.
  Pipeline version/date is not a databank revision. Do not fabricate coordinate URLs,
  replace models, calculate an improvement or submit a re-refinement job.
- Keep success/empty/unavailable/failed access distinct. A later EPPIC component
  failure retains earlier access receipts and cannot produce a complete bundle.
  PDB-REDO's observed 1HTI HTTP 500 establishes only a failed request.
- Preserve EPPIC data reuse as NOT-STATED; neither GPL software nor Apache API
  documentation grants a prediction-data licence. Classify PDB-REDO's explicit
  original-file reuse policy as FREE-WITH-ACKNOWLEDGEMENT with original/parent
  attribution conditions. Fix the unpublished NOT-STATED retention branch to keep
  redistribution unknown instead of granting it; established licences are unchanged.
- Make the existing showcase storage/curation tests prepare their own detached
  cards. The full 12-worker run exposed their dependence on another test executing
  first; original/curated snapshot integrity must be meaningful in isolated runs.
- Add no automatic card enrichment, persisted field or frozen-schema change. Retain
  the stash and 87 byte-identical original exports. Other specialist sources remain
  separately scoped candidates; no remote publication is part of this recovery.

## Recover PDBe validation as literal structure-scoped metrics (2026-10-06)

- Recover explicit entry-wide percentile access from the preserved prototype,
  using the current documented PDBe route and one PDB ID per call. Validate exact
  native entry identity, finite raw values and 0–100 percentile domains. Preserve
  unknown metrics, additional native context and optional relative percentiles.
- Keep raw values distinct from archive-wide and comparable-entry ranks. Do not
  fabricate missing metrics, experimental methods, metric units, quality classes,
  thresholds, comparison population counts or pipeline/statistical revisions.
  The API service version is not the unstated scientific-data revision.
- Emit one independent SourceAssertion per metric with the PDB structure subject.
  Do not apply the old `experimental_quality_assessment`/`database_inference`
  classes, enrich cards, project residue positions or alter frozen schema 0.3.12.
- Observe online and supplied-file acquisition and original-time HTTP archive
  replay. An explicit empty metric collection differs from missing fixtures and
  failed requests; a 404 alone does not prove validation absence.
- Review EMBL-EBI terms and wwPDB archive CC0 scope independently. A separate
  PDBe validation API-response licence remains `NOT-STATED`; PDBe-KB terms are
  not transferred. Preserve native public fixture bytes, hashes and retrieval gaps.
  Retain the original stash and exports; EPPIC/PDB-REDO remain separate candidates.

## Recover MobiDB, SIFTS and source metadata on current contracts (2026-10-06)

- Use the documented MobiDB v1 single-protein export instead of restoring the
  legacy document endpoint. Validate the complete native identity/sequence/release,
  intervals and count/continuation headers. Preserve all annotation sets, series,
  semantic/unit declarations, native normalized/stored coverage and reported issues.
- Preserve curated, homology, derived and prediction bases as the provider states
  them. Do not interpret native `evidence` as MOLI Evidence. Map disorder and PTM
  intervals independently, retaining original labels, providers and provenance;
  unknown PTM experimental basis remains unknown. Exclude sets with reported
  normalization losses under `mobidb_valid_region_sets@1`, retaining them raw.
- Extend the unpublished `residue_knowledge@1` reader to native MobiDB disorder
  features on its explicitly selected source axis, with exact subject and complete
  sequence/hash support. Do not fabricate an IDPO term or place same-sequence
  observations on the canonical card axis automatically.
- Recover SIFTS as one explicit PDB mapping query, keeping every native protein
  or isoform reference, entity, author chain, label asym ID and endpoint/insertion
  number. Independent assertions have the structure subject. Source endpoints do
  not justify calculated residue offsets or entity/sequence equivalence. Release
  and referenced sequence revisions stay unknown. Review EMBL-EBI terms without
  assigning an unverified SIFTS-wide or PDBe-KB licence.
- Preserve MobiDB's required continuation/count headers in the existing shared
  HTTP archive. Replay still uses original source times and never new network
  requests. Add no competing transport or runtime dependency.
- Generate the public metadata catalog and category profiles from the current
  registry under `registry_catalog@1`, with all statuses/access/terms/limitations
  and code-derived limits. Package JSON for offline reading. Adoption status is
  not health, readiness, complete coverage or a query activation policy; old
  hard-coded `verified`/`production_ready` profiles are not restored.
- Add no automatic card enrichment, new persisted field or frozen-schema change.
  Retain the complete stash and all original exports; other specialist integrations
  and consumer projections remain qualified separately.

## Recover direct AlphaMissense substitutions with explicit prediction scope (2026-10-06)

- Select one exact full canonical human AlphaFold DB descriptor and its declared
  native amino-acid substitution artifact. Keep the full discovery response,
  including unqueried isoforms. Refuse ambiguous/fragmented descriptors, unrelated
  proteins, unsupported sequence scope and changed host/artifact identity.
- Validate every CSV row before a positive output cap: headers/width, unique
  substitutions, positions, reference amino acids, alternatives and finite scores
  in [0, 1]. Retain native numeric literals, missing values and provider classes;
  unknown classes remain explicit. Do not reconstruct or threshold classes.
  Keep code recognition under `native_alphamissense_class_vocabulary@1` in
  validation metadata, separate from the provider's asserted classification.
- Map independent source assertions with `knowledge_class=predicted` and an
  explicit AlphaMissense source sequence/hash. Host discovery sequence binding
  does not establish current UniProt or isoform coordinate equivalence.
  The host model version/date is not the unstated prediction-artifact revision.
- Preserve native CSV bytes/hash, parsed row count, output cap and named
  `single_aa_substitution_coverage@1` grid coverage separately. Missing grid rows
  do not establish biological absence. Missing declarations do not query/credit
  the score resource; failed declared downloads remain failures.
- Keep host discovery and prediction artifact acquisition separate, with shared
  HTTP archive replay and original times. Consumer-specific discovery validation
  preserves the existing AlphaFold public failure contract. Register reviewed
  CC BY 4.0 prediction terms and a native public fixture, with requested bibliography.
- Add no automatic card enrichment, persisted fields, isoform/genomic artifact
  reconstruction, clinical assertion or new model inference. Frozen schema 0.3.12
  and the complete original stash remain unchanged.

## Recover explicit sequence candidates without changing entity resolution (2026-10-06)

- Add `exact_sequence_candidates@1` as a standalone raw/FASTA candidate tool.
  Reject invalid/multiple records before access. Normalize whitespace/case and
  an optional final stop, retaining input hashes and the literal header.
- Search UniParc with native MD5, then compare full archive and current UniProt
  canonical sequences. Keep every matching entry separate. Equal sequences,
  shared archive records and historical references do not establish entity identity.
  Require exact queried primary accessions; redirected/alias responses are explicit
  validation failures. Optional taxonomy filtering is exact, without descendants.
- Preserve native `.N` revisions as associations, without fetching historical
  sequence versions. Explicitly exclude `-N` isoform references as unqueried.
  Cap archive rows and canonical checks separately; keep native reference order,
  unfinished scope and per-entry failures. Retain accepted rows/candidates if a
  later page fails. A single candidate in a partial report is not unique identity.
- Use shared online/fixture acquisition and archive replay, with native totals,
  same-source/query continuation guards, consistent releases and page receipts.
  Map archive declarations separately from current sequence support, retaining
  full assertion snapshot hashes, original native metadata and retrieval gaps.
- Register UniParc under official CC BY 4.0 database terms and declare the public
  native fixture. Other database/publication rights remain separate. Add no card
  enrichment, automatic resolver heuristic, identity merge or frozen-schema change.

## Recover richer residue reading as a detached view (2026-10-06)

- Add `Card.residue_knowledge`, named rule `residue_knowledge@1`, separately from
  the existing `residue_annotations@1` readers. Keep their previous results intact.
- Read amino-acid-type properties/statistics independently from position tracks
  and DisProt region assertions. Retain providers, metrics, state definitions,
  sample context, units and exact original SourceAssertions. A reference frequency
  does not become a positional probability; native AAindex `NA` is not zero.
- Require explicit full source sequence/id/subject and optional matching hash for
  positional inputs. Canonical placement requires exactly matching identity and
  content. Explicitly selected source/isoform sequences remain on their own axes;
  equality to the canonical string does not establish identity or placement.
- Pin complete input assertion records, including metadata/revisions, so different
  revisions sharing an assertion id remain distinct. Missing samples and incompatible
  scope remain separate from zero/received data. Invalid dense/sparse positions and
  conflicting declarations are refused or reported unplaced.
- Add no new card field/schema, source access, attribution, prediction, alignment
  or isoform reconstruction. Supplied original assertions remain separate from
  card persistence and runtime acquisition sidecars.

## Recover supplied snapshot intake and bounded DisProt access (2026-10-06)

- Add explicit JSON/JSONL/NDJSON/CSV/TSV/gzip reading with original byte hashes,
  optional SHA-256 verification and detached caller declarations. Local read time
  never substitutes for original source retrieval. The generic loader provides
  neither acquisition credit nor card intake; native clients validate its payload.
- Add direct DisProt accession search with online, fixture and bound supplied-file
  clients. Retain native search/region counts, acquisition/replay identity and
  incomplete default-region scope. Failed API routes never establish source absence.
- Map only the explicit native disorder structural-state term, with coordinates
  on the identified DisProt sequence. Shared UniProt accessions do not establish
  coordinate equivalence; no current-sequence or isoform placement is inferred.
  Retain native region revisions and publication pointers, unknown global release
  and missing underlying bibliography. These remain database SourceAssertions.
- Keep the retrieved public fixture's native coordinates and all returned regions;
  trim publication quotations/HTML and unrelated fields, document hashes and CC BY
  4.0 database terms. Linked article rights remain separate. No automatic protein
  enrichment or frozen card-schema change is made.

## Recover useful pre-pull local work without reverting current contracts (2026-10-06)

- Preserve the complete original stash and export original bytes locally. Inventory
  all 91 paths; keep the 87 useful historical files under ignored `recovered_work/`.
  Archive the source catalog and requirements with current-registry dispositions.
- Reimplement notebook reports, canonical residue readers (`residue_annotations@1`)
  and explicit AAindex1 source access on current cards, SourceAssertions, argument
  contracts and shared acquisition transport. Do not change frozen schema 0.3.12.
- Reports and residue views are offline derived readers. They preserve pinned
  input/support, units and gaps without new credit, identity resolution or isoform
  reconstruction. Disulfide annotations apply only to their endpoints.
- AAindex native values are reference assertions about amino-acid types. Preserve
  literal numbers/NA, bibliographic pointers and unknown units/version/terms; do
  not reuse the prototype's guessed units or infer positional protein properties.
- Legacy evidence stores, unbound ligand cards and the mislabeled PTGS2 file stay
  historical until scientific identity/support and migration can be established.
  Newer current implementations supersede old resolution, caching and governance.
- Use the shared Python 3.14 development environment for all recovery validation,
  as the maintainer requests. No separate installed-artifact qualification is
  part of this local recovery. See `archive/local_work_2026-07/README.md`.

## Preserve references declared by ChEMBL indications (2026-10-06, #108)

- Project native `indication_refs` as incomplete pointer citations, with the role
  `source_cited_reference`. A trial registry, regulatory label or classification
  pointer is not automatically a scientific article or an observed target access.
- `chembl_indication_references@1` retains each native form and every occurrence,
  bound to its indication/molecule/disease row, received page/query/hash or original
  fixture result. Preserve grouped identifiers and overlapping EFO/MeSH query
  occurrences even when the scientific client deduplicates the returned row.
- Credit only received pointers, including completed pages before later failure.
  Keep target access, missing metadata and malformed/absent forms explicit. Do
  not follow links, invent authors/titles/years, infer permissions or overwrite
  fuller host citations. Original references survive archive reuse and inert
  portable Ackredit exports in the enclosing workflow.
- Keep scientific client returns, SourceAssertions and frozen card schema fixed.
  Example `@5` keeps its format: study metadata remains undeclared and cited
  studies remain unfetched. Full underlying study bibliography is still #108 work.
- Call the possible finer #29 operation **filtering by terms of use**, rather
  than source pruning. It would produce a derived view/deck with explicit support
  changes; it must preserve original provenance, citations and the original deck.


## Observe disease channel and identity/variant lookups (2026-10-06, #108/#125)

- Observe built-in DISEASES channel access, ClinVar `variants` and MedGen `concepts`
  in enrichments and public source envelopes. Retain native query/page/file hashes,
  version bases, original access, counts/caps/order and completed intake on failure.
  Do not claim direct access to publications from nearby source statements.
- Keep each DISEASES original receipt on its existing memory index. Header checks
  do not redate the scientific index. Preserve disk JSON format; older cached
  origins/times remain unknown, with the legacy client-clock fallback explicit.
  Channel scores and native resource/text-mining pointers stay separate.
- Treat missing native E-utilities fields, omitted summary UIDs and malformed
  classification shapes as connector failures. Missing fixtures are unavailable;
  ClinVar fixture database versions cannot merge silently. Distinguish ClinVar
  database build and accession revisions from MedGen database `lastupdate`.
  Counts/limits are per gene or concept batch, not unique workflow entities.
- Refuse MedGen identity when native records name multiple UIDs for one concept
  or its search is capped. Preserve those native pairs and received scope in the
  failed trace; never choose by response order or infer absence from a cut.
- Keep transport credentials out of recorded request/retry/archive identities.
  Send the actual key only on the service request, retain native response bytes
  and permit credential rotation for the same archived scientific query.
- Compile verified DISEASES/ClinVar descriptions and the recommended MedGen resource
  citation. Underlying studies, submissions and terminology citations remain
  explicit gaps. Example `@5` retains original `@1`–`@4` reports and their gaps;
  no reconstruction, new reader credit or scientific schema change is introduced.
  Support-aware admission (#29), non-protein packets (#71), public delivery and
  shared consumer guarantees remain pending.

## Observe association intake and disease-deck builds (2026-10-05, #108/#124)

- Observe built-in Open Targets `associations`/`targets` and Orphadata
  `associations`/`genes`, including public envelopes and ordinary enrichments.
  Preserve queries, page/file/lookup identities, versions, source order/counts,
  original retrieval and actual attempts. Scores remain native statements, not efficacy.
- Keep Open Targets page versions/counts separate; refuse scientific merges across
  changed versions/counts and retain completed page intake with its terminal failure.
  Explicit null entities are evaluated absence; missing fields and malformed
  JSON/native fields are connector failures. Missing files are unavailable (#124).
- Keep Orphadata's receipt on the exact existing cached index. Preserve original
  scientific/runtime times across memory/archive reuse (#124); old bare indexes
  cannot recover origins. Reject malformed/unrelated XML in client loading,
  preserving the public parser. Absence covers indexed SwissProt associations;
  fixture subsets and native validation pointers retain their limited scope.
- Disease builders expose detached intake traces with original input/support pins,
  final deck/member pins, executing package/times, rule/limit, source outcomes and
  exclusions. Stored inputs and custom clients do not establish source access.
  Scientific rules, card schema and default storage stay unchanged.
- Compile the complete Open Targets article and Orphadata's recommended dataset
  citation from primary metadata; underlying study metadata remains a gap. Advance
  the example to `@4`, preserving genuine `@1`/`@2`/`@3` reports without acquisition
  or new credit. Other disease families, admission (#29), packets (#71) and shared
  consumer contracts remain open. Delivery and remote qualification are pending.

## Observe MONDO index queries and preserve release integrity (2026-10-05, #108/#123)

- Observe built-in term/equivalence access through the existing runtime formats and
  host Ackredit capture. Keep raw/normalized identifiers, native identity/reference
  forms, OBO header version, exact file/lookup identities and source-scoped bibliography.
  MONDO declarations do not establish access to imported terminologies or publications.
- Carry the original download receipt with the exact process-cached index. Memory
  lookup and release-selector requests have separate scopes and current attempt counts.
  Preserve original file response times in scientific results as well as runtime
  records across memory/archive reuse. A pre-existing index without a receipt states
  unknown origins and retains an explicitly identified legacy source-time fallback.
- Correct the source-client integrity defects in #123: reject obvious non-OBO and
  invalid UTF-8 documents as connector failures before caching; distinguish missing
  fixture files from absent terms. Keep native partial term-stanza fixtures supported.
  The public parser utility remains unchanged; this is no complete OBO validation.
- Keep fixture subsets, empty equivalence queries, unavailable, unqueried and failed
  outcomes distinct. Failed access adds no completed-source credit. Valid mappings,
  identity rules, card field shape/schema, stored snapshots and default persistence
  remain fixed. Direct disease resolution retains exact result/resolution traces.
- Version the local disease example as `@3` for MONDO observation; accept original
  `@1`/`@2` bundles without recreating missing science or credit. Required Open Targets,
  Orphanet, other disease sources and deck-operation observation remain #108 work.
  Delivery is local; no new release or shared recording contract is claimed.

## Admit disease decks conservatively with complete retained support (2026-10-06, #29)

- `disease_deck_admission@1` requires complete exact membership/input bindings and
  admissible whole embedded support. Unknown/restricted shared context refuses the
  operation with a detached item-level report, rather than returning a deck with
  absent support. Source pruning remains pending; no historical registry is inferred.
- The #126 integrity fix checks that each built candidate is actually stated by
  the current member's bound identifier assertions and resolved identifier fields.
  Another candidate's valid native basis is partial, never admissible identity.
  This tightens the unpublished explanation rule without changing historical
  stored reports, source-stated equivalence or the card schema.
- Judge resolved items and every retained raw SourceAssertion separately, including
  unused statements. An allowed alternative does not license a retained raw copy.
  Known depositor terms for a projected relationship do not establish permission
  for the complete raw source record; undeclared per-record rights stay unknown.
- Filter whole member cards only. Preserve native candidate/input bases and exact
  retained member pins. Move removed member identity references into explicitly
  historical exclusion metadata; never present missing identity as active support.
- Record original deck/member/support pins, current registry declarations, reasons,
  obligations and versioned operation in a separate derived deck. JSONL/SQLite and
  pinned knowledge-store reads preserve them without source access or runtime credit.
  Original acquisition/attribution sidecars remain bound to the original deck.
- Delivery remains local and #29 remains open for finer admission, per-record raw
  rights, historical registries and packet scopes. The disease journey keeps its
  existing `@5` receipt format; separate SDK tests exercise this bounded operation.

## Pin disease membership to native rows and original identity (2026-10-05, #91/#112)

- Version builders as `disease_targets@2` and `disease_drugs@2`. Keep source-native
  rows as SourceAssertions; membership, ranking and identity projection remain
  named derivations. Retain Open Targets' full returned record/order/count as well
  as individual rows, Orphanet's native rows and ChEMBL's complete indications.
- Keep the supplied MONDO card unchanged. A separate revision carries additional
  native assertions. `meta.support` under `sabueso.disease_deck_support@1` embeds
  both snapshots/pins for portable JSONL/SQLite decks; it adds no card field,
  predicate, schema or knowledge-store table. Source rows remain scoped context,
  without constructing new selected disease fields or project Evidence.
- Bind kept, capped, unbuilt and unsupported-product candidates to exact native
  assertion items and original MONDO identity. Kept members also bind their actual
  card state and molecular/protein identity support. `disease_deck_explanation@1`
  checks missing/misbound identity, native rows, scores and source row order without
  acquisition or new credit. Old metadata-only decks explicitly lack that support.
- Saving a deck alone stores its input, assertion-bearing revision and members
  atomically. The disease head can advance to the support revision; the original
  input pin remains readable. Export/import preserves the embedded support.
- `disease_deck_terms@1` reports member and all embedded native-source terms.
  Member-only admission cannot prune this support correctly. The initial refusal
  is superseded by conservative `disease_deck_admission@1` above; source pruning
  remains #29. Reports do not grant rights.
  The bounded admission need is recorded in
  [#29](https://github.com/uibcdf/sabueso/issues/29#issuecomment-6003107144).
- Version the local disease example as `@2`; its reader still accepts original
  `@1` bundles and preserves their reports/gaps. Required disease-source observation
  and full bibliography remain #108; non-protein packets remain #71. Delivery is local.

## Keep disease journey support and observation gaps explicit (2026-10-05, #112/#91/#108)

- Exercise existing disease resolution/deck/grouping routes in a public independent
  producer/reader/reacquisition example before extending the SDK. Use separate
  MONDO-anchored target and drug questions; infer neither cross-disease links nor
  efficacy, approval or identity from names/phase metadata.
- Preserve exact card/group statement pins and original named explanations. Keep
  original disease-deck membership metadata with its missing assertion/input pins
  explicit; never manufacture statement support or an observed execution from it.
- Export original runtime attribution for observed operations only. Unobserved
  disease sources and missing indication bibliography remain declared gaps.
- Scope the next implementation to exact disease-deck membership/input support
  (#91), then disease source/deck-operation observation (#108). Disease packets
  remain #71 work; the example does not define a shared MOLI recording format.

## Correct molecular source counts without inventing absence (2026-10-05, #122)

- Version the corrected classification as `knowledge_state@5`. A successful report
  with no usable count is `known` with `count=None`; a mixed/incomplete response
  remains `partial`. Keep the known subtotal and exact unknown-count report indexes.
  Never turn a missing/unusable count or unrecognized outcome into evaluated empty.
- For molecular record intake, ChEMBL/CCD/PubChem native returned record-id lists
  can supply a count. A UniChem native compound id counts one returned compound;
  its linked databases are not direct acquisitions and are not additional records
  from those databases. Explicit area counts take precedence. Do not reconstruct
  request membership/counts from nearby SourceAssertions.
- Keep missing batch ids, failed/incomplete/capped requests and original report
  versions visible. A declared partial/capped empty subset is still partial.
  Native `not_found` reports retain their missing ids and query scope; they do not
  establish external absence when the fixture/archive is unavailable.
- Separate small-molecule ChEMBL indication reports into
  `relationships.investigated_for` and ClinicalTrials.gov reports into
  `relationships.tested_in`; molecular record intake stays in `records`.
  Requested study counts are not returned study counts. This classifies existing
  reports; it does not reconstruct unrecorded operations or query new sources.
- Version the explanation as `knowledge_state_explanation@2`, with each counting
  basis, field, relative report index and original `quality.enrichments` index.
  Exact pinned SourceAssertions remain separate scientific context with
  per-request membership explicitly `not_recorded`.
- Card intake/schema/source assertions stay unchanged. New classifications and
  packets use the new rules; frozen packets and original producer reports retain
  their original rules, pins and attribution. Payload-only readers fetch nothing
  and add no credit. This is local development, not a published replacement yet.

## Adopt the next roadmap after 0.13.0 (2026-10-05, #112)

- The maintainer approved the review of the original architecture, MOLI Knowledge
  role and independent-user promise as the basis for the next roadmap.
- First define and demonstrate three standalone SDK journeys: protein/comparator,
  molecule/activities and disease/related entities. Use their gaps to schedule
  bounded query, explanation, required traceability, history and scale work.
  User documentation and independently readable saved support are acceptance
  requirements, alongside scientific examples and appropriate regressions.
- Prioritize peptide identity and a bounded use as the next scientific expansion,
  before selecting sources or suppliers. Keep clinical, isoform and literature
  objectives visible; local-mirror work #101 remains postponed.
- Coordinate Nextia/Context Assembly, ProjectRecord/Recorda and modeling exchanges
  in parallel with their owners. Standalone Sabueso development does not wait for
  consumer readiness. Shared contracts remain with MOLI; modeling remains with
  MolSysSuite. Both foundational and pilot-driven routes continue.
- Record pending decisions on query scope, entity representations, reproducibility/
  export, literature validation and public contract stability in `ROADMAP.md` and
  `RISKS_AND_OPEN_QUESTIONS.md`. This adopts development priorities, not new API
  semantics, shared contracts or a release schedule.

## Observe chemical identity acquisition and ligand-deck intake (2026-10-04, #108)

- Observe CCD component batches and UniChem InChIKey/source-id lookups through the
  existing required acquisition adapter. Keep normalized logical queries, native
  POST/wire/decoded response identities, original archive times/references, retries
  and completed subsets. A CCD iterable is materialized once before observation.
- Distinguish evaluated empty answers, unavailable fixtures, unqueried offline
  access and original failures. Mixed CCD batches retain per-component outcomes;
  received data before a processing/read failure remains partial, never a complete
  acquisition. Missing fixtures never establish external source absence.
- Keep source versions explicitly unstated. CCD release status/dates and UniChem
  UCI values do not become release versions. Preserve UniChem's native linked
  source forms and existing first-returned-compound selection basis without
  claiming those providers were queried, inferring identity or changing mappings.
- Credit verified CCD/RCSB distribution and UniChem resource descriptions. These
  describe the resources, never experimental findings or linked-provider access.
- Capture `resolve_molecule_card` intake at exact card/resolution pins and expose
  detached `Deck.acquisition_trace` for `ligand_deck`, with native deck snapshot,
  result card pins and input protein pin. Original JSON sidecars remain host-owned;
  loading payloads or deriving a deck creates no trace or credit. Other deck
  operations/results, other sources and custom clients remain explicitly uncovered.
- Scientific schema, hashes, serialized cards/decks, source returns/exceptions,
  identity/class rules, published fixtures and release receipts remain unchanged.
  MOLI still owns ProjectRecord/Recorda persistence and correlation contracts.

## Count ligand measurements separately from source records (2026-10-04, #118)

- Default to `ligand_measurement_count@2`: count distinct included group ids across
  every matched measured-molecule item, including source/parent forms. Summing
  each item's group count could still count a cross-item group more than once.
  Add `bioactivity.records` for distinct included source relationship ids.
- Expose keyword-only `counting_rule` through `ligands`, `compare_ligands` and
  `explain_ligand`, preserving positional compatibility and validating through
  ArgDigest. Explicit `ligand_measurement_count@1` reproduces the published numeric
  source-record counter; both rules add record counts and pinned counting metadata.
  This is a versioned read-time integrity correction, not a stored-schema migration.
- Advance the unreleased crossing explanation to `ligand_deck_explanation@2`:
  preserve exact counted group/record ids, selected counting basis and original
  pinned source support. Historical card/deck reads apply the explicitly selected
  policy without acquisition, new credit or rewriting saved knowledge.
- Retain `measurement_identity@1`, `bioactivity_class@3`, assay filters, ambiguity,
  discordance, class voters, copy-only fallback, unmatched records and site rules.
  Groups never imply independent experimental confirmation. Published 0.12.0
  artifacts, schemas, fixtures and release receipts remain immutable.

## Explain stored ligand crossings and site classes at distinct card pins (2026-10-04, #91/#118)

- Add `Card.explain_ligand_site(ligand_site_ref)` under
  `ligand_site_explanation@1` and `Card.explain_ligand(molecule_ref, deck, ...)`
  under `ligand_deck_explanation@1`. Exact native site ids and SmallMoleculeCard
  ids/options are digested. No alias resolution or source acquisition occurs.
- Retain actual `annotated_site_overlap@2` outputs with complete selected field
  support, alternatives/conflicts, numbering and structure-instance context.
  No stored annotation/overlap is not source absence; aggregate contacts never
  imply instance-level chain spanning. Relevance statements retain source roles.
- Collect actual deck-crossing identity/class/name choices; protein and molecule
  inputs retain distinct relationship/assertion pins and original source versions.
  Nested measurement/site explanations keep their own rules and quantity policies.
  Duplicate deck members remain multiple partial items instead of selecting a pin.
- Record native deck snapshot/membership/metadata context without inventing a
  KnowledgeStore reference. Load the original saved deck separately for historical
  reads. Readers fetch nothing, mutate no card/deck/attribution and add no credit.
- Report the reproduced source-record counter labelled measurements in #118.
  Preserve the existing public view here and state its actual counting basis;
  nested bioactivity support retains group/record counts. Its correction is separate
  work. Scientific class policies, stored schema and published artifacts are unchanged.

## Retain unresolved activity-only copy pointers without changing grouping (2026-10-04, #117)

- The provenance branch previously skipped an absent activity-only original when
  no assay pointer was present. Record the existing `original_not_on_card`
  diagnostic with the exact `copy_of` pointer before that early exit.
- Keep the final singleton filter: later provenance/statement resolution removes
  the diagnostic. Successful exact pointers, assay recovery, candidate selection,
  grouping edges, class voters and copy-only fallback are unchanged.
- This completes an existing diagnostic contract, so retain `measurement_identity@1`
  and `bioactivity_class@3`. No scientific grouping or classification policy changes;
  stored card schema and published artifacts remain immutable.
- An unresolved pointer describes the local stored card, never negative source
  knowledge. A statement join does not prove that the named original was acquired.
  Exact pointers/source support survive current and historical explanations without
  new acquisition, assertions, card mutation or execution credit.

## Explain actual measurement joins and bioactivity voters at card pins (2026-10-04, #91)

- Add `Card.explain_measurement(measurement_ref)` and
  `Card.explain_bioactivity(molecule_ref, include_indirect=False, thresholds=None)`
  under `measurement_group_explanation@1` and `bioactivity_explanation@1`.
  ArgDigest checks exact native selectors and existing quantity-bearing options.
- Collect the actual decisions of `measurement_identity@1` and
  `bioactivity_class@3`; preserve their ordinary outputs. Joins retain publication,
  molecule keys, declared-copy selector and precision quantities. Connectivity
  inside a named copied assay is measurement provenance, never molecular identity.
- Retain each included group's voters and classes, non-copy preference and explicit
  copy-only fallback. Strongest-class selection never hides discordance. Original
  units, ranges, single-point concentrations, thresholds and consistency flags survive.
- Link every stored input relationship/assertion to the current or loaded historical
  card pin and original source versions. Candidate uniqueness and glossary mapping
  need whole-card context, which remains separate from selected records. Stored
  identity records have locators into serialized `entities`; do not invent their
  SourceAssertion membership or minimal identity paths. Missing support is partial;
  an unknown item is not inactivity or evidence of absence.
- These readers fetch nothing, mutate no cards or attribution and create no
  SourceAssertions. Stored schema, frozen fixtures and published release receipts
  stay unchanged. Ligand deck/site aggregation and other derived explanations remain
  #91 work; these APIs explain the protein's measured molecule items only.
- Report the reproduced existing diagnostic omission as #117: an absent
  activity-only copy pointer exits before `unresolved_copies` is populated.
  Preserve the raw pointer and current rule output here; do not claim an empty
  diagnostic list proves all pointers resolved. Its correction is separate work.

## Explain pinned knowledge-state inputs without inventing absence support (2026-10-04, #91/#116)

- Add `Card.explain_knowledge_state(knowledge_area=None, knowledge_source=None)`
  under `knowledge_state_explanation@1`. Collect support descriptors in the actual
  `knowledge_state@4` branches; do not duplicate or change their classification.
  Select exact area/source names, or all rows, through ArgDigest.
- Explain selected fields with their source-specific assertions, complete selected
  support, alternatives, selection rules and conflicts. Counted UniProt predicates
  retain exact relationships and support. Missing support is partial even when its
  loss removes the classified row or makes a predicate appear not stated.
- UniProt absent-field inference and unqueried curation retain their stored anchor,
  source coverage and route. They are classification decisions, never negative
  SourceAssertions or project Evidence. Do not claim reconstructed source history.
- Enrichment states retain exactly matched reports, original versions, count-field
  selection/fallback and coverage outcomes. A locator identifies the stored report
  by card pin, field path and index; it is not an invented KnowledgeStore item id.
  Related scientific support is separate source/area context: per-request assertion
  membership is not recorded and counts are not rebuilt from nearby assertions.
- The reproducible #116 defect unpacked several supporting UniProt versions into
  one value. Join all stated versions deterministically, retaining original unknown
  values in support. This removes a crash, preserves working outputs and keeps the
  existing `knowledge_state@4`; no source version is selected by order or recency.
- These read-time views change no scientific serialization, card pin, acquisition
  or execution credit. Published cards/artifacts/receipts remain immutable. Other
  derived-view explanations stay #91 work.

## Versioned deterministic disease grouping with explicit historical compatibility (2026-10-04, #115/#91)

- Adopt `disease_grouping@2` and `disease_group_explanation@2` as the unreleased
  defaults. Enumerate every stored direct or MedGen/MONDO identity path, retaining
  exact relationship ids and original SourceAssertions. This is a bounded source
  contract traversal, not a general identity closure or similarity-based merge.
- Contradictory targets of one identifier remain `conflicting_identity`, even if
  they share a MONDO hierarchy. Granularity applies across separately stated ids
  with unique targets, only when one stated term is broader than all others.
  Converging paths retain all support; unfinished stored branches alongside a
  reached term remain `incomplete_identity`. Unknown equivalence is never agreement.
- Names, source versions and storage order never select identity. Retain all stored
  MONDO labels, selecting `mondo_name` only for a unique label. Preserve alternative
  hierarchy paths and source qualifier conflicts; never select the latest version.
- Explicit `grouping_rule="disease_grouping@1"` reproduces the historical lookup
  and `disease_group_explanation@1`, including selected/alternative links and its
  partial ambiguity diagnostic. The rule selector is digested; unknown versions
  are refused. Existing positional explanation arguments remain compatible.
- A stored card pin identifies source knowledge, not an implicit grouping rule.
  Explain a loaded pin with an explicit rule to reproduce historical behavior;
  default `@2` is a newly named view of that same knowledge. Neither changes the
  pin, serialized schema, acquisition or credit. Published cards/artifacts remain
  immutable. Other derived-view explanations remain #91 work.

## Source-defined empty BindingDB responses and pinned disease explanations (2026-10-04, #114/#91)

- Accept an exactly empty HTTP 200 body or JSON empty string as BindingDB's
  documented no-match answer, using the same RecordNotFoundError contract as an
  empty native affinities array. Keep whitespace/malformed JSON, unexpected
  nonempty payloads and HTTP errors failed. Only BindingDB opts into empty-body
  acceptance in the shared JSON transport; default behavior remains unchanged.
- The [official REST contract](https://www.bindingdb.org/rwd/bind/BindingDBRESTfulAPI.jsp)
  declares an empty string. A public synthetic no-match identifier probe on
  2026-10-04 returned HTTP 200, text/json, and the native empty affinities array
  (65 bytes, SHA-256 `09bc0dde35898b010ae89187a1db4d6823b1268b81306ca5cb346dc97201d7bb`).
  String compatibility is documentation-backed synthetic regression evidence,
  not a verified live outage. Preserve original wire/archive identities and times.
- Add `Card.explain_disease(disease_ref)` under `disease_group_explanation@1`,
  selecting only a MONDO group at the current or loaded historical card pin.
  Read existing grouping output; retain selected association/annotation-member
  support, source-native identity links, hierarchy steps and their named rules.
  No acquisition, mapping rerun, card mutation or new attribution credit occurs.
- Preserve stored qualifier/selection alternatives and all ungrouped outcomes as
  explicitly whole-card context. Missing support is partial; never infer absence
  or reconstruct lineage that the card does not record.
- The existing `_same_as` lookup discards other same-source targets. Reported as
  #115, with a synthetic reproduction and versioned grouping acceptance. The
  explanation exposes both targets and lookup selection as partial; it does not
  silently change `disease_grouping@1`. Other derived views remain #91 work.
- The parser defect affects published clients; the next qualified release should
  include this integrity fix. This development checkpoint publishes no new artifact
  and does not overwrite the verified 0.12.0 release or frozen schema.

## Observe BindingDB affinity queries and installed mirrors (2026-10-04, #108/#112)

- Instrument existing REST, fixture and mirror query methods, preserving raw
  results, exceptions, scientific mappings and schema. Honor an adapter's declared
  local access route when there are no transport requests.
- Retain cutoff/limit/order, total/kept counts, received response identities,
  archive/retry metadata and native DOI/PubMed forms. Incomplete citations use
  metadata-based identities to preserve fuller host references and alternatives.
- Record mirror release/manifest/installation time as their stated basis, without
  claiming live REST release proof or independent index integrity. Installation,
  update and constructor failures stay outside query observation. Fixture cutoffs
  are not reapplied; record this existing behavior explicitly.
- Mirror data origins are declarations; imported sources are not credited as
  directly consulted. REST origins/global release and absent bibliography stay
  unknown. The verified resource-description paper has a separate role.
- Distinguish decoded-empty responses, missing fixtures, offline-unqueried access,
  original connector/index failures and received data before processing failure.
  The existing documented empty-string parsing incompatibility is reported in #114,
  with failure receipts and no completed-access credit; this slice does not hide it.
- Exercise original traces, saved readers, refresh, provider failures and citation
  conflicts against the public Ackredit floor. Other sources/custom clients,
  result breadth and MOLI record/consumer coordination remain #108 work.

## Observe PubChem compound, structure and BioAssay access (2026-10-04, #108/#112)

- Extend the existing detached source-operation adapter to the three built-in
  online/fixture routes, preserving scientific results, exceptions and schemas.
  Trace native summary revisions per assay, including zero; never infer a global
  database release or row/property version from these revisions.
- Preserve POST input identities, CSV/summary/property response identities, caps,
  row-order rules, retries, local/archive routes and original retrieval times.
  A later failing batch retains received source subsets and the terminal outcome;
  partial counts explicitly describe received rows before completion.
- Separate PubChem's verified resource description from PubMed measurement pointers
  and source-stated depositors. Missing publication metadata and depositor
  bibliography remain gaps. A named depositor is not a directly consulted resource.
  Incomplete pointers use content-based citation identities, preserving fuller host
  citations under original PubMed ids without provider metadata conflicts.
- Distinguish evaluated-empty answers, HTTP absence, rejected input, unavailable
  fixtures and unqueried offline access. Rejected input receives no completed-data
  credit. Readers add no execution credit; runtime traces stay outside card hashes.
- Run unchanged regression cases against the public Ackredit floor outside the
  checkout and extend receiving CI/future staged gates. BindingDB, custom clients,
  broader result coverage and shared MOLI record policy remain open work.

## Complete exact-artifact 0.12.0 publication and archival (2026-10-04, #110)

- Select qualified `7739317` for the immutable 0.12.0 tag. Its `py_1` archive matches
  all 352 non-version Python/JSON source files, passes exact-SHA CI/governance and
  all 12 installed OS/minor lanes, with 56 integration cases and the public workflow.
- Publish the stable GitHub release and promote those same staging bytes. Verify
  the public registry poststate and an independent anonymous download. A public-only
  clean Linux/Python 3.14.7 environment with a new cache checks origins, installed
  bytes/API, frozen-card reading, 56 cases, the workflow and pip check.
- Verify Zenodo 10.5281/zenodo.23134375: its source ZIP checksum/size and all 1160
  files equal the qualified tag. Keep Conda distribution separate from source archival.
  Record all evidence in `sabueso_0.12.0_public_2026-10-04.json`, preserving the
  superseded `py_0` and schema-freeze receipts without overwriting them.
- Add the actual publication date/version DOI and current released behavior to
  maintained documentation in a follow-up metadata/receipt commit. This does not
  move the qualified tag or rebuild the public archive. #110 completes the release;
  #108 remains open for source/result/bibliography coverage and MOLI's record boundary.


## Extend RCSB traceability before authorized 0.12.0 publication (2026-10-04, #108/#110)

- The maintainer requested structural queries, native versions, reuse, empty answers,
  failures, attribution and citations before publishing 0.12.0. Observe built-in
  online/fixture single and batch clients. One logical batch owns normalized ids,
  every chunk/fallback request, and distinct per-entry results/completed ids.
  Credit only completed access, including evaluated-empty results and completed
  subsets in partial batches. Never infer a global database release from entry revisions.
- Request RCSB's native revision fields and primary authors. Preserve only stated
  primary citation metadata, explicitly reporting missing fields. Identical metadata
  reuses a reference; different source-stated forms receive distinct content-based
  identities, preserving earlier references in Ackredit's enclosing workflow.
  The verified resource-description citation remains separate from primary publications.
- Keep runtime traces/citations outside immutable scientific payloads. Schema 0.3.11
  and its clean-installed frozen public card remain frozen. Stored structural support
  credits the RCSB description; applications save intake/workflow sidecars to retain
  the source operation's full original citation metadata.
- The preliminary `4ef9ddc`/`py_0` candidate passed its original gates but lacks this
  requested extension. Preserve its archive/receipts. Qualify a new source SHA and
  `py_1`, including the extended public three-packet workflow and unchanged copied
  RCSB tests in every installed lane. Publish the stable tag at the newly qualified
  SHA, promote the same bytes, verify a clean public install, then verify Zenodo.
- Ackredit #81 is closed through #82; public 0.9.0 is the required portable minimum.
  Broader source/result coverage and MOLI's shared record boundary remain #108/#36 work.


## Freeze 0.3.11 from the clean installed local candidate (2026-10-03, #110)

- Build preliminary Conda 0.12.0 from `01d5bf2` in an isolated builder without an
  upload. Normal installs on Python 3.11–3.14 verify the same archive digest,
  installed bytes, all source modules/resources, public runtime pins and APIs;
  each passes 36 integration regressions, the public workflow and pip check.
- The clean Python 3.14.7 install writes the HsTIM compatibility card from declared
  public UniProt, RCSB and Europe PMC fixtures. It preserves the new located protein
  and derived structure mentions, their assertions/rule and sealed quantities.
  Record the immutable card/archive/source identity in the local receipt and NOTICE.
  The frozen 0.3.11 shape now follows the existing immutability guard even while
  candidate publication remains pending.
- Keep local qualification separate from final-SHA CI and the actual staged-file
  Linux/macOS-arm64/Windows matrix. Stable publication remains gated.
  Omit the optional CFF publication date during qualification rather than inventing
  a publication event; the eventual release and archive state their actual dates.

## Adopt delivered public Ackredit 0.9.0 (2026-10-03, #108/#110)

- The provider's published handoff closes #22/#75/#80. Hosted installed matrix
  37152044426 and promotion 37152421084 preserve the previously received archive;
  an independent public download verifies the same SHA-256.
- Adopt `ackredit>=0.9.0` in metadata, recipe and all runtime environments.
  Installed gates pin public 0.9.0/py_0 and its qualified digest, version and API.
  Remove source overlays/public-pin placeholders and the dependency blocker
  together; keep the generic preflight safeguards for future unpublished providers.
- Runtime CI obtains the provider from public Conda. Dedicated receiving lanes pin
  the first published portable API on all supported minors. Public receiving proof
  remains separate from Sabueso's own Conda installed matrix and schema freeze.
- Preserve the editable primary workspace. The provider's still-0.8.0-based Git
  version cannot satisfy the delivered minimum; report that need as Ackredit #81
  rather than lowering the public floor or inventing a provider tag/version.
  This is a workspace metadata issue, not a public-package delivery blocker.

## Prepare bounded staged 0.12.0 release (2026-10-03, #110)

- The maintainer accepted a substantial 0.12.0 preparation combining located
  literature/structural context, pinned terms and explanations, required packet
  attribution and the first source-acquisition trace. The draft notes and plan
  record this scope without claiming publication or a final candidate SHA.
  `CITATION.cff` follows the planned version, keeping the verified concept/historical
  DOIs; its release date is omitted during blocked preparation, not invented.
- Keep traceability mandatory and state the acquisition slice's actual built-in
  UniProt/Europe PMC coverage. Further sources/results, bibliography gaps and MOLI
  Recorda integration remain #108/#36 work; this release does not claim full coverage.
  The earlier roadmap wording grouped coverage work with the public-release blocker;
  the bounded scope now separates their completion from dependency delivery.
- Use the staged route for a new required provider and schema 0.3.11. Adopt exact
  qualified builder `8da628d9b393e184c3bf3722708b19dcfbf7ef0a` (provider #46/#47),
  preserving immutable coordinates, producer evidence and promotion controls.
- Extend the actual staged-file matrix with required-provider origin/metadata/API
  checks, unchanged copied acquisition/attribution regressions and the public
  saved-reader workflow outside both checkouts. Source CI alone cannot verify the
  eventual Conda file. New Pytest/Receptor dependencies are gate tooling only.
- Leave the public-provider preflight block intact. After verified Ackredit delivery,
  set its real floor/public pins and remove source overlays/blocker together.
  Freeze the new schema from a clean installed candidate before tagging; no frozen
  compatibility artifact is made from the editable workspace.
- Exact final-candidate CI, staged archive inspection and the installed
  Linux/macOS/Windows × Python 3.11–3.14 matrix precede stable publication.
  A builder-pin adoption or preparation receipt is not a staged-build receipt.

## Required source traceability and first acquisition slice (2026-10-03, #108, moli#36)

- The maintainer requires traceability as part of Sabueso's knowledge product and
  MOLI's consuming workflows. Observation is automatic for supported boundaries;
  an application collector is a convenience, not activation of the requirement.
- Instrument built-in UniProt entry/search and Europe PMC mentions/annotations
  first. Keep source-operation identities independent of card/packet identities.
  Record actual fixture/network/reuse/replay access, original versions and response
  identities, empty responses, unavailable fixtures, unqueried requests and failures.
  Partial failed batches preserve completed transport without claiming completed intake.
- Attach detached traces to cards/resolutions, including no-card failures, final
  refresh states and one-call packets. Public source envelopes add a separate trace;
  client return protocols and raw records remain intact. Scientific payloads, hashes,
  card schema and knowledge-store formats are unchanged. Applications save original
  JSON sidecars; saved reading neither reconstructs nor credits execution.
- Credit completed resource access and verified descriptions in the application's
  Ackredit capture. Failed/unqueried access remains in host records with no successful
  acquisition credit. Provider/recording failure diagnoses explicit gaps and preserves
  the scientific result or exception. Bibliography does not establish reuse rights.
- Local formats `sabueso.acquisition_trace@1` and `sabueso.source_acquisition@1`
  are provisional component records. Other sources/custom clients, further results
  and undeclared citations remain explicit gaps in #108. MOLI owns ProjectRecord
  composition and future Recorda routing/correlation/reliability policy (#36);
  this experiment does not implement those platform contracts.
- Keep the existing required-provider public-release gate. Source-installed tests
  and a public-fixture pilot do not establish public dependency delivery.

## Adopt the accepted portable Ackredit contract (2026-10-03, #108, ackredit#75/#22)

- Pin provider source `383a64b2fdbc5472a7cdeb92c464b87433aabd76`, containing the
  accepted `ackredit.attribution@1` contract assigned to prepared 0.9.0. This
  supersedes the earlier provisional-API description and source pin, while retaining
  normal Python 3.11–3.14 installs and automatic required attribution.
- Exercise the installed consumer and provider outside both checkouts in each
  dedicated CI pilot lane, with unchanged tests and frozen public fixture access.
  Testing the source tree alone cannot establish the installed client's behavior.
- Keep the receiving proof for the exact local diagnostic Conda file separate from
  public delivery: Linux Python 3.14.7 passes 14 integration tests, the public
  two-result workflow and pip check. Provider and consumer import from site-packages.
  The archive/installed metadata match SHA-256
  `99e6f9b9f0a3b0a22c66e476230dddabd2ba0017c59beb3253fbadc781d665c6`.
  The receipt is in #108 and ackredit#22/#75; source was
  `15b1958b9752a89974bb1d0df882a17841ed62b4`.
- Preserve release blocking and unversioned required metadata until the accepted
  API's actual public artifact and full supported dependency closure are verified.
  Prepared 0.9.0 is a provider decision, not a public release. Shared publisher
  adoption (molsyssuite#78), staging and hosted exact-file gates remain provider work.
  Repeat receiving tests against the eventual staged/public file and then set the
  actual dependency floor/public pins. No scientific payload or stored schema changes.

## Adopt Ackredit's corrected Python 3.14 contract (2026-10-02, #108, ackredit#80)

- Pin provider source `e4a006a6931f3fb5f97be5b09767c144dfb35662`, which declares
  `>=3.11,<3.15` and aligns its recipe, environments and required CI. Its routine
  CI passed at this exact commit. This supersedes the temporary interpreter
  exception in the original required-dependency decision below.
- Install the candidate normally in every consumer runtime lane. Remove the
  Requires-Python override and experimental 3.14 labels; include 3.14 in the
  dedicated real-provider/public-workflow matrix. The preflight rejects a source
  candidate whose declared range excludes a supported Sabueso minor.
- Preserve the required Ackredit/product contract and the automatic attribution
  behavior. No runtime/card/packet/store schemas or science change.
- Keep the public-release blocker: source compatibility and ordinary source
  installation do not supply a stable portable-API version or a public Conda build
  with a verified clean dependency closure. Those remain ackredit#75/#22; #80
  continues to track the provider's public-delivery qualification. Set the real
  version floor and exact public pins when published; never infer publication from
  a closed issue or a source CI result.

## Required Ackredit and automatic result attribution (2026-10-02, #108, moli#36; interpreter exception superseded)

- The maintainer chose Ackredit as a hard runtime dependency: bibliography and
  attribution are part of Sabueso's knowledge product. This supersedes the initial
  optional-dependency decision below; preserving scientific results on tracking
  failure does not require making a dependency optional.
- Every completed packet composition gets `packet.attribution`, outside its
  scientific payload and hashes. `sabueso.attribution()` is a convenience collector,
  not an activation switch. Applications continue to own sessions/workflows.
- Importing Sabueso or entering an empty collector does not import the provider.
  Composition uses a lazy required import without DepDigest's optional path.
  Missing/broken provider installations emit diagnostics and retain a failed record
  and the completed science, never a successful-attribution claim.
- Save the original detached JSON beside the scientific packet. Payload-only store
  readers return `attribution is None`, without crediting another execution. Packet,
  card and store schemas/hashes do not change.
- Ackredit is required in metadata and the recipe. Its first stable portable-API
  version/build is pending (#75/#22), so no numerical floor or public build is invented.
  A tracked full-commit source overlay provisions every runtime CI lane. Normal
  source installation covers 3.11–3.13. The bounded 3.14 metadata-override probe
  (#80) is experimental consumer evidence, not a provider support/public-install claim.
- The next release is blocked in build, installed-package and promotion workflows
  through `dependency_preflight.py --release`. Re-evaluate #108 when a stable API
  version/public build supports normal clean installation on Python 3.11–3.14;
  then set the actual floor, install public builds in every route and remove the
  source overlay, metadata override and release blocker together.
- The required source candidate includes Ackredit's #78 BibTeX correction. Saved
  original CSL author objects render correctly in text, CSL-JSON and BibTeX; consumer
  regressions check corporate grouping and personal names without new credits.

## Early optional Ackredit integration (superseded, 2026-10-02, #108, moli#36)

- Integrate a bounded runtime adapter now, before the knowledge API grows further.
  `sabueso.attribution()` explicitly observes completed packet composition. It
  collects local detached records (`sabueso.packet_attribution@1`) beside immutable
  knowledge; no shared MOLI payload, card schema, store format or packet hash changes.
- Follow selected stored statements, conflicts and represented relationship
  dependencies with the existing packet-terms support closure, independently of its
  licence verdicts. Full/index scope agrees. Source-record versions remain as stated;
  database releases are not inferred. Broader disease grouping lineage is disclosed.
- Applications own provider sessions. Per-result captures retain reused references
  and contribute to enclosing workflows. Ordinary operations, empty contexts and
  saved readers do not import or credit the provider. Nested observation uses
  ContextVars. Genuine absence retains host records; installed provider failure is
  a catalogued warning with result failure status, never a replacement result.
- Verify complete UniProt/Europe PMC resource-description bibliography offline;
  missing descriptions, target articles and annotation-provider records remain
  explicit gaps. Preserve explicit corporate authors. Report provider defects
  upstream: ackredit#78 owns incorrect author-object BibTeX output. Use CSL-JSON/text
  in the public pilot until the provider fixes it.
- Track a full-commit Ackredit candidate in consumer CI on its declared Python
  3.11–3.13 range. Keep Sabueso's normal 3.11–3.14 CI and public dependency surface.
  Source tests do not establish publication or optional 3.14 closure. Acquisition,
  further result types, public extra and shared boundary coordination remain #108
  work; no release is made by this integration.
- Provider-free subprocess tests identify a missing module with
  `ModuleNotFoundError.name`, as Python does. Public DepDigest 0.12 correctly
  preserves an unnamed/unrelated discovery failure rather than calling it absence;
  the initial CI exposed an incorrectly unnamed test exception. Production results
  and installed-provider tests were unaffected; the consumer test was corrected.

## Read-time literature explanations and packet terms (2026-10-02, #91, #29)

- `literature_explanation@1` walks a publication's stored citation, mention,
  structural citation, measurement and curated/ECO support links. It exposes both
  legs of structural mention context and every qualifier alternative, with exact
  card/item pins. Unlinked annotations remain request outcomes, not SourceAssertions.
  Missing recorded support is partial; missing links never establish article absence.
- `packet_terms@1` is a read-time query over exact saved card pins and the packet's
  represented statements/conflicts/dependencies. Full/index have the same scope for
  the unpublished `packet_aspects@6`; older mappings remain readable, but the terms
  query refuses them until a scope adapter exists. No current mapping substitutes for
  a historical mapping. Index view rules must match the available producer rules.
- Term-bearing statements retain their own resource label, separating article
  fragments from bibliography. A derived relationship requires every recorded
  support leg; source alternatives within a leg use `terms_propagation@1`.
  Disease grouping includes stored MONDO/MedGen identity/hierarchy context because
  exact grouping input lineage was not recorded; it does not claim minimal lineage.
- Registry terms are today's packaged records with their review dates, not terms
  reconstructed as of acquisition. Reports are detached and carry their scope;
  they change no packet hashes/payloads, card schema/shape or store formats.
- Ackredit can provide future runtime/result/workflow bibliography, distinct from
  knowledge support and terms. The optional integration is proposed in #108 and
  moli#36, with consumer feedback to ackredit#75. Provider APIs/publication/Python
  closure remain adoption gates; no runtime dependency is introduced here.

## Literature packet coverage: `packet_aspects@6` (2026-10-02, #71, #92)

- The unpublished mapping adds `relationships.mentioned_in` and
  `relationships.structure_mentioned_in` to the literature aspect. Its index counts
  and cites both separately, and both detail levels expose the same unknowns.
  `full_rules` names `structure_mention_context@1`, read from the producing module.
  Indexes carry references, never copies of quote fragments or structural context.
- Automatic acquisition now requests Europe PMC bibliography (`europepmc={}`). It
  never guesses article ids or fetches located annotations. Explicit article intake
  enters through prebuilt cards and `compose_packet`. PDB context without a matching
  annotation request remains `not_queried`, with a declared per-area explanation.
- `knowledge_query@2`, `knowledge_packet@3`, `packet_index@1`, card schema 0.3.11
  and store format 2 are unchanged. Existing @5 packets read exactly as stored and
  are not compared with @6. A frozen public @5 index was generated with packet code
  at 0ec1423 from the published frozen 0.3.10 card, with provenance in the fixture
  notice; it verifies exact hashing, storage, historical reads and non-comparability.
- The compatibility test exposed that `packet_history` checked format alone and
  reported knowledge changes across incompatible mappings or detail levels. History
  and `same_knowledge` now share the same comparison scope (format, mapping, detail).
  This corrects read-time reporting without rewriting stored packets or hashes.
- Automatic offline acquisition also exposed that an unsaved Europe PMC search
  fixture claimed no article mentions the accession. It now raises `ConnectorError`
  and the packet reports `unavailable`; a real source-stated zero remains
  `not_stated`. No negative literature knowledge is invented from missing fixtures.

## Source-supported PDB mention context (2026-10-02, #92)

- The explicit article route now also reads printed four-character PDB codes with
  matching source-native PDBe names and identifier URIs. Expanded codes and protein
  names remain unhandled. Original annotation content and article ids stay intact.
- A raw occurrence is a Europe PMC SourceAssertion about the PDB entry, not about
  the protein. Supported source-stated `has_structure` pairs already mapped on the
  card supply the protein association (UniProt xrefs or RCSB stated pairs, including
  RCSB assertions about the structure whose value names the protein). No automatic
  retrieval or structural selection is triggered by an annotation. Derived-only,
  dangling or mismatched support is refused.
- `structure_mentioned_in` is a distinct derived protein → publication relationship,
  identified also by `structure_ref`. Rule `structure_mention_context@1` names both
  the raw occurrence and all structural relationships/assertions in its inputs.
  Structural context has `scope: entry_association`; a complex or chimera does not
  establish whole-entry identity, chain/residue scope, or the author's focus.
  Neither scientific claims nor Nextia Evidence are created.
- Direct relationship support holds only raw mention assertions; the structural
  support is explicit in context and derivation. This avoids letting a structural
  source's terms license attached article fragments. All locations and their
  alternatives remain visible in literature and terms. Merging the same rule and
  parameters retains every input from different occurrences.
- `knowledge_state@4` uses per-area counts and request selectors declared by
  enrichers. `located_accession_mapping@2` records processing of both mention kinds;
  historical direct-only requests cannot imply that PDB mentions were queried.
  Valid PDB occurrences without a supported association are reported as unlinked,
  never as negative protein identity or article absence.
- Schema 0.3.11 remains unpublished and accumulates these additive records. Public
  2JK2 in Methods tests the real UniProt association; public 7QON occurrences have
  no supported association on that card. A clearly marked synthetic in-memory 1HTI
  annotation tests accumulated UniProt and RCSB support without altering fixtures.

## Explicit located accession intake (2026-10-02, #92)

- `europepmc={"article_ids": ...}` is an explicit alternative to accession search,
  through the existing declared enricher. Packets do not guess articles to annotate.
- An occurrence reaches `mentioned_in` only when its printed accession and native
  UniProt tag both name the card's anchor. Source-native article ids and annotation
  content remain intact; every occurrence has its own SourceAssertion. Names and
  PDB mentions are outside this increment.
- Acquisition remains `database` with `origin: text_mining`: Sabueso imports Europe
  PMC's annotations, and does not know its pipeline release. No complete sentence,
  scientific claim, extraction by Sabueso or human validation is asserted.
- The additive stored shape is schema 0.3.11 (unpublished); published 0.3.10 is
  frozen. Optional locations are not migration gaps, because refresh cannot guess
  article ids. Recorded explicit requests, including excluded and failed requests,
  are preserved for refresh, together with the terms profile unless overridden.
- Terms reports judge article fragments separately from bibliography, including
  qualifier alternatives. The content label `Europe PMC Annotations` names
  publication terms, not another SourceAssertion source. The API does not state the
  article licence; it stays unknown, and terms profiles exclude intake before
  fetching. The public fixture's separately verified licence is not invented as a
  statement of the API.
- Raw Europe PMC responses may include article fragments. The registry states
  `retention_licence: PUBLICATION-TERMS` separately from the service's bibliographic
  terms. `retention_from_licence@2` uses this override for archived responses, including
  historical records when read: internal retention, sharing unknown. It conservatively
  applies to all of that source's raw answers; Card terms still distinguish bibliography
  and fragments (#100).

## Language & Ecosystem
- Language: **Python**.
- Scientific OSS standards:
  - tests with **pytest**
  - documentation with **Sphinx**
  - package distribution via **conda**
  - development in a **conda micro‑environment**

## Core Data Model
- Output is a **card** with nested sections and strict field ordering.
- Card types: **ProteinCard**, **PeptideCard**, **SmallMoleculeCard**.
 - **Deck** is a first‑class object for collections of cards.
- Identifiers use direct paths: `identifiers.<db>` (no `secondary_ids`).

## SourceAssertions and Provenance (Critical)
- **Uniform SourceAssertion model** for all fields, no exceptions.
- A SourceAssertion records what an external source asserts about an entity or property.
- Cards store **resolved values** only.
- All raw values from all sources are stored as SourceAssertions in `source_assertion_store`,
  which is serialized with the card.
- Each field points to one or more `source_assertion_ids`.
- `selection_rules` is explicit and versioned.
- `quality.conflicts` records unresolved disagreements.

## All‑Values Policy
- **All values from all sources must be preserved**, never discarded.

## Clinical Layer
- Clinical data is included as a **separate layer**:
  - pharmacology
  - ADMET
  - clinical trials
  - pharmacovigilance
  - indications
  - contraindications
  - interactions

## ProteinCard Enhancements
- Protein cards include a **disease** section with disease associations and their SourceAssertions.
- Protein cards include **ligands** with a `role` attribute (e.g., inhibitor, activator, substrate).
- Protein cards provide an operation to **extract a Deck of inhibitor cards**.

## Positional Location Model
- Positional features support both **sequence‑based** and **structure‑based** locations.
- This is required for interoperability with TopoMT and visualization tools.

## Ambiguity Handling
- Ambiguous inputs should return a **Deck** rather than a single Card.
- Ambiguity must be explicit in the output (metadata or quality section).

## Tools API (Public)
- Tools are organized into:
  - `tools.db.*` (per‑database modules)
  - `tools.card.*` (operate on Card)
  - `tools.deck.*` (operate on Deck)
- Tools are intentionally **ad‑hoc** and **heterogeneous** (no common protocol).

## Versioning
- Version strings use **x.y.z** (no leading `v`). Third-party API URLs may include their own
  version segments (e.g., `/v1/`); do not change those.
- Release, card schema, file formats, rules and profiles are separate namespaces (MOLI
  release version policy):
  - card schema `x.y.z`;
  - deck file and curation store: integer `format`;
  - derived rules and enrichment profiles: `name@N`, immutable once published;
  - selection rules: `x.y.z`.
- Views (`Card.structures()` and the others) are Python API, not schema. They change
  with releases, and deprecations are warned about.

## Card schema versioning (2026-09-24)
uibcdf/sabueso#42; the rules are in `devguide/SCHEMA.md` ("Versioning policy").
- Before 1.0, `z` grows with additive optional fields and `y` with anything else. From
  1.0 on, semver.
- A schema version is fixed once a release publishes it. Until then, additive changes
  accumulate in the next version.
- Readers:
  - read their own line, and newer versions of it with a warning, keeping unknown keys;
  - refuse other lines until an explicit migration exists (#51);
  - refuse cards without a version.
- Guards:
  - a frozen card per published schema must stay readable;
  - the recorded card shape must match what the code writes;
  - a published version's shape cannot be rewritten.

## Cache/Store Policy (Pending Decision)
- Decide whether local cache stores **raw source data**, **cards only**, or **both**.
- This must respect licensing constraints.

## Core Ops (Pending Decision)
- Define a minimal, consistent set of **CardOps** and **DeckOps** (compare, filter, sort, expand, etc.).

## Resolver (In Progress)
- Resolver contract defined in `devguide/RESOLVER.md` (0.2.0; selection-rules format 0.1.0).
- Field-level resolver implemented in `sabueso/resolver/field_resolver.py` with tests.
- Field examples documented in `devguide/SELECTION_RULES_EXAMPLES.md`.
- Selection rules are published in docs (`docs/selection_rules.rst`) and machine-readable (`docs/selection_rules.json`).

## Online‑First
- Sabueso is **online‑first**.
- Local card caching is optional and does not replace live queries.

## Terminology: SourceAssertion ≠ Evidence ≠ Provenance (2026-09-23)
- The former Sabueso "evidence" object is renamed **SourceAssertion**: what an external
  source asserts about an entity or property. `EvidenceStore` → `SourceAssertionStore`,
  `evidence_store` → `source_assertion_store`, `evidence_ids` → `source_assertion_ids`,
  mapping outputs `evidences`/`field_evidence` → `source_assertions`/`field_source_assertions`,
  ID prefix `E_` → `SA_`.
- **Evidence** is reserved for Nextia (project-contextual support, contradiction or
  information about a Question/Hypothesis). **Provenance** is cross-cutting.
- Rationale: avoid a permanent ambiguity for humans and MOLI Agent, and follow MOLI Platform
  Architecture 1.0 (`uibcdf/moli`): "External knowledge does not automatically become
  project Evidence".
- Source-native qualifiers (UniProt ECO codes, PubMed IDs, assay descriptors) stay in
  `source_metadata` under their native names; Sabueso defines no generic `evidence` field.
- No deprecated aliases: Sabueso had no release or external consumer when renamed.
- Formal card schema bumped to `0.2.0`; Resolver contract bumped to `0.2.0`.

## SourceAssertion contract aligned with MOLI (2026-09-23)
- SourceAssertion fields follow MOLI Platform Architecture 1.0
  (`schemas/sabueso_source_assertion_conceptual_schema.md`): `id`, `subject_ref`,
  `field_path`, `asserted_value`, optional `normalized_value`, `source`
  (`type` ∈ database|literature|patent|curated|other), `retrieved_at`,
  `source_metadata`, optional `provenance_ref`.
- `subject_ref` is `<namespace>:<record_id>` of the source record (e.g. `uniprot:P52789`);
  linking it to a Sabueso entity is the job of the future EntityResolver.
- The resolver works on `normalized_value` when present, else on `asserted_value`.
- Cards carry a stable `meta.card_id` (`sabueso:<entity_type>:<subject_ref>`, provisional
  syntax) and `meta.schema_version`; SQLite persistence keys cards by `card_id`.
- Sabueso is the Knowledge component of the MOLI Platform's Scientific Context, not a
  MolSysSuite member (MolSysSuite admission withdrawn, `uibcdf/molsyssuite#40`).

## Entity identity, relationships and structures (2026-09-23)
Agreed contract in `devguide/archive/entity_resolver.md` (uibcdf/sabueso#6):
- **Protein identity:** anchored on a UniProt record. Use the reviewed canonical entry
  when one exists; otherwise apply an explicit, recorded preference. Anchor changes are
  recorded as `superseded_by`, never rewritten silently. Consumers treat references as
  opaque.
- **Ambiguity:** resolved only by a named, versioned preference policy
  (`prefer_reviewed@1`). The non-preferred candidates are kept on the Card as
  `alternatives` and never feed fields. Preferences never cross organisms, and identical
  sequences in different organisms are never identity.
- **Relationships:** first-class, with deterministic ids. They are backed by
  SourceAssertions, or by a derivation record when inferred. They are stored with the
  subject Card; re-evaluation in uibcdf/sabueso#19.
- **Structures:** no StructureCard. The ProteinCard exposes a `structures` view over
  `has_structure` relationships, which carry mandatory raw qualifiers (chains, range,
  coverage, other entities present) and a derived classification with visible thresholds.
  Structure facts keep `pdb:<id>` as subject. Re-evaluation in uibcdf/sabueso#20.
- **General rule:** possible future problems of a design decision are recorded in
  `devguide/`, and decisions that need later re-evaluation get an issue with explicit
  triggers.


## Small-molecule identity (2026-09-23)
Decided by the Sabueso owner (uibcdf/sabueso#25, `devguide/archive/molecule_identity.md`):
- **Anchor:** a small molecule is anchored at its standard InChIKey. Its card id is
  `sabueso:small_molecule:inchikey:<key>`.
- **Links:** source records (`chembl:`, `pdb.ligand:`, and the DrugBank, PubChem, ChEBI
  and BindingDB records listed by UniChem) are linked to `inchikey:<key>` with `same_as`,
  supported by the source that states the key.
- **Standard keys only:** records without a standard InChIKey are reported as
  unanchored, never guessed.
- **Variants are not merged:** charge, salt, stereochemistry and tautomer variants have
  different anchors. A future connectivity-level link must be a derived
  `possibly_same_as`.
- Rejected alternatives: a preferred source record (no chemistry source is universal),
  and the UniChem compound id (internal to one service).

## Computable properties are recorded, not computed (2026-09-23)
Proposed in uibcdf/sabueso#25 and accepted by the Sabueso owner. It is the boundary for
uibcdf/sabueso#10.
- **What Sabueso does:** it records the physicochemical properties that sources state
  (logP, TPSA, rotatable bonds, molecular weight, ...). Each value is a SourceAssertion,
  traceable to the source that computed it and to its method. Different methods give
  different values, and they are qualified by method (#10), never reconciled by
  recomputation.
- **What Sabueso does not do:** it does not compute those properties itself. Running a
  descriptor, a fingerprint or a similarity over a structure is modelling. Modelling
  belongs to MolSysSuite, not to the Knowledge component of the MOLI Scientific Context.
  A value computed by Sabueso would have no source to cite.
- **In practice:**
  - no module of the `sabueso` package imports a chemistry toolkit (RDKit, Open Babel,
    OpenEye, Mordred, ...). Toolkits may be used in tests or tooling, never to feed a
    card. `tests/core/test_boundaries_offline.py` enforces this;
  - a computed property, if ever needed on a card, arrives as a MolSysSuite result with
    its own derivation record. It never appears as a SourceAssertion;
  - similarity and fingerprints are the same case, and the more tempting one: "molecules
    similar to this inhibitor" looks like knowledge, but it is a calculation.
- **Scope:** if this boundary starts to bind other MOLI components, it becomes a shared
  contract to raise in `uibcdf/moli`.

## Guard by default against entity merges (2026-09-23)
Closes uibcdf/sabueso#21 (`devguide/archive/legacy_entity_paths.md`).
- `build_card_from_mapping` refuses fields fed by assertions about several subjects,
  unless the caller passes `entity_subjects` after resolving their identity.
- There is no unguarded merge path: a false entity merge is worse than an unresolved
  conflict.
- Small molecules have one identity scheme: every card is anchored at the standard
  InChIKey, whatever the source of its records (ChEMBL, PubChem, PDB CCD).

## Resolution compares like with like (2026-09-23)
Closes uibcdf/sabueso#10 (`devguide/archive/physchem_normalization.md`).
- Every field is resolved from its SourceAssertions, with the packaged rules when none are
  given. A multi-source field never takes the last value merged while citing every source.
- Values are compared only when they measure the same thing: within one method
  (`compare_within`), within one source for representations only a toolkit can
  canonicalise (SMILES), and within the precision each source states
  (`numeric_agreement: "stated_precision"`). The rest are `alternatives`, visible and never
  conflicts; real disagreements stay `conflicts`.
- Items of a list field are a union, not competing values.
- A small molecule's properties describe the structure its card is anchored at (ChEMBL
  `full_mwt`, not the parent's `mw_freebase`).

## Quantities travel with their units, sealed (2026-09-24)
uibcdf/sabueso#32 (`devguide/archive/quantities.md`); the format is PyUnitWizard's
`QuantityRecord` (released in 0.27.0; design in uibcdf/pyunitwizard#83).
- Sabueso answers quantity questions with quantities, and stores every quantity as
  `{value, unit}` in PyUnitWizard's canonical spelling.
- Stored cards seal their quantities (one QuantityRecordBundle, columns by path and
  unit); loaders verify, and there is no default unit.
- Bioactivity concentrations are normalized to nanomolar with explicit conversions; the
  source's value and unit are kept verbatim. pChEMBL is kept as ChEMBL states it.
- Sabueso never sets PyUnitWizard's session policy; stored numbers do not depend on it.
- Every place a card stores quantities, and its unit, is declared in
  `quantities.NEGOTIATED_UNITS`. The writer refuses anything else, and the reader
  declares those units' dimensionalities itself. It never takes its expectations from
  the card it verifies.
- Plausibility is checked, never corrected: `pchembl_consistency@1` and
  `unit_scale_discrepancy@1` flag measurements, and resolver conflicts mark exact 10³ or
  10⁶ ratios. Closes uibcdf/sabueso#32.

## Curated literature assertions (2026-09-24)
uibcdf/sabueso#41, part 2. Free-text claims are deferred to uibcdf/sabueso#43.
- A person or an agent reads a paper and records what it states. Sabueso does not read
  papers: it checks the shape against the field, stores the claim as a literature
  SourceAssertion, and compares it mechanically.
- Only existing knowledge fields and relationship predicates take curated assertions.
  Identity, sequence, metadata, identity links, `has_structure` and `described_in`
  never do.
- Curated bioactivities (uibcdf/sabueso#44):
  - the molecule carries its full identity: its InChIKey and every record linked to it,
    resolved by Sabueso rather than typed by the curator;
  - a curated measurement is compared only with ChEMBL measurements of the same
    publication, the same molecule and the same type, at the precision it was stated
    with;
  - the curator states whether it was measured on this protein or on an ortholog.
- A curated assertion never takes priority automatically ("Literature" is in no priority
  list), and it is never discarded. Its outcome is always recorded (`quality.curation`).
  A difference is reported in `quality.conflicts` and warned about
  (`SABUESO-W-CURATION-001`).
- On list fields, "differs" means the same item, identified by position and
  substitution, site or disease accession, stated differently. Whether two texts
  contradict each other needs a reader, so Sabueso flags the difference and never
  judges it. Free-text lists are `not_compared`.
- Quantities are compared at the precision they were stated with, converted to the
  field's unit ("0.9 kDa" states hundreds of daltons).
- How a curated assertion bears on a project's hypotheses is Nextia Evidence
  (SourceAssertion ≠ Evidence).
- Curations survive rebuilds through a `CurationStore` (uibcdf/sabueso#48):
  - a JSONL file of what was curated, never a card;
  - applied when a card is built, with the same content-derived SourceAssertion ids;
  - outcomes are recomputed, and changes are reported;
  - retractions are kept and never applied.

## Enrichment profiles (2026-09-24)
uibcdf/sabueso#45.
- A profile names a set of card-tool options, and its version is part of the name
  (`structural_baseline@1`). A published profile never changes: a change is a new
  version.
- Explicit options override a profile. The profile, the options it gave and those
  overridden are recorded in `quality.entity_resolution.decision.profile`, so a card
  says how it was built.
- Profiles hold Sabueso's own options only. A study's methodology, meaning why this
  baseline, belongs to Praxis.

## Three public layers (2026-09-24)
uibcdf/sabueso#49, `devguide/SOURCE_ACCESS.md`.
- The layers are source access (raw records in a provenance envelope), mappings
  (SourceAssertions) and cards (resolved knowledge). Each is public.
- Each source has one module with one set of clients, shared by card building and
  direct queries.
- Sabueso retrieves knowledge records, never coordinate files; loading structures
  belongs to MolSysMT.

## Glossary of entities (2026-09-24)
uibcdf/sabueso#52 (Diego's proposal).
- A card lists each molecular entity it mentions once (`entities`). Relationships keep
  their source's record, which is their provenance, and the glossary resolves it to an
  entity.
- Identity is stated, never guessed: records merge only on a source's statement.
- What a curator states is the molecule as given and its InChIKey. The records UniChem
  links are identity knowledge in the glossary, so curated ids do not change when UniChem
  learns a new record.

## Tables and optional dependencies (2026-09-24)
uibcdf/sabueso#46.
- `Card.table(view, **options)` gives flat rows. Quantities stay quantities. Lists
  become `"; "`-joined text.
- `sabueso.to_dataframe(rows, units=None)` gives numbers only in a unit the caller
  names: the unit goes into the column name and `df.attrs["units"]`. A column holding
  several kinds (nanomolar and percent) is refused rather than half converted.
- pandas is optional, and DepDigest checks it at call time (`sabueso/_depdigest.py`,
  `LibraryNotFoundError`). DepDigest therefore now applies to Sabueso, the condition
  recorded in #31.


## Card snapshots and the knowledge store (2026-09-25)
uibcdf/sabueso#7 and #27. The design is recorded in
`devguide/archive/card_versioning_snapshots.md` and `devguide/archive/native_store.md`.
- **A snapshot is content-addressed.** `Card.snapshot_id()` is the SHA-256 of the stored
  card (`Card.to_dict()`) in canonical JSON, with the quantities seal left out and
  SourceAssertions and relationships in canonical order. The same state always has the
  same id, whoever computes it and wherever the card is kept, so a JSON copy can be
  checked against a pin without a store.
- **A revision is what a human reads.** A store records the order in which a card's
  snapshots were saved, when, and with a note. Both at once: the revision for people, the
  hash for identity and integrity.
- **References (provisional, uibcdf/moli#3):** `<card_id>` for the latest state,
  `<card_id>@sha256:<hex>` for one exact state, and `…#SA_…` or `…#REL_…` for an item in
  that state. An item reference must be pinned. A pinned read returns that exact state
  or fails; it never returns another one.
- **The knowledge store is normalized SQLite** (`sabueso.KnowledgeStore`). A card's
  document, meaning its sections, quality, rules, entities and meta, stays one JSON
  column. SourceAssertions and relationships become rows keyed by their content, and are
  shared by every snapshot that holds them. Relationships are indexed by object,
  subject and predicate. Decks are stored by name as their meta and the pinned states of
  their cards.
- **Rows are keyed by content, not by id.** A SourceAssertion id names what was stated,
  so the same statement from another source release is a different row. Two cards share
  a row only when they state exactly the same thing. Different subjects never do.
- **JSON/JSONL stay the exchange formats.** `save_card_sqlite` and `save_deck_sqlite`
  stay as they are. `KnowledgeStore.import_card_table` turns their rows into history.
- **The store's tables are Sabueso's implementation.** Other components rely on the
  reference forms, not on the tables.

## Ranges and stated uncertainty (2026-09-25)
uibcdf/sabueso#37; card schema 0.3.2; rule `bioactivity_class@3`.
- **A range keeps both ends,** verbatim and normalized: `upper_value` and
  `normalized_upper`. It is classified by its band when both ends share one, and is
  `inconclusive` across a threshold. A range is never read as its lower end, and takes
  no pChEMBL check and no scale comparison.
- **ChEMBL_37 states no range.** `standard_upper_value` is null in all 24,527,044
  activities (checked through the API on 2026-09-25). The ChEMBL path is kept for
  fidelity, guarded by a constructed record. Ranges read in papers are the case that
  occurs.
- **Uncertainty is Sabueso's representation,** since PyUnitWizard defines none.
  `normalized_uncertainty` is `{kind, half_width | lower, upper, level?, n?}`, with
  quantity nodes in the measurement's normalized unit. The kinds are `sd`, `sem`,
  `unspecified` (a bare "±") and `ci`. As written, it is part of the curated statement
  and of its id. No database Sabueso maps states an uncertainty.
- **Uncertainty changes neither the class nor agreement.** The class is read from the
  central value. A curated value agrees with ChEMBL's reading of the same paper when
  the numbers agree at their stated precision: agreement is about transcription, not
  about the spread of the measurement. A point and a range never agree.

## Organism identity, gene loci and orthology groups (2026-09-25)
uibcdf/sabueso#54; additive, card schema 0.3.2.
- A protein card states its organism's NCBI taxon (`annotations.taxon_id`) and its
  lineage (`annotations.lineage`, from the root down, the organism excluded), as
  UniProt states them. UniProt's taxon is strain-level when the entry is, so no
  separate strain field is needed.
- `identifiers.gene_loci` lists gene loci in organism databases: VEuPathDB components
  (TriTrypDB, GiardiaDB, HostDB…) and NCBI Gene. A reviewed entry can gather the loci
  of several strain genomes (TcTIM lists 11). Loci are the identity anchors that tell
  paralogs apart (#55); sequence similarity never is.
- OrthoDB and eggNOG groups are `classified_in` relationships, like the other
  classifications. A missing group is "not stated", never "not an ortholog": UniProt
  gives HsTIM an OrthoDB group and TcTIM none.
- `Deck.in_lineage(taxon)` keeps cards whose organism is or descends from the taxon.
  Cards whose lineage is not stated are listed apart, not dropped silently.
  `Deck.group_by(field_path)` groups by a resolved value.

## Identity hygiene (2026-09-25)
uibcdf/sabueso#55 and #62.
- **Identity never comes from sequence similarity.** Paralogs can be closer in
  sequence than redundant entries of one protein: two Trichomonas vaginalis
  paralogs differ in 4 of 252 positions, while human P60174 and Q53HE2 differ in 1
  of 249.
- **Rule `protein_identity_audit@1`** (`sabueso/core/identity_audit.py`) compares two
  entries of related organisms. Related means the same taxon, one in the other's
  lineage, or a strain name extending the species name. The steps:
  - a shared gene locus with an agreeing sequence gives `possibly_same_as`, and with
    another sequence gives `same_gene` (isoforms, fragments, alleles);
  - distinct loci of one genome give `distinct_genes`;
  - otherwise, an identical or near-identical sequence gives `possibly_same_as`.
    Near-identical means the same length and at most 2% of positions differing,
    compared position by position. Different lengths are not compared: aligning
    belongs to MolSysMT.
- **Nothing merges.** `possibly_same_as` is a flag for review. The resolver records
  the findings among search candidates (`decision["identity_audit"]`), and
  `Deck.identity_audit()` among a deck's protein cards.
- **Named anchors are curated.** A curator states a name for an entry
  (`names.synonyms`, with a publication). `resolve(EntityQuery(name=...),
  curations=store)` answers from that anchor before any search (rule
  `curated_name`). A name that designates two entries is ambiguous, and a name
  anchored in another organism does not answer the query.
- **Curated ids include the subject** (id scheme 2, #62). Stores written earlier are
  re-identified record by record when applied or saved, and the old id is kept.

## Knowledge states (2026-09-25)
uibcdf/sabueso#56; rule `knowledge_state@1`.
- `card.knowledge_state()` and `card.table("knowledge_state")` give one row per area
  and source: `known`, `conflicting`, `not_stated`, `not_queried` or `unavailable`,
  with the source release, a count and the basis.
- `not_stated` means the source was consulted and states nothing. For UniProt this
  covers every field and relationship its mapping can give (`STATED_FIELDS`,
  `STATED_PREDICATES`). For enrichments it means the request answered with nothing.
  The basis keeps the reason: "no ChEMBL cross-reference in the UniProt entry" means
  ChEMBL was not asked, not that ChEMBL has no data.
- `not_queried` means the enrichment was not requested; `unavailable` means a request
  failed and nothing was stated.
- These are facts about sources, never Evidence: what an absence means for a project
  is Nextia's.

## Versioned decks and traceable membership (2026-09-25)
uibcdf/sabueso#58.
- **A deck revision is content-addressed**, like a card snapshot: its meta plus the
  pinned references of its cards (`Deck.snapshot_id()`). Decks are referenced as
  `sabueso:deck:<name>`, meaning the latest revision, or `sabueso:deck:<name>@sha256:…`,
  meaning that exact revision or failure. Deck names use letters, digits and `_ . -`.
- **Membership is part of the content.** `meta["membership"]` maps each card to its
  basis, and `meta["excluded"]` records candidates left out with their reason.
  `ambiguity_deck` and `ligand_deck` fill the membership. `Deck.add(card, basis=...)`
  and `Deck.exclude(candidate, reason, by=...)` let a curator do the same.
- **Derived decks record their operations** (`meta["operations"]`), and keep the
  membership of the cards they hold. `filter(predicate)` is marked not reproducible.

## Comparing two cards (2026-09-25)
uibcdf/sabueso#59; rule `card_knowledge_diff@1`.
- `card.compare_knowledge(other, residue_map=None)` says, area by area, what both
  protein cards state, what only one states, and what they state differently.
  - Fields: list items are compared by their identity (`curation.ITEM_IDENTITY`), and
    lists of plain values as values.
  - Relationships: the objects both cards point at, and those only one does.
  - Knowledge states: the ones that differ.
- **Positions need a mapping.** The same number in two entries is not the same residue.
  Positional features are `not_compared` without a residue mapping, and an item with
  an unmapped position is `not_comparable`. The mapping comes from an alignment
  (MolSysMT) and is recorded as the basis.
- **Free text is `not_compared`,** as for curated claims (#43).
- The comparison is a derived view, never a SourceAssertion.

## Predicted structures (2026-09-25)
uibcdf/sabueso#57.
- AlphaFold DB models are `has_predicted_structure` relationships
  (`alphafold:<entry id>`), a predicate of their own. `Card.structures()` and every view
  of experimental structures therefore cannot count them, by construction.
- A model carries what a reader needs to judge it: version, tool, mean pLDDT and its
  bands, the range covered, and whether the modelled sequence is the entry's current
  one. A model of an older sequence version is flagged, not dropped.
- `predicted_structures=True` is an opt-in enrichment. Its outcome is a knowledge
  state like any other: known, not stated (no model), not queried, or unavailable.
- Sabueso records models; it never downloads coordinates (MolSysMT).

## Curated ligand engagement (2026-09-25)
uibcdf/sabueso#61.
- `card.add_literature_engagement(molecule, residues, mechanism, publication, curator,
  covalent_residue=None, method=None, ...)` records the residues a paper says a compound
  acts on, and how. The result is an `engages` relationship, anchored by the molecule's
  InChIKey.
  - Residues are UniProt positions of the entry. A residue code given with a position
    must match the entry's sequence, which catches numbering slips.
  - A covalent engagement names its modified residue.
- Compared with the structural ligand sites of the same molecule (PDBe-KB): shared
  residues corroborate. Different residues are `not_comparable`, never a conflict,
  because a site can differ between states or constructs. Without an observed site the
  engagement is `new`.
- `Card.ligand_sites()` shows curated engagements next to observed contacts, each with
  its source. The curation store keeps them across rebuilds.

## Source registry (2026-09-25)
- `devguide/sources/registry.yaml` records every online resource Sabueso uses, has
  set aside, or has yet to review. Statuses: in_use, evaluating, queued, deferred,
  rejected, retired, out_of_scope. Each decision states its reason, and `deferred`
  states when to revisit.
- It is validated in CI: every `tools.db` module is an in_use entry, and a decision
  without its basis fails. The user page `data_sources.md` is generated from it.
- Proposals arrive through GitHub Discussions ("Data sources", with a form); the
  registry, not the thread, records decisions (`devguide/sources/README.md`).
- It was seeded from Diego's inventory of open resources for drug design (54 queued),
  plus the sources already in use and those set aside earlier (#21, #22, #29, #60).
- To be shared with MOLI once it has proven itself in Sabueso.

## Organism relations from NCBI Taxonomy (2026-09-25)
uibcdf/sabueso#67; card schema 0.3.4.
- `taxonomy=True` (with `taxonomy_client`) adds `annotations.taxonomy`: the organism's
  taxon, its rank and every ancestor with name and rank, from NCBI Taxonomy (Datasets
  API, no key, public domain). UniProt's `annotations.taxon_id` stays the anchor.
- The identity audit uses NCBI ancestors when both cards have them, and its answer is
  final: related (`ncbi_lineage`) or not, whatever the names suggest. Otherwise it falls
  back to UniProt names, and every finding says which one decided (`organisms`).
- `Deck.group_by_rank(rank)` groups cards by the taxon of a rank (genus, family…).
- The resolver's search candidates are still compared by names, because they are not
  enriched; the audit of cards in a deck is exact once they are.

## One measurement, several sources (2026-09-25)
uibcdf/sabueso#66; rule `measurement_identity@1`;
`devguide/archive/measurement_identity.md`.
- Source records are kept. A measurement is a derived group over them, and views count
  measurements.
- Identity in layers: declared provenance (exact); then independent readings of one
  paper (publication, molecule through the glossary, type, relation, value at the
  coarser stated precision); ambiguity is never resolved silently.
- Pairs with the same paper, type and exact value but different molecules are reported
  for review (`molecule_differs`, `stereo_differs`, `molecule_unresolved`). They may be
  curation discrepancies between sources.
- Copies are pointers: a copy whose original is missing leads to it, and is not
  discarded.
- BindingDB is the second bioactivity source. Its monomers are anchored through
  UniChem, never from SMILES.
- PubChem BioAssay (#68): copies deposited by ChEMBL or BindingDB are grouped with
  their originals by provenance (assay and molecule), never vote for a group's class,
  and lead to ChEMBL assays a card lacks. A copy whose compound PubChem standardised
  differently is grouped only when the connectivity leaves one candidate, and is
  flagged.

## Migrating cards (2026-09-25)
uibcdf/sabueso#51; rule `card_migration@1`.
- Loading a card of another schema line is refused, and the error points to the
  explicit `sabueso.migrate_card(data)`. Nothing is migrated silently.
- A migration is honest, not complete.
  - Each step records what it converted and the **gaps**: `missing` when a fresh build
    with the same options would state it, `available` when it is a new enrichment one
    can ask for.
  - Additions a version made are listed in `migration.SCHEMA_CHANGES`, and a test
    requires an entry for every schema version.
- The original is never changed: its snapshot id is recorded, and with `store=` the
  original and the migrated card are two revisions of one card.
- `sabueso.refresh_card(card)` builds the card again with the options its
  enrichments record, re-applies curations, and records which gaps it completed and
  which the sources do not state.
- Steps between lines are functions in `migration.STEPS`. None exists: every card
  published so far is in the 0.3 line.

## Free-text claims typed by topic (2026-09-25)
uibcdf/sabueso#43.
- `card.add_literature_claim(topic, text, publication, curator, about=..., locator=...,
  quote=...)` records a claim that fits no structured field, in `literature.claims`,
  as a curated SourceAssertion. The curation store keeps it across rebuilds.
- **Never compared.** Whether two texts agree needs a reader, so the outcome is always
  `not_compared`. `card.claims(topic=None)` and `card.table("claims")` list claims by
  topic, with their provenance.
- **Topics are Sabueso's own provisional vocabulary** (`curation.CLAIM_TOPICS`): a new
  topic is an additive schema change. A vocabulary shared with Praxis or Nextia would
  be agreed in uibcdf/moli.
- **Promotion.** When claims of one topic recur, they should become a structured field
  or predicate, and cards move to it with `migrate_card` (#51). Biological context may
  be the first case (#60).
- **Claims drafted by an agent** stay SourceAssertions, with the agent recorded as
  curator. They are never Evidence (Nextia).

## Names from UniProt, and the names of a deck (2026-09-25)
- UniProt's other names are mapped with their kind:
  - `names.synonyms` holds `{name, kind}`, where `kind` is `alternative_name` or
    `submission_name`;
  - `names.abbreviations` holds `{name, of}`, `of` being the full name shortened;
  - `names.gene_names` holds `{name, kind, gene}`.
- A curated `{name}` that UniProt states corroborates it. `kind` describes the item,
  it does not state it (`curation.DESCRIPTOR_KEYS`).
- **A name is not an identity.** Most protein names name a function: "TIM" abbreviates
  "triosephosphate isomerase", which every organism's enzyme carries. A label such as
  "TcTIM" is the literature's; it enters as a curated synonym with its publication.
  Only accessions and gene loci identify an entry.
- `deck.unique_names(return_cards=False)` lists the distinct names of a deck, as
  `numpy.unique` does. It follows rule `unique_names@1`: spellings equal ignoring case,
  spaces, hyphens and underscores are one name, shown in the spelling most cards use.
  With `return_cards=True` it also returns, per name, the distinct cards that carry
  it. It is a view for reading and review. Nothing is grouped, stored or merged by
  name. Whether two cards with one name are paralogs or redundant entries is the
  identity audit's question.

## Structural inventory: grouping keys and residue maps (2026-09-26)
uibcdf/sabueso#70, found running the inventory live on two orthologs.
- **`group_by`** chooses the keys of a group among `structures.GROUP_KEYS`. The
  default, every state key, keeps the results of `structure_inventory@1` as they were
  cited. `ligands:interest` reads the ligand state coarsely: `no_ligands` and
  `no_ligand_of_interest` are both `none_of_interest`.
- **`residue_maps` and `reference`** place each card's substitutions in the reference
  card's numbering. The maps come from the caller, e.g. a MolSysMT alignment; Sabueso
  aligns nothing. `shared_substitutions` lists a reference position and residue found in
  several proteins, and the key `substitutions` groups mutants by them.
- **Equal numbers are never equivalent positions.** A card without a map keeps its own
  numbering, and its substitutions match no other card's.
- The rule's parameters record the keys, the reference and the mapped cards, so a
  grouping can be told from another.

## Gene loci across databases (2026-09-26)
uibcdf/sabueso#69.
- Two entries of one gene can state it in different databases. In the case found, a
  Swiss-Prot entry states a TriTrypDB locus, and a TrEMBL entry of a strain genome
  states an NCBI GeneID. The audit could not relate them and fell back to sequence.
- **Reported first.** A sequence-based finding says `gene_loci: not_comparable`, with
  each entry's databases, when both state loci in databases that do not overlap.
- **Decided by a source.** NCBI Gene lists the UniProt entries (Swiss-Prot and TrEMBL)
  of a gene's products. With `resolve(..., ncbi_gene=True)`, the resolver's audit asks
  NCBI Gene for the NCBI loci of a `not_comparable` pair, and only then. When the gene
  lists both entries, the gene is shared as a common locus would be (`gene_products`,
  with the gene and the retrieval date), and the request is recorded in the decision's
  sources. A failed or empty answer changes nothing.
- **Not done:**
  - matching locus tags as text (`TcCLB.508647.200` and `tcr:508647.200`), which is
    fragile and not a source statement;
  - KEGG, whose licence restricts use.
- **Resolution only.** `Deck.identity_audit()` works on cards, which do not store gene
  products. Extend it only when a deck needs it.

## Two integrated routes, and a guide that stays true (2026-09-26)
- **Two routes.** Sabueso's plan follows two routes, integrated in
  `devguide/ROADMAP.md`:
  - the foundational plan of the original design (2026-01 → 2026-09-23);
  - the pilot-driven route (since 2026-09-23).

  The pilots decided the order of the work, not its scope. The foundational objectives
  stay objectives, and the roadmap tracks each one's status: done, partial, pending or
  changed (the last citing the decision that changed it).
- **Nothing is dropped.** The original roadmap, source plan, next steps and
  long-term-direction conversation were archived verbatim, with notes pointing to where
  they are tracked. Sources of the original plan that were missing from the registry
  (eMolecules, ChemSpider, ClinicalTrials.gov, PiSITE, CPPsite, IUPAC resources) were
  added as `queued`.
- **Kinds of document.** The devguide has an index (`devguide/README.md`) that classes
  every document as normative, living, design or historical, and states how the guide
  is kept true.
- **AGENTS.md holds the repository's working rules**, which were recorded nowhere
  before:
  - language, knowledge principles, code conventions;
  - schema policy, tests and fixtures, local gates;
  - commits, releases, recording work, pilot confidentiality.

## Findings of the first live run of the knowledge baseline (2026-09-26)
A live run of the first pilot's knowledge baseline on 0.4.0 was audited against the
sources. Issues #72–#75 record what it found.
- **The oligomer the authors define (#72, `structure_state@2`).**
  - The state read the first assembly by id. For 2V5B, a monomerization structure,
    that is the software-predicted dimer, while the authors defined a monomer.
  - The oligomer now comes from author-defined assemblies, else from the software's.
  - `oligomer_basis` says which, and a software prediction the authors' assemblies do
    not include is flagged (`oligomer_disagreement`), never resolved.
- **Author numbering (#73, card schema 0.3.5).**
  - Positions stay in UniProt numbering. `author_numbering` adds, per chain, the author
    residue numbers from RCSB (`auth_to_entity_poly_seq_mapping` through the entity
    alignment), as compact segments.
  - Views give `author_substitutions` (`E104D` next to UniProt `E105D`).
  - It is a source statement; geometry stays with MolSysMT.
- **Partial source answers (#74, `knowledge_state@2`).**
  - RCSB failed that day, server-side, on the per-chain data of some entries. The client
    now fetches such an entry again without those fields and marks it `_partial`.
  - The card keeps the rest. The enrichment is `partial` (warning
    `SABUESO-W-ENRICH-003`), and the knowledge state is `partial`, naming the
    structures that failed or came back incomplete. "known" no longer hides a gap.
- **The recorded shape and fixture growth.** The shape builder pins its input
  structures, so a new fixture does not change a published shape. Chain-keyed qualifiers
  are recorded as `{chain}`.
- **The measurement review lists only unexplained pairs (#75).**
  - Two compounds of one paper can share a value. When each is already grouped with a
    record of the other source stating its own molecule, pairing them crosswise is no
    discrepancy, and the pair is left out.
  - The list has one entry per pair of molecules, with all its records.
  - On the live P52270 data, 7 entries became 3 unexplained ones: one `molecule_differs`
    worth reading, and two declared copies with other stereochemistry.

## A pinned item is read from its verified snapshot (2026-09-27)
uibcdf/sabueso#79; acceptance case 2 of uibcdf/moli#3.
- `KnowledgeStore.source_assertion(pin#SA_…)` and `relationship(pin#REL_…)` used to read
  the item row directly. `load(pin)` re-verified the whole snapshot, but these did not,
  so a row changed outside Sabueso came back under an unchanged pin.
- Both now rebuild and verify the snapshot, as `load` does, and take the item from that
  verified state. `relationships()` verifies every state it cites before returning, in
  the same transaction.
- Verification is never cached across reads. A cache would let a change made after the
  first read pass unnoticed. The cost is about 0.1 s per item read, for a card of about a
  thousand relationships.

## Early dependency-contract preflight (2026-09-27)
uibcdf/sabueso#76, adopting MOLI's distribution policy (uibcdf/moli#21).
- `pyproject.toml` stays the only authority for runtime names, constraints and
  `requires-python`.
- `devtools/dependency_routes.toml` lists where the runtime is installed: the conda
  recipe, the test, development and docs environments, and the exact public builds the
  staged-package test pins. It also lists, with a reason, the routes that do not install
  the runtime.
- `devtools/dependency_preflight.py` compares them, using the standard library only. It
  fails on:
  - a missing dependency;
  - a weaker or unconstrained floor, or a ceiling above the public one;
  - a missing or wider Python constraint;
  - an unlisted route.
  It never rewrites files. CI's quality job runs it first; it is also a local gate.
- Its first run found real drift. The staged-package test pinned SMonitor 0.16.0, below
  the new floor of 0.17.0, and would have failed to solve at the next release. The pin
  is now the public 0.17.0 build.
- The check for siblings installed from source does not apply: no required lane
  installs a sibling from a Git checkout. The inventory says so, and a lane added later
  must be declared there.
- **The staged-package gate pins its builds in two places**: the workflow's
  `create-args` and the verifier's `PUBLIC_DEPENDENCIES`. The verifier still pinned
  SMonitor 0.16.0. The preflight now reads both, and a test requires them to agree.

## Generated and packaged resources in the release artifact (2026-09-27)
uibcdf/sabueso#77, adopting MOLI's distribution policy (uibcdf/moli#26).
- **One claimed public route**, the `noarch` conda package. No wheel is published.
- **What it carries:**
  - package-critical resources: the packaged selection rules and enrichment profiles
    (`sabueso/resolver/*.json`). A missing one made 0.1.0 unable to build cards (#35);
  - version-bearing payloads: `info/index.json`, the `_version.py` versioningit writes
    at build, and the `dist-info` metadata.
- **Inspection before installation.** The staged-package test inspects the exact staged
  file (`verify_staged_install.py archive`): digest, embedded versions and resources.
  The installed gate then exercises the resources (`api_smoke` reads both JSON files).
- A test keeps `REQUIRED_RESOURCES` equal to the shipped package data. Negative fixtures
  cover a stale embedded version, stale metadata, a missing resource, another digest and
  another version.
- Checked against the published 0.4.0 artifact
  (`sabueso-0.4.0-py_0.tar.bz2`, sha256 `ba12e2d2…2e3e`): passes.

## Immutable Conda coordinates and the public poststate (2026-09-27)
uibcdf/sabueso#78, adopting MOLI's distribution policy (uibcdf/moli#25).
- **The route.** The staged route uploads to `staging`, and promotes by adding `main`
  to the same file through the provider's exact-file primitive, which checks the digest
  and source label. The action is never given `overwrite`, so it never uses `--force`.
- **Before a staged upload.** `release_route.py coordinate` refuses a coordinate the
  registry already holds under any label, identical bytes included. The direct route
  keeps its stricter check: no file of that version may exist.
- **After promotion.** `release_route.py poststate` verifies the exact coordinate,
  labels and SHA-256 with a repeatable read-only registry query and bounded retries. It
  records a receipt; an unobserved record fails the gate. The `conda search` check stays
  as the index view.
- **Negative checks.** An occupied coordinate is refused under `staging`, `main`, both
  or no label. Changed bytes at the public coordinate, a missing `main` label and an
  absent record are refused, and an unobserved poststate stays unresolved.
- **Checked on the live registry.** 0.5.0 is free; 0.4.0 is refused as occupied; the
  public poststate of 0.4.0 matches its tested digest.

## UniProt isoforms, deletions and secondary structure (2026-09-27)
uibcdf/sabueso#80, card schema 0.3.6.
- **Deletions are stated, not implied.** A UniProt "Missing" is
  `substitution: {missing: true}` in variants, mutagenesis and alternative sequences.
  An item with no substitution stays what it was: nothing stated. Curation compares a
  deletion as a substitution of its own. Cards of 0.3.5 or earlier that hold such an
  item report a `missing` gap on migration.
- **Isoform links come from the entry.** An alternative sequence names its isoforms
  through the entry's own list (`Sequence=VSP_…`). No isoform is matched by sequence or
  name, and isoform sequences are not built by applying segments: that would be derived
  knowledge, and fetching them is a later step.
- **Secondary structure is positional, with its structures.** It goes to
  `features_positional.secondary_structure`, one item per segment, with the PDB entries
  it was read from. `structure.secondary_structure` stays unwritten, since
  it would drop that basis.
- **A text comment's isoform restriction lives on its SourceAssertion**
  (`source_metadata.molecule`). The published shape of text comments stays a string.
  Structured comments (catalytic activity, subcellular location) keep it in the value,
  as before.
- **Not curatable yet:** alternative sequences and secondary structure, until a
  publication needs to be compared with them.
- **Per-chain secondary structure from RCSB** (added the same day) is a `has_structure`
  qualifier, with the assigning program. A strand shared by two sheets is one segment,
  and sheets are not kept. A chain without any assignment is left out: not stated,
  never coil. `UNASSIGNED_SEC_STRUCT` counts as an assignment, so a chain with only
  unassigned residues is listed, with no helix or strand.

## Knowledge packets, prototype (2026-09-27)
uibcdf/sabueso#71, before the MOLI contract (uibcdf/moli#22) is agreed; the maintainers
chose to prototype first and align after.
- **Two steps.** `knowledge_packet` resolves the cards the query needs. `compose_packet`
  is a pure function of the query and card states: no network, no LLM, no ranking, no
  summary. The same query and states give the same packet.
- **The query decides what is asked.** Aspects map to resolve options through a fixed,
  versioned mapping (`packet_aspects@1`). Keyword arguments are only a resolver and
  source clients. An unknown aspect or constraint is refused.
- **Two ids.** `snapshot_id` hashes the exact packet, retrieval times included, and is
  what `sabueso:packet:<name>@sha256:…` pins. `content_id` leaves out `retrieved_at` and
  `sabueso_version`, and uses each card's content-equivalence id instead of its pin. So
  two assemblies of unchanged knowledge are recognisably the same, which answers the
  finding recorded on #71 (identical knowledge, different snapshot ids).
- **Facts are the views' output, whole,** with their named rules. Quantities are
  `{value, unit}` nodes, read in their own unit. Summaries with references, if size
  demands them, are a later version.
- **Unknowns come from `knowledge_state@2`,** restricted to the areas of the aspects
  asked. Conflicts come from the cards' records, restricted the same way.
- **Stored like decks.** A packet is saved only when every card state it cites is in
  the store, and a read verifies the packet and those states. The new tables do not
  change the store format.
- **Proteins only** in `knowledge_query@1`: a subject and an optional comparator. Decks
  as subjects, and other entity types, wait for real use.

## Biological context of a target, step 1 (2026-09-27)
uibcdf/sabueso#60. Four curated fields, before any connector (VEuPathDB is step 2):
`annotations.stage_expression`, `essentiality`, `accessibility` and `metabolic_role`.
- **Stated text, never categories.** Items hold the words of the publication. A
  phenotype is not classified. "Essential" is kept only as the authors' `call`.
- **Strict items.** Each field has required and optional keys (`CONTEXT_KEYS` in
  `sabueso/core/curation.py`). Anything else is refused, so a misspelt key cannot
  silently become a new kind of statement.
- **Comparison by condition.** Two statements under the same condition are compared:
  method, stage, host and condition for essentiality; compartment, pathway or stage,
  with stage and host, for the others. A different content there `differs`; another
  stage is another statement.
- **The organism is the card's.** No field names an organism. A result on an ortholog
  belongs to the ortholog's card, since identity is never merged.
- **Absence.** An uncurated field is `not_queried` from `Literature` in the knowledge
  state, with the basis `route: curation`, never `not_stated`.
- **Packets** have a `biological_context` aspect: these fields, and UniProt's
  subcellular location, tissue specificity and pathway.
- Free-text claims on these topics stay possible (#43).

## PHI-base, and caching whole releases (2026-09-27)
uibcdf/sabueso#83, the first source of the coverage plan's pathogen gap.
- **Why PHI-base.** Its curated phenotypes of pathogen mutants are keyed by UniProt
  accession, cover eukaryotic pathogens, and are CC BY 4.0 with versioned releases.
- **Releases, not the web API.** PHI-base 5's web API is undocumented. Its releases on
  Zenodo are versioned and checksummed, so the client uses them.
- **Caching only where told.** The first release cache keeps the policy "Sabueso writes
  only where it is told to". By default a release is indexed in memory for the
  process. A cache directory (`cache_dir=`, `$SABUESO_CACHE_DIR`) keeps it on disk,
  each curation session once (the first attempt, one file per gene, took 2.1 GB).
- **One item per phenotype annotation, with the whole genotype.** A double mutant's
  phenotype carries both alleles and is never read as the single gene's. Nothing is
  classified: "Lethal" or "reduced virulence" is PHI-base's statement about a mutant in
  an experiment.
- **"evidence" stays Nextia's word.** PHI-base's `evidence_code` (how the phenotype was
  observed) is kept as `method`.
- **In packets,** the `biological_context` aspect asks PHI-base (`packet_aspects@1`, not
  yet published).

## Clinical layer, step 1 (2026-09-28)
uibcdf/sabueso#81.
- **Trials only through a stated link.** ClinicalTrials.gov names interventions as text.
  Sabueso asks it only for the NCT ids ChEMBL's drug indications cite, and records that
  basis on every `tested_in`. No trial is matched to a molecule by name.
- **Indications keep ChEMBL's terms.** One `investigated_for` per indication, to the
  term's CURIE (`efo:`, `mondo:`, `doid:`…). Two terms with one MeSH heading are not
  merged. The phase is ChEMBL's, per indication.
- **A cited trial the registry lacks** keeps ChEMBL's statement, with `registry:
  not_found`. A cited trial not fetched is listed in `Card.clinical()["not_fetched"]`,
  never treated as absent.
- **Two sources, two assertions.** The ChEMBL indication record supports both
  relationships. The ClinicalTrials.gov study record, with subject `nct:<id>`,
  supports `tested_in`.
- **Migration changes may name the entity types they apply to** (`entity_types`), so a
  protein is not told it lacks indications, nor a molecule pathogen phenotypes.

## DISEASES, gene–disease associations (2026-09-28)
uibcdf/sabueso#82, the first of the human disease-association sources.
- **Channels stay apart.** One `associated_with` per disease, channel and Ensembl
  protein. A curated association and a text-mined co-mention of one disease are two
  statements.
- **Text mining only when asked.** It links names: the human TPI1 is co-mentioned with
  giardiasis because the parasite's enzyme has the same name. The default channels are
  curated knowledge and experiments.
- **Joined through a stated link.** Rows name Ensembl proteins, and a row reaches a card
  only through an Ensembl protein the UniProt entry cross-references, never by gene
  name. The isoform UniProt maps it to is kept.
- **Scores as stated.** Confidence, source score and z-score are DISEASES's, never
  recomputed or ranked.
- **Not applicable is not "not stated".** For a non-human protein the enrichment is
  `not_applicable`, and the knowledge state says `not_queried` with the reason.
- **Versioned by date.** The files are updated in place, so the version is each file's
  publication date, and the cache is keyed by it.
- **Open Targets (same day).** Associations are per Ensembl gene. A row reaches a card
  only when both sources state the gene–protein link: UniProt cross-references the
  gene, and Open Targets lists the entry among its products. Scores (overall and per
  data type) and rank are recorded as stated, with the data version, never recomputed.
  At most 100 associations per gene by default, in Open Targets' order, with the cut
  reported. `associated_with` is identified by source, channel, Ensembl protein and
  gene, so DISEASES's and Open Targets' statements never merge, and a disease under
  two ontologies stays two references.
- **Orphanet (same day).** One `associated_with` per disorder–gene association, to
  `orphanet:ORPHA:<code>`, with Orphanet's association type, status and validating
  publications. Orphanet states each gene's Swiss-Prot accession, so the link is its
  own. The 22 MB file is indexed in memory once per process, and nothing is written:
  its version is only known after downloading, so a disk cache could not be keyed
  before fetching.

## Reactome, and naming Sabueso over HTTP (2026-09-28)
uibcdf/sabueso#83.
- **Pathways as relationships.** `participates_in`, one per Reactome event mapping the
  accession (lowest-level pathways and reactions), with Reactome's ancestors and its
  orthology-inference flag. UniProt's free-text pathway stays a separate statement.
- **One user agent.** DISEASES's downloads and Reactome's Content Service refuse
  Python's default user agent. New clients name Sabueso and its version through one
  helper (`tools/db/_http.py`); older clients move to it when a source starts refusing
  them.

## ClinVar, and placing variants in UniProt numbering (2026-09-29)
uibcdf/sabueso#83; the numbering rule was agreed with the maintainers before building.
- **Found by a stated gene.** Records come from the NCBI Gene id the UniProt entry
  cross-references, never from a gene symbol.
- **Classifications as stated.** The germline classification, its review status and
  the conditions are ClinVar's words. "Conflicting classifications of pathogenicity"
  is ClinVar's own statement, and Sabueso never resolves it.
- **Placing is strict.** ClinVar's `protein_change` lists the change in every
  isoform's numbering, so it never places a variant. A variant gets a UniProt
  position only when two things hold: the record's transcript is one UniProt states
  for its canonical isoform (RefSeq cross-reference, version included), and the
  residue ClinVar names is the UniProt residue at that position. Otherwise the item
  keeps ClinVar's numbering and says why it is not placed. Nothing is placed by
  similarity.
- **Not for diagnosis.** The docs repeat ClinVar's own warning.
- **gnomAD (same day)** follows the same placement rule, through an Ensembl transcript
  UniProt states for its canonical isoform. gnomAD's transcript ids carry no version,
  so the residue check guards against a changed sequence. Only variants with a protein
  change are kept, and the others are counted. Frequencies (`ac`, `an`, `af`) are kept
  as stated, per exomes and genomes. The placement code is shared (`mappings/_hgvs.py`).

## Placing a change stated on another isoform (2026-09-29)
Agreed with the maintainers as a second pass for the variants of #83.
- **Rule `uniprot_isoform_map@1`.** Each step is a UniProt statement:
  - which isoform a transcript encodes (Ensembl and RefSeq cross-references);
  - how that isoform differs from the canonical sequence (its `VSP_` edits).

  Applying the edits gives a map from isoform positions to canonical ones. The
  residue must still match. The item records `placed_via` (rule, isoform, isoform
  position).
- **An isoform's own segment has no canonical position** (`isoform_specific_position`).
  For TPI1 this accounts for 184 of the 189 gnomAD variants the first pass left out:
  they lie in the 37 residues isoform P60174-3 adds at its N-terminus. Placing them by
  alignment would have been wrong.
- **Alignment is not used.** It is kept as a possible last resort, with its own rule,
  for isoforms UniProt does not describe by edits (#85).
- More precise reasons for what is not placed: `unparsed_protein_change` and
  `stop_codon`, besides `residue_mismatch`.

## Declared enrichers (2026-09-29)
uibcdf/sabueso#86, wave 3 of #83.
- **One contract, one runner.** A source's contribution to a card is declared once.
  The runner applies organism coverage, `not_found` and `error` per request, and a
  fixed order. An enricher's `map` returns its record's outcome, so each source's
  records stay exactly as before.
- **Tables are derived, not kept by hand:** the knowledge-state rows
  (`knowledge_areas`) and the migration map of records to options
  (`options_by_source`). A test checks that each enricher has its parameters,
  digesters and registry entry.
- **Behaviour-preserving steps.** Each step is checked by comparing whole cards
  (snapshot ids and records) before and after, not only by the test suite.
- **Bespoke, for stated reasons:** RCSB structures, the ChEMBL/BindingDB/PubChem
  BioAssay group, and NCBI Gene in the resolution.
- **Step 2 (same day).** STRING, PDBe-KB (ligand sites, interfaces), AlphaFold DB,
  NCBI Taxonomy and InterPro became enrichers. They run in declared stages among the
  bespoke enrichments, so the order of records (part of a card's content) does not
  change. Only the RCSB, ChEMBL, BindingDB and PubChem BioAssay blocks remain in
  `resolve_protein_card`.
- **Step 3 (same day): shared services.**
  - Every client reaches the network through `tools/db/_http.py`: Sabueso's user
    agent, and at most two retries with backoff for 429, 502, 503, 504 and refused
    connections. Timeouts are not retried, since a retry would multiply a slow
    source's cost. Other errors reach the client unchanged, so "not found" stays an
    answer.
  - Release sources share `_release`: memory by default, disk only when told, atomic
    writes, checksums.
  - Keys belong to the user and to a service (`SABUESO_<SERVICE>_KEY`). A card does
    not record whether a key was used: an optional key changes the rate, not the
    answer. A missing required key is `not_queried` (`MissingKeyError`). NCBI is the
    first user, with its optional key.
- **Step 4 (same day): packet options are derived.** An aspect asks every declared
  enricher that answers one of its knowledge areas. The rule: a packet never reports
  as "not queried" what its own aspects could have asked. `packet_aspects@1` is
  unpublished (packets are not in 0.5.0), so its two gaps were corrected in place:
  `structures` now asks AlphaFold DB, and `sequence_features` asks InterPro. Functional
  association (STRING) is not an aspect yet.
- **Step 5 (same day): parallel fetching is deferred (#87).** Measured online: the
  declared enrichers are 18.8 s of a 39.5 s card for HsTIM, and 6.3 s of 34.9 s for
  TcTIM. Concurrency would save at most about a quarter of a card's time, at the cost
  of thread safety and gentler use of rate-limited sources. #87 states when to
  re-evaluate. ClinVar, the slowest, now also takes the optional NCBI key.


## A cut never passes for the whole answer (2026-09-29)
- **The gap.** STRING states no total. With its default limit of 50, a card kept
  HsTIM's 50 most confident partners (of 78 at score ≥ 700), and nothing said so.
- **The rule.** Every source whose answer Sabueso limits must report the cut:
  - with the source's total where it states one (ChEMBL, Open Targets, ClinVar,
    gnomAD);
  - otherwise by asking for one record more than the limit. STRING's cut is then
    recorded as `truncated`, and reported as "50 of more than 50".
- **Where it shows.** The public envelope (`get_partners`) carries `truncated` too.
- **Fixtures.** Some are declared cuts of a larger answer (`temp_data/NOTICE.md`), so
  building cards from them reports truncation. That is the fixture stating what it is,
  not a failure.
- **Defaults: everything, up to a ceiling** (same day, #88). Each source is asked for
  everything it states about an entry, up to 5000 items: ChEMBL, STRING, Open Targets,
  ClinVar, gnomAD, ClinicalTrials.gov. The previous defaults were 50 to 1000, and they
  hid knowledge by default. The ceilings are listed on the data-sources page, read from
  the code. UniProt's name search stays at 500 candidates on purpose: more is ambiguity,
  and the resolution records it. Card size and time are watched in #88.
- **Where sources are documented.** The data-sources page, generated from the registry,
  is the one list of sources in use, their access and licence, their ceilings, and the
  sources set aside or blocked, each with its reason.

## Gaps in the knowledge state, found by the 0.6.0 release (2026-09-29)
- **A cut is partial** (`knowledge_state@3`, #88). A source whose answer was cut at a
  limit read as `known`, although its record and a warning said `truncated`. The row
  is now `partial`, and `basis.truncated_for` names the requests that were cut, as
  `unavailable_for` and `incomplete_for` already do for failures. It is a new rule
  version: packets and views built from now on cite `@3`.
- **"Not stated" carries its release** (#89). `RecordNotFoundError` takes the release
  the client consulted (`version=`), and the enricher runner records it in the
  `not_found` record. The row then reads "not stated by Reactome at release 97". PHI-base,
  Reactome, Orphadata and Open Targets pass it. A source that states no release still
  records `not_found` without one.

## SKEMPI 2.0: interface mutations, joined and placed only on stated grounds (2026-09-29)
uibcdf/sabueso#83, wave 2, first of the interface sources. Card schema 0.3.7.
- **Join.** A SKEMPI row names a PDB entry and the chains of each side (`1BRS_A_D`).
  It joins a protein card only when UniProt states that one of those chains is the
  protein (the PDB cross-reference's `Chains`). The protein names SKEMPI writes are
  kept as text and never used to join.
- **Placement** (`rcsb_author_numbering@1`). Mutations are in the entry's author
  numbering. One is placed in UniProt numbering only through the author numbering RCSB
  states for that chain (#73), of a structure the card holds, and only when its residue
  matches. Mutations on the partner stay in author numbering (`partner_chain`).
  Barnase is the test: its author numbering is the mature protein's, 47 positions from
  UniProt's.
- **As stated.** Affinities, kinetics, thermodynamics and temperature are quantities in
  the units SKEMPI states. A bound keeps its relation, "n.b." is `no_binding`, and an
  assumed temperature is flagged.
- **ΔΔG is derived, never stored** (`binding_ddg@1`, in `Card.interface_mutations()`).
  It is computed from the stored affinities and temperature, and is a bound when an
  affinity is one.
- **Version.** The file states only the database version, 2.0, while the site reports
  later corrections. Each enrichment records the file's SHA-256.
- **Packets.** The `oligomer` aspect now also covers interface mutations. That changes
  what a published mapping asks, so it is `packet_aspects@2`. A test pins each
  version's options: aspect options are derived from the enrichers, and a new enricher
  must never change a published version silently.

## iPPI-DB is blocked (2026-09-29)
- Its compound pages state targets (UniProt), activities and InChIKeys, but only as
  HTML. The CSV export holds SMILES only, and the REST API covers structures, cavities
  and hotspots.
- No data licence was found on the site. The registry's earlier "CC BY-SA 3.0" could
  not be confirmed, and may have been the article's licence.
- Reading HTML pages is fragile and, without terms, not redistributable. It waits on the
  maintainers (#84).

## The disease as an entity, anchored at MONDO (2026-09-29)
uibcdf/sabueso#90, step 1. Card schema 0.3.7.
- **Why MONDO.** Six sources name diseases with different ids (DOID, EFO, MONDO,
  ORPHA, MIM, MeSH). MONDO integrates those terminologies and states, term by term,
  which external ids are the same disease (`MONDO:equivalentTo`). In release v2026-09-01
  that is 118,297 equivalences over 36,015 terms, each external id to exactly one term.
- **Identity** (`mondo_equivalence@1`). An external id resolves only through a stated
  equivalence. The resolution records the statement and the release. Other xrefs are
  related terms, kept apart (`identifiers.related_ids`) and never read as identity:
  for example, EFO:0001360 is cited by MONDO's type 2 diabetes term only as the source
  of other xrefs, so it does not resolve.
- **Obsolete terms are not followed.** The replacement MONDO states is named as a
  candidate. A replacement can be a merge or a split, and whoever cites the old term
  decides.
- **Routing.** Disease namespaces go to disease cards. `omim:` and `mesh:` also number
  genes and chemicals: those find no equivalence and are reported as not found, never
  as a disease.
- **Next steps (#90):** relate the diseases on protein and molecule cards through these
  equivalences, then disease → targets.
- **Step 2 (same day): a protein's diseases, grouped.** `disease_identity` asks MONDO
  about every disease id the other sources put on a protein card: associations,
  UniProt's MIM numbers, and ClinVar's condition ids. Each stated equivalence becomes a
  `same_as` relationship to the MONDO term, backed by a MONDO SourceAssertion.
  `Card.diseases()` groups the statements through those relationships, or when they
  name the same id (`disease_grouping@1`). Nothing else groups, not even an identical
  name. For HsTIM, triosephosphate isomerase deficiency is one disease stated by five
  sources. MedGen concept ids and some EFO terms stay apart, with their reason. In the
  glossary (`entities()`), those ids are diseases, anchored at their MONDO term.
- **Step 3 (same day): ClinVar conditions, MedGen, placeholders.** A first run left 272
  ClinVar statements ungrouped for HsTIM. They were 18 MedGen concepts, and most
  statements were not an identity problem:
  - **One condition is one statement.** ClinVar states that a condition's ids (MedGen,
    OMIM, Orphanet, MONDO…) name it together. Treating each id as a statement had
    left TPI deficiency's MedGen id apart from its own MONDO id. A condition now joins
    a disease when any of its ids does, and ids that reach two terms are
    `conflicting_identity`, both listed, neither chosen.
  - **Placeholders are not diseases.** ClinVar's "not provided" (MedGen C3661900) and
    "not specified" (CN169374) are `condition_not_provided`, 153 of the 272.
  - **MedGen as a source, not a scheme rule.** MONDO states equivalences to MedGen
    records by UID, not by concept id. Reading a MedGen concept id as a UMLS CUI would
    rest on a naming convention that no record states. Instead, MedGen states, record
    by record, the UID of each concept id (`medgen_concept@1`), and MONDO's equivalence
    completes the chain. On HsTIM, both alternatives grouped the same 9 concepts,
    without a single disagreement. The stated route was kept.
  - **Result, live HsTIM:** of ClinVar's conditions, only 6 phenotypic traits have no
    stated equivalence. Three conditions are reported as conflicts: ClinVar gives a
    broader Orphanet id next to a subtype's MONDO and OMIM ids. Telling that granularity
    difference apart with MONDO's hierarchy is a possible next rule.
- **Step 4 (same day): from a disease to its targets and its drugs.**
  - `disease_targets` (`disease_targets@1`) takes Open Targets' associated targets
    (asked by the MONDO id, then its EFO equivalents) and Orphanet's genes of the
    disorder (by its Orphanet equivalents). Each member is a Swiss-Prot product the
    source states for the gene, and its basis lists every statement that brought it.
  - `disease_drugs` (`disease_drugs@1`) takes the molecules whose ChEMBL indications
    name the disease by its MONDO id or its EFO and MeSH equivalents, ordered by
    ChEMBL's phase.
  - **A lower default for decks (50).** Enrichments ask for everything up to 5000
    (#88), but a deck member is a whole card, at least one request: five protein cards
    took about 50 s live. The cut is recorded (`excluded`, reason `limit`) and
    reported, and `limit` asks for more.

## What may be done with the knowledge: a first milestone (2026-09-29)
uibcdf/sabueso#29.
- **Terms are the sources' statements, recorded per source** in the registry (`terms`),
  with the URL of the statement and a review date. They are not SourceAssertions: their
  subject is the source, not an entity. Granularity is the source, except where the
  source states that terms vary per record (PubChem BioAssay's depositors, a curated
  statement's publication). Those are `unknown` until they are recorded per record.
- **Three verdicts:** `allowed` with obligations, `restricted` with the reason, and
  `unknown` with the reason. Unknown is never "no restriction".
- **An item remains when one allowed source states it.** Each statement stands on its
  own, so a value two sources state survives the loss of one of them.
- **Derived knowledge** is recomputed from what remains, and carries the obligations
  of the statements it is computed from; the strictest governs (`terms_propagation@1`).
- **The disclaimer lives in the returned report.** It is a report for a person's
  decision, not legal advice.
- **Answering the acceptance question.** For the *T. cruzi* enzyme with ChEMBL,
  BindingDB and PubChem BioAssay, 272 of 527 measured molecules may be used in a
  commercial product (attribution, share-alike); 255 are known only from PubChem
  BioAssay and are `unknown`.
- **Terms profiles** (same day, #94). `terms="commercial"` or `"non_commercial"` builds
  knowledge only from sources whose stated terms are `allowed` for the profile's use
  (`commercial_product`, `academic_publication`).
  - Named by use, not by institution.
  - A project that may end in commercial exploitation is `commercial` from its first
    day: knowledge that informed a decision cannot be un-used later.
  - Unknown terms are excluded too, with their reason. In a commercial project a wrong
    green light is worse than an exclusion.
  - The card keeps the profile (`quality.terms_profile`, `terms_profile@1`), so a
    packet or a Nextia decision knows under which terms its knowledge was gathered.
  - Curations the user applies are the user's, and are not filtered.
  - Today almost every source in use allows commercial use. The profiles differ through
    sources with unknown terms, and `non_commercial` would let us reconsider sources set
    aside for a non-commercial licence, such as DrugBank's clinical content.
- **Terms per record: PubChem BioAssay by depositor** (same day, #94).
  - A PubChem BioAssay result keeps its depositor's terms. The registry names the
    depositors whose terms are known (ChEMBL, BindingDB: their assays in PubChem are
    copies of their records).
  - Each result is judged by its depositor's terms, and the report says so
    (`PubChem BioAssay (deposited by ChEMBL)`, with its basis). Other depositors stay
    `unknown`.
  - Profiles now ask PubChem BioAssay and keep each result whose depositor's terms
    allow the use. The others are counted (`excluded_records`).
  - The depositor comes from each relationship's `assay.depositor`, so cards stored by
    0.6.0 are judged the same way.
  - For TcTIM with ChEMBL, BindingDB and PubChem BioAssay, all 527 measured molecules
    now remain for a commercial product, with attribution and share-alike. The first
    milestone reported 255 of them as `unknown`.
- **Scientific operations: navigate, explain, as of** (same day, #91).
  - `expand(card, predicate)` follows relationships into a deck of the related
    entities' cards (`relationship_expansion@1`). A member is one entity: refs that
    resolve to the same card are merged, and the basis keeps every statement and its
    SourceAssertions. Merging relies on the stated identity that resolution already
    uses, never on similarity.
  - What cannot be followed is excluded with its reason (`no_card_type`,
    `not_resolved`, `limit`). A related entity without a card type is not dropped.
  - Each member is a whole card, so expansion is capped (50 by default). The entities
    with the most statements are followed first, and the cut is reported as a
    truncation.
  - One name, `expand`: the `neighbors` of the roadmap would only have been a second
    spelling. The reserved `Card.expand(kind)` now takes a predicate.
  - `explain` answers from what is recorded: a deck member's basis and the deck's
    operations, and a card's SourceAssertions. It does not re-run anything.
  - `as_of` reads the store's revisions only. Sabueso does not reconstruct a source's
    past: knowledge on a date is what was built and saved by then.
- **Molecules given as a structure** (same day, #93).
  - A `smiles:` or `inchi:` query is matched by PubChem, and the card is the compound
    PubChem names, anchored at the InChIKey PubChem states
    (`pubchem_structure_lookup`). Sabueso never computes a key from a structure: that
    would make identity depend on a toolkit and its version.
  - A structure PubChem does not hold (CID 0) is `not_found`; one it cannot read (HTTP
    400) is `unsupported`, with PubChem's message; several CIDs are `ambiguous`.
  - Stereochemistry, tautomers and salts are as PubChem handles them. A SMILES without
    stereocentres names the compound with undefined stereochemistry, which is a
    different card: vincristine's flat SMILES resolves to CID 3717450, not 5978.
  - The lookup is the resolution's basis (`decision["structure"]`, with the structure
    as given), not a SourceAssertion: the card is about the compound, and the query is
    the user's.
  - A computed key, as a flagged derived identity under a named rule, waits for a
    stated need.
- **A disease named at two granularities** (same day, #90). On HsTIM, three ClinVar
  conditions reached two MONDO terms and were reported as `conflicting_identity`.
  - MONDO's hierarchy tells them apart. `disease_identity` asks MONDO, for the terms one
    statement reaches, whether one is under the other. It records each chain as
    `subclass_of`: each `is_a` step is a MONDO SourceAssertion, and a chain of several
    steps is derived (`mondo_hierarchy@1`). Only terms met together in one statement
    are related. Relating every term a card reaches recorded 1,107 relationships on
    HsTIM, most of them to broad terms such as "hereditary disease"; asking by
    statement records 3.
  - The statement joins the **broader** term, with the narrower one in `narrower`.
    Joining the most specific term looked natural, and it was right for two of the
    three conditions (Klippel-Feil syndrome 3, familial tumoral calcinosis 1). The
    third was ClinVar's "Obesity", named with the Orphanet id of obesity due to MC4R
    deficiency. What holds for a subtype holds for the disease it belongs to; the
    reverse is a claim no source made.
  - Terms of which neither is under the other (two subtypes) stay a conflict.
  - `disease_grouping@1` has not been released, so it keeps its version, with
    `granularity: mondo_hierarchy@1` among its parameters.
- **How each statement entered** (same day, #92, step 1). Every SourceAssertion
  records `acquisition`, a new optional key in card schema 0.3.7.
  - Methods: `database`, `curation`, `rule_extraction` and `model_extraction`, plus
    `validated_by` on an extraction. An extraction must name its tool and version: a
    statement whose extractor cannot be named cannot be reproduced or weighed.
  - How a database obtained its own record is the database's statement, recorded as
    `origin` only when the source states it. Today that is DISEASES's text-mining
    channel (`text_mining`). STRING's links combine channels, text mining among them,
    in one score, so no single link can be marked.
  - Acquisition is recorded, not inferred. SourceAssertions of older cards read as
    `not_recorded` until a refresh; a migration within a line does not rewrite them.
  - It says how a statement entered, never how true it is. Weighing a statement for a
    project remains Evidence, in Nextia.
  - The key is not in MOLI's conceptual SourceAssertion schema. It was proposed
    there (uibcdf/moli#32), and Sabueso's use is additive.
- **Europe PMC: stated accessions only** (same day, #92, step 2).
  - Europe PMC mines abstracts and open-access full texts for accession numbers. A
    search `ACCESSION_ID:<acc> AND ACCESSION_TYPE:uniprot` finds the articles whose text
    states the accession: 354 for HsTIM. The id is written by the authors, so a
    mention is identity by statement. It becomes `mentioned_in` (protein →
    publication). It says the paper names the entry, never what it states about it.
  - Its gene and protein annotations are not used. They ground a name without the
    organism: in a paper on the human TPI deficiency, "triosephosphate isomerase" is
    tagged with a yeast entry (Q9C401). That is identity by name.
  - Acquisition: a source that serves text-mined records is `database`, with
    `origin: text_mining`, as DISEASES's text-mining channel is. `rule_extraction` and
    `model_extraction` are kept for extractions whose tool and version are known,
    because Sabueso or its user ran them. Europe PMC states no version of its tagger,
    only of its service (6.9), which is recorded as the release.
  - Terms: EMBL-EBI places no restrictions of its own and expects attribution. Each
    article keeps its licence, so only ids and bibliographic data are kept, never text.
  - Not asked by a packet aspect yet. A well-studied protein has thousands of
    mentions, and packet size is watched (#88).

## Knowledge packets: the name, and references instead of copies (2026-09-30)
uibcdf/sabueso#88.
- **The name stays `KnowledgePacket`.** Alternatives were weighed: *brief* and
  *dossier* collide with MOLI's scientific communication (ProjectBriefings,
  ProgressBriefs, dossiers); *slice* and *bundle* already name integration slices and
  deployment bundles; *answer* pairs well with `KnowledgeQuery` but reads as a
  conclusion; *excerpt* was the closest fit. A packet is not a deck: a deck holds whole
  cards, a packet the facts a query asks, with unknowns, conflicts and provenance.
- **`knowledge_packet@2`: each statement once.** In a TcTIM/HsTIM packet with every
  aspect, the joint structure inventory copied each protein's structures field for
  field (31 of 31), and grouped disease statements copied the associations and ClinVar
  conditions of the same aspect. Both now name what they refer to. Associations and
  pathways carry their `relationship_id`, and ClinVar statements their condition index.
- **Measured.** The same cards give 2.04 MB instead of 2.25 MB (−9 %): structures
  halve (288 → 151 KB), diseases −11 % (most groups hold a single Open Targets
  statement). The rest is content, not repetition. Reducing it is a decision about
  what a packet is for (a declared level of detail, or a compact encoding), taken
  apart.
- **Formats are not compared.** `@1` packets are still read. A revision of another
  format has `knowledge_changed: None`, and `same_knowledge` answers None: the ids of
  two formats differ even when the knowledge does not.

## Ceilings for BindingDB and PubChem BioAssay, and PubChem by target (2026-09-30)
uibcdf/sabueso#98, #88.
- **The ceiling held everywhere but here.** Every source stops at 5000 records and
  reports the cut, except BindingDB and PubChem BioAssay, which fetched everything. For
  EGFR that meant 32,346 BindingDB records (16,463 UniChem lookups, one at a time) and
  6569 PubChem assays (one request each, some primary screens of tens of MB): a card
  that would not finish. Both now keep 5000 by default, and record and report a cut.
- **Which records are kept is a named rule**, recorded in the enrichment (card schema
  0.3.8, since 0.3.7 is published).
  - `bindingdb_record_order@1`: by monomer id, affinity type and value. It is only
    deterministic; every BindingDB record has a value.
  - `pubchem_row_order@1`: confirmatory rows with a value, then other rows with a value,
    then rows without one; each by AID and SID. A cut keeps measurements before
    screening outcomes.
- **PubChem by target.** `assay/target/accession/<acc>/concise` returns every result of
  a protein in one request, with the same columns as an assay's table. For TcTIM it
  gives exactly the 493 rows of the 13 assays fetched one by one. For EGFR it takes
  about 21 s instead of more than 27 minutes. Rows of another protein in a multi-target
  assay are left out, as before.
- **BindingDB's monomer → CID file is not an identity route.** It is fast (97.7 % of
  EGFR's monomers, 200 InChIKeys per PubChem request), but a PubChem CID is PubChem's
  standardized compound. On a sample, 5 of 52 differed from the InChIKey UniChem states
  for BindingDB's structure: a stereo layer, a tautomer, or another compound. Identity
  stays with UniChem. BindingDB's monthly TSV, which states its own InChIKey per row,
  is the candidate for heavy use (#98).
- **Polite concurrency for one-record-per-request services** (same day, #98, #87).
  UniChem has no batch query and states no rate limit. `_http.gather` asks it with four
  threads at most, and `Pace` starts no more than five requests per second, the pace
  PubChem states for itself. The pace belongs to the online client (`workers`,
  `per_second`), so saved answers in tests run unpaced. For EGFR, 1769 BindingDB
  monomers took 635 s instead of about 40 minutes: UniChem's latency (about 1.4 s),
  not the pace, is the limit. A cache of lookups would remove repeated ones, but it is
  a raw-payload cache, an open question of `CACHE_POLICY.md`, and is proposed apart.
- **RCSB entries in batches** (same day, #98). The Data API answers `entries(entry_ids:
  [...])` with the same fields as one entry, and leaves out an entry it does not hold.
  Sabueso asks 25 per request. An entry an error touched is asked alone, so the
  partial-entry fallback of #74 still applies to it; a batch that fails as a whole is
  asked entry by entry. A client without `fetch_structures` (saved entries, a user's
  client) is asked one entry at a time. Live, 40 EGFR entries gave a card with the same
  content id as one-at-a-time, in 5.6 s instead of 13.1 s.

## What was downloaded: a retrieval archive, mirrors and access modes (2026-09-30)
uibcdf/sabueso#100, uibcdf/moli#33. Direction adopted; not yet built.
- **Why the policy changes.** Sabueso stored no raw payloads. MOLI's reproducibility
  policy asks every external retrieval to keep what it returned when the licence
  allows, and to say so when not. Repeated builds re-fetch the same answers (#98), and a
  project should be able to work offline and on one release.
- **Three layers, not one cache.** A retrieval archive (what was downloaded), local
  source mirrors (whole releases with an update policy), and the knowledge store (what
  was known). Reusing a fresh archived answer replaces a separate lookup cache.
- **Three users.** An independent user sees no change by default: online, nothing
  written. UIBCDF's research use gets mirrors on a lab machine and archives per project.
  MOLI gets shared mirrors and per-project archives feeding its InputManifest and
  KnowledgeSnapshot.
- **Order.** #99 first; then the archive with replay and freshness; then the mirror
  manager (ChEMBL and BindingDB first); then MOLI's platform side.
- **Licences decide retention.** The registry's terms gain `retention` and `mirror`.
  What cannot be kept keeps its hash and is marked `retained: false`.

## Knowledge store format 2 (2026-09-30)
uibcdf/sabueso#99.
- **When a statement was read belongs to the state, not to the row.** A SourceAssertion
  row is its content without `retrieved_at`, which `card_sa` keeps per state (through
  `retrieval_times`: a card holds few distinct times). A card rebuilt with unchanged
  knowledge shares every row with its previous revision. Pinned ids do not change: the
  snapshot id is computed on the whole card, before storage, and every read rebuilds and
  checks it.
- **Integer keys.** Membership rows repeated two long hex keys, in the table and in
  each index (~150 bytes a row). States and rows are now numbered, and membership
  tables are `WITHOUT ROWID`.
- **Compression.** Documents and rows are zlib-compressed; ids are computed on the
  canonical JSON, never on stored bytes. A row read as text is format 1's.
- **Measured** on a live pilot store: 15.4 MB (format 1) to 4.7 MB (format 2); saving
  both cards again with unchanged knowledge adds 0.2 MB instead of about 5 MB.
- **Upgrade in place.** Format 1 rows are copied as written, and old tables dropped. A
  Sabueso that reads only format 1 refuses format 2 with its message.
- **The archive sits at `_http.urlopen`** (same day, #100, phase 1, first step). Every
  client already goes through it, so one hook archives the answers of all 23 sources,
  their headers and 404s included, without touching each client. `gather` runs each
  request in a copy of its caller's context, so concurrent lookups are archived too.
  A record's reference hashes what was asked, the answer's status, headers and
  content hash, and when; the content is stored once per SHA-256. A card lists the
  records its build made. Retrieval times still come from each client's clock, so
  replay waits for the next step: taking them from the answers.
- **Replay and reuse; times from the answers** (same day, #100, phase 1).
  - A client dated its answers with its own clock before asking, so a replay would
    have dated statements at replay time. Clients now open a stamp (`_http.stamp`,
    35 sites changed mechanically) whose value is the time of their first answer
    when an archive is active. A recorded statement and its record agree, and a
    replayed one keeps its original time.
  - `replaying(of=card)` follows the card's build: a request answered twice (UniProt's
    entry is fetched by the resolver and again by the card tool) gets its two answers,
    in order. Without `of`, the latest record answers. Live, TcTIM's build replayed
    without the network in 4.4 s and gave an identical card.
  - A request the archive does not hold raises `NotArchivedError`, a
    `ConnectorError`, so every client path handles it. `sabueso.resolve` turns those
    records into `not_queried` (`not_in_archive`).
  - `reusing(max_age)` is the design's `archive_first`: an answer archived within
    `max_age` is used, anything older is asked and kept.
- **Answers attributed to their source; retention from the licence** (same day, #100).
  - Several sources share a service (RCSB PDB and PDB CCD one GraphQL endpoint;
    PubChem and PubChem BioAssay PUG REST; ClinVar, MedGen and NCBI Gene E-utilities),
    so a URL cannot name the source. The client says it: `stamp(source)`, with the
    name its SourceAssertions carry; a test checks every name has recorded terms.
  - Retention is derived when read, from the licence (`retention_from_licence@1`), so a
    change of policy never rewrites the archive. Per-record terms (a depositor's, a
    publication's) and unrecorded ones are `keep: internal`, `share: unknown`.
  - A statement links to its source's answers in the build (`explain`, basis
    `source_in_build`), without threading record ids through clients and mappings.
  - Replay made visible that UniProt's entry was read twice per protein build. The
    resolver now keeps the entries it read for the card tool; the second request is
    gone.
  - A replay's missing answer is not a failure, and no longer warns as one.

## Local mirrors, BindingDB first (2026-09-30)
uibcdf/sabueso#100 (phase 2), #98.
- **Manager.** `sabueso.mirrors`: install, status, update (`manual`, `notify`, `auto`
  keeping the previous releases), remove; releases side by side under a directory the
  user names; `using()` makes card tools read installed mirrors (`mirror_first`) or
  never the network (`offline`). A card records the access route and release.
- **BindingDB first**: its monthly TSV (about 600 MB) with a published MD5 was indexed
  by UniProt accession in 154 s (3.65 M records, 704 MB). ChEMBL, several GB, next.
- **Parity with the service**, measured: identical for TcTIM and HsTIM; for EGFR the
  service rounds values the release states with more precision (2,876 records), and
  about 0.2 % of records differ between the live service and the monthly release.
  Both are recorded: a card names its access and release.
- **The release's InChIKeys are not an identity anchor.** For 39 of 112 sampled EGFR
  monomers they drop the stereo layer that UniChem's standard key keeps (one names
  another compound). Anchoring on them would merge stereoisomers, so identity stays
  with UniChem; repeated lookups are saved by `archive.reusing(...)`.
- **Offline** refuses every request not answered by a mirror or an archive
  (`OfflineError`), and the source is `not_queried` (`offline`), never absent.

## ChEBI: classes and roles of a molecule (2026-09-30)
uibcdf/sabueso#83 (wave 2, chemistry).
- **Joined on stated grounds only.** UniChem lists a structure's ChEBI ids; ChEBI states
  each entry's standard InChIKey. An entry becomes part of a card like any other record
  keyed by its stated InChIKey (`build_molecule_cards`), so an entry whose key is
  another is never merged.
- **Batched.** ChEBI 2.0's `compounds/` answers up to 200 ids per request (about 12 s),
  and a secondary id with its primary entry.
- **Roles, direct or inherited.** `roles_classification` lists every role ChEBI
  classifies an entry with, including those it inherits through its classes and parent
  roles (vincristine is a "Bronsted base" through "tertiary amino compound"). Both are
  kept, and `direct` marks the entry's own `has role` statements, so a reader never
  takes an inherited role for a curated one.
- **The definition's markup** (`C<sub>46</sub>…`) stays in the assertion, as written;
  the field's value is its plain text (`normalized_value`).
- Names and formula are not taken: ChEMBL and PubChem state them already, and a second
  spelling would add disagreements without knowledge.

## gnomAD's consequence on the canonical transcript (2026-09-30)
uibcdf/sabueso#85, found while evaluating Ensembl for wave 2 of #83.
- **Ask the source that states it.** Asked for a gene, gnomAD states each variant's
  consequence on the one transcript it ranks most severe. Asked for a transcript, it
  states each variant's consequence on that transcript, with its version, in one
  request (EGFR: 5,942 variants, 3 s). Sabueso now asks for the gene and for each
  Ensembl transcript UniProt states for the canonical isoform.
- **The canonical statement comes first.** A protein change gnomAD states on the
  canonical transcript is kept as stated, and the residue check still applies. A
  variant gnomAD states changes no residue there (intron or UTR) is not placed
  (`not_coding_on_canonical`) and records that consequence, even where UniProt's
  isoform map would place it: the same DNA change can shift a residue on one isoform
  and none on the other. For TPI1, a frameshift at isoform 3's Pro40, which the map
  had placed at canonical Pro3, is a 5' UTR duplication on the canonical transcript.
- **What it changed**, over nine genes: the variants on transcripts UniProt does not
  state fell from 810 to 533 (MAPK14 12 → 0, EGFR 161 → 88, BRCA1 83 → 38), and 328
  are now stated as not coding on the canonical transcript.
- **What is left, checked variant by variant** (same day), on 22 human proteins: the
  nine above; glycolytic enzymes (GAPDH, PGK1, ENO1, ALDOA, LDHA, PKM); genes with
  hard isoforms (CDKN2A, MAPT, APP, CD44); BRAF, PRKDC and ATM. That is 52,928
  protein changes. gnomAD's variant query states every transcript a variant has a
  consequence on. For all 1,682 changes left on transcripts UniProt does not state,
  it states no protein change on the canonical transcript:
  - 1,205 are intronic (1,191) or in the 3' UTR (14) there. The transcript query
    covers the coding region with a margin, so it does not return them.
  - For 477, gnomAD states no consequence on the canonical transcript at all. They
    lie outside it: TP53's alternative 3' exons, and CDKN2A's exon 1β of p14ARF,
    another UniProt entry.
  - None is coding on the canonical transcript.

  They are changes on other proteins or on other exons: PKM's alternative exon, and
  MAPT's exons the canonical transcript skips.
- **Ensembl adds no stated map for them.** For the transcripts left, Ensembl states a
  separate TrEMBL entry (e.g. Q504U8, E7EQX7) or no translation any more, so there is
  no stated route to canonical positions. Alignment (#85 step 2) is not built: it
  would place changes of other exons and other proteins on this one.
- **Only transcripts gnomAD annotates are asked.** UniProt may cross-reference Ensembl
  transcripts newer than the dataset's GENCODE release (ENO1: 17, of which gnomAD
  annotates one). gnomAD's gene record lists its transcripts, so a request is sent
  only for those. The others are recorded as `not_in_dataset`, and the gnomAD
  service's rate limit is not spent on them.
- **A transcript UniProt names no isoform for is not the canonical one** in an entry
  that describes isoforms. CD44's ENST00000442151 (a 294-residue protein) was taken
  as canonical; the residue check stopped its 3 changes. Such a cross-reference is now
  canonical only in an entry without isoforms (`_hgvs.transcript_context`).
- `uniprot_isoform_map@1` stays for ClinVar, and for a gnomAD variant the canonical
  answer does not state.

## KLIFS: kinase pockets and conformations (2026-09-30)
uibcdf/sabueso#83 (wave 2, family-specific sources).
- **Joined through the accession KLIFS states.** KLIFS's kinase list states each
  kinase's UniProt accession (1,127 kinases, human and mouse, one request per process).
  A protein with two kinase domains is two KLIFS kinases (JAK1 and JAK1-b), and the card
  holds both.
- **What a card gains.** For a kinase:
  - the classification (group, family, subfamily);
  - per structure, the conformation KLIFS assigns (DFG in, out or out-like; αC helix
    in or out), the orthosteric and allosteric ligands, and the quality;
  - the 85 pocket positions in KLIFS's common numbering (gatekeeper `GK.45`, hinge,
    `xDFG`).

  Type I and type II inhibitors differ by DFG state, and the pocket positions compare
  across kinases.
- **The pocket in UniProt numbering, through statements only.** KLIFS states the
  pocket residues in one structure's author numbering. The structure is chosen by
  `klifs_pocket_reference@1`, among the kinase's structures the card holds with RCSB's
  author numbering. The order is:
  - a pocket equal to the kinase's (no mutation, no gap);
  - then the highest quality score;
  - then the fewest missing residues and atoms;
  - then the best resolution;
  - then the lowest KLIFS id.

  It is placed with `rcsb_author_numbering@1`, and the residue must be UniProt's. No
  sequence is aligned. For EGFR the gatekeeper is T790, the residue of the T790M
  resistance mutation, so the pocket joins the variant annotations by position.
- **One request per kinase for the pocket.** `interactions_match_residues` answers one
  structure at a time. One structure is enough to place the kinase's 85 positions; if
  another structure's numbering disagreed, the residue check is the guard. Without a
  structure on the card, the
  pocket stays in KLIFS numbering (`no_structure_loaded`), and no pocket request is
  sent.
- **Terms.** No formal licence was found. The FAQ states the data is free and open for
  academia and industry, and asks to be cited. The registry records it as no
  restrictions of its own, with that caveat (`RISKS_AND_OPEN_QUESTIONS.md`).
- **In packets since `packet_aspects@3`** (2026-10-01): classification in
  `identity`, conformations in `structures`, pocket in `ligand_sites`.
- **Not taken now:** KLIFS's interaction fingerprints per structure (one request each),
  its ligand bioactivities (ChEMBL's, already on the card) and its drug list.

## GPCRdb: GPCR numbering and structure states (2026-09-30)
uibcdf/sabueso#83 (wave 2, family-specific sources).
- **Joined through the accession GPCRdb states.** One request finds the receptor of a
  UniProt accession (`protein/accession/<acc>`), and two more read its residues and
  structures. A protein that is not a GPCR is `not_found`.
- **What a card gains.** For a receptor:
  - the class and family;
  - the segments (TM1-7, loops, H8);
  - the generic number of each residue, in every scheme GPCRdb states. The same
    position compares across receptors (D3.32 of aminergic receptors, the DRY motif
    at 3.50, the toggle switch W6.48).
  - per structure, the activation state, the ligands with the function GPCRdb states
    (agonist, antagonist, inverse agonist, allosteric), and the signalling protein.

  This is the vocabulary of GPCR drug design: the state a ligand stabilises, and the
  positions shared across a family.
- **Numbering through sequence identity, not similarity.** GPCRdb numbers residues on
  the sequence its entry states. Its numbers are UniProt's when that sequence is the
  card's UniProt sequence, character by character (`gpcrdb_sequence_numbering@1`), and
  each residue must still match. This is an equality check of two stated sequences,
  not an alignment. When they differ, everything stays in GPCRdb's numbering.
- **Apo is not a ligand.** GPCRdb writes a structure without ligand as a ligand named
  "Apo (no ligand)" with the code `apo`. The card records `apo: true` and no ligand, so
  no false chemical component enters the card.
- **In packets since `packet_aspects@3`** (2026-10-01): classification in
  `identity`, states in `structures`, segments and generic numbers in
  `sequence_features`.
- **Not taken now:** GPCRdb's mutation data. They are literature mutagenesis with
  ligand effects, often with empty fields (the first β2AR record states only the
  mutation). They are read when a use asks.

## Membranes: segments through RCSB, OPM's own API deferred (2026-09-30)
uibcdf/sabueso#83 (wave 2, structures).
- **OPM's API** answers per PDB entry:
  - the hydrophobic thickness, tilt and transfer energy;
  - the membrane type and which side is cytoplasmic;
  - per subunit, the transmembrane segments.

  But:
  - its subunits carry the letters of OPM's own model (C and D for 2RH1, whose PDB
    chain is A), so its segments cannot be placed through the PDB chain;
  - proteins are named by UniProt entry name;
  - no data licence was found on its site. The earlier "CC BY 3.0" could not be
    confirmed.

  Deferred.
- **RCSB integrates the segments**, with their origin. `MEMBRANE_SEGMENT` instance
  features come from OPM and PDBTM, in the PDB chain's entity numbering. Sabueso
  already reads instance features (secondary structure, #80), so the segments join
  `has_structure` as `membrane_segments`, per chain and per resource, in UniProt
  numbering through the entity alignment.
- **Each resource keeps its own segments.** For GPR52 (6LI0) OPM and PDBTM agree on TM1
  and differ by a residue or two elsewhere. Neither is chosen.
- **Statements of other entries are unchanged.** The segments enter RCSB's statement
  only when stated, so a soluble protein's statements keep their content.
- **What it serves.** Lipid-facing sites and membrane-accessible ligands are placed
  against the transmembrane span of the very structure that shows them.

## SAbDab: antibody complexes of a protein (2026-09-30)
uibcdf/sabueso#83 (wave 2, structures).
- **SAbDab2's annotations of the PDB.** The classic summary download now answers with
  the SAbDab2 web application. Its API publishes one JSON file (about 15 MB) with every
  antibody instance: heavy and light chains and their antigens, with the PDB entity and
  chain of each. It is read once per process, as SKEMPI's CSV is, with its SHA-256.
- **Joined through the chains UniProt states.** An antibody enters a protein's card
  when one of its antigens is a protein or peptide chain UniProt states is this protein
  in that PDB entry. Antigen names are never used. Haptens, sugars and ions carry the
  chain of the polymer they sit on, so they never make a protein an antigen.
- **Every antigen is kept, and marked.** SAbDab assigns as antigens the chains bound to
  the antibody in the structure. In 9IJR an scFv is listed with GPR52 and β-arrestin 1
  as antigens. The card keeps both, with `this_protein`, and does not claim the
  antibody recognises the receptor.
- **Antibodies are not entities yet.** Their chains, types and V gene subgroups are
  kept on the target's card. Antibody cards, CDRs and Thera-SAbDab's therapeutics wait
  for a use.
- **In packets since `packet_aspects@3`** (2026-10-01), in `structures`.

## Wave 2 of the source coverage plan, closed (2026-09-30)
uibcdf/sabueso#83.
- **In use:** ChEBI (molecules), KLIFS (kinases), GPCRdb (GPCRs), SAbDab (antibody
  complexes), and OPM's and PDBTM's transmembrane segments through RCSB. gnomAD now
  also reads the canonical transcript (#85).
- **Deferred or blocked, with the reason in the registry:**
  - the Chemical Probes Portal: no documented access; accessions only in pages;
  - SureChEMBL: mentions cannot be restricted to the claims;
  - OPM's own API: its own chain letters, and no licence found;
  - ESM Atlas: MGnify ids only.
- **Ensembl, deferred** once its service answered again (same day). For orthology:
  - its Compara answers in 44-52 s per gene;
  - it names orthologs as Ensembl genes, one cross-reference request each away from
    UniProt;
  - its vertebrate Compara has no trypanosomatids.

  OMA names orthologs by UniProt accession, and states TcTIM and human TPI1 as
  orthologs of each other. It is proposed as the orthology source (evaluating: its
  licence is to be confirmed).
- **Each source was surveyed for batch or bulk access and tested live before design**
  (whole files for SAbDab, one list request for KLIFS). Each joins only through an
  identifier its source states: an accession, the PDB chains UniProt states, or an
  InChIKey.

## OMA: orthologs, joined only through an exact match (2026-10-01)
uibcdf/sabueso#83, instead of Ensembl's Compara (deferred, 2026-09-30).
- **Why OMA.** It states pairwise orthologs across about 2,600 genomes, by UniProt
  accession where one exists, in one request per protein. That includes the
  parasite–host pairs the pilots compare. Human TPI1 has T. cruzi's TIM among its
  3,090 orthologs, 1:1.
- **The query joins only through an exact match OMA states.** OMA maps an accession to
  one of its proteins, sometimes of another strain, and says whether the sequence is
  the same (`seq_match`). TcTIM (P52270) is mapped to CL Brener's Q4DV43 with
  `modified`. Taking Q4DV43's orthologs for P52270 would be identity by similarity, so
  the card records `not_found` and names the protein OMA chose.
- **Orthologs named by stated identifiers.**
  - A UniProt accession OMA states is taken as is.
  - A Swiss-Prot entry name is resolved to its accession by UniProt, which states
    that; the name is kept as `canonical_id`. Only active entries count. A retired
    entry can keep the name of the entry that replaced it: P00938, demerged into
    P60174 and P60175, is still named TPIS_HUMAN. A name with more than one active
    entry stays unresolved. Fixed after 0.8.0: 5 of the 566 names among human TPI1's
    orthologs had a retired entry, and one could be taken.
  - Anything else (RefSeq, GenBank) stays `oma:<OMA id>`.
- **One relationship per OMA protein.** Identical proteins of several strains share one
  UniProt entry (Salmonella LT2 and 14028s, both TPIS_SALTY). `oma_id` is an identity
  qualifier, so each genome's ortholog keeps its species.
- **Options.** `rel_type` is filtered by OMA itself; `taxa` keeps exact taxon ids
  (strains are their own taxa, e.g. 353153 for CL Brener). The ceiling is 5000.
- **Terms.** CC BY 4.0, from OMA's Terms of Use as published in its browser's public
  source. The site's pages answer 403 to non-browser clients. An older FAQ line says
  CC BY-SA 2.5 for the browser, and both are recorded.
- **In packets since `packet_aspects@3`** (2026-10-01): the `orthology` aspect,
  asked by name.

## packet_aspects@3: the wave-2 sources in packets (2026-10-01)
uibcdf/sabueso#83, #88. `@2` was published in 0.7.0 and is not changed; `@3` is a new
version.
- **Where each source fits:**
  - KLIFS and GPCRdb classifications in `identity`, what the protein is;
  - kinase conformations, GPCR states and antibody complexes in `structures`, what
    each structure shows;
  - the kinase pocket in `ligand_sites`;
  - GPCR segments and generic numbers in `sequence_features`, positions on the
    sequence.

  Each enters an aspect's facts only when the card holds it, so a protein without
  them keeps the same facts.
- **`orthology` is an aspect of its own, asked only by name.** OMA gives thousands of
  orthologs per protein (3,090 for human TPI1), and packet size is watched (#88).
  With a comparator, the aspect says whether OMA states one protein an ortholog of the
  other, by the accessions the cards are anchored at, and nothing more. For HsTIM and
  TcTIM (P52270) that is empty, because OMA maps P52270 to another strain's protein.
- **Packets of different mappings are not compared.** `same_knowledge` is `None`, as
  for different formats.
- STRING and Europe PMC stay outside packets.

## Where a variant matters: gnomAD's pext (2026-10-01)
uibcdf/sabueso#102.
- **Sources surveyed.**
  - UniProt states tissue specificity as curated text, sometimes per isoform. PKM M1
    and M2 each have their own comment, and Sabueso already keeps the restriction on
    each SourceAssertion. It is text, not values to join with positions.
  - UniProt cross-references HPA, Bgee and Expression Atlas, which are gene-level.
  - GTEx's transcript medians (v8) give PKM's M2 transcript 217 TPM in skeletal muscle
    and the M1 ones 1-3, against the known biology. Short-read quantification cannot
    tell two mutually exclusive exons of one length apart, and GENCODE v26 lacks most
    transcripts UniProt states. Set aside.
  - gnomAD's pext (GTEx v10, GRCh38) gives, per coding region, the share of the gene's
    expression in each of 49 tissues that includes it. It recovers PKM's biology: the
    M1 exon reaches 0.58 in skeletal muscle and 0.01 in oesophagus. Chosen.
- **Stored as stated, joined by a rule.**
  - The pext regions are gnomAD's statements (`annotations.exon_usage_by_tissue`,
    option `exon_usage`, its own enrichment record, data `pext`).
  - `Card.variant_tissue_usage()` places each population variant's genomic position in
    its region (`pext_at_variant@1`, with the threshold as a parameter).
  - A variant outside every region is `outside_pext_regions`, never "not expressed":
    pext covers coding regions only.
  - Nothing derived is stored.
- **What it shows.**
  - TPI1's isoform-3 segment is expressed in testis only (0.38).
  - PKM's M1 exon is expressed in 23 tissues, and an alternative PKM transcript's
    region in none (86 variants).
- **It exposed a placement error.** Next to an exon the canonical transcript lacks, the
  residues on both sides are identical in the two isoforms (PKM's M1 exon, KRAS's exon
  4A). UniProt's isoform map placed changes there on canonical residues, but the
  canonical protein never carries them. gnomAD's transcript query did not catch them,
  because they are intronic on the canonical transcript, beyond its margin.

  Such changes are now asked of gnomAD variant by variant (25 per request) before the
  map is applied. In PKM and KRAS, 14 and 17 wrong placements are gone.
  `no_consequence_on_canonical` is new: gnomAD states no consequence on the canonical
  transcript at all.
- **Per isoform (same day): `isoform_exon_usage@1`.**
  - UniProt states which transcript encodes each isoform (its cross-references), and
    gnomAD states each transcript's CDS exons, in the same request as the pext. Both
    are stored (`annotations.isoform_coding_exons`).
  - An isoform's own coding bases lie in no other isoform's transcript, and the view
    gives their mean pext per tissue.
  - Isoforms built by combining exons (tau) rarely own any base, so the view also
    gives the `variable_regions`: runs of coding bases that not every isoform
    includes, with the isoforms that include them.
  - UniProt's tissue-specificity statements restricted to an isoform
    (`molecule: "Isoform M2"`) are shown with it.

  PKM is where the two meet:
  - UniProt states M2 in proliferating cells and M1 in adult tissues;
  - the pext of M2's own exon is in all 49 tissues, and of M1's in 23, highest in
    skeletal muscle.
- **Still open (#102):** tissues as UBERON terms, and isoforms whose transcripts gnomAD
  does not annotate.

## Reference entry and genome-strain entry: related, never merged (2026-10-01)
uibcdf/sabueso#103, from the TcTIM pilot (REQ-TCTIM-009).
- **The case.**
  - TcTIM's reviewed entry, P52270, carries the structures (*T. cruzi*, species
    level).
  - Proteome-based sources such as OMA use the genome strain's entry, CL Brener's
    Q4DV43.
  - The two differ at 4 of 251 positions.
  - OMA's orthology reached the human card as Q4DV43, but did not reach TcTIM's card,
    and nothing on the cards showed that the two entries were related.
- **UniProt states the relation.** `uniref=True` reads the clusters UniProt places
  the entry in (`identifiers.uniref`). For each other member of its UniRef90 cluster
  it adds `clustered_with`, saying whether the member shares the card's UniRef100
  cluster (an identical sequence or a fragment of it). This is similarity stated by
  UniProt, never `same_as`.
- **Where two sequences differ.** `Card.sequence_differences` lists differing
  positions only for sequences of equal length (`equal_length_positions@1`). Nothing
  is aligned: different lengths are `different_lengths`.
- **A source that maps an accession elsewhere says where.** OMA's `not_found` now names
  the UniProt entry of the protein it chose ("TRYCC03899 (Q4DV43)"), so that the card
  of that entry can be asked.
- **`packet_aspects@4`.** `identifiers.uniref` falls under `identity`'s areas, so
  `identity` now asks UniRef; `@3`, published in 0.8.0, is unchanged.
- **Card schema 0.3.9**, since 0.3.8 is published.

## Unreadable answers are asked again, and retries are recorded (2026-10-01)
uibcdf/sabueso#97.
- **What failed.** In eight full builds of the TcTIM/HsTIM baseline in one day:
  - BindingDB failed three times, each a 200 whose body was not JSON, answered
    normally minutes later;
  - ChEMBL's document endpoint answered HTTP 500 once;
  - OMA answered 502 to about one request in three.
- **A client that reads JSON says so** (`urlopen(..., expect_json=True)`). A 200 whose
  body is empty or not JSON is asked again, like a transient status. A second failure
  reaches the client, which reports an `error`.
  - InterPro is not marked: it answers an empty body when a protein has no residues,
    and that is an answer.
  - Reactome's version endpoint answers plain text, and is the one Reactome request
    not marked.
- **HTTP 500 is retried.** Every Sabueso request is a read, and 500 has passed on the
  next request.
- **Never silent.** Each retry is noted with its source and reason, and the card lists
  them per source and reason (`quality.retries`, schema 0.3.9). An answer that needed a
  retry is distinguishable from one that came at once.


## Validation runs are run from scratch; the archive only records (2026-10-01)
uibcdf/sabueso#100.
- A validation run asks every source again. It never builds from an earlier run's
  answers (`reusing`, `replaying`). It shows what the sources state today and what a new
  Sabueso changed, and it has repeatedly revealed problems in areas a change was not
  meant to touch.
- A run records what the sources answered (`archive.recording()`), in one local archive
  per run. A card lists the answers its build used (`quality.retrievals`), so an
  unexpected value can be traced to the answer it came from. A replay is a diagnostic
  tool after a run, not a way to run.
- `reusing` is for user projects that repeat builds.
- A run's archive is not shared: several sources' terms do not allow redistributing
  their responses.

## Tissues as ontology terms, and isoforms whose exons are unknown (2026-10-01)
uibcdf/sabueso#102.
- **Tissue terms come from GTEx.** gnomAD's pext names GTEx tissues by GTEx's ids, in
  lower case. GTEx states an ontology term for each tissue: UBERON, or EFO for a cell
  line. `gtex=True` records GTEx's statement for the tissues the card's pext names
  (`annotations.tissue_terms`). The views join the two ids by `gtex_tissue_key@1`
  (lower case, other characters as `_`), which compares identifiers of one dataset,
  never names. All 49 pext tissues match one GTEx v10 tissue each.
- **A term never replaces a tissue.** GTEx gives the cerebellum and the cerebellar
  hemisphere one term (UBERON:0002037). Grouping by term would merge two sampled
  tissues, so the views keep each tissue and name its term.
- **Packets do not carry tissue terms yet.** `packet_aspects@4` is published, and a new
  mapping makes packets of the two mappings incomparable. Tissue terms join the
  biological context with `packet_aspects@5`, together with what real packet use asks.
- **Most isoforms without exons have no stated transcript.** On 20 human proteins, 64
  isoforms had no exons. For 62, UniProt states no Ensembl transcript; Ensembl 116 maps
  none of the four checked either. Only APP's isoforms 3 and 7 have transcripts
  gnomAD's release does not annotate (newer than GENCODE 39). Sabueso does not align,
  so the first stay without exons.
- **The view says why, and what follows** (`isoform_exon_usage@2`):
  - an isoform without exons is `no_transcript_stated`, `transcript_not_in_gnomad`
    (with the transcripts) or `transcripts_not_recorded` (a card before 0.3.10). This
    reads UniProt's own cross-references, now recorded
    (`identifiers.ensembl_transcripts`);
  - own bases are counted against the isoforms whose exons are known. When some are
    not, a base counted as own may be shared with one of them: `own_bases_complete`
    and `variable_regions_complete` are false. `@1` did not say so.
- **Not done: exons from Ensembl for the two APP transcripts.** It would bring Ensembl
  in for 2 of 64 isoforms. Proposed when a use needs it.
- **A defect found along the way:** the pext enrichment record counted 0 regions since
  0.8.0, because the field's name was shadowed by the enricher's. The knowledge state
  was right (it counts the card's items); the record is right now.

## Tissue terms join the packets: `packet_aspects@5` (2026-10-01)
uibcdf/sabueso#102, #71.
- `biological_context` also reports GTEx's tissue terms (`annotations.tissue_terms`),
  beside the pext they name. The aspect asks `gtex=True` with `exon_usage=True`.
- The entry of the same day said tissue terms would wait for the next mapping. The
  maintainers asked to proceed with packets, so `@5` is that mapping.
- A packet of `@4` and one of `@5` are not compared (`same_knowledge` is `None`).
- About 10 KB more per human protein (49 tissues).

## A packet's level of detail: an index by reference (2026-10-01)
uibcdf/sabueso#88, #71; shared contract in uibcdf/moli#22.
- **The problem.** A full packet holds every view's output. For the TcTIM/HsTIM pair
  with three bioactivity sources it is 2.1 MB: bioactivities 861 KB, diseases 578 KB,
  HsTIM's population variants 313 KB. A heavily studied target is many times that.
- **The decision (maintainers, 2026-10-01).** A query declares its `detail`. `"full"`,
  the default, is unchanged. `"index"` gives, per aspect and protein, what the cards
  hold, by reference (`packet_index@1`):
  - per field: its count, its sources and the SourceAssertions that state it;
  - per relationship area: its count, its sources and every relationship's id;
  - the views a full packet would hold (`full_views`), which the pinned cards compute.
- **The boundary holds.** Nothing is ranked, selected or summarized beyond counting.
  Every item is read through the card's pin (`packet.item(role, id, store)`).
  Selecting and summarizing stay with MOLI's Context Assembly (uibcdf/moli#22).
  `unknowns`, `conflicts` and `provenance` are whole at either level.
- **Measured.** The pilot pair is 135 KB as an index (−94 %).
- **Formats.** `knowledge_query@2` adds `detail`, and a `@1` query reads as `"full"`.
  `knowledge_packet@3` states its `detail`; `@1` and `@2` are still read. Packets of
  different formats, mappings or levels of detail are not compared.

## Packets: what MOLI agreed on detail, ids and disclosure (2026-10-01)
uibcdf/moli#22 (a MOLI maintainer's answer, 2026-10-01), #88, #71.
- **`index` is accepted** as Context Assembly's first input: an inventory by reference,
  to decide what to read. `full` materializes every view. No second deterministic
  summary in Sabueso: selection, priority and synthesis belong to Context Assembly. A
  new level needs a concrete consumer, and is versioned.
- **What an index must allow, and what Sabueso does for it:**
  - the aspects, knowledge states, rules, sources and pinned references available:
    `areas` and `unknowns`, and `full_rules` (added), the rules the full views apply,
    read from the modules that define them and checked against a full packet;
  - each chosen item resolved against exactly the cited pin: `packet.item` reads that
    state, and a store without it refuses; the latest is never read instead;
  - the detail never changes what was asked, nor turns `not_queried` into
    `not_stated`: a test pins that both levels ask the same options.
- **Ids.** The pin (`snapshot_id`) is what is cited. `content_id` compares a projection
  without retrieval times. Its equality is not the same observation, provenance or an
  irrelevant change, and it never replaces the pin in Evidence, Decisions or Runs.
  Consumers keep Sabueso's reference whole and opaque until uibcdf/moli#3 agrees its
  public form.
- **Model extraction** (point 5): a statement a model extracts from a publication keeps
  the publication as its source, with `acquisition.method: model_extraction`, its tool,
  version and `validated_by`. This is what #92 already records.
- **Disclosure.** An index reveals existence, counts, sources and relationships even
  without values. Authorization and disclosure policy apply before any packet, index or
  item reaches a consumer, and again before a reasoning backend. Sabueso does not
  authorize; that is the platform's (risk recorded).
- **Closing moli#22** waits on a consumer test: a versioned query gets an index, an
  item is read by its pin, Nextia records an Evidence, and the citation survives a new
  acquisition. It also covers an unresolvable pin and an index with unauthorized
  content.

## Explain structural inventory items through exact card states (2026-10-01)
uibcdf/sabueso#91, #104.
- `Deck.explain(card_id)` keeps its membership explanation. The keyword selector
  `structure_ref` explains an experimental structure's inventory item using the same
  options as `structure_inventory`.
- `structure_inventory_explanation@1` records every protein card's pin and the full
  normalized options, including supplied residue maps. Existing coverage, state and
  inventory rules determine the result; the explanation does not classify separately.
- A group exposes all of its members' stored relationships and SourceAssertions, with
  pinned references. An exclusion keeps its classification; unknown states keep their
  reasons. No relationship on the card means `not_on_card`, not scientific absence.
- Support is relationship-level. The pinned card's sequence and length are exposed as
  context with their support and conflicts, without claiming they were the exact inputs
  of an older mapping. This limit remains explicit until mappings record their inputs.
- The view reads stored knowledge, never asks sources, and returns detached records.
  Historical use loads a saved deck pin; missing pins fail instead of reading latest.
- #104 fixes a reader mismatch discovered by this path: generated assertion ids retain
  source names with spaces, such as `RCSB PDB`, but the item-reference parser rejected
  them. Ordinary internal spaces are accepted for assertions; control whitespace and
  reference delimiters remain invalid. Existing ids, hashes, card schemas and the
  store format are unchanged, and snapshot verification still applies.

## Public literature rehearsal and curation acquisition integrity (2026-10-01)
uibcdf/sabueso#92, #105.
- A three-reading review draft and an offline preservation rehearsal use only the
  published abstract of PMID 18562316 and public HsTIM fixtures. The proposal records
  Codex as its preparer; no human validation is claimed. The rehearsal's cards identify
  their curator as an acceptance-test simulation, apart from accepted knowledge.
- UniProt's link to 2VOM, RCSB's primary citation and author numbering, and the canonical
  residue/mapped mutation anchor E104D in the paper at canonical position 105. The
  script verifies these statements instead of assuming equal numbering or identity.
- The mechanical outcomes are one `differs` and two `not_compared`. Existing source
  values and conflicts remain visible; three assertions and two free-text claims are
  retained through rebuilds, with historical support pinned. This is not a claim of
  scientific novelty or a judgment of contradiction.
- #105 was discovered during preparation: `CurationStore` exported any literature
  SourceAssertion, then replayed it as `curation`, even if its acquisition was
  `model_extraction` or `rule_extraction`. Export now uses the same acquisition boundary
  as `literature_view`: curations and legacy curations with metadata only. Human
  validation does not turn an extraction into curation. `KnowledgeStore` preserves
  extraction states unchanged. No stored schema or format changes.
- The acquisition contract of #92 governs new intake. Earlier entries that allowed
  agent-curated readings precede that distinction; an agent-prepared draft is not a
  person's validation. Durable extraction intake/replay remains #92 work.
- The full suite exposed a local-date assumption after midnight UTC (#106). The two
  temporal navigation tests now control the store's UTC clock, derive the day from it
  and exercise an equivalent instant in a negative timezone offset. Revisions advance
  explicitly without a sleep; production UTC semantics are unchanged.

## Located accession annotations start at source access (2026-10-02)
uibcdf/sabueso#92.
- `tools.db.europepmc.get_annotations(article_ids)` asks the Annotations API for
  accession-number annotations of explicit `MED:<pmid>` or `PMC:PMC<id>` articles.
  Requests use bounded batches; raw records retain the returned publication ids,
  annotation links, providers, sections, tags and quote fragments. No pipeline
  release is stated, so the envelope's version is None. The API's documentation
  version is not an extraction-tool version.
- The real public example is P60174 in a figure of PMC12400196. Its original article
  is CC BY 4.0, verified in its full-text XML; the fixture records only the complete
  accession-annotation response and its attribution. The API may return a MED record
  for a PMC request; both identifiers remain source-native.
- `prefix`, `exact` and `postfix` are quote fragments, not a complete sentence or a
  scientific claim. The returned accession tags do not justify grounding a protein
  name. A successful empty annotations response is kept as such, without concluding
  that the article has no accession; a failed request remains a ConnectorError.
- This increment is source access only: existing card enrichment stays bibliographic.
  Incorporating locations into cards requires explicit intake and recorded article
  terms, especially when a PDB mention is related to a protein through stated
  structure identity. Those mappings and own scientific extraction remain #92.
  Card schema 0.3.10 is unchanged.

## Bounded local literature extraction and original attribution (2026-10-04)

Maintainer-approved post-0.12.0 work (#92/#108) starts with the deterministic
`literal_uniprot_mention@1` rule on explicitly identified supplied text fragments.
An explicit UniProt namespace or official entry URL is required; names, bare ids,
isoform suffixes and longer tokens do not establish a canonical entry mention.
Each occurrence retains its exact text, Unicode offsets, locator, input identity
and rule-extraction tool/version/configuration. It is an extraction of a printed
identifier, not a biological claim, human validation or entity merge.

The initial API returns detached assertions, supported relationships and original
Ackredit attribution. It does not change published card schema 0.3.11 or route
extractions through `CurationStore`. Publication metadata and fragment rights stay
unknown rather than inferred. Provider failures preserve scientific results and
explicit attribution gaps. Card intake/replay and broader statement extraction
remain #92; shared project routing stays MOLI #36/#18.

The original-design review #112 maps actual implementation and remaining functions
without converting illustrative future APIs into commitments. Clinical/peptide
scope, persistent consumer acceptance and deferred mirrors retain their owners.

## Explicit literal extraction intake and replay (2026-10-04)

The maintainer authorized continuing the first design-review follow-up (#92/#112).
`Card.add_literature_extraction` intakes the delivered `literal_uniprot_mention@1`
result only for the exact UniProt subject, validating its original occurrence
identity and relationship support before mutation. Existing occurrences keep their
first stored retrieval times; alternative fragments retain support and qualifier
forms. New scientific intake metadata starts unpublished schema 0.3.12; every
published schema/shape remains immutable. Older cards require explicit migration.

`ExtractionStore` is a component-local, versioned JSONL store of exact original
results, independently of cards and human curation. It retains original portable
attribution and unknown fragment terms; a content address detects changed records.
Readers add no credit. Explicit application credits reused references with original
use contexts and producer versions, and separately credits current intake software.
Runtime intake records remain detached from scientific card hashes. Their card pin
is the state at intake, before any subsequent mutation.

Refresh preserves stored scientific support without re-executing the rule. Original
receipts are reused only when supplied through the extraction store; otherwise a
detached stored-support event states that original runtime attribution is missing.
Missing historical assertions/relationships fail explicitly, and changing the
subject never silently transfers an extraction. Unknown-rights fragments cannot
enter a terms-profile card. `CurationStore` remains exclusively human curation.

Article metadata/terms, broader statement rules and validated model extraction remain
#92. This store and runtime format are Sabueso-local; MOLI still owns shared
ProjectRecord/Recorda contracts and Nextia owns project Evidence.

## PDBe-KB aggregate acquisition observation (2026-10-04)

The maintainer authorized extending required traceability (#108) to the two existing
PDBe-KB aggregate clients. Ligand-site and interface-residue queries retain separate
operation/response identities, retries, original archive times, explicit unknown
versions and empty/unavailable/unqueried/failed outcomes without changing scientific
returns, exceptions, mappings or schemas. Group counts measure returned source
records, not validated identities or mapped relationships.

Native group indices, numbering and listed/mapped/interacting structure references
remain PDBe-KB declarations. They establish no additional direct provider access,
identity equivalence or underlying structure version. Verified PDBe-KB description
bibliography is credited independently of missing structure/method/provider citations.
Saved readers remain inert; hosts persist original runtime JSON explicitly. Shared
MOLI persistence/correlation policy and broader source observation remain open.

## AlphaFold DB acquisition observation (2026-10-04)

The maintainer authorized the next required source-observation slice (#108).
AlphaFold DB model-list queries retain original response/archive identities,
per-record model versions, native identifier forms, retries and honest terminal
outcomes, while scientific returns/exceptions, maps and card schema remain fixed.
Missing latest versions remain unknown; historical versions are declarations,
not additional access. Repeated ids retain separate versioned record indices.

Source-declared tools/providers, isoform/fragment ranges and artifact URLs establish
no additional source access, coordinate download, identity equivalence or current
generation execution. Model versions are not experimental revisions or database
releases. The database's recommended three papers receive resource/background
description credit, separately from unreturned model-specific references; Sabueso
alone receives executed-software credit for this query. Original sidecars remain
host-owned; saved readers stay inert. Shared MOLI persistence and consumer acceptance
retain their existing owners.

## 2026-10-04 — Observe InterPro's family-site query without inferring member execution

The existing `site_residues` operation now retains native signature keys and
accession/name/member forms, source-supplied locations, header/fixture release
bases, original decoded/wire/archive identities, retries and reuse/replay (#108).
Counts measure returned signature records, not mapped sites. Empty objects/bodies
and HTTP 204 retain the original absence contract; HTTP 404 stays not-found.
Neither distinguishes an unknown accession from no site annotation. Missing
fixtures, unqueried access, unexpected/partial records and failure remain distinct.

InterPro's resource description has verified complete bibliography. Unreturned
member/signature/site references stay gaps; declared providers and source-provided
positions do not claim direct member access, local alignment or InterProScan
execution. Scientific mappings, identity, schema and original returns/exceptions
remain unchanged. Saved readers remain inert. Applications retain original runtime
sidecars; this local adapter does not establish a shared MOLI persistence contract.

## Explicit bibliography binding with separate fragment rights (2026-10-05)

For #92/#108, query Europe PMC core metadata only for an explicitly supplied native
publication identifier. Bind one complete result to a supplied-fragment publication
only when the source states that identifier. Native PMID/PMCID/DOI declarations,
returned authors/journal/pages/dates and licence literals remain original database
support under `article_metadata_binding@1`, separate from `literal_uniprot_mention@1`.
No abstract/full text is projected, no article URL is followed, and an arbitrary
supplied fragment is not authenticated as article text.

The unpublished 0.3.12 intake manifest adds optional metadata support IDs/rule.
Assertion identities include explicit alias/service context, excluding retrieval time;
alternatives never replace prior metadata or another source's citation fields.
ExtractionStore retains original bindings/access sidecars; refresh preserves support
without a query or rule execution. Saved readers remain inert; composition credits
represented stored article citations without new access. Native incomplete bibliography
and unavailable original credit remain gaps.

Service versions are not article revisions. Licence literals remain unnormalized;
open-access status is not permission, and article terms do not license an arbitrary
supplied fragment. Fragment terms/profile boundaries and raw publication-term archive
retention remain unchanged. Broader extraction, supplied-fragment rights, model/human
validation and the MOLI application-record boundary remain open.

## 2026-10-05 — Exercise application persistence without freezing a shared record

For #108/#112, retain an application-owned example bundle of pinned knowledge,
original ExtractionStore results, operation/result sidecars and portable Ackredit
workflow attribution. Run its producer, reader and reuse in independent processes;
verify file digests, result/item bindings and workflow contextual-use closure before
rendering original references. Fixture reacquisition advances current heads while
historical item pins, native bibliography and original attribution remain intact.
Reading does not acquire knowledge or credit another execution; missing original
sidecars are refused rather than reconstructed from current payloads or versions.

The manifest is provisional local application data, not a platform contract.
Content hashes detect inconsistency, not authenticity or permission. Transactional
multi-file delivery, journaling and ProjectRecord/Recorda reliability remain MOLI
#36/#18; Nextia owns explicit project interpretation/Evidence. The public fragment
is synthetic with unknown rights. Published 0.12.0's compatible pilot and immutable
release receipts remain that release's qualification.

## 2026-10-05 — Explain original oligomer inputs without rewriting scientific rules

For #91, `Card.explain_oligomer()` explains the whole native view with
`oligomer_explanation@1`. It retains source assemblies/methods, actual partner
branches, family-site members, original source versions and current/historical
item pins. All matching selected annotation assertions remain support; alternatives
and conflicts remain context. Relationship-level support does not manufacture
per-qualifier mapping lineage or original execution attribution. Readers are inert
and detached, with no stored schema change or new SourceAssertion.

The published agreement rule compares integer positions without confirming their
numbering. Preserve its actual result, expose the native numbering/sequence data,
and mark unconfirmed agreement partial. A versioned scientific correction with
explicit legacy behavior belongs to #120; equal numbers never establish identity.

## 2026-10-05 — Version interface comparison and preserve explicit legacy selection

For #120, default `interface_site_agreement@2` compares only declared UniProt
interface positions for the exact card subject with family sites on that entry in
1-based indexing. Missing/conflicting context, unlocated contacts, nonpositive
positions and incompatible declarations retain reasons and uncomputed None sets.
Computed empty sets remain lists; partial family scope and missing comparison
inputs are explicit. Equal residue numbers never establish correspondence.

Both `Card.oligomer` and `Card.explain_oligomer` digest keyword-only `agreement_rule`.
Explicit `@1` preserves the original view and `oligomer_explanation@1`, including
historical pins. Default explanation `@2` retains native rule inputs and original
support without new acquisition, mutation or credit. No stored card schema changes.
New full/index packets advertise `@2`; saved payloads are read as originally stored.
`packet_aspects@6` retains its frozen source/area scope: the changed scientific rule
is named in the new facts and index, rather than rewriting an existing packet.

## 2026-10-06 — Observe clinical queries; retrieve reference modules explicitly (#108/#127/#128)

- Keep clinical card SourceAssertions and published schema 0.3.12 frozen. Add a
  separate source-envelope reference query and runtime acquisition context.
- Complete native pagination before classifying absence; refuse malformed answers,
  unrelated NCT ids, conflicting duplicate records and token loops. Unavailable
  fixture answers remain unavailable, including partial saved subsets (#127).
- Preserve native citations, links, update dates and exact occurrences. Registry
  timestamps are not verified per-page versions or publication years. Free citations
  are not parsed for identity, and linked targets are never followed automatically.
- Let explicit Europe PMC queries contribute their own native bibliographic metadata
  to the enclosing workflow. Preserve collective authors as literal names in their
  original order; compact author strings cannot replace a complete native list (#128).
- Retain bibliography gaps, separate resource/registry/pointer roles and inert saved
  readers using the existing public Ackredit minimum. No new provider contract is needed.


## 2026-10-08 — Rebuild HK2 as a current public test system

Use human HK2 (UniProt P52789) alongside TcTIM/HsTIM as a public regression
system. Rebuild cards and notebooks from qualified native responses using the
current API, rather than promoting historical card exports to expected knowledge.
The initial integrated baseline uses the existing unchanged UniProt fixture;
additional provider responses require their own qualification and rights.
Historical artifacts remain a temporary local backup and unverified query/case
reference, not a maintained parallel scientific baseline. The misleading old
PTGS2 filename does not create a PTGS2 test system. See
[HK2_TEST_SYSTEM.md](HK2_TEST_SYSTEM.md) and
[the final historical review](archive/local_work_2026-07/followup_35_final_review_and_hk2.md).

## 2026-10-09 — Declare shared-source terms ownership (#136)

Use one canonical resource for each scientific source name in the packaged terms
export. Resource order never decides ownership. A resource sharing that source
declares `terms.shared_with` and repeats the owner's complete policy record;
validation refuses undeclared duplicate owners, mismatched records, missing or
foreign-name owners, chains and cycles. Compare all policy fields, including
retention, depositor restrictions and review dates, so a duplicate cannot hide a
different restriction or claim a fresher review.

UniProtKB owns the `UniProt` terms and UniRef declares that ownership. Both use
provider-level UniProt Consortium attribution, with the owner's original recorded
review date and unchanged CC-BY-4.0 licence/statement. This corrects attribution
and registry ownership; it is not a new source licence review. Keep SourceAssertion
names, biological identity, quantity/card schemas and original saved reports fixed.

## 2026-10-09 — Accept the quality completion work plan (#112)

The maintainer accepted the bounded work packages in the
[quality completion proposal](pending_proposals/design_implementation_review.md#quality-completion-proposal-2026-10-09-112).
Continue real consumer validation before extending the exercised inspection,
pinned explanations and source-operation/bibliography coverage. Follow with a
rights-qualified literature statement, one clinical/query/terms slice and measured
workload/failure behavior. These refine the existing roadmap; they do not authorize
a new architecture, provider-count milestone or release publication.

Keep engineering execution, installed-artifact qualification and human scientific
acceptance separate. A source-supported result is useful only with inspectable
identity, scope, support, quantities, revisions, rights and explicit gaps. Private
consumer notebooks and results stay private and read-only. Project Evidence and
Discovery remain with Nextia, whose design pause does not block standalone Sabueso
quality work. Record concrete defects in their owning issues and correct observed
contracts with public regressions.

## 2026-10-10 — Observe gnomAD operation scope and unqueried gene prerequisites (#108/#141)

Observe the four built-in variant/transcript/consequence/pext routes without
altering normal supplied-gene scientific mapping or pins. Preserve actual GraphQL
queries, native identities and transcript versions; requested dataset/genome and
client GTEx labels are separate from unknown native release. Failed later batches
retain completed scope but return no partial science. Missing local files are
unavailable. Reuse the existing prerequisite gate for absent Ensembl gene identity:
stop before client construction and record unqueried scope, not source absence.
Credit the existing GraphQL resource without inventing publications. Source/CI,
installed-artifact and human/consumer acceptance remain separate. See
[scope and qualification](pending_proposals/gnomad_observation.md).


## 2026-10-10 — Open Targets missing upstream gene scope (#142)

Use the existing `RequestPrerequisiteMissing` gate for absent upstream Ensembl gene
identity. Return `not_queried` before constructing or calling a source client,
retain requested options, and report unknown counts with the blocking input.
Do not change native target-to-protein binding gates, valid-gene scientific payloads
or historical saved cards. An explicit refresh may record the corrected outcome
while the exact old pin remains readable. Keep legacy `NothingToAsk` compatibility
in the generic runner and audit the remaining six source-local gates under #143;
this bounded correction does not qualify those routes or live provider behavior.


## 2026-10-10 — Six source-local prerequisite gates (#143)

Classify absent upstream Ensembl protein, NCBI Gene, PDB, usable MedGen concept
identity or a queryable named disease as unqueried in the six built-in dependent
enrichers. MONDO needs a supported identifier or a MedGen UID; a text label,
unsupported namespace, placeholder or unresolved concept cannot be queried.
Use the existing exception before constructing clients; retain requested options
and unknown knowledge counts. Preserve actual queried empty/missing/error outcomes,
organism coverage, source-native mapping and the generic legacy exception contract.
Explicit refresh records the correction while original SourceAssertions and both
pins remain available; saved reading never reclassifies historical cards. Keep
this bounded integrity correction separate from adding acquisition instrumentation
to SKEMPI/SAbDab and from derived comparative operation/bibliography work (#108).
See [scope and qualification](archive/source_prerequisites.md).


## 2026-10-13 — Version disease identity coverage by identifier (#144)

Keep grouping @1/@2 and their explanations explicit and unchanged. Default to
grouping/explanation @3 with `disease_identity_coverage@1`: exact completed
identifier diagnostics differ from blocked/unavailable requests and unknown
historical scope. Source-wide counts or another identifier's answer never prove
coverage. The MedGen acquisition route needs stored UIDs before MONDO can be
asked; this prerequisite cannot erase a direct source-stated MONDO equivalence.
Preserve positive stored paths, conflicts, original SourceAssertions and pins.
Coverage is derived metadata, never new SourceAssertions or Evidence.

Packets use a new `packet_aspects@7` mapping for the corrected disease view and
retain its paths/coverage. Stored @6 payloads stay exact; full/index terms support
both mappings, reconstructing the historical @2 view for @6 index scope. Neither
card schemas nor shared query/packet formats change. Public source qualification,
installed-artifact delivery and consumer-owned acceptance remain separate.
See [scope and qualification](archive/disease_identity_coverage.md).

## 2026-10-13 — Observe comparative view execution in explicit contexts (#108)

Preserve the existing scientific algorithms and their ordinary dictionaries. Only
an explicit `sabueso.attribution()` context observes the three ordinary sequence,
variant and isoform views, collecting `sabueso.comparative_operation@1` separately
from packet/source/literature events. Plain calls and pinned explanations stay
inert; saved reading never invents earlier execution.

Declare `comparative_input_scope@1` for selected input fields and all stored
isoform tissue-specificity assertions actually consulted by the engine. Keep
scientific support gaps, underlying bibliography gaps, original source labels and
unverified database releases distinct. Repeated executions retain reused input
credit and distinct execution identities. Provider failure preserves completed
science; scientific exceptions propagate with a failed host record and no
completed credit. Missing/changed pins refuse attribution.

Share one operation-independent source-record declaration with packet composition;
otherwise a mixed workflow registers conflicting notes for the same resource id.
The actual operation stays in each use context. Original saved sidecars retain
their metadata and source identity remains unchanged.

Use the existing public Ackredit capture API and existing offline descriptions.
No source query, auto-discovery or shared Recorda/ProjectRecord contract is added.
See [scope and qualification](pending_proposals/comparative_operations.md).

## 2026-10-13 — Batch locally checked code and recover deferred CI (#112)

The maintainer approved intermediate `[skip ci]` direct pushes after applicable
local checks, including tested code. Record the head, tested and untested scope,
owner issue and recovery route. Finish the block with exact-head CI and governance
through an unskipped push or explicitly authorized manual runs. Local test success
and deferred development publication are not remote qualification. Required PR
checks and immediate security/dependency/packaging/migration/integration gates
remain mandatory, as do release and installed-artifact gates.

Enable manual governance execution and include default-branch coverage publication
in manual CI, so the recovery route covers the same applicable jobs as a push.
Inspect all job conclusions and full receptor captures; an overall green run with
skipped applicable jobs is insufficient. Keep canonical MOLI guidance unchanged.
See [local policy](TESTS.md#recovering-deferred-ci) and the
[current deferred block](pending_proposals/deferred_ci.md).

## 2026-10-13 — Persist comparative results and original workflow credit (#108/#112)

Version the public comparison example as `@3`, retaining ordinary views alongside
explanations, original execution/source records and enclosing workflow attribution.
Bind sidecars to reports and exact input pins; validate the stored support/credit
and export original bibliography without rerunning science or loading the backend.
Reacquisition keeps earlier files and distinct execution identities. An unstated
fixture annotation remains partial support without resource credit.

Accept original `@1`/`@2` and keep their rules and execution gaps; never reconstruct
past records from today's runtime. Preserve their generation during reacquisition.
Scientific algorithms, SourceAssertions, card schemas and fixtures remain unchanged.
This is component-local example persistence, not shared ProjectRecord/Recorda or
Nextia Evidence. Complete bibliography and consumer acceptance remain separate.
See [scope and checks](pending_proposals/comparative_journey_attribution.md).

## 2026-10-13 — Scope verified resource and upstream pext references (#108/#112)

Curate three verified offline references for gnomAD/GTEx resources and pext
methodology. Keep collective bylines and complete publication coordinates;
describe online/issue years and the papers' original dataset scopes explicitly.
Preserve existing API/portal credit. Only completed pext access or valid stored
gnomAD pext input selects `method_description` under `pext_reference_scope@1`.
This never claims upstream method execution, native method/data revision or
entry-study membership. Missing/failed access and unsupported inputs receive no
completed method credit. Specific publications and revisions remain gaps.

Store original metadata and scope with each execution; readers validate and render
those records without today's catalogue or fresh credit. Older records lacking
method fields retain their references and gaps. No SourceAssertions, Evidence,
scientific algorithms, card schemas or provider query are added. Shared MOLI
recording, complete bibliography and consumer usefulness remain separate.
See [verified sources and acceptance](pending_proposals/comparative_bibliography.md).


## 2026-10-13 — Retain complete comparative input scope once per host operation

Use `sabueso.comparative_operation@2` and `comparative_input_scope_reference@1`
for exact execution/field/hash links from bibliographic uses to the host's retained
input scope. Full-scope duplication per supported assertion made serialization
quadratic in the public receiving regression. Preserve all scientific values,
assertions, individual use context and historical `@1` records; require the host
sidecar for complete detached-credit scope validation. This is component-local
recording, not a MOLI wire schema, SourceAssertion or Evidence (#108/#112).

## Located review drafts preserve the acquisition boundary (2026-10-14)

uibcdf/sabueso#92, #105, #132, #112.

- Initial example `@1` at `f08bdad` used human-curation APIs for two agent-prepared
  structural readings. Pending scientist review and an explicit agent name did
  not satisfy the 2026-10-01 acquisition decision. That source is unqualified;
  its CI was cancelled and its original local bundles remain diagnostic history.
- Corrected example `@2` preserves unchanged licensed native text, explicit subject
  support, the original baseline card pin and proposed readings in a separate
  sidecar. It creates no literature SourceAssertions or curation records, refuses
  imported curations and rejects the unqualified `@1` route.
- This applies the existing contract, not a new schema or agent policy. A name's
  validation cannot establish human review. Actual extraction must retain a
  declared tool/version and acquisition method; accepted future intake remains
  #92 work. The old core/argument docstrings are aligned with the existing decision.
- The structural article's parasite results cannot become human experiments or
  supply protocols for the stored ChEMBL assays. The native parameter review found
  incomplete conditions; source-specific protocol review remains pending.

## 2026-10-21 — Share the first structural exploration result (#148)

Use the existing single-protein structural inventory, knowledge-state scope and
pinned inventory explanation over the verified Card capture. Human
`view("structures", options=None)` and technical `select("structures", fields=None,
options=None)` share that materialized result; no second scientific inference or
source acquisition is introduced. Human scientific cells and projected machine
pages retain original rules, conflicts, exclusions, unknowns and units. This is
a bounded slice B continuation, not acceptance of all profiles or saved sessions.
See [the scope and qualification](pending_proposals/card_structures_exploration.md).

## 2026-10-22 — Captured contextual navigation (#148)

Deliver `CardItem.related()` and exact-result `CardView.follow(item_ref)` over
retained source records, endpoint/glossary references and explicitly supplied
captures. Preserve source selections and navigation origins; switch to each
destination's own profile without recapture or acquisition. Keep repeated inputs,
distinct revisions, missing identity basis and ambiguity explicit. Only exact
references and retained source-supported `same_as` paths admit destinations under
`retained_context_links@1`; related source facts never become project Evidence or
new SourceAssertions. Context-only destinations have no focal Card or explorer.
Independent focal selection bindings and focal-aware structural caches prevent
cross-Card result leakage. See the [scope](pending_proposals/card_context_navigation.md).
Saved reading, broader machine conformance and researcher acceptance remain open;
0.15.0 consolidation remains paused.

## 2026-10-22 — First portable literal/field exploration (#148)

Deliver one `sabueso.card_exploration@1` bundle and `read_exploration` reader for
supported literal/field views, original disease hierarchy/context navigation and
literal machine selections. Preserve captures, full underlying results, typed
quantity/source bindings, exact selections and navigation origins; validate
independently before atomic publication and inert reading. Report integrity,
source bindings, recorded navigation decisions and unverified scopes separately.
New interpretation requires `start_new`; missing optional operations are `not_saved`.
Required closure and unavailable historical verifiers fail explicitly. Derived
structure/coverage persistence remains pending rather than being admitted as
unverified scientific data. See the [scope](pending_proposals/card_saved_exploration.md).
No Card schema, scientific rule, source intake or shared MOLI contract changes;
0.15.0 consolidation remains paused.
