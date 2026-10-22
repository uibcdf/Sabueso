# Explore a Card

**Development API:** this page describes the development checkout, after 0.14.0.
The released 0.14.0 package does not provide `card.explore()` yet. This first
version offers readable inspection, protein function fields and a structural panel; further
scientific topics are still being built.

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
**Coverage and quality records**. Protein Cards also offer **Protein function** and **Experimental structures**.
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
shows stored records; this initial interface does not independently classify
source knowledge coverage.

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
record; it is never a naked unitless number. The first machine selector supports
projection/options; machine filters, ordering and exact membership remain pending.
Human filtering/order and direct retained item lookup are available as above.

## What comes next

The same generic inspection works for protein, small-molecule, disease and
unrecognized Card natures. Protein function and region questions are implemented;
molecule/disease scientific panels, broader protein questions, human navigation to
related Cards and saved exploration sessions remain pending. Other natures return
an explicit unsupported question catalog. Inspect `explorer.capabilities` and a view's
`capabilities` for the delivered operations.

`explorer.access` reads the exact same capture through bounded machine pages;
see {doc}`../../api/core`. Existing scientific methods such as `card.structures()`
remain available through their established APIs; the first structural panel
shares their existing readers rather than introducing a new scientific engine.
