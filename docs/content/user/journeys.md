# Reproducible scientific journeys

Start with a scientific question: what do sources state about two proteins, where
do they disagree, and which structures and ligands are represented? Sabueso can
resolve the entities, expose their source-supported knowledge and retain the exact
states you used. This workflow can be used directly from Python.

## Resolve and inspect

```python
import sabueso

tctim, tc_resolution = sabueso.resolve("P52270", structures=["1TCD"], chembl={})
hstim, hs_resolution = sabueso.resolve("P60174", structures=["1HTI"], chembl={})

print(tc_resolution.status, hs_resolution.status)
print(tctim.knowledge_state())
print(hstim.quality.get("conflicts", []))
```

These identifiers are public test systems, TcTIM and HsTIM. Online calls can fail
or return only part of the requested data. Check resolution and source outcomes
before using a card; an unavailable source does not establish biological absence.
For name/organism queries and alternatives, see {doc}`resolving`.

```python
comparison = tctim.compare_knowledge(hstim)
tc_ligands = sabueso.ligand_deck(tctim)
hs_ligands = sabueso.ligand_deck(hstim)
shared = tctim.compare_ligands(tc_ligands, hstim, hs_ligands)
```

Each derived result names its rule. Without an explicit residue map, positional
features remain `not_compared`: identical numbers in two proteins are not aligned
positions. Shared molecular identity and activity classes do not by themselves
establish selectivity or make different assays equivalent. See {doc}`bioactivities`
and {doc}`decks` for the comparison scope.

## Save the exact knowledge and its original execution

```python
store = sabueso.KnowledgeStore("knowledge.db")
tc_ref = store.save(tctim)
hs_ref = store.save(hstim)
tc_deck_ref = store.save_deck(tc_ligands, "tc-ligands")
hs_deck_ref = store.save_deck(hs_ligands, "hs-ligands")

packet = sabueso.compose_packet(
    sabueso.KnowledgeQuery(
        "P52270",
        comparator="P60174",
        aspects=["identity", "structures", "bioactivities"],
        detail="index",
    ),
    tctim,
    hstim,
)
packet_ref = store.save_packet(packet, "comparison")
```

Keep the original card/deck acquisition traces and packet attribution as separate
JSON files. Use an enclosing Ackredit session/capture to retain workflow attribution
and export citations. Saving scientific payloads alone cannot preserve an earlier
execution. The executable example below performs these steps, binds their outputs
and verifies original references. See {doc}`attribution` for the SDK pattern.

In a later process, `store.load(tc_ref)` and `store.load_packet(packet_ref)` read
the original state. A packet's `cite` and `item` methods locate exact historical
support; a missing pin fails rather than selecting the newest card. Reading saved
knowledge adds no acquisition or attribution credit. Preserve original derived
reports too, so later readers need not recreate them with newer rules.

## Run the complete offline journey

In a development checkout, with Sabueso installed and the repository's public
fixtures available, run from the repository root:

```bash
python examples/user_journeys/protein_comparison.py produce --output /tmp/sabueso-comparison --fixtures temp_data
python examples/user_journeys/protein_comparison.py read --output /tmp/sabueso-comparison
python examples/user_journeys/protein_comparison.py reacquire --output /tmp/sabueso-comparison --fixtures temp_data
python examples/user_journeys/protein_comparison.py read --output /tmp/sabueso-comparison
```

Start with an empty output directory. Each command uses a separate process; the
reader needs no fixture files. The producer resolves by name/organism, reads
ChEMBL/BindingDB measurements, builds ligand decks, preserves units and alternatives,
and saves both full and index packets. The reader validates original files and
support before exporting CSL-JSON and BibTeX references.

Development example format `@2` also retains canonical active-site residues stated
by each source and the composition of that selected set. The caller's selection
is named `source_active_site_selection@1`; composition uses
`residue_set_composition@1`. Each protein keeps its own sequence axis and exact
historical SourceAssertions. Equal residue numbers or compositions do not establish
a correspondence. These derived views currently lack dedicated execution sidecars;
their rules and source support do not imply complete operation observation.

The reader accepts original `@1` bundles without adding or recomputing residue
context. In either format it checks original inputs and retains the producer's
report, rather than rerunning derived rules. See {doc}`source_annotations`.

Reacquisition reads the same fixtures at a later observation time. It advances
current heads without changing earlier citations, reports or bibliography. No
network access occurs. The missing 1IIG RCSB fixture is unavailable; the example
does not claim that RCSB lacks 1IIG. Its structure/activity subsets are explicit,
and output counts are not a census of everything known about these proteins.

