# Knowledge packets

A knowledge packet answers a declared question in one call. It resolves the proteins,
composes what Sabueso's views say about the aspects asked, states what is not known,
and pins every card state it read, so that the answer can be cited and read back
exactly.

```{note}
Knowledge packets are a prototype, released in 0.6.0. Their shared contract with the
rest of MOLI is under discussion (uibcdf/moli#22), so their shape may change.
```

## A question and its answer

```python
import sabueso

query = sabueso.KnowledgeQuery("P60174", comparator="P52270")
packet = sabueso.knowledge_packet(query, store="knowledge.db", packet_name="tim_pair")

packet.ref  # 'sabueso:packet:tim_pair@sha256:…'
packet.facts.keys()  # the aspects asked
packet.unknowns["subject"]["rows"][:3]
```

A `KnowledgeQuery` is structured, not free text:

- `subject`: a UniProt accession; `comparator`: another one, optional;
- `aspects`: among `identity`, `structures`, `oligomer`, `ligand_sites`,
  `bioactivities`, `sequence_features`, `literature`, `disease_association`,
  `biological_context` and `orthology` (all but `orthology` by default: a protein has
  thousands of orthologs, so a query asks for them by name);
- `constraints`: for now `bioactivity_sources`, among ChEMBL (the default), BindingDB
  and PubChem BioAssay.

