# Literature and curation

What sources say about publications, and what a curator reads in them. A curated
statement is a SourceAssertion whose source is the paper: it is compared with the
databases, never given priority, and kept across rebuilds.

## Literal extraction from supplied text (since 0.13.0)

`sabueso.extract_literature_mentions(text, identifier, publication, locator)` runs
the fixed rule `literal_uniprot_mention@1`. Supply the exact text fragment, its
canonical UniProt accession, a `pubmed:` or `doi:` reference and its location in
that publication. It accepts explicit `UniProt:P60174`, `UniProtKB:P60174` or an
official UniProt entry URL. Names, bare accessions, isoform suffixes and longer tokens
do not match. Matching is case sensitive and does not establish sequence identity
or a biological finding.

The result has one detached `SourceAssertion` per occurrence, with the literal
text, zero-based Unicode offsets (exclusive end), locator and input SHA-256, plus
supported `mentioned_in` relationships. Acquisition is `rule_extraction`, with
the tool, version and configuration; no human validation is invented. An empty
result concerns the supplied fragment only.

Save the result's original `extraction_trace` alongside its statements. It credits
the executed software, identified publication and input fragment through Ackredit.
Saved portable readers render those original references without new credit.
Publication metadata and fragment terms remain unknown when not supplied; a
publication reference grants no reuse rights. Provider failures warn and preserve
the scientific extraction with explicit failed attribution.

This rule runs entirely on supplied text. Explicit intake and original-result
replay and explicit article bibliography/declared terms are available since
0.13.0; supplied-fragment rights, broader statements and validation remain #92. Intake uses published card schema
0.3.12; published 0.3.11 is fixed.

### Intake, persistence and reuse (since 0.13.0)

```python
extractions = sabueso.ExtractionStore("extractions.jsonl")
extractions.save(result)  # exact original support and runtime attribution
card, resolution = sabueso.resolve("uniprot:P60174", extractions=extractions)
# Alternatively, explicitly intake into an existing current-schema card:
event = card.add_literature_extraction(result)
refreshed, resolution = sabueso.refresh_card(card, extractions=extractions)
```

The card retains the original SourceAssertions and supported relationships,
including each occurrence's location, input hash and named extraction tool/version.
Alternative fragments keep their support and qualifier forms. Intake requires the
exact UniProt subject and rejects inconsistent support before mutation. Migrate an
older card explicitly with `sabueso.migrate_card(card.to_dict())` first. Extraction
is never exported or replayed as human curation through `CurationStore`.

`ExtractionStore.records()` and saved card/portable readers add no credit. Explicit
store application credits **reused references**, retaining original use contexts and
producer versions, and credits the current intake software separately. Repeated
intake does not change scientific payloads. The store holds original result JSON;
it neither fetches text nor reruns extraction. Original terms remain unknown;
intake cannot add unknown-rights fragments to a card built under a terms profile.

Save `card.literature_intake_traces` separately for the intake execution record,
or collect original extraction/intake events through `sabueso.attribution()` and
its `literature` accessor. The event's card pin identifies the state at intake;
later card mutations may create a different pin. Runtime records stay outside
scientific card payloads and hashes.

A refresh without an original extraction store still preserves stored scientific
support and its original retrieval times. Its detached event says `stored_support`
and `original_runtime_sidecar_not_supplied`; it cannot recreate original runtime
credit. Supply the original store when attribution reuse is required. Missing
stored support fails explicitly instead of reconstructing it. Provider failures
preserve the scientific result with a diagnosed attribution gap.

### Explicit article bibliography and declared terms (since 0.13.0)

```python
from sabueso.tools.db import europepmc

metadata = europepmc.get_article("pubmed:40832834")
# `text` is an independently supplied fragment, with its real location.
result = sabueso.extract_literature_mentions(
    text, "P60174", "pubmed:40832834", locator, article_metadata=metadata
)
extractions.save(result)
card.add_literature_extraction(result)
```

