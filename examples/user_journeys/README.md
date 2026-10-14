# Independent scientific user journeys

These examples exercise the approved roadmap after 0.13.0 (#112). They use public
Sabueso APIs, public test systems and frozen responses declared in
`temp_data/NOTICE.md`. These examples are development work in this
checkout; its local validation is separate from published-package qualification.

## Protein and comparator

### Structure, assay and located-literature dossier

```bash
python examples/user_journeys/scientific_dossier.py produce --output /tmp/sabueso-scientific-dossier --fixtures temp_data
python examples/user_journeys/scientific_dossier.py read --output /tmp/sabueso-scientific-dossier
python examples/user_journeys/scientific_dossier.py reacquire --output /tmp/sabueso-scientific-dossier --fixtures temp_data
python examples/user_journeys/scientific_dossier.py read --output /tmp/sabueso-scientific-dossier
```

Use an empty output directory. This example asks which stored TcTIM/HsTIM
structures and assay records meet explicit illustrative criteria, and which
located literature mentions are available. It creates readable per-stage
`dossier.md` files alongside complete JSON, exact pinned cards in `knowledge.db`,
original acquisition/credit sidecars and reader bibliography exports.

Structural criteria are resolution at most 3 angstrom, coverage at least 0.9,
source-reference sequence, an author-assigned homo dimer and observed coverage
of completely supported source active-site positions. Every criterion reports
met, not met or unknown. The example preserves author numbering, mutations,
fragments, alternate assemblies and disagreements. Source-reference does not
universally mean wild type. Equal positions across the proteins are not aligned.
Meeting these illustrative criteria is not project model selection.

Assay rows preserve the stated measurement and normalized quantity separately,
target assignment, full original qualifiers, conditions and exact support.
The example rule asks for direct assignment D, IC50, equality and a normalized
concentration; eligible records still require human comparability review.
ChEMBL and BindingDB requests are explicitly capped at 25 records per source.
Partial source coverage is retained, not presented as a complete potency survey.

The stored-context table exposes source activity/target and assay identifiers,
organism/taxon, confidence, stated target variant, original publication pointers
and measurement notes. `stored_assay_context_review@1` marks named fields missing
from the saved qualifiers; it does not claim absence from the source. Protocol
curation and experimental comparability remain unestablished. Missing mutation
annotations do not establish wild type, and matching assay IDs, text or units
does not establish equivalent protocols.

Europe PMC annotations are explicitly requested for MED:18562316 and
PMC:PMC12400196. A located P60174 figure occurrence includes the returned
fragment, location and supporting assertions. It establishes an accession
mention; it is not a curated mechanistic finding. An empty annotation response
does not prove absence from an article. Full-text curation, selectivity,
molecule prioritization and project Evidence remain outside this example.

The example-local format `sabueso.scientific_dossier_example@2` uses existing SDK
APIs; it introduces no card or shared MOLI schema. Original producer versions
and the example source hash are recorded. Reacquisition advances stored heads
while preserving original results, pins, rules and credit. Independent reading
requires no fixtures or network, checks original support and refuses inconsistent
units, values, references, scope or overstated interpretation. Its dossier
derivation is explicitly not runtime-observed. These technical checks do not
replace scientific review or qualify a published installation.

Historical `@1` dossiers remain readable in their original shape and rendering.
`produce --legacy` creates that format; reacquisition retains the original format.
The context review is added only to new `@2` reports.

### Comparative sequence and tissue support

Development pinned sequence/tissue support has a separate public example:

```bash
python examples/user_journeys/comparative_support.py produce --output /tmp/sabueso-comparative-support --fixtures temp_data
python examples/user_journeys/comparative_support.py read --output /tmp/sabueso-comparative-support
python examples/user_journeys/comparative_support.py reacquire --output /tmp/sabueso-comparative-support --fixtures temp_data
python examples/user_journeys/comparative_support.py read --output /tmp/sabueso-comparative-support
```

It retains P52270/Q4DV43 sequence and P60174 variant/isoform/term explanations at
exact pins. Original fields, assertions and genomic intersections remain
inspectable after later fixture reads. Readers require no fixtures and add no
source access, derivation or credit. New reports use format `@3`, preserving
coordinate scope and per-tissue coverage (#138), observed comparative operation
`@2` and original bibliography (#108). `produce --legacy` creates historical `@1`;
`produce --unobserved` creates `@2` without the original runtime sidecars.
Reacquisition retains the original format and rules; readers support all three. These
examples are outside published 0.14.0 and preserve the other journey formats.

From the repository root, with this checkout installed editable:

```bash
python examples/user_journeys/protein_comparison.py produce --output /tmp/sabueso-comparison --fixtures temp_data
python examples/user_journeys/protein_comparison.py read --output /tmp/sabueso-comparison
python examples/user_journeys/protein_comparison.py reacquire --output /tmp/sabueso-comparison --fixtures temp_data
python examples/user_journeys/protein_comparison.py read --output /tmp/sabueso-comparison
```

Use an empty output directory for `produce`. Each command starts a separate
process. The reader needs the output bundle and installed dependencies, but no
fixture directory; it refuses incomplete or inconsistent original records.
Network access is forbidden for every command.

The journey resolves triosephosphate isomerase by name and organism: TcTIM
(P52270, taxon 5693) and HsTIM (P60174, taxon 9606). It retains the resolution's
identity audit and alternatives, explicitly asks for two RCSB structures per
protein, collects ChEMBL/BindingDB activities and source-stated UniChem identity,
and builds molecular ligand decks from ChEMBL/CCD statements.

It compares fields, relationships and ligand knowledge, preserves measurement
types/units and named derivation rules, and saves supporting SourceAssertions at
exact card pins. Original reports also explain one activity, measurement group and
shared-ligand crossing per protein as representative supported results.
No residue map is supplied: equal residue numbers are not aligned
positions, so positional comparisons remain `not_compared`. A shared ligand does
not establish selectivity, binding at a particular site or equivalence of assays.

The output holds:

- `knowledge.db`: historical protein/molecule cards, ligand decks and full/index
  packets with both proteins;
- per-stage reports with original comparisons, resolution decisions, conflicts,
  alternatives, knowledge states, source coverage and redistribution terms;
- original acquisition traces, observed operations, per-packet attribution and
  enclosing Ackredit workflow attribution;
- manifests binding exact scientific references and original sidecar digests;
- reader reports and original CSL-JSON/BibTeX reference exports.

Views may contain PyUnitWizard quantities. The example serializes them as
`{value, unit}` in their own units; it never stringifies or discards a unit.
Reacquisition reads the same frozen responses at a later fixture-read time,
advancing current heads while preserving the original scientific results, pins,
versions and bibliography. It is not a fresh public download or a new database
release. The reader exports the original producer's report rather than rerunning
its derivations under a newer reader version.

## Molecules against a declared target

```bash
python examples/user_journeys/molecule_target.py produce --output /tmp/sabueso-molecule-target --fixtures temp_data
python examples/user_journeys/molecule_target.py read --output /tmp/sabueso-molecule-target
python examples/user_journeys/molecule_target.py reacquire --output /tmp/sabueso-molecule-target --fixtures temp_data
python examples/user_journeys/molecule_target.py read --output /tmp/sabueso-molecule-target
```

The target is explicitly TcTIM (P52270), with ChEMBL activities and the requested
RCSB structure 1SUX. The selected molecules are BTS (CHEMBL1161789) and benznidazole
(CHEMBL110). ChEMBL/CCD/UniChem statements anchor their identity; no name or
structure similarity establishes a join. The two-member deck records the supplied
identifiers as its selection basis. Unmatched activity records belong to other
molecules outside this selection, not failed molecular identities.

BTS has a reported IC50 of 33,000 nM and structural context in 1SUX. Benznidazole
has an 18% inhibition measurement at 400 micromolar and another record without a
determined value. Their assay descriptions, target assignment, publications,
source versions, original statements, grouping/classification rules and parameters
remain inspectable. `weak`, `inactive` and `not_determined` are rule outputs for
these measurements, not universal activity, binding-site or clinical conclusions.

ChEMBL also reports four benznidazole indication rows, a maximum clinical phase and
16 cited NCT ids. The EFO/MONDO/DOID disease references remain separate. Trials are
explicitly not fetched; BTS indications, other targets and BindingDB activities
are not queried. Missing benznidazole UniChem fixture data is observed as
unavailable, not proof of missing external identity. Linked PubChem/DrugBank ids
do not mean those sources were accessed. Complete clinical coverage remains pending.

The bundle stores all three cards, their exact relationship/statement support,
the selected deck and an index packet for the **target context**. This packet is
not molecule-filtered; the producer's separate report declares the narrower
question. Independent readers verify native molecular/deck pins, assay and identity
links, original operation/workflow attribution and historical packet support,
without fetching fixtures, rerunning scientific derivations or generating credit.
Historical `knowledge_state@4` can incorrectly report successful CCD/UniChem intake
as `not_stated`. `knowledge_state@5`, delivered in 0.14.0, corrects native record counts,
retains unknown counts/missing subsets and separates clinical intake
([#122](https://github.com/uibcdf/sabueso/issues/122)). Readers retain the original
report and its named rules; original statements and observed queries stay available.

The full original explanations deliberately retain broad classification context:
the current frozen example produces about 30 MB of report JSON per acquisition.
The reader loads each pinned card once and inspects its item stores, avoiding
repeated deserialization for thousands of contextual links. This measured example
does not establish an export-size or performance guarantee (#98/#88).

The script reuses file/quantity/network helpers in `protein_comparison.py`; keep
both scripts together when copying the example outside the repository.

## Coverage and limits

These are explicit source/fixture subsets, not all known structures or ligands.
The 1IIG RCSB fixture is deliberately unavailable; this is not an assertion that
RCSB has no such structure. A source can be partial, unqueried or unavailable even
when the application finishes successfully. Inspect the per-query acquisition
outcomes, source totals/caps and knowledge-state rows before interpreting a result.

Runtime observation is bounded by the installed Sabueso adapters. Original JSON
must travel beside the scientific store; payload-only reads cannot recreate an
earlier execution. Bibliography does not grant data-reuse rights. Terms reports
describe the packaged registry at production, not perpetual permission.

The manifest is local to this example. Hashes detect changed files and references;
they do not authenticate a source or implement MOLI ProjectRecord/Recorda storage.
An interrupted producer can leave an incomplete bundle, which the reader refuses.
No Nextia Evidence is created.

## Diseases and related entities

```bash
python examples/user_journeys/disease_entities.py produce --output /tmp/sabueso-disease-entities --fixtures temp_data
python examples/user_journeys/disease_entities.py read --output /tmp/sabueso-disease-entities
python examples/user_journeys/disease_entities.py reacquire --output /tmp/sabueso-disease-entities --fixtures temp_data
python examples/user_journeys/disease_entities.py read --output /tmp/sabueso-disease-entities
```

Copy all three scripts together for an independent installed-SDK check. The disease
script uses the other scripts' file/quantity/network and support-inspection helpers;
these remain example-local, without a shared serialization contract.

Two separate MONDO-anchored diseases exercise target and drug decks: Orphanet 868
(triosephosphate isomerase deficiency) and MeSH D014355 (Chagas disease). No link
between those two diseases is inferred. The example keeps exact MONDO/card support,
original Open Targets/Orphanet membership bases and ChEMBL indication rows,
unbuilt/capped candidates and original HsTIM disease-group explanations, including
ungrouped identity paths. Related EFO:0001360 remains unresolved. Trials, approvals,
efficacy and disease packets are outside the declared query scope.

The reader checks historical item support and original membership metadata rather
than recreating them under its own rules. Original available runtime attribution
and CSL-JSON/BibTeX survive reacquisition. Missing/misbound files, wrong members,
altered support/bases and overstated coverage fail before reference export.

Development rules `@2` now preserve exact membership SourceAssertion pins, original
MONDO input and member identity, including unbuilt/capped candidates (#91).
The example `@5` reader also accepts original `@1`, `@2`, `@3` and `@4` reports, keeping their
support and observation gaps rather than recreating old knowledge. Exported decks carry embedded support;
saving the deck alone into an empty store makes its scientific pins resolvable.
Deck terms include that content. Development `disease_deck_admission@1` requires
admissible whole embedded context and filters unchanged member cards by all stored
statements. Shared unknown/restricted terms refuse; finer filtering by terms of use remains pending
(#29). Separate SDK tests cover admission; this example keeps its `@5` format.

Development MONDO term/equivalence access now retains original index/release
observations and bibliography. Open Targets/Orphanet queries and disease-deck builds
also retain native page/file/version/time, source outcomes and original input/result
pins. DISEASES/ClinVar/MedGen source access is also observed (#108/#125).
Acceptance remains partial: underlying study bibliography is incomplete. Stored card data never
establishes new source credit.
Source totals, attempted candidates and built cards are distinct scopes; the example
reports each without interpreting a fixture gap as external absence. Keep all files
beside the store; hashes are consistency checks, not authenticity or permissions.
Native ChEMBL indication references now enter workflow attribution with original
row/page occurrence scope and explicit unfetched-target/missing-metadata gaps.
The example keeps `@5`: original reports and their declared gaps stay unchanged.
Complete underlying study bibliography and finer filtering by terms of use remain pending.
Broader molecular reverse queries and clinical observation remain separate work.
The #122 correction was delivered in 0.14.0; historical reports retain their original rules.

## Located primary source statements

```bash
python examples/user_journeys/literature_source_review.py produce --output /tmp/sabueso-located-source --fixtures temp_data
python examples/user_journeys/literature_source_review.py read --output /tmp/sabueso-located-source
```

This independent example records two actual structural source statements from
Kontellas et al. (2025), DOI 10.1107/S2053230X25006454, under
`sabueso.located_source_review_example@1`. It retains the unchanged CC BY 4.0
article XML, original fragments, locators and quotes. Source-stated P60174
membership in Figure 4 and UniProt's P60174–2JK2 relationship establish the
explicit subject binding; no sequence similarity or residue mapping is used.

Existing `Card.add_literature_claim` and `CurationStore` APIs preserve the
statements in curated and rebuilt cards, with their original SourceAssertions.
The curator is Codex (agent); scientist review remains pending and claims have
`not_compared` outcomes. This is explicit curation, not automatic literal-rule
extraction or a human-accepted result. Original claims/literature views are saved
by the producer. The independent reader checks their original native support,
curations and source locations without new source access, views, curation or
credit, and preserves original bibliography exports.

Article full text was supplied as a native public input; its download is not an
SDK-observed full-text acquisition. Only fixture entry/article-metadata access
is observed. Curation execution observation is explicitly absent. Reported use
of the human template and membership in a published alignment do not execute
modeling, establish inhibition/selectivity, transfer the studied parasite's
results to HsTIM, supply ChEMBL assay protocols or create Nextia Evidence.
Copy `literature_source_review.py` and `protein_comparison.py` together when
running outside the checkout. See the developer's
[located source review](../../devguide/pending_proposals/located_source_review.md)
for its qualification and remaining scope.
