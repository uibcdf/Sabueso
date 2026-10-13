# Disease association

A human protein card can hold what DISEASES, Open Targets and Orphanet state about the
diseases its gene is associated with. Each source, and each DISEASES channel, is kept
apart.

```{note}
Disease associations are available since release 0.6.0.
```

```python
import sabueso

card, _ = sabueso.resolve("P60174", diseases={})  # human triosephosphate isomerase
for rel in card.relationships("associated_with"):
    q = rel["qualifiers"]
    print(rel["object_ref"], q["disease_name"], q["channel"], q.get("source_database"))
```

## Channels

- `knowledge` (default): associations curated by other resources (MedlinePlus, UniProt
  keywords…), with the resource and DISEASES's confidence.
- `experiments` (default): associations from experimental resources (for example GWAS
  through TIGA), with their own score.
- `textmining` (only when asked, `diseases={"channels": ["knowledge", "textmining"]}`):
  co-mentions in the literature, with a z-score. Text mining links **names**, not
  molecules. The human triosephosphate isomerase is co-mentioned with giardiasis,
  because the parasite's enzyme has the same name.

The same disease in two channels is two relationships, never merged. Scores are
DISEASES's own, as it states them; Sabueso does not rank them.

## How an association reaches the card

DISEASES names genes by Ensembl protein. An association is added only for an Ensembl
protein that the UniProt entry cross-references: `via_protein`, and `uniprot_isoform`
when UniProt maps it to an isoform. It is never matched by gene name.

## Open Targets

`sabueso.resolve("P60174", open_targets={})` adds every association Open Targets states
for the gene, up to a safety ceiling of 5000 (`{"limit": n}` asks for fewer), in Open
Targets' own order. A cut is recorded and reported with a warning. Each association keeps:
- the overall `score`, `datatype_scores` (genetic association, literature, known
  drug…) and `rank`. They are Open Targets' own computation, recorded as stated with
  the data version, never recomputed;
- the disease under Open Targets' term (`mondo:MONDO:0014221`). The same disease under
  a DISEASES term (`doid:DOID:0050884`) stays a separate reference.

The association reaches the card through the Ensembl gene the UniProt entry
cross-references (`via_gene`). It is added only when Open Targets also lists the entry
among that gene's products.

## Orphanet (rare disorders)

`sabueso.resolve("P60174", orphadata=True)` adds the rare disorders Orphanet associates
with the gene (`orphanet:ORPHA:868`). Each one comes with Orphanet's wording:
- the association type (for example "Disease-causing germline mutation(s) in") and its
  status ("Assessed");
- the disorder's type and group;
- the publications that validate it.

Orphanet states the gene's UniProt accession itself, so the link is its own. The file
(about 22 MB) is downloaded once per process, and its date is the version.

## ClinVar (variants)

`sabueso.resolve("P60174", clinvar={})` adds ClinVar's variants of the gene
(`annotations.clinical_variants`), found by the NCBI Gene id the UniProt entry
cross-references. By default every record of the gene, up to 5000 (`{"limit": n}` asks for fewer); a cut is reported.
Each variant keeps what ClinVar states:
- the HGVS title, variant type and consequences;
- the germline classification and its review status. "Conflicting classifications of
  pathogenicity" is ClinVar's own statement, never resolved;
- the conditions, with their cross-references.