`get_article` accepts `pubmed:<id>`, `pmc:PMC<id>` or `doi:<doi>`. Europe PMC's core
response supplies bibliography, native identifiers, complete returned author records,
journal/pages/dates and literal licence declarations. The public projection excludes
the abstract; no full-text endpoint or linked article is consulted. Its service
version is recorded separately from the unstated article revision. Multiple matching
records and truncated results remain explicit and cannot be silently bound.

Binding requires a unique complete record stating the fragment's publication identity.
Metadata is a separate database SourceAssertion under `article_metadata_binding@1`;
the occurrence assertions retain `rule_extraction`. Source-declared aliases support
the explicit binding, never an identity guessed from names or titles. Nothing verifies
that an arbitrary supplied fragment is a quotation from that article.

`card.literature()` and `card.explain_literature(ref)` expose `article_metadata`
alternatives, original support IDs, retrieval times, bibliography and declared terms.
These do not overwrite existing source citation fields. `card.terms(use)` and pinned
packet terms report `declared_article_terms` separately: a literal such as `cc by`
does not state a licence version, and an open-access flag is not a reuse grant.
Supplied-fragment terms remain unknown and keep the existing terms-profile guard.
Raw archived core answers may include an abstract and retain the publication-term
retention policy; the bibliographic projection does not relax raw-answer sharing.

The original query trace records received/empty/partial/failed/unavailable/unqueried
outcomes, request hashes, service-version basis and original archive reuse. Supply
the original envelope to reuse its detached attribution through extraction/intake;
missing original metadata credit is reported. `ExtractionStore` saves this exact
binding. Card refresh preserves stored metadata without querying or rerunning the
rule, and saved readers remain inert. Packet composition credits represented stored
article citations only, without claiming new source access. Incomplete bibliography
retains the native available fields and explicit gaps.

## Literature on a card

`card.literature()` answers "which publications support which statements on this
card?". It does not read papers. It collects what sources state about publications:

```python
import sabueso

card, _ = sabueso.resolve("P60174", structures="all")
for pub in card.literature()["publications"]:
    print(pub["publication_ref"], pub["year"], pub["title"])
    for cited in pub["cited_by"]:  # e.g. UniProt, with what it cites the paper for
        print("  cited for:", cited["scope"])
    print("  primary citation of:", pub["primary_citation_of"])  # PDB entries
    for s in pub["supports"]:  # statements whose evidence names the paper
        print("  supports:", s["field_path"], s["value"], s["eco_code"])
```

- A publication is named `pubmed:<id>`, or `doi:<doi>` when it has no PubMed id. If it
  has neither, it keeps UniProt's own citation id (`uniprot.citation:<id>`).
- `cited_by` comes from `described_in` relationships: the references of the UniProt
  entry, with their scope (for example `HOMODIMERIZATION` or `VARIANT TPID ASP-105`).
- `primary_citation_of` lists the structures on the card whose primary citation it is.
  Only structures fetched from RCSB have one.
- `supports` lists the statements whose ECO evidence names the paper. UniProt's
  `Ref.<n>` evidences are resolved through the entry's reference numbers.
- A paper cited only as evidence (for example by a GO annotation) appears with its id
  and no title.

## Publications that mention the protein

`sabueso.resolve(..., europepmc={})` adds the publications whose text states the
protein's UniProt accession, found by Europe PMC's text mining of abstracts and
open-access full texts:

```python
card, _ = sabueso.resolve("P60174", europepmc={})  # or {"limit": 100}, newest first
for rel in card.relationships("mentioned_in"):
    print(rel["object_ref"], rel["qualifiers"]["year"], rel["qualifiers"]["title"])
```

- Only a stated accession counts. Europe PMC also tags gene and protein *names* with
  UniProt entries, but without the organism: "triosephosphate isomerase" in a paper on
  the human deficiency is tagged with a yeast entry. Sabueso does not use those.
- A mention says that the paper names the entry, not what it states about it. It
  appears in `card.literature()` under `mentions`, never as curated.
- These are not UniProt's curated references, which come as `described_in`
  (`cited_by`).
- Every article is fetched, up to 5000, and a cut is reported. HsTIM is mentioned in
  354 in the frozen search of 2026-09-29; live totals change.

