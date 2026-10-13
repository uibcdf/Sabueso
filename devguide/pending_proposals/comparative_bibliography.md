# Verified comparative resource and pext descriptions (#108, #112)

Development adds three offline bibliographic records with scoped credit. They
describe resources or an upstream annotation method; none is a native entry's
primary study, proof of its release, Nextia Evidence or permission to reuse data.
Provider declarations and primary metadata were checked on 2026-10-13.

| Reference | Verified declaration and metadata | Scope |
| --- | --- | --- |
| Chen et al., Nature 625/7993, 92–100, DOI `10.1038/s41586-023-06045-0` | The provider's [accepted citation clarification](https://github.com/broadinstitute/gnomad-browser/issues/1832) identifies this flagship paper for current gnomAD, including v4 before its own publication. [PubMed](https://pubmed.ncbi.nlm.nih.gov/38057664/) gives all 47 byline authors, including the consortium, online publication 2023-12-06 and the 2024 journal issue. [Author correction](https://pubmed.ncbi.nlm.nih.gov/38225470/) is retained as a note. | Generic provider-recommended resource description; not a returned record's release/primary-study association. |
| GTEx Consortium, Science 369/6509, 1318–1330 (2020), DOI `10.1126/science.aaz1776` | The [GTEx downloads page](https://gtexportal.org/home/downloads/adult-gtex/) lists the consortium paper; the [primary author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC7737656/) displays its collective byline and v8 analysis scope. [PubMed metadata](https://pubmed.ncbi.nlm.nih.gov/32913098/) confirms its coordinates. | Resource description with a literal collective author. The paper's v8 analyses do not prove a queried v10 tissue row's revision or study. |
| Cummings et al., Nature 581/7809, 452–458 (2020), DOI `10.1038/s41586-020-2329-2` | The [provider's manuscript announcement](https://gnomad.broadinstitute.org/news/2020-05-the-gnomad-papers/) links this transcript-expression method; [primary metadata](https://pubmed.ncbi.nlm.nih.gov/32461655/) states 18 byline authors, including two collectives. The [provider's v4 pext announcement](https://gnomad.broadinstitute.org/news/2024-11-gnomad-v4-pext/) distinguishes newer GTEx v10 tracks from earlier v7 tracks. | Upstream pext method description. The original v7 study is not bound to a returned row or claimed as the method revision Sabueso executed. |

`comparative_bibliography.py` holds the curated records; resource descriptions
reuse the existing offline catalogue and keep API/portal references. Acquisition
credits `method_description` only for `gnomad_pext`, under
`pext_reference_scope@1`. Missing/failed access gets no completed-data credit.
Comparative execution attaches the description only to valid, represented gnomAD
`annotations.exon_usage_by_tissue` support. Variant-only fields, missing/misbound
assertions and foreign sources do not qualify. Each eligible use retains its exact
pin/assertion and original source-label/acquisition context. Repeated source,
packet and comparison use shares identical citation metadata in the workflow.

The scope explicitly states `method_execution=not_performed`, unknown native
method revision, no inferred native dataset binding and unestablished entry-study
membership. Sabueso reads supplied pext and executes its own named tissue rules;
it does not execute the upstream annotation pipeline. Source acquisition context
distinguishes native absent references from separately curated offline descriptions.
Specific variant/tissue/entry publications remain unqueried or undeclared, and
native revisions remain unknown. New records separate these gaps from the now
available method description. Historical records keep their original gaps.

The independent example reader accepts original records lacking method fields.
It verifies stored scope/credit/citation bindings and exports original metadata,
without calling today's catalogue, acquiring sources, deriving views or generating
credit. Genuine prechange `@3` bundles preserve original producers, files and
bibliography. The precommit comparison also preserves all three card pins and
complete scientific views/explanations from `8857190` exactly.

Local selected qualification passes 278 cases in 49.12 seconds with twelve
pytest-receptor workers and two deliberate fixture warnings. Fifteen added cases
cover scoped references, real source/provider credit, absent/failed access,
invalid stored support, complete collective-author exports and misbound method
sidecars. The full local-original offline checkpoint passes all 6,262 cases in
155.58 seconds, with thirteen expected fixture warnings and fatal SQLite lifetime
guards. Public fixtures, SourceAssertions,
scientific algorithms/card schemas and earlier receipts remain unchanged; no
scientific provider query is added. Public metadata pages were read during
development, not automatically by the SDK.

Published at `25f6163`; full remote qualification remains pending under the
[deferred block](deferred_ci.md). Installed public-Ackredit CI includes this module
and the persisted journey; all four receiving jobs pass. The
[publication snapshot](comparative_block_publication.json) records thirteen successful
CI jobs, queued macOS, pending coverage and passing exact-source governance.
Complete test-log summaries and CI capture verification remain pending. Published 0.14.0,
installed-artifact qualification and private/human consumer acceptance remain
separate. After the bounded bibliography slice, qualify the final block head and
return to the existing consumer routes (#132). Broader verified bibliography,
other result scopes and MOLI recording remain open under #108.
