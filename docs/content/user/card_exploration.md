# Explore a Card

**Development API:** this page describes the development checkout, after 0.14.0.
The released 0.14.0 package does not provide `card.explore()` yet. This first
version offers readable inspection, distinct protein/molecule/disease routes and
source knowledge coverage; broader scientific topics are still being built.

For a complete executable example using frozen public inputs, see
{download}`the three-Card walkthrough <../../../examples/user_journeys/card_exploration.py>`.
From the repository root, run its `produce --output <empty-directory> --fixtures
temp_data` command, then `read --output <same-directory>` in a separate process.
It covers TcTIM, benznidazole and a MONDO term, with source tracing, empty-filter
recovery and saved reading. No network access is needed.

Start with a Card you have already resolved or loaded:

```python
explorer = card.explore()
explorer.overview()
```

In a notebook the last expression displays a concise preview; in a terminal use
`print(explorer.overview())`. The opening shows the recorded name when available,
the Card's nature, retained record counts and any stored conflict notice. A protein
opening adds its retained organism, accession, sequence length, function/catalytic
annotations and source attribution, followed by routes into the knowledge. Counts
say how much is retained, not how completely the sources cover your system.
Molecules start with retained chemical identity and representations; diseases start
with ontology definition and scoped terminology. Neither opening calculates new
chemistry or interprets a term as a diagnosis.

The explorer captures the Card once. Later changes to `card` do not change this
exploration. It works locally: opening, searching and reading support do not
refresh sources. `mode="live"` describes an active local exploration context,
not live source freshness.

## Discover and open content

```python
topics = explorer.topics()
topics
```

Shared topics are **Explore all content**, **Source statements** and
**Knowledge coverage** and **Stored quality records**. Protein Cards also offer
**Protein function**, **Experimental structures**, **Sequence and annotations**,
**Predicted models** and **Sites and contact statements**; molecules offer **Chemical
identity** and **Physicochemical properties**; diseases offer **Disease definition**,
**Disease classification** and **Identity terminology**.
Only available routes appear. Open a topic
from its displayed index, or use its public key:

```python
content = explorer.view("content")
choice = content.filter("label", equals="Knowledge")
knowledge = choice.items()[0].open()
knowledge
```

`Knowledge` is a root label, so you do not need to know the Card's internal paths.
Inspect the displayed labels, then open an item by its current index. `items()`
contains every selected item, including those beyond the ten-item preview:

```python
for item in knowledge.items():
    print(item.label)

assert knowledge.back() is choice
```

Every item binds its original identity and location; its display position is not
an entity identity. `item.back()` returns its selected view, and `item.open().back()`
returns that same view. At the root, `back()` stays at the root.

## Inspect support and conflicts

Open source statements directly:

```python
sources = explorer.view("sources")
if len(sources.items()):
    statement = sources.items()[0]
    statement.open()  # complete original record
    statement.explain()  # original support context
```

For a selected knowledge field, `item.explain()` exposes its retained source
references, selection metadata and stored conflicts when present. A referenced
statement that was not retained is explicitly marked `not_retained`. A relation's
support remains relationship-level support; it is not invented individual lineage
for every qualifier. All original fields remain reachable with `open()` or
`native_payload`, including information absent from the concise columns.

A conflicting value stays visible alongside its original conflict details.
Stored zero, false, empty text and null remain distinct. A null value by itself
does not mean a source stated that information was absent. The coverage topic
uses the existing knowledge-state classifier for supported natures, as described
below. `explorer.view("quality")` opens the original quality/enrichment records.
Generic unrecognized natures retain literal coverage/quality inspection.

## Search, select and read complete values

```python
matches = explorer.search("triosephosphate")
matches.table()

alphabetical = content.sort("label")
selected = content.filter("label", equals="Knowledge")
```

Search matches literal keys and scalar values with Unicode casefold. It retains
all hits and their original locations; it is not a semantic search. For literal content, display filtering and sorting support `label` and `kind`.
The structural panel below adds its declared scientific columns. They never
change scientific classes, source admission or the underlying result.

