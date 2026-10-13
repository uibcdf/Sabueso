# What may be done with the knowledge

Development FDA OOPD detailed pages retain the explicitly linked
[FDA website policy](https://www.fda.gov/about-fda/about-website/website-policies):
public-domain reuse unless otherwise noted, with independent contributing-source
and other rights retained. Credit is requested, together with source URL and copy
date. The shared US-PD display label now refers to the source's policy; it does not
substitute NLM or openFDA terms for FDA OOPD. Rights metadata is independent of the
online client's current HTTP-404 access failure.

Development TTD target listings retain NOT-STATED data terms: public access
qualifies source fidelity, while automated use/sharing remain unknown and archive
retention internal. Original factual qualification stays local unreleased. iPTMnet
report database terms are CC BY-NC-SA 4.0 with attribution, noncommercial and
share-alike conditions; independent contributing-source rights remain separate.

Development BRENDA EC-class descriptions carry the provider's CC BY 4.0 data
terms and BRENDA/DSMZ/current-publication attribution. SOAP account and bulk
active acceptance concern separate acquisition routes. ASD's research-only data
conditions prohibit third-party distribution; TTD's public export has no qualified
data grant. Article and frontend software licences do not replace data terms.

Development DepMap model metadata retains the selected public **24Q4 article v1**
CC BY 4.0 grant, attribution and original native file support. That grant is not
propagated to other releases or collaborator datasets. Pharos/TCRD selected-target
outputs keep contributing-source rights separate and a distinct data grant
`NOT-STATED`; software/article licences do not qualify automated redistribution.

Every value and relationship on a card traces to the SourceAssertions that state it, and
each SourceAssertion names its source. Sabueso can therefore say, for a use you name,
what each source states about its own terms, and what knowledge remains if you keep
only the sources that allow that use.

```{note}
Card/deck reports were released in 0.7.0; packet reports below were released in 0.12.0. This is a report of what the sources state, not
legal advice: the decision, and the responsibility for it, stay with you.
```

```python
report = card.terms("commercial_product")
report["sources"]["ChEMBL"]  # licence, verdict, obligations, attribution, statement
report["obligations"]  # e.g. ["attribution", "share_alike"]
report["attribution"]  # the attribution texts to carry
report["unknown"]  # sources whose terms Sabueso cannot answer for
card_report = report["cards"][0]
card_report["objects"]  # per related entity (a measured molecule…): complete,
# partial, unknown or none
deck.admissible("commercial_product")  # only cards whose knowledge all remains
```

Development raw-response retention also preserves `NOT-STATED` licences as
`share="unknown"` with `reason="licence_not_stated"`. A reviewed service page or
software licence does not grant redistribution of its data. EPPIC's prediction-data
reuse remains unknown; PDB-REDO's recorded usage policy permits reuse with its stated
attribution and parent-data conditions.

AlphaFill's recorded usage policy permits reuse with source/parent acknowledgement
and AlphaFold parent conditions. LIGYSIS data redistribution remains unknown:
free/commercial website access, MIT software and publication terms are distinct
from the raw site's data terms. These development connectors retain the registry's
recorded terms in transport/archive receipts.

GlyGen's recorded CC BY 4.0 database-set grant retains GlyGen/original-provider
attribution. Native pointers do not change contributing-source licences or grant
rights to linked publications; the source lists those licences separately.

## Development disease-deck admission

For portable disease support (`sabueso.disease_deck_support@1`), admission follows
`disease_deck_admission@1`. All embedded disease snapshots, native returned rows and
excluded-candidate context must permit the requested use. Each member is then
checked as an unchanged card: an allowed alternative for a resolved value does not
license other raw SourceAssertions that would also be exported. Unused native
statements are checked too. Per-record rights not declared for raw content remain
unknown, even when an individual projected relationship has known depositor terms.

```python
admitted = deck.admissible("redistribution")
admitted.meta["admission"]["terms"]  # original admission scope and obligations
admitted.meta["admission"]["input_deck_snapshot_id"]  # original deck content address
admitted.meta["excluded"]  # rejected cards, item reasons and historical identity pins
```

Shared unknown/restricted terms raise `ArgumentError`; its `admission_report`
contains exact item locators and registry verdicts without asserted values. No
derived deck is produced in that case. Pruning an individual source from complete
native context is not implemented. Malformed or incomplete support raises
`StorageError` before admission. Retained members keep their exact card pins; removed
member identity references are historical, separate from the still-readable native
candidate basis. JSONL/SQLite and knowledge-store reads preserve that distinction.

The operation changes no original deck, acquires nothing and adds no runtime credit.
Keep original acquisition/attribution sidecars beside the original deck. The report
uses the current packaged registry and its review dates, not historical terms at
acquisition. These are development capabilities; #29 remains open.

## Uses

`internal_research`, `academic_publication`, `redistribution`, `derived_dataset` and
`commercial_product`. The use is yours to name. Sabueso does not guess it.

## Verdicts

- **allowed**, with obligations:
  - `attribution` (CC BY, CC BY-SA);
  - `credit_requested` (NLM's public-domain data);
  - `share_alike` (CC BY-SA), when the data leaves your hands: redistribution, a
    derived dataset, a product. It does not bind a publication that cites.
- **restricted**, with the reason, e.g. a non-commercial licence for a commercial
  product.
- **unknown**, with the reason: no terms recorded, or terms that depend on each record
  and are not recorded for this one. A curated statement keeps its publication's terms.
  Unknown is never "no restriction".

**Terms per record.** A PubChem BioAssay result keeps the terms of whoever deposited
the assay. An assay deposited by ChEMBL or BindingDB is a copy of their records, so it
is judged by their terms, and the report says so: `PubChem BioAssay (deposited by
ChEMBL)`, with its `basis`. An assay of any other depositor stays `unknown`, with the
reason `depositor_terms_not_recorded`.

A piece of knowledge **remains** for a use when at least one source that states it is
allowed. For human and *T. cruzi* triosephosphate isomerase, everything remains for a
commercial product, with attribution and share-alike (ChEMBL, BindingDB, and PubChem
BioAssay results deposited by ChEMBL).

Each source's terms, with the statement they come from and the date they were reviewed,
are listed on the *Data sources* page. A record older than a year is flagged
`review_due`.

## Terms of a packet (since 0.12.0)

```python
report = packet.terms("redistribution", store)
report["sources"]  # stated terms, review dates and attribution
report["scope"]["subject"]  # exact card pin and each represented support item
report["unknown"]  # includes article fragments whose publication terms are unstated
```

`packet_terms@1` reads exact card pins from the knowledge store. It reports the
SourceAssertions represented by the asked views, their conflicts and stored
relationship dependencies, rather than every source on the entire card. Full and
index packets share this support scope. Counts are statements and relationships,
not unique scientific facts. Both legs of a derived structural mention must remain
for the derived relationship to remain; source alternatives within a leg are
judged separately. Allowed bibliography never licenses attached text fragments.

This operation supports `packet_aspects@6/@7` in development (published 0.14.0: @6).
Older packets remain readable,
but their terms query raises `StorageError` until a historical scope adapter exists.
Missing cards or support are also refused; current heads never replace historical
pins. Index view rules must be recognized before views are reconstructed.

The report uses the current packaged terms registry with its review dates. It does
not reconstruct the terms registry as of the card's acquisition. Exact mapping and
qualifier lineage was not always recorded; disease grouping includes the stored
MONDO/MedGen identity/hierarchy context rather than claiming minimal inputs. These
limits are stated in the report. It is detached, changes no packet hashes or payload,
and does not record runtime usage or produce a pipeline bibliography.

## Building under a terms profile

A project can also build its knowledge only from sources whose terms allow its use:

```python
card, _ = sabueso.resolve(
    "P52270", chembl={}, pubchem_bioassay=True, terms="commercial"
)
card.quality["terms_profile"]  # the profile, and the sources it excluded, with why
```

- `terms="commercial"`: for a project that may end in commercial exploitation. Choose
  it from the first day: knowledge that informed a decision cannot be un-used later.
- `terms="non_commercial"`: for research without commercial exploitation.
- The profiles are named by use, not by institution. An academic lab under an industry
  contract makes commercial use, and a non-profit may not.
- A source the profile does not admit is not asked. The enrichment records
  `not_queried`, with the profile and the reason, and the knowledge state shows it.
  Sources with unknown terms are excluded too.
- A source whose records keep their depositor's terms is asked, and each record is kept
  only if its depositor's terms allow the use. PubChem BioAssay results of other
  depositors are left out, counted in the enrichment record and in
  `terms_profile["excluded_records"]`.
- Curated statements you apply are yours: the profile does not filter them.
- In development after 0.11.0, refresh preserves the recorded profile unless you
  explicitly override `terms`. Located Europe PMC article fragments have unrecorded
  publication terms, so both profiles exclude that intake before fetching.

Some sources need an account, a key, an academic licence or a written agreement before
they can be asked at all. They are listed, with what each needs, on the *Data sources*
page.

## Declared article terms (since 0.13.0)

Explicit article metadata supplied to literal extraction retains the source's licence
literal and open-access declaration. Card and exact-pinned packet terms expose optional
`declared_article_terms`, each linked to its original metadata SourceAssertion. This is
declarative context: an unspecified licence version is not inferred, and an open-access
flag grants no supplied-fragment permission. The fragment still reports unknown terms
and cannot bypass a terms profile. Raw Europe PMC core archives keep publication-term
retention independently of the bibliography-only public projection.
