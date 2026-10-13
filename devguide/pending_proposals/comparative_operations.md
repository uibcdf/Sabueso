# Observed comparative view executions (#108)

Development observes `Card.sequence_differences`, `Card.variant_tissue_usage` and
`Card.isoform_tissue_usage` only inside an explicit `sabueso.attribution()` context.
`AttributionRun.operations` retains independent records in
`sabueso.comparative_operation@1`, separate from packet `records`, source
`acquisitions` and literature events. Nested contexts each retain the event once;
context isolation remains Python's ContextVar boundary. Plain calls, explanations
and saved readers stay inert. No new public arguments or card fields are added.

Each event binds its execution identity/times, original producer, requested
parameters, applied rule and exact input pins to the unchanged return's canonical
digest. A repeated calculation retains a distinct execution identity even when
its scientific result is identical. Missing/unequal sequences and evaluated-empty
views are completed knowledge limits, not scientific execution failures. A genuine
scientific exception retains a failed host event with no completed credit and is
re-raised unchanged. Invalid public arguments stop before execution observation.

`comparative_input_scope@1` declares selected input-field support; the isoform
engine separately reads all stored tissue-specificity assertions, including those
without a selected field. References retain their original card pins, source-record
versions/bases, acquisition labels and retrieval times. Missing, misbound or
nonmatching assertions remain explicit; they receive no false resource credit.
Input-state changes or unavailable pins refuse completed attribution while
preserving the scientific return. This scope is not reconstructed row-level
mapping, exact source-request membership or independently verified database release.

The existing public Ackredit capture/scope/registration API records executed
software and reused stored knowledge, contributing to the application's session
and enclosing capture. Resource descriptions come from the existing offline
bibliography. Missing descriptions and underlying method/entry publications stay
in `bibliography_gaps`, separate from scientific `support_gaps`. No new citation
metadata, provider access, auto-discovery, source operation or Nextia Evidence is
invented. Provider absence/failure preserves completed results and host records
with the existing SMonitor attribution diagnostic.

Packet composition and comparative execution share one operation-independent
source-record declaration. A public mixed workflow reproduced conflicting notes
under one stable source-record id; the shared declaration fixes both execution
orders without changing resource identity or original saved sidecars. Current
operation contexts state the actual use, rather than putting it in shared metadata.

Twenty-six public/synthetic regressions cover real provider credit,
current/historical public views and nested tissue-key rules, genuine fresh-process
absence, changed/missing/misbound input support, scientific/provider failure,
nested reuse and an independent inert saved reader outside the checkout.
Local selected qualification passes 190 cases in 42.37 seconds with twelve
pytest-receptor workers. All 6,208 local-original offline cases pass in 167.94 seconds, with 13 expected
fixture warnings and fatal SQLite/unraisable guards. Shape/schema (1,627 paths),
fixture delivery, registry, dependency preflight, MOLI/canonical guide, style,
warning-fatal Sphinx and 212 relative links pass. Nine earlier source/release
receipts remain byte-exact. Implementation `31b6255` and CI policy `c7916cf` are
published on development `main` with `[skip ci]`, as
[recorded in #112](https://github.com/uibcdf/sabueso/issues/112#issuecomment-6149457079).
Exact-source remote qualification is pending under the
[approved deferred CI block](deferred_ci.md). Qualify the resulting final block
head using [the full recovery route](../TESTS.md#recovering-deferred-ci).
The new module also runs in installed public-Ackredit CI. Card schemas, original
fixtures and scientific rule outputs remain unchanged; source access coverage stays
38 families. Published 0.14.0 is unchanged.

The next [persisted journey slice](comparative_journey_attribution.md) integrates
these records into public example `@3`, with ordinary views/explanations and
original source/workflow attribution. Its inert reader checks result/support/
credit bindings, retains historical execution gaps and exports saved bibliography
after reacquisition. This slice has its own local checks and deferred remote scope;
the published implementation above is not a passing receipt for the new example.

Broader comparative/explanation/other-result observation, complete verified
resource bibliography and MOLI ProjectRecord/Recorda coordination remain
[#108](https://github.com/uibcdf/sabueso/issues/108). Installed-artifact qualification
and human/consumer usefulness remain separate under #112/#132. The existing staged
release proposal remains separate from source publication.
