# Located primary-source review (#92/#132/#112)

A located mention alone is not a substantive source statement. The new independent
example `examples/user_journeys/literature_source_review.py` prepares two narrow,
located structural readings for scientist review from an already identified public article. It uses
existing source and persistence APIs; no SDK API, card schema, source adapter,
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

## Draft status, persistence and original execution

The preparer is **Codex (agent)**. Scientist review remains **pending**. Neither
reading is entered into `literature.claims`, exported through `CurationStore` or
labelled `acquisition.method: curation`. The baseline card retains its original
UniProt SourceAssertions at an exact KnowledgeStore pin. A separate
`proposals.json` sidecar retains the proposed text, source fragment and locator.
A human may review those readings before using existing curation APIs under
their own identity; this example never supplies that acceptance.

The acquisition contract in [SCHEMA](../SCHEMA.md) and the 2026-10-01 decision
in [DECISIONS](../DECISIONS.md) distinguish human curation from extraction.
Initial `f08bdad` incorrectly used curation for agent-prepared readings despite
labelling scientist review pending. It is not a qualified scientific checkpoint;
its example-local `@1` bundles are refused by the corrected reader and retained
only as diagnostic originals. This correction uses
`sabueso.located_source_review_example@2`; existing scientific dossier formats
and their qualified receipts remain unchanged.

Bare accessions in the native caption do not satisfy `literal_uniprot_mention@1`'s
explicit namespace/URL rule. The example never rewrites the source into a fake
namespace, invents a model version or presents a fixed reading as an executed
scientific extraction rule. Broader substantive extraction/intake remains #92
work; the existing SDK extraction store accepts only its delivered literal rule.

Only fixture entry/article-metadata access has original SDK/Ackredit acquisition
sidecars. The external full-text download is a supplied public input, not an
SDK-observed full-text acquisition. Draft preparation execution observation is
explicitly `not_observed`. Original runtime provenance, resource/article
references and the workflow union are retained without claiming additional
executed upstream methods.

A separate reader needs no fixtures. It checks the original XML and fragment
locations, source-supported identity, original card pin/assertion membership,
draft sidecar, human rendering and attribution. It refuses a card with imported
literature claims or curations. It never calls resolution, refresh, curation,
claim/literature derivation or new credit. Original reference exports cannot be
overwritten after alteration. Rehashed drafts that claim acceptance or alter
scientific/provenance content are rejected.

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

Fourteen independent-process cases cover the corrected draft route, including
explicit rejection of the unqualified `@1` curation format. The 234 selected
cases pass in 29.26 seconds; all 6,300 local-original cases pass in 170.25 seconds
with thirteen expected fixture warnings, twelve receptor workers and fatal
SQLite/unraisable guards. Ruff, source registry, fixture delivery, dependency/
governance, canonical-guide equality, links and warning-fatal Sphinx pass.
Corrected exact-source hosted qualification is pending; older qualified source
receipts remain unchanged. This is development example qualification, not new
curated knowledge, published release delivery or an accepted scientist conclusion.