Previews abbreviate long values and show at most ten items, with the omitted
count. Complete values are explicit:

```python
complete_rows = selected.rows()  # structured rows, including typed cells
complete_node = (
    selected.native_payload
)  # original result node, before display filtering
```

`rows()` may return substantial data; its cells preserve values, state, reason
and support. Declared quantities are PyUnitWizard quantities, with original units
retained. The original payload keeps the Card's sealed `{value, unit}` encoding.
Unknown extension values remain literal and inspectable. For a convenient known
section field, use `explorer.inspect("names.canonical_name")`; keys that themselves
contain dots are reached through items or exact typed locations.

## Ask about protein function

For a protein, discover the available questions before choosing one:

```python
questions = explorer.questions()
questions
function = explorer.answer("function")
function
```

This opens the same retained fields as `explorer.view("function")`. The panel
separates function description, catalytic activity, pathways and identity context.
Its value cells contain the actual field values; `item.open()` keeps the complete
original field node. It never infers a function from the protein name.

In the public frozen TcTIM Card, the reaction and EC 5.3.1.1 are retained from
UniProt, while a textual function description is not retained. Those are different
facts. Review the actual supporting statement and return to your selected answer:

```python
catalytic = function.filter("label", equals="Catalytic activity")
if len(catalytic.items()):
    annotation = catalytic.items()[0]
    support = annotation.explain()
    support  # readable original source records
    if len(support.items()):
        source_record = support.items()[0].open()
        source_record.native_payload  # original asserted value, version and retrieval
        assert source_record.back() is support
    assert support.back() is catalytic
    assert catalytic.back() is function
```

Missing original records remain explicit in `support.native_payload`; stored
conflicts, selection rules and alternatives remain there too. No source record is
invented for a field without attribution. `function.native_payload["field_gaps"]`
distinguishes absent supported fields from unrecognized retained shapes. The
latter stay reachable with `inspect()`. Field inspection does not classify source
coverage or establish biological absence.

## Read a protein sequence and its source annotations

```python
sequence = explorer.answer("sequence_annotations")
sequence.table()
primary = sequence.filter("label", equals="Primary sequence")
if len(primary.items()):
    complete_sequence = primary.items()[0].cells["value"].value
sequence_mass = sequence.filter("label", equals="Sequence molecular weight")
if len(sequence_mass.items()):
    original_mass = sequence_mass.items()[0].cells["value"].value  # retains its unit
```

Each row is an original sequence or positional-annotation field. Annotation
previews show the source's axis, indexing and endpoint modifiers. A different or
missing axis is not silently mapped to this protein. The full field and its
original source records remain inspectable:

```python
active_fields = sequence.filter("label", equals="Active sites")
if len(active_fields.items()):
    active_field = active_fields.items()[0]
    annotation_rows = active_field.open().filter("label", equals="Annotations")
    if len(annotation_rows.items()):
        annotations = annotation_rows.items()[0].open()
        annotations
        if len(annotations.items()):
            original_annotation = annotations.items()[0].open()
            original_annotation.native_payload
    field_sources = active_field.explain()
    field_sources
    assert field_sources.back() is active_fields
```

Support here belongs to the complete selected annotation field; it does not
invent per-annotation source membership. Stored fragments, unknown location
modifiers, alternative source statements and conflicts remain available. No
alignment, residue correspondence or source query is performed.

## Inspect predicted models separately

```python
models = explorer.answer("predicted_models")
models.table()
if len(models.items()):
    model = models.items()[0]
    model.open()  # original complete model relationship and qualifiers
    model.explain()  # original relationship source records
```

Model declarations retain source versions/tools, pLDDT values/bands where stated,
source range and recorded isoform/sequence-match context. The recorded match flag
can originate in checksum comparison during mapping; this pane does not attribute
it directly to AlphaFold or certify its original derivation/input basis.
Zero metrics, a false sequence
match and unknown values stay distinct. These are source metrics, not experimental
resolution or an inferred ranking. This pane does not calculate current sequence
coverage or align an isoform. A missing consistent canonical UniProt identity is
a prerequisite gap; a model list alone does not establish source completeness.

