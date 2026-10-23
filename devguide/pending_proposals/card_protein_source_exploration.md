---
summary: Original sequence, predicted-model and site/contact source exploration.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-23
closed:
verification: inspected
area: [public-api, human-exploration, scientific-views, storage]
blocked_by: []
supersedes: []
---

# Protein sequence and source context

This continuation delivers four retained-context routes under the
[complete exploration design required before 0.15.0](card_exploration_completion_0150.md).
They present original retained protein knowledge with readable labels and shared
source/back/saved access. They do not complete all derived scientific adapters,
compact scientific selectors or human acceptance.

## Delivered routes

| Topic / question | Original retained content | Scope |
| --- | --- | --- |
| `sequence` / `sequence_annotations` | UniProt identifier, primary sequence, length, molecular weight, checksums and every stored positional-annotation field | One original field per row; unknown feature keys remain explicitly other annotations; no alignment or location projection |
| `predicted_structures` / `predicted_models` | Exact-subject `has_predicted_structure` relationships | One original model declaration per row, with version/tool, source metric/bands/range and recorded isoform/match context; no computed current coverage or experimental equivalence |
| `sites` / `retained_sites` | Original active/binding/family-site fields and exact-subject ligand/interface contact relationships | Source annotations and contact declarations stay distinct; no overlap, proximity, cavity, instance merge or new source knowledge |
| `ligand_instances` / `structure_ligands` | Individual literal instances inside exact-subject `has_structure.qualifiers.ligands` declarations | One original instance per row; select by structure/component/instance; original mapped contact numbering and distances stay explicit, without assembly or PDBe aggregate joins |

The original function and region questions keep their initial catalog order.
Model/contact relationship selection requires a consistent retained canonical
UniProt identity. Missing or conflicting identity is a prerequisite gap, not a
source-absence finding. Foreign subject relationships are not admitted by matching
names, residue numbers or model labels. Source annotations with different or
unknown axes remain visible exactly as stated; displaying them does not place
them on the focal sequence.

Annotation field previews name the original sequence axis, indexing, endpoint
modifiers and bounded fragments. Opening a field offers **Annotations**, then
readable annotation items; complete original data and source references remain
available. A source label or preview never becomes an item identity: typed
locations preserve literal keys (including dots), source record IDs and ordered
indices within the captured snapshot.

Original field support supports the entire selected annotation field; it is not
invented per-feature attribution. Model/contact source rows retain relationship
support without assigning every qualifier an independent source. The existing
`residue_knowledge`, predicted-structure and comparison engines
are unchanged by these source panels. The subsequent
[contact integrity correction](card_contact_mapping_integrity.md) strengthens
new RCSB mappings and native ligand-instance identity/position scope. Derived
coverage, overlap, instance and cross-topic interpretation
remain integration work in the broad design, with their existing scientific rules
and explanations; these panels do not duplicate those calculations. Original
instance inspection is now available; its derived overlap/assembly and cross-topic
integration remain open.

## Original structure-local ligand instances

The frozen membership predicates in `card_ligand_instances_v1.py` select exact
typed relationship, ligand-list and instance-list locations. Equal component or
instance names do not merge rows. The containing structure relationship supplies
support, with explicit qualifier-conflict wording; no per-contact source lineage
is fabricated. Selection cells `structure_ref`, `component_id` and `instance_id`
read only those literal parents. Full instance values remain unchanged and
independently inspectable. Saved verification uses the frozen predicates, original
locations and list ordinals, without live Card reconstruction or scientific readers.
Existing saved capsules retain their original membership and bytes.

Bounded previews show recorded chains, bound/investigation flags and at most three
contacts, retaining `position`, `seq_id`, UniProt reference and distance units.
Missing/null declarations, retained empty lists and malformed declarations have
distinct scoped gaps. A malformed ligand declaration previously raised during
entity-glossary construction and prevented Card capture; glossary construction
now skips that invalid entity candidate while preserving the original declaration.
The view never substitutes missing metadata with an absence conclusion.

Inspection of the preceding `mappings/rcsb_structures.py::_ligand_contacts` established that
UniProt positions are mapped from entity alignments and distances are selected
minima among source neighbour rows. The public frozen Card's structure relationship
has original UniProt/RCSB assertions but no named derivation binding for these
contact operations. New wording therefore says **recorded minimum distance** and
does not certify its historical alignment/minimum-selection basis. Like the
AlphaFold context gap below, completing derived contact/region navigation must
retain actual rule/input bindings for new mappings, while keeping historical
missing scope explicit. Current Card fields cannot repair old provenance. The
[subsequent correction](card_contact_mapping_integrity.md) now retains actual
original contact/alignment inputs and scoped `rcsb_ligand_contacts@1` for new RCSB
mappings, without relabeling historical records as newly qualified mappings.

