# Test fixtures: sources, versions and licences

This directory contains **frozen public database responses** and compatibility
records built from them. Published fixtures are redistributed with Sabueso so its
offline tests are reproducible. Development artifacts explicitly marked local and
unreleased below have not been qualified for public redistribution; their exact
file set and applicable terms require review before a public repository checkpoint.
Public acquisition alone does not qualify redistribution. Each source's data keeps
its own terms below.

Sabueso's code is MIT licensed (`LICENSE`). That licence does **not** apply to these
files: each keeps the licence of the source it came from, listed below. A repository
holding both is a collection of separately licensed works.

These files are not included in the Python distribution (the wheel and sdist ship only
the `sabueso` package). Published fixtures are distributed with the git repository;
the local unreleased qualification artifacts are a separate delivery scope.

Where a fixture was trimmed to the fields the tests need, or wrapped in a small envelope
recording the release and retrieval time, it is a modified copy. It is redistributed
under the source's licence, and the modification is stated here and in the client that
wrote it (`sabueso/tools/db/`, `sabueso/resolver/`).

## Reviewed recovery inputs

The reviewed recovery file inventory is
[`devguide/sources/fixture_delivery.json`](../devguide/sources/fixture_delivery.json).
It records 49 repository-delivery inputs and 37 protected local-only originals,
with exact byte identities and file-specific decisions. `.gitignore` protects
the local input directories; `python tools/fixture_delivery.py --check` rejects
their inclusion in the Git index and checks the reviewed repository inputs.
Local originals retain their native content and notices. Their native regression
modules require pytest's explicit `--local-source-inputs` option; ordinary public
CI does not require or distribute those originals. Input-specific PRIDE and
OmniPath decisions do not license other records from those resources. DisProt's
original response remains local pending embedded-quotation rights qualification.
See [fixture delivery](../devguide/sources/FIXTURE_DELIVERY.md) for both test scopes.

## Local unreleased MEROPS qualification artifacts