## Inspect source sites and contact statements

```python
sites = explorer.answer("retained_sites")
sites.table()
contact_statements = sites.filter("kind", equals="contact_relationship")
if len(contact_statements.items()):
    contact = contact_statements.items()[0]
    contact.open()  # original numbering, residue records and observed_in context
    contact_sources = contact.explain()
    assert contact_sources.back() is contact_statements
```

The public TcTIM input has three functional-site fields and eight ligand/interface
contact relationships. Aggregated contacts are not individual ligand instances.
This source pane does not compute annotated overlaps, physical proximity or a
cavity. It preserves numbering and original per-residue observations; the existing
scientific readers keep their own interpretation/rules. Full instance/overlap and
cross-topic integration remain under development. These source views support the
same `save()`, original independent reading and exact bounded payload access as
other field views.

## Explore experimental structures

For a protein Card, open the retained inventory:

```python
structures = explorer.view("structures")
structures.table()
selected = structures.filter("structure_ref", equals="pdb:1SUX")
if len(selected.items()):
    structure = selected.items()[0]
    detail = structure.open()
    explanation = structure.explain()
    assert detail.back() is selected
    assert explanation.back() is selected
```

The table separates method, resolution with units, chains, sequence coverage and
coverage class. Rows are retained inventory entries, not independent experiments
or chain counts. Sequence coverage of 1.0 does **not** establish coordinate
completeness. Original source/request states remain visible, including unqueried,
failed and incomplete scope. A missing value stays unknown; no biological absence
is inferred from the preview.

`structure.open().native_payload` contains the complete original entry.
`structure.explain().native_payload` contains the cached original scientific
explanation: its named rules, pinned relationships, source statements and group
context. The explorer does not choose a preferred structure. Filtering to a
nonretained label returns an empty display selection, preserving the original
result, exclusions and source coverage.

New structural explanations begin with readable retained state, effective options
and original named rules. Their items are the original source records for this
structure relationship, so you can open a statement directly:

```python
if len(explanation.items()):
    source_statement = explanation.items()[0].open()
    source_statement
    assert source_statement.back() is explanation
```

These records support the relationship; they do not establish individual
qualifier lineage or directly assert the derived grouping. Missing source records
and qualifier conflicts are explicit. Full group members, sequence context and
scientific detail remain in `explanation.native_payload`. Earlier saved
explanations keep their original item labels/organization; follow the structure's
`related()` source links to inspect original records in those readings.

```python
ordered = structures.sort("resolution", unit="angstrom")
fragments_too = explorer.view("structures", options={"include_fragments": True})
region = explorer.view("structures", options={"region": [[1, 10]]})
```

The region uses the existing reader's captured canonical/UniProt numbering; it
adds original per-chain missing-coordinate detail to the native entry. Fragment
admission and the effective region are scientific options, so they create a new
result. `structures.exclusions` retains original scientific exclusions and reasons.
Sorting keeps unknown resolution last in either direction and preserves original
units. A wrong dimension is an argument error, even for an empty selection.

## Ask about an explicit sequence region

Use the question route when region scope matters. For public TcTIM:

```python
answer = explorer.answer(
    "region_coverage",
    options={"sequence_ref": "uniprot:P52270", "region": [[170, 180]]},
)
answer.table()
answer.request  # question, destination topic and normalized effective options
selected_region = answer.filter("structure_ref", equals="pdb:1SUX")
if len(selected_region.items()):
    region_item = selected_region.items()[0]
    region_item.open()
    region_item.explain()
```

The preview labels the exact sequence axis and requested positions, and separates
sequence coverage from complete chains in the **retained coordinate annotations**.
For this frozen Card, 1SUX has no missing positions in that region on chains A/B;
other entries can have unknown coordinate annotations. This does not compare
isoforms, align sequences or transfer residue numbers between proteins.

