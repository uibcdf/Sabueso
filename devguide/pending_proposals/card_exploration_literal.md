---
summary: Initial human literal Card exploration and its explicit delivery boundary.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-21
closed:
verification: inspected
area: [public-api, human-exploration, agent-access]
blocked_by: []
supersedes: []
---

# Human literal Card exploration

## Delivered development scope

`card.explore(related_cards=())` now returns `CardExplorer`. It creates one
`CardAccess` and exposes that exact object through `explorer.access`. Both facades
read the same detached, schema/quantity-verified capture. Rendering, navigation,
search and explanation perform no acquisition or scientific derivation. This
continues slice A; it does not deliver the complete
[v1 contract](card_exploration_v1_contract.md), a public release or researcher
acceptance. The [machine slice](card_access_literal.md) retains its own receipt.

Implemented operations:

- `overview()` opens a labeled root, recorded canonical name when present,
  nature, retained statement/relationship counts and an explicit conflict notice.
  Counts concern retained records, not scientific coverage or source freshness.
- `topics()` lists only content, source statements and stored coverage/quality
  records. Catalog items open those routes. `view(topic)` is their exact-key entry.
- `inspect()` exposes every stored focal Card member, including extensions and
  seals. `inspect("names.canonical_name")` is convenient section-field navigation;
  `inspect(locator=location)` accepts the machine reader's typed locations. Literal
  keys containing dots stay accessible through items or typed `Key` segments.
- `search(text)` finds all local literal key/scalar matches using Unicode casefold,
  preserving original text and locations. It is neither semantic search nor a
  source query. Its native payload is the original focal capture, not copied hits.
- `questions()` reports `unsupported` with an explanation and literal alternatives.
  Scientific questions are explicitly absent from capabilities, rather than
  presented as an empty biological answer.

The [user walkthrough](../../docs/content/user/card_exploration.md) introduces
the delivered calls without requiring internal paths. It clearly distinguishes
the development API from released 0.14.0.

## Objects, navigation and completeness

`CardView.items()` returns a read-only `CardItems` sequence of **all** selected
items. Indexing/slicing/iteration do not depend on the ten-item renderer preview.
Each `CardItem` has a readable label, kind, stable reference, typed cells,
`payload_location`, original support and `is_selected`. `open()` inspects its full
payload, `explain()` opens retained support/selection metadata and stored conflicts,
and `back()` returns its originating selected view. Views also retain their origin;
a root's `back()` returns that same root. There are no hidden source calls.

`filter(column, equals=...)` and `sort(column, descending=False)` currently accept
only the advertised string columns `label` and `kind`. They retain result/item
identities, source coverage and the original items. `item(item_ref)` also retrieves
a display-filtered original item; `is_selected` makes that distinction explicit.
Wrong columns, types, locations and foreign references raise the existing
ArgDigest/SMonitor errors. Unknown keywords retain `UnknownArgumentError`.

`summary()` and `table()` change presentation only. Text and inert, escaped HTML
show at most ten items and abbreviated values, disclose omitted counts, and state
Python navigation calls. The HTML table is a preview, not a clickable application.
`rows()` returns complete defensive structured rows; `native_payload` explicitly
returns the complete original node. Mutable cell values, support and metadata are
copies; no renderer calls `rows()` or serializes a large nested value to truncate it.

Literal inspection reuses machine `XR_` results and `XI_` item identities over
pinned typed locations. Presentation/selection yields a separate `XV_`; navigation
history is excluded. Search has its own versioned, captured-input/query binding.
These are local handles, not new shared MOLI identities.

Declared quantity nodes become PyUnitWizard `Cell.value` quantities through the
existing field-bound provider record with explicit original field/unit expectations.
Raw payloads retain `{value, unit}` and their captured integrity seal. Extension
quantity lookalikes remain literal. Raw null, zero, false and empty values remain
`present`, never inferred source absence. Exact stored field conflicts yield a
`conflicting` cell with the retained value and original conflict details available.
Support distinguishes original field references, original assertions, stored
metadata and relationship-level support; missing referenced statements are
`not_retained`, not fabricated. Qualifier-specific lineage is not inferred.

## Example with an already loaded Card

```python
explorer = card.explore()
opening = explorer.overview()
topics = explorer.topics()
content = topics.items()[0].open()  # delivered content route
first = content.items()[0]
detail = first.open()
assert detail.back() is content
support = first.explain()
all_selected_rows = content.rows()
page = explorer.access.read(first.payload_location).page(max_bytes=8192)
```

Use `topics.items()` to discover labels before selecting a position. Every item
binds its original location; a display index is never an entity identity.

## Remaining work and qualification

Scientific protein/small-molecule/disease adapters, question answering, scientific
value/quantity sorting, item-related links, human cross-Card destination resolution,
portable saved results and the broader catalogs remain pending. Supplied related
captures remain available through `explorer.access.read`; human inspection refuses
to silently switch their focal context/profile. `capabilities` exposes this limit.
The next bounded scientific target is the existing TcTIM structural reader, with
its original scientific explanation and source support, followed by the other
nature-specific routes. Human usability still requires actual researcher review.

The regression suite uses synthetic literals plus the unchanged frozen public
TcTIM Card. It checks shared one-time capture, all-nature literal reachability,
zero/false/null/empty values, full locations, defensive objects, selection identity,
back navigation, complete Unicode hits, bounded escaped text/HTML, declared units,
stored conflicts/missing support, exact source records, related-context refusal and
bad arguments with digestion enabled or skipped. All **42 new regressions**,
**140 selected cases** (4.32 seconds) and **6,424 full local-original offline cases**
(553.42 seconds; thirteen expected fixture warnings) pass with twelve
pytest-receptor workers in the existing editable Python 3.14 environment. Full
SQLite/unraisable guards and selected RuntimeWarning guards are fatal.

Ruff, fixture delivery, dependency routes, schema/shape alignment, local governance
and warning-fatal Sphinx HTML pass. The seven user-walkthrough blocks execute with
frozen public TcTIM and sockets forbidden. Original public inputs remain unchanged;
twelve code/test fingerprints bind the local receipt to the committed source.
Completed task-owned scratch is removed; concise logs/fingerprints retain owner
#148 and review at the next exploration checkpoint or substantial release.

This is an intermediate development push under the authorized
[deferred-CI route](deferred_ci.md), not remote/installed qualification or a release.
The exact published SHA is recorded in #148. Two pre-final runs interrupted during
review are not qualification evidence; their owned process trees were stopped
before the final gate. Previous code/release receipts remain original.