Sequence molecular weight uses the existing PyUnitWizard Card codec and declared
field/unit expectation. Source scores remain original source metrics with their
own context. Zero, false, null, missing metadata, conflicting qualifiers and
unqueried/partial source coverage are not interchangeable. The separate coverage
view continues to report the original knowledge-state scope.

Inspection of `mappings/alphafold.py` establishes that `sequence_matches` is
computed by checksum comparison, and `isoform` is mapping context; they are not
direct fields of the original AlphaFold record. The mapper currently retains no
named derivation/input binding for those qualifiers. The new pane labels them
**Recorded sequence-match flag** and **Recorded isoform context**, explicitly
withholding direct source attribution and derivation certification. Original
qualifier values and original AlphaFold assertions remain unchanged. Versioning
and retaining that comparison's actual original inputs is an open #148 model
integration requirement, not a claim that current Card fields recover historical
mapping provenance. The earlier display wording was corrected before publication.

## Shared access and original saved reading

These views use the existing captured human objects and literal result storage.
`items()`, exact labels, full `cells`, `open()`, `explain()`, `related()` and `back()`
retain original payload/support and the selected context. Source connections,
scientific classification and a new Card capture are not needed for navigation.
`explorer.access.read(item.payload_location)` reaches the exact same retained
node through bounded machine pages; specialized machine `select()` still covers
structures only and is not silently extended by a new human route.

The original-instance continuation adds 19 exploration cases and three glossary
regressions. Its final **662 selected offline cases pass in 123.19 seconds**, using
twelve pytest-receptor workers with fatal runtime/SQLite/unraisable guards. The 36
public guide blocks execute offline; the expanded three-Card producer reopens in
an independent process with fixture access and live reconstruction/readers forbidden.
Three actual API panels (two public and one explicit synthetic false/empty case)
have technical visual review. Style, fixture-delivery, dependency/governance,
Markdown/snippet/Python-3.11 syntax and warning-fatal Sphinx checks pass. Original
public inputs and historical capsules remain unchanged. Exact source/environment
receipts belong to #148; this selected receipt does not qualify a full suite,
remote CI, installed artifacts or researcher acceptance. Useful local logs,
original bundles and visual evidence are retained under
`recovered_work/card_ligand_instances_20261023/`, owner #148, review at the next
exploration checkpoint or release; owned disposable build/test/browser paths are
removed after their last use.

Saving retains exact original fields/relationships, quantity bindings, membership,
gaps, labels, question and navigation closure. New source-panel membership uses
the explicit `card_protein_source_v1` predicates for historical binding; ordinary
source profile catalog changes cannot substitute a different membership during
reading. Current scientific readers are not invoked by the saved reader. Missing
unretained variants stay `not_saved`, and `start_new()` remains an explicit new
local interpretation.

No Card schema, source assertion, scientific rule, quantity codec or persistence
format identifier changes. Existing ArgDigest/SMonitor and optional-dependency
boundaries remain in place; no new public arguments or dependencies are added.
Twenty-three new regression cases cover public values/units, annotations/axes,
original model metrics, foreign/missing identity, different natures, literal dotted
keys, independent inert reading, exact saved requests, incomplete-membership
refusal, escaped complete text, bounded traversal and zero/false/isoform context.
Twenty-two cases passed in 6.56 seconds before the final recorded-context wording
correction and its additional regression. All **6,869 local-original offline cases
passed in 661.69 seconds** at that preceding source, with twelve receptor workers,
fatal SQLite/unraisable guards and thirteen expected fixture warnings. Its exact
full-source fingerprints remain original; the final label-only correction is
qualified by the affected selected cases, not a silently transferred full receipt.
An earlier interrupted full run is not qualification evidence.
All **682 selected cases pass in 77.69 seconds** on the final recorded-context
wording and its 23-case regression set, with twelve receptor workers and fatal
runtime/SQLite/unraisable guards. The final display correction changes no stored
qualifier, source record, value, quantity, selection or scientific calculation.
All 35 guide blocks execute offline; the expanded three-Card
example independently reopens its original source panels without fixture reads
or live scientific/Card reconstruction. Applicable static/documentation gates
and warning-fatal Sphinx checks pass.
Final broader qualification and exact source/environment receipts are recorded
in #148; technical passing counts do not establish scientist usability.

## Remaining broad-design work

Complete derived model/sequence context, annotation-to-structure/region navigation,
site/contact/instance/assembly integration and original overlap explanations,
then activity/clinical/literature and comparison/association routes. Bring compact
scientific adapter parity and all new saved science to the full design, and test
the combined experience with researchers and useful-scale workloads before
0.15.0. Keep the [deferred-CI recovery](deferred_ci.md) and release pause in force.