The new example is part of the development checkout. Its original runtime records
travel beside `knowledge.db`; retain the complete output directory. Hash checks
detect inconsistency, not authenticity or reuse permission. Inspect {doc}`terms`
and {doc}`source_coverage` before reusing or redistributing knowledge.

## Sequence and tissue comparisons

The development example `examples/user_journeys/comparative_support.py` compares
the stated P52270/Q4DV43 sequences and inspects P60174 variant/isoform tissue
usage. It saves ordinary results, explanations, exact card pins and original
execution records:

```bash
python examples/user_journeys/comparative_support.py produce --output /tmp/sabueso-comparative-support --fixtures temp_data
python examples/user_journeys/comparative_support.py read --output /tmp/sabueso-comparative-support
python examples/user_journeys/comparative_support.py reacquire --output /tmp/sabueso-comparative-support --fixtures temp_data
python examples/user_journeys/comparative_support.py read --output /tmp/sabueso-comparative-support
```

Start with an empty output directory and retain the complete bundle, including
`knowledge.db`. Each stage's report contains three views and their explanations;
runtime JSON separately retains observed source access, the three comparative
executions and enclosing workflow attribution. Original producers, result digests,
rules, parameters and input assertions remain bound to the saved results.
Reacquisition advances card heads and records new executions while preserving
the original files and citations.

The reader needs no fixtures. It verifies original hashes, pins, source support,
result/execution bindings and workflow credit before exporting CSL-JSON and BibTeX.
It runs no comparison, source query or fresh credit registration. Scientific gaps
and incomplete bibliography stay separate; the public isoform fixture's unstated
tissue-specificity field remains partial support. Resource descriptions do not
supply missing method or entry publications.

Example `@3` also reads original `@1`/`@2` explanations without inventing their
missing execution history. Explicit `--legacy` or `--unobserved` production
reproduces those formats; reacquisition preserves the original generation.
These public offline development examples are outside published 0.14.0 and do
not qualify live providers, an installed artifact or private consumer acceptance.
Equal sequence positions establish neither identity nor alignment; tissue usage
alone does not establish selectivity or efficacy.

## From diseases to targets and drugs

The development example `examples/user_journeys/disease_entities.py` asks two
separate questions: which targets sources associate with triosephosphate isomerase
deficiency, and which drugs ChEMBL associates with Chagas disease. It resolves
Orphanet/MeSH identifiers through MONDO's stated equivalences. Related identifiers
without a stated equivalence remain unresolved; shared names do not establish identity.

```bash
python examples/user_journeys/disease_entities.py produce --output /tmp/sabueso-disease-entities --fixtures temp_data
python examples/user_journeys/disease_entities.py read --output /tmp/sabueso-disease-entities
python examples/user_journeys/disease_entities.py reacquire --output /tmp/sabueso-disease-entities --fixtures temp_data
python examples/user_journeys/disease_entities.py read --output /tmp/sabueso-disease-entities
```

The producer saves disease cards, target/drug decks and an enriched HsTIM context.
It retains original membership bases, scores, phases, exclusions, limits, grouped
and ungrouped disease statements, exact card support and terms. In the fixture
target query, 20 rows of a source-declared 252, three attempted candidates and one
built card are different counts. Missing UniProt fixtures do not establish absence
from UniProt. Drug indications and target associations do not establish clinical
efficacy. Cited studies remain unqueried. See {doc}`disease_association`.

Keep the complete output directory. The independent reader needs no fixtures,
checks historical card items and original deck bases, and exports the original
available bibliography without acquiring sources or deriving the report again.
Reacquisition advances stored heads while the original references remain readable.

Development disease rules `@2` now pin each membership's original native statements,
MONDO input and member identity, including unbuilt/capped candidates. Saving a deck
alone preserves those scientific snapshots; JSONL/SQLite exports carry them too.
The example `@5` reader also accepts original `@1`, `@2`, `@3` and `@4` bundles with their
original support and observation gaps; it does not reconstruct missing work later.

Development MONDO term/equivalence queries now retain original index/release
observations and resource citations. Open Targets/Orphanet association queries and
disease-deck builds also retain original page/file/version/time receipts and exact
input/support/result pins. DISEASES, ClinVar and MedGen now retain their own
source-query observations and resource citations. Available credit
does not establish a complete disease-workflow bibliography. Non-protein packets
are not yet supported. These are development examples and bounded SDK checks,
not complete disease traceability or shared MOLI recording guarantees. The new
deck terms report includes embedded support sources. Development `Deck.admissible`
now supports conservative whole-context admission: shared unknown/restricted terms
refuse the operation, and individual non-admissible members are excluded with their
historical support references. This example still preserves its original `@5`
reports; admission is covered separately by the SDK acceptance tests.
