# MOLI component coordination

This repository is directly governed by the MOLI platform for shared cross-component contracts.

Before cross-component or architectural work, read `MOLI_GUIDE.md`. Its canonical source is `uibcdf/moli/MOLI_GUIDE.md`; do not intentionally diverge the local copy.

This repository remains authoritative for its own implementation, tests, local API, scientific behavior, releases, and component-specific development decisions.

Use `uibcdf/moli` when a change affects a shared MOLI contract, terminology, architecture boundary, or coordination policy. Report provider-specific limitations to the provider repository and cross-link consumer work.

For a needed fix in another repository, use its issue when no fix is ready or
submit a ready fix as a pull request for owner review. If urgent work is done
by or directly with Diego or Liliana, ask them whether to use a direct push,
pull request or issue; direct push needs explicit permission. Follow
`MOLI_GUIDE.md#cross-component-feedback`.

For authorized direct pushes, batch short local commits when practical and
choose local checks and CI according to the changed behavior. Consider
`[skip ci]` only where this repository permits it and deferred tests have a
recovery route; verify a final code checkpoint before claiming completion.
Follow `MOLI_GUIDE.md#moli-engineering-baseline` and the local CI policy.

Do not expose confidential vertical-pilot content in public issues or documentation.

# Working in Sabueso

Sabueso is the Knowledge component of MOLI's Scientific Context. **Sabueso knows; it does
not discover.** Start with `devguide/README.md`, then `devguide/CHECKPOINT.md` and
`devguide/ROADMAP.md`.

## Language

Everything written into the repository is in English: code, comments, docstrings,
commit messages, issues, pull requests, release notes and documentation.

## Knowledge principles (see `devguide/ARCHITECTURE.md`)

