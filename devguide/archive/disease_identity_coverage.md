# Identifier-scoped disease identity coverage (#144)

Archived on 2026-10-13 after exact-source qualification of development main.
Published 0.14.0 and historical stored rules/pins remain unchanged.

Historical `disease_grouping@1` and `@2` treat any MONDO enrichment record as
proof that identity was queried. A blocked condition can therefore be labelled
`no_stated_equivalence`; counts and another identifier's answer do not establish
its scope. Both historical algorithms remain explicitly selectable and unchanged.

Development defaults to `disease_grouping@3`, with
`disease_identity_coverage@1` and `disease_group_explanation@3`. Every statement
keeps its stored identity paths and per-identifier source steps. Completed exact
MONDO `ungrouped` diagnostics retain no-equivalence/obsolete outcomes. MedGen's
exact `missing` concept list describes a missing UID; it does not establish a
MONDO query. A concept without a stored UID blocks that acquisition step. A direct
stored MONDO equivalence remains valid independently of the indirect route. Blocked requests,
unavailable access, unknown identifier scope and mixed outcomes remain distinct.
A successful source-wide count or an unscoped not-found exception is not proof
that this identifier received an empty answer. Unavailable request context without
identifier scope never claims an individual query was attempted or failed.

Positive stored identity and alternative/conflicting paths remain available even
when another access attempt failed. Failed/blocked diagnostics cannot erase an
upstream named MONDO identifier. The grouping rule retains the historical path
and granularity policy; coverage does not invent equivalences, SourceAssertions,
Evidence or source operations. Rows refer to exact stored enrichment indexes;
explanations bind their context to the original card pin. Unknown historical scope
is not backfilled. No new Card fields, schema change or acquisition is needed.

New packets declare `packet_aspects@7` and retain identity paths/coverage beside
named disease statements. Full and index terms adapters support mappings @6/@7;
index @6 explicitly reconstructs grouping @2 and its historical rule declaration.
Stored @6 packets remain exact; packets with different mappings are not compared.
The shared query/packet format is unchanged. Consumer acceptance stays #132.

Local qualification passes: 39 new public/synthetic regressions, 253 selected
cases in 77.15 seconds and all 6,182 local-original offline cases in 155.03 seconds,
with 13 expected warnings, twelve pytest-receptor workers and fatal SQLite/
unraisable guards. An independent producer/reader outside the checkout retains
seven card pins and four full/index packet pins with source access and fresh
credit forbidden. Original @1/@2 outputs and @6 packet facts equal the prechange
algorithms; explicit new materialization declares its current runtime without
rewriting stored reports. Style, shape/schema (1,627 paths), source registry, fixture
delivery, dependency preflight, MOLI/canonical guide, warning-fatal Sphinx and
174 relative links pass. Eight prior source/release receipts remain byte-exact.
Source `cf5900db748c6ddfea1a6ca7a3e727ffc4d6c3b6` passes
[15/15 exact-SHA CI jobs](https://github.com/uibcdf/sabueso/actions/runs/38372344354)
and [governance](https://github.com/uibcdf/sabueso/actions/runs/38372344308).
The [source receipt](disease_identity_coverage_checkpoint.json) independently
verifies complete GH Run Receptor captures and 13 terminal test summaries:
nine public offline lanes each pass 4,629 cases (10 native skips, 26 online
deselections), and four installed public-Ackredit lanes each pass 1,267 cases.
After installing the source editable, 79 selected cases pass in 7.37 seconds.
All six participating imports/metadata match their local checkouts outside the
repository; all fourteen installed MolSysSuite member distributions are editable.
The qualified producer is `0.14.0+32.gcf5900d`; later documentation metadata does
not replace its original receipt. This is source qualification; full installed
artifact delivery and human/consumer acceptance remain separate. The new regression
module is also included in installed public-Ackredit CI outside the checkout.
Published 0.14.0, frozen cards and schemas remain unchanged. No new provider
queries or private/pilot fixture content.

Owning issue: [#144](https://github.com/uibcdf/sabueso/issues/144).
Next: derived comparative operation and complete bibliography
[#108](https://github.com/uibcdf/sabueso/issues/108), followed by the existing
candidate/staging/installed-package route for a substantial release proposal.