**Numbering.** ClinVar lists a protein change in every isoform's numbering ("E142D,
E105D, E23D"). A variant is placed in UniProt numbering (`location`, `numbering:
"uniprot"`) only when two things hold: its transcript is one UniProt states for the
canonical isoform, and the residue ClinVar names is the UniProt residue at that
position. A change on another isoform's transcript is placed through that isoform's
edits as UniProt states them (`placed_via`, rule `uniprot_isoform_map@1`). For example,
position 142 of isoform P60174-3 is canonical 105. A change inside an isoform's own
segment has no canonical position.

Otherwise `not_placed` says why:
- `no_protein_change`;
- `unparsed_protein_change`;
- `transcript_not_canonical`;
- `isoform_specific_position`;
- `stop_codon`;
- `residue_mismatch`.

Nothing is placed by aligning sequences.

ClinVar is not for diagnostic use without review by a genetics professional.

## gnomAD (population frequencies)

`sabueso.resolve("P60174", gnomad={})` adds gnomAD's variants of the gene with a protein
change, each with its allele count, allele number and frequency in exomes and genomes
(`annotations.population_variants`). gnomAD is asked for the gene and for the Ensembl
transcripts UniProt states for the canonical isoform. When gnomAD states a protein
change on the canonical transcript, that is the one kept, in UniProt numbering (the
residue must match). A variant gnomAD states changes no residue of the canonical
transcript (it is in an intron or a UTR there) keeps its consequence on the other
transcript, with `canonical_consequence`, and is not placed
(`not_coding_on_canonical`). Otherwise the same rule as ClinVar applies. Variants
without a protein change are left out, and the enrichment record counts them.

### In which tissues a variant matters

`exon_usage=True` adds gnomAD's pext of the gene (`annotations.exon_usage_by_tissue`).
For each coding region, it gives the share of the gene's expression in each GTEx v10
tissue that includes the region. With the variants on the card,
`card.variant_tissue_usage()` places each variant's genomic position in its region,
under the published rule `pext_at_variant@1`, and lists the tissues at or above a threshold
(0.1 by default).

For TPI1, the variants in isoform 3's own N-terminal segment lie in a region expressed
in testis only (0.38; below 0.01 on average), while E105D lies in a region every
tissue expresses.

### In which tissues an isoform is made

`card.isoform_tissue_usage()` answers per isoform. For each one it gives:

- what UniProt states about its tissues, when a tissue-specificity statement is
  restricted to that isoform;
- where its own coding bases are expressed, from gnomAD's pext. Its own bases are those
  in no other isoform's transcript, and the transcripts and their exons are the ones
  UniProt and gnomAD state.

For PKM, UniProt states M2 is "specifically expressed in proliferating cells" and M1 is
"expressed in adult tissues". The pext of their own exons agrees: M2's is expressed in
all 49 GTEx tissues, and M1's in 23, up to 0.58 in skeletal muscle.

Isoforms built by combining exons, such as tau's, rarely own any base. For them,
`variable_regions` lists each run of coding bases that not every isoform includes,
with the isoforms that include it and its pext.

An isoform whose exons are not known says why:

- `no_transcript_stated`: UniProt states no Ensembl transcript for it. Sabueso does
  not align sequences, so its genomic structure stays unknown. This is the common
  case, 12 of CD44's 19 isoforms. Ensembl (release 116) maps none of the four such
  isoforms checked to a transcript either (of CD44, PKM, CACNA1C and APP).
- `transcript_not_in_gnomad`: UniProt states a transcript newer than gnomAD's
  release (APP's isoforms 3 and 7).

Own bases are counted against the isoforms whose exons are known. When some are not,
a base counted as one isoform's own may be shared with one of them, so
`own_bases_complete` and `variable_regions_complete` are false. PKM's isoform 3 has no
known exons, so M1's and M2's own exons carry that caveat.

### Tissues as ontology terms

`gtex=True`, with `exon_usage=True`, adds the term GTEx states for each tissue the pext
names: UBERON for a tissue, or EFO for a cell line (`annotations.tissue_terms`). Both
views then list `tissue_terms`, joined by GTEx's tissue id (`gtex_tissue_key@1`):

```python
card, _ = sabueso.resolve("P14618", exon_usage=True, gtex=True)
view = card.isoform_tissue_usage()
view["tissue_terms"]["terms"]["muscle_skeletal"]
# {'gtex_id': 'Muscle_Skeletal', 'name': 'Muscle - Skeletal', 'ontology_id': 'UBERON:0011907'}
```

A term never replaces a tissue. GTEx gives the cerebellum and the cerebellar
hemisphere the same term, UBERON:0002037, and they stay two tissues.

### Genomic scope and tissue coverage (development)

Development views default to `pext_at_variant@2` and `isoform_exon_usage@3`.
They require matching explicit chromosome and assembly, and compatible stated
transcript links before comparing isoform coding bases. A variant's assembly
comes from its explicit input or selected assertion coordinate context. Current
gnomAD acquisitions retain the requested GRCh38 reference; old dataset labels
alone cannot supply missing context. Migration reports the gap; rebuilding can
obtain it. No sequence alignment or genome liftover occurs.

Overlapping pext records contribute a base once only when every record states the
same value for that tissue. Disagreements and missing values stay separate.
`coverage_by_tissue` reports `bases_with_value`, `bases_missing_value`,
`bases_conflicting_value` and `complete`; `by_tissue` is the mean over that tissue's
resolved bases, or `None` when none are resolved. Read a mean with its coverage:
unknown bases never count as zero expression. The top tissue and threshold list
use only resolved means; they do not establish pathogenicity or total expression.

Explicit `usage_rule="pext_at_variant@1"` or `"isoform_exon_usage@2"` on views
and explanations reproduces the published historical behavior. Saved reports keep
the rules and original support with which they were produced.

### Inspecting original comparative support (development)

```python
variant_support = card.explain_variant_tissue_usage(threshold=0.1)
isoform_support = card.explain_isoform_tissue_usage(threshold=0.1)
sequence_support = card.explain_sequence_differences(other_card)
```

These explanations retain the existing `view`, exact card pins, original selected
fields and assertions, alternatives, input locators, parameters and scope gaps.
Variant explanations show coordinate scope and every overlapping region;
isoform explanations show CDS inputs, partitioned intersections and tissue-specificity
inclusion/exclusion. Tissue joins retain the actual GTEx term statements. A source
version label does not independently verify a native release, and stored scientific
support does not reconstruct execution credit or bibliography.

The original rules retain their historical limitations: variant joins do not
check assembly; isoform subtraction/intersection does not check chromosome or
assembly and counts overlapping pext regions separately. Explicit historical
usage rules retain those limits and their original explanations. New rule versions
correct scoped joins and per-tissue coverage under
[#138](https://github.com/uibcdf/sabueso/issues/138). A low pext value
does not establish harmlessness, and equal sequence positions establish neither
residue correspondence nor identity. Cutoffs are dimensionless numbers in [0, 1].

Save the original explanation alongside its pinned cards when a later reader must
retain the producer's original rules and version. The public development example
`examples/user_journeys/comparative_support.py` demonstrates independent inert
reading and later fixture reacquisition. This API slice is outside published 0.14.0.

The values come from isoform quantifications of adult tissues, so a low value is not
proof that a change is harmless. By default every variant, up to 5000 (`{"limit": n}` asks for fewer); a cut is reported.

## Coverage

DISEASES, Open Targets, Orphanet and ClinVar cover human genes only. For a protein of another organism,
the knowledge state says `not_queried`, with that reason, never `not_stated`.

The files are downloaded once per process, about 50 MB with text mining. Set
`$SABUESO_CACHE_DIR` to keep them between sessions. The version recorded is each file's
publication date.

## Disease cards (MONDO)

A disease is also an entity of its own, anchored at a MONDO term. MONDO integrates the
terminologies the sources above use (DOID, Orphanet, OMIM, MeSH, EFO, NCIT…) and states,
term by term, which of their ids are the same disease.

```{note}
Disease cards are on main, not yet in a release (card schema 0.3.7).
```

```python
import sabueso

