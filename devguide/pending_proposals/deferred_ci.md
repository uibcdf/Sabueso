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
The scientific implementation is committed locally at
`31b6255ceb2fa7c6ab23153c6e78307a41fa3465`, based on published development head
`576b7e95c78099360b97b9522f86f381b925ce1f`.
Its [scope report](comparative_operations.md) records 26 new regressions,
190 selected cases and 6,208 full local-original offline cases through
pytest-receptor with twelve workers, plus 26 post-editable cases and an
independent inert saved reader. Python 3.14.7 uses the shared editable environment;
public fixtures, schemas, historical receipts and scientific engines remain exact.
No scientific provider queries were added.

The following policy commit also enables manual governance and manual-main
coverage publication. Identify that commit with
`git log -1 --format=%H -- .github/workflows/moli-governance.yml`.
Its validation covers workflow structure, dispatch/main coverage conditions,
dependency preflight, local governance, canonical-guide equality and relative links.
These checks do not prove GitHub execution, Codecov delivery or cross-platform
installed behavior. The existing source pytest result remains applicable because
this policy commit changes no Python source, fixture or scientific test input.

Publication and remote qualification are pending. Before any authorized push,
record its actual `git rev-parse HEAD`, included commits and applicable local
checks in the owning issue and local checkpoint record. Extend this entry if
more implementation enters the block. Qualification is missing all thirteen
remote test lanes, Ruff, coverage publication and governance for the resulting
head. Earlier green CI on `cf5900d` does not validate this block.

Recovery: publish an authorized unskipped final checkpoint, or explicitly dispatch
both `ci.yml` and `moli-governance.yml` on the published final `main` head as
described in [TESTS.md](../TESTS.md#recovering-deferred-ci). Retain full
gh-run-receptor captures and verify every applicable job against that exact SHA.
Only then record remote source qualification. Keep #108, #112 and consumer
acceptance open for their remaining scope; release and installed-artifact
qualification remain separate. No remote run has been started for this block.
