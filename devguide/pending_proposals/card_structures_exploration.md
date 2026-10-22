---
summary: First shared scientific exploration adapter over the captured structural inventory.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-21
closed:
verification: inspected
area: [public-api, human-exploration, agent-access, scientific-views]
blocked_by: []
supersedes: []
---

# Captured structural exploration

## Delivered boundary

This is the first scientific continuation of [human literal exploration](card_exploration_literal.md)
and [bounded machine access](card_access_literal.md), within slice B of the
[v1 contract](card_exploration_v1_contract.md). It does not complete slice B,
researcher acceptance or a release. Consolidation of 0.15.0 stays paused.

Both `explorer.view("structures", options=None)` and
`access.select("structures", fields=None, options=None)` materialize the same
`structure_exploration@1` result. The only scientific options are
`include_fragments=False` and `region=None`. Regions use the existing reader's
captured canonical/UniProt numbering, with its positive positions/inclusive ranges.
The normalized effective options are retained; changing them creates another
result. No other captured Card is joined or chosen by recency.

Materialization rebuilds a private reader input from the verified focal capture,
without retaining or rereading the caller's mutable Card. Its pin is the already
verified capture; explaining an item does not serialize/reseal the Card again.
The adapter delegates to the existing `structure_inventory`, `knowledge_state`
and `explain_structure_inventory` readers. It introduces no new admission/state/coverage rule, preferred structure or
source assertion.
The original rules, parameters, source records, group context, admission/exclusions,
not-inventoried reasons and original explanation are retained. Existing SDK APIs,
schemas, provider acquisition, quantity seals and source fixtures are unchanged.

## Human route

```python
explorer = card.explore()
structures = explorer.view("structures")
selected = structures.filter("structure_ref", equals="pdb:1SUX")
selected.table()
if len(selected.items()):
    item = selected.items()[0]
    detail = item.open()
    explanation = item.explain()
    assert detail.back() is selected
    assert explanation.back() is selected
```

Protein topic catalogs now advertise experimental structures. Other natures retain
their generic routes; an explicit structures request returns `not_applicable`.
A protein without a Card identity reports `missing_prerequisite`, with literal
inspection available. An empty admitted inventory is `empty` with its original
source coverage/exclusions, never an assertion that no structure exists.
Question aliases are still unavailable, rather than empty biological answers.

Rows are original inventory entries, not chains or independent experiments. Items
have typed columns `structure_ref`, `method`, `resolution`, `chains`, `coverage`,
`coverage_class` and `state`, plus core `label`/`kind`. `open()` returns the selected
native entry and structural-state detail; `explain()` returns the original cached
inventory explanation, with native PyUnitWizard quantities in `native_payload`.
The complete retained scientific wire tree remains inspectable through locations.

Human filters use typed exact equality; resolution requires a scalar compatible
length quantity. Sorting supports scalar columns, preserves missing values last
in either direction, rejects undeclared list/object order and validates units even
for empty selections. Resolution sorting uses an explicit target `unit`, or this
adapter's declared angstrom unit; session defaults do not choose scientific order.
All other admitted rows remain addressable through `item(item_ref)`, while display
filtering/order leaves the result, original admission and coverage unchanged.

Text and escaped inert HTML tables show separate scientific columns. Previews
remain bounded; original values are reached through items/rows/native payload.
Source/request states and the caveat that inventory sequence coverage does **not**
establish coordinate completeness remain visible. Unknown retained qualifiers,
original conflicts and missing referenced assertions stay explicit. Relationship
support is never manufactured as individual qualifier lineage.

## Machine route and limits

```python
access = explorer.access
selection = access.select("structures", fields=["structure_ref", "resolution"])
page = selection.page(limit=2, max_bytes=8192)
```