# The same disease, named by DISEASES (DOID), Orphanet and MONDO
for query in ("doid:DOID:0050884", "ORPHA:868", "mondo:MONDO:0014221"):
    card, resolution = sabueso.resolve(query)
    print(card.id, resolution.decision.get("identity"))

card.get("names.canonical_name")  # triosephosphate isomerase deficiency
card.get("identifiers.equivalent_ids")  # the ids MONDO states are this disease
card.relationships("subclass_of")  # its parent terms in MONDO
```

- **Identity only through stated equivalence** (`mondo_equivalence@1`). An id of another
  terminology resolves only when MONDO states that it is the same disease. The
  resolution records that statement and the MONDO release.
- **Related is not the same.** MONDO's other cross-references are related terms. They
  are kept in `identifiers.related_ids`, and never used to join.
- **Obsolete terms** are not followed. The resolution (`obsolete`) names the replacement
  MONDO states as a candidate.
- `omim:` and `mesh:` also number genes and chemicals. Those have no MONDO equivalence
  and are reported as not found, never as a disease.
- MONDO's release file (about 53 MB) is downloaded once per process and checked against
  its published SHA-256.

## A protein's diseases, grouped (MONDO)

The same disease reaches a protein card under several ids: DISEASES writes
`doid:DOID:0050884`, Orphanet `orphanet:ORPHA:868`, UniProt the MIM number `615512`,
ClinVar a list of ids per condition. `disease_identity=True` asks MONDO which of them
it states are the same disease, and `Card.diseases()` groups them:

```python
card, _ = sabueso.resolve(
    "P60174",
    diseases={},
    open_targets={},
    orphadata=True,
    clinvar={},
    medgen=True,
    disease_identity=True,
)
view = card.diseases()
for disease in view["diseases"]:
    print(disease["mondo"], disease.get("mondo_name"), disease["sources"])
