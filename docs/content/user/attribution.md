# Automatic traceability and attribution

## Comparative view executions in development

Inside an explicit `sabueso.attribution()` context, three ordinary views retain
their execution separately from the scientific response:

```python
import ackredit
import sabueso

with ackredit.session("comparison workflow"):
    with sabueso.attribution() as run:
        differences = left.sequence_differences(right)
        variants = human.variant_tissue_usage(threshold=0.2)
        isoforms = human.isoform_tissue_usage(threshold=0.2)

original_operations = run.operations
```

The application supplies the cards and saves their exact pins together with the
original views and operation records. `sabueso.comparative_operation@1` keeps an
execution identity, original producer, times, requested parameters, applied rules,
input pins and a digest of each unchanged result. Repeated calculations retain
distinct executions and reused input credit. `operations` stays separate from
packet `records` and source `acquisitions`; it returns independent copies.
Packet and comparative uses share the same source-record declaration, so either
execution order contributes reused resources to one enclosing workflow.

`comparative_input_scope@1` describes selected input-field support. Isoform tissue
text follows all stored tissue-specificity assertions, as the existing engine
does. This does not establish row-level mapping or source-request membership.
Original source labels remain labels rather than verified database releases.
Missing or mismatched assertions stay in `support_gaps`; missing descriptions and
underlying publications stay separately in `bibliography_gaps`. Only represented
valid support receives stored-knowledge credit; no source access is performed.

Missing/unequal sequences and evaluated-empty views retain completed execution
with their original knowledge limits. Scientific failures propagate unchanged
with a failed record and no completed credit. Provider failure or unavailable/
changed pins preserve the scientific result and diagnose missing attribution.
The application can render a successful record's original
`provider.attribution` with `ackredit.Attribution.from_dict`, as below.

Plain view calls, pinned explanations and saved reading remain inert. A saved
reader verifies original pins/result digests and renders the saved bibliography;
it never recalculates a view to recreate past execution. This development slice
is outside published 0.14.0; broader operations and complete resource bibliography
remain #108 work.

