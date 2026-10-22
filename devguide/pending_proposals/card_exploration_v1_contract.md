---
summary: Concrete v1 contracts resolving the five pre-implementation exploration findings.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-21
closed:
verification: inspected
area: [public-api, human-exploration, scientific-views, documentation]
blocked_by: []
supersedes: []
---

# Card exploration v1 contract

## Status and scope

This contract resolves the five design gaps in the
[detailed proposal](card_exploration_detailed_design.md#pre-implementation-review)
at the maintainer's request. It is the current concrete design for the first
delivery; the broader nature-specific catalogs remain the development target.
Names below are selected for this design; only the subsets linked below are
implemented, and no measured usability is claimed. The maintainer has now authorized bounded implementation;
0.15.0 consolidation remains paused. The subsequent
[human/agent distinction](card_human_exploration_api.md#human-and-agent-access-to-the-same-knowledge)
shares this structured foundation. The additive
[agent access contract](card_agent_access_v1_contract.md) now specifies bounded
machine responses over the same captures/results, including projection, cursor
binding and exact quantity/support access. Human rendering is not an agent
transport protocol. Both contracts still require implementation and validation.
The [initial literal machine slice](card_access_literal.md) now delivers capture,
typed stored-content access, bounded pages and raw export; it does not implement
the complete A–D contract below. The [human literal continuation](card_exploration_literal.md)
now delivers generic interaction objects, original-support inspection and bounded
text/HTML over that same capture. The [first structural adapter](card_structures_exploration.md) now adds shared
inventory/explanation and typed human selection with projected machine pages.
The [first protein journey](card_protein_exploration.md) adds its scientific opening,
function fields, explicit function/region questions and original-source return path.
The [nature/coverage continuation](card_nature_exploration.md) now implements initial
molecule/disease field/relationship routes, their question aliases and original
knowledge-state views with lazy scoped explanations.
The [contextual navigation continuation](card_context_navigation.md) now delivers
initial retained source/endpoint links and explicit supplied-Card transitions,
including missing context and revision choices. The
[first saved-reading continuation](card_saved_exploration.md) delivers supported
literal/field and navigation persistence. The
[scientific continuation](card_saved_science.md) now retains original structures,
canonical-region answers and coverage with historical verifiers. Broader scientific
adapters, remaining machine conformance, measured costs and human acceptance stay open.

Share navigation and integrity contracts; retain separate protein, small-molecule
and disease scientific profiles. Every valid Card passing the current reader,
canonical serialization, snapshot and quantity contracts
gets complete literal inspection, including a Card with no recognized nature.
An unsupported schema or failed quantity integrity check remains an explicit
storage error, not permission to present unverified scientific values.

The [public input inspection](card_exploration_design_inputs.json) verifies the
facts used in the paper walkthroughs below through existing local SDK readers.
The proposed exploration API was not executed. Original inputs were unchanged,
online access was forbidden, and no private/pilot content was used.

## 1. Result, item and presentation model

### Public objects

| Object | Required public state and behavior |
| --- | --- |
| `CardExplorer` | Read-only captured Card context, profile, mode (`live` or `saved`), catalogs and explicit view operations |
| `CardView` | Scientific result binding, outcome, coverage, capabilities, presentation/selection and navigation origin |
| `CardItems` | Read-only sequence of the currently selected, ordered `CardItem` objects; supports iteration, length, integer indexing and slicing |
| `CardItem` | Readable `label`, `kind`, stable `item_ref`, named cells, original payload location and support; `open`, `explain`, `related`, `back` |
| `Cell` | Typed value, state, reason and support; quantity values are PyUnitWizard quantities; mutable returned values are defensive copies |

Ordinary exploration uses objects, labels and named columns. References and
payload locations remain available for exact programmatic work; they are not
required to open an item. No object exposes a mutable captured Card/store.
`CardExplorer.access` exposes the machine facade over this same capture/cache;
`card.access()` is its direct entry, without requiring human navigation. These
entries share a capture factory and scientific adapters, not separate rules.

A semantic result records all of the following, even when the concise renderer
does not print them:

| Record field | Contract |
| --- | --- |
| `result_ref` | Component-local deterministic result handle, described below |
| `context` | Focal Card pin or null, snapshot identity, profile/adapter versions, all contributing captured Card pins, effective scientific options and original scientific rule identifiers |
| `outcome` | Operation status and reason, independent of source knowledge coverage |
| `coverage` | Original scoped source/area states, limits, failures and unknown denominators; never inferred from a missing display row |
| `schema` | Item kind, row grain, column keys/labels/types, quantity field/unit expectations and supported presentations/operations |
| `items` | Native admitted items, their typed cells, support and original payload locations; full values are retained |
| `exclusions` | Original scientific exclusions and their actual reasons/support, distinct from later display filtering |
| `native_payload` | Original scientific reader output, including material not in the default columns, with declared quantity encoding at persistence |
| `explanations`, `links` | Original item explanations and supported destination records prepared from the captured context |

Cell states are `present`, `unknown`, `not_retained`, `not_applicable` and
`conflicting`. An existing selected value may remain visible in a conflicting
cell, accompanied by alternatives and support. Zero, false, empty text, absent
value and unavailable source coverage are not interchangeable. A null value does
not independently establish `not_stated` by a source.

Support entries state their basis: original assertion, relationship-level support,
stored metadata location, named derived rule/input or unavailable support. Stored
metadata is not relabeled as a SourceAssertion; relationship support is not invented
as lineage for every individual qualifier. Derived findings retain their original
rule and inputs rather than receiving fabricated source statements.

Adapters read original scientific outputs, not flattened legacy table strings.
They prepare their original explanation/support records during explicit result
materialization, reusing existing readers and original effective rules/options.
Later display, selection and item explanation read that materialized result.
They do not call the scientific view again. Support is shared by pinned reference;
do not embed a full Card in every item.

### Identity and display state

`result_ref` has the component-local form `XR_<sha256>`. Its versioned digest
input includes input snapshot identities, profile/adapter identity, topic,
effective scientific options, original rules and the canonical scientific payload.
Canonical payload encoding uses declared adapter schemas and PyUnitWizard codecs,
not a session's display form. Navigation, column visibility, sorting, preview
limits and display filters are excluded. These are not new shared MOLI pin formats.

The digest is computed from a versioned identity projection before adding result/
item handles: semantic item keys, values, original support and inputs are included,
while the newly generated handles, cached renderings and navigation are excluded.
Do not hash a record that recursively contains its own digest. Literal native
fields that happen to have similar names are not dropped by a generic key filter.
Adapter identity schemas separate original scientific rule/parameter data from
SDK producer/runtime metadata: the latter is retained and covered by artifact
digests, without changing a semantic result solely because a documentation commit
changed the producer's development version. Source-record revisions remain part
of the scientific input, not excluded producer metadata.

`item_ref` is `XI_<sha256>` over the result reference and typed semantic item key.
Stored records use pinned record IDs; fields use their captured literal path;
derived groups use their original rule and full member keys. Use IDs for assertion
and relationship stores, whose canonical snapshot hash ignores list order.
Ordered list positions are valid only within the bound snapshot's actual ordered
collection. Sorting a view never changes an item reference.

Each `CardView` separately retains its presentation, current selected item refs,
filter/order specification, focused item and finite navigation trail. These do not
change the scientific result. A filter cannot change a class, grouping, native
exclusion, source join or threshold. Changed scientific options create a new result.
`view_ref` is `XV_<sha256>` over the versioned result/presentation/selection record,
excluding its own handle and navigation history. The saved finite navigation trail
can therefore reference the same scientific/presentation state at different steps
without recursive object serialization or changing item identity.

### Rows and presentations

`items()` exposes all current selected items, independent of the renderer's
ten-row preview. `rows()` returns a list of defensive structured records:

```text
{item_ref, kind, label, cells: {column_key: CellRecord}, support, payload_location}
CellRecord = {value, state, reason, support}
```

This is a lossless row contract, not the current flat `Card.table()` contract.
Lists, nested values, quantities, missing reasons and references remain structured.
Existing flat-row/DataFrame APIs remain unchanged; do not pass these new structured
rows to the legacy converter and imply that the resulting frame is an equivalent
exploration artifact. A future convenience projection must declare its losses and
retain units and item/context bindings.

`summary()` and `table()` return presentation views over the same result.
An unsupported table presentation returns a view with outcome `not_applicable`,
a reason and an available detail route; it does not invent an empty scientific
table. In v1, overview/detail presentations need not be tabular. Scientific views,
inspection, catalogs, links and source explanations declare their own table grain.

## 2. Selection and navigation

Selected candidate interface additions to the detailed proposal:

| Call | Exact behavior |
| --- | --- |
| `view.items()` | Read-only `CardItems` for all currently selected items |
| `view.items()[i]` | Select the item at this display position now; the returned object binds its stable reference, never the integer as an identity |
| `item.open()` | Return its detail view, or follow it when it is a link/route item; the action is explicit and source-free |
| `item.explain()` | Return the original materialized explanation, including alternatives and effective scientific context |
| `item.related()` | Return a link view with declared roles, destinations, availability and identity/support basis |
| `view.item(item_ref)` | Advanced exact lookup in the original result, also for display-filtered items; show their exclusion from the current selection |
| `links.follow(item_ref)` | Advanced alias for opening the referenced link item; reject a non-link or foreign-result reference |
| `view.back()` | Return the originating `CardView`; at the root return the same root view with `at_root=True` |
| `item.back()` | Return its originating selected/ordered view |
| `view.explorer` | The focal captured Card's explorer, or null for destination context without a supplied Card; its mode is explicit |

`item.related()` has the item's detail view as origin, even if the user did not
first call `open()`. Opening a link retains that link view as origin. Exploring a
supplied destination Card switches to its own profile; going back preserves the
original source view and selection. Navigation cycles do not recursively expand
Cards: the trail records actual user steps and references captured objects.

The first v1 filter remains `filter(column, equals=value)`. It checks a declared
column and typed value. Missing/conflicting cell states remain inspectable; a
missing value is excluded with its display-selection reason rather than read as
a negative measurement. `sort(column, descending=False, unit=None)` puts missing
values last. Heterogeneous incompatible values are rejected with an explanation.
Mixed compatible quantity units require an explicit target `unit`; no session
default decides order. Region/range/scientific thresholds use declared topic
options, not an implicit predicate language.
`label` and `kind` are declared core columns on item views, so a researcher can
select a visible scientific label without knowing a canonical stored field path.
Equality uses the complete recorded column value, never a truncated rendering.
Filtering by a label selects matching rows; it does not merge their identities.

No-match filters produce a legitimate empty view with the original result and
coverage retained. The previous view is available through `back()`. Bad columns,
wrong dimensions, malformed references and unsupported argument names raise
ArgDigest/SMonitor `ArgumentError`; an out-of-range sequence index is ordinary
`IndexError`. Users can inspect `len(items)` or iterate without indexing empties.

## 3. Captured context, joins and complete inspection

`card.explore(related_cards=())` captures valid Card payloads once and verifies
their existing quantity/snapshot contracts. A Card without `card_id` uses a local
snapshot binding, not an invented global identity; its generic data remains
inspectable. Subject-dependent scientific routes report their missing prerequisite.
Capture uses the current `Card.to_dict()` serialization, which may regenerate a
quantity seal through the existing codec. Preserve that captured payload and its
seal thereafter; do not claim the original file bytes or historical seal were
archived merely by capturing an in-memory Card. The existing semantic snapshot
identity and separately retained original-file hashes have different purposes.

| Supplied context case | Resolution |
| --- | --- |
| Repeated identical Card pin/content | Retain one capture and record the repeated input in context metadata |
| Same Card identity, different snapshots | Retain both pins; never choose latest by date or input order |
| Multiple matching destination pins | Return an `ambiguous` destination view with labeled candidate link items; opening one explicitly selects that pin for navigation |
| Several agreeing supported paths to the same pin | Retain all paths/support and one destination; do not discard alternatives |
| Conflicting identity paths | Return ambiguity with the conflicting paths; no automatic identity repair |
| Destination mentioned but no Card supplied | Show the retained relationship/entity context with `context_not_supplied`; no foreign Card fields, acquisition or invented identity |

Join only an exact pinned/Card record reference or a retained source-stated
identity path with its actual support. Use named rule `retained_context_links@1`
for this derived navigation finding and state its basis. Name/sequence similarity
and chemical-name/formula equality never establish identity. A path whose claimed
source basis is not retained is an explicit missing prerequisite, not a verified
join. Navigating to a revision is not a scientific resolution of conflicting values.

For context-only destinations, `view.explorer` is null and the presentation explains
how an explicitly supplied Card would enable further exploration. The available
retained relationship and its source can still be inspected. No empty molecule
or disease Card is synthesized to support an apparently successful transition.
Its focal Card/snapshot fields are null; the known target `subject_ref` and actual
contributing source Card pins remain explicit. An anonymous but captured Card is
different: it has a local snapshot identity even though its global Card ref is null.

### Operation outcomes versus source coverage

Outcomes are `ok`, `empty`, `context_not_supplied`, `ambiguous`, `not_saved`,
`not_applicable`, `unsupported` and `missing_prerequisite`, each with a reason.
They describe this operation, not what a source asserts. Knowledge coverage retains
the original per-source states and scope. In particular:

- missing target context does not mean no activity;
- an unavailable adapter does not mean a queried source found nothing;
- unqueried trials do not mean an empty registry response;
- a missing saved explanation is not a failed live source request.

Known catalogs expose only implemented specialized routes or explicitly available
literal routes. Unknown route names are argument errors with valid choices;
known unavailable capabilities have their typed outcome and available fallback.

### Literal traversal

`inspect()` starts at the full stored root, including seals and unknown content.
Canonical section paths remain dot-separated. Its item objects open dictionaries,
lists and leaves directly, so no new path syntax is needed for ordinary traversal.
Advanced `inspect(locator=...)` accepts the typed locators emitted by inspection:
`Key(literal_string)`, `Record(id)` for ID-bearing stores and `Index(n)` for ordered
lists, always bound to an input snapshot. Supplying both a field path and a locator
is invalid. A key containing dots remains one literal key in a locator.
The generated locator records its owner Card/snapshot and typed segments;
`item.payload_location` exposes it for `inspect(locator=...)`. This stored-node
locator does not replace the scientific sequence/structure `location` contract.

An inventory traversal must reach every retained node and original type/value,
including unusual extension keys and filtered/excluded source records. Literal
extension content is not assigned guessed scientific semantics. Declared schema/
adapter paths determine which values are physical quantities; an arbitrary native
dictionary resembling a quantity does not authorize a scientific conversion.

Local search initially uses Unicode case-folded literal substring matching over
retained keys, scalar textual/numeric representations and identifiers. It is not
fuzzy identity resolution, regex execution or natural-language inference. Hits
retain matched original text, snapshot-bound location and match context; render
limits do not remove remaining hits. Unsupported opaque content is reported in
search scope and remains reachable through literal inspection.

## 4. Saved results and explicit new exploration

Live result materialization retains original item explanations and links alongside
the scientific output, under its effective options/rules. Saving does not need
to rerun that scientific view. The cost of materialization is distinct from cheap
representation and must be measured on declared workloads.

`view.save(path)` writes one self-contained UTF-8 JSON bundle, format
`sabueso.card_exploration@1`, using a temporary sibling followed by atomic replace.
Refuse an existing destination by default; `overwrite=True` is explicit. A failed
write preserves the previous file. Validate the bundle before final replacement.
The return value is a receipt mapping containing `path`, `bundle_digest` and
`root_view_ref`; callers may retain its digest independently.

| Bundle member | Required contents |
| --- | --- |
| `format`, `producer` | Format identity, original SDK/adapter/profile versions and creation context |
| `root_view_ref` | Exact saved entry presentation and selection, distinct from scientific `result_ref` |
| `cards` | Every contributing capture, once, in the existing `Card.to_dict()` format with its captured seal and exact snapshot binding |
| `results` | Original native results, typed items/cells, exclusions, original explanations, links and effective scientific inputs/rules |
| `views`, `navigation` | Entry view and finite originating trail, including original filters/order and linked results actually materialized |
| `capabilities` | Exact retained view/topic variants, explanations, links and unavailable/not-saved destinations; source coverage is separate |
| `digests`, `quantities` | Canonical member/bundle digests and PyUnitWizard-owned quantity records for result quantities outside Card payloads |

Save the full semantic result, including display-filtered items, and the originating
trail/support closure. Do not derive every unvisited topic. Missing explanation
payload for a first-slice item declared explainable is a save error, not silent
downgrading. Previously unmaterialized scientific views remain `not_saved`.
Whole contributing Cards may contain more than the visible selection: the save
contract and representation state this clearly. Source response archives, article
bodies and runtime sidecars are excluded from v1; retained references and missing
bindings remain visible. No new acquisition credit is produced by reading/saving.
The [machine facade](card_agent_access_v1_contract.md#5-shared-results-saved-mode-and-bounded-first-delivery)
uses this same unpublished bundle design. Saving a machine selection additionally
retains its exact projection/filter/order/request record; it still includes the
underlying complete result and captured Cards, not just a small page. Ephemeral
session cursors are not portable; saved readers issue fresh local cursors over
retained results and never recompute missing scientific variants.

Use the provider's existing `QuantityRecord`/`QuantityRecordBundle` codecs, with
explicit field/unit/dimensional expectations declared by each known adapter.
Keep captured Card quantity seals unchanged. Do not invent a second unit format
or call the Card-specific sealing function on an arbitrary view payload. Canonical
digest input covers provider records and all non-quantity payloads. Existing source
nodes/qualifiers remain literal source values, with their original units/context.
The bundle digest is over canonical JSON excluding only its own digest slot;
member digests and provider seals remain covered. It is distinct from a raw file
byte hash. `expected_digest` and the save receipt refer to this canonical digest.

`sabueso.read_exploration(path, expected_digest=None)` validates known format and
adapter versions, quantities, member hashes, pins, referenced membership, original
field/support bindings and declared retention closure before returning a saved
`CardView`. A missing member declared retained, inconsistent quantity, changed
bound field or unsupported required version raises `StorageError`. Unknown optional
presentation metadata is preserved without inventing semantics.

Recorded criterion/expectation/decision consistency is checked by a versioned
independent verifier, as in existing saved-reader contracts; this does not rerun
an SDK scientific view or create a new classification. A required verifier that
is unavailable is an explicit unsupported-validation error. Original derived
fields beyond that verifier's scope are labeled recorded, not independently
verified. Integrity, support binding and derivation verification remain separate
reported scopes. Hashes alone establish neither source authenticity nor truth;
an independently retained `expected_digest` additionally checks the caller's
original bundle binding.

Saved-mode operations have the following fixed behavior:

| Operation | Saved behavior |
| --- | --- |
| Representation, `items`, `rows`, `open`, `filter`, `sort`, `back` | Use retained values/navigation only; no scientific reader or acquisition |
| `explain`, `related`, `follow` | Use the retained original payload; report `not_saved` for an explicitly unavailable non-required payload, never recompute |
| `inspect`, local search | Traverse captured literal data without new scientific classification or identity joins |
| `explorer.view` / `answer` | Exact retained-request lookup using saved effective/default bindings; otherwise `not_saved`, with available retained variants; never substitute current defaults |
| `explorer.start_new()` | Explicitly create a live explorer from the captured Cards using installed profile/readers; original saved results remain unchanged and the new result is labeled a new interpretation |

The saved explorer retains its mode and capability manifest. `start_new()` performs
no network access and does not follow a store's latest revision. A refreshed
external source state requires a separately explicit acquisition through existing
APIs. Query recipe execution is outside v1.

## 5. First delivery and adapter mapping

The first complete checkpoint consists of the following bounded slices. No step
can claim the whole long-term scientific catalog.

| Slice | Required delivery | Acceptance boundary |
| --- | --- | --- |
| A: capture and inspection | Immutable captures, result/item/cell model, literal traversal, discovery, original sources/coverage, basic search/filter/order | Every node of valid protein, molecule, disease and generic Cards is reachable; no source queries |
| B: scientific profiles | The adapters below, labeled item selection, original explanations and question aliases | One complete supported scientific route per nature, with verified public calls/responses |
| C: contextual navigation | Retained-node links and explicit related-Card captures; duplicate/revision/identity cases above | Exact destination selection and return, including missing and ambiguous context |
| D: portable saved reading | Versioned bundle, original support closure, independent validation, inert reader and explicit `start_new` | Original result survives Card mutation, installed-rule changes and independent-process reading |

| Initial topic/route | Existing stored paths/readers | Item/table grain and support |
| --- | --- | --- |
| Shared identity/content/sources | `Card.to_dict`, `entities`, `source_assertion_store`, `relationship_store`; preserved meta/quality/selection rules | One retained identity field, literal child or assertion record, with exact location and original support basis |
| Shared coverage | Explicit existing `knowledge_state()` / `explain_knowledge_state()` | One original source/area row; existing named rule and request-scope gaps retained |
| Protein `function` | Retained `annotations.function` when present, `annotations.catalytic_activity`, `sequence.length`, organism/name fields | One native statement/annotation; missing text is not inferred from an enzyme name |
| Protein `structures` | Native `structures(include_fragments, region)` output and original stored structural support | One existing inventory entry per item/table row, expandable to stored chain/assembly context; not a chain or independent experiment count |
| Molecule `chemistry` | `identifiers.inchikey`, SMILES/InChI, names, formula and retained `same_as` basis | One native identity/representation field, with source identity context; no computed chemistry |
| Molecule `properties` | Retained `properties.physchem.*` nodes, selected/alternative assertions and quality/selection records | One canonical stored property field per row; method-specific alternatives remain distinct in detail and explanation |
| Disease `definition` | Native MONDO definition, canonical name, scoped synonyms and term-status metadata | One retained field/statement, not a diagnosis or a new summary claim |
| Disease `classification` | Stored `subclass_of` relationships; equivalent/related identifiers remain accessible through identity context | One stored parent relationship per table row; equivalence lists are not fabricated as new stored edges |

Initial question aliases are protein `function`/`region_coverage`, molecule
`chemical_identity`/`property_context`, disease `meaning`/`classification`.
`answer()` dispatches to these same adapters; it never maintains a second result
engine. Region coverage requires an explicit supported sequence axis and region.
The disease classification answer includes a clearly labeled route to equivalent
identifiers rather than conflating them with hierarchy edges.

Broader activity/clinical/comparative/variant/site panels retain their detailed
designs but are not required rich adapters in the first slice. Their retained
information is reachable through literal/source inspection from slice A. Do not
advertise a deferred scientific panel as delivered or read its absence as no data.
Optional structure drawings, DataFrame projections, richer filters and query
recipes can follow without weakening complete access or source support.

## Public paper walkthroughs

These are complete proposed selections against verified public inputs, not runtime
transcripts of the future API. The input receipt retains the actual current SDK
inspection, pins and supporting records. Use an empty/negative variant alongside
each successful selection; synthetic negative cases must be labeled synthetic.
The snippets assume `import sabueso` and the indicated already loaded Card; they
specify exploration after explicit acquisition/loading, not a new acquisition route.

### Protein: TcTIM

The input is the original frozen schema 0.3.9 Card. The proposed opening reads:

```text
Triosephosphate isomerase, glycosomal · Protein
Trypanosoma cruzi · UniProt P52270 · 251 residues
Retained catalytic annotation: EC 5.3.1.1 (UniProt)
Saved Card, schema 0.3.9; current sources have not been queried.
Explore: function · experimental structures · sources · coverage · all content
```

```python
p = protein.explore()
structures = p.view("structures")
selected = structures.filter("structure_ref", equals="pdb:1SUX")
selected.table()
if len(selected.items()):
    structure = selected.items()[0]
    structure.open()
    structure.explain()
else:
    selected.summary()
```

The verified current-reader selection is 1SUX, X-ray, resolution 2.0 angstrom,
chains A/B and coverage 1.0 under that reader's retained scope. Its default native
view has seven admitted items; that is not a current worldwide structure count.
Detail/explanation shows original support and named coverage/state rules. A
filter selecting a nonexistent retained record returns an empty selection with
the same coverage; `back()` restores the inventory.

The selected detail presentation is proposed as:

```text
1SUX · Experimental structure
Method: X-ray · Resolution: 2.0 angstrom · Chains: A, B
Inventory sequence coverage: 1.0 (derived under the recorded rule)
This coverage alone does not establish coordinate completeness.
Relationship support: UniProt P52270; RCSB PDB 1SUX
Actions: original source detail · related retained context · back to inventory
```

### Small molecule: benznidazole

The input is built only from the existing supplied ChEMBL CHEMBL110 record. Its
proposed opening reads:

```text
BENZNIDAZOLE · Small molecule
Identity: ChEMBL CHEMBL110, anchored at the source-stated standard InChIKey
Available here: chemical identity and retained physicochemical properties
This example supplies no target Card and performs no trial acquisition.
Explore: chemical identity · properties · sources · all content
```

```python
m = molecule.explore()
m.view("chemistry")
properties = m.view("properties")
selected = properties.filter("label", equals="Molecular weight")
if len(selected.items()):
    weight = selected.items()[0]
    weight.open()
    weight.explain()
else:
    selected.summary()
```

The verified retained value is 260.25 dalton. Explanation shows ChEMBL_37,
CHEMBL110, original asserted text `260.25`, explicit source-unit context and the
normalized quantity. It does not label this an experimental measurement or infer
an unstated calculation method. Missing target context is shown separately from
what the record says about identity or properties.

```text
Molecular weight: 260.25 dalton
Source: ChEMBL_37 · CHEMBL110
Original asserted value: "260.25" · Source unit metadata: Da
Selected stored quantity: 260.25 dalton · Method not stated in this assertion
Actions: original assertion · alternative values, if retained · back to properties
```

### Disease: MONDO:0014221

The input uses the existing local MONDO fixture. The proposed opening reads:

```text
triosephosphate isomerase deficiency · Disease
MONDO:0014221 · ontology definition and classification context
Four parent relationships are retained in this supplied term Card.
Parent/target/drug Cards were not supplied; no additional sources were queried.
Explore: definition · classification · identity terminology · sources · all content
```

```python
d = disease.explore()
parents = d.view("classification")
selected = parents.filter("object_ref", equals="mondo:MONDO:0002908")
if len(selected.items()):
    edge = selected.items()[0]
    edge.explain()
    targets = edge.related().filter("role", equals="object")
    if len(targets.items()):
        parent_context = targets.items()[0].open()
        parent_context.back()
else:
    selected.summary()
```

The verified parent edge is retained with its actual MONDO assertion. With no
parent Card supplied, opening it displays the known parent reference and original
relationship support, outcome `context_not_supplied` and no invented parent
definition or molecular associations. That is useful retained context, not an
empty answer from a newly queried source.

```text
MONDO:0014221 — subclass_of → MONDO:0002908
Source: MONDO 2026-09-01 · Original relationship assertion retained
Destination: context_not_supplied
Available here: parent identifier and the statement supporting this relationship
Parent definition: no parent Card supplied in this exploration
Actions: inspect relationship source · back to classification
```

### Reopen exactly, then explicitly start a new interpretation

```python
selected.save("exploration.json")
saved = sabueso.read_exploration("exploration.json")
saved.table()
for item in saved.items():
    item.explain()
new_explorer = saved.explorer.start_new()
```

The saved table/filter, original explanations and support stay fixed even if the
live source Card changes. `start_new()` is the explicit boundary to installed
readers/rules; it does not alter the original result or refresh external sources.

## Acceptance and disposition of the review

| Review finding | Concrete resolution here | Remaining validation |
| --- | --- | --- |
| Result/item model | Typed objects, result/item identity, separate presentation, structured rows and adapter grain | Implementation/conformance tests |
| Selection/navigation | Readable item collection, explicit `open`, complete public selectors, root/back and context-only behavior | Python/Jupyter prototype and researcher walkthrough |
| Cross-Card scope | Exact captures, explicit ambiguity/revision rules, supported join basis and typed literal traversal | Duplicate/revision/identity and full-node coverage cases |
| Saved results | Versioned self-contained bundle, retained capabilities, original explanation closure, inert saved mode and explicit new interpretation | Codec/validation, mutation and independent-process qualification |
| First delivery | Slices A–D, exact initial adapters/aliases and verified public input facts | Build the bounded implementation only after scope agreement; measure usability separately |

These five contracts are resolved at design level. #148 remains open for
implementation and acceptance. Human usefulness is not established by this paper
prototype. Researchers unfamiliar with Sabueso must locate, select, explain and
revisit the examples without developer coaching, distinguish source/coverage
limits and recover from empty/ambiguous states. Record those results before
claiming the intended exceptional experience.

The implementation acceptance matrix must also exercise: a syntactically valid
source identifier absent from the captured view; duplicate identical inputs;
two revisions requiring explicit destination choice; conflicting identity paths;
a generic key containing dots and an ordered-list leaf; altered cells rehashed
against unchanged input Cards; missing required saved support; an unavailable
required historical verifier; and explicit `start_new()` without acquisition.
Synthetic variants of these cases are contract tests, not new source knowledge.
