---
summary: Selective, bounded machine access sharing Card exploration science and captured inputs.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-21
closed:
verification: inspected
area: [public-api, agent-access, human-exploration, documentation]
blocked_by: []
supersedes: []
---

# Card agent access v1 contract

## Status and boundary

The maintainer requires two access experiences: friendly scientific exploration
for a researcher; technical, economical and complete access for an agent. This
document selects the local machine-access contract alongside the
[human v1 contract](card_exploration_v1_contract.md). It is a design, not an
implemented API, a benchmark or a new shared MOLI query/packet standard.

Current implementation boundary: the
[initial literal-access slice](card_access_literal.md) now implements `Card.access`,
discovery/read/selection lookup, bounded pages and raw export. Scientific
`select`/`explain`, human `explore()` and portable saved exploration below remain
planned. Query capabilities before using a designed operation; this document is
the full target contract, not a claim that all of it is delivered.

The common captured context, scientific adapters, result/item identities,
source assertions, quantity expectations and rule versions belong to the same
implementation. Machine requests do not parse human prose/HTML and do not need
human navigation history. There is no second scientific engine or LLM dependency.
Unknown Card natures get complete literal access, not invented scientific views.

Existing `get`, `extract`, `relationships`, views, `KnowledgeQuery`, packet formats
and acquisition functions remain unchanged. Current full/index queries are
protein-oriented; an index can contain every item reference. Neither it nor the
proposed human `rows()` promises bounded output. Reuse their readers, without
silently extending historical signatures or formats. A changed shared query or
packet contract needs coordination through [MOLI #22](https://github.com/uibcdf/moli/issues/22).
This design adds no server, MCP tool, autonomous acquisition or project reasoning.
0.15.0 consolidation remains paused.

## 1. Entry, discovery and explicit selection

Select `card.access(related_cards=()) -> CardAccess` as a direct machine entry.
It uses exactly the same capture factory as `card.explore(related_cards=())`.
`explorer.access` returns a facade over that explorer's existing capture/cache;
it never recaptures the live Card. Independent calls capture independently.
All guarantees for anonymous Cards, duplicates, revisions and cross-Card ambiguity
remain those of the human v1 contract. A related Card is never chosen by recency.

`CardAccess` and `AccessSelection` are read-only Python objects with terse reprs
containing handles/counts/capabilities, not automatic scientific payload dumps.
Only explicit page retrieval produces the machine envelope. Arguments use
ArgDigest, per-argument digesters and SMonitor diagnostics; schema selectors and
backend semantic guards apply even with digestion skipped. These are ordinary
Python APIs, independent of any agent vendor or tokenizer.

| Operation | Selected behavior |
| --- | --- |
| `access.catalog(kind="topics", locator=None)` | Return an `AccessSelection` over descriptors, without running scientific adapters. Kinds are `topics`, `fields` and retained `selections`; fields default to immediate children of the full captured Card root, or of the supplied literal location. A locator is valid only for `fields`. Topic descriptors include scientific options, selectable columns, mandatory qualifiers, declared types/quantity expectations and supported operations. Large descriptors use inspectable locations, not unbounded inline schemas. |
| `access.select(topic, *, fields=None, where=None, item_refs=None, order_by=None, options=None)` | Explicitly materialize/reuse the same scientific result as the corresponding human view; return an immutable `AccessSelection` with recorded effective request. No implicit source access. |
| `access.selection(selection_ref)` | Return an exact already retained selection by its `XA_` handle, including its original projection/filter/order. Foreign or unretained handles fail; no request reconstruction or adapter execution. |
| `selection.page(*, limit=32, max_bytes=65536, cursor=None)` | Return one bounded structured envelope over the fixed selection. No scientific adapter rerun, source access or new scientific credit on page reads. |
| `access.read(location, *, text_slice=None)` | Select literal children of a container or one scalar at a captured Card/result/selection location. It does not recursively inline a subtree or classify extension content. A text slice is an explicit partial-text operation described below. |
| `access.explain(item_ref)` | Select the original explanation already materialized for that result/item, including its effective options and alternatives. Large explanation content is traversable through `read`; this does not rerun a scientific reader. |
| `selection.save(path, *, overwrite=False)` | Use the shared exploration bundle, retaining the underlying full semantic result, original support closure and machine selection. Return the shared save receipt; this is explicitly not a small projection-only export. |
| `access.export_card(path, *, overwrite=False)` | Explicit bulk export of the focal captured Card in the existing sealed Card format, with atomic publication and default refusal to overwrite. Return path, original snapshot identity and file SHA-256; no new Card serialization or live refresh. |

The access facade reads an existing context; it never substitutes
`knowledge_packet(...)`, which can acquire knowledge. Exact source refs or
generated locations open only retained context. A reference to an unsupplied Card
produces `context_not_supplied` with its available relationship support.

### Selection grammar

- `topic` is an exact catalog key. Unknown keys fail with `ArgumentError`; known
  unsupported scientific routes report their outcome and literal fallback.
- `options` contains only that topic's declared scientific arguments. Defaults
  are resolved and retained once. A changed region, threshold or rule version is
  a different scientific request/result; a projection is not.
- `fields=None` selects the adapter's declared compact default columns.
  `fields=[]` asks for item identity/state/support metadata without optional values.
  Otherwise use an ordered list of exact declared column keys, without duplicates.
  A string is normalized to one key; unknown keys fail. Nested data is reached
  through locations, not an implicit projection-expression language.
- `where` is a mapping of declared columns to typed equality values. Multiple
  conditions combine with AND. Empty means no display filter. Values use the same
  comparison/quantity rules as human `filter`; no regex, executable predicates,
  fuzzy identity or hidden scientific threshold is introduced.
- `item_refs` is optional exact membership in this result. Duplicates fail; foreign
  references fail rather than becoming no-match rows. An empty list explicitly
  selects nothing. `where` and membership intersect without identity merging.
- `order_by` is null (stable adapter order) or one mapping with `column`,
  `descending` and optional `unit`. It uses human sorting's type/dimension checks
  and missing-last policy. Ties preserve the adapter's deterministic item-key
  order, independent of source assertion/relationship insertion order.

Missing/conflicting values retain typed cell states. A null equality filter can
only match an explicitly present null if the column admits one; it does not select
unknown/unqueried records. Filters cannot erase scientific exclusions or change
source coverage. Missing filter-column values remain excluded display rows whose
counts and original cells can be inspected in selection metadata.

An `AccessSelection` binds the underlying `XR_` result, ordered item membership,
projection and effective filter/order/request. Its local `selection_ref` is
`XA_<sha256>` over `card_access_selection@1` plus that versioned canonical record,
excluding its own handle, cursor, page size and rendering. Typed quantity operands
use the provider codec. This is a Sabueso-local handle, not a new MOLI pin syntax.
Selections cache original results and explanations; pages are projections over
them. Materialization can still inspect the entire Card or build a full view:
small output is not a claim of cheap computation.

### Initial scientific column schemas

The adapters expose the following first-delivery columns, alongside the core
`label`/`kind` selectors. Extra native fields stay accessible by payload location;
they are not silently promoted to selectable columns. The catalog declares the
actual scalar/list/union types and per-cell quantity expectations.

| Topic | Selectable value/context columns | Default projected columns |
| --- | --- | --- |
| Protein `function` | `field_path`, `value` | Both |
| Protein `structures` | `structure_ref`, `method`, `resolution`, `chains`, `coverage`, `coverage_class`, `state` | `structure_ref`, `method`, `resolution`, `chains`, `coverage` |
| Molecule `chemistry` | `field_path`, `value` | Both |
| Molecule `properties` | `field_path`, `value` | Both |
| Disease `definition` | `field_path`, `value` | Both |
| Disease `classification` | `subject_ref`, `predicate`, `object_ref` | All three |

`value` is typed per item; the catalog declares its union rather than forcing
quantities, formula strings and dimensionless properties into one numeric type.
Canonical `field_path` is mandatory item identity for field-grain rows even when
not explicitly projected. It is the economical exact selector for agents; a
translated human label never changes that field's scientific identity. Rules and
interpretation/support metadata remain mandatory independently of these columns.
Filtering or ordering heterogeneous `value` requires a `field_path` equality
discriminator unless the selected scope already has one declared compatible type
and physical dimension. Resolve that scope before validating value operands; do
not let mapping insertion order decide validation. Wrong units/types for that
declared field are errors, not silent no-match rows.

## 2. Response envelope, projection and scientific meaning

Every page is finite JSON data, format `sabueso.card_access_page@1`. A Python
mapping and its canonical UTF-8 representation carry the same scientific data.
JSON is produced only on explicit request/serialization, not in object repr.

| Required member | Meaning |
| --- | --- |
| `format`, `selection_ref`, `result_ref` | Wire version, fixed access request/selection and underlying semantic result. Literal/catalog selections also use a declared result adapter; handles never imply a source assertion. |
| `context` | Focal Card ref or null, snapshot ID, mode (`live`/`saved`), profile/adapter identities and `context_location` for the complete captured-input/request/rule record. Related contributors retain exact owner locations on their items. |
| `outcome` | Original operation status/reason, independent of pagination and source coverage. Empty scientific inventory and empty display selection remain distinguishable in referenced request metadata. |
| `coverage` | Location of complete original scoped coverage, `detail="referenced"` or `"inline_complete"`, and `inspection_required` when scope/qualifier details were not included. A reference alone never claims that those details were delivered. |
| `items` | Selected item records, in the fixed order, with projected cells and mandatory interpretation/support metadata. |
| `page` | Offset, returned item count, known total or null, `complete`, `values_complete`, `next_cursor`, effective limits and optional blockage information. `complete` concerns item enumeration for this selection only; `values_complete` states whether all requested values and mandatory interpretation metadata for the returned items were inline. Neither claims global scientific/source completeness. |

Each scientific item retains `item_ref`, `kind`, exact subject/relationship refs
where applicable, original payload location, state, source-support locations/refs
and projected cells. A cell retains `state`, `reason`, its value or an explicit
`value_location`, original support basis and its field identity. A scalar, list,
boolean, zero, empty string and missing value remain distinguishable.

Adapters declare **mandatory interpretation metadata** associated with each value:
for example, a censored measurement's relation and assay context, a structure's
experimental/predicted kind and scope, or a selected conflicting field's conflict
state and alternatives route. These are not removable projection columns. No
generic rule invents scientific qualifiers for unknown extensions. Catalogs expose
the actual adapter requirements before a query is made.

If required qualifiers/support membership are too large to inline, the value is
replaced by a typed deferred cell: `state` and `reason` remain, `value_included=false`,
`value_location` and `interpretation_location` identify its complete retained
closure. The frame marks `inspection_required=true`. Do not emit a naked selected
value with an omitted censor/conflict/scope qualifier. Unknown comparability stays
unknown; projecting fewer fields cannot make measurements comparable.

Long lists, original source bodies retained on the Card, nested objects and
nonselected columns use exact locations, not string truncation. Whether a value
was inline or deferred is delivery metadata, not a scientific cell-state change.
A value location is an access path, not a new assertion or an authenticity claim.

### Quantities

Python scientific results use PyUnitWizard quantities. Wire cells containing
quantities use PyUnitWizard's `QuantityRecord` or `QuantityRecordBundle`, not bare
numbers, stringified quantities or a new consumer-owned unit codec. Known adapters
declare field/unit/dimensional expectations; readers verify the provider record
and that handshake. Native Card quantity nodes/seals remain unchanged when
traversed literally or exported. An unknown extension dictionary resembling
`{value, unit}` is not automatically a scientific quantity.

The existing [public inspection receipt](card_exploration_design_inputs.json)
already contains provider records for 1SUX's 2.0 angstrom resolution and the
molecule's 260.25 dalton molecular weight, with explicit field expectations. Use
these exact public examples for codec conformance; the existing receipt is not a
machine page and is not rewritten by this design.

## 3. Record/byte limits and pagination

Initial engineering defaults are 32 items and 65,536 bytes, independently bounded.
Admit `1 <= limit <= 256` and `1024 <= max_bytes <= 1048576`, integer values
excluding booleans. These are prototype defaults to measure, not demonstrated
optimal token budgets. The byte limit covers the **entire canonical UTF-8 JSON
envelope**, including source/quantity records, cursor and mandatory metadata,
without compression. It does not cover Python-object memory or agent tool framing.
No provider/tokenizer-independent exact token count is promised.

Pack the longest prefix that fits both limits, with complete atomic item frames.
Measure the final envelope after including pagination fields/cursor. Reduce the
prefix until it fits; never cut JSON, units, source refs or Unicode text. Oversized
optional data is explicitly deferred by location as above. If the next item still
cannot fit, do not skip it or return an advancing empty page:

- A fitting earlier prefix may be returned with `complete=false` and a cursor
  pointing to the blocked item; expose its blockage/required inspection location
  if that metadata itself fits.
- With no fitting next item, return an incomplete page with no progress cursor,
  `blocked={code: "item_too_large", location: ...}`. The caller may raise the limit
  within the admitted range, read its literal/deferred contents, or explicitly
  export. A requested selection is never reported complete merely because it was
  too large to deliver.
- If even mandatory envelope/error metadata cannot fit, raise SMonitor
  `ArgumentError` with reason `response_budget_too_small`. Do not violate the
  requested bound, substitute scientific absence, or promise that an external
  exception renderer fits that JSON limit.

`total` is the exact retained selection size after materialization when known;
unknown totals stay null. `complete=true` means no selected item frames remain and
no unresolved item-frame blockage; it says nothing about missing source knowledge
or deferred values/details. `values_complete=false` and explicit locations prevent
a terminal index/projection page from masquerading as complete delivery of values.
`returned=0` can only be terminal empty selection or explicit blockage. Byte and
record ceilings cannot silently remove members.

### Cursor binding and lifecycle

Cursors are opaque session-local tokens backed by retained lookup records, not
caller-editable offsets, trusted base64 JSON or a claim that a digest authenticates
data. The access context records each token's format, selection/result identity,
capture, next position and deterministic ordering. No TTL clock influences a
scientific result. Tokens live while that access session retains their selections;
releasing the session invalidates them. There is no silent cursor eviction that
recomputes a view. A future explicit cache eviction API must report invalidation.

Use a cursor only on the originating selection in that session. Malformed,
foreign-session, foreign-selection and unretained tokens fail with
`ArgumentError`, never restart at page zero or move to current/latest data.
Retries of an existing token with the same limits return the same data and stable
continuation. Changing limits changes only the prefix length/encoding, not the
selection. Source Card mutation, SDK version changes or a modified session default
cannot change an already materialized result. A new access session/request is
explicit.

Cursor creation/validation is not a security boundary or authorization credential.
No network service is introduced. Persisted results use the shared saved bundle;
ephemeral cursors are not portable bookmarks.

## 4. Literal locations, large text and complete access

Locations on the machine boundary are versioned, typed mappings, not strings to
evaluate. The reader accepts only generated/validated locations:

- `kind="card"`: owner Card pin or null, snapshot ID and typed segments
  `Key(value)`, `Record(id)` or `Index(n)` from the human literal locator contract.
  Keys containing dots stay literal; ID-bearing assertion/relationship stores use
  records, never insertion indices.
- `kind="result"`: retained result reference and typed segments within its
  materialized payload/explanations/coverage. No reader execution on a miss.
- `kind="selection"`: retained selection reference and typed segments for its
  effective request/projection/filter/order and display exclusions.

The location format is `card_access_location@1`. Context owners are explicit;
segments do not redefine molecular sequence/structure `Location`. Exact pinned
assertion/relationship refs already carried by a result can be resolved to these
locations; this does not grant arbitrary store access. A missing retained owner
is explicit missing context or `not_saved`, not permission to find a newer one.

`read` of a mapping/list returns immediate-child descriptors, each with original
key/index/record ID, type and child location. Child enumeration is paginated and
does not include a full large scalar or subtree by default. `read` of a scalar
selects its complete value if it fits, otherwise a descriptor with exact length,
deferred location and a size reason. Empty containers still have explicit type
and count; false/zero/null/empty text are not empty containers.

For strings only, `text_slice={"start": n, "stop": m}` selects an exact half-open
Unicode code-point interval, with `0 <= n <= m <= length`. The response states the
original location, original total length, selected range, `partial` and exact
text. No Unicode normalization or approximate quotation is performed. A large
requested slice that cannot fit is deferred with the same range/length information;
the caller requests a smaller range. Other scalar types reject text slicing.
An empty slice at a valid boundary is valid partial content, not a missing field.
This is literal transport, not a new scientific finding or a source-stated fragment.

Very long keys, owner refs or locator descriptors can themselves exceed the
response bound. Do not cut them or claim complete enumeration: report the blocked
item with a compact session-owned lookup handle if that fits; otherwise use the
explicit budget error and bulk-export route. Such a handle resolves only to its
original captured location in the same session and has the cursor lifecycle's
no-fallback guarantees. It is not a new global identity.

Exhausting immediate-child pages, following every child and explicitly retrieving
all text ranges recovers original nodes/values/types without a whole-Card prompt
where their mandatory frames fit. Explicit bulk export provides lossless access
when a mandatory atom/frame exceeds the maximum bound or iteration is costly.
Record-store order is not a scientific identity; ordered-list indices remain
snapshot-bound. Do not claim that every pathological key/record fits a small page.
The whole captured Card can contain more than the visible query, including unknown
extensions. No article/runtime sidecar is implied if it was never retained.

## 5. Shared results, saved mode and bounded first delivery

The human and machine facades reuse results keyed by captured inputs, scientific
adapter, effective options and rules. Projection/filter/order affect selection,
not scientific `XR_` identity. Presentations must not secretly compute a different
classification, omit alternatives or apply another default threshold.

Saving a machine selection extends the **unpublished design** of the existing
`sabueso.card_exploration@1` bundle: retain its exact selection record, projection,
original semantic result, captured Cards, support/interpretation closure and
available adapter versions. No new saved scientific format is introduced and no
published artifact is edited. The shared validation checks original membership,
values, qualifiers, field/support bindings, provider quantities and independently
verifiable recorded decisions. Current readers never recalculate science merely
to construct a machine page.

The saved machine entry is a presentation over the original result/selection;
`root_view_ref` remains an `XV_` handle. Its capability manifest also records
`root_machine_selection_ref` (the original `XA_` handle). The reopened root remains
a `CardView`, compatible with the shared reader contract. Its access facade's
`selection(root_machine_selection_ref)` restores the exact retained machine
selection; the `selections` catalog provides paginated discovery of other retained
requests. Cataloging selections uses a fixed catalog snapshot so enumerating it
does not recursively add its own newly created descriptor selection to that list.

Reopen with the shared `read_exploration`; `.explorer.access` has `mode="saved"`.
Query only retained scientific variants; absent variants report `not_saved`.
Literal inspection and projections over retained results are allowed. Saved
selections obtain new local cursors; old session cursors are rejected. The explicit
shared `start_new()` boundary remains necessary for a new live interpretation,
without fetching sources or changing the original. Projection cannot launder an
invalid/tampered saved input into a small apparently valid page.

Implement as part of shared slices A–D, not a competing parallel science roadmap:

| Slice | Machine delivery alongside the human contract |
| --- | --- |
| A | Shared capture, field/topic discovery, generic read, exact locations, bounded envelopes and page cursors |
| B | Select/projection/equality/order over the initial nature-specific scientific adapters; exact quantity and interpretation metadata |
| C | Same explicit retained-context joins, ambiguity/revision outcomes and original support/explanation access |
| D | Shared self-contained saving, validated inert reading, fresh local cursors and explicit new interpretation |

Activity/clinical/comparative/site/variant rich panels retain the broader human
catalog's deferred status. Their retained nodes are reachable literally, without
advertising an unimplemented scientific machine adapter. No semantic duplication
or new source provider is needed to deliver this access layer.

## 6. Proposed calls and acceptance

These are proposed calls, not executed API transcripts. `protein` and `molecule`
are already loaded public Cards from the
[verified input inspection](card_exploration_design_inputs.json).

```python
machine = protein.access()
topics = machine.catalog()
topic_page = topics.page(limit=8, max_bytes=8192)
selection = machine.select(
    "structures",
    fields=["method", "resolution", "coverage"],
    where={"structure_ref": "pdb:1SUX"},
    options={"include_fragments": False, "region": None},
)
page = selection.page(limit=1, max_bytes=8192)
if page["items"]:
    explanation = machine.explain(page["items"][0]["item_ref"])
    explanation_page = explanation.page(limit=8, max_bytes=8192)
```

The supported scientific values remain 1SUX, X-ray, 2.0 angstrom and coverage 1.0
under the original rules; the coverage's interpretation limit remains required.
Source support is the retained UniProt/RCSB relationship support, not invented
per-qualifier lineage. Do not claim that this proposed envelope fits 8,192 bytes
until the complete serializer measures it. Byte ceilings may defer value/detail.

```python
properties = molecule.access().select(
    "properties",
    fields=["value"],
    where={"field_path": "properties.physchem.molecular_weight"},
)
first = properties.page(limit=1, max_bytes=8192)
rest = first["page"]["next_cursor"]
if rest is not None:
    following = properties.page(cursor=rest, limit=1, max_bytes=8192)
```

The original 260.25 dalton quantity, ChEMBL support and unstated-method
qualifier remain unchanged. A subsequent page cannot switch to a newer molecule
Card. Disease classification uses the same access mechanics with its own columns
and retained MONDO edges; no missing parent Card is synthesized.

| Required conformance exercise | What must be established |
| --- | --- |
| Human/machine parity for all initial natures | Same scientific result/values/options/units/support/unknowns despite different presentations and projections |
| Discovery and sparse selection | Catalog does not run all views; a request for one field does not serialize the whole Card or lose its support binding |
| Exhaustive reconstruction | Traverse all nodes, dot-containing keys, ordered lists, ID stores, seals, unknown extensions, Unicode text chunks and empty/false/zero/null values without loss |
| Pagination | Exact byte/record bounds on the final envelope; deterministic ties, no omission/duplication, retry idempotence, mutation isolation and explicit oversized-item handling |
| Invalid/foreign selectors | Bad columns/types/units/refs/options/cursors are errors; legitimate no-match is not a failed source query |
| Interpretation closure | Censoring, identity ambiguity, conflicting alternatives and scope qualifiers cannot disappear behind a compact naked value |
| Quantities | Provider record and field/unit handshake, non-default session policy, wrong dimensions, malformed/tampered record and atomic delivery |
| Saved reading | Independent process, original variants/qualifiers, fresh cursors, historical original support; no source calls, scientific adapter execution or new credit |
| Economy and cost | Measure canonical bytes and optional named-tokenizer tokens on declared public tasks; report capture/materialization/page time and memory separately. No invented saving percentage or fixed runtime guarantee |

Tests may use synthetic oversize/conflict/Unicode/cursor mutations labeled as
contract cases. They are not source assertions. No runtime/response-cost/human
acceptance is claimed by this document. The next implementation checkpoint should
build shared capture plus bounded literal discovery/read, then one complete
scientific route and its source expansion, before broadening the catalog.
