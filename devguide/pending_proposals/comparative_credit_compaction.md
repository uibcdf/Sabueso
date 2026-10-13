# Compact comparative credit during consumer hand-off (#108, #112)

The MOLI receiving exercise exposed excessive serialization of comparative
attribution. Every stored-knowledge, description and method use repeated the
complete operation input scope. With many SourceAssertions, the result/workflow
payload therefore grew roughly with the square of supported statements.

An entirely public synthetic regression reproduces the issue using 64/128
independent gnomAD-labelled assertions. Before the fix, combined host/workflow
JSON grew from 4,908,917 to 17,471,157 bytes and failed the proportional-growth
bound. These are synthetic serialization measurements, not private pilot metrics,
CPU/memory measurements or a general complexity claim for scientific algorithms.

New records use `sabueso.comparative_operation@2`. The complete exact input scope
remains in `record.inputs`; each bibliographic use carries
`comparative_input_scope_reference@1`, naming that execution, its `inputs` field
and the SHA256 of its canonical scope. Each actual resource use still retains
its own exact Card pin, field/assertion reference, source-record identity/label,
retrieval context and descriptive-method scope. Selection drops no assertions.
The host sidecar must accompany detached credit for full scope verification.

This replaces duplicated serialization, not scientific values, algorithms,
SourceAssertions, card fields, schemas, quantities or source access. Resource,
method-description and executing-software roles remain distinct. The input-scope
reference is technical derivation context, never a new SourceAssertion or Evidence.
Historical `@1` contexts stay original. The owner reader branches on the declared
version, verifies either the complete historical context or the new exact
reference/hash, and never regenerates metadata or compacts a saved original.

Four additional regressions cover proportional serialization, misbound context
owner/hash and the original full-context format. The complete selected scope
passes 172 cases in 67.25 seconds; the full local-original offline suite passes
6,266 cases in 153.99 seconds with thirteen expected fixture warnings. Both use
Python 3.14, pytest-receptor, twelve workers and fatal SQLite/unraisable guards.
A genuinely saved prechange public `@1` original/later bundle also passes the
new independent reader with acquisition, derivation, catalogue/backend access and
new credit forbidden; every original file, producer and export hash is unchanged.
The public 64/128-statement corrected payloads measure 917,786/1,822,170 bytes
(ratio about 1.99), while retaining all input assertions and use roles. These
measurements retain their own recorded development metadata.

MOLI owns its application-side receiving example and Recorda integration. A
closed store may retain only the full native snapshots needed by its declared
result, through Sabueso's existing owner-issued load/save API with exact pin/state
checks; its new container is a separate artifact. A store projection never changes
the original scientific reports, asserts replayability or reconstructs missing
historical credit. Native source-response archival, general self-contained export,
ProjectRecord routing, Nextia interpretation and installed/human acceptance remain
separate owner work. Private trials and details remain private.

The correction is published with explicit maintainer authorization at
`792bd0da45245ad0fca08e4b431e5e49e4d76ae8`, without `[skip ci]`.
The [publication snapshot](comparative_credit_compaction_publication.json) retains
that original publication state and the owning issue summaries.
Its automatic [governance](https://github.com/uibcdf/sabueso/actions/runs/38456975421)
passes 1/1; [CI](https://github.com/uibcdf/sabueso/actions/runs/38456975623) is pending.
The earlier block is independently source-qualified at `25f6163`; those results
do not qualify this correction. Complete full receptor captures and every
applicable job summary must pass on `792bd0d` before claiming source qualification.

The separate [MOLI receiving PR #67](https://github.com/uibcdf/moli/pull/67) has
[18 passing public receiving cases](https://github.com/uibcdf/moli/actions/runs/38454271829)
and [passing applicable governance](https://github.com/uibcdf/moli/actions/runs/38454272358)
on `fc110e882f3b5887d64fedcc60fca46250c062eb`. Its default-branch coverage job is
inapplicable to that PR. The CI source pin stays at qualified Sabueso `25f6163`,
so it does not qualify the later correction. Local receiving checks additionally
exercise the new operation `@2`. The PR remains draft for owner review; this is
an application example, not acceptance of a shared recording format or release.
