---
summary: Intuitive human exploration with complete access to retained Card knowledge and its support.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-21
closed:
verification: inspected
area: [public-api, human-exploration, scientific-views, documentation]
blocked_by: []
supersedes: []
---

# Human exploration of Card

## Purpose and decision status

A researcher should be able to open a Card, understand what it knows about a
molecular system, explore the available information and assess options using
explicit criteria and inspectable source support. Starting should be simple;
understanding the details should not require reverse-engineering the schema.

The maintainer requested this plan during the pause before proposed 0.15.0
consolidation (#112). **Accepted direction:** intuitive progressive exploration,
complete inspectability of retained Card content and source-grounded decision
assistance. **Proposed design:** the contracts and delivery sequence below.
Public names, signatures, concrete result types and persistence formats still
require design acceptance. This document implements no API and commits no feature
to 0.15.0; consolidation remains paused.

The [detailed design proposal](card_exploration_detailed_design.md) develops concrete
candidate interactions and separate protein, small-molecule and disease experiences.
Following the maintainer's clarification, share exploration guarantees and familiar
navigation while designing scientific topics, questions and presentations for each
nature. A single scientific view design is not required to fit every Card.

Sabueso knows; it does not discover. Follow [architecture](../ARCHITECTURE.md),
[API conventions](../API_CONVENTIONS.md), [schema policy](../SCHEMA.md) and
[quantity integrity](../../MOLI_GUIDE.md#physical-quantities-and-units).
This is component-local work; a changed shared MOLI contract would require its
own platform coordination. No private pilot content is needed for this design.

## User experience to design for

Use the progression **Card → topic → item → explanation/source**. Support both
guided browsing and a direct route for someone who already knows what to inspect.

Start by opening a saved Card or explicitly resolving/building one with a declared
acquisition scope. Browsing must not implicitly rebuild or refresh it. Orientation
shows the snapshot/date and available source revision bases; an old saved answer
must not look like a current source query. Unknown dates/releases stay unknown.

| Researcher's question | Expected experience |
| --- | --- |
| Which entity am I looking at? | Identity, organism/type and source-stated identity basis; ambiguity is visible before interpretation |
| What information do we have? | A short orientation and discoverable topic catalog, with scope, important conflicts and missing coverage |
| What matters for my question? | A coherent thematic view with understandable items, quantities, context and explicit selection criteria |
| Why is this value or finding shown? | The exact item's explanation, supporting and alternative assertions, original qualifiers and any derivation rule |
| What am I missing? | Distinct unqueried, failed/unavailable, empty-answer, not-stated, partial and conflicting states, with their recorded scope |
| Where is an unusual piece of information? | Local search and a readable structured inspector reaching retained fields beyond the dedicated views |
| How can I use or revisit this? | Programmatic values and saved/exported results retaining the exact snapshot, options, support and limitations |

The first screen should orient, not dump the schema. Keep a small, consistent
set of navigation actions, plain labels, useful help and discoverable topics and
options. A user should not need to know a field path or SourceAssertion identifier
to start. Experienced users must still be able to use those exact references.

Progressive disclosure must never conceal a qualifier that changes interpretation:
identity ambiguity, conflicts, experimental versus predicted structures, censored
measurements, incomplete scope and unknown comparability stay visible where they
matter. Show what a summary omits and how to reach it. Avoid unexplained scores,
empty cells that conflate states and silent truncation.

Text/Python and Jupyter HTML are first-class presentations of the same result.
Use accessible labels and tables; essential meaning must survive plain text and
must not depend only on color, hover or a particular widget. Choose defaults through
public examples and researcher walkthroughs, not by exposing every engine option
on the first screen.

A public TcTIM walkthrough should feel continuous: confirm which source-stated
entity the Card describes; see available topics and gaps; open the structural
inventory; inspect an assembly/chain against an explicit coverage criterion;
follow its supporting source; return to the inventory with the selection intact.
The same navigation concepts should lead from a molecule's activity summary to
individual measurements and their assay context, without changing scientific scope
or requiring the researcher to manage internal identifiers.

### Five required interaction-design refinements

The design review in [#148](https://github.com/uibcdf/sabueso/issues/148#issuecomment-6325377962)
identified the following concrete deliverables. These refine the plan's acceptance
requirements; the interaction prototypes and researcher validation are still pending.

1. **Specify the first contact.** Produce the exact proposed opening presentation,
   with identity and snapshot context, a short source-supported orientation,
   available topics, consequential gaps/conflicts and a small set of useful next
   actions, in that order. Show which details expand on demand. Use verified public
   Card values or clearly marked placeholders, never invented TcTIM findings or
   counts. The prototype must let a newcomer identify the system, understand the
   available scope and choose a next action without a schema explanation.

2. **Provide question-oriented routes.** Complement topic browsing with recognizable
   scientific questions, such as what sources state about function, which sequence
   regions retained structures represent, or which measurements concern a molecule
   and under what conditions. Map each route to explicit retained scope, existing
   views and applicable criteria; explain a missing answer. Question labels do not
   require natural-language parsing or a new inference engine. Deliver a small
   question-to-view map and a complete public TcTIM exploration script.

3. **Connect exploration across areas.** Specify supported transitions between
   structure, site, ligand, measurement/assay and publication contexts. A transition
   must retain exact entity/relationship references, snapshot, effective selection
   and a clear way back; users must not reconstruct internal identifiers or restart
   at the Card root. Follow only explicit supported relationships or declared
   versioned derivations. Missing joins stay visible and do not trigger identity
   guesses or acquisition. Deliver at least one cross-topic walkthrough, including
   a missing-link case and return to the original selection.

4. **Require comprehension as well as reachability.** Define readable labels,
   contextual descriptions, units, relationships and explanations for supported
   scientific content. Routine reading should not require learning SourceAssertion,
   pin, store or schema vocabulary; exact technical names/references remain
   accessible in deeper detail. The generic inspector guarantees complete access
   but cannot substitute for understandable presentation of routine scientific
   information. Deliver a label/context specification and examples distinguishing
   unqueried, unavailable, not-stated and conflicting content. Unknown extension
   semantics remain explicitly unknown rather than receiving invented explanations.

5. **Specify navigation in Python and Jupyter.** For every walkthrough, show the
   proposed calls and exact text/HTML responses, returned-object behavior, available
   next operations, help/discovery path and recovery from an empty or filtered
   result. Identify which transitions are Python calls and which, if any, are
   optional presentation controls; do not assume rich rendering supplies interactive
   navigation. Aim for a small consistent vocabulary, useful autocomplete and
   help, with equivalent scientific access in plain Python. Validate against a
   declared level of Python familiarity without requiring Sabueso internals.

Review these deliverables together: a simple opening that cannot reach an assay's
context, or a complete inspector that a newcomer cannot understand, fails the
combined experience requirement. The next design artifacts are end-to-end public
walkthroughs for each nature, starting with TcTIM and corresponding molecular and
disease examples, showing what the researcher does and sees at each step, with
explicitly supported transitions and honest unavailable states.

## Existing foundations and demonstrated gap

The current [public API](../PUBLIC_API.md) already supplies thematic methods such
as `structures`, `predicted_structures`, `bioactivities`, `clinical`, `literature`,
`entities`, `knowledge_state` and several comparative/site views, with associated
explanations. `table` returns rows for selected topics, preserving quantities;
`sabueso.to_dataframe` is optional conversion. `get`, `list_fields`, `extract` and
`to_dict` expose stored content; `to_notebook` produces an offline report.

These are useful foundations, not evidence of a uniform exploration contract.
For example, explaining a bioactivity currently requires repeating the view's
`include_indirect` and `thresholds` options. `list_fields` walks sections, whereas
the stored Card also contains assertion/relationship stores, quality, entities,
selection rules, metadata, quantity seals and preserved unknown content. A list
of scientific tables alone cannot provide complete access.

Reuse the existing scientific engines, support readers and storage mechanisms.
Add a coherent exploration contract only where these user tasks demonstrate a
gap. Preserve existing public methods and dictionary/list return contracts;
do not turn every method into a new incompatible object or duplicate scientific
rules in a presentation layer. See also the
[implementation review](design_implementation_review.md) and
[scientific usefulness acceptance](consumer_scientific_acceptance.md).

## Proposed exploration contracts

### Semantic results and presentations

A thematic view is a scientific result with context. A summary, table, sequence
track, relation view, detail panel or export presents that result. Not all topics
are naturally tabular. The same value, rule and support must mean the same thing
in every presentation; rendering must not become a separate scientific engine.

Each result needs its entity and exact Card snapshot identity, topic/scope,
effective options, selection criteria, rule identifiers when derived, stable item
references, coverage/limitations and links to support. Human criteria are view
context, not source assertions about a research project. Explain defaults and
record effective values without requiring the user to repeat them for an item.

Declare item and row granularity. A structure entry, assembly and chain are
different objects; a molecule, measurement group, source measurement and assay
are different objects. Avoid ambiguous joins and misleading row counts. Show
displayed, selected and retained counts separately, and source-returned totals
only where known. Neither a row count nor source overlap proves independent
experiments or global completeness.

Filtering and sorting select the presentation of an existing result by default;
they do not silently recalculate scientific classes, discard dissenting support
or change grouping thresholds. Make any explicit recomputation a distinct action,
with its effective inputs and versioned rule. Explain an item using the original
result context, including relevant inputs hidden by a display filter.

Use stable references, not row numbers. Respect existing `_ref` conventions and
dot-separated canonical field paths. Navigation into nested lists or unusual
extension keys needs an unambiguous locator contract without changing frozen
field paths. Reaching a related entity's retained context is browsing; acquiring
another Card or expanding the graph must be explicit.

Illustrative navigation vocabulary, **not an implemented or frozen API**:
`overview`, `topics`, `view`, `search`, followed by a view's summary/table,
filter, item, explanation and export actions. Decide whether unified entry points,
existing direct thematic methods or both best satisfy the walkthroughs before
choosing names. Keep one understandable conceptual model rather than parallel
ways to ask subtly different versions of the same question.

### Complete inspectability without overwhelming the user

Complete access means **all information retained in the Card**, not all information
on the internet or every original provider response. Every retained meaningful
node must have a readable access route: a dedicated thematic view or a generic
structured inspector. Rich topic views may be added incrementally; the fallback
must exist from the first delivered slice. `to_dict()` alone is not human access.

| Retained content | Required route and safeguards |
| --- | --- |
| Scientific fields, nested values and qualifiers | Topic/item detail or expandable literal inspection; preserve names, types and full values |
| Relationships and entity identities | Navigable records with roles, endpoints, identity basis and exact references; no similarity-based merge |
| Selected and alternative SourceAssertions | Readable asserted values, subject, source record/revision/retrieval and selection basis; preserve conflicts |
| Derived findings and selection rules | Named/versioned rules, actual input/support and limitations; never presented as SourceAssertions |
| Coverage, quality and acquisition records | Recorded question/source scope, outcomes, limits and unknowns; source absence is not a negative assertion |
| Quantities and their seals | PyUnitWizard quantities and serialized value/unit records, original bounds/context and technical integrity metadata |
| Bibliography, terms and attribution | Retained source/method references, rights and attribution context, distinguished from scientific support and runtime observation |
| Card metadata and preserved extension content | Readable technical inspection, including stored migration/integrity metadata where present; no unmapped dead ends |

Establish a completeness inventory against the full serialized Card model,
including nested collections and preserved unknown fields. For each retained node,
record its thematic or generic route and verify that navigation preserves the
value, type, unit and reference. An intentional short display is not data loss
if the complete value is reachable. A new schema field must remain inspectable
even before a specialized panel exists. Generic inspection labels literal content
honestly rather than inventing its scientific interpretation.

Original response bodies, full articles and acquisition/runtime traces may be
outside the Card or not retained at all. Show a separately bound archive/sidecar
when available; otherwise state what is unavailable or unbound. Do not infer exact
request membership from a source-level archive association or reconstruct missing
execution history. SourceAssertion, provenance, bibliography and Nextia Evidence
remain distinct. Opening external material is a separate visible action.

### Decision assistance and scientific honesty

Help users understand options through explicit criteria and inspectable context:
for example, which retained structures satisfy a declared coverage criterion,
which activity records concern the requested target, or which source supports a
functional statement. Report supported matches, exclusions, conflicts and unknowns
with reasons. The user must be able to inspect alternatives and change criteria.

Do not silently rank structures or compounds, infer assay comparability or
selectivity, or claim efficacy from heterogeneous records. Any later ranking needs
an explicit scientific contract, criteria, versioned rule and acceptance. No
unjustified global confidence or completeness score. Suggestions should direct the
researcher to relevant retained context or explicit acquisition options, with the
information gap explained; they must not manufacture missing knowledge.

Preserve original quantities, units, relation signs, censoring and experimental
context. Display conversion must name the requested unit and keep original values
reachable. Programmatic and exported values must retain units and meaning; a unit
must not live only in a column name. Missing values need structured reasons, not
just blanks. Project judgments and proposed scientific interpretations remain
outside source knowledge. Existing curation admits source-supported statements;
it does not turn project conclusions into SourceAssertions. This exploration work
does not redefine that contract.

### Snapshot integrity, saved results and execution cost

Bind a result to the exact Card snapshot and effective view context. A later Card
mutation or refresh must not silently alter a displayed item's explanation. An
updated view is an explicit new result. Choose the snapshot/pin mechanism before
implementation, reusing stores and support readers rather than copying a full
Card into every row.

Distinguish saving the exact result from saving a query recipe for later execution.
Reopening the former preserves its original values, rules, options and support
without recomputation. Running the latter is explicit and records new inputs and
rule versions. A bare CSV may be a convenience export, but must not masquerade as
a complete saved result: its omissions and companion context must be clear.

Inspection, local search, display and filtering must not query providers, mutate
the Card, add source assertions or create new acquisition credit. Search locates
retained content; a similar name is not identity resolution. Explicit local derived
views retain their named/versioned rules; inert saved reading does not rerun them.
An LLM, network access or API key must not be required to explore a saved Card.

Representations must be bounded and cheap, with visible display limits and access
to all remaining items. Separate display pagination from acquisition caps. Load
expensive detail deliberately, keep large text/collections navigable and measure
time/memory on declared workloads before setting budgets. Optional dataframe or
rich-rendering dependencies go through DepDigest; plain Python/text remains useful.
Public inputs and diagnostics follow ArgDigest and SMonitor. Invalid options must
offer understandable corrections; scientifically empty/unknown results must retain
their structured state. Preserve supported Python 3.11–3.14.

## Walkthroughs and acceptance

Use public TcTIM/HsTIM/HK2 and existing public molecular/disease examples. Develop
the protein, small-molecule and disease experiences separately under the shared
interaction guarantees. Structural options, molecule/assay measurements and a
source-supported functional statement are contrasting tasks, not a universal
scientific menu. Each nature needs its own opening, questions, detail granularity
and explicit unknown/non-applicable states, as specified in the detailed proposal.

| Acceptance task | What must be demonstrated |
| --- | --- |
| Orient and find information | The concrete opening lets a researcher identify the entity, understand retained scope and choose a useful next action without field-path knowledge |
| Follow a scientific question | A question-oriented route reaches relevant retained information, states its scope/criteria and explains missing answers |
| Continue across topics | An explicitly supported transition preserves identity, snapshot and selection; missing joins are explained and returning restores the original context |
| Inspect structural options | Entry/assembly/chain granularity, experimental/predicted status, criteria, missing coverage and source support remain clear |
| Inspect activity context | Molecule, group, measurement, assay and document are distinguishable; units, signs, target basis and unknown comparability survive navigation |
| Trace one functional statement | Full assertion/qualifiers, alternatives, selection basis and source locator are reachable without guessing identifiers |
| Understand and reach content | Routine scientific fields have readable labels/context; an extension value, technical metadata node and excluded/undisplayed item remain accessible through the generic route |
| Discover the next operation | The Python/Jupyter walkthrough shows calls, responses and help; a newcomer can proceed or recover from empty/filtered results without internal identifiers |
| Explain the exact selection | Changing display filters does not change the original classification or its support; item explanations remember effective options |
| Reopen after change | A saved result remains original after Card refresh/mutation and rule updates; a fresh query is a separate operation |
| Explore offline at useful scale | Plain text and Jupyter remain navigable; bounded rendering, full-access routes and zero hidden source calls are demonstrated |

Technical acceptance requires model-wide access coverage, unit/reference/support
integrity, compatibility, deterministic rule context, saved-result integrity and
bounded rendering. Use meaningful failure cases, including conflicting assertions,
empty/unqueried/failed scopes, mixed units, censored values, ambiguous identity,
large collections and unknown extension keys. Apply the local gates in
[TESTS.md](../TESTS.md) to each eventual implementation slice; examples must run
against the installed checkout and have independently readable saved results.

Human acceptance is separate: researchers unfamiliar with Sabueso must exercise
the walkthroughs without developer coaching, using the declared Python familiarity
and supplied help. They must explain what the results mean, where support comes
from and what remains unknown.
Record task success, navigation difficulties, misunderstandings and the changes
they motivate. Agree usability/performance budgets on these workloads rather than
claiming excellence from test counts or an attractive notebook alone. This document
records inspected capabilities and intended acceptance, **not measured usability**.

## Delivery sequence and open decisions

1. **Design inventory:** map current retained content, existing APIs and user tasks;
   identify reuse and real gaps. Deliver the complete-access matrix and concrete
   public walkthrough inputs, including meaningful failure/unknown cases.
2. **Interaction prototypes:** deliver the
   [five interaction refinements](#five-required-interaction-design-refinements),
   beginning with the complete public TcTIM script and corresponding small-molecule
   and disease scripts, with exact proposed calls/responses for each nature.
   Compare text/Jupyter navigation and generic inspection. Review granularity,
   consequential warnings, cross-topic continuity and discoverability before
   selecting names.
3. **Contract and human review:** exercise the prototypes with researchers; settle
   snapshot/reference semantics, filtering versus recomputation, saved result versus
   recipe, return types and compatibility. Record decisions and bounded acceptance
   in #148. Updating this design does not authorize API implementation.
4. **Explicitly scoped implementation:** after maintainer agreement, deliver a small
   end-to-end slice with the generic access fallback, source tracing and saved-result
   behavior. Reuse existing engines; update public contracts/docs alongside code.
   Later topic panels extend this surface without hiding retained content.
5. **Qualification and consolidation review:** demonstrate technical and human
   acceptance, measure costs, reconcile foundational and consumer-driven priorities,
   and separately decide release scope. No automatic resumption of 0.15.0.

Open decisions include the smallest public vocabulary; whether a lightweight view
object or an existing-result adapter fits best; stable nested locators; exact
snapshot binding for unsaved mutable Cards; saved-result format/ownership; search
scope; and measured display/performance defaults. Avoid a new schema/store/report
framework unless the accepted use case requires it. Any eventual schema change
follows the unpublished-version policy and migration rules.

Alternatives considered: raw dictionaries alone preserve access but leave too much
interpretation/navigation work to the user; tables alone flatten context; a large
new facade implemented upfront risks duplicating engines and freezing an untested
interaction model. Prefer progressive exploration with complete fallback access,
tested through concrete tasks before freezing the public surface.

## Resolution

Open under [#148](https://github.com/uibcdf/sabueso/issues/148), coordinated with
[#112](https://github.com/uibcdf/sabueso/issues/112). No implementation or human
usability acceptance is claimed. The prior
[saved-consumer review](pilot_usefulness_review_20261021.md) retains its narrower
technical scope and its separate primary-method/scientist-review gaps.
