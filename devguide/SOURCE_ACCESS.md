# Source access (uibcdf/sabueso#49)

The common acquisition, validation and card-contribution contract. Provider-specific
protocols, native fields and qualification limits are maintained in the
[native access reference](sources/NATIVE_ACCESS_REFERENCE.md),
[development API](sources/DEVELOPMENT_API.md) and
[mapping scopes](sources/NATIVE_MAPPING_CONVENTIONS.md).
The [registry](sources/registry.yaml) owns source adoption/terms; the
[fixture delivery inventory](sources/FIXTURE_DELIVERY.md) owns reviewed input delivery.

## HTTP response lifetime (#151)

The shared transport closes transient `HTTPError` responses that it discards
before retry waiting. If retry observation or waiting fails, no discarded
response remains open. A final raw transport error keeps its native identity
and readable body: the direct caller owns that response and closes it after use.
An archive reads and closes the original error before constructing its separate
buffered error; the original also closes when reading or recording fails.
Archive recording/replay/reuse do not transfer a live network handle to storage.

A source client that translates an HTTP error to a Sabueso error, or consumes it
as a source-specific empty/invalid result, closes that response itself. Code,
message, headers, status classification and exception causes remain available;
the cause is not an open response-body reader after translation. KLIFS, MobiDB
and PubChem finish their native error-body parsing before closure. In particular,
a malformed body does not become a source-stated absence and PubChem retains its
native structure-fault message. Successful response context managers retain their
existing ownership. The release helper also closes HTTP errors consumed by
absent-version preflight or discarded during public-poststate polling; explicit
404 acceptance and fail-closed publication checks are unchanged. No registry
query, publication or credential access is performed by the offline regression.
No warning suppression or new HTTP retry policy is involved.