`fields=None` uses the compact default columns: structure reference, method,
resolution, chains and coverage. `fields=[]` retains item identity/state/support
and mandatory interpretation without optional projected values. Duplicate/unknown
fields and unsupported options are argument errors. This first machine selector
supports projection and scientific options; `where`, exact membership and
`order_by` remain unimplemented and are not accepted or advertised as available.

Scientific selections reuse the existing whole-envelope record/byte limits and
session/selection-bound cursor rules. Projecting columns changes `XA_`, not `XR_`
or `XI_`. Pages retain experimental kind, original structural state, inventory
status/reason, conflicts, coverage scope, effective region/axis and rule bindings.
When values plus their mandatory interpretation exceed the budget, both are
replaced by exact retained locations. A naked value is never emitted after
silently omitting its conflict/scope context. `complete` and `values_complete`
remain delivery metadata, not global scientific/source coverage.

Resolution cells use cached PyUnitWizard `QuantityRecord` data, with explicit
`relationships.has_structure.resolution` / `angstrom` expectations. Native data
retains typed quantities; literal Card traversal/export retains the original seal.
There is no new consumer-owned quantity codec or persisted exploration format.

`access.explain(item_ref)` selects the already materialized original explanation
as a traversable wire record. A foreign/unretained item fails; no reconstruction,
source access, new credit or scientific reader execution occurs during paging,
printing, selection, navigation or explanation. The scientific request itself
may inspect the full Card and compute original group/exclusion explanations;
small output is not a claim of cheap materialization.

Result identity binds exact captured inputs, focal context, effective options,
original scientific payload and named/versioned rules. Only producer metadata in
the declared generated rule records is excluded from semantic identity; original
stored content and similarly named fields are never generically discarded.
Complete producer metadata remains retained in the result/context. These are local
handles, not a changed MOLI query, packet or shared identity contract.

## Qualification and remaining work

Regressions compare native results and original explanations against unchanged
readers using frozen public TcTIM. Synthetic variants cover fragments/exclusions,
missing/failed/unknown scope, missing references, conflicting qualifiers, opaque
locations, byte-budget deferral, typed quantities, wrong dimensions/types, empty
selections, cached read counts, defensive values, stable identities and navigation.
Original public inputs remain unchanged. **40 new regressions**, **225 selected
cases / 17.70 seconds** and **6,464 full local-original offline cases / 615.96 seconds**
pass with twelve pytest-receptor workers and thirteen expected fixture warnings.
The full SQLite/unraisable guards and selected RuntimeWarning guards are fatal.
Ruff, fixture delivery, dependency routes, schema alignment, local governance and
warning-fatal Sphinx HTML pass. Twelve example blocks execute with public frozen
TcTIM and sockets forbidden. The thirteen changed code/test fingerprints match
the qualified source; Python 3.11 syntax checks pass in addition to the Python
3.14 runtime gate. Fourteen installed suite-member editables and seven participating
imports/versions verify outside the checkout.

The exact published SHA is recorded in #148. This intermediate checkpoint uses
[deferred CI](deferred_ci.md): remote/installed lanes and hosted governance remain
pending for the exploration block; previous source/release receipts stay original.
Completed task-owned pytest/Sphinx/cache trees are removed. Useful logs, source
fingerprints and the public walkthrough retain owner #148 and review at the next
exploration checkpoint or substantial release.

Current projected wire cells reference original support through the item-level
`support_location`; they do not yet emit the full v1 per-cell support labels and
inline membership contract. That conformance work belongs to the next machine
selector checkpoint, including atomic deferral for large support membership.
This first adapter must not be labeled full machine-v1 conformance.

The subsequent [human protein journey](card_protein_exploration.md) follows the
maintainer's human-experience priority: opening, function fields and explicit
function/region questions over these results. Initial molecule/disease routes and
shared scientific coverage follow. Economical machine filtering/membership/order
and per-cell support conformance remain separately tracked in #148.
Contextual Card navigation, related links and portable saved sessions retain their
separate slices C/D. Researcher usability remains an independent acceptance route.
