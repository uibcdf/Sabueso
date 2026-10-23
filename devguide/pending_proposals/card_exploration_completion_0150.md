---
summary: Maintainer-required complete exploration design and human acceptance before 0.15.0.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-22
closed:
verification: inspected
area: [public-api, human-exploration, scientific-views, release]
blocked_by: []
supersedes: []
---

# Complete Card exploration before 0.15.0

## Maintainer decision and release gate

On 2026-10-22 the maintainer explicitly required **the entire broad exploration
design and the human experience before 0.15.0**, including activities, clinical
context, variants, sites and comparisons. This supersedes treating those panels
as extensions after this release. The [A–D checkpoint](card_exploration_v1_closeout.md)
remains an intermediate milestone; completing its finite queue alone cannot
admit 0.15.0. The [detailed nature-specific design](card_exploration_detailed_design.md)
and [human exploration plan](card_human_exploration_api.md) define the target.

The implementation remains authorized. Version changes, schema freezing,
candidate selection, staging, publication and release consolidation remain paused.
No human usability, full implementation or release qualification is claimed by
this decision. #148 owns local exploration delivery; #112 owns release coordination.

## Broad profile delivery inventory

Each row needs a scientific presentation and supported navigation, not merely a
generic dictionary browser. Existing readers and their original explanations,
rules and scope are reused; missing adapter work is distinguished from missing
source knowledge. Current initial routes are implemented in development, not
accepted as the complete broad profile.

| Nature / topic | Current exploration position | Completion requirement |
| --- | --- | --- |
| Protein: function | Initial fields/question delivered | Finish broad-profile integration and researcher review of original function/organism/sequence scope |
| Protein: sequence and annotated regions | Literal access; canonical-region structural question delivered | Readable sequence-axis/feature view, numbering and unplaced annotations, supported source/region navigation |
| Protein: experimental structures | Initial adapter, selection, saved reading and readable original support/source orientation delivered | Complete chain/assembly detail and cross-topic transitions; qualify scientist interpretation |
| Protein: predicted models | Existing `predicted_structures()` reader; no rich explorer panel | Distinct model/version/metric presentation and original support; never imply experimental equivalence |
| Protein: sites and molecular contacts | Existing residue/site/interface readers; no rich explorer panel | Source sites/contact instances, explicit axes, original overlap rules and transitions to structure/sequence |
| Protein: variants and isoform context | Existing tissue/variant/isoform readers; no rich explorer panel | Original genomic/transcript/isoform context, per-tissue unknowns, named rules and scoped support |
| Protein: comparative context | Existing comparison readers; no rich explorer panel | Explicit supplied-Card comparison, relationship basis and maps where required; no identity merge by similarity |
| Protein: molecules and measured activities | Existing protein-centered `bioactivities()` and explanations; no rich explorer panel | Molecule/group/measurement/assay/document drill-down with original target assignment, units, qualifiers and comparison limits |
| Protein: biological associations | Existing stored relationships/readers; no rich explorer panel | Typed disease/pathway/interaction context with exact direction and original support; no invented causality |
| Molecule: chemical identity | Initial chemistry fields and source identity links delivered | Broad-profile presentation of retained stereochemical/charge/parent context, including absent/ambiguous scope |
| Molecule: physicochemical properties | Initial fields/methods/units/alternatives delivered | Complete nature-specific presentation and scientific interpretation review; calculated/measured/unknown stay distinct |
| Molecule: chemical classes and roles | Retained ChEBI mapping; no rich explorer panel | Readable direct/inherited source classes/roles; no inferred pharmacological effect |
| Molecule: target/activity context | Literal retained context; no rich explorer panel | Exact molecule identity join to retained or explicitly supplied measurements; never apply a protein-only reader to a molecule |
| Molecule: indications and clinical studies | Existing `clinical()` semantics; no rich explorer panel | Separate indication, source-cited trial and fetched registry record; explicit unqueried/failed scope and source-specific status |
| Disease: definition and terminology | Initial definition/synonym/term context delivered | Complete broad-profile orientation, source/release/term-status presentation and researcher review |
| Disease: classification and related terms | Initial parent/identity routes delivered | Clear hierarchy/equivalence distinction, exact supported transitions and full original scope |
| Disease: retained associations | Literal/source inspection; no rich explorer panel | Explicitly retained molecular/clinical relationships or supplied-context associations; identifier basis and direction stay visible |
| Shared: identity, sources, coverage and full content | Initial discovery/inspection/support/coverage delivered | Consistent integration across all panels; generic/unknown natures retain complete literal access |
| Shared: literature | Existing literature readers/explanations; no rich explorer panel | Publication roles, exact cited identities and original locators; no implication that every paper supports every displayed claim |
| Shared: contextual navigation and saved reading | Initial capture/navigation and structural/field/coverage history delivered | Support every newly delivered panel's exact options, source closure, independent inert reading and explicit new interpretation |
| Shared: compact agent access | Literal and structural exact selection delivered | Bring the agreed agent contract to new scientific adapters; equivalent requests share science, scope, units and support |

An unsupported/unqueried state is a legitimate answer for a particular captured
Card. It is not proof that a missing rich adapter is implemented. Each panel
needs a positive public-data example and applicable missing/partial/conflicting
or non-applicable cases. Identity, quantity and support contracts remain mandatory.
No browsing operation may acquire new data, refresh a Card or fabricate findings.

## Implementation order

1. Finish readable structural support/source orientation and its saved compatibility.
2. Complete protein sequence, predicted models and sites/contact/assembly routes,
   sharing existing axes, residue knowledge and original structural support.
3. Complete activity/assay/document and shared literature journeys, then molecule
   target context and clinical/classification views with explicit identity joins.
4. Complete variants/isoforms/comparisons and biological/disease associations with
   explicitly supplied context and original genomic, numbering and source scope.
5. Qualify broad-profile navigation, saved reading and compact agent parity for
   all delivered routes. Review opening menus, defaults, errors, empty recovery
   and support wording as one coherent experience.
6. Complete human walkthroughs, workload qualification and final technical gates
   before considering release consolidation. Do not declare the experience
   exceptional solely from tests, generated panels or implementation checkmarks.

Every implementation block updates this inventory, its technical tests and #148.
Use bounded public fixtures; private pilots remain read-only and do not enter
public examples or tests. A missing scientific reader/identity contract requires
a concrete design and owning issue; it does not authorize an implicit heuristic.

## Human acceptance and the intended exceptional experience

Researchers with declared Python familiarity must be able to orient themselves,
find relevant scientific questions, select and compare supported options, inspect
their full sources/qualifiers, recover from empty or ambiguous states, cross topics
without losing context, and reopen the original reading after change. They must
understand the difference between a selected value and alternatives, an unqueried
source and absence, a relationship and identity, and calculated versus measured
or unknown methods. Essential interpretation must work in text and Jupyter.

Prepare actual public protein, molecule and disease journeys across the broad
panels. Record task success, misinterpretations, navigation/help needs and fixes;
include the maintainer and a researcher unfamiliar with internals. Agree
workload-specific time/memory budgets and verify them, distinguishing capture,
materialization, cached interaction, persistence, process memory and response size.
Human acceptance needs observable reviewer feedback, not an agent's prediction
of a positive reaction. Agent conformance and human usefulness are separate gates.

Before 0.15.0, every row above must have its implemented scope, relevant public
walkthrough and technical receipt, with human acceptance recorded for the combined
experience. Final exact-SHA CI/governance through gh-run-receptor and the existing
installed-artifact/release gates remain mandatory. Only then may the maintainer
decide to resume the separate release route.
