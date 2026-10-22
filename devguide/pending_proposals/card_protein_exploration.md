# First human protein exploration journey (#148)

This development continuation prioritizes a useful human journey over further
machine grammar. It follows the [v1 design](card_exploration_v1_contract.md) and
[structural adapter](card_structures_exploration.md); it does not complete slices
B–D or establish researcher acceptance. Consolidation of 0.15.0 remains paused.

## Delivered journey

`card.explore()` captures once. A protein's `overview()` shows retained name,
organism, UniProt accession, sequence length, function/catalytic annotations and
actual attribution. The preview states captured schema, stored conflicts and that
current sources have not been queried. Ordered topic routes lead to protein
function, experimental structures, source statements, quality records and complete
content. Other natures retain their generic opening until their own designs are
implemented. Merely displaying the opening never runs the structural inventory.

`view("function")` selects exact retained field nodes for function, catalytic
activity, pathways, name, organism, accession and sequence length. Each item has a
readable label and its original typed Card location. Its value cell exposes the
actual field value; `open()` exposes the unmodified field envelope. `explain()`
lists the original supporting assertion records directly, with their actual
asserted value, source/version and retrieval metadata accessible through `open()`.
The explanation's `native_payload` retains unretained references, stored conflicts
and selection metadata. Back navigation restores the precise selected view.

No description is inferred from a protein name. Missing fields, retained null,
retained empty values, stored conflicts and unrecognized retained shapes remain
distinct; `native_payload["field_gaps"]` reports absent or unrecognized fields.
All raw content remains inspectable. The field panel does not classify source
coverage or create new SourceAssertions, scientific findings or identity links.
`protein_function_fields@1` identifies this presentation adapter, not a new
biological derivation rule. Source values, original assertions and existing rules
retain their own meanings.

## Executable question catalog

For proteins, `questions()` lists only `function` and `region_coverage`, with
readable wording, scope and required inputs. `answer(question, options=None)`
dispatches to the existing field/structural routes. Unknown keys/options are
argument errors. Other natures expose no protein question routes.

- `function` has no options and shares the function view's captured result.
- `region_coverage` requires explicit `sequence_ref="uniprot:<accession>"` and
  `region` positions/inclusive ranges; optional `include_fragments` defaults false.
  The retained canonical accession, Card identity, primary sequence and length
  must agree and have no recorded identity/sequence conflict. No similarity join,
  isoform assumption or residue-number transfer is allowed. Out-of-range positions
  are errors. Missing scope returns `missing_prerequisite`; unsupported axes return
  `unsupported`, without invoking the structural reader. Rejected/incomplete requests
  retain their exact normalized options/outcome and distinct result references.

`CardView.request` retains question, destination topic and normalized effective
options independently of `result_ref`. Equivalent normalized structural requests
share the existing human/machine result and original explanation cache. The
question context survives display filtering, ordering and detail navigation;
`view_ref` distinguishes the question presentation. No acquisition occurs.

Region previews show the exact axis, bounded explicit positions and each entry's
complete chains under the retained coordinate annotations, including unknowns.
Sequence coverage alone never establishes coordinate completeness. The original
native missing-coordinate detail and source/request coverage remain accessible.

## Public demonstration and acceptance

The [user walkthrough](../../docs/content/user/card_exploration.md) starts with an
already loaded public frozen TcTIM Card. It goes from the opening through function,
catalytic statement, original UniProt record and back, then an explicit canonical
region, 1SUX detail and original structural explanation. The frozen Card retains
the reaction/EC 5.3.1.1 without a textual function description; these are displayed
separately. For positions 170–180, 1SUX's existing reader reports no missing
positions on chains A/B; unknown coordinate context for other entries stays unknown.
These are captured facts, not current service availability or project conclusions.

Thirty-six new regression cases cover this journey, defensive capture, shared
results, exact original support and return navigation, scope prerequisites,
identity/sequence conflicts, foreign axes, invalid/out-of-range regions, empty/null
and unsupported shapes, wrong natures, ArgDigest and escaped bounded previews.
All 261 selected cases pass in 19.87 seconds with twelve pytest-receptor workers,
including original human/access/argument and native structure/inventory/explanation/
knowledge-state tests. RuntimeWarning, unclosed SQLite and unraisable guards are
fatal. Applicable Ruff, fixture-delivery, dependency, schema and local-governance
gates pass; warning-fatal Sphinx HTML passes. Thirteen user-guide code blocks
execute with public frozen TcTIM and sockets forbidden. The six changed Python
files also parse as Python 3.11. Fourteen installed suite-member editables and seven
participating imports verify outside the checkout. All **6,500 full local-original
offline cases pass in 559.96 seconds**, with twelve receptor workers, fatal
SQLite/unraisable guards and thirteen expected fixture warnings. Exact source is
recorded in #148; task-owned receipts retain unchanged source/input fingerprints.
The [deferred-CI recovery](deferred_ci.md) remains separate from local qualification.

The [subsequent nature/coverage continuation](card_nature_exploration.md) now delivers
the initial distinct molecule/disease experiences and original scientific coverage.
Next complete contextual links/navigation and saved reading. Machine exact
filter/order/membership and per-cell support conformance remain explicitly pending
in #148. A scientist still needs to try the complete journeys without developer
coaching; passing regressions do not prove an intuitive or exceptional experience.
