# Deferred development CI (#112, #108)

The maintainer approved batching locally checked development commits on
2026-10-13, allowing `[skip ci]` on intermediate authorized direct pushes and
recovering remote gates once per completed block. The rule and exact-head recovery
commands live in [TESTS.md](../TESTS.md#recovering-deferred-ci). This changes
Sabueso's local practice within the existing MOLI policy; it changes no shared
contract or release gate.

## Current block: comparative execution observation

Owner: [#108](https://github.com/uibcdf/sabueso/issues/108), with engineering
consolidation under [#112](https://github.com/uibcdf/sabueso/issues/112).
The scientific implementation is published at
`31b6255ceb2fa7c6ab23153c6e78307a41fa3465`, based on published development head
`576b7e95c78099360b97b9522f86f381b925ce1f`.
Its [scope report](comparative_operations.md) records 26 new regressions,
190 selected cases and 6,208 full local-original offline cases through
pytest-receptor with twelve workers, plus 26 post-editable cases and an
independent inert saved reader. Python 3.14.7 uses the shared editable environment;
public fixtures, schemas, historical receipts and scientific engines remain exact.
No scientific provider queries were added.

Policy commit `c7916cfb17e47ab7513f702170993931b9636fc0` also enables manual
governance and manual-main coverage publication.
Its validation covers workflow structure, dispatch/main coverage conditions,
dependency preflight, local governance, canonical-guide equality and relative links.
These checks do not prove GitHub execution, Codecov delivery or cross-platform
installed behavior. The existing source pytest result remains applicable because
this policy commit changes no Python source, fixture or scientific test input.
After installing its editable metadata (`0.14.0+35.gc7916cf`), the 26 comparative
operation cases pass in 8.41 seconds with twelve receptor workers; six participating
imports and all fourteen installed suite distributions use local editable checkouts.
The original implementation's producer receipts remain unchanged.

The maintainer explicitly authorized publication to `main` and a public #112
summary on 2026-10-13. Both commits are published through `c7916cf` with `[skip ci]`;
the [owning issue update](https://github.com/uibcdf/sabueso/issues/112#issuecomment-6149457079)
records local results and deferred scope. Remote qualification remains pending.
This publication status update changes documentation only. Before each further authorized push,
record its actual `git rev-parse HEAD`, included commits and applicable local
checks in the owning issue and local checkpoint record. Extend this entry if
more implementation enters the block. Qualification is missing all thirteen
remote test lanes, Ruff, coverage publication and governance for the resulting
head. Earlier green CI on `cf5900d` does not validate this block.

The next local [persisted comparative journey](comparative_journey_attribution.md)
enters this block: example `@3`, original source/comparative/workflow records,
historical `@1`/`@2` reading and independent reference export after reacquisition.
229 selected and all 6,247 local-original offline cases pass with twelve receptor
workers and applicable documentation/style/dependency/governance gates.
This addition is unpublished and unqualified
remotely; the installed public-Ackredit lanes now include its example/tests.
Record its committed head before further authorized publication. Final remote
recovery must cover this scope too.

The subsequent [verified bibliography slice](comparative_bibliography.md) adds
offline resource descriptions and pext-only method credit, original-reader
compatibility and installed-lane selectors. 278 selected and all 6,262
local-original offline cases pass with twelve receptor workers; the full run takes
155.58 seconds with thirteen expected fixture warnings. Publication and remote
qualification are pending.
Qualify the final resulting head with all applicable CI and governance jobs before
claiming this block remotely qualified or returning qualified source to #132.

Recovery: publish an authorized unskipped final checkpoint, or explicitly dispatch
both `ci.yml` and `moli-governance.yml` on the published final `main` head as
described in [TESTS.md](../TESTS.md#recovering-deferred-ci). Retain full
gh-run-receptor captures and verify every applicable job against that exact SHA.
Only then record remote source qualification. Keep #108, #112 and consumer
acceptance open for their remaining scope; release and installed-artifact
qualification remain separate. No remote run has been started for this block.
