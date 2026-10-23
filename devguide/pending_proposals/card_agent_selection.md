# Structural agent selection (#148)

This continuation implements the initial structural machine selection grammar
from the [agent contract](card_agent_access_v1_contract.md). It does not complete
all machine conformance, broader nature-specific scientific adapters, measured
cost or researcher acceptance. The 0.15.0 consolidation pause remains in effect.

## One scientific result, explicit display selection

`CardAccess.select("structures", fields=None, where=None, item_refs=None,
order_by=None, options=None)` uses the same captured structural result as the
human explorer. Scientific options still define that result; display criteria
never change its scientific exclusions, source coverage, rules or item identity.

- `where` maps exact declared columns to typed equalities, combined with AND.
  Comparison reuses the human scalar/list/object and physical quantity rules.
  Unknown cells do not match an equality. Resolution requires a finite scalar
  length quantity; its retained operand is a field-bound QuantityRecord in
  angstrom, independent of session defaults.
- `item_refs` restricts exact membership in this result. An empty list selects
  nothing; malformed, duplicate and foreign refs fail. Caller order does not
  reorder the adapter: membership is normalized as a set with sorted references.
- `order_by` has `column`, optional boolean `descending=False` and optional `unit`.
  It reuses human type/dimension checks and missing-last behavior, also for an
  empty selection. Scalar ties retain deterministic structure-ref/relationship-key
  order; lists and objects have no invented sort order.

Invalid syntax/types/units fail through SMonitor ArgumentError before scientific
materialization. Foreign membership fails after the result is known. Backend
guards remain active with digestion skipped; `where`, `item_refs` and `order_by`
each have their own ArgDigest digester. No new dependency or scientific rule is
introduced.

## Exact requests, complete support and economical pages

Unrestricted requests keep their original `scientific_access_selection@1` handles
and meaning. Restricted/ordered requests use `scientific_access_selection@2`,
binding fields and the versioned `structure_access_selection@1` policy record.
Changes to comparison semantics, ordering or operand normalization require a new
policy version; historical verification never switches to current helpers.
That record retains normalized operands/order/membership, exact ordered members,
underlying/selected counts and each display exclusion's location, reason and cell
state. Read it through the page's `context.context_location`; projection does not
inline this potentially large metadata. The original full result remains available
through the target/native locations, including excluded rows and original support.

The topic catalog advertises selection policy/operations at the access layer.
The original `structure_exploration@1` result schema stays frozen. Its historical
machine-capability flags describe that original adapter declaration, not current
access-layer policy. Item/byte bounds, deferred interpretation, source-support
locations and session/selection-owned retryable cursors keep their existing
contracts. An empty display selection never becomes an empty scientific inventory.

## Saved reading

The shared scientific bundle retains the exact selection and full original result.
The frozen v1 selection policy verifies its decisions against the original result,
using historical comparison helpers; it does not call current scientific producers
or current comparison helpers. Unknown policy versions and coherently rebound
member/exclusion/quantity decisions and invalid or duplicate projected columns
are refused independently of their rebound hashes. Original format @1 literal and
scientific producer capsules remain unchanged and readable.
`validation.verified_selection_policies` names the policies actually checked,
separately from `verified_scientific_rules`; display selection is not new knowledge.

Saved `select` only returns an exact retained request/projection; another request
is `not_saved`. A partial/ordered machine selection is not substituted for the
unrestricted human structures topic. Complete original native content remains
inspectable; starting a new interpretation stays explicit with `start_new()`.
Request identity uses canonical typed data, not Python's loose numeric equality:
integer and floating operands can identify distinct requests. Provider quantity
records retain their numeric type as well as their explicit field/unit binding.
Use `access.selection(selection_ref)` to retrieve a known retained selection
without restating its operands.

## Acceptance

Regression coverage includes public TcTIM human/machine equivalence, typed
quantity operands and changed session policy, exact/foreign/empty membership,
unknown cells, deterministic ties, cursor isolation/retries, exact byte/record
bounds, original support, caller mutation isolation, saved/resaved requests,
independent-process historical reading and coherent selector tampering. Test and
publication receipts are recorded in #148 after the applicable gates complete.

All 577 selected cases pass in 104.86 seconds with twelve pytest-receptor workers
and fatal runtime/SQLite/unraisable guards. This continuation adds 66 cases.
All 6,765 local-original offline cases pass in 783.63 seconds, with twelve receptor
workers, fatal SQLite/unraisable guards and thirteen expected fixture warnings.
Source fingerprints and final post-installation/publication receipts belong to #148.

The subsequent [cell-support continuation](card_cell_support.md) adds structural
per-cell interpretation/support conformance and one public capture/materialization/
page/save/read observation. Continue broader-topic conformance, populated-session
and other-nature costs, and researcher acceptance. Small output alone does not
establish cheap computation, complete scientific coverage or researcher usefulness.