The question requires a retained consistent canonical UniProt identity, primary
sequence and length. Missing inputs return `missing_prerequisite`; another
accession, isoform or coordinate axis returns `unsupported`. Invalid positions,
unknown options and regions beyond the stored sequence length raise argument
errors. No question starts acquisition. Opening the region question from
`questions().items()` explains the required options when they have not been supplied.
`answer.request` survives filtering/sorting and is separate from the shared
scientific result: the same normalized region/options reuse the structural panel's
original inventory, explanation and machine result.

## Read compact machine pages

The same captured structural result is available in compact machine pages:

```python
selection = explorer.access.select("structures", fields=["structure_ref", "resolution"])
page = selection.page(limit=2, max_bytes=8192)
```

Column projection does not rerun the scientific reader or change item identity.
Pages state item/value completeness and provide exact locations when data plus
required interpretation do not fit. Resolution uses a field-bound PyUnitWizard
record; it is never a naked unitless number. Each cell identifies its field and
support basis. Its `support_ref` points to the containing item's shared `support`,
which lists the original assertions and explicitly marks any missing members.
This support belongs to the relationship; it does not establish a source for each
individual qualifier. `support_location` opens the complete original support.

If mandatory interpretation or support cannot fit, the item marks
`inspection_required=True`. Its cells keep their scientific states and exact
`value_location`/`interpretation_location`, with `value_included=False`, and the
page reports `values_complete=False`. Follow those locations with
`explorer.access.read(...)` to inspect them in bounded pages. Unknown values and
deferred delivery are different conditions. An item that fits on a fresh page
continues there with the returned cursor.

Select structural rows with typed
equalities and scalar ordering over that same scientific result:

```python
import pyunitwizard as puw

compact = explorer.access.select(
    "structures",
    fields=["structure_ref", "resolution"],
    where={"resolution": puw.quantity(2.0, "angstrom")},
    order_by={"column": "coverage", "descending": True},
)
compact_page = compact.page(limit=2, max_bytes=8192)
```

Multiple equalities combine with AND. `item_refs=[...]` restricts exact members
of this result; `item_refs=[]` selects nothing. Foreign references are errors.
The request metadata, reachable through `compact_page["context"]["context_location"]`,
retains the criteria, underlying/selected counts and display exclusions. Filtering
does not change the original scientific coverage. Missing cells do not match an
equality; sorting places them last in either direction.

Saving a machine selection preserves its original full scientific result and
support, as well as its exact projection/filter/membership/order. Saved `select`
can reopen that exact request; another variant is `not_saved`. A partial machine
selection never stands in for the unrestricted human structures topic.

## Explore a small molecule

For an already loaded molecule Card, start with its chemical identity and then
review a property. These calls do not resolve identifiers or calculate descriptors:

```python
molecule_explorer = molecule.explore()
molecule_explorer.overview()
chemistry = molecule_explorer.answer("chemical_identity")
chemistry
molecule_properties = molecule_explorer.answer("property_context")
molecule_properties.table()
```

Chemical representations, formula and retained `same_as` statements remain separate
items with their original support. A shared name or equal representation never
creates a new identity link. In the public benznidazole example:

```python
mass_selection = molecule_properties.filter("label", equals="Molecular weight")
if len(mass_selection.items()):
    mass = mass_selection.items()[0]
    mass.cells["value"].value  # PyUnitWizard quantity, 260.25 dalton in this example
    mass.open()  # complete stored field, with original unit
    mass_support = mass.explain()
    mass_support  # original selected and alternative source statements
    assert mass_support.back() is mass_selection
```

Property previews retain units and show methods when stated in selected support.
The ChEMBL record states ALogP for logP; the molecular-weight assertion does not
state a method. It is not relabeled as an experimental measurement. Source records
retain original asserted text, normalized values, source units, versions and method
metadata. `explain().native_payload` distinguishes selected support from unselected
`alternative_source_assertions`, `stored_alternatives` and conflicts. Alternatives
never replace the selected value or disappear from the explanation. When selection
references themselves are unrecognized, actual field assertions remain explicitly
`unclassified_field_source_assertions`; no selected/alternative role is invented.

