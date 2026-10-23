---
summary: Bounded first-version delivery audit and remaining researcher acceptance.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-22
closed:
verification: inspected
area: [public-api, human-exploration, documentation]
blocked_by: []
supersedes: []
---

# First-version exploration closeout

## Boundary

The maintainer requested closure against the actual first-version contract before
expanding the scientific catalogs. The [A–D delivery table](card_exploration_v1_contract.md#5-first-delivery-and-adapter-mapping)
is the scope: complete inspection, initial scientific routes for three natures,
contextual navigation and portable original reading. Activity, clinical, variant,
site and comparative rich panels are later extensions, not prerequisites for
this bounded delivery. Their retained data must still be inspectable.

This audit separates delivered mechanisms from a completed exceptional human
experience. It does not close #148, qualify a release, establish all machine-v1
conformance or resume 0.15.0 consolidation. Existing historical qualification
receipts stay bound to their original source. Runtime source starts here at
`87708a670d1f914affe3d49b3b8d3de7b841dce7`.

## Delivery matrix

“Implemented” means the mechanism has implementation and regression coverage in
the linked files; it does not certify every prose requirement or human usability.
Test paths below are relative to `tests/core/`.

| First-version requirement | Implementation / technical coverage | Disposition |
| --- | --- | --- |
| A: one detached capture, shared human/agent context, defensive values | `test_card_exploration_offline.py`, `test_card_access_offline.py` | Implemented; no implicit source acquisition |
| A: every valid stored node reachable, including unknown natures, literal dotted keys, ordered lists and extension values | Complete traversal/reconstruction cases in the same two files | Implemented; generic access does not invent scientific meaning |
| A: discovery, literal search, bounded text/HTML, complete items and structured rows | `test_card_exploration_offline.py` | Implemented; default presentation/help still needs researcher review |
| B: protein function and canonical-region/structure route | `test_card_protein_exploration_offline.py`, `test_card_structures_exploration_offline.py` | Implemented; structural explanation presentation needs the improvement below |
| B: molecule identity and properties with original methods/units | `test_card_nature_exploration_offline.py`, `test_card_human_labels_offline.py`, `test_card_method_preview_offline.py` | Implemented; no claim of molecule activity/clinical adapters |
| B: disease definition, scoped synonyms, parent relationships and separate identity terminology | `test_card_nature_exploration_offline.py`, `test_card_human_labels_offline.py` | Implemented; missing parent Cards remain explicit |
| B: original explanations, alternatives, missing support and unknown/partial coverage | Nature/wording cases above, `test_knowledge_state_explanation_offline.py` | Implemented; source truth and human interpretation remain separate |
| B: display-only selection/order, typed quantities, exact original result/options | Structural/protein/nature cases and `test_card_agent_selection_offline.py` | Implemented for declared initial columns/routes; broader selectors are separate |
| C: source/endpoint links, explicitly supplied Cards, exact return context | `test_card_context_navigation_offline.py` | Implemented, including unavailable context |
| C: duplicate inputs, revision choices, conflicting identity paths and unsupported joins | Same contextual navigation cases | Implemented; no similarity-based identity or silent revision selection |
| D: original values/support/selection survive change, independent inert reading | `test_card_saved_exploration_offline.py`, `test_card_saved_science_offline.py` | Implemented for initial retained routes; missing variants stay `not_saved` |
| D: atomic no-clobber save, units/bindings, unavailable historical verifier and coherent tampering refusal | Same saved-reader cases | Implemented; no new portable format is introduced here |
| Human acceptance: discover, interpret, recover and revisit without developer coaching | Three public journeys and review tasks below | Open; agent execution is technical preparation only |
| Useful-scale costs and final delivery qualification | Existing [bounded cost observation](card_cell_support.md), #148 deferred CI | Partial; researcher workload budgets and exact final remote gates remain open |

## Reproducible public journeys

The executable [example](../../examples/user_journeys/card_exploration.py) runs the
actual public API with network connections forbidden. It uses the three existing
public inputs from `temp_data/NOTICE.md`; no private pilot, live query, new source,
scientific rule, Card schema or SDK runtime change is involved.

- **TcTIM:** orient to organism/accession and the missing prose function field;
  inspect retained catalytic activity, one of seven structural entries and its
  original source. Structural inspection is not model recommendation.
- **Benznidazole:** inspect exact retained identity, molecular weight with its
  original unit/source, ALogP method and recorded coverage. No target-activity or
  efficacy conclusion is made.
- **MONDO:0014221:** inspect definition/synonym scope, separate identity terminology,
  one of four broader-term relationships, its source and an explicitly unsupplied
  destination Card. No equivalence or diagnosis is inferred from the parent edge.

Each journey exercises an empty display filter and exact return, then saves one
scientific selection with original support. A separate `read` invocation reopens
all three selections without loading fixture files. The adjacent `receipts.json`
is example bookkeeping for original bundle digests/view references, not a new
Sabueso format or independent scientific verifier. Users should retain digests
separately if they require an independent original-artifact check.

Run commands and interpretation notes are in the
[example README](../../examples/user_journeys/README.md#human-card-exploration).
This is a scripted technical demonstration, not an uncoached usability study.

Technical checkpoint: all three producers complete and all three selections reopen
in a separate process outside the checkout, with fixture-file access,
`Card.from_dict`, structural readers and knowledge-state readers forbidden.
Original source links and exact return paths work in both modes. The selected
322 initial human/access/profile/navigation/saved cases pass in 83.01 seconds
with pytest-receptor, twelve workers and fatal runtime/SQLite/unraisable guards.
Formatting, lint, local governance, Markdown/snippet syntax and warning-fatal
Sphinx checks pass. This checkpoint changes documentation/example code only;
the existing SDK runtime and original public inputs/capsules remain unchanged.

## Observed friction and fixed remaining work

The actual TcTIM walkthrough exposes an important usability limit: structural
`item.explain()` initially displays technical keys such as `card_id`, `group`,
`item` and `rules`. Its first item is metadata, not a source assertion. The
original source can already be opened through
`item.related().filter("role", equals="source")`, with a correct return path.
The example uses that declared link rather than pretending that the first
explanation item is a source. This is an observed presentation limitation;
its effect on a new researcher's task success is not measured yet.

Keep the first-version closure queue finite:

1. **Structural support orientation:** provide a readable explanation of the
   retained structural decision/basis and an evident route to its original source
   records, retaining rules, ambiguity, full native details and saved compatibility.
2. **Researcher walkthrough and polish:** run the tasks below with the maintainer,
   then a researcher unfamiliar with internals. Fix observed first-version
   navigation, wording and recovery problems; do not add panels to avoid them.
3. **Workload and final technical checkpoint:** agree useful-scale time/memory
   budgets for those tasks, check them, and recover deferred exact-head CI and
   governance through gh-run-receptor. Preserve the separate installed-artifact
   and release route.

These items replace a generic instruction to finish every nature profile before
first-version acceptance. A newly demonstrated integrity defect remains actionable
under #148, but optional catalog growth does not silently enlarge this queue.

## Researcher review tasks

Record Python familiarity and supplied help. Let the researcher work without
developer coaching; do not count reading this scripted example as task discovery.

| Task | Observe / ask the researcher to explain |
| --- | --- |
| Open TcTIM, find one functional statement and inspect one structural option | Which exact entity/sequence is shown? What does the source state? Does sequence coverage establish coordinate completeness? Can its source and return route be found? |
| Inspect benznidazole identity and a property | Can the researcher find the full value/unit and method/source context? Do they distinguish reported calculated properties from experiments and unknown target activity? |
| Inspect MONDO definition and one parent | Are synonym scope, equivalence, related identifiers and broader terms understood? Does an unsupplied parent mean missing context rather than no knowledge? |
| Recover a no-match filter and reopen a saved selection | Can the researcher recover the original view, explain saved versus new interpretation, and follow the original support? |

Record task completion, wrong interpretations, requested help, navigation detours,
time and memory observations, proposed changes and recheck results. Agree success
criteria with the maintainer before calling this exceptional human usability.
Technical passing counts alone cannot complete this row.
