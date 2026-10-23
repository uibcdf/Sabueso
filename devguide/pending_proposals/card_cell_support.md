# Structural cell support and measured access costs (#148)

This continuation closes the structural adapter's per-cell machine support gap.
It does not complete machine adapters for other topics, broader scientific
profiles, researcher acceptance or remote qualification. The pause before 0.15.0
consolidation remains in effect.

## Cell meaning and complete support

Each projected cell identifies its adapter/column in `field`, its original
`state`/`reason`, `support_basis="relationship_level"`, and `support_ref` identifying
the original relationship. It matches the containing item's inline `support.ref`,
or the original `relationship_id` reached through `support_location` when deferred.
That shared support lists every original
SourceAssertion member, its retained/not-retained state and its exact original
location when present. Membership is not repeated for each column. This is
relationship support, not fabricated assertion lineage for individual qualifiers.
Named scientific rules and mandatory scope/conflict information remain in the
item's interpretation. Complete original support/rule/explanation records remain
at `support_location`; projection never removes them from the captured result.

Cells also expose exact `value_location` and `interpretation_location` paths.
The field identity names the adapter column, not an invented Card/source path.
Resolution's provider QuantityRecord independently retains the canonical
`relationships.has_structure.resolution` field and angstrom handshake. Display
`label` aliases the retained structure reference; display `kind` is a located
adapter literal, never a new SourceAssertion. Subject and relationship refs remain
explicit, with the exact captured revision identified by the original locations.

When values, mandatory interpretation or support membership exceed the byte
budget, the item defers them atomically. Its typed cells retain field identity,
scientific state/reason, support basis/ref and value/interpretation locations,
with `value_included=false`; selected values and partial support are not emitted.
The item has `inspection_required=true` and the page `values_complete=false`.
Zero projected columns do not bypass mandatory interpretation/support. This is
delivery metadata: unknown/conflicting cells retain their scientific states.
Original scoped coverage still has its independent inspection requirement.

An item that fits completely on a fresh page starts that next page when previous
items used the remaining space. It is not unnecessarily deferred to fill a page.
An indivisible deferred frame that still cannot fit retains the existing explicit
blockage/retry contract. Record/byte bounds cover the whole canonical envelope.

The current delivery layer applies to live and historically verified inert results.
Original scientific wire schemas, derivation/selection policies, quantities,
identities and saved formats are unchanged. The original filtered machine capsule
from `f720d14` joins the two earlier historical fixtures; its unchanged producer
bytes exercise current delivery without current scientific execution. See the
[fixture declaration](../../tests/core/data/README.md).

## Bounded cost observation

The [machine-readable receipt](../evidence/card_exploration_costs_20261022.json)
records the exact public TcTIM input, implementation hashes, environment, individual
samples and verification scope. It was measured over the changed implementation
based on `f720d14`, before committing it; the SDK label is the one actually observed.
One task selects 1SUX from seven structures and projects method, resolution and
coverage. No source access is permitted. Imports/input loading/setup are excluded;
each operation has one excluded warm-up and three serial timing samples. Memory
is measured in a separate single execution with tracemalloc: new Python
allocations within that operation, excluding setup, not RSS or total workflow memory.

| Operation | Median seconds | Traced peak allocated bytes |
| --- | ---: | ---: |
| Detached capture | 0.038050429 | 2,070,897 |
| Materialization and selection, capture already prepared | 0.042201170 | 2,512,381 |
| Page over the cached result | 0.000716477 | 37,723 |
| Save the selection and complete original session | 0.455616560 | 8,744,458 |
| Read and verify original session | 0.296560216 | 8,680,956 |

The complete page is **5,768 canonical UTF-8 bytes** within its 8,192-byte budget,
including inline values, interpretation and support membership. The input file is
517,500 bytes, captured Card canonical data 319,305 bytes, and the saved fresh
session 1,063,518 bytes. These are different objects, not a like-for-like savings
percentage. The historical multi-step producer session is 89,849,893 bytes before
fixture compression: retained history/support can greatly exceed one page or one
fresh session. Do not infer storage scale from a compact response.

Reproduce from the repository root, with the shared editable SDK installed and a
new task-owned output directory:

```bash
python devtools/measure_card_exploration.py recovered_work/my_card_cost_observation
```

The tool refuses an existing output directory, performs no acquisition and removes
only its exact generated session files after successful measurement; the receipt
remains. These are local observations for one public task with a warm filesystem,
not performance thresholds, token counts, scaling guarantees or human acceptance.
Other natures/topics, populated sessions and whole-process memory need their own
measurements before broader cost claims.

## Acceptance and remaining work

Regression cases reconstruct values/interpretation/support through bounded public
reads for all nine structural projection columns. Synthetic large-support,
large-conflict and large-value cases test typed atomic deferral with empty/single/
full projections; missing assertion members and unknown/conflicting states stay
explicit. Pagination tests cover complete next-page delivery and retry identity.
Original frozen-capsule reading forbids current scientific entry points and source
access, retaining its original wire and versioned selection policy.

Twenty-one new cases and all 598 selected cases pass in 71.05 seconds with twelve
pytest-receptor workers and fatal runtime/SQLite/unraisable guards. All 6,786
local-original offline cases pass in 623.79 seconds, with twelve receptor workers,
fatal SQLite/unraisable guards and thirteen expected fixture warnings. Applicable
static, fixture-delivery, dependency, local governance and warning-fatal Sphinx
gates pass. Exact publication/environment and source fingerprints belong to #148.

The subsequent [human wording continuation](card_human_support_labels.md) now adds
source-role and ontology previews over the original records. Broader molecule/
disease scientific machine selection, technical conformance over their specialized
semantics and researcher walkthroughs remain separate #148 work. Remote exact-head and installed-artifact
qualification remain under the [deferred-CI route](deferred_ci.md); a local pass
does not close those gates or select a release.