The development `merops/` files below are held locally for reader qualification;
public fixture/repository redistribution is **not qualified**. This local recovery
has not been committed, pushed or packaged. MEROPS declares its complete database
content the Library under GNU Library GPL, with no stated version. The
[historical Library GPL](https://www.gnu.org/licenses/old-licenses/lgpl-2.0.txt)
section 0 distinguishes running a tool from distributing database-derived content;
[GNU GPL 3 section 2](https://www.gnu.org/licenses/gpl-3.0.txt), incorporated by the
currently linked LGPL, distinguishes unshared work from conveying it. These support
local unshared qualification; they do not select a provider version or qualify a
public derived dataset. Keep data and source notices separate from Sabueso's MIT code.

- `merops/accession_assignments.tsv`: full unchanged public
  [dnld_list export](https://ftp.ebi.ac.uk/pub/databases/merops/current_release/dnld_list.txt),
  2914699 bytes, SHA-256
  `9758b658cd7d5f043311d5babf439590baf88b97623ad2a5d42e7e6827abc711`.
  Original public 2026-10-06 probe, exact time unknown (`null`); live GET on
  2026-10-07 matches every byte. All 116744 CRLF lines remain, including three
  displaced four-column rows and the literal quoted accession at line 108853.
  Export/assignment/sequence revisions are unstated. No data modification.
- `merops/availability.html`: unchanged public
  [provider statement](https://www.ebi.ac.uk/merops/about/availability.shtml),
  received 2026-10-07, 7930 bytes, SHA-256
  `caf8b691977e408f0814fd52dcc96c199aed93b7c9b12a7b0244d87e3e1ffacc`.
  Includes source copyright and whole-database Library declaration; no modification.
- `merops/GNU-LIBRARY-GPL-2.0.txt`: unchanged GNU historical licence text,
  25270 bytes, SHA-256
  `cc535c21133c895b56b374c8a1dc1eb948d99003ed2b47372069456b62f42b24`.
- `merops/GNU-LGPL-3.0.txt`: unchanged
  [GNU LGPL text](https://www.gnu.org/licenses/lgpl-3.0.txt), 7652 bytes, SHA-256
  `e3a994d82e644b03a792a930f574002658412f62407f5fee083f2555c5f23118`.
- `merops/GNU-GPL-3.0.txt`: unchanged incorporated GNU GPL text,
  35149 bytes, SHA-256
  `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`.
  GNU licence support files were received 2026-10-07. Their verbatim-copy permission
  applies to licence documents, not to arbitrary MEROPS data redistribution.

Credit MEROPS, EMBL-EBI and original contributing data providers. The normalized
`GNU-LIBRARY-GPL-UNVERSIONED` declaration preserves the stated licence; automated
use verdicts stay unknown, with internal retention and unknown sharing. Underlying
input rights and publication/software grants remain separate. See
[follow-up 10](../devguide/archive/local_work_2026-07/followup_10_source_integration.md).

## Contents

| Files | Source | Version / release | Retrieved | Licence |
| --- | --- | --- | --- | --- |
| `ttd/P2-01-TTD_uniprot_all.txt` | Unchanged original public TTD target cross-reference listing; all 4298 four-field blocks | Native header 10.1.01 (2024.01.10); individual target/UniProt revisions unstated | 2026-10-07 | Separate data grant NOT-STATED; original factual export local unreleased; article/software/input rights separate |
| `iptmnet/entry__P60174.html`, `iptmnet/entry__Q15796.html` | Unchanged native public iPTMnet report pages with all substrate groups, source scores and hidden source/PMID links | Dataset/record/sequence/scoring-rule revisions unstated | 2026-10-07 | Provider database CC BY-NC-SA 4.0; credit iPTMnet/UD/PIR/Georgetown; original contributing source/publication rights separate |
| `fda_orphan/page__476815.html`, `fda_orphan/page__106597.html`, `fda_orphan/search_form.html` | Unchanged original public OOPD detailed pages and search form; designation/approval tables independent, returned form is not scientific data | Dataset/record revisions unstated; procedural dates are native literals | 2026-10-08 UTC (2026-10-07 local) | FDA website public-domain policy unless otherwise noted; independent contributing-source and other rights remain separate; credit requested |
| `brenda/enzyme_class__5.3.1.1.json`, `brenda/enzyme_class__2.7.1.1.json`, `brenda/enzyme_class__7.99.99.99999.json` | BRENDA / DSMZ public SPARQL prototype; unchanged exact-EC descriptions and empty solution response | Prototype dataset/individual EC revisions unstated | 2026-10-07 | CC BY 4.0 for BRENDA data; credit BRENDA/DSMZ and Hauenstein et al. (2026), doi:10.1093/nar/gkaf1113 |
| `pharos/target__P60174.json`, `pharos/target__P31749.json`, `pharos/target__P00000.json` | Pharos/TCRD public GraphQL target metadata; unchanged exact-target and native-null responses | Individual target/TDL-rule revisions unstated | 2026-10-07 | Separate data grant NOT-STATED; original factual fixtures local unreleased; article/software and contributing-source rights separate |
| `depmap/24Q4__figshare_27993248__v1.json`; `depmap/24Q4__Model.csv`; `depmap/24Q4__README.txt` | Unchanged native DepMap/Broad public publication, complete 2105-row Model.csv and README | 24Q4, article 27993248 v1; individual model/ontology revisions unstated | 2026-10-07 | CC BY 4.0 for this selected public article; credit DepMap/Broad, release DOI, portal and program |
| `metalpdb/site__12ca_2.json`; `metalpdb/donor_distance_table__12ca_2.html` | Unchanged public [MetalPDB site JSON](https://metalpdb.cerm.unifi.it/api?query=site:12ca_2): 849 bytes, SHA-256 `4fbde4d64312472953cd7fc7eafe2da327a7fa1b67881bf56a9eddc45f8e68c4`. The HTML is an explicitly extracted single donor table from the [public Coordination Sphere](https://metalpdb.cerm.unifi.it/pdbSearchResult?id=12ca_2), 10906 bytes, SHA-256 `e389920434736f4ae6e813d94c71d12d4dd90692529890a0c641435d9b4fc283`, declaring Distance (Å) and matching three rounded API distances. The full original page stays outside fixtures; extraction is a modification, without semantic editing. | Site/structure/sequence revisions unstated; native counts/geometry/representative flags are independent | JSON: original public probe 2026-10-06, exact time unrecorded (`null`); fresh byte-identical JSON and unit-table qualification 2026-10-07 | [Official API/help](https://metalpdb.cerm.unifi.it/api_help), reviewed 2026-10-07. Separate data grant NOT-STATED; credit MetalPDB and CERM/University of Florence; retain native site/PDB/metal/ligand/donor context and API URL. JSON and the declared small HTML excerpt remain local unreleased recovery. Publication/software/input rights remain separate; no blanket redistribution permission inferred. |
| `ecod/domain__80374.json` | Unchanged public [ECOD UID 80374 JSON](http://prodata.swmed.edu/ecod/api/v1/domains/80374): e1iepA1, original PDB/chain/UniProt pointer, opaque range, id/name hierarchy, false/manual flags and unacquired file pointers. 617 bytes; SHA-256 `8768342d13ff78fe8f1f3a1328c0108f96a733eb85e1ac979a699cec912f2c5e`. | Domain/classification/sequence revisions unstated; API v1 and distribution catalog v295.2 are separate | 2026-10-07; original probe exact time unrecorded (`null`) | [Official documentation](http://prodata.swmed.edu/ecod/documentation), reviewed 2026-10-07. Separate data grant NOT-STATED; credit ECOD/Grishin Laboratory and retain native UID/domain/structure/classification/API URL. Original factual bytes remain local unreleased recovery. Publication/software and underlying PDB/Pfam/UniProt rights remain separate; no redistribution permission inferred. |
| `tcdb/accession_assignments.tsv` | Unchanged public [TCDB accession-to-system headerless export](https://tcdb.org/cgi-bin/projectv/public/acc2tcid.py): all 24956 two-column rows, thirteen blank accessions, case variants, versioned identifiers, repeated pairs and two six-component TC codes. 486702 bytes; SHA-256 `c59e2b2c5293e0f33e75bcc0bf89e0eb6988be54fb7f2121935749bda3feef8a`. | Export/assignment/sequence revisions unstated; website dates are separate | 2026-10-06 original probe; exact time unrecorded (`null`); byte-identical public export qualified 2026-10-07 | [Official FAQ](https://tcdb.org/faq.php), reviewed 2026-10-07, states website-text CC BY-SA 3.0/GFDL; separate export grant remains NOT-STATED. Credit TCDB/Saier Laboratory and retain native identifiers/export URL. Original factual export stays local unreleased recovery; no blanket redistribution or input-resource grant is asserted. |
| `channelsdb/annotations__1tqn.json` | Unmodified public [ChannelsDB PDB annotations DTO](https://channelsdb2.biodata.ceitec.cz/api/annotations/pdb/1tqn): one entry with 43 reaction literals, zero ChannelsDB-group residues and 22 independent UniProt-group residue comments. 13127 bytes; SHA-256 `9279b3cf4e1329addc20ffd861e18969f65698daf860d310ebb7d11d89d64c5c`. | Annotation/input sequence/model/assembly revisions and numbering axes unstated; API version 1.0.0 is separate | 2026-10-07; exact original probe retrieval time unrecorded (`null`) | [Official documentation](https://channelsdb2.biodata.ceitec.cz/documentation.html), reviewed 2026-10-07. Separate data grant `NOT-STATED`; frontend Apache, article CC BY and UniProt/publication rights remain separate. Credit ChannelsDB contributors, doi:10.1093/nar/gkad1012, and retain native references. Original bytes remain local unreleased recovery; no redistribution permission is inferred. |
| `channelsdb/channels__1tqn.json` | Full unmodified [public existing PDB channel DTO](https://channelsdb2.biodata.ceitec.cz/api/channels/pdb/1tqn): twelve channel categories, 26 native channels, 910 layers and seven independent comments/references. 751462 bytes; SHA-256 `f279ce91ee43ec6df7854923b8c46b723c31c2ebca204ae0309c3923ba5dd7f7`. Native geometry/properties remain raw and unqualified; no coordinate download or calculation. | Channel/input/sequence/model/assembly/numbering revisions unstated; API 1.0.0 and HTTP dates are separate | 2026-10-08T08:55:00+00:00, observed HTTP 200; byte-identical to the earlier original probe, whose exact retrieval time remains unknown | [Official documentation](https://channelsdb2.biodata.ceitec.cz/documentation.html), reviewed 2026-10-08. Data grant remains NOT-STATED; software/article/input rights stay separate. Credit ChannelsDB contributors, doi:10.1093/nar/gkad1012, and retain native input/reference labels. Local unpublished recovery; unknown sharing permission. |
| `gwas_catalog/associations__HBB__size2__page0.json`; `gwas_catalog/associations__TPI1__size2__page0.json` | Unchanged public native GWAS Catalog v2 HAL pages for exact standard mapped-gene filters, page 0, size 2. HBB contains two factual association/study/variant/trait records from PMID 39024449 of native total 279: 2485 bytes, SHA-256 `14f63516b1a620e3e41ddbd681acf507bc88f5685229103ece6c61a172b05786`. TPI1 declares zero elements: 198 bytes, SHA-256 `4dde3abd2cc12114cc229c93e6acb95e07d1467d2ebee03b3c18376ae1df92b7`. | Dataset/association/assembly/sequence revisions unstated; API v2 is separate | Public probes acquired 2026-10-06; exact first retrieval times unrecorded (`null`); terms reviewed 2026-10-07 | [Catalog data terms](https://www.ebi.ac.uk/gwas/docs/about/) apply [EMBL-EBI Services Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/): no restrictions added by EMBL-EBI beyond original-owner rights, with scientific attribution. Credit NHGRI-EBI GWAS Catalog and Verma et al., PMID 39024449, DOI 10.1126/science.adj1182. These small factual API records are unchanged; no article text, supplementary file, summary-statistics dataset or participant data is included. Original-owner rights remain applicable; neither summary-statistics CC0 nor software Apache is assigned to these curated records. |
| `pride/project__PXD013616.json` | Unchanged public [PRIDE Archive native project JSON](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD013616), complete metadata for PXD013616 with original depositor protocols, CV objects, publications and administrative counts. 8484 bytes; SHA-256 `b5ff728947d5e0e394633022e26ba57622ccbfad2d6e9da46b8a60add6c2de71`. | Project/sequence revisions unstated; route v2, API 3.0 and submission/publication dates are separate | 2026-10-07; exact first retrieval time unrecorded (`null`) | Native project `license` and [official project page](https://www.ebi.ac.uk/pride/archive/projects/PXD013616) declare Creative Commons Public Domain CC0. Credit PRIDE Archive and original depositors/publications, including the native DOI 10.1126/sciadv.aay4697. No modification. This per-project grant does not cover arbitrary PRIDE projects, linked publications or Proteins API input providers; no linked files or article are acquired. |
| `monarch/associations__HGNC_12009__limit2__offset0.json` | Unchanged public Monarch v3 expanded page for `subject=HGNC:12009`, `direct=true`, `limit=2`, `offset=0`: two original BioGRID associations, native total 232. 5205 bytes; SHA-256 `0456c3b120f0922eab4a0508f4169ac253ba973a5191bce625da65cc2607e858`. | KG/association/entity revisions unstated; API 0.1.0 is separate | 2026-10-07; exact first download time unrecorded (`null`) | BioGRID inputs have an explicit [MIT data/download-files grant](https://downloads.thebiogrid.org/BioGRID). Credit BioGRID/Mike Tyers Lab, original contributors, Stark et al. (2006) and Monarch. The unchanged original grant/copyright/disclaimer is retained in `monarch/BioGRID-LICENSE.txt` (1094 bytes, SHA-256 `39a74f854f2d9370b8d349ca329cb6bd37390b8b47b6b5edd5825276721a1391`, native Windows-1252). [Monarch's BioGRID ingest documentation](https://monarch-app.monarchinitiative.org/Sources/biogrid/) separately lists BSD-3-Clause; `monarch/Monarch-software-LICENSE.txt` preserves the original software notice (1519 bytes, SHA-256 `a768a54062e03d696719c37f2c505609e2a965248ad3e2667d33c3c16c1c5f57`), without treating it as a blanket KG grant. Native labels, ECO and publication pointers keep independent origin; linked content is not acquired. No modification. |
| `omnipath/interactions__P60174.json` | Unchanged native human OmniPath interaction array for `partners=P60174`, `datasets=omnipath`, `organisms=9606`, `fields=sources,references`, `format=json`, `license=academic`. One P29466-to-P60174 occurrence; 288 bytes; SHA-256 `6f5a542228162871e4645e3f7897eba1bc660fb4c9ffc7bf75d9f852030d4e6a`. | Dataset/interaction/support revisions unstated | 2026-10-06; exact first retrieval time unrecorded (`null`) | This row declares only SPIKE/SPIKE_LC support. [OmniPath native licence metadata](https://omnipathdb.org/resources?format=json) names CC BY 4.0 for both; the [provider's SPIKE description](https://omnipathdb.org/info) also declares CC BY 4.0. Credit OmniPath, SPIKE and original contributors, retaining native reference 17959595. No modification. This grant does not license other OmniPath rows, linked publications, original inputs with separate rights or software. The academic query filter is not a reuse grant. |
| `wikipathways/findPathwaysByXref.json` | Unchanged official [findPathwaysByXref JSON](https://www.wikipathways.org/json/findPathwaysByXref.json), all 2218 native pathway rows and 14 original fields; 12084935 bytes, SHA-256 `09da862b2d2dc08c98c0a0d98640892c076668d5ad251ee373502dcf89bbce22` | Native pathway date labels retained; dataset/GPML/entity/sequence revisions unstated | 2026-10-06; exact first download timestamp unrecorded (`null`) | [WikiPathways CC0 content terms](https://www.wikipathways.org/terms.html), reviewed by direct public GET 2026-10-06. Retain WikiPathways, native pathway authors and contributor attribution; linked publications and external resources have independent rights and are not acquired. |
| `ema_orphan/designations.json` | Unchanged official [orphan-designation JSON](https://www.ema.europa.eu/en/documents/report/medicines-output-orphan_designations-json-report_en.json), all 3310 native page occurrences; 2070548 bytes, SHA-256 `8a83500533765c0d43a63b58581ef9c51d2df6f709fdc1d61c6f0ac74a80fd54` | Native declared total 3310 and generation timestamp 2026-10-06T18:05:23Z; dataset/record/product/sequence revisions unstated | 2026-10-06; exact first retrieval time unrecorded (`null`), separate from file generation | [Official EMA reproduction grant](https://www.ema.europa.eu/en/about-us/about-website/legal-notice), reviewed by direct public GET 2026-10-06. EMA-owned content may be reproduced for commercial/noncommercial use with EMA acknowledgement in every copy. Credit European Medicines Agency, original JSON URL and October 2026 access. Third-party content/logo/linked-document rights remain separate. |
| `civic/01-Oct-2026-AcceptedClinicalEvidenceSummaries.tsv` | Unchanged public [monthly accepted-items TSV](https://civicdb.org/downloads/01-Oct-2026/01-Oct-2026-AcceptedClinicalEvidenceSummaries.tsv), all 4940 native 25-column rows; 4154685 bytes, SHA-256 `a618939c33c7cc9cc530be5f0a51fc330b29ad46b3f9a5bebeddcd871375e086` | Explicit monthly export 01-Oct-2026; entity/sequence revisions unstated; review dates retained literally | 2026-10-06; exact first retrieval time unrecorded (`null`) | [CIViC content CC0 1.0](https://docs.civicdb.org/en/latest/about/faq.html#how-is-civic-licensed), reviewed 2026-10-06. Credit CIViC contributors and Griffith et al. (2017), doi:10.1038/ng.3774; retain native citations. Application MIT and linked publications retain separate rights. |
| `drugcentral/target_relations.tsv.gz` | Unchanged public native [drug-target interaction export](https://unmtid-dbs.net/download/drug.target.interaction.tsv.gz), linked by the [official download page](https://drugcentral.org/download). 956583 compressed bytes; SHA-256 `1908684983a79a067a44da952e1f6fd26b0f34cc36560cd9be0f0843bbfee1e1`. Decompressed original TSV: 5472138 bytes, SHA-256 `d3be9317010da11f90b2213063f4cb8a95dc4173404338d97f8a3b6070088596`, 22364 independent 20-column rows. | Export/target/drug/sequence revisions unstated; website 2027 and full database dump date do not supply them | 2026-10-06; exact first retrieval time unrecorded (`null`) | [Official resource licence](https://drugcentral.org/privacy), reviewed 2026-10-06, links [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Credit DrugCentral and Ursu et al. (2017), doi:10.1093/nar/gkw993; retain attribution/share-alike and indicate changes if modified. This compressed fixture is unchanged. Underlying data/publication rights remain separate; linked sources are not acquired. |
| `clingen/gene_validity.csv` | ClinGen unchanged gene-disease validity CSV with native preamble/header and all 3702 curations; 1129673 bytes, SHA-256 `979e814b2371a13133ab11ef14b613c58f11967928634b2af128df0632865016` | Native file label 2026-10-06; dataset/gene/sequence revisions unstated; independent classification dates/SOP retained | 2026-10-06; exact original retrieval time unrecorded | [ClinGen CC0 1.0 curated content](https://clinicalgenome.org/docs/terms-of-use/); source/access-date and original-panel attribution requested; linked report/publication/input rights separate |
| `hpa/profile__ENSG00000111669.json` | Human Protein Atlas unchanged single-gene JSON subset for TPI1; 9394 bytes, SHA-256 `62b81e47662b8c4d74a51cb41c4ba68803cf339150a34441f49ae37f9b85401a`; full native response retained, 22 categorical declarations mapped | Dataset/gene/sequence revisions unstated; website release is not assigned | 2026-10-06; exact original retrieval time unrecorded | [HPA CC BY 4.0](https://www.proteinatlas.org/about/licence) for copyrightable parts, with third-party input rights retained; credit HPA, the specific gene/data URL and appropriate primary publication |
| `signor/relations__P60174__9606.tsv` | SIGNOR unchanged native `getData.php?id=P60174&organism=9606`; 1272 bytes, SHA-256 `bf6a5d23113c3576e33cddd9367826cd953becd9ad158b06bc1497115d503537`; 3 rows | Export/relation/sequence/score revisions unstated; requested organism separate from native taxonomy | 2026-10-06; exact original time unrecorded | [SIGNOR CC BY 4.0](https://signor.uniroma2.it/documentation/); attribute source, link licence and indicate changes; linked publication/input rights separate |
| `signor/relations__P31749__9606.tsv` | SIGNOR unchanged native `getData.php?id=P31749&organism=9606`; 197038 bytes, SHA-256 `33fba2855ea54311e73773181e33992286d164da674806916ac1c6d242db556f`; 456 rows | Export/relation/sequence/score revisions unstated; requested organism separate from native taxonomy | 2026-10-06; exact original time unrecorded | [SIGNOR CC BY 4.0](https://signor.uniroma2.it/documentation/); attribute source, link licence and indicate changes; linked publication/input rights separate |
| `signor/relations__P31749__10090.tsv` | SIGNOR unchanged native `getData.php?id=P31749&organism=10090`; 16 bytes, SHA-256 `998dddbd7011f78f68ca8d7b6e4ba910c10b98d60a2e1e39ace8bfc3de0cce4c`; 0 rows; literal `No result found.` | Export/relation/sequence/score revisions unstated; requested organism separate from native taxonomy | 2026-10-06; exact original time unrecorded | [SIGNOR CC BY 4.0](https://signor.uniroma2.it/documentation/); attribute source, link licence and indicate changes; linked publication/input rights separate |
| `appris/annotations__ENSG00000111669.json` | APPRIS unchanged default human gene JSON exporter; 252247 bytes, SHA-256 `e9b7a1f300e76ac359bfc845af03b28f043c9c5b6db14b41a670dd6794de5a95` | Dataset/assembly/record/sequence revisions not stated | 2026-10-06; original exact time unrecorded | [APPRIS CC BY-NC-SA 4.0](https://appris.bioinfo.cnio.es/partials/license.html); noncommercial, attribution, licence link and share-alike obligations; linked input/publication terms separate |
| `complex_portal/complex__CPX-2158.json` | Complex Portal full native public JSON at `/intact/complex-ws/complex/CPX-2158`; 30432 unchanged bytes, SHA-256 `bd960ad715608e19a1c2f0e57e4c651172365617e8f8d2c79cc45636aa76dca3`; original retrieval timestamp was not recorded | Record/participant sequence revisions not stated; native release dates remain separate | 2026-10-06 | [Complex Portal CC0 1.0 data grant](https://raw.githubusercontent.com/Complex-Portal/complex-portal-documentation/master/about/license_privacy.md), including webservice data; provider attribution encouraged; software/publication rights separate |
| `complex_portal/complex__CPX-3055.json` | Complex Portal full native public JSON at `/intact/complex-ws/complex/CPX-3055`; 20074 unchanged bytes, SHA-256 `2e04fc10a879a4b6ac87992e870c47756d27038b95791c338038b477efe8722c`; original retrieval timestamp was not recorded | Record/participant sequence revisions not stated; native release dates remain separate | 2026-10-06 | [Complex Portal CC0 1.0 data grant](https://raw.githubusercontent.com/Complex-Portal/complex-portal-documentation/master/about/license_privacy.md), including webservice data; provider attribution encouraged; software/publication rights separate |
| `complex_portal/complex__CPX-14819.json` | Complex Portal full native public JSON at `/intact/complex-ws/complex/CPX-14819`; 6819 unchanged bytes, SHA-256 `c2784febffa50c9d10fea56f0af0e4d163e2e34a6def5715394623957fcb9214`; original retrieval timestamp was not recorded | Record/participant sequence revisions not stated; native release dates remain separate | 2026-10-06 | [Complex Portal CC0 1.0 data grant](https://raw.githubusercontent.com/Complex-Portal/complex-portal-documentation/master/about/license_privacy.md), including webservice data; provider attribution encouraged; software/publication rights separate |
| `cath/v4_4_0/domain_summary__1htiA00.json` | CATH native full domain summary for `1htiA00`, requested route `v4_4_0`; unchanged public response, 15056 bytes, SHA-256 `f476ec51fe7bba6e1251604c3a8ef05b4bc6b953f5960fef72fba9e19da2189f`. [API documentation](https://github.com/UCLOrengoGroup/cath-api-docs); original retrieval timestamp was not recorded | Response release/record/sequence revisions not stated; route is a request declaration | 2026-10-06 | [CATH CC BY 4.0](https://www.cathdb.info/); attribution required, indicate modifications; parent resource/publication rights remain separate |
| `cath/v4_4_0/domain_summary__1cukA01.json` | CATH native full domain summary for `1cukA01`, requested route `v4_4_0`; unchanged public response, 6626 bytes, SHA-256 `b2824b38a5b930a258f65e71c11d5b285c14aa152c322b4f18b039fe678dc909`. [API documentation](https://github.com/UCLOrengoGroup/cath-api-docs); original retrieval timestamp was not recorded | Response release/record/sequence revisions not stated; route is a request declaration | 2026-10-06 | [CATH CC BY 4.0](https://www.cathdb.info/); attribution required, indicate modifications; parent resource/publication rights remain separate |
| `cath/v4_4_0/domain_summary__3g06A01.json` | CATH native full domain summary for `3g06A01`, requested route `v4_4_0`; unchanged public response, 18549 bytes, SHA-256 `47764bbed4d5639efd56ab4b4f1f739ff98dd317d89a85617d07270a05046b5f`. [API documentation](https://github.com/UCLOrengoGroup/cath-api-docs); original retrieval timestamp was not recorded | Response release/record/sequence revisions not stated; route is a request declaration | 2026-10-06 | [CATH CC BY 4.0](https://www.cathdb.info/); attribution required, indicate modifications; parent resource/publication rights remain separate |
| `cath/v4_4_0/domain_summary__3a85A01.json` | CATH native full domain summary for `3a85A01`, requested route `v4_4_0`; unchanged public response, 9023 bytes, SHA-256 `89529bcf1891e06c758d167681873baa54dd3de3987edf7bffadc90d8836ccb5`. [API documentation](https://github.com/UCLOrengoGroup/cath-api-docs); original retrieval timestamp was not recorded | Response release/record/sequence revisions not stated; route is a request declaration | 2026-10-06 | [CATH CC BY 4.0](https://www.cathdb.info/); attribution required, indicate modifications; parent resource/publication rights remain separate |
| `uniprot_isoforms/P60174.json`; `uniprot_isoforms/P60174-1.fasta`; `uniprot_isoforms/P60174-3.fasta`; `uniprot_isoforms/P60174-4.fasta` | Full unmodified public UniProt parent JSON and selected native isoform FASTA responses. Parent 86279 bytes/SHA-256 `25b200a9f5f22f24d68d7f64445b447770b1875126829b1de2f9e7e01cc6acdd`; FASTA -1: 349 bytes/`4f2e6a59a3fd7c780ca6686dfbbeb67cb2d2812b0f1ccffe7043d27b98c65375`; -3: 386 bytes/`ecb73ad7021fcbc244ad4b42a79354439818dbad69ea56e78ae3a831bf0810dc`; -4: 265 bytes/`79ca8380928aed003ef40f9e29ffb567ea5b5b5db442ea63edbb011d0edd66df`. Native names 1/2/3 correspond to IDs -1/-3/-4 and lengths 249/286/167. | Parent entry version 212/canonical sequence version 4; isoform sequence revisions unstated. Original service release 2026_03 remains separate, with no fixture header declaration or fabricated isoform revision. | 2026-10-06; exact original client retrieval times unrecorded (`null`) | [UniProt CC BY 4.0](https://rest.uniprot.org/help/license), reviewed 2026-10-06; credit UniProtKB and UniProt Consortium. [Official FASTA format](https://www.uniprot.org/help/fasta-headers) and [alternative-product declarations](https://web.expasy.org/docs/userman.html#CC_line). Original bytes remain unmodified; parent/FASTA are independent observations. |
| `swissmodel/metadata__P60174.json` | Full unmodified public [SWISS-MODEL Repository v2 metadata response](https://swissmodel.expasy.org/repository/uniprot/P60174.json), unfiltered: 30 occurrences (29 PDB, one SWISSMODEL), 57 paired alignments and full 249-residue target sequence. 79925 bytes; SHA-256 `71ef900ff67d4b25c3fa3295165ce6c527aae666bf63a000c0f09da5e97e710a`. | Metadata/model/sequence revision unstated; API 2.0, native query time and creation/PDB-release dates stay separate | 2026-10-06; exact original client retrieval time unrecorded (`null`), native query date `2026-10-06T20:01:04.880Z` is retained separately | [Official data terms](https://swissmodel.expasy.org/docs/terms_of_use), reviewed 2026-10-06: CC BY-SA 4.0, source credit, licence link, change indication and share-alike for adaptations. Credit SWISS-MODEL Repository, Bienert et al. (2017), doi:10.1093/nar/gkw1132 and Waterhouse et al. (2018), doi:10.1093/nar/gky427. Parent PDB/UniProt inputs and publication rights remain separate. |
| `amypro/entries.json` | Full unmodified public [AmyPro JSON export](https://amypro.net/data/amypro.json): 125 entries, 156 declared regions and investigated sequences, native categories/prion strings, mutations, parent bounds and publication pointers. 115711 bytes; SHA-256 `9b7d31b89406499611cbd6d349eaaaa8cdd4d065c3fc964c5bbfd51379770cdd`. Individual Python-literal `.json` downloads are not used. | Export/entry/sequence revision unstated; site/footer and HTTP file dates are not assigned as record revisions | 2026-10-06; exact original client retrieval time unrecorded (`null`) | [Official help/download](https://amypro.net/#/help), reviewed 2026-10-06. Separate data grant remains `NOT-STATED`; the resource paper's CC BY-NC 4.0 is not assigned to database exports. Credit AmyPro and Varadi et al., doi:10.1093/nar/gkx950. Original bytes remain local unreleased recovery; no redistribution permission is inferred. |
| `eppic/interface_residues__1hti__1.json` | Full unmodified native public EPPIC `interfaceResidues/1hti/1` GET response: 496 per-side rows (248 per side), including zero areas, 44 quoted `NaN` fractions and all native serial/type/region/entropy fields. 78142 bytes; SHA-256 `b21afdcf1aca5e0974eecc2dc3297808a4f59ed37aba56db5e40e9459b174c61`. Parent context is the separately declared `interfaces__1hti.json` fixture. | Record/sequence/calculation revisions unstated; source serials do not establish canonical or author/label numbering | 2026-10-06; exact original client retrieval time unrecorded (`null`) | Same reviewed EPPIC public-resource terms as the annotation fixtures: separate prediction-data licence remains `NOT-STATED`; GPL software, served API software and paper licences are not assigned to response data. Credit EPPIC/Bliven et al., doi:10.1371/journal.pcbi.1006104. Original bytes remain local unreleased recovery; no new redistribution permission is asserted. |
| `intact/interactions__P60174.mitab`; `intact/interactions__P60174.headers.json` | Full unmodified public native PSICQUIC `id:P60174` MITAB 2.7 response, all 80 rows and 42 columns. Body 898329 bytes; SHA-256 `48b43fc580ad3ba7af9a2446ca6041168768938cca29bb5017c7924cad914762`. Sidecar represents four observed count/service header values and the exact request declaration; it is not an HTTP wire-byte copy. | Record/participant sequence revision unstated; implementation 1.5.3 and specification 1.4 remain separate context | 2026-10-06; exact original client retrieval time unrecorded (`null`) | [Official IntAct/IMEx licence](https://www.imexconsortium.org/about/#licence), reviewed 2026-10-06: CC BY 4.0 for MITAB and service data. Credit IntAct, EMBL-EBI and contributing curation teams; preserve native publication pointers. Software and linked article rights are separate. |
| `alphafill/metadata__P60174.json` | Full unmodified public native AlphaFill metadata GET response for model `AF-P60174-F1`: 55 template hits and 86 transplants, original alignment/donor numbering, clash distances, PAE and validation. 207002 bytes; SHA-256 `129911c1a03216cc15ae03479f2bdb3fb8604712c7ad3a4e866464c1e49bd58c`. | Current metadata revision unknown; native run software 2.1.1/date 2023-12-22 and input-file literal remain separate | 2026-10-06; exact original client retrieval time unrecorded (`null`) | [AlphaFill Usage Policy](https://alphafill.eu/license), reviewed 2026-10-06: free commercial/non-commercial use and original-file redistribution, modified parent attribution and applicable parent AlphaFold terms. Credit AlphaFill/AlphaFold and Hekkelman et al. (2023), doi:10.1038/s41592-022-01685-y. Classified as `FREE-WITH-ACKNOWLEDGEMENT`; BSD software licence is separate. |
| `ligysis/result__P60174__1.html` | Full unmodified public native LIGYSIS result page for HsTIM segment 1, containing two sites and their original score/membership/count/identity literals; page assets are not downloaded or executed. 96597 bytes; SHA-256 `3ccb0df740fe353b1f2a12f1362459e0296e6cfacda1736ca8a4e23479d6aacc`. | Result/source sequence revisions unknown; no website copyright year or article date is assigned as a revision | 2026-10-06; exact original client retrieval time unrecorded (`null`) | [Official about/access page](https://www.compbio.dundee.ac.uk/ligysis/about), reviewed 2026-10-06. Separate dataset redistribution licence not established (`NOT-STATED`); linked [MIT code licence](https://github.com/bartongroup/LIGYSIS-web/blob/master/LICENSE) and article CC BY are not assigned to data. Credit LIGYSIS/Barton Group and Utgés et al., doi:10.1093/nar/gkaf411. |
| `ligysis/mapping__P60174__1__7t0q.json` | Full unmodified original public read-only POST response from [LIGYSIS structure mapping](https://www.compbio.dundee.ac.uk/ligysis/get-uniprot-mapping), requested with `pdbId=7t0q`, `proteinId=P60174`, `segmentId=1`. Four directed residue dictionaries, two chain-to-accession declarations and eight remappings; no coordinates or jobs. 9185 bytes; SHA-256 `31cecd5b839f7c513fb2d330dfa618abc86b99d1756a8ab0ee37580e961be836`. | Mapping/structure/sequence revisions not stated; provider code SHA and HTTP date are not scientific revisions | 2026-10-08T07:06:36+00:00; observed public HTTP 200 | [Official access/credit page](https://www.compbio.dundee.ac.uk/ligysis/about), reviewed 2026-10-08. Dataset sharing permission remains unknown (`NOT-STATED`); linked MIT applies to code. Credit LIGYSIS/Barton Group and Utgés et al., doi:10.1093/nar/gkaf411. Local unpublished qualification only. |
| `glygen/protein__P60174.json` | Unmodified full public native GlyGen protein detail GET response for HsTIM; includes source sequence P60174-1, three glycosylation rows and thirteen phosphorylation rows with native categories, isoform correspondence comments and original support pointers. SHA-256 `81c1dc5ea38978d8c507ea86886005baebf2b035253a7a19adccf7c2ae28f481`; 432627 bytes. Other response sections remain raw and unqualified. | Protein/source sequence revision unknown; native history says introduced in release 1.8.25, which is not a current record revision | 2026-10-06; exact original client retrieval time unrecorded (`null`) | [GlyGen licence](https://www.glygen.org/license.html), reviewed 2026-10-06, applies CC BY 4.0 to database sets; [official licence page source](https://github.com/glygener/glygen-frontend/blob/master/src/pages/License.js). Credit GlyGen and original annotation providers. Contributing-source terms and publication rights remain separate. |
| `eppic/entry__1hti.json`; `eppic/interfaces__1hti.json`; `eppic/assemblies__1hti.json` | Unmodified public native EPPIC REST v3 response bytes for 1HTI: exact entry/run context, nine interfaces and three assemblies (including unit-cell ID 0). Entry SHA-256 `948a1fde23a6b81cc2646a7952d07b8f3e15c08a60a6371faf68a4972defdd69`; interfaces `681ab10013e975c2e33073861a51d13b7c1e0a314ccbf9405fe822613558ce2d`; assemblies `e293ee5a35165c7178811d49f1b0632aa71505ef56f7ea655ddd85aad1d203c0`. | Prediction-record revision unknown; native run parameters state EPPIC version/build `NA`, UniProt `2026_01`, separately from entry releaseDate | 2026-10-06; exact original client retrieval times unrecorded (`null`) | Official [public data download route](https://www.eppic-web.org/downloads), reviewed 2026-10-06. Separate prediction-data reuse licence not established (`NOT-STATED`). GPL software and Apache 2.0 served API documentation are not assigned as prediction-data licences. Credit EPPIC and Bliven et al. (2018), doi:10.1371/journal.pcbi.1006104. |
| `pdb_redo/entry__1cbs.json`; `pdb_redo/versions__1cbs.json` | Unmodified native public PDB-REDO databank data.json and versions.json bytes. Full properties, original/redo residue-angle arrays, input revisions, all software versions and used flags retained. Entry SHA-256 `b61c728e49ac0ffdde336360f229b3b8940da1b1737ac8e584d1d79db34a6cbf`; versions `9fd8a90154eefc30316c3b6585aa63964aada47e74df30ec927480721d6e30ad`. | Databank record revision unknown; native pipeline 8.22, creation date 2026-09-02 and input revisions retained separately | 2026-10-06; exact original client retrieval times unrecorded (`null`) | Official [PDB-REDO Usage Policy](https://pdb-redo.eu/license), reviewed 2026-10-06: commercial/non-commercial use and redistribution of original files; modified files require parent attribution. Credit PDB-REDO and original structure authors; parent PDB terms apply where applicable. Classified as `FREE-WITH-ACKNOWLEDGEMENT`, without assigning a Creative Commons licence. |
| `pdbe_validation/global_percentiles__1hti.json`; `pdbe_validation/global_percentiles__1cbs.json` | Unmodified native PDBe `/api/validation/global-percentiles/entry/<pdb_id>` JSON response bytes. 1HTI retains three metrics; 1CBS retains five. Raw values, archive-wide and comparable-entry percentiles remain literal. SHA-256: 1HTI `e2a53971c2e5b2d228cd648726d5f418959a5e79dc623b36c9d8321499bb2c3d`; 1CBS `fb6374c0276e3b5aa1c09233cdaad644801241f1f014d6ef9bacf09dcfd49607`. | Validation/statistical revision not stated; current documented API service 2.10.9 is not a data revision | 2026-10-06; exact original client retrieval time unrecorded (`null`) | [EMBL-EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/), reviewed 2026-10-06; original-owner rights remain applicable. Separate API-response reuse licence not established. [wwPDB CC0](https://www.wwpdb.org/about/usage-policies) explicitly covers archive data files; this is not assigned as a separate API-response licence, and PDBe-KB terms are not borrowed. |
| `mobidb/annotations__P60174.json`; `mobidb/annotations__P37840.json`; `mobidb/annotations__P60174.headers.json`; `mobidb/annotations__P37840.headers.json` | Unmodified native MobiDB v1 single-protein JSON export body bytes. All annotation sets, complete source sequences, provenance, series/measurement semantics, native coverage and representation issues retained. Headers are JSON representations of the observed HTTP header values, not wire-byte copies. P60174 body SHA-256 `ff827772f4e6f05d057eb005d5791168a660172f0b0fa072d9af623b54410456`, header representation SHA-256 `822eb16f0a73d384ef0487309c4d359dc320d6f5e5f817633b6afb4b05584016`; P37840 body SHA-256 `2bb758834ea0bf2c5c7582e261027f5990d9ff76c1538a0854ce5984b209b5ea`, header representation SHA-256 `75598114b2315aa1f4a0a08f3189cfceeaa15e150923a2bf390f00d77a294cc6`. | Database 7.0, release 2026_07; API v1, retained separately | 2026-10-06; exact original client retrieval time unrecorded (`null`); native HTTP Date remains header context | CC BY 4.0 under [MobiDB License & policy](https://mobidb.org/about#license), reviewed 2026-10-06. Preserve provider/method/aggregation provenance. Native annotation basis is not MOLI Evidence; original PTM experimental basis is not retained by the provider. |
| `sifts/mappings__1hti.json` | Unmodified native PDBe SIFTS UniProt segment response for public 1HTI; both P60174 chain mappings, entity/internal/author numbering and insertion fields retained. SHA-256 `c89e616ce17f23da172b5dd044e071a166e9db22a7639a7beb6cfd1566470a78`. | Release and referenced sequence revisions not stated | 2026-10-06; exact original client retrieval time unrecorded (`null`) | [EMBL-EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/), linked by the official SIFTS resource, reviewed 2026-10-06. No separate SIFTS-wide licence established; original-owner rights remain applicable. No PDBe-KB licence is assigned by inference. |
| `alphamissense/alphafold/P60174.json`; `alphamissense/AF-P60174-F1-aa-substitutions.csv` | Unmodified native AlphaFold DB discovery response and its declared canonical HsTIM AlphaMissense artifact. Discovery retains one canonical and two isoform descriptors; only the canonical artifact is fetched. CSV keeps all 4731 native substitutions and original CRLF bytes. Discovery SHA-256 `f2ec3d0776b465f5264a4ebc9bc041b33da224e61dae8979e93ca34aef70b15e`; CSV SHA-256 `d5831f6d4971e3440a51c665de67443ad79b8ff9910788e419a0899c963a8796`. | Host model v6; AlphaMissense prediction-artifact revision not stated. Host version/date is not the score version. | 2026-10-06; exact original retrieval time unrecorded (`null`) | CC BY 4.0 for predictions, stated in the [official AlphaMissense README](https://github.com/google-deepmind/alphamissense#alphamissense-predictions-license); credit DeepMind and Cheng et al., Science (2023), doi:10.1126/science.adg7492. Host metadata follows AlphaFold DB CC BY 4.0. No source-code or article fragments copied. |
| `uniparc/search__A8D44FC2C980A7677A3B54788D0FA323.json` | UniParc (UniProt Consortium), native MD5 search for the public HsTIM sequence. Untrimmed response body retained in an explicit query/count/release wrapper and original page receipt. Original body SHA-256 `5ce9fffb29818f15d00df60948f0d5788c5b5656d84e39c577beea2db8cef186`; wrapper SHA-256 `2c3ba4abdcae3b299a9b623403ace4c186001c353d681b11851874ed8086ddd6`. Nine returned UniProtKB references include historical revisions and an isoform; 457 is the native count of all cross-references, not UniProt candidates. | header release `2026_03`, not a sequence revision; native entry dates retained | 2026-10-06; exact original retrieval time not recorded (`null`); retained server `Date` is not independent retrieval proof | CC BY 4.0 under the official [UniProt licence](https://rest.uniprot.org/help/license); credit UniParc / UniProt Consortium. Other referenced databases retain their own rights. |
| `disprot/records__P37840.json` | DisProt, native `https://disprot.org/api/search?acc=P37840` response for alpha-synuclein (DP00070); entry identity, full native sequence, counts and all 22 returned regions kept. Unrelated fields, publication quotations and HTML references omitted; native region coordinates/revisions/reference ids unchanged. The response declares 40 regions, so this default subset is incomplete. Original response SHA-256 `051e7280c99230903d26f8a55f01d0805ab7bde57c36036cd90204c97c625a49`; trimmed fixture SHA-256 `37ba18b6ca95cc53b8c8305a43bdc09e5290d38c4e4b0fb388e8f30714f579af` | global release not stated; native region revisions retained, not global versions | 2026-10-06 | CC BY 4.0, as stated on [DisProt](https://disprot.org/); credit DisProt. Linked article rights remain separate; no article text retained |
| `P00938.json`, `P35372.json`, `P52270.json`, `P52789.json`, `P60174.json`, `P60175.json`, `Q6FHP9.json`, `V9HWK1.json`, `A0A140VJM9.json` | UniProtKB (UniProt Consortium) | release 2026_03 | 2026-09-23 | CC BY 4.0 |
| `P00648.json` | UniProtKB (UniProt Consortium), barnase of *Bacillus amyloliquefaciens*, a public test system for interface mutations | release 2026_03 (entry version 146) | 2026-09-29 | CC BY 4.0 |
| `Q9Y2T5.json` | UniProtKB (UniProt Consortium), human GPR52, a public test system for GPCR numbering (GPCRdb) | entry version 170 | 2026-09-30 | CC BY 4.0 |
| `Q4DV43.json` | UniProtKB (UniProt Consortium), the TIM of *T. cruzi* strain CL Brener (TrEMBL), TcTIM's genome-strain entry, a public test system (#103) | entry version 97 | 2026-10-01 | CC BY 4.0 |
| `O75716.json` | UniProtKB (UniProt Consortium), human STK16, a public test system for kinase pockets (KLIFS) | entry version 221 | 2026-09-30 | CC BY 4.0 |
| `mondo/mondo.obo` | MONDO (Monarch Initiative), release v2026-09-01: the file's header and the whole stanzas of 63 terms: those equivalent to the diseases on the HsTIM and benznidazole fixtures, plus type 2 diabetes mellitus and its parent, and an obsolete term and its replacement; unchanged | v2026-09-01 | 2026-09-29 | CC BY 4.0 |
| `medgen/concepts.json` | MedGen (NCBI), the record UID of each MedGen concept id naming a condition in the ClinVar fixture (esearch by concept id, then esummary), and the database's last update; only the ids are kept | last update 2026/09/28 23:56 | 2026-09-29 | US public domain (NLM policy) |
| `skempi/skempi_v2.csv` | SKEMPI 2.0 (Jankauskaitė et al. 2019), the 105 rows of the barnase–barstar complexes (1BRS, 1B2S, 1B2U, 1B3S, 1X1W, 1X1X), header kept; a subset of the whole file, rows unchanged | 2.0 (CSV of 2018-06-06) | 2026-09-29 | CC BY 4.0 |
| `Q4D3W2.json`, `Q4QGX0.json` | UniProtKB (UniProt Consortium), a *T. cruzi* and an *L. major* entry with PHI-base records | release 2026_03 | 2026-09-27 | CC BY 4.0 |
| `phi_base/*.json` | PHI-base 5 (Zenodo record 21196331), the curation sessions naming Q4D3W2, H2DQH1 and Q4QGX0, as split by `sabueso.tools.db.phi_base.split_release` | 5.6 | 2026-09-27 | CC BY 4.0 (cite PHI-base; Urban et al., Nucleic Acids Res. 2025) |
| `uniprot_search/*.json` | UniProtKB search responses; refreshed with lineage and gene-locus cross-references, and the Trichomonas vaginalis search added, on 2026-09-25 (same release, same results) | release 2026_03 | 2026-09-23 | CC BY 4.0 |
| `alphafold/*.json` | AlphaFold DB (Google DeepMind and EMBL-EBI), prediction API responses | model version 6 | 2026-09-25 | CC BY 4.0 |
| `ncbi_taxonomy/*.json` | NCBI Taxonomy (NCBI/NLM), Datasets API taxon records, trimmed to id, name, rank, lineage and BLAST name | Datasets API 18.37.0 | 2026-09-25 | US public domain (NLM policy) |
| `ncbi_gene/*.xml` | NCBI Gene (NCBI/NLM), Entrez E-utilities `efetch` gene records (XML), as returned | E-utilities | 2026-09-26 | US public domain (NLM policy) |
| `bindingdb/*.json` | BindingDB, REST `getLigandsByUniprots` responses for P52270 and P60174 | — | 2026-09-25 | **CC BY-SA 3.0** (treated as such: BindingDB curation is CC BY 3.0, ChEMBL imports CC BY-SA 3.0, and records state no origin) |
| `pubchem_bioassay/*.json` | PubChem BioAssay (NCBI/NLM): assays linked to P52270 and P60174, their summaries, concise tables and the InChIKeys of their compounds | — | 2026-09-25 | US public domain (NLM policy); deposited data keeps its depositor's terms: these assays were deposited by ChEMBL (**CC BY-SA 3.0**) and BindingDB |
| `rcsb/*.json` | RCSB PDB (wwPDB archive), GraphQL entry data; assemblies added and 3Q37 retrieved 2026-09-24; all refetched with mutations, tags, unobserved residues, refinement and dates, and 2OMA, 2VOM, 4HHP and 4UNK added, 2026-09-25; refetched with author numbering, and 2V5B and 1WYI added, 2026-09-26 (1KLG kept from 2026-09-25: RCSB answered it only partially that day); all refetched with the program that assigned each instance feature (`provenance_source`), 2026-09-27, each answered completely, 1KLG included; 1BRS (barnase–barstar) added 2026-09-29; 2BUJ (STK16) and 6LI0 (GPR52, with OPM's and PDBTM's membrane segments) added 2026-09-30 | — | 2026-09-23 | CC0 1.0 |
| `pdb_ccd/*.json` | wwPDB Chemical Component Dictionary, served by RCSB PDB | — | 2026-09-23 | CC0 1.0 |
| `pdbe_kb/*.json` | PDBe-KB (EMBL-EBI), ligand binding sites (2026-09-23) and interface residues (2026-09-24) | — | 2026-09-23 | CC BY 4.0 |
| `interpro/*.json` | InterPro (EMBL-EBI), site residues from the CDD member database | InterPro 110.0 | 2026-09-23 | see note below |
| `string/*.json` | STRING; HsTIM's 50 most confident partners at score ≥ 700, of 78, marked `truncated` 2026-09-29 (refetched: same rows) | 12.0 | 2026-09-23 | CC BY 4.0 |
| `chembl/*.json`, `CHEMBL90555.json` | ChEMBL (EMBL-EBI); CHEMBL90555 added to `chembl/molecules.json` 2026-09-24; `chembl/indications.json` (benznidazole, CHEMBL110) added 2026-09-28 | ChEMBL_37 (released 2026-05-01) | 2026-09-23 | **CC BY-SA 3.0** |
| `diseases/*.tsv`, `diseases/versions.json` | DISEASES (Jensen lab), the filtered rows of HsTIM's Ensembl protein ENSP00000229270 per channel | files of 2026-09-18 (knowledge, experiments) and 2026-09-20 (text mining) | 2026-09-28 | CC BY 4.0 |
| `open_targets/ENSG00000111669.json` | Open Targets Platform, HsTIM's gene (TPI1): its target record and first 20 of 483 associated diseases | data 26.09 | 2026-09-28 | CC0 1.0 |
| `open_targets/diseases/MONDO_0014221.json` | Open Targets Platform, triosephosphate isomerase deficiency: its first 20 of 252 associated targets, in Open Targets' order | data 26.09 | 2026-09-29 | CC0 1.0 |
| `orphadata/en_product6.xml` | Orphadata Science (Orphanet, INSERM), the disorders naming HsTIM (P60174); "Orphadata Science: Free access data from Orphanet. © INSERM 1999." | file of 2026-06-23 | 2026-09-28 | CC BY 4.0 |
| `reactome/P60174.json` | Reactome, HsTIM's pathways, reactions and pathway ancestors | release 97 | 2026-09-28 | CC0 1.0 |
| `clinvar/7167.json` | ClinVar (NCBI), 21 of the 249 variation summaries of TPI1 (GeneID 7167), chosen to cover each kind of record | Build260924-0125.1 | 2026-09-29 | Freely available; credit ClinVar |
| `gnomad/ENSG00000111669.json` | gnomAD (Broad Institute), 18 of the 1,668 variants of TPI1: protein changes on the canonical transcript, on isoform P60174-3's (inside and outside its own segment) and on a transcript UniProt does not state (12-6869106-A-G, added 2026-09-30), and non-coding ones; the gene's transcripts gnomAD annotates (added 2026-09-30) | dataset gnomad_r4 | 2026-09-29, 2026-09-30 | CC0 1.0 |
| `uniref/*.json` | UniProt's UniRef: the clusters of P52270 and the 7 members of UniRef90_P52270 | release 2026_03 | 2026-10-01 | CC BY 4.0 |
| `oma/*.json` | OMA (Dessimoz lab): the cross-references OMA states for P60174 and P52270, 7 of P60174's 3,090 orthologs, and UniProt's accessions for their Swiss-Prot entry names (`entry_names.json`, UniProt search); the OMA protein P52270 is mapped to (`protein_TRYCC03899.json`, added 2026-10-01) | OMA REST API 1.11 | 2026-10-01 | CC BY 4.0 (OMA; UniProt) |
| `sabdab/rcsb_pdb_annotations.json` | SAbDab (Oxford Protein Informatics Group), SAbDab2's annotations of the PDB (`api/rcsb-pdb-annotations`), the 9 antibody instances of 1YY9, 10BT, 9IJR, 9IJS and 9MQI | API 2.1.4 | 2026-09-30 | CC BY 4.0 |
| `gpcrdb/*.json` | GPCRdb, GPR52 (gpr52_human): its receptor entry, its residues with segments and generic numbers, and its seven structures | REST services | 2026-09-30 | CC BY 4.0 |
| `klifs/*.json` | KLIFS (Kooistra lab), STK16 (MPSK1, kinase 280): five entries of the kinase list (AKT1, EGFR, JAK1, JAK1-b, MPSK1), its information, its two structures (2BUJ chains A and B) and chain B's pocket residues | api_v2 | 2026-09-30 | no formal licence; the FAQ states the data is free and open for academia and industry |
| `gnomad/consequences.json` | gnomAD (Broad Institute), the consequence on every transcript of the six TPI1 fixture changes the isoform map would place (variant query) | dataset gnomad_r4 | 2026-10-01 | CC0 1.0 |
| `gnomad/pext_ENSG00000111669.json` | gnomAD (Broad Institute), the pext of TPI1 (GRCh38): 12 coding regions, each with its mean and its value in 49 GTEx v10 tissues, and the gene's transcripts with their exons | gnomad_r4 pext (GTEx v10) | 2026-10-01 | CC0 1.0 (gnomAD; computed from GTEx) |
| `gtex/tissue_site_detail_gtex_v10.json` | GTEx Portal API v2 (`dataset/tissueSiteDetail`, gtex_v10): the 54 tissues of GTEx v10, each with its id, name, tissue site and the ontology term GTEx states (UBERON, or EFO for a cell line); only those fields kept | gtex_v10 | 2026-10-01 | GTEx open-access data, free to use with acknowledgement of the GTEx Portal |
| `gnomad/ENST00000396705.json` | gnomAD (Broad Institute), the same variants as stated on TPI1's canonical transcript (version 10), 9 of its 1,404 | dataset gnomad_r4 | 2026-09-30 | CC0 1.0 |
| `clinicaltrials/studies.json` | ClinicalTrials.gov (NLM), the 16 studies ChEMBL's benznidazole indications cite | API v2 data of 2026-09-25 | 2026-09-28 | US government work; Source: National Library of Medicine |
| `clinicaltrials/references.json` | ClinicalTrials.gov API v2 `studies`, `filter.ids=NCT00123916`, native NCT/title/update and complete `referencesModule` projection, `pageSize=50`; the returned page has no continuation token. Original wire SHA-256 `c6e970a8df25c7d56892afc6eb118e573d981231d1cb27282bdbcca3cd0ead21`. Wrapped with the independently received native version metadata; that timestamp does not verify this page's release coherence. No linked publications/websites/participant data fetched by the registry query | API 2.0.5; `dataTimestamp=2026-10-05T09:00:05`; native study update 2020-03-03 is not a publication year | 2026-10-06 | Registry source terms: Source: National Library of Medicine. Citation/link declarations do not grant rights to linked articles or participant datasets |
| `europepmc/articles/pubmed__18585495.json` | Europe PMC REST `search`, `query=EXT_ID:18585495 AND SRC:MED`, `resultType=core`; native identifiers, title, all nine returned author entries, journal/pages/dates and declared links. Bibliographic projection only, abstract and unrelated fields omitted; no full-text endpoint or declared link consulted. Wire SHA-256 `941bf5f0fd76ea5c6a8ef61caea29cdaf3db600144c7070803a28f20a8f98482` | service 6.9, not article revision | 2026-10-06 | EMBL-EBI service terms, attribution expected; native article licence not stated; no article text retained |
| `europepmc/articles/pubmed__26323937.json` | Europe PMC REST `search`, `query=EXT_ID:26323937 AND SRC:MED`, `resultType=core`; native identifiers, title, all 22 returned author entries, journal/pages/dates and declared links. Bibliographic projection only, abstract and unrelated fields omitted; no full-text endpoint or declared link consulted. Wire SHA-256 `1ae9ef653c92f2bd11ab598129e61c70b30848594b9db0e60d35afd5cbe06d9a` | service 6.9, not article revision | 2026-10-06 | EMBL-EBI service terms, attribution expected; native article licence not stated; no article text retained |
| `europepmc/articles/pubmed__19753491.json` | Europe PMC REST `search`, `query=EXT_ID:19753491 AND SRC:MED`, `resultType=core`; native identifiers, title, all nine returned author entries, journal/pages/dates and declared links. Bibliographic projection only, abstract and unrelated fields omitted; no full-text endpoint or declared link consulted. Wire SHA-256 `6bcb3c63e4c4aae44d730317983dbc7d72f4eb8d6aa8419b2f6c4bd018dda7a9` | service 6.9, not article revision | 2026-10-06 | EMBL-EBI service terms, attribution expected; native article licence not stated; no article text retained |
| `unichem/*.json` | UniChem (EMBL-EBI); vincristine added 2026-09-24; lookups of the BindingDB monomers of the TIM fixtures by source id (`source31__<monomer>.json`) added 2026-09-25 | — | 2026-09-23 | see note below |
| `5978.json`, `66414.json` | PubChem (NCBI/NLM) | — | earlier | US public domain (NLM policy) |
| `europepmc/articles/pubmed__40832834.json` | Europe PMC REST `search`, `query=EXT_ID:40832834 AND SRC:MED`, `resultType=core`; selected native identifiers, title, all six authors (including declared ORCID/affiliation), journal, publication dates/pages, licence and full-text URL declarations. Abstract and unrelated core fields omitted; no full-text endpoint or URL consulted. Original wire SHA-256 `5b07a339c9135436a00abab958251418603da76173286f01585d992b0f0bdd48` | service 6.9, not article revision | 2026-10-04 | EMBL-EBI service terms, attribution expected; native article licence literal `cc by` retained without inferring a version or fragment permission. Bibliographic projection only; independent full-text licence verification for the existing annotation fixture is recorded below |
| `europepmc/P60174.json` | Europe PMC (EMBL-EBI) REST search `ACCESSION_ID:P60174 AND ACCESSION_TYPE:uniprot`: 25 of the 354 articles whose text states HsTIM's accession (the 24 newest and a preprint), ids and bibliographic data only (#92) | service 6.9 | 2026-09-29 | EMBL-EBI terms of use (no restrictions of its own; attribution); no article text is kept |
| `europepmc/annotations/PMC_PMC12400196.json` | Europe PMC Annotations API `annotationsByArticleIds`, `articleIds=PMC:PMC12400196`, `type=Accession Numbers`; complete seven-annotation response, including a located P60174 mention in a figure. Kontellas et al., *Triosephosphate isomerase from Fasciola hepatica: high-resolution crystal structure as a drug target*, DOI [10.1107/S2053230X25006454](https://doi.org/10.1107/S2053230X25006454), [PMC12400196](https://europepmc.org/articles/PMC12400196) | no release stated | 2026-10-02 | Article **CC BY 4.0**, verified in its full-text XML `license_ref`; annotation provider Europe PMC under EMBL-EBI terms, attribution expected. Only API text fragments are stored, not the full article |
| `europepmc/annotations/MED_18562316.json` | Europe PMC Annotations API, `articleIds=MED:18562316`, `type=Accession Numbers`; answered with an empty annotations list (#92). This does not establish that the article contains no accession | no release stated | 2026-10-02 | EMBL-EBI terms of use, attribution expected; no article text is kept |
| `chebi/compounds.json` | ChEBI 2.0 (EMBL-EBI) API, 7 entries: vincristine and ligands of the TIM fixtures, with the fields Sabueso reads (structure, classes, roles, definition, stars) (#83) | — | 2026-09-30 | CC BY 4.0 |
| `pubchem/titles__66414_3717450_2244.json` | Full unchanged public [PubChem PUG-REST property response](https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/66414,3717450,2244/property/Title,MolecularWeight,MolecularFormula,XLogP,TPSA,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,InChI,InChIKey,SMILES,ConnectivitySMILES/JSON), including native summary-page titles and existing compound properties. 2202 bytes; SHA-256 `546d7d0dfda191b17b90986531817b9a71541c593d3039c7f72c577816a95f1a`. | Source record revision unstated; retrieval is not a release | 2026-10-08T13:28:41.378512+00:00 | US public domain ([NLM policy](https://www.ncbi.nlm.nih.gov/home/about/policies/)); deposited data retains its depositor terms. PubChem/National Library of Medicine attribution. |
| `pubchem/structures.json`, `pubchem/3717450.json` | PubChem (NCBI/NLM) PUG REST: structure lookups (vincristine's SMILES, its SMILES without stereocentres, its InChI, a structure PubChem does not hold, an unreadable SMILES), and the property table of CID 3717450 (vincristine with undefined stereochemistry) (#93) | — | 2026-09-29 | US public domain (NLM policy) |
| `2NZT.json` | RCSB PDB entry | — | earlier | CC0 1.0 |
| `frozen_packets/*.json` | Historical `packet_aspects@5` literature index, generated with Sabueso's packet code at commit `0ec1423e8291f2eaab701ba942cd78266f3fd431` from the existing published `schema_0.3.10__P60174.json` card, before implementing `packet_aspects@6`; a derived compatibility artifact, not a raw provider response or a newly published package | `knowledge_packet@3`, `packet_aspects@5` | 2026-10-02 | Each part keeps its source's licence, as declared for the frozen card below |
| `frozen_cards/*.json` | Sabueso cards built from the fixtures above by a published release, kept to test that later versions still read them (#42). `schema_0.3.0__P52270.json`: the published conda package `sabueso=0.1.1` (uibcdf channel; card schema 0.3.0). `schema_0.3.1__P52270.json`: the release 0.2.0 candidate, built as its conda package and installed in a clean environment (card schema 0.3.1). Both were run on the UniProt, RCSB PDB and ChEMBL fixtures. `schema_0.3.2__P52270.json`: the release 0.3.0 candidate, built and installed the same way (card schema 0.3.2), run on the UniProt, RCSB PDB, ChEMBL, PDBe-KB and AlphaFold DB fixtures, with curated statements under a placeholder DOI (`doi:10.0000/frozen-card`) that claim nothing about the literature. `schema_0.3.3__P60174.json`: the release 0.3.1 candidate, built and installed the same way (card schema 0.3.3), run on the HsTIM UniProt, RCSB PDB, ChEMBL, PDBe-KB and AlphaFold DB fixtures, so that it holds AlphaFold models of isoforms. `schema_0.3.4__P52270.json`: the release 0.4.0 candidate, built and installed the same way (card schema 0.3.4), run on the TcTIM UniProt, RCSB PDB (every entry UniProt lists, with mutations, constructs and observed residues), ChEMBL (first 25 records), PDBe-KB, InterPro, AlphaFold DB, NCBI Taxonomy, BindingDB and UniChem fixtures. PubChem BioAssay is left out to keep the card small: its copies pull in every ChEMBL record they point to. `schema_0.3.5__P60174.json`: the release 0.5.0 candidate, built and installed the same way (card schema 0.3.5), run on the HsTIM UniProt, RCSB PDB (1HTI, 1WYI, 2VOM, 4UNK: author numbering, an author-defined tetramer, two mutants), ChEMBL (first 25 records), PDBe-KB, InterPro, AlphaFold DB, NCBI Taxonomy, BindingDB and UniChem fixtures. `schema_0.3.6__P60174.json`: the release 0.6.0 candidate, built and installed the same way (card schema 0.3.6), run on the same fixtures plus STRING, DISEASES (three channels), Open Targets, Orphadata, Reactome, ClinVar and gnomAD: isoforms, secondary structure, disease associations, pathways, and clinical and population variants placed in UniProt numbering. `schema_0.3.7__P60174.json`: the release 0.7.0 candidate, built and installed the same way (card schema 0.3.7), run on the same fixtures plus MedGen, MONDO (disease identity and hierarchy) and Europe PMC (text-mined accession mentions): every SourceAssertion states how it entered. `schema_0.3.8__P60174.json`: the release 0.8.0 candidate, built and installed the same way (card schema 0.3.8), run on the same fixtures plus gnomAD's pext and canonical-transcript answers, OMA's orthologs, and KLIFS, GPCRdb and SAbDab (not found for TPI1). `schema_0.3.9__P52270.json`: the release 0.9.0 candidate, built and installed the same way (card schema 0.3.9), run on the TcTIM fixtures of `schema_0.3.4__P52270.json` plus UniRef (its clusters, and the members of UniRef90_P52270, among them CL Brener's Q4DV43) and OMA (which maps P52270 to CL Brener's entry, so its orthologs are not joined). `schema_0.3.10__P60174.json`: the release 0.10.0 candidate, built and installed the same way (card schema 0.3.10), run on the fixtures of `schema_0.3.8__P60174.json` plus GTEx's tissue terms for the pext's 49 tissues; it also holds UniProt's Ensembl transcripts per isoform | — | 2026-09-24 | each part keeps its source's licence; the ChEMBL part is **CC BY-SA 3.0** |
| `frozen_cards/schema_0.3.11__P60174.json` | Sabueso 0.12.0 preliminary local Conda candidate from commit `01d5bf2474ac9765f162d88b3ab52c7d25714124`, archive SHA-256 `5cd6b0fb3a16a4da37d6d875f9b4a1e57282cb7de71b0e1e49007405030e86a7`, installed normally in a clean Python 3.14.7 prefix. Generated from the existing public UniProt P60174, RCSB 1HTI/1KLG/4UNK and Europe PMC PMC12400196 annotation fixtures above; retains located protein and derived structure mentions, source assertions and sealed quantities. Candidate compatibility record, not a published release claim; source/archive/writer checks are in `devtools/conda-build/receipts/sabueso_0.12.0_local_schema_freeze_2026-10-03.json` | card schema 0.3.11, frozen for candidate 0.12.0 | 2026-10-03 (generation; existing source retrieval dates above) | Each part keeps its source licence: UniProt and article fragments CC BY 4.0, RCSB CC0 1.0; Europe PMC attribution/EMBL-EBI terms |
| `frozen_cards/schema_0.3.12__P60174.json` | Sabueso 0.13.0 preliminary local Conda candidate from commit `c236e4f30db6c15e09e76ae0892ea2f71802665d`, archive SHA-256 `6f461bd1ca13ebfeda60cd724ec6b5af9fa5c46348e3fae82d36afac6dc3840c`, installed normally in an independent Python 3.14.7 prefix with public dependencies. Existing public UniProt P60174, RCSB 1HTI/1KLG/4UNK, Europe PMC PMC12400196 annotation and PMID 40832834 article-metadata fixtures; includes explicitly synthetic repository-authored text (`Synthetic schema example: UniProt:P60174`), not an article quotation or scientific finding, with unknown stored fragment rights. Retains original literal extraction/bibliographic support and sealed quantities. Source/archive/writer qualification: `devtools/conda-build/receipts/sabueso_0.13.0_local_schema_freeze_2026-10-05.json` | card schema 0.3.12, frozen for candidate 0.13.0 | 2026-10-05 (generation; existing source retrieval dates above) | Source parts retain UniProt CC BY 4.0, RCSB CC0 1.0 and Europe PMC attribution/EMBL-EBI terms; synthetic repository text follows MIT |
| `frozen_cards/schema_0.3.13__P60174.json` | Sabueso 0.14.0 preliminary local Conda candidate from commit `5fbd3edead997222bde702dba1c80d733a87c7fa`, archive SHA-256 `1e2f5e2bc1ec145428477e5838111f9e24f4fc606c465712eec028a809e1a8e7`, installed normally in an independent Python 3.14.8 prefix with the exact public minimum dependencies. Generated from existing public UniProt P60174 and RCSB 1HTI/1KLG/4UNK fixtures; stored retrieval dates remain 2026-09-23 and 2026-09-27 respectively, separate from generation. Retains native UniProt annotations, structures, original assertions and sealed quantities. Writer/source/archive qualification: `devtools/conda-build/receipts/sabueso_0.14.0_local_schema_freeze_2026-10-09.json`; card SHA-256 `f44dc762f25f1c280707e083f8718ef5390a98540bcd1fd2a306a7f7de38cd15`. This is candidate compatibility evidence, not stable publication. | card schema 0.3.13, frozen for candidate 0.14.0 | 2026-10-09 (generation; original retrieval dates above) | Source parts retain UniProt CC BY 4.0 and RCSB CC0 1.0; derived code follows MIT. Credit UniProt Consortium and RCSB/wwPDB; no protected original or private/pilot content. |

Modifications: the ChEMBL activity and molecule fixtures keep only the fields the clients
request and drop the `molfile` block; the UniChem fixtures keep the compound's InChIKey,
UCI and source list. The RCSB entries hold the fields the structure query requests, including per-instance
ligand neighbours. The rest are verbatim responses, re-serialised as indented, key-sorted
JSON.

## Attribution

### Native open article for located source review

`europepmc/fulltext/PMC12400196.xml` is the complete, unchanged public Europe PMC
`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12400196/fullTextXML` response,
retrieved on 2026-10-14. Georgios Kontellas et al., *Triosephosphate isomerase from
Fasciola hepatica: high-resolution crystal structure as a drug target*, Acta
Crystallographica F 81 (2025), 381–387, DOI
[10.1107/S2053230X25006454](https://doi.org/10.1107/S2053230X25006454), PMID 40832834.
Its native `license_ref` explicitly states
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No article revision is
inferred from retrieval time or service metadata. Europe PMC/EMBL-EBI attribution
and the article's own licence remain separate. The digest and public delivery
decision are recorded in `devguide/sources/fixture_delivery.json`.

Source-review examples identify selected XML fragments and prepare agent-authored
review drafts with original locators and short quotations; they do not alter this
native response or transfer findings between the organisms named in the article.

- **UniProtKB** — © UniProt Consortium, https://www.uniprot.org/terms, distributed under
  CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
- **RCSB PDB / wwPDB** — data files of the PDB archive are released under CC0 1.0
  (https://creativecommons.org/publicdomain/zero/1.0/). No attribution is required;
  crediting the depositors of each structure is good practice.
- **PDBe-KB** — PDBe-KB consortium, https://www.ebi.ac.uk/pdbe/pdbe-kb, CC BY 4.0, free for
  academic and commercial use. PDBe-KB asks users to cite the PDBe-KB consortium paper.
- **InterPro** — EMBL-EBI, https://www.ebi.ac.uk/interpro/. InterPro data is CC0 1.0, but
  InterPro notes that member-database signature collections may carry their own terms.
  The site residues in these fixtures come from **CDD** (NCBI), a U.S. government work
  under NLM policy, like PubChem.
- **STRING** — https://string-db.org, CC BY 4.0.
- **MONDO** — Mondo Disease Ontology, Monarch Initiative, https://mondo.monarchinitiative.org/,
  CC BY 4.0. Cite Mondo and the release (v2026-09-01).
- **SKEMPI 2.0** — https://life.bsc.es/pid/skempi2/, CC BY 4.0 (its terms of download and
  use). Cite: Jankauskaitė J, Jiménez-García B, Dapkūnas J, Fernández-Recio J, Moal IH
  (2019) SKEMPI 2.0: an updated benchmark of changes in protein–protein binding energy,
  kinetics and thermodynamics upon mutation. Bioinformatics 35, 462–469.
- **AlphaFold DB** — Google DeepMind and EMBL-EBI, https://alphafold.ebi.ac.uk, CC BY 4.0.
  Cite Jumper et al., Nature 2021 (AlphaFold) and the AlphaFold DB paper (Varadi et al.).
- **ChEMBL** — EMBL-EBI, https://www.ebi.ac.uk/chembl/, CC BY-SA 3.0 Unported
  (https://creativecommons.org/licenses/by-sa/3.0/).
- **UniChem** — EMBL-EBI, https://www.ebi.ac.uk/unichem/. EMBL-EBI adds no restrictions
  of its own beyond those of the original data owners, so the rights of the resources a
  UniChem record points to still apply. The fixtures hold cross-reference identifiers
  (for example a DrugBank accession), not the content of those resources.
- **PubChem** — NCBI/NLM. Works produced by the U.S. government are not subject to
  copyright in the United States; individual depositor contributions may have their own
  terms.

## ChEMBL share-alike

ChEMBL is the only source here with a share-alike clause. What it means in practice:

- The ChEMBL fixtures, including the trimmed copies, are redistributed **under CC BY-SA
  3.0**, with the attribution above. They are not relicensed as MIT.
- Sabueso's code is an independent work that reads these files. It is not an adaptation of
  ChEMBL data, so it stays MIT. The repository is a collection of separately licensed
  works, which CC BY-SA 3.0 allows.
- Anything that *is* an adaptation of ChEMBL data, such as a derived dataset built from
  these records, would have to be shared under CC BY-SA 3.0.
- Isolated factual values quoted in tests and reports (an IC50, a ChEMBL id, a compound
  name) are used to document measured behaviour.

This is a good-faith reading, not legal advice. Before a release that redistributes
larger ChEMBL extracts, or a dataset derived from them, confirm the scope with ChEMBL's
current licence statement.

## Adding a fixture

Add a row above with the source, its version or release, the retrieval date and the
licence. If the source is not already listed, check its licence and attribution first,
and record any restriction in `devguide/LICENSING_AND_COMPLIANCE.md`. Keep fixtures
trimmed to what the tests need.

## APPRIS native human gene exporter (development recovery)

`appris/annotations__ENSG00000111669.json` is the unchanged public default JSON
response from `https://apprisws.bioinfo.cnio.es/rest/exporter/id/homo_sapiens/ENSG00000111669?format=json`,
received on 2026-10-06 (exact original retrieval timestamp unrecorded): 252247 bytes,
SHA-256 `e9b7a1f300e76ac359bfc845af03b28f043c9c5b6db14b41a670dd6794de5a95`.
It contains 1010 native occurrences, 60 principal-isoform rows and 21 distinct
transcript references, including repeated/conflicting declarations. Native
genomic coordinates, source labels and note/score/flag strings are unmodified;
assembly/dataset/record/sequence revisions are not stated by these rows.
APPRIS's [official statement](https://appris.bioinfo.cnio.es/partials/license.html)
declares CC BY-NC-SA 4.0: credit APPRIS, link the licence, indicate adaptations,
retain noncommercial use and share-alike obligations. Linked method inputs and
publications retain independent terms; none are fetched with this fixture.

## SIGNOR native causal tables (development recovery)

The three `signor/relations__*.tsv` files are unchanged public responses requested
on 2026-10-06. The original exact retrieval timestamps were not recorded. Native
responses have no header and use the documented 28-field order plus an empty
trailing field. P60174 has three rows; its first native interaction is retained,
including regulator SRC, target TPI1 and the original publication/causal context.
P31749 with requested organism 9606 has 456 rows and native taxonomy literals
9606, 10090, 10116, 9534, -1 and blank; none are reassigned to the requested organism.
P31749 with requested organism 10090 returns exactly `No result found.` (16 bytes),
a source query declaration, not gene or biological absence and not HTTP failure.
Scores, residue/sequence strings, DIRECT flags, sentences and modification/complex
context remain source-served literals. Unknown scientific revisions stay explicit.

[SIGNOR's official documentation](https://signor.uniroma2.it/documentation/), read
2026-10-06, declares CC BY 4.0. Credit SIGNOR and contributing curators, link the
licence and indicate adaptations. Linked publications/input resources retain
independent rights and are not acquired with these responses. The curation manual
and SIGNOR 3.0 score documentation describe their own historical method scope;
neither establishes the current export's score model/version or sequence revision.

## HPA native single-gene summary (development recovery)

The public TPI1 response is retained unchanged from
`https://www.proteinatlas.org/ENSG00000111669.json`. This documented route supplies
only a subset of search data. Its RNA/protein categorical summaries do not supply
isoform-resolved assays or establish a measured protein identity. The reader keeps
all native quantitative/context fields; categorical mapping does not project
nTPM, nCPM, pTPM, intensity, concentration, scores or prognostic values.

Credit Human Protein Atlas, the specific gene/data URL and appropriate primary
publications; tissue context includes Uhlen et al. (2015),
doi:10.1126/science.1260419. HPA states CC BY 4.0 for copyrightable database parts
and requires respect for third-party input rights. No images, source code or
publication excerpts are included. The original exact retrieval time and native
dataset/gene/sequence revisions remain unknown.

## ClinGen native gene-disease validity export (development recovery)

The public `https://search.clinicalgenome.org/kb/gene-validity/download` CSV is
retained unchanged, including its native six-row preamble/header/separators and
all 3702 curations. `FILE CREATED: 2026-10-06` is a source file label, not an
observed retrieval time or scientific dataset/sequence revision. Classifications,
mode of inheritance, SOP, expert panel, report namespace and date remain native.
Legacy CGGCIEX report dates may omit timezone; UTC is not filled in.

ClinGen's curated content is dedicated under CC0 1.0. Credit ClinGen, source access
date when actually known and the original panels as requested. The report pointers
are not acquired; publications and external input resources retain separate rights.
No clinical recommendation, strongest classification, protein/isoform or variant
interpretation is inferred. An unlisted gene is distinct from a listed No Known
Disease Relationship declaration and an unavailable/failed response.

## HPO native gene-phenotype release (local unreleased qualification)

`hpo/v2026-09-01/genes_to_phenotype.txt` is the complete unchanged public
[HPO release asset](https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2026-09-01/genes_to_phenotype.txt),
read 2026-10-07 via the download linked by the official JAX website. It contains
333983 six-column rows, 20821704 bytes, SHA-256
`507a17bff9c49e6329fbd88b1f91734fa7e9fdea5c06304044c0892eb6ab248c`.
The first exact acquisition time was not recorded and remains unknown; the dated
release is known from the official redirect, independently of HTTP dates.
No row is rewritten or removed. Credit the Human Phenotype Ontology Consortium
and retain `v2026-09-01`; the supported dataset description is https://hpo.jax.org/.

`hpo/license.component.html` is unchanged public data-licence support from the
[official website source](https://github.com/TheJacksonLaboratory/hpo-web/blob/a85f0fa92835a9f6a37881b89b6260ca3b9f4960/src/app/static/resources/license/license.component.html),
read 2026-10-07, 1764 bytes, SHA-256 **cdd288c39f224b07642e59c1b4cd3f81d9f4210cbd4dbf18428dd2749be6c8cd**. The old website route
returns 404; this source is a data statement, not the web software licence.
The HPO Consortium requires acknowledgment/citation, version/date for public
files and unchanged content/logical relationships, and requests website credit/logo.
OMIM/Orphanet and other inputs remain separately scoped. A native disease namespace
is not per-occurrence contributor/publication attribution. These original files
remain local unreleased qualification artifacts; no public derivative collection
or blanket redistribution/commercial-use grant is claimed. Source terms retain
`HPO-CONSORTIUM` with unknown automated-use/sharing and internal retention.

## 3did domain-motif native export (local unreleased qualification)

`3did/3did_dmi_flat.gz` is the complete unchanged public native gzip linked from
[3did's download page](https://3did.irbbarcelona.org/download.php), read 2026-10-07
from https://3did.irbbarcelona.org/download/current/3did_dmi_flat.gz after its
public download access recovered. Original gzip: 149724 bytes, SHA-256
`ef3d339e7643efb3ae2ed1857ecbbc3c350d3cf08ff9ef79daea4c667907bdfb`.
Decoded native text: 826632 bytes, SHA-256
`85fd69fb419b994eb4c506c466e469a22af3bc16af7b042da64f2c58637c93aa`.
All 1657 pairs and 17478 structural occurrences remain unchanged. The first
probe's exact acquisition time is unknown; native scientific/PDB/Pfam/sequence
revisions are unstated, and pattern dates/current-route labels do not replace them.

Credit 3did and the Structural Bioinformatics and Network Biology Group at IRB
Barcelona; retain native Pfam/PLoS_CB_2010 labels and exact structural-instance
support. The provider's public download/about statements do not specify a separate
export-data grant. Terms remain NOT-STATED, with software/publication and input
rights separate. This original factual gzip remains local unreleased qualification
material; no public fixture or derivative-collection distribution grant is claimed.
No coordinates, source publications, DDI contacts or HMM profile data are included.
## PDBTM native XML (local unreleased qualification)

`pdbtm/1c3w.xml` is the complete unchanged public native response from
https://pdbtm.unitmp.org/api/v1/entry/1c3w.xml, first probed 2026-10-06 and
independently matched 2026-10-07. It is **6866 bytes**, SHA-256
`37ae24e30f12457eb91fb9198c5a7a6643e46e33efa0c039048784ff5b7ac55e`, with its
original ISO-8859-1 declaration and entire COPYRIGHT statement retained. Exact
first retrieval time is unrecorded; fixtures keep `retrieved_at=None`. A live
development receipt records 2026-10-07T20:09:18+00:00 separately from this fixture.
All three chain occurrences and 45 region declarations are preserved, together
with history, raw scores, biological/membrane matrices and original sequence text.

The embedded statement identifies PDBTM/Institute of Enzymology, Budapest and
conditions nonprofit-institution use on unchanged content and retained copyright;
use by and for commercial entities requires an agreement. `PDBTM-CONDITIONAL`
records this conditional statement with unknown automated use/sharing and internal
retention. This original remains local unreleased qualification, not a publicly
redistributable fixture or MIT-licensed data. Public derivative collections,
commercial use and input-resource rights require separate qualification. Each
mapped occurrence carries the entire unchanged XML/copyright; XML character
decoding does not rewrite the file. Matrices/raw scores remain uninterpreted, with
units/axes unqualified; no coordinates, transform execution or canonical mapping.

## ProBiS native reference-chain catalog (local unreleased qualification)

`probis/nrpdb-2015-07-31.txt` is the entire unchanged public artifact linked from
[ProBiS-Database](http://probis.cmm.ki.si/?what=database), received from
[the native catalog URL](http://probis.cmm.ki.si/download/nrpdb-2015-07-31.txt)
on 2026-10-07. Its **1003440 bytes**, **42270 headerless five-column rows** have
SHA-256 `2a4f3dd8f3f186f482541c51f177899cbf3c174cc21838dd6a9b185646c12c0a`.
The first probe's exact time is unrecorded; fixture time stays `None`. Independently
matched live receipt: **2026-10-07T20:36:55+00:00**. The dated filename is an
artifact label, not a qualified dataset/PDB/sequence revision.

All padding, gaps, repeated chains and unknown column meanings remain unchanged.
Three `5a2q.h` and five `2ww9.L` occurrences are preserved; `1ytb.A` listing does
not repair a documented `1ytb.B` alignment example. No separate data grant is
qualified (NOT-STATED); software/article licences and input rights remain separate.
This original factual artifact is local unreleased qualification, with automated
sharing unknown; no public fixture or derivative-collection grant is claimed.

## Interactome3D native protein metadata (local unreleased qualification)

`interactome3d/human__2024_12__representative__proteins.dat` is the entire unchanged
public artifact linked from the provider's [archived directory](https://interactome3d.irbbarcelona.org/downloadset.php?path=representative&queryid=human&release=2024_12).
[Native file](https://interactome3d.irbbarcelona.org/data/previous_releases/2024_12/human/representative/proteins.dat)
received 2026-10-07: **1618274 bytes**, **18000** fourteen-column rows, SHA-256
`bb1671bedacab71e528a18c1d7f662046fe61d299b70da791f1b61325098d83d`.
First probe exact time is unrecorded; fixture `retrieved_at=None`. Independent live
match: **2026-10-07T20:51:35+00:00**. The selected archive label is separate from
unstated native export/PDB/sequence revisions.

The unchanged table retains 10636 Structure and 7364 Model occurrences, including
251 whitespace-chain rows and multiple representative structures/models per accession.
Native [help](https://interactome3d.irbbarcelona.org/help.php) qualifies identity/
coverage as percentages; scores and endpoints remain distinct. The provider/about
page does not qualify a separate data grant (NOT-STATED). Attribution retains
Interactome3D/IRB Barcelona, artifact scope, original row/hash; software/articles
and input rights are separate. This original factual artifact stays local unreleased,
with automated sharing unknown; no public fixture/derivative redistribution grant.

## Pharos target metadata (2026-10-07, local unreleased qualification)

`pharos/target__P60174.json`, `pharos/target__P31749.json` and
`pharos/target__P00000.json`
are unchanged public responses from the provider-documented
https://pharos-api.ncats.io/graphql endpoint. Query: `SabuesoTarget($accession:
String!) { target(q: {uniprot: $accession}) { name sym uniprot tdl fam } }`.
They preserve native five-field targets and explicit null respectively; no search
or aggregate source is acquired. Provider/NIH IDG attribution and contributing
source rights remain separate. A separate data grant is NOT-STATED; article/code
licences are not assigned to outputs. Keep original factual fixtures local and
unreleased pending applicable sharing qualification.

## DepMap 24Q4 public release (2026-10-07)

`depmap/24Q4__Model.csv`, `depmap/24Q4__README.txt` and
`depmap/24Q4__figshare_27993248__v1.json` are unchanged public provider artifacts.
Metadata: https://api.figshare.com/v2/articles/27993248/versions/1;
release DOI: https://doi.org/10.25452/figshare.plus.27993248.v1.
Model.csv: https://ndownloader.figshare.com/files/51065297, 645696 bytes,
SHA-256 `b7a0c1385e6cef30132b56aff61f1261d11e3f490490b355c430d32ee0dbdcfa`,
MD5 `675210d17675f3517b0ce39a3c274f16` (matches provider metadata).
README: https://ndownloader.figshare.com/files/51065795,
SHA-256 `f744a5cf5c112e01276e772679157aac8e85cdc4a8f6d3b86d808e3bfd332891`.
The native article declares CC BY 4.0. Credit DepMap, Broad Institute (2024),
DepMap 24Q4 Public, article version 1, the DepMap portal and program. These are
public model descriptions, not private or pilot data. This selected publication's
licence is not extended to other releases or collaborator files.

## BRENDA EC-class descriptions (2026-10-07)

The public prototype linked by [BRENDA](https://brenda-enzymes.org/download.php)
uses [the DSMZ endpoint](https://sparql.dsmz.de/brenda) and its D3O schema.
These three original JSON responses select `ec label name description` for
one exact EC URI, with independent OPTIONAL systematic-name and description
bindings, without LIMIT or OFFSET. Queries and RDF terms are reproduced by
`sabueso.mappings.brenda.response_query`; this is descriptive class context,
not kinetic measurements or a protein assignment. EC 5.3.1.1 has a native empty
description; 2.7.1.1 has a nonempty description; 7.99.99.99999 has zero solutions.
The no-match probe is not an assigned biological class or an absence assertion.

Original SHA-256 hashes respectively:
`9c1b4c3cc16247040a01d6112c420a7e06cae0342498a4e3e1af7120424eff30`,
`e87e87600b3e42395afa8b9c045462667494faa34dee53543ba2be88e4903b30`,
`c638f070fbc8317157ddd05f2ae6a46f59e7ab1228044324a60f7cedd3db835b`.
[Provider data and online-use terms](https://brenda-enzymes.org/license.php)
state CC BY 4.0. Credit BRENDA, DSMZ Digital Diversity and
[Hauenstein et al. (2026)](https://doi.org/10.1093/nar/gkaf1113).
SOAP registration and bulk-file active acceptance are separate unused routes.
The main website's release is not a native prototype dataset revision.

## FDA OOPD detailed pages (2026-10-08 UTC, 2026-10-07 local)

Original public [page 476815](https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=476815)
and [page 106597](https://www.accessdata.fda.gov/scripts/opdlisting/oopd/detailedIndex.cfm?cfgridkey=106597)
are preserved without edits, including original CRLF and nested HTML tables:

- `fda_orphan/page__476815.html`: 30002 bytes, SHA-256
  `549798ff1dada54a7d34d52876d13962136392ef903db59dda2fda2a196e08f4`;
  one designation and one empty native approval table.
- `fda_orphan/page__106597.html`: 36357 bytes, SHA-256
  `3afd99f87e17caeaf2d91469c76c2db7b61e16ae93060f8f6c3d121ce9998d23`;
  one designation and three separate marketing-approval tables.
- `fda_orphan/search_form.html`: unchanged [public search form](https://www.accessdata.fda.gov/scripts/opdlisting/oopd/index.cfm),
  34331 bytes, SHA-256
  `6bbe6fe07e08d5361d16d0eff3ce03f3f0895308cdf263fe1b6539e4fd645b65`.
  An HTTP-200 form returned instead of requested data must fail reader qualification.

Native acquisitions occurred at 05:25:35 UTC for the detailed pages and 05:23:39 UTC
for the form. Scientific dataset/record revisions are unstated. Native procedural
dates, N/A, blank exclusivity fields, repeated product-name strings and sponsor
address qualifiers remain original. The page locator is not a stable designation,
product or protein identifier and is not echoed by the HTML.

The explicitly linked [FDA website policy](https://www.fda.gov/about-fda/about-website/website-policies)
states public-domain reuse unless otherwise noted; independent contributing-source
and other rights remain separate. Credit to U.S. Food and Drug Administration /
Office of Orphan Products Development is requested. Retain the source URL and
acquisition date. This is not an openFDA CC0 grant or current clinical advice.

## TTD target listing (2026-10-07, local unreleased qualification)

The [official download component](https://ttd.idrblab.cn/full-data-download)
explicitly links the original public
[`P2-01-TTD_uniprot_all.txt`](https://ttd.idrblab.cn/files/download/P2-01-TTD_uniprot_all.txt).
The full unchanged file is 525950 bytes, SHA-256
`74b2dbb4c03e14b01d02b54bdce45507da0da1e457859e1669cdf76b39feb22e`.
Its native header states version 10.1.01 (2024.01.10); 4298 target blocks have
TARGETID/UNIPROID/TARGNAME/TARGTYPE fields, including 613 NOUNIPROTAC values.
UNIPROID is not uniformly an accession; native entry names, inconsistencies and
placeholders are not repaired. Native TARGTYPE is source context, not a derived
clinical or druggability finding. The source footer reserves rights and no
separate data grant is qualified. NOT-STATED keeps automated use/sharing unknown;
original factual qualification stays local unreleased. Article/software rights
are not assigned to this export. Credit TTD, IDRB/Zhejiang University and
BIDD/National University of Singapore, retaining the full native header and URL.

## iPTMnet native report pages (2026-10-07)

Original public [P60174](https://research.bioinformatics.udel.edu/iptmnet/entry/P60174/)
and provider-linked sample [Q15796](https://research.bioinformatics.udel.edu/iptmnet/entry/Q15796/)
reports are unchanged HTML, including full source group tabs and hidden
score/publication/source content. Bytes/SHA-256 respectively:
95748 / `13c3f90770bff2cbc34463508d453758fe518ebf9069491d229a7a623d6a9f90`,
166093 / `82833fa0fa7a1a6da2a9a7821c79eb8592211b7b86056cc53ad5584f1c681300`.
P60174 has 72 rows (62/7/3 by group); Q15796 has 60 (42/15/3), including an
unplaced modification and native score0. Rows retain source aggregate support;
no canonical placement, independent enzyme/source/PMID pairing or curated/
inferred classification is reconstructed. Dataset and sequence revisions stay
unknown. Other report sections are raw received support, not separately mapped.

The [official provider licence](https://research.bioinformatics.udel.edu/iptmnet/license)
states database CC BY-NC-SA 4.0, separate from software/article rights. Credit
iPTMnet, University of Delaware / Protein Information Resource and Georgetown
University. Retain licence, native URL and contributing source/publication pointers;
noncommercial and share-alike conditions apply and no endorsement is implied.
Original provider bytes are unchanged; parser projections are Sabueso's extraction.
Independent contributing-source rights remain separate. No scripts execute and no
linked content is acquired. The REST API's earlier failures remain independent.
