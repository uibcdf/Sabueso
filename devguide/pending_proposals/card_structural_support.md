---
summary: Readable original structural decisions with direct relationship source records.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-22
closed:
verification: inspected
area: [public-api, human-exploration, storage]
blocked_by: []
supersedes: []
---

# Readable structural support

The [initial public walkthrough](card_exploration_v1_closeout.md) exposed a concrete
friction: structural `item.explain()` began with technical metadata rather than
the scientific basis and accessible original statements. This continuation
implements readable orientation and direct source inspection. It is part of the
[full design required before 0.15.0](card_exploration_completion_0150.md), not
completion of that design or human acceptance.

## Delivered behavior

New structural explanations display the original inventory status, named and
versioned explanation/classification rules, effective fragment/region options and
retained structural state. Unknown states remain unknown and false remains false.
A grouped state is not a structure recommendation. Sequence coverage still does
not establish coordinate completeness. Qualifier conflicts remain unresolved and
visible before opening complete details.

The item list contains original retained source records supporting this exact
structure relationship, in original declared order with duplicate references
shown once. Opening one reaches its full captured statement, source version,
method/unit metadata and original record; returning restores the explanation and
then the exact structural selection. Missing supporting records remain explicit;
a declared empty reference list is not reinterpreted as source absence.

These are **relationship support**, not fabricated qualifier-level lineage or
source assertions of a derived classification. The complete original explanation,
including other group members, reference context, rules and source references,
remains unchanged in `native_payload`. The human facade does not rerun an inventory,
explanation engine, source client or classification to render the support.
The compact machine facade retains the full original scientific result.

Recognition requires an exact explanation location in a registered
`structure_exploration@1` result. A literal Card extension, matching dictionary
keys, rule name or title alone cannot acquire scientific presentation or support.
Previews remain bounded and HTML-escaped; full source bodies remain accessible.

## Saved reading and compatibility

New saved explanation rows bind exactly the present original assertion locations
declared by the item's frozen relationship support. The reader checks that
membership and rejects missing, foreign or reordered support. This is an additive
human presentation admitted by the existing unpublished exploration format;
no Card schema, scientific wire, rule, quantity codec or format identifier changes.

Earlier saved explanations keep their original item labels and membership,
including their metadata organization. Current readable orientation can explain
their verified original result without converting the stored item list. Source
links from the originating structure remain available. Original producer capsules
and earlier demonstration bundles are not regenerated. Independent readers use
original inputs and the existing frozen verifiers, not current scientific engines.

Eleven new regressions cover public exact support/value parity, direct source
opening/return, missing/empty support, literal lookalikes, original region options,
bounded escaped source text, independent saved reading, historical item
organization and refusal to save incomplete source membership. All eleven pass
in 9.56 seconds with twelve pytest-receptor workers and fatal runtime/SQLite/
unraisable guards. All **6,847 local-original offline cases pass in 660.07 seconds**,
with twelve receptor workers, fatal SQLite/unraisable guards and thirteen expected
fixture warnings. The public guide's 31 blocks execute with source connections
forbidden; four actual HTML panels are rendered and visually inspected, including
one explicitly synthetic conflict/missing-support variant. The three-Card example
also produces and independently reopens its original selections outside the
checkout with fixture access and live reconstruction/readers forbidden.
Applicable static/fixture/dependency/governance, Markdown/snippet/Python 3.11 syntax
and warning-fatal Sphinx checks pass. Qualification receipts in #148 retain the
exact final source, tests, input/capsule hashes and environment; researcher
interpretation remains open.

No public arguments, scientific calculations, dependencies, schema fields or
quantity encodings are added. Existing ArgDigest/SMonitor boundaries and
StorageError diagnostics are reused; optional-dependency and new unit-codec
integration are not applicable to this presentation change. Follow the existing
[deferred-CI route](deferred_ci.md) for this intermediate implementation.
