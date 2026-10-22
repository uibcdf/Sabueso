# Explore a Card

**Development API:** this page describes the development checkout, after 0.14.0.
The released 0.14.0 package does not provide `card.explore()` yet. This first
version offers readable inspection and a protein structural panel; further
scientific topics are still being built.

Start with a Card you have already resolved or loaded:

```python
explorer = card.explore()
explorer.overview()
```

In a notebook the last expression displays a concise preview; in a terminal use
`print(explorer.overview())`. The opening shows the recorded name when available,
the Card's nature, retained record counts and any stored conflict notice. Counts
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
**Coverage and quality records**. Protein Cards also offer **Experimental structures**.
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

The same captured scientific result is available in compact machine pages:

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
unrecognized Card natures. The structural panel is the first scientific route. Question aliases, further
protein/molecule/disease panels, human navigation to related Cards and saved
exploration sessions remain pending. `explorer.questions()` reports this explicitly; it does not present an
empty scientific answer. Inspect `explorer.capabilities` and a view's
`capabilities` for the delivered operations.

`explorer.access` reads the exact same capture through bounded machine pages;
see {doc}`../../api/core`. Existing scientific methods such as `card.structures()`
remain available through their established APIs; the first structural panel
shares their existing readers rather than introducing a new scientific engine.
