# First portable exploration reading (#148)

The [scientific continuation](card_saved_science.md) now adds format @2 and
historical checks for the initial structural/region/coverage routes. This document
retains the original literal @1 contract, first-slice limits and original receipts;
the continuation records current scientific behavior and remaining acceptance.

This is the first bounded slice D after [contextual navigation](card_context_navigation.md).
It supports literal inspection, initial field profiles, retained disease hierarchy
and contextual navigation. Derived structural inventories, region questions and
knowledge-state results/explanations still require historical scientific verifiers;
the complete D contract remains open. This is development behavior, not a release
or resumption of 0.15.0 consolidation.

## Public behavior

- `CardView.save(path, overwrite=False)` writes a self-contained UTF-8 JSON bundle
  `sabueso.card_exploration@1`. It returns `path`, canonical `bundle_digest` and
  `root_view_ref`. `AccessSelection.save` uses the same bundle and reader for
  supported literal machine selections, retaining the original `XA_` request.
- `sabueso.read_exploration(path, expected_digest=None)` returns a saved `CardView`.
  Its explorer/access mode is `saved`; representations explicitly say so. Retained
  values, labels, cells, units, support, full underlying results, display selections,
  source records and actual return paths are preserved. Equal semantic view handles
  may have distinct navigation histories; both remain recorded.
- `view.validation` reports integrity, input/value/unit/support/request bindings,
  recorded navigation-decision verification and the separate unverified scopes.
  Hashes do not establish source authenticity or scientific truth. An independently
  retained expected digest additionally checks the caller's original bundle binding.
- `explorer.start_new()` creates a fresh local interpretation over the same detached
  captures. It does not serialize the caller's Cards, fetch sources, select a store's
  latest snapshot or change the saved result. New scientific computation is explicit.

The bundle includes every contributing captured Card once, with its existing seal;
it can contain more information than the visible filtered table. Source response
archives, article bodies, runtime/bibliography sidecars and external provenance
records are not packaged. Their retained references do not become fetched content
or new acquisition credit. Original public fixture bytes and Card schemas are unchanged.

## Preparation, closure and inert reading

Saving a live supported view prepares original literal support and recorded context
links for already materialized results, including display-filtered items. It does
not execute unvisited scientific topics or recursively materialize every support
view. The original capture factory remains the sole intake; saving/reading never
mutates the caller Card or creates SourceAssertions.

Required root/ancestor explanations and links must be present. A missing required
member is a `StorageError`, not a silent capability downgrade. An unretained
optional explanation/link or scientific request returns `not_saved`, with no
scientific reader or live identity join. Supported scientific field/question routes
reuse only retained variants; saved topic discovery distinguishes unavailable ones.
Literal traversal/search remains available over complete captured data. Cold literal
nodes can therefore be read even when their original explanation closure was not
saved; their capabilities expose that distinction. Saving such a new root requires
its retained closure or an explicit new local exploration.

Source, related-Card, missing-context and ambiguous-revision navigation preserve
originating selections. Subsequent operations through a destination's explorer also
retain the original transition. Identity uses only the original recorded source
basis; reading does not discover new identity paths. Anonymous captures retain their
local snapshots, distinct from context-only destinations with null focal identity.

Saved machine selections restore their original request through the `selections`
catalog and `selection(original_selection_ref)`. Fresh local cursors are issued;
old live/saved-session cursors are not transported. Record/byte page limits and
full/deferred literal value delivery keep the established protocol.

## Independent validation and atomic writes

The `literal_exploration_binding@1` verifier checks captured snapshots and quantity
seals, typed locations, literal/field values and units, original support, field and
hierarchy membership, exact request/selection identity, display filtering/order,
required closure and root machine bindings. Recorded `retained_context_links@1`
decisions are checked independently against captured source-stated paths, candidate
pins and blocked/missing support. This is recorded-decision consistency validation,
not a call to the live scientific view or identity navigator. Labels/reason wording
remain recorded presentation metadata; scientific classifications are not admitted
by this verifier. Unknown required formats/verifiers are explicit errors.

Quantity cells use PyUnitWizard `QuantityRecord` with declared field/unit handshakes;
captured Card seals are retained unchanged. Verification compares physical source
values and required field/unit bindings, allowing compatible provider codecs without
inventing another unit representation. Ordinary extension lookalikes remain literal.
All member digests and the whole canonical bundle digest are checked. Duplicate JSON
members, changed values against unchanged captures, foreign membership and missing
retained nodes fail even when outer hashes are recalculated. Optional presentation
metadata survives reading and resaving without gaining scientific meaning.

Writes validate before publication, use a temporary sibling and atomic replacement,
and refuse existing outputs by default through atomic no-clobber publication. Failure
preserves the previous destination. The owning issue retains final source/gate receipts.
No dependency, shared MOLI contract, Card schema or migration changes are introduced.

## Qualification of this slice

Forty-five new public/synthetic cases cover original values/units/support,
display/history preservation, inert independent-process reading, exact requests,
missing/ambiguous context, atomic publication and coherently rehashed malformed
bundles. The selected human/access/argument, structural/state and both quantity
suites, including the integrated #150 diagnostic receiving, pass 471 cases with
twelve pytest-receptor workers and fatal runtime,
SQLite/unraisable guards. Twenty-three public guide blocks execute with sockets
forbidden; four actual API panels and the validation report retain that scope.
Warning-fatal Sphinx, Ruff, local documentation/compatibility checks and applicable
fixture/schema/dependency/governance gates pass. Exact source and final full-suite
receipts are recorded in the owning issue. All 6,629 full local-original offline
cases pass in 740.21 seconds with twelve receptor workers, fatal SQLite/unraisable
guards and thirteen expected fixture warnings. Researcher acceptance remains pending.

## Remaining work

The first slice does not qualify persistence of derived structures, regional
classifications or knowledge-state results. Their `save` capabilities are false,
including literal projections into unsupported scientific result trees; missing
historical verification raises `StorageError`. Unrelated unsupported materializations
are excluded rather than smuggled into a supported bundle. Their captured raw Card
content remains accessible through ordinary literal inspection.

Complete historical verifiers and saved scientific closures next, then remaining
machine selector/support conformance, measured access/storage cost and researcher
walkthroughs. Source-preview selected/alternative roles and direct-versus-derived
ontology labels remain presentation work. Exact-head remote CI/installed/governance
qualification follows the [deferred route](deferred_ci.md); prior receipts remain
original. Passing automated and independent-process cases does not establish human
usefulness or the intended exceptional experience.

## Windows test text I/O correction — 2026-10-22 (#148)

The first ordinary matrix including this slice exposes four Windows/Python 3.12
failures at `45070f9`: tests read UTF-8 exports/bundles with the default code
page, corrupting Unicode before comparison or intended closure/adapter checks.
The product writer and reader already explicitly use UTF-8. All four native
failure shapes reproduce locally with a temporary CP1252-default Path fixture.

Twelve test text I/O calls now name UTF-8. The 45 existing cases pass both under
that simulation and the normal Linux/Python 3.14.9 locale, using published
pytest-receptor 1.2.0. Unicode values, mutation/seal logic and exact expected
failures stay intact. No runtime/storage or workflow-wide encoding change is
made. The [dated receipt](../evidence/windows_utf8_test_io_148_20261022.json) fixes
source/log hashes, the simulation and complete integrity-checked results.
A simulation does not replace native Windows qualification: final exact-head
ordinary CI/governance evidence is recorded in #148 and #151. The original
failed run is not passing evidence. This test correction does not expand
scientific saved adapters, qualify protected originals or publish a release.
