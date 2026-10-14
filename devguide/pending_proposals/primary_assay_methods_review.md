# Primary assay-method access review (#92/#132/#112)

The three documents shared by the complete public TcTIM/HsTIM ChEMBL fixtures
have verified bibliographic identities. None of the consulted routes supplied
their complete experimental methods. This is an access and source-scope review
prepared by Codex (agent) on 2026-10-14; scientist review remains pending.
No protocol, literature SourceAssertion or curation record is accepted.

The [review receipt](primary_assay_methods_review.json) records source hashes,
counts, assay identifiers and access outcomes. It is research evidence, not an
SDK acquisition trace or a new code qualification. The qualified
[located-source example receipt](located_source_review_checkpoint.json) and
earlier dossier receipts retain their original sources and results.

## Document identity and access

| Native document and primary references | Identity | Available material; methods status |
| --- | --- | --- |
| `CHEMBL1156043`; [PMID 19733070](https://pubmed.ncbi.nlm.nih.gov/19733070/); DOI `10.1016/j.bmcl.2009.08.055` | 2009 publication agrees with native metadata | [Author-institution record](https://www.uaeh.edu.mx/investigacion/productos/5359/) and [publisher preview](https://www.sciencedirect.com/science/article/abs/pii/S0960894X09011913) provide metadata/abstract; complete methods not obtained |
| `CHEMBL1629474`; [PMID 20889239](https://pubmed.ncbi.nlm.nih.gov/20889239/); DOI `10.1016/j.ejmech.2010.09.034` | 2010 publication agrees with native metadata | [Publisher record](https://www.sciencedirect.com/science/article/pii/S0223523410006823) and [RIQUIM institutional record](https://riquim.fq.edu.uy/items/show/2008) identify the article; the repository PDF delivers a library notice, not its text |
| `CHEMBL4431335`; [PMID 27503677](https://pubmed.ncbi.nlm.nih.gov/27503677/); DOI `10.1016/j.bmcl.2015.08.018` | Published in 2016, electronically published in 2015; the DOI year is consistent | [Publisher preview](https://www.sciencedirect.com/science/article/abs/pii/S0960894X15008422) provides abstract/acknowledgments, not experimental methods |

Browser challenges on two directly opened PubMed pages did not establish
bibliographic disagreement. Indexed primary metadata and the institutional/
publisher records verify the pointers. Metadata verification is separate from
verification of a delivered article body.

The RIQUIM file linked as full text is a one-page PDF of 29,389 bytes, SHA-256
`5918b075056be3a462cc2e7d0524b83d59ef036fd85a2d93a690c48344492c06`.
Local PDF text extraction and rendering confirm a notice referring the reader
to the library. It contains no article identity or methods. An HTTP success,
PDF extension and repository link label cannot establish full-text delivery.
The institutional rights statement permits private research/teaching; this
review establishes no public redistribution grant. No downloaded PDF, response
HTML, headers or other article material is added to public fixtures.

These public web consultations and three external native downloads are not
SDK-observed source operations. The author page and DOI redirect response also
remain metadata/navigation inputs, never experimental source text. Private
originals and hashes are retained locally; their presence does not establish
full-text SDK access, article revision, scientific extraction or human curation.

## Scope of the native activity inventory

The unchanged fixtures `temp_data/chembl/CHEMBL5834.json` (493 rows) and
`temp_data/chembl/CHEMBL4880.json` (36 rows) contain eleven distinct document
pointers in total. Their three shared documents account for **497 activity
rows and twelve distinct assays**. This is the complete stored fixture inventory,
not a new online response, a current source count, or the saved dossier's capped
card scope. Rows are source records, not independent experiments.

| Document | TcTIM stored rows and types | HsTIM stored rows and types | Distinct assays |
| --- | --- | --- | --- |
| `CHEMBL1156043` | 5: 4 IC50, 1 Kd | 4: 4 IC50 | 3 |
| `CHEMBL1629474` | 459: 454 Inhibition, 5 IC50 | 5: 5 Inhibition | 4 |
| `CHEMBL4431335` | 19: 16 Inhibition, 3 IC50 | 5: 5 Inhibition | 5 |

All twelve stored assay-parameter arrays are empty; variant metadata is null.
The native descriptions still retain useful partial context: incubation scope,
different fixed compound concentrations, and, for the 2016 document, a coupled
NADH/dehydrogenase readout. These are ChEMBL's descriptions. They do not provide
a verified complete primary protocol or establish that a coupled readout was
controlled for interference.

The source inventory distinguishes sixteen IC50 rows, 480 Inhibition rows and
one Kd row. The Kd label and a binding assay category do not establish whether
the value was experimentally measured or calculated; that requires the actual
source method. Fixed-dose inhibition is not an IC50. A greater-than qualifier
remains a bound, and missing variant metadata does not establish wild type.
Shared documents, compound identifiers, target assignment and compatible units
do not establish experimental equivalence or justify a selectivity ratio.

## Remaining work and intake boundary

Original methods are still needed for all three articles. Obtain them through
authorized institutional access, an author-supplied original or a legitimately
available source. Record article-specific rights separately from access rights;
access alone does not permit redistribution. Do not fill these gaps from another
organism's structural study, reviews, citing papers or reconstructed protocols.

For each acquired article, first verify the delivered body against the publication
identity and locate its Methods/supplementary material. Preserve the original
bytes, source, retrieval basis and actual revision basis where stated. A future
full-text intake under #92 must distinguish an article, abstract, redirect,
challenge, library notice and supplement rather than accepting a filename or
HTTP status as the article. This is an owner-local intake requirement, not a
claim that such an SDK route has been implemented.

Then inspect the stated constructs/mutations, assay versus preincubation scope,
substrates, concentrations, buffer, temperature, time, readout and controls.
Record which numbered compounds, tables and assays each statement actually
supports; do not map them by similar names. Separate biochemical inhibition,
binding and computed quantities. Agent readings remain drafts outside card
knowledge until their acquisition method and review are properly recorded.
Human review must precede a claim of scientist acceptance; Nextia retains
ownership of project interpretation and Evidence.

This bounded review closes bibliographic identification and records the access
gap. Experimental comparability and consumer usefulness remain open under
#132; #92 owns source-text intake and #112 coordinates delivery. The SDK, schemas,
cards, source fixtures and prior qualified scientific receipts are unchanged.