Source rows now label **Selected support**, **Alternative statement** or
**Selection role unknown**. These describe the original field selection; they do
not rank source reliability. Alternative statements can agree with the selected
value. The preview shows the retained source method and source unit when stated,
and flags missing source records and unresolved conflicts. Open any row for its
complete original statement:

```python
logp = molecule_properties.filter("label", equals="logP")
if len(logp.items()):
    logp_sources = logp.items()[0].explain()
    logp_sources.table()
    if len(logp_sources.items()):
        logp_sources.items()[0].label
        logp_sources.items()[0].open()
```

Missing or unrecognized selection references produce an unknown method and keep
all original data available for inspection. A missing supporting record is also
distinct from a source record that states no method. When a preview inspects only
four references from a longer selection, it explicitly reports that partial scope;
open `explain()` to inspect the complete support.

## Explore a disease term

For an already loaded disease Card:

```python
disease_explorer = disease.explore()
disease_explorer.overview()
meaning = disease_explorer.answer("meaning")
meaning
parents = disease_explorer.answer("classification")
parents.table()
terminology = disease_explorer.view("identity")
terminology
```

The definition keeps its original references; synonyms keep their ontology scope.
Missing term-status metadata stays missing. Parent rows contain only stored
`subclass_of` relationships whose subject is this exact focal disease. The identity
route separates source-stated equivalent identifiers from related xrefs; neither
list becomes a fabricated parent edge. No parent Card is silently opened or fetched.

Synonym scopes use readable wording such as **exact synonym** and **related
synonym**; their original scope codes remain in the full stored value. Synonym
scope does not establish disease identity. The classification table adds a **Basis**
preview: **Source-supported broader term** means support is retained and no
derivation is recorded. **Derived broader term** names its recorded versioned
rule. Missing support or an incomplete derivation is explicit. These labels do
not independently validate a source claim, invent parent names or change the
stored relationship:

```python
parents.table()
if len(parents.items()):
    parents.items()[0].label
    parents.items()[0].open()
```

For public MONDO:0014221, four parent edges are retained. Inspect one by reference:

```python
parent_selection = parents.filter("object_ref", equals="mondo:MONDO:0002908")
if len(parent_selection.items()):
    parent_edge = parent_selection.items()[0]
    parent_edge.open()  # the actual retained relationship
    parent_support = parent_edge.explain()
    assert parent_support.back() is parent_selection
```

## Follow related context and return

For a retained parent relationship, discover its source and endpoint links:

```python
if len(parent_selection.items()):
    links = parent_selection.items()[0].related()
    links.table()
    objects = links.filter("role", equals="object")
    if len(objects.items()):
        destination = objects.items()[0].open()
        destination
        assert destination.back() is objects
        assert links.back().back() is parent_selection
```

A link has a readable label, `role`, `target_ref` and `availability`. The link view
returns to the relationship detail, then to the exact original selection. A source
link opens the original assertion, including its native metadata; it does not open
a provider website. `links.follow(item_ref)` is an advanced alias for explicitly
opening one of that result's link items.

If the destination Card was not supplied, its outcome is `context_not_supplied`.
`destination.explorer` is `None`, and its focal Card pin/snapshot are null. The
known target reference, available glossary record and original relationship support
remain readable in `native_payload`. No foreign definition or molecule property is
invented. `back()` works normally. Missing source basis or a missing referenced
record in a supplied pin is instead `missing_prerequisite`; neither means a source
stated biological absence.

When you already hold the destination Cards, supply them explicitly with
`card.explore(related_cards=[...])`. Opening a supported link then switches to the
destination's own profile. Its explorer offers that nature's topics and questions,
and subsequent views keep the transition's return path. No source request or Card
refresh occurs. Names, equal sequences, orthology and chemical similarity do not
establish identity; only exact references and retained source-supported identity
links admit a destination.