The [lifetime regression receipt](evidence/http_lifetime_151_20261022.json) records
network-free response ownership tests, source/installed qualification and limits.
Final native CI evidence is retained in [#151](https://github.com/uibcdf/sabueso/issues/151).
This development correction does not change the published 0.14.0 package.

## One module per source

An active source accessed directly has a `sabueso.tools.db.<source>` module, public `get_*` functions
and a mapping in `sabueso.mappings.<source>`. It is declared `in_use` in the
registry, including access, applicable data terms, acquisition requirements and
scientific scope. `in_use` means Sabueso reads it directly or through stated
cross-references; it does not establish live health, card contribution or release.

### Shared source terms

The packaged terms export has one canonical registry resource per
`SourceAssertion.source.name`. A second resource using that same scientific source
name declares `terms.shared_with: <owner resource id>` and the same complete terms
record. The owner declares the name directly; chains, cycles, different policy
records and undeclared duplicates are refused by both the registry gate and export.
The result is independent of registry row order (#136).

UniRef shares the `uniprot` resource's terms for the scientific source `UniProt`.
The shared attribution names the UniProt Consortium; it does not imply that a
UniProtKB-only build acquired UniRef. The canonical review date belongs to the
owner's recorded terms. Source identities, source assertion support and historical
saved terms reports are not relabeled or rewritten.

Survey the provider's documented batch, per-record and release routes before
designing a client. Respect required keys/agreements and response/throttling
semantics. A reachable website, current software version or article licence does
not qualify arbitrary responses or identify scientific record revisions.

## Client protocol

Online, fixture and supplied-snapshot implementations share the source's explicit
method/query contract. Native responses validate against the requested source,
record and scope; parsing is separate from acquisition. Preserve original
response identity, fields, literal blanks, occurrences, unknowns and conflicts.
Validate the received scope before selecting: malformed later rows cannot silently
become absence or an apparently complete selected record.

- `record` preserves source content; normalized knowledge belongs in mappings.
- `query` states the exact normalized request; supplied declarations remain
  distinguishable from a provider's native echo.
- `retrieved_at` states an original observed or declared acquisition time. Local
  read time, HTTP modification time and procedural dates have separate bases.
- `version` retains the qualified native record/release revision or `None` when
  unstated. Service, code and route versions are not interchangeable with it.
- Received cuts, limits and totals keep their own declared scope. Retaining all
  bytes is not proof of database completeness.

Source-stated empty/not-listed responses differ from unasked, unavailable,
unauthorized, malformed and failed acquisition. Use the existing connector and
not-found errors; card enrichment isolates per-source/per-request outcomes.
Do not bypass access gates or infer permission from availability.

A declared enricher whose required upstream input is missing or ambiguous raises
`RequestPrerequisiteMissing` before constructing or calling its client. The runner
records `not_queried` and its prerequisite explanation. gnomAD and Open Targets
require an upstream Ensembl gene cross-reference (#141/#142); missing gene identity
creates no source operation or data-resource credit. This does not change an
actually queried Open Targets target that omits the caller protein. The
built-in gates for DISEASES (Ensembl protein), ClinVar (NCBI Gene), SKEMPI and
SAbDab (PDB), MedGen (usable concept id), and MONDO disease identity (a named
disease with a queryable identity) now use the same prerequisite boundary (#143;
[qualification](archive/source_prerequisites.md)). Generic legacy
`NothingToAsk` compatibility remains; historical saved classifications are never
rewritten during reads. GTEx requires pext tissue
keys and one unambiguous GTEx release label in the upstream record; missing inputs
are not GTEx absence (#135). Development GTEx observation records the dataset
label as a request parameter and native revision as unknown; returned row counts
and a single response do not establish whole-dataset coverage (#108).

The built-in online OMA, UniRef, gnomAD and GTEx routes validate the native
containers they consume (#137). An omitted required envelope or list, wrong JSON
container or unanswered gnomAD consequence alias is a connector failure, never an
empty scientific result. A GraphQL error with a partial record is a failure; the
existing explicit not-found error form and well-formed empty/null answers retain
their own semantics. These checks do not qualify every nested native field or add
source-operation observation to every route. The separate development GTEx slice
observes existing tissue access; development UniRef observes existing cluster/member
pages with their individual release and limit bases. Development OMA observes
xrefs/protein/ortholog operations separately from UniProt entry-name resolution;
development gnomAD observes variant/transcript/consequence/pext GraphQL scope,
query labels versus unknown native releases, and partial alias batches. Missing
local consequence inputs are unavailable. Both gnomAD enrichers stop as unqueried
when the entry states no Ensembl gene, before constructing a client (#141).
Derived operation coverage remains open. Original response bytes, source identity
and card schemas stay fixed. [gnomAD scope](pending_proposals/gnomad_observation.md).

Development [comparative bibliography](pending_proposals/comparative_bibliography.md)
adds offline gnomAD/GTEx resource descriptions and scoped upstream pext method
references. `method_description` is credited for completed pext access or valid
stored pext support under `pext_reference_scope@1`; it never claims upstream method
execution, a native revision or row-study membership. Missing/failed access has no
completed credit. Native entry references remain unknown/unqueried, and original
saved records are not supplemented during reading. No scientific payload/schema
or source request changes accompany the bibliography.

Online UniRef members use `uniref_member_pagination@1`: at most 100 logical pages,
including empty pages, and no repeated exact request URL. Exhaustion or a cycle
raises `ConnectorError`; completed pages remain observable without partial card
assertions. The existing 5,000-row ceiling remains successful explicit truncation.
Retries are bounded separately by shared transport policy; this is not a strict
elapsed-time guarantee. [Policy and verification](archive/uniref_pagination.md).

### Supplied originals

`load_source_snapshot` parses explicit supported formats and preserves original
compressed-byte identity, caller binding/terms/time and the local read receipt.
It does not authenticate the caller, prove source access, grant reuse rights or
admit knowledge into cards. Source-specific snapshot clients additionally validate
their native record shape and source/query/identity. Shared bound clients reject
foreign source/kind/query/revision declarations before file I/O.

Raw JSON duplicate keys/nonfinite values, malformed tables and mismatched supplied
digests fail. Hash equality is integrity, not authenticity or a scientific revision.
No source links, embedded scripts or referenced calculations execute on file intake.
See the native reference for the exact formats and binding contract of each client.

## Public functions

Public `get_*` arguments use ArgDigest, one digester per argument name. Diagnostics
use SMonitor; optional dependencies use DepDigest. `skip_digestion` is not permission
to bypass native validation or acquire an invalid scope. Test invalid public
arguments before source access as well as caller/file copying and original support.
The [argument contract](ARGUMENT_CONTRACTS.md) lists the public boundaries and plain
accessor exceptions; [PUBLIC_API.md](PUBLIC_API.md) records exposed interfaces.

## Required acquisition traceability (#108, moli#36)

Scientific support, observed runtime and bibliography retain separate meanings.
Supported clients observe acquisition automatically through the common services.
Trace successful, empty, reused, unavailable, failed, truncated and unqueried scope;
preserve original response identities and times through archive replay. A custom
or uncovered boundary states `not_observed`, rather than claiming complete provenance.

The native reference records published and development observation coverage for
each route. It includes UniProt/Europe PMC/RCSB, ChEMBL/PubChem/BindingDB,
PDB CCD/UniChem, PDBe-KB/AlphaFold/InterPro and later disease/clinical and
NCBI Taxonomy slices, plus
[development GTEx tissue observation](pending_proposals/gtex_observation.md) and
[development UniRef page observation](pending_proposals/uniref_observation.md) and
[development OMA operation observation](pending_proposals/oma_observation.md).
Each new source must declare and test its observation coverage and gaps.
Per-result and workflow sidecars preserve original citations and producer context;
saved readers add no source access, recomputation or credit.

Development [comparative view observation](pending_proposals/comparative_operations.md)
retains actual sequence/variant/isoform executions only in an explicit attribution
context. Its separate `operations` accessor binds original input pins and result
digests; stored-input credit never claims another source query. Plain calls,
explanations and saved readers stay inert. Selected field support and all-stored
isoform tissue text are declared, not reconstructed row-level/request lineage.

Source authors, native publication pointers, acquired article metadata and complete
bibliography have distinct coverage. A PMID or article title alone does not prove
that its publication content was acquired or that bibliography is complete.
MOLI owns shared ProjectRecord/Recorda composition; local envelopes/sidecars are
not shared recording or consumer-Evidence acceptance. Follow #108 and the
[attribution proposal](pending_proposals/ackredit_knowledge_pipeline_attribution.md).

## Enriching cards (#86)

Standalone mappings retain their original subject: an EC class, structure, cell
model or regulatory page is not a protein merely because an identifier is linked.
Decide an integration from a concrete scientific use. Source-stated identity,
numbering/sequence axes, revisions and units are required before transfer.

A source that contributes to cards declares an enricher in `sabueso/enrichers/`:
option, source name, registry id, areas, organism coverage, `requests`, `fetch` and
`map`. The shared runner derives knowledge-state and migration coverage and applies
deterministic ordering and per-request outcomes. Packet options derive from those
declarations. See [SOURCE_ARCHITECTURE.md](SOURCE_ARCHITECTURE.md).

1. Implement the native client, public function and source mapping.
2. Declare/register the justified enricher in the appropriate stage/order.
3. Add its resolution option/client and corresponding argument digesters.
4. Add qualified fixture support, a representative card-shape case and wiring tests.

`tests/core/test_enrichers_offline.py` checks declarations, arguments, digesters,
registry and derived coverage. RCSB structures, the bioactivity group and NCBI Gene
remain explicitly bespoke for the reasons in the source architecture. Absence from
the enricher registry alone does not characterize those established routes.

## Shared transport and source services

- Use `_http.urlopen` for user identification/retries; JSON requests pass
  `expect_json=True` when an unreadable body is a failed response.
- `_http.gather` supports documented per-record pacing; offline saved responses
  require no source requests. Do not add parallel fetching without measurements.
- `_release` supports explicitly qualified release declarations.
- `_keys.required` handles user-supplied credentials without storing/logging them;
  a missing key remains `not_queried`, not biological absence.

Bounded source-specific original representations and validation stay local to
their clients/mappings. Shared parsing must preserve source semantics, not erase
differences to make providers superficially uniform.

## Fixtures and qualification

Every fixture declares original source, date, revision basis, applicable terms and
modifications in `temp_data/NOTICE.md`. No private/pilot data enters public fixtures.
Public access and code MIT do not license external data. The reviewed recovery
inventory protects local-only originals and separates public from full local
native qualification. Follow [TESTS.md](TESTS.md) and
[FIXTURE_DELIVERY.md](sources/FIXTURE_DELIVERY.md).

Native fixture replay, public parser-contract regressions, live acquisition, saved
scientific journeys, consumer acceptance and release delivery are separate gates.
Record the scope of each passing result. Reopen deferred sources only when the
registry's named access/input/terms condition changes.

## Deprecated (removed before 1.0)

Legacy `fetch_*_json` and `create_*_card_online` aliases are replaced by `get_*` and
`sabueso.resolve`. Offline `create_*_card_from_json`/`create_*_card_from_file` routes
remain. The provider reference preserves the exact compatibility list.

## Boundaries

Source-reported predictions, geometry, ranks, potential sites and regulatory status
remain their original source assertions. They do not establish Sabueso calculations,
experimental confirmation, clinical interpretation or Nextia Evidence. Derived
views name their versioned rule and support; they are not stored as SourceAssertions.

## Possible future problems

Measure full-export parsing and original-support retention on bounded journeys
before changing caches/storage (#98/#100). Keep missing identity, coordinate axes,
input revisions and rights explicit; the registry and owning issues record
reactivation conditions and design decisions.

## Explicit article metadata acquisition (since 0.13.0, #92/#108)

Explicit Europe PMC PMID/PMCID/DOI metadata and source-stated binding preserve
native alternatives, authors/citations/terms and original query support. Supplied
fragment text is not authenticated by its bibliography or granted article rights.
See the [native reference](sources/NATIVE_ACCESS_REFERENCE.md) and
[literature user guide](../docs/content/user/literature_and_curation.md).

## ClinicalTrials.gov observation and native references (development, #108/#127)

Explicit study/reference access and separately requested article metadata retain
their own acquisition/bibliography scope. No automatic linked acquisition or
clinical inference follows. The [clinical checkpoint](pending_proposals/clinical_registry_checkpoint.md)
records precise implementations and qualification receipts.