for item in view["ungrouped"]:
    print(item["refs"], item["source"], item["reason"])
print(view["rule"]["rule"])  # development: disease_grouping@3; published 0.14.0: @2
```

- Each id MONDO states is the same disease becomes a `same_as` relationship to its
  MONDO term (`basis: mondo_equivalence@1`), backed by a MONDO SourceAssertion.
- Statements are grouped only through those, or when they name the same id. For human
  triosephosphate isomerase, triosephosphate isomerase deficiency is one disease stated
  by ClinVar, DISEASES, Open Targets, Orphanet and UniProt.
- A ClinVar condition is one statement with every id ClinVar states for it. The
  0.13.0 `@2` rule retains every direct and MedGen/MONDO path in `identity_paths`.
  A conflicting target of one identifier prevents grouping, even if MONDO places
  the candidate terms in a hierarchy. Names and newer source versions never choose.
- `medgen=True` asks MedGen which record each MedGen concept id is (`C1860808` is
  record 349893). MONDO states its equivalences by those records, so a condition named
  only by a MedGen concept id reaches MONDO through two statements, MedGen's and
  MONDO's (`medgen_concept@1`).
- What reaches no MONDO term stays apart, with its reason. It is never grouped by
  name:
  - `condition_not_provided`: ClinVar's "not provided" and "not specified", which are
    not diseases;
  - `no_stated_equivalence`: for example some EFO terms, or phenotypic traits;
  - `no_id_stated`: a condition named only by text;
  - `namespace_not_mapped`: for example HP phenotype terms;
  - `conflicting_identity`: one identifier has contradictory MONDO targets, or
    separately stated identifiers reach terms without a unique supported broader
    term. All candidates and paths are retained, and none is chosen;
  - `incomplete_identity` (0.13.0 `@2`): a candidate reaches MONDO but another
    stored identity branch is unfinished. Retain both instead of claiming agreement.
- A condition named at two granularities joins the broader disease. ClinVar sometimes
  gives a broader Orphanet id next to the MONDO and OMIM ids of a subtype, or names
  "Obesity" with the Orphanet id of obesity due to MC4R deficiency. When MONDO places
  one term under the other, the statement joins the broader term, because what holds
  for a subtype holds for the disease it belongs to. The narrower term is kept in the
  statement (`narrower`), with MONDO's chain of terms (`mondo_hierarchy@1`).
- `disease_identity` reads the diseases the other sources put on the card, so ask for
  them in the same call.

## Explain a disease group (since 0.13.0)

```python
explanation = card.explain_disease("mondo:MONDO:0014221")
print(explanation["status"], explanation["card_ref"])
for row in explanation["statements"]:
    print(row["statement"]["source"], row["input"]["source_assertions"])
