# Scientific dossier criterion integrity (#146)

Owner: [Sabueso #146](https://github.com/uibcdf/sabueso/issues/146).
Coordination: #112; scientific consumer acceptance: #132.
Scope: development example and regression tests, not the published SDK/schema.

## Reproduction and impact

At source `391ba08fb8b3dacfbc85743505536397e2da9a11`, the independent dossier
reader checks overall status against the recorded check statuses but does not
fully bind those checks to their original inputs. A copied public TcTIM/HsTIM
dossier can retain exact cards, qualifiers and quantities while changing a failed
assay/structure's check values and statuses to claim that all criteria are met.
Regenerating Markdown and rehashing both files makes the altered report pass.

Five independent negative cases reproduce the gap: empty assay checks, coherent
promotion of an ineligible assay, a changed expected measurement type, an invented
unknown reason, and coherent promotion of a failing structure. All five tests
fail against the old reader because it exits successfully. Earlier mutation
tests could instead fail on stale human output or on the later manifest's hash
of the original manifest, masking the missing scientific guard.

## Correction and boundary

The producer and reader share the unchanged original `@1` criterion checks.
Reading compares complete records, including their keys, values, expectations,
statuses and unknown reasons. Assay inputs come from the exact pinned relationship;
structural criterion inputs come from the saved structure item and declared
positions. Resolution checks explicitly decode saved `{value, unit}` records
through PyUnitWizard, retaining the original angstrom threshold. JSON equality
distinguishes boolean results from numeric values.

This is validation of the recorded criterion computation, not a new scientific
view, structural reclassification, source acquisition, curation or credit. It
does not authenticate every upstream structural classification or article body.
The SDK, source adapters, schemas, fixtures and criteria/rule identifiers remain
unchanged. Historical dossier `@1` and `@2` retain their original results and
rendering; old scientific/CI receipts keep their original scope.

Negative tests isolate the original stage and regenerate its human output and
manifest. The five new cases require the specific criterion-input rejection,
rather than any error. Genuine historical bundles produced before this fix also
pass independent reading, with original report/runtime/Markdown hashes and
reference bytes unchanged. New producers/readers/reacquisition pass all 25
dossier cases with twelve pytest-receptor workers.

## Qualification and remaining work

The first full local-original run was not a passing checkpoint: 6,274 cases
passed, 24 failed and seven errored when the task's `/tmp` results exhausted
disk quota. All reported failure groups were quota or subsequent SQLite I/O
errors. Its completed, task-owned temporary directory was removed after retaining
the summary and failed-node inventory. Recovery uses an explicit disposable test
directory on the repository filesystem, in the same Python 3.14 environment.
That nested layout exposed parent-conftest leakage in two synthetic fixture
collection tests: a second run passed 6,303 cases but failed those two before
collection. The child runner now sets `--confcutdir` to its own project, and all
twelve fixture-delivery cases pass with the nested layout (3.16 seconds). This
test-only isolation change preserves the actual public/local fixture gates.

Full local and exact-source hosted qualification are pending. This fix does not
supply missing primary assay methods or scientist acceptance. Those remain
separate dependencies, documented in the [method-access review](../pending_proposals/primary_assay_methods_review.md).
