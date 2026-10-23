# Human source roles and ontology wording (#148)

This continuation improves the initial human exploration views. It adds no
scientific reader, source access, Card schema, machine adapter, dependency or
saved format. Broader scientific profiles and researcher acceptance remain open;
the pause before 0.15.0 consolidation stays in effect.

## Source explanations

Direct original source-record rows now distinguish the roles already retained
by their explanation metadata:

| Label | Original basis |
| --- | --- |
| Selected support | The field declares selected assertion IDs and this record belongs to that support |
| Alternative statement | An existing alternative field assertion, outside the declared selected support; its value can agree with the selected value |
| Selection role unknown | An existing field assertion for which selection references were missing or unrecognized |
| Relationship support | Original relationship-level support, without inventing qualifier-level or selected-field lineage |

The labels describe the original selection, never source reliability or new
scientific findings. A plain source catalog has no selected/alternative role.
Only exact typed source-store locations receive source-record presentation;
extension dictionaries resembling source assertions remain literal.

Source previews include retained asserted content, source version/retrieval,
source method and source unit when stated. An acquisition/extraction method is
not relabeled as a scientific method. Missing scientific methods stay unstated.
Normalized source values and complete original bodies remain inspectable through
`open()`; the preview does not create unitless normalized measurements.
Missing supporting records and unresolved conflicts are visible before drilling
into full metadata. Stored alternative-selection context remains accessible.

All original records, support membership, methods, units, conflicts and alternatives
remain unchanged. Displaying an alternative does not replace a selected value.
Labels are readable wording; stable item references, typed locations and original
support retain programmatic identity. Machines do not need to parse labels.

## Disease terminology

Known synonym scope codes have readable labels: exact, related, broad and narrow
synonym. Unknown scope values keep their literal bounded preview; absent scope
is explicit. Full values preserve original codes and shapes. Synonym scope never
creates disease equivalence or hierarchy.

Classification labels and the table's additional **Basis** preview distinguish:

- a source-supported broader term with retained support and no recorded derivation;
- a derived broader term with its original named, versioned rule;
- missing support, missing basis or an incomplete derivation.

Retained source support plus absence of derivation is not presented as independent
proof of a direct source statement. A path length, shared name, record count or
supplied destination Card cannot supply a missing basis. Parent names are not
invented and destination Cards are not silently joined or fetched. Original
subject/predicate/object cells, exact focal membership and full relationship records
remain unchanged. The additional Basis preview is explanatory text, not a new
filterable scientific column or stored derived classification.

## Saved reading and bounded presentation

Newly saved views record their readable item labels. Earlier recorded labels,
label-based filters and ordered memberships remain original: current wording never
replaces a saved label. Current previews can explain roles and ontology scope from
the original retained metadata without recalculating science or acquiring sources.
Saved schemas, cells, scientific wire, identities, rules and formats stay unchanged.

Rendering abbreviates text and containers, limits visible rows, escapes source
content and preserves complete `items()`, `rows()`, `open()` and `native_payload`
access. It does not copy large original explanation bodies to determine display
roles or copy relationship conflict/derivation bodies to check retained support.
Human and agent entries continue to share the same captured results.

## Acceptance

Public ChEMBL and MONDO examples exercise selected source methods/units, readable
synonyms and retained parent support. Explicitly synthetic variants cover
alternative/conflicting statements, unknown and empty selection references,
missing assertions, unknown synonym shapes, derived/incomplete/missing relationship
bases, long untrusted text and escaped HTML. Inert independent saved reading
forbids Card construction, live explanations and source queries; saved/resaved
original values and earlier label-filter decisions remain intact. Existing frozen
producer capsules remain unchanged.

Twenty-six new cases and all 624 selected cases pass in 72.48 seconds with twelve
pytest-receptor workers and fatal runtime/SQLite/unraisable guards. All thirty
guide blocks execute with sockets forbidden over the three unchanged public inputs.
Six actual API panels support technical review: four public and two explicitly
synthetic demonstrations. Source fingerprints bind the implementation to the
eventual commit; the observed pre-commit SDK label remains recorded honestly.
All 6,812 local-original offline cases pass in 629.57 seconds, with twelve receptor
workers, fatal SQLite/unraisable guards and thirteen expected fixture warnings.
Applicable static/fixture/dependency/local-governance and warning-fatal Sphinx gates
pass. All six panels were rendered locally and visually inspected; this is still
technical acceptance, not a scientist usability study.

A separate post-checkpoint inspection reproduced a preexisting method-preview
shape gap: a synthetic nonempty mapping or integer `source_assertion_ids` fails
inside `_method` before the unknown selection can be presented. It was recorded
in #148 and is corrected by the bounded continuation below. No source data was
queried or changed by the reproductions.

## Selected-method reference correction

Method and attribution previews now share the original selection-shape guard.
An absent reference declaration remains not retained; an explicit null, scalar,
mapping or list containing a non-string member remains unrecognized. A malformed
member anywhere in the list invalidates the declaration as a whole, including
after the four-reference preview boundary. Valid members are not silently
salvaged as selected support. This matches the existing field-explanation roles.
The full stored field and unclassified original statements remain inspectable.

A declared empty list remains distinct from an unknown declaration. Valid public
ALogP method attribution and original quantities/units are unchanged. A missing
selected source record makes its method unknown, while retained known methods
remain visible with an explicit support gap. Previews inspect at most four valid
references and label a longer selection partial; an uninspected tail never
establishes that a source did not state a method. No science, schema, saved format,
source assertion, input fixture or dependency is changed.

Twenty-four new regression cases cover false/zero/null/scalar/mapping references,
mixed lists including invalid tail members, absent versus empty declarations,
original valid method/unit behavior, missing/partial support, four-reference limits
and inert saved reading with complete original malformed fields. Twenty-three
cases fail on the preceding implementation and the valid public control passes;
all twenty-four pass after the correction. Broader selected checks qualify this
small presentation correction; the preceding 6,812-case full-suite receipt remains
bound to `f48421f`, not silently transferred to the new head.
All 648 selected cases pass in 80.02 seconds with twelve pytest-receptor workers
and fatal runtime/SQLite/unraisable guards. Applicable static, fixture-delivery,
dependency and local-governance gates pass; publication receipts retain exact
source/environment hashes. The malformed-reference follow-up is resolved in this
scope, with remote qualification still following #148's deferred route.

Local checks and the public walkthrough retain exact source/input/environment
receipts under owner #148. Static API panels are technical review, not a completed
scientist usability study. Complete profiles, broader nature-specific machine
adapters, populated-session cost/whole-process memory, researcher walkthroughs and
remote qualification remain separate. Follow the existing
[deferred-CI recovery](deferred_ci.md) and [cost observation limits](card_cell_support.md).
