# Sabueso — Argument contracts (ArgDigest)

Structural machine selection (#148) adds one digester each for `where`,
`item_refs` and `order_by`. Backend guards validate declared typed equalities,
finite physical operands, exact membership without duplicates and scalar sorting
with explicit units, including skipped digestion and empty selections. Invalid
grammar fails before materialization; foreign references fail against the known
result. Saved mode validates the frozen policy and returns only exact retained
requests, never substituting a partial selection for a full human topic.

Saved exploration (#148) reuses `path`/`overwrite` digestion for human/machine
`save`, and adds one `expected_digest` digester for the public shared reader:
`None` or exact `sha256:<64 lowercase hex>`. Backend guards remain active with
digestion skipped. Wrong output arguments are argument errors; invalid saved
bindings, missing retained closure or unavailable required verifiers are storage
errors. Unsupported saved scientific requests return `not_saved`; malformed
known request syntax remains an argument error, never a source absence.

Contextual navigation (#148) reuses `item_ref` digestion for `CardView.follow`
and checks exact link-result membership at the backend, including skipped
digestion. Link selection accepts declared role/target/availability string columns;
quantity units remain invalid. Unknown keywords are refused. `related()` takes no
arguments and never treats arbitrary field text as an identity reference.

Nature-specific exploration (#148) reuses topic/question/option digestion with
profile-specific declared catalogs. Field and ontology/coverage panels reject
nonempty scientific options. Hierarchy accepts declared subject/predicate/object
string selection; coverage accepts its original scalar columns, requiring finite
non-boolean count equality and preserving unknown counts. Record columns reject
quantity units. Backend guards remain active with digestion skipped. Chemical
quantities reuse existing declared field/unit codecs; no new representation is
introduced.

Protein question access (#148) digests `answer(question, options=None)` with one
`question` digester and the exact caller-specific `options` mapping branch. Backend
guards reject unknown questions/options, foreign or unsupported sequence axes and
invalid/out-of-range regions even with digestion skipped. Missing explicit scope
is `missing_prerequisite`, never an unscoped scientific execution. Function has no
options. Region scope reuses the existing region/fragment normalization and checks
retained canonical identity/sequence consistency before invoking the shared reader.

Structural exploration (#148) adds strict `options`/`fields` branches only for
scientific selection and human view calls, preserving legacy resolve options and
field-path contracts. Options reuse `include_fragments`/`region` digestion;
`unit` has its own digester. Human equality/sort validate the selected schema
and explicit quantity dimension, including empty selections. Machine projection
rejects duplicate/unknown fields; unsupported machine grammar is not ignored.

Human literal exploration (#148) also digests `Card.explore`/`CardExplorer`,
`inspect`, `view`, `search`, item lookup and label/kind display selection.
`field_path`, `locator` and `topic` use exact caller-specific branches; curation
and publication contracts remain unchanged. `column`, `equals`, `descending` and
`item_ref` each have a digester. Backend guards remain active with digestion skipped.

Development literal Card access (#148) digests `Card.access`/`CardAccess`
construction (`card`, `related_cards`), catalog (`kind`, optional typed `locator`),
read (`location`, `text_slice`), selection lookup (`selection_ref`), pages
(`limit`, `max_bytes`, `cursor`) and export (`path`, `overwrite`). Location and
snapshot/membership checks remain at the backend, including when digestion is
skipped. The existing publication-text `locator` contract is unchanged outside
the explicit Card-access catalog and human-inspection callers. Page bounds exclude booleans; cursors
are opaque session/selection-owned tokens. Unknown keywords retain ArgDigest's
`UnknownArgumentError`; bad semantic values raise SMonitor `ArgumentError`.
The argument discovery guard includes literal access and human explorer/view methods.

Development FDA OOPD reuses standard `identifier` digestion (outer whitespace
is trimmed), then enforces 1-12 ASCII digits without zero/leading zero, prefix,
query or path syntax. Skipped digestion still enforces that literal contract.
Snapshot source/kind/query/native HTML representation/unknown revision must match;
gzip/UTF-8/hash failures and incomplete late tables fail explicitly. The HTML does
not echo the numeric page locator: URL observation or caller binding identifies a
page only, never a stable designation/product/protein entity.

Development TTD reuses `identifier` digestion and requires exact `T` plus five
ASCII digits, even when digestion is skipped. Snapshot source/kind/query/release
must match the request and native header. All original blocks validate before
selection; field keys/order, date, original title and target identity fail explicitly
on unsupported input. Cross-reference literals never become accession arguments.

iPTMnet reuses `identifier` digestion with an exact uppercase base accession,
without isoform/prefix/search/path inputs. Snapshots bind iPTMnet, substrate_report,
HTML representation/selected panel, exact accession and unknown revision. Native
accession/link identity and tab/table correspondence are checked; malformed late
groups, duplicate sections/attributes, foreign queries, cuts and revisions fail.

Development BRENDA reuses the `identifier` digester, then enforces one exact
four-component ASCII numeric EC literal without prefixes, leading zeroes or
wildcards, even with digestion skipped. Snapshot declarations bind BRENDA,
`enzyme_class`, the exact EC/four-field SPARQL query and an unknown scientific
revision. RDF URI identity must equal the query; literals retain string datatype
and language, missing OPTIONALs remain absent, and malformed late rows fail.
No source metadata is silently resealed for another query or release.

Development Pharos reuses `identifier` digestion plus backend exact uppercase
base-accession checks, also with digestion skipped. Isoform/search/URL selectors
are unsupported. Snapshots bind Pharos/TCRD, target, exact accession/five requested
fields and unknown scientific revision; original JSON/gzip hashes remain distinct
from caller source/terms declarations. Native null and GraphQL errors are separate.

Development DepMap reuses `identifier` and `release` digestion plus backend checks
for exact `ACH-` plus six digits and fixed `24Q4` article-v1 Model.csv. Snapshot
source/kind/query/revision bindings and original CSV/gzip hashes validate before
all-row parsing/selection. Names and aliases are not selectors. Caller metadata
does not independently prove release identity or reuse permission.

Development Interactome3D reuses `identifier` and `release` digesters and backend
checks, including skipped digestion: exact uppercase accession literal, optional
explicit isoform suffix and the sole qualified `2024_12` release. `current`, other
archives, prefixes, lowercase and compound/pair queries are unsupported. Snapshots
bind Interactome3D, protein_structures, human/representative/proteins.dat scope,
exact accession/release and unknown native version. Whole-table validation precedes
selection; optional SHA verifies original supplied TSV/gzip bytes. Caller metadata
is not independent proof of provider identity, scientific revision or permitted use.

Development ProBiS reuses the existing `identifier` digester and strict backend
checks, including skipped digestion, for a lowercase four-character PDB literal,
one dot and one case-sensitive alphanumeric chain. Prefixes, multicharacter chains,
URLs and automatic case repair are unsupported. Snapshots bind ProBiS-Database,
kind `reference_chain_catalog`, exact chain/artifact query and unknown scientific
version. SHA verifies supplied TSV/gzip bytes; every five-column row validates
before selection. Caller declarations do not establish source identity or reuse rights.

Development PDBTM uses the existing `identifier` digester and strict backend
guards, including skipped digestion, for one exact lowercase four-character PDB
value. Prefixes, chain selectors and URL components are unsupported. Snapshots
bind source PDBTM, kind `transmembrane_topology`, exact PDB/XML query and unknown
scientific version. Optional SHA verifies supplied XML/gzip bytes; XML declaration,
namespace/native ID, copyright and every chain/region validate before mapping.
Caller metadata does not prove source identity, revision or permitted use.

Development 3did uses `identifier` with strict backend validation for one exact
lowercase four-character PDB literal, even when digestion is skipped. Prefixes,
chain selectors, uppercase, padding/URL syntax and extended IDs are outside this
qualified query contract. Snapshot metadata binds source 3did, kind
`domain_motif_interactions`, exact PDB/export query and unstated scientific
version. Optional SHA verifies original text/gzip bytes; caller metadata does
not independently establish identity, revision or reuse permission.


Development HPO reuses `identifier` and `release` digesters and enforces backend
scope even when digestion is skipped: a literal positive NCBI Gene ID without
padding/prefix/symbol, plus an exact valid `vYYYY-MM-DD` release. The default
qualified artifact is `v2026-09-01`; `latest`, malformed dates and URL components
fail before transport. Snapshots bind source HPO, kind gene_phenotypes, exact
query/export/release and matching version. Original file hashes verify bytes;
caller metadata is not independent proof of source identity or reuse permission.


Sabueso digests the arguments of its public tools with ArgDigest, as MOLI's
support-library policy requires (uibcdf/sabueso#31) and as the sibling components do
(MolSysMT, MolSysViewer).

## Layout

Development MEROPS uses the existing text identifier digester plus strict backend
checks for one exact native `Trembl:`, `swissprot:` or `PIR:` prefixed literal.
Public digestion trims outer whitespace; native case/version/quoted text remains
unchanged. Three-column assignments validate before selection; four-column
representations are explicitly unassigned, without joining or shifting. The
original quoted accession is accepted as a literal with an unresolved qualifier,
not repaired into a current accession. Checks also apply with digestion skipped.
Bound metadata requires source MEROPS, kind accession_assignments, exact literal
query/export and unknown revision; malformed late rows fail before mapping.


Development MetalPDB requires one explicit site ID such as `12ca_2`. The existing
identifier digester trims public text; backend checks also apply when digestion
is skipped. Only the four-character PDB prefix is lowercased; source chain/residue/
atom literals stay exact. PDB-only, UniProt and compound/search query expressions
are rejected. Bound JSON/gzip metadata requires source MetalPDB, kind site, exact
canonical site_id query and unknown revision. Native arrays/types and every
received row validate before any assertion; no indexing fallback or number repair.


Development ECOD uses the existing text identifier digester plus backend checks
for an explicit ASCII numeric UID string of one to nine digits. Zero padding is
normalized numerically; domain and chain case stays native. Checks also apply with
digestion skipped. Snapshot metadata binds source ECOD, kind domain, exact integer
uid query and unknown revision; booleans/floats are not UIDs. Only the observed
experimental JSON shape is qualified. Range text is preserved without parsing,
offsets, canonical placement or inferred numbering/sequence revisions.


Development TCDB requires one exact nonempty native accession literal, preserving
case and version suffixes. The public text digester trims outer whitespace; source
checks reject unsafe/internal whitespace or namespace prefixes even when digestion
is skipped. This lexical check does not establish UniProt/RefSeq identity. Native
TSV/gzip snapshots bind source TCDB, kind accession_assignments, exact literal
query, export acc2tcid and unknown revision. All received rows are validated before
selection; blank native accessions remain unbound and five/six-component TC codes
remain opaque. No source string is repaired, uppercased or dropped.

Development ChannelsDB annotations require one four-character PDB ID starting
with 1–9. Public identifiers use the existing text digester and lowercase native
PDB query; backend lexical checks also apply with digestion skipped. No chain,
UniProt, assembly, AlphaFill or calculation selector is inferred. Supplied JSON/
gzip binds source `ChannelsDB`, kind `pdb_annotations`, exact lowercase `pdb_id`
query and unknown revision. Native text/reference/residue/chain values are never
trimmed, parsed as canonical coordinates or assigned a sequence axis.

Development ChannelsDB channel reading reuses that explicit PDB contract with
kind `pdb_channels`. All twelve category arrays and native membership/annotation
items are checked before output under `channelsdb_tunnel_membership_json@1`.
Id/Cavity are native string-or-integer labels (excluding bool); Auto is literal
string-or-bool and is never coerced to an evidence class. Required residue/index
arrays contain nonempty strings; empty arrays remain explicit. Labels need not
parse as residue coordinates or valid indices, and the independent arrays need
not have equal cardinality or matching token sets. All scientific revisions remain
unknown; bound file and custom-client source/kind/query/revision/cut mismatches fail.

Development GWAS Catalog requires one literal standard mapped-gene
symbol, a positive limit no greater than 500 and a zero-based nonnegative integer
`page`. The new page digester rejects booleans/floats; backend checks still apply
when digestion is skipped. This local limit cap is not a claimed provider maximum.
The existing identifier digester trims public text; native row symbols are compared
exactly without trimming/case repair. The reader fixes `extended_geneset=false`,
validates every row, HAL shape, page totals/counts and official-host page links.
Original numerical/text statistics, nullable/empty fields and future context remain
unchanged. Supplied JSON/gzip binds source/kind/full query and unknown version,
with optional original-byte SHA. A gene filter is not an identity resolution.

Development Monarch requires an exact CURIE, positive limit no greater than 500
and nonnegative integer offset. The new `offset` digester rejects booleans/floats;
source checks also apply with digestion skipped. Expanded native pages must identify
the exact requested subject and echo limit/offset, with consistent totals and cuts.
Snapshots bind the complete direct-subject query and optional original-byte SHA.
Native qualifiers/negation and knowledge/agent labels are retained without coercion.
Development PRIDE requires one PXD plus six-digit project identity and validates
the original JSON before mapping. The existing identifier digester trims public
text; source checks also apply when digestion is skipped. Path/name/multiple
selections, wrong project/shape/revision/cut and malformed arrays fail explicitly;
missing individual licence metadata remains unstated. Native CV objects are not
rewritten into the strings suggested by some API schemas.

Development WikiPathways requires one literal supported namespaced ID, with exact
case, accession/isoform and Ensembl version digits retained. Bare accessions,
symbols, names, unsupported prefixes and multiple IDs fail before access, including
when digestion is skipped. Matching uses comma/semicolon token boundaries across
seven original fields; prefixes are never inferred from column names. Full finite
JSON, required native strings, pathway identity/URL and native date labels are
validated before selection. Supplied JSON/gzip binds source, kind, exact xref/dataset/
scope, unknown version and optional original-byte SHA. Native malformed aliases
and heterogeneous cells remain literal; they do not become canonical identities.


Development EMA orphan access requires one exact `EU/3/YY/number` string, retaining
its digits rather than normalizing leading zeros. Existing identifier/client
digesters apply; backend checks also apply when digestion is skipped. Names,
protein IDs, lowercase/multiple IDs, placeholders and alternate EMA references
cannot be queried by this scoped reader. Full JSON meta/data shape, finite values,
count equality, UTC generation timestamp, required native field types and independent
official page URLs are checked before selection. Native number placeholders remain
literal in the full export. Snapshots bind source, kind, exact number/dataset,
unknown version and optional original JSON/gzip byte SHA; metadata adds no remote credit.

Development CIViC requires one exact positive molecular-profile ID string and a
mandatory monthly release in `01-Mon-YYYY` form. Existing identifier/release/client
digesters trim public text; backend checks still apply when digestion is skipped.
Names, protein IDs, padded IDs, nightly/latest, multiple queries and malformed
release paths fail closed. All native rows are validated before selection. Supplied
TSV/gzip binds CIViC, kind molecular_profile_items, exact profile/dataset/release,
matching version and optional original-byte SHA; declaration adds no remote credit.

Development DrugCentral accepts one exact base UniProt accession, checked after
identifier digestion and again in client/mapping backends, including skipped
public digestion. Native composite target tokens are local selection context, not
multiple user queries or identity merges. Snapshots bind source DrugCentral, kind
target_relations, exact accession and dataset drug_target_interactions, unknown
version and optional SHA-256 of original compressed/uncompressed bytes.


Development ClinGen `get_gene_validity` reuses `identifier` and `client`, requiring
an exact `HGNC:` plus positive integer gene identifier after standard digestion.
Names, protein IDs, bare numbers, padded IDs, suffixes and multiple identifiers
are refused even when digestion is skipped. Native preamble/header/width, gene and
MONDO identities, report namespaces and classification dates are validated across
the full export before selection. Unknown classification/MOI/SOP labels stay literal;
legacy dates with no timezone are not filled. Mapping and snapshot binding recheck
source/kind/query/revision/cut. File dates cannot be supplied as native revisions.

Development HPA `get_gene_profile` reuses `identifier` and `client`, then
requires a single unversioned human ENSG identifier and matching native `Ensembl`.
Standard identifier digestion strips surrounding whitespace; skipped digestion
still checks exact identity. A list, wrong gene, malformed category/reference,
non-finite JSON, invented revision or local cut fails explicitly. Mapping and
snapshot binding independently validate exact source/kind/query/native identity.
Missing categorical keys remain separate from native null declarations. No suffix
stripping, gene-symbol lookup or gene-to-protein identity merge is performed.

Development SIGNOR `get_relations` reuses `identifier`, `taxon_id` and `client`.
An exact base UniProt accession and integer organism request 9606/10090/10116 are
required even when digestion is skipped. Names, isoform suffixes, multiple IDs,
path/query decorations and other organism requests are refused. Complete native
column shape, entity/relation identity, query namespace, DIRECT and taxonomy
literals are validated before mapping. Requested organism is not native taxonomy.
Snapshot constructors reuse the metadata/SHA digesters; declared source/kind/query/
revision must match exactly before a supplied table is admitted.

Development APPRIS `get_gene_annotations` reuses `identifier` and `client`, then
requires an exact unversioned human `ENSG` plus eleven digits even with digestion
skipped. Gene names, protein/transcript IDs, version suffixes, multiple IDs and
query decorations are refused. Dataset/assembly/reference-set/method filters are
not part of this qualified provider-default route. Native row identities/types,
genomic range/strand/frame and envelope source/query/cut/revision are validated
before mapping; no principal selection or protein coordinate inference occurs.

Development Complex Portal `get_complex` reuses `identifier` and `client`, then
requires an unversioned positive primary `CPX-<number>` accession before client access,
including when digestion is skipped. Names, protein/internal EBI IDs, zero/leading-zero
suffixes and URL/path decorations are refused. Native primary/internal identity and
primary CPX cross-reference must agree. All participant/feature/reference and annotation
arrays, finite JSON, native flag/ECO/star types and dates are validated before mapping.
Zero/null stoichiometry and unknown ranges remain native; they are not coerced to
missing participants or canonical positions. Supplied snapshots check exact query
binding and optional original-byte SHA-256; unsupported client revisions/cuts fail.

Development CATH `get_domain_summary` reuses `identifier` and `client` and adds
`release`, a non-empty selector digester. Source semantics require a seven-character
PDB-chain-domain ID and a fixed `v<major>_<minor>_<patch>` release before client access,
also when digestion is skipped. Only the PDB-code part is lowercased; chain case stays
native. Moving aliases, URL/path decorations and guessed revisions are refused.
Complete domain identity, classification hierarchy, finite JSON, native sequence
lengths and residue/segment correspondence are validated before mapping. Snapshot
metadata is query-bound; optional SHA-256 verification uses original file bytes.

Development UniProt `get_isoform_sequence` reuses `identifier` and `client` digesters,
then requires a base accession plus a positive isoform suffix before client access,
even with digestion skipped. Base-only identifiers, names, leading-zero suffixes
and URL/path decorations are refused. Full parent identity, finite JSON, sequence/
checksum/audit and every isoform declaration are checked before selection. Duplicate
IDs and malformed VAR_SEQ pointer lists fail closed. The native FASTA ID must match
exactly; no canonical fallback, multi-record parsing or sequence repair is allowed.
Client/envelope cuts and unsupported revisions are refused. Missing declaration
scope, explicit empty arrays and unsupported sequence statuses remain distinct.

Development SWISS-MODEL `get_metadata` reuses `identifier` and `client` digesters,
then requires a base UniProt accession before access, even when digestion is skipped.
Native v2 query identity/unfiltered scope, full sequence length/MD5, entry references,
explicit structure arrays, finite scores and every target/template alignment are
checked. Booleans are not bounds or scores. Target peptides match the source sequence;
paired column lengths and outer bounds match native segments. Extra context stays
literal, without current UniProt equivalence or template author/label projection.

Development AmyPro `get_entry` reuses `identifier` and `client` digesters, then
requires an explicit positive `AP` plus five-digit native entry ID before access,
including when digestion is skipped. The full received export must have unique
native IDs, finite JSON, required literal fields and explicit region dictionaries.
Region bounds must match the investigated entry sequence. Parent bounds and mutation
strings remain native declarations rather than inferred sequence equivalence.

Development IntAct `get_interactions` reuses `identifier`, `limit` and `client`
digesters, then requires one UniProt accession (optionally an explicit positive
isoform suffix) and a single-page limit from 1 to 200 before access. These checks
still run with digestion skipped. The whole native MITAB page, exact primary/
alternative namespace-qualified matches and native total header are checked
before selecting rows. Aliases/xrefs and equal identifiers in another namespace
never establish the requested protein.

Development AlphaFill/LIGYSIS functions reuse `identifier` and `client`, then
require a base UniProt accession before access. LIGYSIS additionally digests the
required `segment` through its own positive-integer digester (excluding bool),
with no default first-segment choice. Semantic checks still run when digestion is
skipped. AlphaFill validates the native model ID, finite metrics, alignment scope,
unique placed chain IDs and distinct donor numbering. LIGYSIS validates exact
accession/segment identity, native counts/bounds, unique site IDs, complete membership
and score ranges before mapping. JavaScript expressions are never evaluated.
`map_displayed_residues` additionally requires the exact result-page envelope/query,
unknown revision and received completeness, then validates the independent
`cc`/`newChartData` column contract. Every row is checked before assertions are
returned. Repeated positions stay independent; table identity does not infer a site
or current sequence axis. The site-only mapper keeps its six-literal contract.
`map_residue_correspondences` reuses the exact detail-envelope guard and validates
both directed literal dictionaries completely before output. Native four-character
structure parents, non-empty case-sensitive chain labels, integer-shaped string
keys and integer values are required; bool/float/coerced-string values and insertion
code-shaped keys fail. Signed/zero/leading-zero labels retain their literal form;
unknown numbering schemes are not normalized. Opposite parents need not match and
non-bijective/contradictory declarations remain independent, without protein identity.

Development GlyGen `get_protein` reuses `identifier` and `client` digesters, then
requires a base UniProt accession before client access. Native canonical identifier,
source sequence/length, complete modification table counts, finite JSON and literal
support pointers are checked before mapping. Isoform queries are not inferred from
base accessions; the response's canonical designation remains explicit.

Development EPPIC/PDB-REDO functions reuse `identifier` and `client` digesters,
then require one four-character PDB ID before client access. EPPIC validates native
entry/interface/cluster identities, method scores, explicit collections and source
component hashes; PDB-REDO validates exact native PDB identity, finite JSON, fraction
R-factors/null, native pipeline date/version and software revision/use types.

EPPIC `get_interface_residues` additionally requires `interface_id`, digested as
a positive integer excluding bool, with no default interface choice. Public PDB
and interface constraints also run when digestion is skipped. The complete context
must identify the selected interface before detail access. Native side/serial/region
types, finite area/entropy values and numeric-or-quoted-NaN fractions are checked;
unknown regions, negative serials, null labels and repeated occurrences stay native.
The mapper verifies exact component hashes/revision scope without renumbering rows.

Development `pdbe_validation.get_global_percentiles` reuses `identifier` and
`client` digesters, then checks a four-character PDB ID before access. Exact native
entry identity, finite raw values and 0–100 percentile ranks are checked separately.
`relative` is optional; missing and zero remain distinct. Unknown native metric names
and additional context are preserved without assigning undocumented units.

Development MobiDB and SIFTS access reuse the existing `identifier` and `client`
digesters. Semantic checks restrict queries to canonical UniProt accessions and
four-character PDB IDs respectively before client access. Native sequence/release,
export counts and continuation headers, annotation bases, interval bounds and
structural endpoint numbering are validated at the source boundary. Offline
`tools.sources.get_catalog()` has no data-selection arguments or source access.

Development `alphamissense.get_annotations` digests `identifier`, `limit` and
`client`. Semantic validation requires a canonical UniProt accession and positive
integer row limit before discovery. Native discovery identity, full supported
human sequence, artifact URL, substitution positions/reference amino acids,
numeric score bounds and duplicate rows are checked independently. The complete
CSV is validated before the result cap; malformed rows never disappear behind it.

Development sequence lookup digests `sequence_input` (nonempty text), `taxon_id`
(None or a positive integer excluding bool), `limit` and both client arguments.
`checksum` requires 32 hexadecimal MD5 characters and normalizes uppercase.
Semantic validation rejects multiple FASTA entries, invalid amino-acid characters,
gaps and internal stops before acquisition; optional terminal `*` removal is named
in the normalization receipt. Current source identity, sequence/length/checksum,
taxonomy, native totals/pages/releases and scope are validated independently.

- `sabueso/_argdigest.py`: the configuration, the same as the siblings'.
  - `DIGESTION_STYLE = "package"`, `STRICTNESS = "warn"`, `SKIP_PARAM = "skip_digestion"`.
  - `UNKNOWN_ARGUMENT = "error"`: a mistyped keyword is refused, as plain Python would.
- `sabueso/_private/argdigest/digest.py`: `arg_digest()`, the decorator bound to that
  configuration.
- `sabueso/_private/argdigest/argument/<name>.py`: one digester per argument name,
  `digest_<name>(value, caller=None)`. Shared helpers live in `_shared.py`, outside the
  digester package.
- `sabueso/_private/argdigest/function/`: function contracts (axis 1). A closed signature
  needs none. `sabueso.resolve` takes `**options`, and its contract admits the
  `card_options` domain (`sabueso/_private/argdigest/domain/card_options.py`). That
  domain is the union of the options of `resolve_protein_card` and
  `resolve_molecule_card`, read from their signatures so the two cannot drift. The tool
  `resolve` routes to refuses an option that belongs only to the other tool.

## Decorated functions

`tests/core/test_argument_contracts_offline.py` discovers them. It finds every `get_*`
of `sabueso.tools.db` and every decorated public method of `Card`, `Deck`,
`KnowledgeStore`, `CurationStore`, `ExtractionStore` and `KnowledgePacket`, so that a new one cannot miss its digesters. As of
2026-09-26 they are:

- **Tools:** `resolve`, `resolve_protein_card`, `resolve_molecule_card`, `ligand_deck`,
  `ambiguity_deck`, `knowledge_packet`, `to_dataframe`, `expand`, and every
  source-access function (`get_*`, `uniprot.search`).
  Since 0.13.0, `extract_literature_mentions` digests `text`, `identifier`, `publication`
  and `locator`, plus optional `article_metadata` (a mapping or None); its semantic boundary additionally requires a canonical UniProt
  accession and an explicit fragment location. The public tool guard includes it. Metadata binding validates the explicit
  Europe PMC article envelope, source-stated identity, unique complete result and
  consistent original receipt before extraction. `get_article(identifier)` digests
  `identifier` and semantically requires pubmed:<id>, pmc:PMC<id> or doi:<doi>; names
  and guessed identifiers are refused before access.
  `extraction` accepts a result mapping; semantic validation checks the delivered
  rule, occurrence identity and relationship support before mutation. `extractions`
  accepts an `ExtractionStore`, its path or None. Store constructor/save/apply and
  `Card.add_literature_extraction` are digested; plain `records()` is an inert reader.
  Europe PMC's `get_annotations` digests `article_ids`: one `MED:<pmid>` or
  `PMC:PMC<id>` string, or a non-empty list/tuple, normalized to uppercase with
  duplicates removed in input order. Names, bare accessions and malformed ids are
  refused before requesting annotations.
  The card option `europepmc={"article_ids": ...}` uses the same digester. It is
  separate from the bibliographic search's `{}` or `{"limit": n}`; combining
  `article_ids` and `limit` is refused.
- **Card views and operations:**
  - `bioactivities`, `structures`, `ligands`, `compare_ligands`, `compare_knowledge`;
  - `claims`, `table`, `extract`;
  - the curation methods (`add_literature_*`);
  - `expand` (a predicate, or several, from the relationship vocabulary; `options`
    keyed by entity type) and `explain` (#91).
  `Card.compare` and `Deck.compare` reach their field paths through `Card.extract`.
  `explain_literature(publication_ref)` accepts the literature view's native
  `pubmed:`, `doi:`, `europepmc:MED:`, `europepmc:PMC:` and `uniprot.citation:`
  references, with whitespace stripped. It neither guesses aliases nor matches names.
  Since 0.13.0, `explain_disease(disease_ref)` selects a MONDO group using
  `mondo:MONDO:<seven-digit id>` or `MONDO:<seven-digit id>`; namespace case and
  surrounding whitespace are normalized. Other ontologies, names and malformed
  identifiers are refused; no equivalence lookup or acquisition occurs.
  `diseases` and `explain_disease` digest `grouping_rule`: exactly
  `disease_grouping@3` (development default), `disease_grouping@2` (published
  0.14.0 default) or `disease_grouping@1` (explicit historical compatibility). Unknown versions and non-string selectors are refused.
  `explain_disease` takes this selector as a keyword-only argument, preserving its
  existing positional `skip_digestion` argument.
  Since 0.13.0, `explain_knowledge_state` digests `knowledge_area` and
  `knowledge_source`: None selects all; a nonempty string selects an exact native
  row name with surrounding whitespace stripped. No case/name alias matching or
  source lookup occurs. Unknown selectors return no matching row; malformed shapes
  and empty strings are refused.
  Since 0.13.0, `explain_measurement` digests `measurement_ref`: an exact local
  `REL_` id or `MG_` plus 16 lowercase hexadecimal digits. Pinned fragments,
  activity ids and malformed selectors are refused. `explain_bioactivity` digests
  `molecule_ref`: the exact namespaced item key from `bioactivities()`, without
  case changes, whitespace normalization or identifier resolution. It reuses
  `include_indirect` and quantity-bearing `thresholds` contracts. A well-formed
  missing native item returns `not_on_card`, never a negative measurement.
  Since 0.13.0, `explain_ligand_site` digests `ligand_site_ref`: an exact local
  `REL_` id from `ligand_sites()`. Source ligand identifiers, groups and pinned
  fragments are refused. `explain_ligand` reuses `molecule_ref` with its caller
  contract: the exact `sabueso:small_molecule:<namespace>:<id>` from `ligands(deck)`;
  a bioactivity source-record key is refused instead of silently returning an
  empty crossing. It reuses `deck`, `include_indirect` and quantity `thresholds`.
  `ligands`, `compare_ligands` and `explain_ligand` digest keyword-only
  `counting_rule`: exactly `ligand_measurement_count@1` (published numeric counter)
  or `ligand_measurement_count@2` (default, distinct included groups).
  Unsupported versions, aliases and non-string values are refused; existing
  positional arguments, including `skip_digestion`, retain their positions.
  Since 0.13.0, `oligomer` and `explain_oligomer` digest keyword-only
  `agreement_rule`: exactly `interface_site_agreement@1` (legacy integer-only)
  or `interface_site_agreement@2` (default, confirmed UniProt/1-based comparison).
  Aliases, unsupported versions and non-string values are refused. No identifier
  resolution occurs; `explain_oligomer` retains its positional `skip_digestion`.
- **Deck operations:** `summarize`, `structure_inventory`, `unique_names`,
  `group_by_rank`, `expand`, `explain`.
  `explain` accepts `structure_ref=None` for membership, or `pdb:<four-character id>`
  (normalized to uppercase) for an inventory item. Inventory options use the same
  digesters as `structure_inventory`; non-default options require a structure selector.
- **KnowledgeStore:** `save`, `load`, `history`, `source_assertion`, `relationship`,
  `relationships`, `save_deck`, `load_deck`, `deck_history`, `save_packet`,
  `load_packet`, `packet_history`, `import_card_table`, `as_of`, `revision_as_of`,
  `changed_since` (`when`: a date, a datetime or an ISO string, #91).
- **KnowledgeQuery** (#71): its constructor digests `subject`, `comparator`, `aspects`
  and `constraints`. `knowledge_packet` takes `**clients` and admits the
  `source_clients` domain, the resolver and the `*_client` options of
  `resolve_protein_card`. So a keyword never changes what a query asks.
  **KnowledgePacket**: `terms(use, store)` uses the existing `use` and `store`
  digesters; a missing store is refused by the method, never replaced by fresh data.
- **Resolver:** `EntityResolver(uniprot_client, policy, rcsb_client, ncbi_gene_client)`.
- **SQLite storage**, where the table name is interpolated into SQL:
  - `save_card_sqlite`, `load_card_sqlite`;
  - `save_deck_sqlite`, `read_deck_sqlite`, `load_deck_sqlite`.
  `Card.to_sqlite` and `Deck.to_sqlite` go through them.
- **Classmethods.** `Card.from_sqlite` and `Deck.from_sqlite` are classmethods, which
  ArgDigest does not wrap cleanly (uibcdf/argdigest#19). The storage readers they call
  digest `table` directly, with the same digester.

Not decorated, because their only constraints are ordinary types, or because a wrong
value fails loudly instead of answering plausibly:
- `attribution()`, which accepts no arguments, the packet's detached `attribution`
  property and its run's detached `records`, `acquisitions`, `literature` and
  development `operations` accessors; the comparative observer adds no arguments;
- the JSON storage helpers, which take a path and a card or deck;
- `Card.get`, `set`, `quantity`, `quantity_columns`, `relationships`, `entity`;
- `Deck.add`, `extend`, `exclude`, `basis`, `sort`, `filter`, `map`, `in_lineage`,
  `group_by`, `intersect`, `difference`;
- `CurationStore`'s methods.

A method whose wrong value would answer plausibly (a typo that returns an empty result)
must be decorated. `claims(topic)` and `group_by_rank(rank)` were found missing on
2026-09-26 and are now decorated. `Card.expand` used to return an empty Deck for any
kind, which read as "nothing related"; it now follows relationship predicates only
(#91), and refuses anything else.

Rules for all of them:

- `@arg_digest()` goes under `@signal`.
- Each function takes `skip_digestion=False`. Use it only for internal calls with values
  Sabueso just built, never at a public boundary.

## What the digesters decide, and what they do not

- **Refused with `ArgumentError`** (`SABUESO-E-ARG-001`, also a `ValueError`): values that
  would otherwise run and give a plausible wrong result. Examples:
  - `structures="1SUX"` used to iterate its characters; it is now one structure;
  - unknown source options (`chembl={"limt": 10}`) and out-of-range ones;
  - non-boolean switches;
  - strings where a client object is expected;
  - table names that are not plain SQL identifiers, or that Sabueso reserves (`deck_meta`).
- **Normalized**: a single value where a list is expected is one item, not its characters.
  `structures="1SUX"` is one structure, and `card.extract("identifiers.uniprot")` is one
  field.
- **Not refused**: whether an identifier names a supported record. That is the resolver's
  answer, recorded in the resolution (`status="unsupported"`), not an argument error.
- **Source clients are duck-typed**: any object, or `None` for the online default. Their
  protocol is exercised by the call, and failures are source outcomes.

## Guards

Development comparative explanation APIs reuse the protein-Card `other` digester.
The new `threshold` digester admits only finite Python int/float dimensionless
cutoffs in [0, 1], excluding bool. The explanation engines retain these semantic
checks even when digestion is skipped. Development ordinary tissue views use the
same guards; explicit historical usage rules retain their original algorithms.
No quantity or pathogenicity meaning is inferred from the cutoff.

`Card.residue_composition` reuses the shared `residues`, `sequence_ref` and
`source_assertions` digesters. The existing `residues` digester also serves engagement
APIs with their own accepted row shapes; the composition's semantic boundary requires
a list of positive integer sequence positions (excluding bool), even when digestion
is skipped. Empty selection is explicit; out-of-bounds positions raise rather than
being cut. Structural residue dictionaries and one-/three-letter row labels are not
coerced into positions. Source sequence declarations require exact id, subject,
uppercase sequence and any stated hash, with contradictory content refused. Missing
canonical support and excluded invalid source declarations remain explicit.

Development recovery (2026-10-06): `Card.get_residue(position)` requires a positive
integer (not bool); both residue readers accept only `sequence="canonical"`.
The semantic reader refuses missing sequence/UniProt identity and out-of-range
positions. `Card.to_notebook` and `tools.card.write_notebook` digest `card`, `path`,
optional text `title`, `mode` (`full`/`minimal`), `language` (`en`/`es`) and boolean
`include_code`/`include_card_snapshot`. AAindex `get_index` digests `identifier`
and `client`; the client additionally requires a native four-letter/six-digit
uppercase accession before access. No isoform guessing or refresh occurs.

`load_source_snapshot` digests `path`, `source_metadata`, `file_format`,
`expected_sha256` and `records_key`. Metadata requires non-empty `source` and
`kind`, optional dict `query`, optional text retrieval/version and finite JSON
terms. Unknown keys are refused. Formats are explicit or inferred from the suffix;
SHA-256 is exactly 64 hexadecimal characters. Formats are JSON/JSONL/NDJSON/CSV/TSV
or literal UTF-8 HTML/TXT, optionally gzip-compressed. `records_key` wraps row lists
only; it cannot rewrite text or a native object. Literal text keeps BOM and line
endings and establishes no native identity or completeness.
DisProt digests `identifier`/`client`; native canonical UniProt accessions are
validated before file/network access, and identity, sequence, bounds, counts,
ontology flags and integer revisions are checked before mapping.

`Card.residue_knowledge` uses the same positive-integer `position` contract.
`sequence_ref` accepts `canonical` or a non-empty namespaced sequence reference;
`source_assertions` accepts a list of dict records or `None`. The reader additionally
requires identified finite-JSON SourceAssertions, full source sequence declarations
for positional inputs, exact subject/id/content/hash agreement, 1-based coordinates
and unambiguous dense/sparse samples. Invalid source scope is reported as unplaced;
missing or contradictory requested sequences are refused. No isoform is inferred.

`tests/core/test_argument_contracts_offline.py`:

- every listed public tool is wrapped by ArgDigest, and every parameter has a digester;
- the refusals listed above;
- unknown keywords are refused;
- no `DigestNotDigestedWarning` on ordinary calls.

## Known limitations

- ArgDigest's wrapper adds frames. Diagnostics raised inside decorated functions therefore
  compute their stack level (`sabueso/_private/smonitor/outcomes.py`, see
  `DIAGNOSTICS.md`). Reported upstream.
- A truthy non-boolean `skip_digestion` (for example `"yes"`) switches digestion off
  before the flag itself is digested, so only a falsy non-boolean reaches its digester.
  Reported upstream.
- Refusals name the caller as `<module>.<function>`, so a method's class is missing, for
  example `sabueso.resolver.entity_resolver.__init__`. Reported upstream
  (uibcdf/argdigest#18).
- A decorated classmethod warns that `cls` has no digester (uibcdf/argdigest#19). Until
  that is fixed, classmethods are not decorated; see above.


Development `ligysis.get_structure_mapping(identifier, segment, pdb_id)` additionally
digests `pdb_id` through its four-character PDB digester, excluding traversal and
non-string inputs and normalizing query case. Semantic validation also runs with
digestion skipped. Both native residue directions must contain exactly the requested
structure parent. All four tables are validated before selection: signed integer
string keys/integer values, non-empty case-sensitive chain labels, and exact native
UniProt references (including positive isoform suffixes). Extra finite native JSON
remains raw. Empty received tables differ from missing tables. The mapper requires
an exact three-key query, unknown revision and uncut envelope. Native chain/accession
parents need not match residue/remapping parents and never fill missing declarations.
Protein/segment query context is not confirmed by the response.

Development bound native-file clients for AlphaFill, GlyGen, SIFTS and LIGYSIS reuse
`path`, `source_metadata` and `expected_sha256` argument digesters. Metadata is
validated and detached at construction; optional SHA-256 is normalized. Each call
requires exact source/kind/query context and an unknown scientific revision before
opening the file. Getter arguments retain their existing ArgDigest and native
identifier/segment/PDB checks. Native JSON/HTML format is fixed by the reader;
foreign declared context, invalid bytes, duplicate keys and native identity/shape
mismatches cannot produce qualified source output. Missing files retain unavailable
acquisition rather than an empty biological result. No generic card option is added.


Development ordinary tissue views and their explanations share `usage_rule`
digestion. A per-method guard refuses a variant rule on an isoform method (and the
reverse), also when digestion is skipped. Defaults are `pext_at_variant@2` and
`isoform_exon_usage@3`; explicit prior versions retain historical behavior. All four
methods validate finite dimensionless `threshold` in [0, 1]; booleans, nonnumbers,
nonfinite values and oversized integers fail through SMonitor/ArgumentError.