The development [comparative journey](journeys.md#sequence-and-tissue-comparisons)
persists these records together with source acquisition and enclosing workflow
attribution. Its independent reader verifies saved result/support/credit bindings
and exports original references after reacquisition. Historical example formats
retain their execution gaps; today's runtime and bibliography never supply past credit.

## Source acquisition and packet composition

Development adds verified offline resource descriptions for gnomAD and GTEx,
plus a pext method description where the workflow actually accesses or reuses
supported pext data:

- [Chen et al.](https://doi.org/10.1038/s41586-023-06045-0), the provider-recommended
  gnomAD flagship description (online 2023; journal issue 2024).
- [GTEx Consortium (2020)](https://doi.org/10.1126/science.aaz1776), with the original
  collective author and its v8 analysis scope.
- [Cummings et al. (2020)](https://doi.org/10.1038/s41586-020-2329-2), the description
  of upstream pext methodology, with its 18 byline authors and original v7 study scope.

`method_description` credit follows `pext_reference_scope@1`: a completed pext
access or valid gnomAD pext input, with its original context. Variant-only queries,
failed/unavailable access and unsupported inputs receive no completed method credit.
Sabueso consumes precomputed annotations; this credit does not claim it executed
that upstream pipeline. Resource and method descriptions do not identify a row's
primary study or native dataset/method revision. Those gaps remain explicit.
Saved readers export their original references, including historical missing
metadata, without using newer declarations.

The provider's [citation clarification](https://github.com/broadinstitute/gnomad-browser/issues/1832)
and [pext release announcement](https://gnomad.broadinstitute.org/news/2024-11-gnomad-v4-pext/),
the [GTEx downloads](https://gtexportal.org/home/downloads/adult-gtex/) and primary
[gnomAD](https://pubmed.ncbi.nlm.nih.gov/38057664/),
[GTEx](https://pmc.ncbi.nlm.nih.gov/articles/PMC7737656/) and
[pext](https://pubmed.ncbi.nlm.nih.gov/32461655/) metadata were checked 2026-10-13.
No DOI or article lookup happens automatically at runtime.

Development gnomAD variant/transcript/consequence/pext access retains actual
GraphQL queries, original response identities/times and native transcript versions.
Requested dataset/genome and client pext/GTEx labels stay separate from unknown
native releases. Null consequence aliases differ from empty consequence lists;
failed later batches retain completed access without returning partial science.
Missing local files are unavailable. Missing upstream Ensembl gene identity stops
as unqueried before source client construction. The existing GraphQL API URL is
credited as a resource together with its verified background description. Pext
method descriptions are scoped separately; entry publications, actual method
revisions and native dataset revisions remain gaps.
Received/client/card-selected counts are distinct, and original supplied-gene pins
and saved attribution survive inert reading. Development coverage becomes 38
source families; these changes are outside the unchanged published 0.14.0 artifact.

Development OMA access retains separate xref, protein and ortholog observations.
Entry-name resolution is attributed to UniProtKB, which supplies those bindings.
Original response hashes, revision gaps, continuation, batch ambiguity and partial
failures remain explicit. The OMA REST API resource and UniProtKB search API URL
come from the existing connectors; resource credit supplies no entry/method
publication metadata or sequence revision. Missing local files mean unavailable
access. Client row counts differ from taxon/limit-selected card relationships;
the card's quality record preserves that selected scope. Modified source mappings
remain unjoined. Original scientific pins and saved credit remain readable without
fresh operations. This OMA slice extends coverage to 37 source families; gnomAD extends it above. It is
outside the unchanged published 0.14.0 artifact.

Development UniRef cluster/member access retains original page releases, links,
received/kept counts and partial failure scope under source `UniProt`. Portable
attribution credits the UniProt description and the specific UniRef API resource
already used by the connector. Client version labels do not prove coherent page
releases; missing headers stay unknown and fixture releases are declared labels.
Missing local files mean unavailable access. Cluster membership remains similarity,
and resource descriptions do not supply member publications or sequence revisions.
Saved readers retain exact pins and original credit without fresh operations.
Online member access stops before repeating a request URL or exceeding 100 logical
pages, including empty pages. Either condition raises a connector error: the trace
retains completed pages and the termination reason, while failed enrichment adds
no partial cluster assertions. The 5,000-member ceiling remains a successful,
explicitly truncated result. Transport retries have separate limits; the page
budget does not provide a strict elapsed-time deadline.
This extension is outside the unchanged published 0.14.0 artifact.

Development GTEx tissue access credits the [GTEx Portal](https://gtexportal.org/),
whose URL and acknowledgement are declared in Sabueso's source registry and public
fixture notice. Built-in online/fixture `tissues` and public `get_tissues` retain
original access records and portable attribution. The requested dataset label is
separate from an unknown native revision; returned row counts differ from the
terms selected into a card, and one response does not prove dataset completeness.
Missing local fixtures are unavailable; malformed responses and failed requests
do not establish absence. Blocked prerequisites create no GTEx operation. Archive
replay retains original response times; saved readers add no fresh credit.
The consortium resource description does not supply per-tissue primary studies;
those publications remain explicit gaps. This extension is on development
main and is outside the unchanged published 0.14.0 artifact.

Development NCBI Taxonomy access credits the
[NCBI Taxonomy resource](https://www.ncbi.nlm.nih.gov/taxonomy), verified
2026-10-08. Built-in online/fixture `taxa` operations and public `get_taxon`
retain original batch/query/response identities and missing/unavailable/failed
scope. Completed batches remain creditable before later failures. Replay preserves
original acquisition times; saved readers add no source access or fresh credit.
The Datasets API route version is not a taxonomy record revision, and the resource
description does not supply underlying taxonomic publications or a data-use grant.

Development FDA OOPD page declarations credit the U.S. Food and Drug
Administration, Office of Orphan Products Development, retaining each requested
page URL, acquisition date, original HTML/table/hash and separate approval
occurrences. FDA's policy requests credit rather than requiring it; exceptions
and contributing-source rights remain explicit. Native clinical/product literals
remain source statements and do not establish protein-target or clinical findings.

Development TTD target listings credit the Therapeutic Target Database, IDRB /
Zhejiang University and BIDD / National University of Singapore, retaining native
header release/date/provider URL and row support. No separate data grant is inferred.
Development iPTMnet reports credit iPTMnet, University of Delaware / Protein
Information Resource and Georgetown University, retaining original source/PMID
links and the [database licence](https://research.bioinformatics.udel.edu/iptmnet/license).
These source declarations do not constitute MOLI Evidence or clinical conclusions.

Development BRENDA EC-class descriptions credit the BRENDA Enzyme Database,
DSMZ Digital Diversity and [Hauenstein et al. (2026)](https://doi.org/10.1093/nar/gkaf1113),
*BRENDA in 2026: a Global Core Biodata Resource for functional enzyme and metabolic
data within the DSMZ Digital Diversity*, as requested by the
[provider citation page](https://brenda-enzymes.org/references.php), checked 2026-10-07.
These describe the resource; they are not experimental evidence for a queried class.

Development Pharos target metadata credits [Pharos/TCRD](https://pharos.nih.gov/)
and keeps contributing-source rights separate. Unknown target/TDL-rule revisions
and unstated data reuse terms remain explicit.

Development DepMap model context credits **DepMap, Broad Institute (2024),
DepMap 24Q4 Public**, [article version 1](https://doi.org/10.25452/figshare.plus.27993248.v1),
the DepMap portal and program. The article states CC BY 4.0; its grant applies to
the qualified release rather than every collaborator dataset.

Development Interactome3D metadata credits
[Interactome3D](https://interactome3d.irbbarcelona.org/about.php) and IRB Barcelona's
Structural Bioinformatics and Network Biology Group, with original row/hash and
selected archived representative scope. Data terms remain NOT-STATED; original
factual qualification is local unreleased with automated sharing unknown.

Development ProBiS catalog listings credit
[ProBiS-Database](http://probis.cmm.ki.si/?what=database) and retain native artifact,
row/line and full-document hash. The dated filename is not a scientific revision.
Data terms remain NOT-STATED; software/article licences do not qualify this export.
Original factual qualification stays local unreleased with automated sharing unknown.

Development PDBTM topology keeps the complete original XML and embedded COPYRIGHT
with every independent chain occurrence. Credit [PDBTM](https://pdbtm.unitmp.org/)
and the Institute of Enzymology, Budapest, as the native statement records.
Builtin resource bibliography is separate from per-entry scientific support.
Conditional nonprofit unchanged-content/copyright and commercial-agreement terms
remain explicit; automated use/sharing is unknown and qualification local unreleased.
PDB/source inputs and software rights are independent of Sabueso's MIT licence.

Development 3did DMI instances retain original block, pattern/date and structural
row support, with domain/motif input labels and full export hash. Credit
[3did and IRB Barcelona](https://3did.irbbarcelona.org/) independently of Pfam and
PLoS_CB_2010 source declarations. The builtin resource bibliography does not supply
per-instance experimental papers or current input licences. Data rights remain
NOT-STATED and original factual qualification bytes stay local unreleased; no
article/software grant or MOLI Evidence is assigned.


Development HPO gene/disease annotations retain original Gene/HP/disease/frequency
literals with native row/hash and dated release. Credit the
[Human Phenotype Ontology Consortium](https://hpo.jax.org/), preserving artifact
version `v2026-09-01`. The builtin dataset bibliography describes HPO and does not
supply per-occurrence experimental publication or contributor support. Its custom
unchanged-content/data terms and original input rights remain separate from
Sabueso's MIT licence; unchanged qualification artifacts stay local unreleased.


Development MEROPS classifications retain every native selected occurrence with
full-export hash, original namespace/family/taxonomy text and unresolved-row support.
Credit [MEROPS and EMBL-EBI](https://www.ebi.ac.uk/merops/) separately from native
row support. The [provider's whole-database Library GPL declaration](https://www.ebi.ac.uk/merops/about/availability.shtml)
is preserved with unspecified version. Local unshared qualification does not
establish publication/redistribution rights: automated use verdicts remain unknown,
archive retention internal and sharing unknown. Input/software/article rights stay
separate; no cleavage, activity or protein identity is inferred.


Development MetalPDB site assertions retain original site/PDB and metal/ligand/
donor context, response hash and donor-distance unit qualification. Credit MetalPDB
and CERM/University of Florence; the resource bibliography points to
[MetalPDB](https://metalpdb.cerm.unifi.it/) separately from site support. The
[public Coordination Sphere](https://metalpdb.cerm.unifi.it/pdbSearchResult?id=12ca_2)
declares Distance (Å); the native API's matching donor values retain full precision.
The API/about statement supplies no separate data redistribution grant. Terms
remain NOT-STATED; original JSON and the declared small HTML table excerpt stay
local unreleased work. Publication/software and input-resource rights are separate.


Development ECOD domain assertions retain native UID/domain, structure/chain,
classification and API URL. Credit ECOD and Grishin Laboratory; the resource
bibliography points to [ECOD](http://prodata.swmed.edu/ecod/), separate from domain
support. The [official API documentation](http://prodata.swmed.edu/ecod/documentation/api),
read on 2026-10-07, permits public unauthenticated access but supplies no separate
data redistribution grant. Terms remain NOT-STATED; original factual bytes stay
local unreleased work. Software/publication and PDB/Pfam/UniProt rights are separate.


Development TCDB assignments retain original accession/TC-system literals,
independent line occurrences and full-export hash. Credit TCDB and Saier Laboratory;
the resource bibliography points to [TCDB](https://tcdb.org/), separately from row
support. The [official FAQ](https://tcdb.org/faq.php), verified by direct public GET
2026-10-07, declares CC BY-SA 3.0 and GFDL for website text. That statement is not
assigned as a blanket grant for the assignment export or input resources: separate
export terms remain NOT-STATED and the original fixture stays local unreleased
work. No family, sequence or publication record is acquired.

Development ChannelsDB annotations retain original source groups and reference
literals. Credit ChannelsDB 2.0 contributors and the resource description,
[doi:10.1093/nar/gkad1012](https://doi.org/10.1093/nar/gkad1012), verified against
[the primary resource article](https://academic.oup.com/nar/article/52/D1/D413/7416806)
on 2026-10-07. This describes the resource, not the support for each annotation.
The [official documentation](https://channelsdb2.biodata.ceitec.cz/documentation.html)
does not establish a separate annotation-data redistribution grant in this review.
Keep data terms `NOT-STATED`; frontend Apache, article CC BY and underlying
UniProt/publication rights remain separate. No linked publications are acquired.

Development GWAS Catalog association pages retain native association/study IDs,
publication pointers, exact query/page boundaries and original statistical context.
Credit NHGRI-EBI GWAS Catalog and original study authors; the unchanged HBB fixture
retains PMID 39024449 and Verma et al., doi:10.1126/science.adj1182. [Catalog terms](https://www.ebi.ac.uk/gwas/docs/about/)
apply [EMBL-EBI Services Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/),
with original-owner rights. Summary-statistics CC0, visualisation CC BY and software
Apache are separate; no blanket licence is inferred for curated rows or articles.
No article text, summary-statistics dataset or participant data is acquired. Original
JSON/gzip/hash/time and replay keep source support without new access credit.

Development Monarch association pages retain native primary and aggregator sources,
ECO and publication pointers. The BioGRID-only fixture retains its original MIT
download-files notice with contributor attribution; arbitrary KG inputs keep their
own rights. Recommended data and BSD software terms are separate. Development
PRIDE project metadata retains the depositor's native per-project licence and source
publication context. PXD013616 declares CC0; cite its PXD identity and depositors.
That grant is not assigned to other projects or Proteins API providers. Neither
reader acquires linked content or creates new experimental support.

Development OmniPath access retains original aggregate resource names and
resource-prefixed publication references. Credit OmniPath and those contributors.
Resource/dataset/licence filters do not remove all other input annotations or grant
reuse rights. The SPIKE/SPIKE_LC-only TPI1 fixture is separately qualified under
CC BY 4.0 in `temp_data/NOTICE.md`; that grant is not propagated to arbitrary
OmniPath responses. Source-wide sharing terms remain unknown; input/publication
rights and the original snapshot time stay explicit.

Development WikiPathways native pathway cross-references retain [CC0 content
terms](https://www.wikipathways.org/terms.html), original pathway authors and
contributing-resource context. Credit WikiPathways and make the content terms
clear. Linked publications/external resources have separate rights and are not
acquired. Original snapshot bytes/time and replay receipts do not add access credit.


Development EMA orphan access preserves one original complete JSON acquisition,
its declared total and generation timestamp, independent page declarations and
original byte identity/retrieval time. Acknowledge European Medicines Agency (EMA)
in each copy, retaining the native data URL and actual access month/year.
EMA-owned metadata reproduction permits commercial and noncommercial use;
third-party material and linked documents keep separate rights. Supplied snapshots
add a local receipt; replay keeps original time without new remote access credit.

Development CIViC retains a complete native monthly accepted-items acquisition
with original bytes/time, explicit export label and independent row support.
CIViC contributors, native citations and Griffith et al. (2017), doi:10.1038/ng.3774,
remain attributable. Its content is CC0; linked publication rights are separate.
Supplied TSV/gzip adds declared metadata and a local receipt; replay retains the
original time and release without new source access credit.


Development DrugCentral supplies independent native drug-target observations with
full raw activity/MOA/source context and original composite-target scope. It does
not infer potency, molecule identity, clinical effects or automatic card enrichment.
Data retains [DrugCentral CC BY-SA 4.0](https://drugcentral.org/privacy), original
provider attribution, modification notices and applicable share-alike.

Development ClinGen retains one complete native CSV acquisition, original document
hash and independent matched row support. Native file/classification labels are
separate from actually observed retrieval time and unknown scientific revisions.
Source curated content has CC0; ClinGen requests source/access-date and appropriate
panel attribution. Linked reports and publications are not acquired. Supplied native
CSV/gzip files retain caller-declared original time and byte hashes without new
remote credit; archive replay keeps the original acquisition time.

Development HPA retains one native single-gene JSON subset acquisition and
independent categorical support with response hashes and the specific gene/data
URL. HPA requests resource and primary-publication attribution. CC BY 4.0 covers
copyrightable database parts; third-party input constraints remain independent.
Native dataset/gene/sequence revisions stay unknown. Linked assays, datasets and
publications are not acquired. Supplied JSON/gzip files retain declared original
times and local hashes without new remote-access credit.

Development SIGNOR retains one original native causal table acquisition with
row-level publication pointers, source-served sentences and regulator/target
context. Dataset bibliography does not fetch underlying article or sequence
support. Scientific revisions and score-model version remain unstated; CC BY 4.0
terms accompany the source without licensing independently linked publications.

Development APPRIS retains one native human-gene exporter acquisition and
independent row occurrences with original contributing-method labels. Dataset
bibliography does not imply acquisition of underlying sequence/structure/method
support or publications. Dataset/assembly/record/sequence revisions remain unstated.
The source's CC BY-NC-SA 4.0 obligations accompany terms and archive retention;
commercial products are restricted by this stated licence.

Development Complex Portal retains one native complex acquisition, complete
response hash, original release-date/prediction/ECO declarations and a resource
bibliography description. Original cross-reference qualifiers and pointers survive;
underlying experimental/prediction support and publications are not acquired.
Record/participant sequence revisions remain unstated. Query-bound supplied files
retain separate local receipts and optional SHA-256 checks without remote-access
credit. Official CC0 1.0 covers the data; software and linked resource/article rights
remain independent.

Development CATH domain summaries retain one original access receipt, full native
response hash and CATH dataset description. Required release selectors describe the
request route; response release, record and sequence revisions remain unstated.
Underlying structure/GO/EC publications are not fetched. Query-bound supplied
snapshots add local file receipts with optional SHA-256 verification, without original
remote-access credit. CATH resource data retain CC BY 4.0 attribution and separate
parent-resource rights.

Since 0.12.0, every completed packet composition attaches
`packet.attribution`. It keeps the resources behind selected stored statements, their
original source-record versions and pins, and the software executing composition.
The records are separate from the packet, its hashes and its terms report.
Traceability is a required Sabueso property. The first source-access slice also
retains automatic acquisition traces for built-in UniProt, Europe PMC and RCSB PDB clients;
its declared gaps prevent a claim of complete pipeline coverage.

Since 0.13.0, Sabueso extends that boundary to the built-in ChEMBL, PubChem and
BindingDB clients and adds detached attribution for `extract_literature_mentions`.
It also observes PDB CCD and UniChem chemical identity access, molecular resolution
and ligand-deck construction.
PDBe-KB ligand-site and interface-residue aggregates are observed too.
AlphaFold DB queries retain each returned model's native identity and version.
Development AAindex1 direct access retains original document/record identities,
literal publication pointers and an AAindex dataset description. Source release,
structured units and linked publication metadata remain explicit gaps. Notebook
reports and residue readers use stored knowledge and create no acquisition credit.
Development UniParc checksum search retains native pages, totals, release headers
and original archive-replay times, with a UniParc dataset citation. Its explicit
sequence candidate tool separately records current UniProt entry checks. Other
sequence databases and underlying publications are not fetched; their bibliography
gaps remain visible. Equal sequences do not establish protein identity.
Development AlphaMissense queries record host metadata discovery and the declared
prediction CSV as separate accesses. The prediction record retains its byte hash,
score revision gap and the requested Cheng et al. (2023) citation. Missing artifact
declarations create no prediction-resource credit. Mapping saved records acquires
no source or new credit; predicted classes remain separate from clinical assertions.

Development MobiDB v1 exports and SIFTS mapping queries retain their own acquisition
records, dataset descriptions, original source scope and bibliography gaps.
MobiDB database release differs from its API version. SIFTS releases and referenced
sequence revisions are unstated. Underlying provider/method publications are not
fetched; raw annotation provenance remains available. Metadata catalog and
detached source readers create no acquisition credit.

Development explicit UniProt isoform access records parent JSON and selected native
FASTA as separate operations with original times/hashes and UniProt resource credit.
Parent entry/canonical versions and database release remain separate from unknown
isoform sequence revision. Native declaration/VAR_SEQ pointers remain contextual;
isoform-specific publications and other isoforms are unqueried. Failed sequence
access keeps the successful parent observation. Supplied-file receipts do not prove
remote access. Mapping into supplied residue-reader input creates no acquisition or
new credit. The [official FASTA contract](https://www.uniprot.org/help/fasta-headers)
and [CC BY 4.0 data statement](https://rest.uniprot.org/help/license) were reviewed
on 2026-10-06; the alternative-isoform header carries no canonical PE/SV fields.

Development SWISS-MODEL Repository access retains the full unfiltered response,
native provider/target/alignment context, original retrieval time/hash and separate
API/query/creation/release dates. Resource credit uses Bienert et al. (2017),
[doi:10.1093/nar/gkw1132](https://doi.org/10.1093/nar/gkw1132), and the provider-requested
method citation, Waterhouse et al. (2018),
[doi:10.1093/nar/gky427](https://doi.org/10.1093/nar/gky427), verified against the
[official help](https://swissmodel.expasy.org/docs/repository_help) on 2026-10-06.
Neither is a primary citation for each PDB/template entry. Linked publications are
unqueried; metadata/model/sequence revisions remain gaps. Mapping saved responses
creates no new access or credit. Data follow the provider's CC BY-SA 4.0 statement,
with separate parent PDB/UniProt and article rights.

Development AmyPro access retains the whole export, original entry selection,
time/hash, native entry-level PubMed pointers and the Varadi et al. resource citation
(doi:10.1093/nar/gkx950). Export/sequence revisions and per-region method/publication
support remain gaps. Mapping saved entries queries no linked resource or new credit;
the article licence is separate from unstated database-export reuse rights.

Development direct IntAct access retains original query/page/count/byte identity,
native publication pointers and dataset attribution. Service versions are not
interaction revisions; the underlying publication/method metadata and participant
sequence revisions remain explicit gaps. Fixture/archive replay retains original
scope and times without new remote credit. Native MITAB data follows the
[IntAct CC BY 4.0 statement](https://www.imexconsortium.org/about/#licence), separately
from software and linked article rights. Existing UniProt interaction access remains
attributed to UniProt; a provider pointer does not establish separate IntAct access.

The application owns the Ackredit session:

```python
import ackredit
import sabueso

with ackredit.session("my knowledge workflow"):
    with ackredit.capture("workflow") as workflow:
        identity = sabueso.compose_packet(identity_query, card)
        literature = sabueso.compose_packet(literature_query, card)

result_records = [identity.attribution, literature.attribution]
workflow_references = workflow.attribution.to_dict()
```

`card` and both queries are supplied by the application. Each completed composition
gets a record, including resources reused by the preceding result. The application's
workflow collects their union. An optional `sabueso.attribution()` collector retains
records from several compositions. Nested collectors retain their contained
results, and the enclosing context retains those results too. No isolated component
session is created. Composition inside `knowledge_packet` uses the same adapter.

Each record carries:

- `format: sabueso.packet_attribution@1`: a provisional local record for this pilot;
- the packet snapshot, original producer version and its runtime-metadata basis;
- `scope`: pinned statement/relationship support, including conflicts and both legs
  of derived relationships;
- `resources`: source-record identities, explicitly unstated versions as `null`,
  original retrieval/acquisition metadata and contextual uses;
- `bibliography` and `bibliography_gaps`: declared descriptions and missing records;
- `provider`: status, original Ackredit version and detached provider attribution.

`packet.attribution` and a collector's `run.records` return independent copies.
Save them beside the corresponding packets:

```python
import json
from pathlib import Path

Path("result.attribution.json").write_text(json.dumps(result_records[0], indent=2))

saved = json.loads(Path("result.attribution.json").read_text())
original = ackredit.Attribution.from_dict(saved["provider"]["attribution"])
references = original.report(format="csl-json")
text = original.report(format="text")
```

Reading the saved JSON or packet adds no credit. Ackredit's detached reader renders
original records without new registration, source requests or DOI enrichment. Do
not substitute the reader's current version or a current card head for saved pins.
In a source checkout, runtime package metadata can be stale; use an installed
candidate when exact producer-version evidence matters.
The knowledge store and `packet.to_dict()` retain scientific payloads only: a packet
loaded from them has `attribution is None`. Retain and read the original JSON sidecar
alongside it; never manufacture execution attribution while loading saved knowledge.

## Source acquisition

`resolve` and `refresh_card` retain `card.acquisition_trace` and
`resolution.acquisition_trace`. A failed resolution returning no card still has a
trace on its resolution; an escaping exception retains `error.acquisition_trace`.
`knowledge_packet` attaches its intake trace to `packet.acquisition_trace`.
`compose_packet` reads existing knowledge and makes no new acquisition claim.

```python
with ackredit.session("my source workflow"):
    with ackredit.capture("workflow") as workflow:
        card, resolution = sabueso.resolve("P60174")

trace = resolution.acquisition_trace
Path("acquisition.trace.json").write_text(json.dumps(trace, indent=2))
```

These traces observe the built-in clients listed in {doc}`source_coverage`.
The corresponding public source envelopes add `acquisition_trace` while retaining
the original raw `record`. Sources outside that declared boundary and custom clients
are explicitly unobserved. A source not asked has no event or
credit. `sabueso.attribution()` can collect the same events as `run.acquisitions`,
separately from completed packet composition in `run.records`.

Each event keeps the query, original producer and source versions, observed route,
original retrieval time, response identity and outcome. Entry versions, service
versions and database releases have distinct bases. Archive reuse/replay retains
original response hashes and retrieval references with no new network attempt.
Fixture reads are local fixture access. Empty answers, actual HTTP absence,
unavailable fixtures, unqueried offline requests and failures remain distinct;
partial failed batches retain their completed transport observations.

Completed access contributes contextual uses and references to the application's
Ackredit capture, including evaluated-empty answers and local replay. A failed or
unqueried access remains in the host trace with provider status `not_attempted`;
it does not claim successful acquisition. Provider or recording failures diagnose
explicit gaps while preserving the scientific return or exception.

Save original JSON beside the scientific objects. The provisional local formats
`sabueso.acquisition_trace@1` and `sabueso.source_acquisition@1` are separate from
card and packet schemas. Payload-only saved readers have `acquisition_trace is None`
and add no execution credit. There is no implicit persistence. MOLI owns future
ProjectRecord/Recorda correlation, routing and recording policy; this local slice
does not establish a complete project record.

## References cited by ChEMBL indications (development)

Built-in `get_indications` and the disease builder's `indications_for` query now contribute the references
ChEMBL declares to the enclosing Ackredit workflow. These include trial-registry
pointers, regulatory labels and classifications. Sabueso preserves native reference
types, identifiers and URLs, including grouped identifiers, without following them.
They carry the role `source_cited_reference`: ChEMBL was consulted; the referenced
target was not consulted by that operation.

`indication_reference_context` in each acquisition record keeps the exact indication,
molecule and disease IDs, page/query/hash and every reference occurrence. Fixtures
retain the original decoded result basis. Duplicate bibliography entries share one
citation, while occurrences from different rows or query pages remain distinct.
References from received pages survive a subsequent failure. Archive reuse/replay
keeps original times, versions and reference forms.

Missing titles, authors, dates and reference-target access remain explicit gaps.
These incomplete citations can be exported from saved portable attribution without
requests or new credit. They do not establish efficacy, approval, target permissions
or a complete bibliography of underlying studies. Scientific card data is unchanged.

## MONDO identity queries (development)

Built-in MONDO term and stated-equivalence queries now retain the normalized
identifier, native OBO data-version and file identity, checksum basis and original
index origin. The source's `MONDO:equivalentTo` statements establish identity;
names and related cross-references do not. Definition and imported-resource pointers
are declared context, without querying their publications or linked terminologies.

The same downloaded index can answer many queries. `memory` means local index
reuse; `mixed` can combine a current release-selector lookup with that old index.
Original download receipts remain distinct from current requests/network counts.
Archive reuse/replay keeps the original response time, hashes and references.
A pre-existing index without a receipt explicitly lacks its original time/origin.

Fixture subsets do not establish absence from the whole release. Empty equivalence
lookups, missing fixture terms/files, offline-unqueried access and download/checksum
failures retain separate outcomes. Non-OBO and invalid UTF-8 documents are connector
failures and receive no completed query credit. Source results and runtime events
preserve the same original release response time. A pre-existing index without a
receipt retains the legacy client-clock fallback in its source result, while the
trace explicitly reports an unknown original retrieval time.

Completed queries contribute MONDO's resource description to the enclosing Ackredit
capture, including evaluated-empty queries and index reuse. Direct disease
resolution retains its original card/resolution trace and exact card pin. Save that
JSON beside the scientific objects; saved readers add no credit.

## Disease associations and deck builds (development)

Open Targets `associations` and `targets` record raw/normalized identifiers,
GraphQL page queries and hashes, native data versions, source order and returned/
total counts. A source-row limit differs from a built-card limit. Completed pages
remain visible if a later page fails; mixed versions/counts are refused rather than
merged into a scientific result. Null entities are evaluated absence; missing
fields, GraphQL errors and malformed documents are failures, not absence.

Orphanet `associations` and `genes` retain the exact XML file identity, its header
date and original index receipt. Memory/archive reuse keeps the original scientific
and runtime retrieval time. Bare older indexes explicitly lack origins. Lookups
cover SwissProt-indexed associations, not all native genes or inherited disease
classification; fixture subsets and missing files remain scoped. Native validation
pointers survive without claiming access to their publications.

Completed queries contribute resource bibliography to Ackredit. Open Targets uses
its [recommended publication](https://platform-docs.opentargets.org/citation.md),
[doi:10.1093/nar/gkae1128](https://doi.org/10.1093/nar/gkae1128), with all 32 authors,
2025 issue date and journal/pages from
[primary public metadata](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1093/nar/gkae1128&format=json&resultType=core).
Orphadata uses its [recommended dataset citation](https://www.orphadata.com/faq/),
with the native XML date retained as version. Copyright 1999 is not an invented
publication date. Underlying association/validation study metadata remains an
explicit bibliography gap; no runtime publication lookup is added.

`disease_targets` and `disease_drugs` expose detached traces with original disease
input/support pins, final deck/member pins, executing version/times, rule/limit,
source statuses and exclusions. Stored disease cards do not create fresh MONDO
access, and custom clients remain unobserved. Save traces beside science;
payload-only readers acquire/credit nothing. Development DISEASES, ClinVar and MedGen
queries also retain original source access. Complete underlying study bibliography
and shared MOLI recording guarantees remain pending.

DISEASES preserves publication dates and original file/index origins per channel;
knowledge, experiments and text mining retain their own score and reference scope.
Older disk indexes declare unknown original times. ClinVar preserves per-gene
search totals/caps, returned variant UID/accession versions and classification
conflicts. MedGen preserves source-stated concept/UID pairs; ambiguous identity
and capped searches fail explicitly. Both retain NCBI page queries, hashes and
original archive times, with build versus database-last-update version bases.
Unavailable fixtures and invalid answers are distinct from evaluated absence.
Recorded request identities exclude personal API keys.

Resource bibliography uses [DISEASES's recommended description](https://diseases.jensenlab.org/cgi/About),
[doi:10.1093/database/baac019](https://doi.org/10.1093/database/baac019),
with all four authors and native 2022 journal metadata;
[ClinVar's recommended original paper](https://www.ncbi.nlm.nih.gov/clinvar/docs/faq/),
[doi:10.1093/nar/gkt1113](https://doi.org/10.1093/nar/gkt1113), with all seven authors
in the initials stated by NCBI; and [MedGen's recommended resource citation](https://www.ncbi.nlm.nih.gov/medgen/docs/faq/),
with its 2012 start year, separate from query/update dates. These descriptions do
not establish access to the underlying studies, ClinVar submissions or terminology
publications; those remain explicit bibliography gaps. No DOI enrichment runs at runtime.

## Structural queries and citations

A built-in RCSB lookup records the normalized PDB identifiers and GraphQL request
identities. A batch is one logical acquisition event with `entries` and
`completed_ids`; its `requests` include every chunk, retry and individual or
instance-field fallback. Per-entry outcomes retain received, partial, empty and
failed results without treating a failed entry as acquired. An empty identifier
list is `not_queried`; a missing fixture is `unavailable`. A mixed batch is `partial`
and credits only its completed entries, with failed entries retained in context.

RCSB's native `major_revision`, `minor_revision` and `revision_date` are retained
when stated. Complete entry revisions use `entry_revision`; a batch reports
`per_entry_revision`. Missing revisions remain `not_stated`, with any supplied date
retained as partial metadata. These are entry revisions, never a global database
release: the public RCSB envelope's `version` remains `null`. Archive reuse/replay
retains original revisions, citations, retrieval times and response hashes.
The GraphQL query also requests `rcsb_authors` for primary citations; existing raw
records are returned without tracing edits. Native field names are documented in
RCSB's [data migration guide](https://data.rcsb.org/migration-guide.html).

Completed structural intake credits the RCSB description and each source-stated
primary publication, including DOI/PubMed identifiers, title, authors, year and
journal when supplied. Missing citation metadata is an explicit bibliography gap;
no runtime lookup fills it. Identical citation metadata reuses one reference.
Different source-stated forms retain distinct metadata-based identifiers so that
partial or changed references cannot overwrite earlier ones in the same workflow.
The original per-entry metadata remains in the trace. A structure packet's stored
support credits the RCSB description; save the intake or enclosing workflow record
to retain its original primary-publication references as well.

## AlphaFold DB models (since 0.13.0)

`alphafold.get_prediction` retains the protein query and native per-record model
identifiers, versions, original response/archive hashes and retrieval times.
Empty model lists, HTTP absence, unavailable fixtures, unqueried offline access and
failures stay distinct. Unexpected non-list responses do not claim completed-model
credit. Partly invalid lists retain received subsets while the original public
processing exception escapes with its trace.

`latestVersion` belongs to each source record. Missing values remain unknown even
when `allVersions` lists past versions; those historical models were not consulted.
Isoform/fragment accessions, ranges, checksums, dates and native identifier forms
remain declared context. Repeated model ids keep separate indexed versions.
Model and sequence versions never become a global database release or an experimental
structure revision. Counts measure returned source records, not mapped relationships.

Declared tools/providers and artifact URLs do not claim a local prediction execution,
additional source access or coordinate/PAE/MSA downloads. The three recommended
database/background papers retain `resource_description` roles; Sabueso alone
receives the query's `executed_software` role. Those papers do not prove each model's
method or replace missing model-specific method/provider citations. No runtime
bibliography lookup fills the gap. Scientific mappings and the separation of
experimental/predicted structures remain unchanged.

Card and refresh traces name exact final pins. Persist original JSON sidecars
explicitly; saved card readers, prediction views and citation rendering add no
new acquisition or execution credit.

## InterPro family-site residues (since 0.13.0)

`interpro.get_site_residues` observes the existing protein-scoped site-residue
query. Native signature keys/accessions, member-database declarations, locations
and fragments retain their source scope. Counts mean returned signature records,
not mapped family sites. The source provides the positions; Sabueso runs no
alignment, InterProScan or member-database analysis in this operation.

`InterPro-Version` and fixture `version` retain distinct header/fixture release
bases. Missing versions remain unknown; member signatures and queried UniProt
accessions do not establish additional releases or direct provider access.
Archive reuse/replay retains original versions, response identities and retrieval
times. Empty bodies/objects and HTTP 204, HTTP absence, unavailable fixtures,
unqueried offline access and failures remain distinct. An empty answer cannot
distinguish an unknown accession from one with no stated sites. Unexpected shapes
receive no invented completed annotation credit; partial maps retain actual subsets.

The InterPro resource-description citation is separate from missing member,
signature and site citations. Source declaration does not establish rights to all
member resources. Scientific cards/mappings/schema remain unchanged. Persist the
original runtime sidecars; saved readers and bibliography rendering add no credit.

## PDBe-KB aggregate queries (since 0.13.0)

`pdbe_kb.get_ligand_sites` and `pdbe_kb.get_interface_residues` retain separate
protein-scoped queries, original retrieval times, response identities, archive
reuse/replay and retries. Completed empty answers and HTTP absence remain distinct
from unavailable fixtures, offline unqueried access and failures. Direct client
methods keep their original scientific envelopes; public functions expose the
detached record in `acquisition_trace`, and card/refresh operations keep their pins.

Source versions remain unstated. The trace keeps native group identifiers and
response indices, numbering kinds and distinct listed/mapped/interacting PDB
references, including original entity/chain forms. These are PDBe-KB statements;
they do not claim direct access to UniProt, PDB entries, PISA or other providers.
The group count is a source response count, not mapped relationships or validated
identities. Full original scientific records remain in the source response/card.
An omitted/null aggregate data field has an unknown count, distinct from a returned
empty record/list under the existing client contract.

The resource-description citation is separate from underlying structure and
annotation method/provider publications, whose missing metadata remains explicit.
No extra bibliography request is made. Save original JSON sidecars explicitly;
loading saved cards, rendering citations and reading ligand/interface views add
no new acquisition or execution credit.

## Chemical identity queries (since 0.13.0)

CCD component batches and UniChem's InChIKey/source-id lookups retain their original
queries, POST identities, response hashes, retrieval times, retries and archive
reuse/replay. CCD batches retain an outcome for each requested component. A missing
fixture is unavailable, not a source-empty answer; mixed batches credit completed
access only. Received components before a later GraphQL or fixture read failure
remain partial while the original exception escapes.

Source versions remain `not_stated`. CCD release status/dates and UniChem compound
ids do not prove release versions. UniChem's linked source records are retained as
its statements; their presence does not establish direct access to those databases.
The trace states the client's existing first-returned-compound selection basis.
Original identity and source-selection behavior are unchanged.

`resolve_molecule_card` retains card/resolution traces. `ligand_deck` retains
`deck.acquisition_trace`, including its native snapshot id, result card pins and
input protein pin. Save the original JSON beside the scientific objects, just as
for a protein card:

```python
with ackredit.session("ligand intake"):
    deck = sabueso.ligand_deck(protein_card, unichem=True)

Path("ligands.acquisition.json").write_text(
    json.dumps(deck.acquisition_trace, indent=2)
)
```

`protein_card` is supplied by the application. Payload-only saved decks have no
acquisition trace; ordinary deck operations create no trace or credit. Resource
descriptions cite CCD and its RCSB distribution service, and UniChem itself, without
claiming experimental primary citations or access to UniChem's linked providers.

## ChEMBL queries (since 0.13.0)

Built-in bioactivity, assay-activity, molecule and indication operations retain
normalized queries, pages and chunks, source totals/caps, transport retries and
native document citations. Public `get_*` envelopes retain the original raw record
and add the detached acquisition trace. A failure after received content pages keeps
those pages and their hashes in a `partial` event; the scientific API still raises
its original exception. Credit covers the received subset, with the failed requests
retained in context. Empty answers, unavailable fixture datasets and unqueried
logical batches remain distinct.

`source_version.origin` distinguishes a fetched status response, a fixture and the
existing client's release cache. Its scope is explicitly
`client_reported_release_not_verified_per_page`; cached status metadata cannot prove
the release of each archived or live page. Archive reuse/replay retains original
retrieval times and response identities without new network attempts. ChEMBL's
native document metadata contributes primary citations, with missing authors and
other fields left unknown. Original readers add no execution credit.

## PubChem queries (since 0.13.0)

Compound property lookups, structure matches (SMILES/InChI) and BioAssay target
queries automatically retain detached traces. Public `get_compound`,
`get_structure_match` and `get_assays` envelopes keep their raw scientific records.
Their traces preserve queries, POST-body hashes, received response hashes, retries,
original retrieval times and archive reuse/replay without new network attempts.

BioAssay additionally records summary/compound batches, retained/total target-row
counts, the row-order rule and caps. Native assay `Version`, `Revision` and
`LastDataChange` are preserved per received summary. They do not describe a global
PubChem release or prove the version of every target row. Compound and structure
responses without versions explicitly say `not_stated`.

A failing later batch retains a `partial` event with the completed responses and
terminal outcome while the original exception still escapes. Its count means
received target rows before completion. Empty responses, HTTP absence, rejected
structure input, missing fixtures and offline unqueried access remain distinct.
Rejected input adds no completed-data-access credit.

PubChem's resource-description citation and the measurements' PubMed pointers have
different roles. Unknown publication metadata remains a bibliography gap; no lookup
fills it. Source-stated depositor names/ids are retained, but do not claim those
databases were consulted or their citations recovered.
Pointer citations retain separate content-based identities, preserving a fuller
publication citation already credited by the host under the original PubMed id.
Save the original trace or
workflow attribution to retain these references; payload-only readers add no credit.

```python
from sabueso.tools.db.pubchem import FixturePubChemClient, get_compound

with ackredit.session("compound lookup"):
    answer = get_compound("5978", client=FixturePubChemClient("temp_data"))
    trace = answer["acquisition_trace"]
```

## BindingDB queries (since 0.13.0)

REST, saved fixtures and installed-mirror affinity queries automatically retain
detached traces through `get_affinities` and card acquisition. They record the
accession, cutoff, record limit/order, retained/total counts, native response hashes,
retries and original DOI/PubMed pointers. Archive reuse/replay preserves original
retrieval times and identities without new network attempts.

REST and fixtures do not declare a global release. A mirror query records
`access: mirror`, its installed monthly release and original manifest with URL,
checksum and installation time. These describe the installed release manifest;
they do not prove the live service's version or independently verify the index at
every read. The client's retrieval time is its installation time; event start/end
times identify the query. Query tracing does not cover mirror installation/update.

The cutoff is a `{value, unit}` quantity with its application basis. REST receives
it as a query; the mirror applies it locally. The existing fixture client does not
reapply the cutoff to its frozen response, and the trace states that explicitly.
Scientific records and cutoff selection remain unchanged.

Decoded empty answers, unavailable fixtures, unqueried offline access, failures
and data received before a processing failure are distinct. An HTTP 404 remains a
connector failure under BindingDB's existing client contract. The documented
empty-string forms are handled by the 0.13.0 fix in
[Sabueso #114](https://github.com/uibcdf/sabueso/issues/114): an exactly empty HTTP
200 body or a JSON empty string is an evaluated-empty answer, retaining the client's
`RecordNotFoundError` outcome and original receipt. Unexpected payloads and malformed
nonempty bodies remain failures. The shared transport accepts an empty body only
when this source opts in; other sources retain their existing JSON checks.

BindingDB's resource-description paper and measurement DOI/PubMed pointers have
separate roles. Incomplete pointers retain their own metadata-based identities,
preserving fuller host citations and differing source forms. Missing bibliographic
metadata stays unknown. Mirror-declared origins such as ChEMBL are declarations,
not claims of direct access to those databases. REST origins remain unstated.
Save the original acquisition/workflow record; payload-only readers add no credit.

## Dependency and failures

Ackredit is a required runtime dependency. Importing Sabueso and entering an empty
collector do not load it; composition and completed observed source access
automatically load it and credit their respective uses.
A missing or broken provider in an invalid installation produces
`SABUESO-W-ATTRIBUTION-001`, marks attribution
`failed`, and preserves the completed packet and host record. Missing stored support
marks `support_status: unavailable` and skips provider credit. These statuses never
mean that missing references were successfully collected. A provider failure after
some credits can leave a partial enclosing workflow; inspect the result records and
diagnostics before claiming completeness.

The adapter uses a lazy required import, without DepDigest's optional-library path.
This integration does not enable import hooks, journals, automatic DOI enrichment
or reminders. Ackredit **>=0.9.0** supplies the published portable contract
`ackredit.attribution@1`. Runtime CI installs public Conda dependencies; the receiving
lanes pin public Ackredit 0.9.0/py_0 on Python 3.11–3.14 and run the unchanged
integration tests and public workflow outside both checkouts. Provider delivery
issues [#22](https://github.com/uibcdf/ackredit/issues/22),
[#75](https://github.com/uibcdf/ackredit/issues/75) and
[#80](https://github.com/uibcdf/ackredit/issues/80) are closed. Sabueso 0.13.0 passes its own exact-artifact OS/minor matrix and clean
public installation, with the full receipt in the repository's
`devtools/conda-build/receipts/sabueso_0.13.0_public_2026-10-05.json`.

## Scope and bibliography

The packet adapter observes **composition over stored statements**. The separate
acquisition adapter observes the bounded clients above. Arbitrary card views,
other sources and further result types remain open in
[Sabueso #108](https://github.com/uibcdf/sabueso/issues/108). Neither adapter infers
a new download from stored card provenance or a failed request.

Full and index packets use the same stored-support closure as packet terms. Unused
statements receive no credit. Exact unrecorded mapping lineage cannot be recovered:
disease grouping includes broader stored MONDO/MedGen identity and hierarchy context.
The record says so. A resource's version is its source-record version, not an inferred
global database release.

The offline resource-description declarations were verified on 2026-10-02/04/05:

- MONDO's [official resource page](https://mondo.monarchinitiative.org/) links
  *Mondo: integrating disease terminology across communities*, DOI
  `10.1093/genetics/iyaf215`. [Europe PMC's public core metadata](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:41052288%20AND%20SRC:MED&format=json&resultType=core)
  supplies the full returned 115-author list and Genetics 232/4, iyaf215, issue year
  2026 (first online in 2025). This is resource-description metadata, not a citation
  for every imported term or an additional runtime article lookup.

- InterPro's [official resource references](https://www.ebi.ac.uk/training/online/courses/interpro-functional-and-structural-analysis/references/)
  and [publisher metadata](https://api.crossref.org/works/10.1093/nar/gkae1082)
  verify *InterPro: the protein sequence classification resource in 2025*, all 34
  authors, Nucleic Acids Research 53/D1 D444-D456, DOI
  `10.1093/nar/gkae1082`. Its issue year is 2025 (online in 2024).
- AlphaFold's [official citation guidance](https://www.ebi.ac.uk/training/online/courses/alphafold/accessing-and-predicting-protein-structures-with-alphafold/how-to-cite-alphafold/)
  recommends the database papers `10.1093/nar/gkad1011` and `10.1093/nar/gkab1061`,
  and the background method paper `10.1038/s41586-021-03819-2`.
  Publisher-deposited Crossref metadata supplies the full author lists and issue
  dates: [2024 database description](https://api.crossref.org/works/10.1093/nar/gkad1011)
  (23 authors, 52/D1, D368–D375), [original database description](https://api.crossref.org/works/10.1093/nar/gkab1061)
  (27 authors, 2022, 50/D1, D439–D444) and [method background](https://api.crossref.org/works/10.1038/s41586-021-03819-2)
  (34 authors, 2021, 596/7873, 583–589). The database papers' issue years differ
  from their online publication years (2023 and 2021). They do not establish
  the method of every model or a prediction execution by Sabueso.
- PDBe-KB's [resource citation guidance](https://www.ebi.ac.uk/pdbe/pdbe-kb)
  recommends *PDBe-KB: collaboratively defining the biological context of structural
  data*, DOI `10.1093/nar/gkab988`. The [original article](https://academic.oup.com/nar/article/50/D1/D534/6424755)
  provides its consortium author and issue metadata: 2022, 50/D1, D534–D542,
  distinct from online publication in 2021. This description does not replace
  underlying structure or method/provider citations.
- CCD's [official description](https://www.wwpdb.org/data/ccd) cites
  *The chemical component dictionary: complete descriptions of constituent
  molecules in experimentally determined 3D macromolecules in the Protein Data Bank*,
  DOI `10.1093/bioinformatics/btu789`. The six authors and issue metadata come from
  [its publication record](https://pubmed.ncbi.nlm.nih.gov/25540181/): 2015, 31(8),
  1274–1278, distinct from the 2014 online publication date. The RCSB description
  below separately describes the API distributing the CCD records.
- UniChem's [original resource article](https://pmc.ncbi.nlm.nih.gov/articles/PMC3616875/),
  *UniChem: a unified chemical structure cross-referencing and identifier tracking
  system*, and [publication record](https://pubmed.ncbi.nlm.nih.gov/23317286/)
  provide its ten authors, DOI `10.1186/1758-2946-5-3` and issue metadata (2013, 5(1), 3).
- UniProt's [recommended citation](https://www.uniprot.org/help/publications), with
  complete metadata from the [original paper](https://academic.oup.com/nar/article/53/D1/D609/7902999):
  *UniProt: the Universal Protein Knowledgebase in 2025*, DOI `10.1093/nar/gkae1010`.
- Europe PMC's *Europe PMC in 2023*, with the full 22-author list and metadata from
  [the publication record](https://pubmed.ncbi.nlm.nih.gov/37994696/), DOI
  `10.1093/nar/gkad1085`. Its bibliographic year is 2024; the title is not its year.
- RCSB's [citation policy](https://www.rcsb.org/pages/policies) recommends
  *Updated resources for exploring experimentally-determined PDB structures and
  Computed Structure Models at the RCSB Protein Data Bank*, DOI
  `10.1093/nar/gkae1091`. The full 51-author metadata comes from the
  [publisher-deposited Crossref record](https://api.crossref.org/works/10.1093/nar/gkae1091).
  Its bibliographic issue year is 2025, distinct from its online publication date.
- ChEMBL's [recommended citation](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/general-questions)
  lists the 20 authors and issue metadata of *The ChEMBL Database in 2023: a drug
  discovery platform spanning multiple bioactivity data types and time periods*,
  DOI `10.1093/nar/gkad1004`, bibliographic year 2024. This resource description is
  separate from the original publications cited by its measurements.
- Sabueso's software metadata comes from its `CITATION.cff`, using the project
  concept DOI and the executing package's version. A preceding release's version DOI
  is not attached to an unreleased checkout.
- PubChem's [citation guidelines](https://pubchem.ncbi.nlm.nih.gov/citations.html)
  recommend *PubChem 2025 update*, DOI `10.1093/nar/gkae1059`. Its 13-author list and
  volume/issue/pages come from the [original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11701573/).
  The bibliographic issue year is 2025, distinct from online publication in 2024.
  This description also covers the BioAssay resource; it does not replace the
  experimental publications identified in received target rows.
- BindingDB's [original resource article](https://www.bindingdb.org/rwd/bind/gkae1075.pdf),
  *BindingDB in 2024: a FAIR knowledgebase of protein-small molecule binding data*,
  provides its seven authors, DOI `10.1093/nar/gkae1075` and bibliographic issue
  metadata (2025, 53/D1, D1633-D1644). The title's year and online publication date
  differ from the issue year. It is separate from measurement DOI/PubMed pointers.

Other resource descriptions are explicit gaps. Target publications and annotation
providers also need their own citations; a service-description paper does not replace
them. No missing authors, dates or release identifiers are invented. Terms and
fragment reuse rights are answered separately by the terms report.

CSL-JSON, text and BibTeX preserve the corporate UniProt author. The published minimum includes the provider's correction for explicit CSL author objects
([Ackredit #78](https://github.com/uibcdf/ackredit/issues/78)); saved-reader regression
tests check corporate-name grouping and Europe PMC's personal names without new credit.

The complete runnable public workflow is in `examples/ackredit_pilot/`, using only
the frozen public HsTIM fixtures declared in `temp_data/NOTICE.md`.

Since 0.13.0, Sabueso also includes `examples/persisted_pipeline/`: independent
producer, reader and reuse processes retain full/index packets, an exact index-item
read, original extraction/article metadata and portable workflow attribution.
The reader verifies sidecar hashes and result bindings before rendering historical
citations; reading adds no credit. Reacquisition advances current heads while old
pins and original bibliography remain readable. A missing fixture stays unavailable,
without an external absence claim. The fragment is explicitly synthetic with unknown
reuse rights. This example uses the API delivered in 0.14.0; its manifest is local,
and shared ProjectRecord/Recorda integration remains open.

## ClinicalTrials.gov references (development)

Study and explicit reference queries retain native NCT identity, all continuation
pages, decoded response identities, original times, archive reuse, empty answers and
failures. The registry data timestamp, API protocol version and study update date
have distinct meanings; none supplies a publication year. Missing studies are
reported only after a complete query. An absent fixture answer is unavailable.

For references, query a stated NCT id explicitly:

```python
import ackredit
from sabueso.tools.db import clinicaltrials, europepmc

with ackredit.capture("registry-bibliography") as workflow:
    registry = clinicaltrials.get_study_references("NCT00123916")
    study = registry["record"]["studies"]["NCT00123916"]
    references = (
        study["protocolSection"].get("referencesModule", {}).get("references", [])
    )
    articles = [
        europepmc.get_article("pubmed:" + ref["pmid"])
        for ref in references
        if ref.get("pmid")
    ]

original = workflow.attribution.to_dict()
```

The registry query credits the registry and its declared references with separate
roles. It does not follow PMID, see-also, participant-data or retraction links.
The explicit Europe PMC queries above contribute their own observed metadata and
source versions. Returned collective authors remain literal names alongside personal
authors (#128). Missing citation metadata, article permissions and unqueried targets
remain explicit. Free citation text is preserved without identity extraction or
clinical interpretation. Save the original attribution alongside the source envelopes;
saved bibliography rendering adds no requests or credits. Card schema 0.3.12 and
existing clinical SourceAssertions are unchanged. Public release 0.13.0 does not
include this development extension.
