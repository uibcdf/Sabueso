# Located primary-source review (#92/#132/#112)

A located mention alone is not a substantive source statement. The new independent
example `examples/user_journeys/literature_source_review.py` records two narrow,
actual structural statements from an already identified public article. It uses
existing curation and persistence APIs; no SDK API, card schema, source adapter,
scientific grouping or published artifact changes.

## Source and subject scope

Kontellas et al. (2025), *Triosephosphate isomerase from Fasciola hepatica:
high-resolution crystal structure as a drug target*, DOI
[10.1107/S2053230X25006454](https://doi.org/10.1107/S2053230X25006454), PMID 40832834,
[PMC12400196](https://pmc.ncbi.nlm.nih.gov/articles/PMC12400196/), states:

| Recorded statement | Original location | Explicit subject basis |
| --- | --- | --- |
| Human TPI structure PDB 2JK2 was used as the MoRDa molecular-replacement template for FhTPI | `sec2.4/p[1]` | The text names human TPI and 2JK2; the native UniProt P60174 card states `has_structure pdb:2JK2` |
| Human accession P60174 is included in the published multiple sequence alignment performed with Clustal Omega | `fig4/caption` | The caption names *H. sapiens* and its Swiss-Prot accession P60174 |

The complete unchanged public `fullTextXML` response was retrieved once on
2026-10-14. It has 78,100 bytes and SHA-256
`eff2c488e4b17ded8e30530b98ff949fdada1294329c957d26e6ab71945abfef`.
Its own native `license_ref` explicitly grants CC BY 4.0; attribution and delivery
are recorded in [NOTICE](../../temp_data/NOTICE.md) and the
[file decision](../sources/fixture_delivery.json). Service terms do not replace
article rights. Retrieval date/service version do not establish article revision.
The stored metadata fixture and the later full-text download have distinct origins.

`located_publication_subject_binding@1` reports those explicit identity bases;
it is an example-local finding, never a SourceAssertion. No similarity merge,
sequence alignment, residue correspondence, modeling or project Evidence is
performed. The article's parasite experiments are not human experiments; its
resolution or proposed inhibitory observations cannot be transferred to HsTIM.

## Curation, persistence and original execution

The curator is **Codex (agent)**. Scientist review remains **pending**. Existing
`Card.add_literature_claim` records each statement with topic, publication,
locator, quote and SourceAssertion. Each outcome is `not_compared`; recording a
claim does not establish its validity or human acceptance. `CurationStore` retains
the exact originals on rebuild, and `KnowledgeStore` pins baseline/curated/rebuilt
cards. Baseline source statements are retained unchanged.

Bare accessions in this native caption do not satisfy `literal_uniprot_mention@1`'s
explicit namespace/URL rule. The example never rewrites the source into a fake
namespace or relabels rule extraction as curation. It explicitly records agent
curation through the existing API. The example format is
`sabueso.located_source_review_example@1`, distinct from the historical dossier
formats and their original receipts.

Only fixture entry/article-metadata access has original SDK/Ackredit acquisition
sidecars. The external full-text download is a supplied public input, not an
SDK-observed full-text acquisition. Curation execution observation is explicitly
`not_observed`. Original runtime provenance, resource/article references and the
workflow union are retained without claiming additional executed upstream methods.

A separate reader needs no fixtures. It checks the original XML and fragment
locations, source-supported identity, exact card pins and original assertions,
curation records, saved claim/literature views, human rendering and attribution.
It never calls resolution, refresh, curation, claim/literature derivation or new
credit. Original reference exports cannot be overwritten after alteration.
Rehashed but scientifically or curatorially altered reports are rejected.

## Assay-protocol review outcome

The public native ChEMBL inputs `CHEMBL5834.json` and `CHEMBL4880.json` preserve
assay descriptions, parameters, variant metadata and document pointers. The
review found no complete comparable protocol in their assay-parameter arrays.
The one populated parameter set (CHEMBL5652684) contains disease vocabulary
`MONDO:0004992` and `cancer`, not assay conditions. Some descriptions include
individual durations; those do not provide complete substrate, construct,
concentration, temperature, readout and control scope.

The open article above is a structural study of a different organism, not the
primary protocol of the stored ChEMBL activities. Its Methods cannot fill those
assay gaps. No parameter is converted into an experimental condition, no missing
variant becomes wild type, and no matching identifier/unit establishes assay
comparability. Dossier `@2` remains an inspection of stored qualifiers, with
`experimental_protocol: not_curated` and comparability not established.

Next: inspect the actual activity-linked primary documents under their own rights
and subject scope, record explicit protocols where available, and obtain scientist
review of these source statements and dossier usefulness. Full-text SDK access,
automatic substantive extraction, mechanistic/selectivity inference, scientific
consumer acceptance and installed release delivery remain separate work. This
bounded route advances usable source knowledge without expanding Sabueso into
Discovery.

## Qualification

Thirteen new independent-process cases and 233 selected literature/curation,
article, dossier and fixture cases pass with Python 3.14 and twelve receptor
workers (31.97 seconds). All 6,299 full local-original cases pass in 200.22
seconds, with thirteen expected fixture warnings and fatal SQLite/unraisable
guards. Ruff, source registry, fixture delivery (51 repository / 37 protected),
dependency/governance, canonical-guide equality, Markdown targets and warning-fatal
Sphinx pass. Seven participant imports and editable metadata agree outside the
checkout. Exact-source hosted qualification is pending; earlier receipts remain
unchanged. This example is development
source qualification, not a published release or accepted scientist conclusion.