Several supplied revisions or conflicting identity destinations produce an
`ambiguous` view containing labeled candidate links. Inspect those candidates and
open one explicitly. Sabueso never selects the newest or the first supplied Card.
Choosing a revision for navigation does not reconcile scientific conflicts. All
agreeing/conflicting source identity paths remain available for inspection.

## Understand knowledge coverage

For protein, molecule and disease Cards, this view reuses the existing
`knowledge_state@5` result and its original `knowledge_state_explanation@2`:

```python
coverage = explorer.view("coverage")
coverage.table()
unqueried = coverage.filter("state", equals="not_queried")
if len(unqueried.items()):
    knowledge_gap = unqueried.items()[0]
    explanation_of_gap = knowledge_gap.explain()
    explanation_of_gap.native_payload
    assert explanation_of_gap.back() is unqueried
```

Each row has an area, source, state, count and release. Known, conflicting,
not-stated, unqueried, unavailable and partial states retain the existing reader's
meaning. An unknown count is not zero. These rows describe the classifier's actual
retained scope; an unlisted area does not establish absence or global completeness.
The original unfiltered result remains in `coverage.native_payload`.

The result is cached per captured context. A row's original scoped explanation is
computed on first explicit `explain()` and retained for subsequent navigation; no
source acquisition or new source assertion occurs. The explanation distinguishes
classification inputs from related stored knowledge and does not invent per-request
assertion membership. Filtering/sorting changes only the display. A missing pinned
Card identity returns `missing_prerequisite`; original quality remains inspectable.

The same capture exposes each new panel item's exact retained payload through
`explorer.access.read(item.payload_location)`, including cached coverage rows.
Specialized machine `select()` still supports structures only; broader machine
selection/conformance remains pending. No unsupported selector silently falls back.

## Save a supported exploration and reopen it

Supported literal/field views, disease hierarchy, experimental structures,
canonical-region answers, knowledge coverage and contextual navigation can be
saved. Check `view.capabilities["save"]` for the particular result and retained
support closure. Complete captured data remains readable through inspection.

For the molecule property selection above, choose an output path you own:

```python
from pathlib import Path
import sabueso

review_path = Path("molecule-review.json")
receipt = mass_selection.save(review_path)
saved = sabueso.read_exploration(review_path, expected_digest=receipt["bundle_digest"])
saved
```

The default refuses an existing destination. To replace one deliberately, use
`overwrite=True`; a failed write preserves the previous file. Keep the receipt's
digest independently when you want to verify this exact original bundle later.
The file includes the full underlying result, hidden rows and contributing captured
Cards, which can contain more information than the visible table. It does not
package source response archives, article bodies or external runtime sidecars.

```python
saved.validation
if len(saved.items()):
    retained_property = saved.items()[0]
    original_sources = retained_property.explain()
    original_sources
    assert original_sources.back() is saved
```

Saved mode retains values, source records, units, display selection and return
paths. It does not call scientific readers or discover new identity paths.
`validation` distinguishes verified input/support bindings from recorded wording
and scientific truth that hashes cannot establish. Source, missing-context and
ambiguous-revision views remain distinct. The topic catalog marks unretained
variants as `not_saved`; opening one does not compute a replacement with new defaults.

Complete literal data remains inspectable. A newly opened node may lack its saved
explanation/link closure; its capabilities show that gap, and optional operations
return `not_saved`. To begin a new local interpretation explicitly:

```python
new_explorer = saved.explorer.start_new()
assert new_explorer.mode == "live"
assert saved.explorer.mode == "saved"
assert new_explorer.context["snapshot_id"] == saved.context["snapshot_id"]
```

This reuses the original captures without refreshing sources. It leaves saved
results unchanged. Scientific views run only when you explicitly request them.

Literal machine selections use the same file and reader. The reopened root exposes
the original exact selection handle; continuation cursors are freshly local:

```python
literal_access = card.access()
literal_selection = literal_access.read(literal_access.root_location)
literal_receipt = literal_selection.save(Path("literal-reading.json"))
literal_saved = sabueso.read_exploration(
    Path("literal-reading.json"), expected_digest=literal_receipt["bundle_digest"]
)
original_selection_ref = literal_saved.capabilities["root_machine_selection_ref"]
restored_selection = literal_saved.explorer.access.selection(original_selection_ref)
restored_selection.page(limit=2, max_bytes=65536)
```

The `selections` catalog discovers other retained requests. Old session cursors
are rejected. Saving a small machine selection still retains the full underlying
result and captured inputs; the bounded page is a transport view, not the bundle's
storage scope. Original structural machine selections now share the same saved
reader; broader scientific selectors remain pending.

## Keep a scientific reading without redoing it later

Save the structural view you have been reviewing:

```python
structure_review = card.explore().view("structures").table()
structure_receipt = structure_review.save(Path("structure-review.json"))
saved_structures = sabueso.read_exploration(
    Path("structure-review.json"),
    expected_digest=structure_receipt["bundle_digest"],
)
saved_structures
```

The reopened result retains its original inventory, quantities, exclusions,
conflicts, source scope and return paths. It does not classify the Card again
with the installed reader. Its validation reports the historical rules actually
checked against the original inputs:

```python
saved_structures.validation["verified_scientific_rules"]
if len(saved_structures.items()):
    retained_structure = saved_structures.items()[0]
    retained_structure.open().native_payload
    original_explanation = retained_structure.explain()
    assert original_explanation.back() is saved_structures
```

Knowledge coverage is saved in the same way. The file retains the full underlying
source/area result even when you save a filtered table:

```python
coverage_review = card.explore().view("coverage").filter("source", equals="RCSB PDB")
coverage_receipt = coverage_review.save(Path("coverage-review.json"))
saved_coverage = sabueso.read_exploration(
    Path("coverage-review.json"), expected_digest=coverage_receipt["bundle_digest"]
)
saved_coverage
```

Original `known`, `partial`, `not_queried`, `not_stated` and failed-source states
remain distinct. Historical consistency does not establish source truth. Missing
saved variants return `not_saved`; use `start_new()` explicitly to request a new
local interpretation. Complete support/history bundles can be much larger than
their visible table; bounded machine pages are a separate delivery limit.

An agent can reopen an exact original structural projection through the same API:

```python
technical = card.access().select("structures", fields=["structure_ref", "resolution"])
technical_receipt = technical.save(Path("structural-selection.json"))
technical_saved = sabueso.read_exploration(
    Path("structural-selection.json"),
    expected_digest=technical_receipt["bundle_digest"],
)
original = technical_saved.explorer.access.select(
    "structures", fields=["structure_ref", "resolution"]
)
assert original.selection_ref == technical.selection_ref
original.page(limit=2, max_bytes=8192)
```

Only retained effective options/projections are available in saved mode. Reading
does not compute another region, adopt a newer default or reconstruct old cursors.
The format-@1 literal reader remains supported alongside scientific format @2.

## What comes next

The bounded first version consists of complete inspection, initial nature-specific
routes, explicit contextual navigation and portable saved reading. Richer activity,
clinical, variant, site and comparative panels remain under development. The
complete broad design and validated human experience are required before the
planned 0.15.0 release. Researcher review and useful-scale qualification remain open.

The same generic inspection works for protein, small-molecule, disease and
unrecognized Card natures. Initial protein, molecule and disease questions are
implemented, together with explicit navigation to supplied related Cards and
retained context for missing destinations. Supported literal/field and navigation
sessions and initial structural/region/coverage results can now be saved. Broader
scientific panels, full machine conformance and technical/human acceptance remain
pending. Unrecognized natures return an explicit
unsupported question catalog. Inspect `explorer.capabilities` and a view's
`capabilities` for the delivered operations.

`explorer.access` reads the exact same capture through bounded machine pages;
see {doc}`../../api/core`. Existing scientific methods such as `card.structures()`
remain available through their established APIs; the first structural panel
shares their existing readers rather than introducing a new scientific engine.