```

Development `disease_group_explanation@3` reads the `disease_grouping@3` view at one
exact card snapshot. `disease_identity_coverage@1` distinguishes exact completed
identifier diagnostics, unasked/unavailable steps, unrecorded scope and mixed
outcomes; a source-wide count is not identifier coverage. `coverage_context` retains
original enrichment indexes at that pin. Explicit grouping rules `@1`/`@2` keep
their historical explanations; published 0.14.0 defaults to `@2`. Associations keep
their relationship and SourceAssertions;
UniProt/ClinVar members are matched to the selected stored annotation values.
MedGen/MONDO identity links and each stored hierarchy step have pinned item
references readable through the knowledge store. Source versions, acquisition
metadata, qualifier conflicts and field-selection alternatives remain visible.
Field context describes the stored selected fields, not reconstructed historical
mapping inputs or a newly resolved disease.

Only MONDO group selectors are accepted, including `MONDO:0014221`; names and
other ontology aliases are refused. A missing group is `not_on_card`, never evidence
that the protein has no disease. `ungrouped_context` retains the **whole card's**
ungrouped statements and their reasons; it does not associate all of them with the
requested term. Missing stored support produces `partial` with explicit gaps.

Published 0.12.0 uses `disease_grouping@1`. To reproduce that historical lookup since
0.13.0, select it explicitly in both views:

```python
historical_view = card.diseases(grouping_rule="disease_grouping@1")
historical_explanation = card.explain_disease(
    "MONDO:0014221", grouping_rule="disease_grouping@1"
)
```

The historical lookup may choose the last stored target of one identifier;
`disease_group_explanation@1` exposes its selected/alternative links as partial.
Default `@2` removes this storage-order dependence
([#115](https://github.com/uibcdf/sabueso/issues/115)), retaining every candidate
path and its pinned support. Compatible converging paths can group; contradictory
targets remain ungrouped. A unique MONDO label is `mondo_name`; all stored labels
remain in `mondo_names`. Multiple hierarchy paths stay in `narrower[term]["paths"]`
instead of selecting one; a unique path retains the existing `"path"` field.

Load an original pinned card from `KnowledgeStore` to explain a historical state.
The operation does not fetch, mutate the card, rebuild mappings or add execution
credit. Its records are detached from the card; scientific serialization is unchanged.

## From a disease to its targets and its drugs

```python
import sabueso

targets = sabueso.disease_targets("ORPHA:868")  # a deck of protein cards
for card in targets.cards:
    print(card.id, targets.basis(card.id)["statements"])
print(targets.meta["excluded"])  # what was left out, and why

drugs = sabueso.disease_drugs("mondo:MONDO:0001444")  # Chagas disease
for card in drugs.cards:
    print(
        card.id, [i["max_phase_for_ind"] for i in drugs.basis(card.id)["indications"]]
    )
```

- **Targets** (`disease_targets@1`) come from Open Targets' associated targets (asked by
  the MONDO id, then its EFO equivalents) and Orphanet's genes of the disorder (asked by
  its Orphanet equivalents). Each member is the Swiss-Prot product a source states for
  the gene. Its basis lists every statement that brought it, with Open Targets' score
  and rank, or Orphanet's association type and status, as stated.
- **Drugs** (`disease_drugs@1`) are the molecules whose ChEMBL drug indications name the
  disease by its MONDO id or by the EFO and MeSH ids MONDO states are the same disease.
  They are ordered by ChEMBL's `max_phase_for_ind`, highest first.
- Nothing is matched by name, and a disease that does not resolve is refused.
- **Each member is a whole card**, which costs at least one request. So these decks
  build 50 members by default (`limit=`). The rest are listed in `meta["excluded"]` with
  the reason `limit`, and the cut is reported with a warning. A gene with no Swiss-Prot
  product is excluded with its reason.

In development after 0.13.0, `disease_targets@2` and `disease_drugs@2` preserve native
membership assertions, exact original MONDO identity and member-card identity.
`deck.explain(card.id)["support"]` shows the original source items and their pins,
or explicit missing/misbound support. Open Targets' returned record preserves row
order/counts; its score is source-stated and the position is derived from that
returned order. Excluded and unbuilt candidates keep their supporting rows too.

`store.save_deck(deck, "targets")` atomically saves members and the embedded
scientific support. The original disease input remains unchanged; a separate
assertion-bearing revision may advance the stored disease head. Later
`store.source_assertion(ref)` reads exact native support even after new acquisitions.
JSONL/SQLite deck exports preserve it for reimport into an empty store. Native
statements do not establish observed access or a complete bibliography; preserve
original runtime sidecars separately. The new deck terms report includes all
embedded sources. Development `Deck.admissible` requires all shared context to
permit the use, then filters whole members against all their stored statements
under `disease_deck_admission@1`. Unknown/restricted shared terms refuse; finer
filtering by terms of use remains pending. Published rules `@1` remain readable with their
original support gaps.