- `SourceAssertion ≠ Evidence ≠ Provenance`. Sabueso records what sources assert; it
  never creates Evidence (Nextia's) and never imports project conclusions as knowledge.
- Every value is linked to the SourceAssertions that support it. Selection never
  discards them. Conflicts and ambiguity are reported, never resolved silently.
- Derived knowledge (a class, group, state or finding) carries a named, versioned rule
  (`name@N`) and is never stored as a SourceAssertion.
- Identity is never merged by similarity: not by sequence, not by a shared name, not by
  an equal residue number. Two entries are one entity only when a source states it.
  Every identity finding states its basis.
- Absence is not evidence. Tell apart what a source does not state, what was not asked,
  and what failed.
- Physical quantities are PyUnitWizard quantities, stored as `{value, unit}`. A unit
  never lives in a field name, and units are never lost across MOLI boundaries.

## Code conventions

- The UIBCDF tools:
  - public arguments are checked through ArgDigest, one digester per argument name, in
    `sabueso/_private/argdigest/argument/` (`devguide/ARGUMENT_CONTRACTS.md`);
  - diagnostics go through SMonitor (`devguide/DIAGNOSTICS.md`);
  - optional dependencies go through DepDigest.
- A new source follows `devguide/SOURCE_ACCESS.md`:
  - a client with online and fixture implementations;
  - public `get_*` functions;
  - a mapping in `sabueso/mappings/`;
  - to enrich cards, a declared enricher in `sabueso/enrichers/` (#86). The knowledge
    state and migration read it; a test checks its wiring;
  - an `in_use` entry in `devguide/sources/registry.yaml` (then
    `python tools/source_registry.py --write`).
- Python 3.11–3.14 are supported. Use Python 3.14 for routine local development
  and pytest; provision the Conda environment and install this checkout with
  `python -m pip install --no-deps --editable .`. Install other participating
  Python components editable in a compatible shared environment when testing
  their integration, and verify import paths.
- Report bugs of UIBCDF tools, such as ArgDigest, PyUnitWizard, SMonitor, DepDigest or
  the receptors, upstream in their repositories, and cross-link them.

## Card schema

- Card schema changes follow the versioning policy in `devguide/SCHEMA.md`:
  - an additive change goes to the unpublished version;
  - a published version (it has a frozen card in `temp_data/frozen_cards/`) is never
    changed;
  - every change is described in the schema file, and listed in
    `sabueso/core/migration.py` (`SCHEMA_CHANGES`).
- After an intended change, record the shape (`python tools/card_shape.py --write`), and
  update `devguide/FIELD_PATHS.md` and `devguide/SCHEMA.md`.

## Tests and fixtures

- Local workspace development uses `molsyssuite@uibcdf_3.14`. Sabueso and every
  MolSysSuite package installed in that environment must use its local checkout
  through `pip install --no-deps --editable .`. Verify editable metadata outside
  the checkout. Use separate environments for installed-artifact qualification.
- Run pytest through the receptor, as `MOLI_GUIDE.md` asks:
  `python -m pytest -m "not online" --receptor=llm`.
- Fixtures in `temp_data/` are frozen **public** responses, each declared in
  `temp_data/NOTICE.md` with its source, date and licence. No private or pilot data, ever.
  TcTIM and HsTIM may be used as public test systems.
- Select applicable local gates for the changed files and behavior from
  `devguide/TESTS.md`. The full offline pytest suite is a code-validation
  checkpoint, not a requirement for every documentation or exploratory commit.
  - Run each selected gate on its own and read its result.
  - Never pipe a gate through `tail` or `grep`, and never chain a commit after a command
    whose exit code does not reflect the gate.

## Commits, CI and releases

- Maintainers may commit directly to `main` once the applicable local gates pass.
  Batch short commits locally when a remote checkpoint is unnecessary. Authorized
  intermediate direct pushes may use `[skip ci]` after applicable local checks,
  including tested code, when no immediate remote gate is needed. Record the
  deferred head, scope, owning issue and recovery route. Finish the block with
  an unskipped push or explicitly authorized manual CI and governance runs,
  verifying every applicable gate on the exact final SHA through gh-run-receptor.
  Never use the marker to evade required PR checks or immediate security,
  dependency, packaging, migration or integration gates. See `devguide/TESTS.md`
  and `MOLI_GUIDE.md#moli-engineering-baseline`.
- Releases follow the staged route in `devtools/conda-build/README.md`:
  - the candidate's CI, a staging build, and the installed-package gates on Linux,
    macOS and Windows;
  - then the GitHub release, promotion to the public channel, a clean public install,
    and the Zenodo archive.
- Before creating or editing a public GitHub Release, check that its visible title
  is exactly the canonical `X.Y.Z` version and matches the tag and package version.
  Put descriptions in the release notes. Follow
  `MOLI_GUIDE.md#moli-engineering-baseline`.
- Never document an installation route before a clean install from the public channel
  has been verified.
- Releases are few and substantial. Propose one for a substantial set of changes, for an
  integrity fix that affects users of a published version, or when the maintainers ask.

## Recording work

Report defects and needs in their owning issues; put source behavior, edge
cases and workarounds in code, regression tests and technical documentation,
not in `AGENTS.md`. Add an instruction here or in a nested `AGENTS.md` only
when normal repository review accepts a lasting rule about how contributors
or agents should work across future tasks and existing guidance is insufficient.
Use an adoption issue only if that accepted working instruction cannot be
placed with the fix or decision. Do not ask for a separate `AGENTS.md` decision
for every defect. Propose cross-component adoption only for an accepted
working instruction with shared evidence. Follow
`MOLI_GUIDE.md#durable-instructions-for-development-agents`. For work in the
developer guide, also read `devguide/AGENTS.md`.

- A decision goes to `devguide/DECISIONS.md`, and a possible future problem to
  `devguide/RISKS_AND_OPEN_QUESTIONS.md`.
- A decision to re-evaluate later gets a GitHub issue.
- A change that makes a devguide line false updates it in the same commit
  (`devguide/README.md`, "Keeping the guide true").
- Work is planned along two integrated routes, the foundational plan and the
  pilot-driven route (`devguide/ROADMAP.md`). Neither replaces the other.
- Vertical pilots are private:
  - read them only;
  - phrase their needs generically in public issues, commits and docs;
  - never copy their hypotheses, strategies, campaigns or candidate regions.
