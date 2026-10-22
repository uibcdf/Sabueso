---
summary: Initial bounded literal Card access implementation and its qualification boundary.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-21
closed:
verification: inspected
area: [public-api, agent-access, human-exploration]
blocked_by: []
supersedes: []
---

# Bounded literal Card access

## Delivered development scope

`Card.access(related_cards=())` now uses one detached, validated capture factory
and exposes the first machine-access portion of slice A from the
[agent contract](card_agent_access_v1_contract.md). This is development SDK code,
not a public release, the complete slice A, or acceptance of the human experience.
The [human literal continuation](card_exploration_literal.md) now reuses this
capture through `Card.explore()` and `explorer.access`, without reconstructing science.

Implemented public operations:

- `access.context`, `profile`, `root_location` and `capabilities` return defensive
  metadata or scalar state; repr does not dump Card content.
- `catalog(kind="topics"|"fields"|"selections", locator=None)` discovers implemented
  literal content, immediate fields or retained selections. The catalog of
  selections does not recursively include its own catalog selections.
- `read(location, text_slice=None)` traverses full stored content, including unknown
  extensions, assertion/relationship stores and seals. Containers return immediate
  child descriptors; scalar values are literal, not new scientific findings.
- `selection(selection_ref)` retrieves an exact retained request without rerunning
  readers. `AccessSelection.page(limit=32, max_bytes=65536, cursor=None)` enforces
  1–256 records and 1,024–1,048,576 bytes for the whole canonical UTF-8 JSON frame.
- `export_card(path, overwrite=False)` atomically exports the captured focal Card
  in its existing sealed format. A no-overwrite race cannot clobber caller data;
  write/publication failure preserves an existing file and cleans its owned sibling.

The capture serializes each distinct supplied object once, checks the current
schema/quantity contracts, detaches stored JSON types, preserves duplicates in
input metadata and retains different revisions separately. An anonymous Card has
a local snapshot without a fabricated global identity. A readable newer schema
retains extension content and emits the existing schema warning.
Here `mode="live"` means an active local access context over the supplied capture;
it does not mean that external sources were refreshed.

Full typed Card locations bind owner pin/snapshot and `Key`/`Record`/`Index`
segments. Normal output uses compact session-owned lookup locations; these never
fall back to another session or a current store revision. ID stores use records,
not insertion indices. Ordered-list indices and literal keys containing dots keep
their original meaning. Pages explicitly state the selected node's type/size/owner,
including for empty mappings/lists or a related Card's different snapshot.

`page.complete` concerns item enumeration. `page.values_complete` concerns inline
delivery; nested/oversized values have explicit deferred locations. Strings support
exact half-open Unicode code-point ranges without normalization. Large keys have
an inspectable key location. There is no JSON/string/quantity truncation or silent
item skipping. Insufficient mandatory metadata is an `ArgumentError` with structured
`extra["reason"]="response_budget_too_small"`; malformed/foreign cursors never
restart a query. Unknown keyword arguments retain ArgDigest's established
`UnknownArgumentError` boundary.

Declared Card quantity leaves retain a PyUnitWizard-owned field-bound quantity
record alongside literal data. Consumers verify it with explicit field/unit
expectations. Unknown extension dictionaries resembling quantities remain literal.
No optional dependency is added, so no new DepDigest boundary is needed. Public
arguments use ArgDigest; semantic guards remain active with digestion skipped;
exceptions use the existing SMonitor catalog.

## Example using the implemented API

Here `card` is an already loaded Card. This example performs no acquisition:

```python
access = card.access()
fields = access.catalog("fields")
page = fields.page(limit=8, max_bytes=8192)
for item in page["items"]:
    print(item["key"], item["node_type"], item["location"])
root = access.read(access.root_location)
next_page = root.page(limit=2, max_bytes=8192)
cursor = next_page["page"]["next_cursor"]
if cursor is not None:
    continuation = root.page(cursor=cursor, limit=2, max_bytes=8192)
```

Inspect `value_included`, `value_location`, `node_type` and `page.values_complete`
before interpreting a page. Reading a container is enumeration, not recursive
delivery of its entire subtree. Coverage points to literal retained quality data
and states `classification="not_evaluated"`; this initial adapter does not call
`knowledge_state()` or declare a scientific area known/absent from display counts.

## Remaining delivery and acceptance

The initial literal slice omitted scientific `select`/`explain`. The
[structural continuation](card_structures_exploration.md) now adds the first
shared scientific selection/explanation; exploration `save` and saved-mode reading
remain pending. The [generic human facade](card_exploration_literal.md)
now delivers labeled literal inspection and original-support reading. The first
structural scientific presentation is delivered; broader thematic adapters and
value/qualifier support closure remain pending. Raw export is not the portable
exploration bundle or an archive
of original source response bytes. Existing SDK/schema/packet formats stay intact.

Regression coverage checks all supported natures and the generic fallback using
labeled synthetic literal content; a frozen public TcTIM Card supplies actual
ID-store, resolution quantity and export checks. Cases cover exact reconstruction,
zero/false/null/empty types, mutation isolation, one-time capture, repeated inputs,
separate revisions, byte/record bounds, cursor retry/foreign binding, Unicode,
large keys, non-default unit policy, original quantity-seal corruption, unsupported
schemas, atomic no-clobber/failure and forbidden source/scientific-reader access.
This is technical acceptance, not a token-saving benchmark or researcher acceptance.

Local qualification passes 56 new literal-access regressions within **177 selected
cases** (9.31 seconds) and **all 6,382 local-original offline cases** (517.02 seconds,
thirteen expected fixture warnings), with twelve pytest-receptor workers and fatal
SQLite/unraisable guards for the full run. Ruff, fixture delivery, dependency,
schema alignment, local governance and warning-fatal Sphinx HTML build pass;
the three original public design inputs keep their original hashes.

The first full/Sphinx attempt exhausted `/tmp` quota and is not passing evidence.
Repeating with task-owned scratch on the workspace filesystem passes; completed
scratch is removed and concise local logs/source fingerprints retain owner #148
and review at the next exploration checkpoint or substantial release. No separate
environment was created. The published implementation SHA is recorded in #148.
Remote qualification follows the
[deferred-CI route](../TESTS.md#recovering-deferred-ci) for an intermediate
`[skip ci]` push; a skipped run is not passing code evidence. Preserve original
source receipts. 0.15.0 consolidation remains paused.
