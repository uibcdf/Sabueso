# Scientific usefulness review and assay-context inspection (#132, #112)

This bounded review follows the approved question-driven route in
[consumer acceptance](consumer_scientific_acceptance.md), the public
[use cases](../USE_CASES.md) and the [scientific dossier](scientific_dossier.md).
Original saved inputs and documented consumer needs were inspected read-only.
Private inventories, input hashes, notebook content and detailed review results
remain private. No new scientific provider query or project Evidence was produced.

## Supported answers and remaining work

| Review question | What can be inspected | Remaining need and owner |
| --- | --- | --- |
| Which source entry is being used? | Resolution decisions, source-stated identity links, alternatives and exact original pins | A scientist checks entry/taxon applicability. Correspondence computation belongs to modeling; related entries are not silently merged. |
| Which structures meet declared criteria? | Assembly basis/disagreement, sequence differences, constructs, coverage, numbering, resolution quantities and region support | A scientist declares the relevant region/criteria and chooses project models. Existing source inventory and pre-screening do not perform model preparation or geometric alignment. |
| What experimental context accompanies a measurement? | Original measurement, source record, assay/target identifiers, organism, confidence, stated variant, document pointers and flags | These fields were retained but insufficiently visible in the readable dossier. The new inspection addresses that gap; actual protocol comparability remains human review. Missing mapped fields do not prove source absence. |
| What located statements support an interpretation? | Original bibliography and supported accession occurrences | A mention alone does not establish a mechanistic statement. Rights-qualified source text and human curation are required for substantive source claims; Nextia owns project interpretation as Evidence. |
| Can the exact original knowledge be reused? | Sealed snapshots, pinned support, original reports and credit through independent reading | Shared consumer-owned receiving and staged installed-release qualification retain separate acceptance. The new dossier is not automatically covered by MOLI's comparative receiving example. |

## Chosen improvement

Make retained assay context directly inspectable before adding a connector or
query facade. The existing SDK already preserves the needed qualifier fields;
this is an example inspection improvement, with no API/card/schema/source change.

New `sabueso.scientific_dossier_example@2` adds a per-record
`stored_assay_context_review@1`. It states the presence or absence of named paths
**in the original saved qualifiers**, separately from record eligibility. Its
human table exposes source activity/target identifiers, assay identifiers/types,
organism/taxon, confidence, variant annotation, publication pointers, original
stated values/bounds and validity/duplicate notes alongside exact support.
The full original qualifiers remain the source of values; no text-based condition
inference, cross-record assay identity, ranking or selectivity is introduced.

An eligible direct-target IC50 equality record can still lack an assay identifier
or protocol context. A source-reference protein sequence does not establish the
construct used in an assay. A missing variant annotation does not establish a
wild-type target. Matching assay identifiers, descriptions or units do not by
themselves establish equivalent protocols. Protocol curation remains explicitly
absent and experimental comparability is not established by this review rule.

Original `@1` reports remain readable in their original shape and rendering.
`produce --legacy` exercises that route; reacquisition keeps whichever original
format was produced. No context review is retrofitted into old reports. The reader
checks a new context review against its exact original relationship qualifiers,
retaining the original eligibility rule, quantities, support and producer/credit.

Twenty public fixture cases cover the dossier, including native ChEMBL assay/
document context, explicitly missing BindingDB fields, historical format/read/
reacquisition and rejection of altered context or invented protocol curation.
The genuine earlier public dossier was also read with the updated example while
retaining its original producer, results and pins. These are technical inspection
checks, separate from scientist acceptance of an experimental comparison.

## Next acceptance and delivery

Local checkpoint: Python 3.14.7 in the existing editable workspace passes twenty
selected cases and all 6,286 local-original offline cases (144.65 seconds, nine
expected fixture warnings), using twelve pytest-receptor workers and fatal
SQLite/unraisable guards. Ruff format/check, fixture delivery, dependency preflight,
local/canonical MOLI governance and warning-fatal Sphinx pass. Genuine historical
`@1` reading and unchanged source values/eligibility are separately verified.

Hosted checkpoint: the [source receipt](scientific_usefulness_checkpoint.json)
qualifies `1bd8c051d848ec1d979b45402b62da0e033a4204`, published without `[skip ci]`.
[CI](https://github.com/uibcdf/sabueso/actions/runs/38527586847) passes 15/15 and
[governance](https://github.com/uibcdf/sabueso/actions/runs/38527587001) passes 1/1.
Every full gh-run-receptor capture member and all thirteen test summaries are
independently checked. Nine public OS/minor lanes pass 4,733 cases each (ten native
skips, 26 online deselections); four installed public-Ackredit 0.9.0 lanes pass
1,391 each. Ruff and coverage publication pass; external service visibility is not
independently qualified. Historical receipts remain original, and this development
source/receiving scope does not qualify a future staged release artifact.

Review the displayed context and actual source protocols before comparing
measurements. Curate substantive source statements when suitable text/rights and
a curator are available. Extend SDK behavior only for a demonstrated missing
support or inspection path. Keep source limitations and consumer decisions with
their respective owners; do not import project conclusions into Sabueso knowledge.

The [0.15.0 proposal](release_consolidation_0150.md) groups the accumulated
integrity/observation work and this bounded inspection improvement. The source
checkpoint, final candidate/version decision, staging artifact, installed OS/minor
matrix, schema freeze and publication route remain distinct steps. This review
does not create a release, approve a project model or close #132/#112.