Anything else is refused, never ignored. What each aspect asks of the sources is fixed
by a named, versioned mapping. Development uses `packet_aspects@8`: ligand-site
instances carry explicit identity/sequence scope under `ligand_instance_scope@1`,
and indexes declare that rule. Foreign or unknown-axis contacts remain unplaced;
unidentified instances cannot prove chain spanning. Instance/flag structure
references keep RCSB support in both full and index terms reports. Earlier `@6`/`@7` packet
interpretations and their terms scopes remain supported without substituting the
new reader. The `@7` disease context is retained: disease
statements retain their identity paths and identifier-scoped coverage under
`disease_grouping@3` and `disease_identity_coverage@1`. Published 0.14.0 uses
`packet_aspects@6` (since 0.12.0): direct UniProt mentions and supported PDB mention
context join the
literature index and unknowns. Automatic acquisition asks Europe PMC for
bibliography only. Released `@5` added GTEx's tissue terms
(UBERON, or EFO for a cell line) to `biological_context`, next to the gnomAD pext they
name. `@4` added UniRef to `identity`
(the entry's clusters and the entries `clustered_with` it, #103). `@3` added to `@2` the kinase and
GPCR classifications (`identity`), kinase conformations, GPCR states and antibody
complexes (`structures`), the kinase pocket (`ligand_sites`), GPCR segments and generic
residue numbers (`sequence_features`), and the `orthology` aspect (OMA). Packets of
different mappings are not compared (`same_knowledge` is `None`). Keyword arguments to
`knowledge_packet` only choose how the sources are reached (a `resolver`, or source
clients such as `chembl_client`); they never change what is asked.

An aspect asks the default acquisition route of each source that answers its areas.
Located article annotations require separate explicit requests; bibliography cannot
query them, so PDB mention context remains `not_queried` with that explanation.
Other reasons include a source that does not cover the organism (a human-only source for a
parasite protein), only curation states the area, or the query did not name the source
(`bioactivity_sources`). `sabueso.core.packets.aspect_options(aspect)` lists what an
aspect asks for.

## What a packet holds

- `entities`: the pinned state of each card it was composed from.
- `facts`: per aspect and per protein, the output of Sabueso's views, each with its
  named rule. With a comparator, some aspects also hold what the two say together: the
  identity audit, the structure inventory, and, for `orthology`, the relationships
  in which OMA states one protein an ortholog of the other.
- `conflicts`: where sources disagree, as the cards record it.
- `unknowns`: per source, what is `not_stated`, `not_queried`, `unavailable` or
  `partial`, for the areas of the aspects asked. An absence is a fact about a source,
  never evidence.
- `provenance`: the sources, their releases and retrieval dates, how their statements
  entered (`acquisition`: for example `database`, `database (text_mining)` or
  `curation`), and what each enrichment returned.

Quantities keep their unit, as `{value, unit}`.

A packet holds each statement once (`knowledge_packet@2`), and other places name it
instead of copying it:
- a grouped disease statement names what it groups, from the same aspect: an
  association by its `relationship_id` (`associations`), a UniProt disease by its
  `accession`, a ClinVar condition by its `variant` and `condition` index
  (`clinical_variants`). Beside the reference it keeps what the grouping adds:
  `grouped_by`, `narrower`, or the `reason` it was not grouped. Development mapping
  `@7` also keeps `identity_paths` and `identity_coverage` beside that reference;
- the joint structure inventory names each protein's structure by its
  `relationship_id`, found in that protein's `structures` facts.

A fact names the SourceAssertions behind it. `packet.cite("subject", "SA_…")` gives its
pinned reference, which `store.source_assertion(ref)` reads back.

## An index instead of the facts

A full packet holds every view's output. For a well-studied protein that is large: the
0.10.0 measurement of a TcTIM/HsTIM packet with three bioactivity sources was 2.1 MB, 861 KB of it
bioactivities. `detail="index"` asks for what the cards hold instead, by reference:

```python
query = sabueso.KnowledgeQuery("P52270", comparator="P60174", detail="index")
packet = sabueso.knowledge_packet(query, store=store, packet_name="tim_index")
area = packet.facts["bioactivities"]["subject"]["areas"][
    "relationships.has_bioactivity"
]
area["count"], area["by_source"]
# 1002, {'BindingDB': 17, 'ChEMBL': 493, 'PubChem BioAssay': 492}
packet.item("subject", area["relationship_ids"][0], store)  # the measurement, as stored
```

Per aspect and protein, an index gives each field the card holds (how many items, from
which sources, and the SourceAssertions that state them) and each relationship area (how
many, from which sources, and every relationship's id). It names the views a full packet
would hold (`full_views`) and the rules they apply (`full_rules`), which the pinned
cards compute or carry. The level of detail never changes what is asked of the sources, so what
an index reports as `not_queried` a full packet would not have asked either. Nothing is ranked, selected
or summarized beyond counting (`packet_index@1`), and `unknowns`, `conflicts` and
`provenance` are whole. That 0.10.0 packet was 135 KB as an index.

An index and a full packet are never compared (`same_knowledge` is `None`).

### Literature mentions (since 0.12.0)

The literature index distinguishes `relationships.mentioned_in` (a direct UniProt
mention) from `relationships.structure_mentioned_in` (a PDB mention with a
source-supported association to the protein). The latter keeps both statements
under `structure_mention_context@1`; it infers no chain, author focus or scientific
claim. An index names that rule in `full_rules` and cites each relationship without
copying article fragments.

To index located annotations, build a card with explicit articles, then compose:

```python
card, _ = sabueso.resolve("P60174", europepmc={"article_ids": "PMC:PMC12400196"})
query = sabueso.KnowledgeQuery("P60174", aspects=["literature"], detail="index")
packet = sabueso.compose_packet(query, card)
store.save(card)
store.save_packet(packet, "located_literature")
area = packet.facts["literature"]["subject"]["areas"][
    "relationships.structure_mentioned_in"
]
relationship = packet.item("subject", area["relationship_ids"][0], store)
context = relationship["qualifiers"]["structure_context"]
support = [
    packet.item("subject", identifier, store)
    for identifier in context["source_assertion_ids"]
]
```

These reads use the packet's exact card state even after a later acquisition.
Composing a card without these requests reports `not_queried`; a returned empty
annotation answer is `not_stated`, a failed request is `unavailable`, and a mixture
of supported mentions and failed requests is `partial`. Both detail levels report
the same gaps. Missing offline search fixtures are also unavailable; they do not
establish an absence of articles.

`packet.item` reads the exact card state the packet pins. A store that does not hold
it refuses (`StorageError`); the latest state is never read in its place.

Sabueso does not authorize. An index reveals what exists, how much and from where, even
without values. Before an index, a packet or an item reaches anyone, the platform
applies the recipient's disclosure policy (uibcdf/moli#22).

## Read the support's terms (since 0.12.0)

`packet.terms("redistribution", store)` follows represented statement support at
the exact saved card pins. It reports source-stated terms, attribution, restrictions
and unknowns, including publication terms for article fragments. Full and index
support `packet_aspects@6/@7`; @6 index scope retains historical disease
grouping @2, while @7 includes grouping @3 and identity coverage @1. Other mappings
need a scope adapter. The
detached report uses the current packaged registry with review dates and does not
change the packet. See [terms](terms.md) for its scope and lineage limits.

## Deterministic, with two ids

A packet never calls a language model, never ranks, and never summarizes: a full packet
holds the aspects asked as the views compute them, and an index counts and references
what the cards hold. The same query and the same card states give the same packet.

Sources change, though, and reading them again records new retrieval times. So a
packet has two ids:

- `packet.snapshot_id()`: the exact state, retrieval times included. This is what its
  pinned reference names.
- `packet.content_id()`: the knowledge alone, without retrieval times or the Sabueso
  version that built the cards. `packet.same_knowledge(other)` compares it.

Cite the pin, never the `content_id`. Two packets with one `content_id` state the same
knowledge, but they are not the same observation: they were read at different times,
perhaps from different releases (uibcdf/moli#22). Keep the reference Sabueso gives
whole, as an opaque string: its public form is still being agreed in MOLI
(uibcdf/moli#3).

`store.packet_history("tim_pair")` lists each saved revision with its format, its
`content_id` and `knowledge_changed`. So "has anything changed since the last time?"
has an answer. Packets saved by earlier releases (`knowledge_packet@1`, `@2`) are still
read; `@3` states its level of detail. Revisions with different formats, aspect
mappings or detail levels are not compared: `knowledge_changed` and
`same_knowledge` are `None`, never a change that did not happen.

## Stored packets

- `store.save_packet(packet, name)` refuses a packet whose cards are not in the store.
  `knowledge_packet(..., store=…)` saves them first.
- `store.load_packet(name or ref)` verifies the packet and every card state it cites.
  A store changed outside Sabueso is refused.
- `store.packet_names()` lists the names.

To compose a packet from cards you already have, without resolving again, use
`sabueso.compose_packet(query, subject_card, comparator_card)`.
Composition automatically attaches `packet.attribution`, a detached runtime
record outside the scientific payload and hashes. Save its original JSON beside the
packet; payload-only saved readers add no credit and have no reconstructed capture.
See [automatic attribution](attribution.md) for application workflows and failure status.

The cards are used as they are. An aspect whose sources they were not built with
shows as `not_queried`.
