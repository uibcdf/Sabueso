# Initial molecule/disease exploration and shared coverage (#148)

This development continuation implements the next initial profiles in the
[v1 contract](card_exploration_v1_contract.md), following the
[protein journey](card_protein_exploration.md). Human navigation remains the
priority; complete machine conformance, contextual cross-Card navigation, saved
reading and researcher acceptance remain separate. The 0.15.0 pause continues.

## Delivered routes

| Nature | Opening and topics | Question aliases |
| --- | --- | --- |
| Small molecule | Source-stated identity, representations, formula, native identity links and retained physicochemical properties | `chemical_identity`, `property_context` |
| Disease | Ontology definition/references, scoped synonyms, retained term metadata, exact focal parent edges and separate identity terminology | `meaning`, `classification` |
| All three supported natures | Original source/area knowledge states and lazy exact scoped explanations; original quality records remain separate | `view("coverage")`, `view("quality")` |

The shared field presentation now declares each panel's nature, labels and exact
typed locations. New molecular/disease questions dispatch to those same views;
they do not create a second result engine. Scientific field selection remains
label/kind based; disease hierarchy supports subject/predicate/object selection,
and coverage supports its declared scalar columns, with unknown counts last.
Unknown options and unsupported columns are argument errors even with digestion
skipped. Known routes on the wrong nature are explicitly not applicable.

Chemical identity shows only retained `same_as` statements, without merging by
name, representation or similarity. A property value remains distinct from its
method and source. Molecular weight and polar surface area use the existing
field-bound PyUnitWizard codec with explicit field/unit expectations; raw field
nodes and original source units remain available. No new quantity format, schema,
chemical calculation or experimental classification is introduced.

Field explanations retain selected support, every retained unselected assertion
for the same field, stored selection alternatives and conflicts. The direct source
list includes original selected and alternative records; the structured support
payload identifies their roles. Unretained references stay explicit, and missing,
null, empty and unrecognized stored shapes remain distinct. Literal property keys
containing dots keep exact typed locations. All content remains accessible through
generic inspection, regardless of panel admission.

Disease hierarchy shows stored `subclass_of` records for the exact focal subject.
Other-subject edges remain in complete literal inspection. Equivalent identifiers
and related xrefs have separate labeled fields in `identity`; neither creates new
hierarchy edges. Original relationship-level support and derivation remain intact.
The classification view explicitly points to identity terminology. Parent Cards
are not automatically joined, opened or fetched, even when supplied as context.
Ontology terminology never becomes a diagnosis; missing term status never becomes
an inferred active/obsolete state.

## Original coverage, capture and access

`view("coverage")` materializes the existing `knowledge_state@5` result once for
the focal capture. `item.explain()` lazily materializes the exact existing
`explain_knowledge_state(area, source)` result and caches it at that original scope.
It retains `knowledge_state_explanation@2`, classification inputs, selected and
alternative scientific support, unclassified context and gaps. Repeated display,
filtering, sorting, item inspection or explanation reading does not reclassify a
materialized result. A previously unrequested row explanation remains an explicit
local computation, not a claim of zero algorithmic cost.

Every native row/state/count/release is preserved. Source/request outcome is not
per-request assertion membership; unknown counts are not zero. Only the original
classifier's actual areas are enumerated. An absent row is not negative knowledge
or proof that its provider was queried. There is no new global completeness score.
Missing pinned identity is an operational prerequisite gap, without executing the
coverage reader or fabricating support. Generic unrecognized natures keep literal
coverage/quality inspection rather than an inferred scientific profile.

These panels share the explorer's detached immutable input and typed literal
result registry. All new item payloads are available through
`explorer.access.read(item.payload_location)` with the existing bounded pages;
the machine scientific selector still advertises structures only. No projection,
filter/membership grammar or per-cell machine support conformance is claimed for
these new panels. Context states the focal capture actually used; supplied related
captures do not silently become scientific inputs.

## Verification and remaining work

Thirty-seven new cases use unchanged declared public ChEMBL, MONDO and frozen TcTIM
inputs, with sockets forbidden; altered negative variants are explicitly synthetic.
They cover exact original quantity/source/method support under a non-default unit
policy, selected/alternative statements, disease scope/equivalence boundaries,
literal keys and unrecognized shapes, original native coverage/explanation parity,
state/count preservation, one-time capture, lazy cache behavior, defensive bounded
rendering, argument guards and absence of new attribution. Two reproduced development edge cases are corrected:
null selection-support metadata retains actual field assertions as unclassified
context, and skipped digestion rejects array-shaped options before value comparisons.
Neither failure is attributed to an upstream provider. The previous protein
negative tests now distinguish the other natures' own delivered question catalogs.

All 341 selected cases pass in 27.58 seconds with twelve pytest-receptor workers,
including prior human/access/argument, native knowledge-state/explanation and
quantity cases. RuntimeWarnings, unclosed SQLite and unraisable guards are fatal.
Ruff, fixture delivery, dependency routes, schema alignment and local governance
pass; warning-fatal Sphinx HTML passes. Eighteen user-guide code blocks execute
with all three public Card natures and sockets forbidden. Six changed Python files
parse as Python 3.11; fourteen installed suite-member editables and seven
participating imports verify outside the checkout. All **6,537 full local-original
offline cases pass in 540.61 seconds**, with twelve receptor workers, fatal
SQLite/unraisable guards and thirteen expected fixture warnings. Original source/input
fingerprints remain unchanged; the exact intermediate SHA is recorded in #148. [Deferred CI](deferred_ci.md) does not qualify remote OS/minor,
installed-package or hosted-governance lanes; prior qualified-source/release
receipts remain original. No private pilot data, new source query, fixture or
schema change is included.

The [contextual navigation continuation](card_context_navigation.md) now adds
retained links and explicit cross-Card transitions. Next: portable saved reading,
coordinated machine conformance and measured cost. Human
acceptance must check that researchers can distinguish selected support from
unselected alternatives in the preview, navigate without schema knowledge and
interpret coverage correctly. Passing tests do not establish the intended
exceptional scientific experience.

The discovery-copy refinement observed at this checkpoint is corrected in the
contextual-navigation continuation: generic fallback discovery now explicitly
describes literal, unevaluated quality inspection. Its classifier/data behavior
remains unchanged. Researcher review should still check clarity of this boundary.