### Locate a stated accession in an explicit article

`get_annotations` reads Europe PMC's accession-number annotations for a named
publication, preserving its provider, annotation link, section and text fragments:

```python
from sabueso.tools.db.europepmc import get_annotations, FixtureEuropePMCClient

response = get_annotations(
    "PMC:PMC12400196", client=FixtureEuropePMCClient("temp_data")
)  # omit client for the live source
for article in response["record"]:
    for annotation in article["annotations"]:
        if (
            annotation.get("subType") == "UniProt"
            and annotation.get("exact") == "P60174"
        ):
            print(annotation["section"], annotation["id"])
            print(annotation["prefix"], annotation["exact"], annotation["postfix"])
```

This public example is a figure annotation in [Kontellas et al. (2025)](
https://doi.org/10.1107/S2053230X25006454), whose article is CC BY 4.0. The raw tag
also states `http://identifiers.org/uniprot:P60174`. The API returns a MED record
with a `pmcid` for this PMC request; both original identifiers are kept.
One article id or a list is accepted, using `MED:<pmid>` or `PMC:PMC<id>`.

`prefix`, `exact` and `postfix` are fragments, not a complete sentence. An empty
annotations answer does not establish that an accession is absent from the paper.
Failures raise `ConnectorError`. This route returns source records; it does not add
locations or scientific claims to a card. Article terms govern storage of text
fragments, and the response's `version` is None when no source release is stated.

### Keep located mentions on a card (since 0.12.0)

Use explicit articles to add their located accession mentions to a protein card:

```python
card, _ = sabueso.resolve("P60174", europepmc={"article_ids": "PMC:PMC12400196"})
for publication in card.literature()["publications"]:
    for mention in publication["mentions"]:
        for location in mention.get("locations", []):
            annotation = location["annotation"]
            print(annotation.get("section"), annotation.get("id"))
            print(card.explain([location["source_assertion_id"]]))
```

`article_ids` accepts the same ids as `get_annotations`; it cannot be combined with
the search's `limit`. Requests are isolated per article, with outcomes in
`card.quality["enrichments"]`. The native MED and PMC ids remain as returned. The
printed accession and its UniProt tag must both identify the card's anchor for a
direct protein mention. Names and other UniProt accessions do not establish identity.

PDB mentions use a separate route within the same request. A printed four-character
PDB code and matching PDBe tag identify the mentioned entry. If a source-supported
`has_structure` relationship already associates that entry with the protein, the
card adds a derived `structure_mentioned_in` relationship. No structures are fetched
or selected because an article mentions them. PDB mentions without association
support are listed in the request's `unlinked_pdb_mentions`.

```python
for publication in card.literature()["publications"]:
    for mention in publication.get("structure_mentions", []):
        print(mention["structure_ref"], mention["locations"])
        context = mention["structure_context"]
        print(card.explain(context["source_assertion_ids"]))
        print(mention["derivation"])
```

This view retains both the article's raw PDB mention and the structural source's
association with the protein, under rule `structure_mention_context@1`. It describes
an entry association: a PDB entry may contain a complex or chimera. It does not infer
which chain, residues or molecule the author discusses, whole-entry identity, or a
scientific claim. It stays separate from `mentions`. In the public example, the
2JK2 mention in Methods has UniProt support; 7QON mentions remain unlinked. Expanded
PDB codes are currently unhandled.

Each occurrence keeps its annotation unchanged and its own SourceAssertion, imported
from Europe PMC with `acquisition={"method": "database", "origin": "text_mining"}`.
There is no human validation or scientific claim. Different qualifier answers stay
visible in `qualifier_conflicts`. Refresh asks the recorded article ids again; a
stored historical assertion remains readable by its pin after refresh.

Article terms govern these fragments. The annotation response does not state the
article's licence, so `card.terms("redistribution")` reports **Europe PMC Annotations**
as unknown, separately from bibliography, and includes every located fragment among
its items. This remains unknown even for the CC BY public example: its fixture licence
was checked separately, and is not invented as a statement of the annotation API.
The `commercial` and `non_commercial` terms profiles exclude this intake before
fetching. Schema 0.3.11 adds these optional locations and structure context; published 0.3.10 cards are kept
unchanged.

### Explain a publication's links (since 0.12.0)

```python
explanation = card.explain_literature("pubmed:40832834")
explanation["card_ref"]  # exact state read
for link in explanation["links"]:
    print(link["relationship_ref"], link["source_assertions"])
    print(link["structure_contexts"])  # both legs, when linked through a PDB entry
explanation["unlinked_pdb_mentions"]  # recorded rejected occurrences, with reasons
```

`literature_explanation@1` follows stored citation, mention, primary structural
citation, measurement and curated/ECO support. It keeps each relationship and its
alternatives, with pinned assertion references. It neither acquires articles nor
selects structures. Its structural context still has only `entry_association` scope.

Use the exact `publication_ref` listed by `card.literature()`. Native `pubmed:`,
`doi:`, `europepmc:MED:`, `europepmc:PMC:` and `uniprot.citation:` references are
accepted; aliases are not guessed. `not_on_card` means no stored link, and `partial`
means support is missing from the stored card. Recorded annotation requests retain
their own outcomes; neither status establishes absence in the publication.

To explain an earlier observation, load its card pin first:

```python
historical = store.load(saved_card_ref)
explanation = historical.explain_literature("pubmed:40832834")
```

## Curated literature assertions

When you read a paper, record what it states on the card. Sabueso keeps where the
statement comes from and compares it with what databases state:

```python
record = card.add_literature_assertion(
    "features_positional.natural_variant",
    {
        "start": 105,
        "substitution": {"original": "E", "alternatives": ["D"]},
        "description": "destabilizes the dimer",
    },
    publication="pubmed:18562316",  # or "doi:10...."
    curator="your-name",
    locator="Fig. 2",  # where in the paper
    quote="...",  # optional, a short excerpt (at most 300 characters)
)
print(record["outcome"])  # new, corroborates, differs, not_comparable or not_compared
```

- **Fields.** Knowledge fields only: `annotations.*` (see also the biological context
  below), `features_positional.*` (except
  family sites, alternative sequences and secondary structure), `properties.physchem.*`
  and `names.synonyms`. A positional item can give `start` (and `end`) in the card's
  UniProt numbering instead of a full location.
- **Outcomes.** The same item, identified for example by position and substitution:
  - with the same content, it `corroborates`;
  - with a different content, it `differs`. It is recorded in `quality.conflicts` and a
    `CuratedDisagreementWarning` is shown.

  Sabueso cannot tell whether two texts mean the same thing, so it flags the
  difference for you to judge. Free-text fields such as `annotations.subunit` are
  `not_compared`.
- **Priority.** A curated assertion never takes priority automatically, and nothing is
  discarded or overridden.

### Biological context of a target

Whether a protein is worth studying as a target in an organism depends on facts that
come from papers and organism databases. Four fields hold them, curated as above:

| Field | Item |
|---|---|
| `annotations.stage_expression` | `stage`, `observation`; optional `host`, `method`, `level`, `note` |
| `annotations.essentiality` | `method`, `phenotype`; optional `stage`, `host`, `condition`, `call`, `note` |
| `annotations.accessibility` | `compartment`; optional `exposure`, `stage`, `host`, `method`, `note` |
| `annotations.metabolic_role` | `pathway`, `role`; optional `stage`, `host`, `method`, `note` |

```python
card.add_literature_assertion(
    "annotations.essentiality",
    {"method": "RNAi knockdown", "phenotype": "growth arrest", "stage": "epimastigote"},
    publication="doi:10....",
    curator="your-name",
    locator="Fig. 3",
)
```

- **Values are text, as stated.** A phenotype is never turned into a category. `call`
  records the authors' own word, such as "essential", if they use one.
- **The organism is the card's.** A knockdown done on an ortholog is curated on the
  ortholog's card, not on this one.
- **Comparison.** Two statements under the same condition are compared: essentiality by
  method, stage, host and condition, the others by stage and host. Another stage is
  another statement.
- **Knowledge state.** A field nothing has been curated for is `not_queried` from
  `Literature`, never `not_stated`: nobody has read the literature for it yet.

For pathogen genes, databases also state some of this.
`sabueso.resolve(..., phi_base=True)` adds what PHI-base curates about mutants of the
gene (`annotations.pathogen_phenotypes`): for example "Lethal" for a knockout, or
"reduced virulence" on a host. Each item comes with its whole genotype, the pathogen and
host strains, the publication and the PHI-base release. The first use downloads a
PHI-base release, about 12 MB, and keeps its index in memory. To keep it between
sessions, set `$SABUESO_CACHE_DIR`.

The pathways a protein takes part in come from Reactome:
`sabueso.resolve(..., reactome=True)` adds `participates_in` relationships to its
lowest-level pathways and its reactions. Each pathway comes with its ancestors
(Glycolysis, Glucose metabolism, …, Metabolism), and each event with whether Reactome
inferred it from orthology.
- **Quantities.** Give the unit (`"0.825 kDa"`, `puw.quantity(825, "Da")`). The value is
  kept as written and compared at the precision it was stated with.
- **Relationships.** `card.add_literature_relationship(predicate, object_ref,
  qualifiers, publication=..., curator=...)` records an interaction, the residues at an
  interface, and so on. It merges with the same relationship from other sources, and
  qualifiers stated differently are kept as conflicts and flagged. Bioactivity
  measurements have their own method, below.
- **Bioactivities read in a paper.** `card.add_literature_bioactivity(molecule,
  "IC50", "33 uM", publication=..., curator=..., target_assignment="direct")`.
  - The molecule can be a small-molecule card, an identifier (`chembl:`, `pubchem:`,
    `pdb.ligand:` or `inchikey:`), or a recorded identity. Sabueso keeps its InChIKey
    and every record linked to it.
  - The measurement is compared with ChEMBL's measurements from the same paper, the
    same molecule and the same type. ChEMBL now states each measurement's PubMed id.
  - Curated measurements appear in `card.bioactivities()`, marked `curated`.
    `target_assignment="homology"` (measured on an ortholog) is left out by default, as
    ChEMBL's homology assignments are.
  - A range is `value="10 uM", upper_value="20 uM"`. It is classified by its band when
    both ends share one, and as inconclusive when it spans a threshold.
  - An uncertainty the paper states goes in `uncertainty`:
    `{"kind": "sd", "value": "3 nM", "n": 3}` (also `"sem"`, or `"unspecified"` for a
    bare "±"), or `{"kind": "ci", "lower": "8 nM", "upper": "18 nM", "level": 0.95}`.
    It is part of the statement and appears in `card.bioactivities()` and the table.
    It does not change the class, which is read from the value itself. It does not change
    the comparison with ChEMBL either: both read the same paper, so they should state
    the same number.
- **How a compound acts on residues.** `card.add_literature_engagement(molecule,
  [{"position": 15, "residue": "Cys"}], "covalent", publication=..., curator=...,
  covalent_residue=15, method="mass spectrometry")`.
  - Positions are the entry's UniProt numbering. A residue code, when you give it,
    must match the entry's sequence.
  - The engagement is compared with the residues the same molecule contacts in
    structures (PDBe-KB): shared residues corroborate. Different ones are "not
    comparable", not a contradiction.
  - It shows in `card.ligand_sites()["curated_engagements"]`.
- **A claim that fits no field.** `card.add_literature_claim("interface", "…text…",
  publication=..., curator=..., about=["residues:15"])`.
  - The topic comes from a fixed list: interface, mechanism, selectivity, stability,
    inhibition, structure, dynamics, localization, expression, essentiality, pathway,
    other.
  - Claims are kept and listed by topic (`card.claims()`, `card.table("claims")`), but
    never compared, because two texts need a reader. Their outcome is `not_compared`.
- **Where it shows.** `card.literature()` lists each publication's curated assertions
  with their outcome.
- **Scope.** How a statement bears on a project's hypotheses is not Sabueso's: that is
  Evidence, in Nextia.

## How each statement entered

Every SourceAssertion records how it entered the card (`acquisition`). This is not a
measure of how true the statement is:

```python
card.acquisition()
# {"methods": {"database": {"UniProt": 412, ...}, "curation": {"Literature": 3}},
#  "origins": {"text_mining": {"DISEASES": 42}}, "extractions": []}
card.explain([source_assertion_id])[0]["acquisition"]
```

- `database`: imported from a source's record. When the source states that its record
  was mined from text, for example DISEASES's text-mining channel or Europe PMC's
  mentions, `origin` says `text_mining`.
- `curation`: a person read the publication and recorded it, as above.
- `rule_extraction` and `model_extraction`: extracted from a text by a named tool or
  model, with its version, run by Sabueso or by you. The literal rule released in 0.13.0
  above is implemented; broader rules and model extraction remain pending. A model-extracted statement is
  never reported as curated.
- Cards saved before this was recorded read as `not_recorded` until they are built
  again.

Knowledge packets report the same per source, in their provenance.

## Names that papers use

A paper may call a protein by a name UniProt does not list, such as a paralog's
"TIM2". Record it once:

```python
card.add_literature_assertion(
    "names.synonyms", {"name": "TIM2"}, "pubmed:...", "curator"
)
store.save(card)
sabueso.resolve(EntityQuery(name="TIM2", organism=5722), curations=store)
```

Resolution then uses that anchor (rule `curated_name`), with the publication in its
decision. A name curated for two entries is reported as ambiguous. A name anchored
in another organism does not answer the query.

## Keep curations across rebuilds

A card is rebuilt whenever you query the sources again, for example to get a newer
UniProt release. Keep what you curated in a **curation store**, a JSONL file you own, and
apply it when the card is built:

```python
store = sabueso.CurationStore("curation.jsonl")
store.save(card)  # records the card's curated assertions; saving twice changes nothing

# Another day: the card is rebuilt from the sources, and the curations are applied.
card, _ = sabueso.resolve("P60174", curations=store)  # or curations="curation.jsonl"
print(card.quality["curation_store"])  # applied, skipped_retracted, changed
```

- **Same ids.** Each curated assertion gets back the same SourceAssertion id, because the
  id is derived from what was stated: publication, field, value and locator. A reference
  to it keeps meaning the same thing.
- **Recomputed outcomes.** Outcomes are compared again against the fresh sources. An
  outcome that changed since it was last recorded is listed in `changed`, for example
  `new` → `corroborates` when a database starts to state the same thing. Save again to
  record the outcome last seen.
- **Retraction.** `store.retract(source_assertion_id, reason, curator)` keeps the record,
  with who retracted it, why and when. It is never applied again.
- **Scope.** Records of other entities in the same store are ignored.
- **Acquisition.** Only curated literature assertions are exported. Rule/model
  extractions remain extractions, including those a person validated; they are left
  out rather than relabelled on replay. Legacy curations with curation metadata are
  still exported. Use `KnowledgeStore` to retain an extraction's exact acquired card
  state. Curation records previously exported without their extraction provenance
  cannot recover it automatically; consult the original card state.

A small public [review draft and preservation rehearsal](https://github.com/uibcdf/sabueso/tree/main/examples/literature_curation)
uses HsTIM and one published abstract. It produces explicitly hypothetical artifacts
for checking outcomes and rebuilds, with human validation left unset.

## Located readings prepared by an agent

`examples/user_journeys/literature_source_review.py` preserves a native licensed
article and two located readings as a review draft. The preparer is Codex (agent),
with scientist review pending. The proposals remain separate from card knowledge;
no literature SourceAssertions or human curation are created. The corrected
example format `@2` rejects its initial unqualified `@1` curation bundles.

A non-empty `curator` argument validates the name's shape, not whether a person
reviewed the paper. Agent preparation cannot supply human acceptance. An actual
rule/model extraction needs its own named tool/version and keeps that acquisition
method even after validation. The SDK's current extraction intake is bounded to
its delivered literal rule; the draft example does not bypass that boundary.
