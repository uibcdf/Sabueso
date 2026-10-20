# Conda publication routes

Sabueso builds one `noarch: python` artifact for Python 3.11–3.14.
The recipe freezes the exact Conda version into the ephemeral build source;
the repository's dynamic `versioningit` configuration remains unchanged.
The build workflow accepts either a reviewed direct release or an immutable
staging candidate, as selected in `release_plan.toml`.

Before creating or editing a public GitHub Release, check that its visible
title (`name`) is exactly the canonical `X.Y.Z` version and equals its tag
and package version. Use `gh release create X.Y.Z --title X.Y.Z` or set the API
`name` and `tag_name` identically; put descriptive text in the notes. Verify
the resulting metadata. Historical release titles are reviewed separately.

Before a release, update the plan to the proposed three-part version and
record the route, reason, reviewer, and required exact-commit workflows.
Sabueso's full matrix (`ci.yml`: Ruff and the offline suite on Python 3.11–3.14)
and the MOLI governance check (`moli-governance.yml`) are required. CI's offline
scope uses reviewed repository inputs; protected local-only originals are not
release inputs. Retain applicable opted-in native qualification separately, and
pass `python tools/fixture_delivery.py --check` before publishing the candidate
source. See [test scopes](../../devguide/TESTS.md).
Run them at the final candidate SHA. A direct route is appropriate
only when no pre-public installed-artifact or coupled-consumer gate is needed;
the registry must confirm that the version is unoccupied. A staged route is
required for a new interpreter, dependency, packaging contract, or other
change that needs clean installed-package evidence before public visibility.

Before any candidate build, `python devtools/dependency_preflight.py --release` must pass. It is a
read-only check that the recipe, every environment installing the runtime, and the
exact public builds pinned by the staged-package test agree with `pyproject.toml`
(`devtools/dependency_routes.toml`, #76). CI's quality job runs the development check
without `--release`, allowing only explicitly inventoried required source candidates
while reporting their release blockers.

**Immutable coordinates (#78).**
- A Conda file coordinate (`uibcdf/sabueso/<version>/noarch/<filename>`) is never
  overwritten, under any label, even with the same bytes.
- Before a staged upload, `release_route.py coordinate` refuses a coordinate the
  registry already holds. A corrected build needs a new build number or version. The
  direct route refuses any existing file of the version.
- After promotion, `release_route.py poststate` queries the registry read-only, with
  bounded retries. The exact coordinate must carry the `main` label and the tested
  SHA-256. The result is kept as a receipt (`sabueso-conda-poststate-*`).
- A red poststate is diagnosed with read-only queries, never with another upload or
  promotion.

For the staged route, dispatch
`.github/workflows/build_and_upload_conda_packages.yaml` with the exact
`candidate_sha`, `version`, and `build_number` (normally zero). It uploads
only to `uibcdf/label/staging` and retains the route and producer receipts.
Then dispatch `.github/workflows/test_staged_conda_package.yaml` with the
same coordinates and successful staging run ID. Before any installation, it downloads
the exact staged file and inspects it (`verify_staged_install.py archive`, #77): its
digest against the producer receipts, the version it embeds (`info/index.json`,
`_version.py` and the `dist-info` metadata), and the package-critical resources
(`REQUIRED_RESOURCES`: the packaged selection rules, enrichment profiles, source
terms and development metadata catalog). The catalog is an unreleased resource;
older release receipts remain scoped to the resources present in those artifacts. This is
the only claimed public route (the `noarch` conda package); Sabueso publishes no wheel. The gate checks artifact
digest, source channel, public dependency provenance, package version, and
an API smoke test (a card whose quantities are sealed by `to_dict()` and verified by
`from_dict()`) in clean Linux, macOS Apple Silicon (arm64) and Windows
environments for Python 3.11–3.14, with the
public SMonitor, PyUnitWizard and DepDigest builds.
The installed check also rejects an Ackredit import from a source checkout,
inconsistent provider metadata or missing portable capture/reader APIs. Each
installed lane then runs the unchanged acquisition/packet-attribution regressions
and public offline workflow outside both checkouts, using only copied public
fixtures and the installed provider/consumer. Pytest and published Pytest Receptor
are gate tooling; no runtime source overlay or pip replacement is installed.
Do not publish a stable GitHub Release until every cell passes.

For a staged release, the release event verifies the plan and does not
rebuild. Dispatch `.github/workflows/promote_conda_package.yaml` only after
the stable GitHub Release exists, using the independently verified digest.
It promotes the exact staged file to the public channel and checks the public
record. For a direct route, the release event builds and uploads once to
`main`, then independently checks the public file's digest.

This mechanism mirrors PyUnitWizard's (uibcdf/pyunitwizard), as MOLI's distribution
policy expects of every component (uibcdf/sabueso#34). The local verification build
described in `meta.yaml` (`SABUESO_CONDA_VERSION=X.Y.Z conda build ...`) is never
uploaded.

Before documenting any installation route, verify a clean installation from the public
channel; staging and source tests alone are not publication.

## Card schema at release

The release notes state the card schema the release writes. If the release publishes a
card schema no earlier release published, add its frozen card before tagging:
`temp_data/frozen_cards/schema_<version>__<public accession>.json`. Build it with
the candidate's package: `SABUESO_CONDA_VERSION=X.Y.Z conda build devtools/conda-build
--no-anaconda-upload --output-folder <tmp>`, install it in a clean environment, and
write the card from the fixtures there
(see `devguide/SCHEMA.md`, "Versioning policy", and uibcdf/sabueso#42). From then on,
that schema's recorded shape is fixed.

## Delivered required provider

Ackredit 0.9.0/py_0 is public, carrying the first published portable attribution
contract (#108; ackredit#22/#75/#80). Metadata, recipe and environments require
`ackredit>=0.9.0`; CI uses public Conda without a source overlay. The installed-file
matrix pins the public build and rejects any other archive digest:
`37661090f6ad19a74b8155d8a4d4b4a068c9099f4ceba0743b3abfe887e97fe1`.
The public bytes match the previously independently verified staging file.

Provider installed run 37152044426 covers Linux/macOS arm64 × Python 3.11–3.14;
promotion 37152421084 preserves the archive. Independent receiving compatibility
on all four Linux minors passes the 36 tests, public workflow and pip check with
Sabueso's planned exact public core pins. Staging/public receiving receipts remain
separate from Sabueso's actual Conda candidate qualification. `dependency_preflight.py
--release` passes the adopted closure; it retains generic future-provider guards.
The primary workspace keeps all 14 installed workspace packages editable. Its
current 0.9.0-based Ackredit editable satisfies the public minimum, with runtime/
distribution agreement and a passing pip check (2026-10-04). Provider #81 records
the earlier Git-version mismatch and receiving confirmation.

## Published 0.14.0 (#134)

The current `release_plan.toml` selects 0.14.0 and the staged route;
`release_notes_0.14.0.md` states the consolidation scope and known limits. The
installed matrix now includes taxonomy observation and unchanged residue,
isoform/sequence, supplied-file, notebook and public HK2 regressions, alongside
clinical attribution and independent public journeys. Nbformat is gate tooling
for notebook validation; it does not become a runtime dependency.

Preliminary local source `5fbd3ed` builds one unuploaded Conda file, SHA-256
`1e2f5e2bc1ec145428477e5838111f9e24f4fc606c465712eec028a809e1a8e7`.
All 517 implementation/resource files equal source and the clean installation.
The public-minimum Python 3.14.8 installed writer freezes
`schema_0.3.13__P60174.json` from the existing public UniProt/RCSB inputs. Original
retrieval dates remain separate from generation. The local qualification receipt
is `receipts/sabueso_0.14.0_local_schema_freeze_2026-10-09.json`.
The local installed gate passes 1,277 cases with one explicitly excluded native
DisProt original, the public workflow and pip check. This is preliminary local
evidence, not the final staging file or publication.
Final source/tag `78623d0` passes CI 37925885113 (15/15) and governance
37925885489. Producer 37929742651 builds `sabueso-0.14.0-py_0.tar.bz2`, SHA-256
`ceb940bc37c85934ca0fadfdeb315cc69095aea46ed255d73b7c5f3e33376daa`;
all 517 implementation/resource files equal source. Installed matrix 37930116530
passes producer verification and all twelve OS/minor lanes, each with 1,277 cases,
one deliberate local-only DisProt exclusion and the public workflow. Release event
37931493554 verifies without rebuilding; promotion 37931518272 preserves the file
and verifies its public labels/digest. Anonymous public bytes equal staging.
A fresh public-only Linux/Python 3.14.8 installation with a new cache passes
bytes/origins/API, frozen-card reading, the same 1,277 cases/one exclusion,
workflow and pip check. Zenodo DOI `10.5281/zenodo.23263488` archives all 1,318
source files identical to the tag; both DOI destinations are verified. Complete
receipt: `receipts/sabueso_0.14.0_public_2026-10-09.json`.
Full private consumer acceptance (#132), SQLite connection lifetime (#133) and
broader source observation/bibliography (#108) remain explicit limits.

## Published 0.13.0 (#121)

The 0.13.0 release selected the staged route; scope and compatibility
limits are in `release_notes_0.13.0.md`. The preparation uses the qualified public
minimum dependency closure listed above and all 19 installed receiving test files
already wired in the matrix (613 cases at the preceding code checkpoint).

The unpublished local Conda candidate `c236e4f` passes archive/source/installed-byte
qualification, all 613 unchanged receiving cases, public workflow, API and pip check
on Python 3.14.7 with the exact public minimum closure. Its clean installed writer
freezes `schema_0.3.12__P60174.json`, including original literal extraction and public
article metadata. The source/input/archive/writer receipt is
`receipts/sabueso_0.13.0_local_schema_freeze_2026-10-05.json`; this is local evidence,
not the final staged archive. Commit that fixture before selecting the final candidate
SHA.

Final source/tag `7e78d07` passes CI 37308420258 (15/15) and governance 37308420271.
Staging producer 37309502566 builds `sabueso-0.13.0-py_0.tar.bz2`, SHA-256
`1e8f80375cbc08c04df452dbbb55084dc4ff41c6242fbb07e3479f0cd4c7361c`;
all 382 non-version Python/JSON files equal source. Installed matrix 37310099058
passes producer evidence and all 12 OS/minor lanes, each with 613 cases and the
public workflow. Release event 37311427178 verifies without rebuilding; promotion
37311466982 preserves the archive and verifies its public poststate. Anonymous
public bytes equal staging; a fresh public-only Linux/Python 3.14.7 install passes
bytes/origins/API, frozen-card read, all 613 cases, workflow and pip check.
Zenodo DOI `10.5281/zenodo.23162373` holds all 960 source files identical to the tag.
Complete receipt: `receipts/sabueso_0.13.0_public_2026-10-05.json`.
Historical tags, artifacts and receipts stay immutable.

## Prepared 0.12.0 scope (#110, historical)


`release_plan.toml` selects 0.12.0 and the staged route;
`release_notes_0.12.0.md` contains the reusable draft. The preliminary local
Conda candidate at `01d5bf2` passes installed checks on all four Linux minors
and supplies `schema_0.3.11__P60174.json` from its clean Python 3.14.7 install.
The local artifact/hash, source, public pins, regressions and schema-freeze receipt
are in `receipts/sabueso_0.12.0_local_schema_freeze_2026-10-03.json`.
Local qualification is separate from the actual staging receipt below.

The preparation includes the exact qualified builder
`8da628d9b393e184c3bf3722708b19dcfbf7ef0a`, retaining upload, immutable coordinate,
producer-receipt and promotion contracts. Provider #46/#47 and the MolSysSuite #78
handoff supply environment-aware compilation qualification; this pin adoption is
not an actual Sabueso staged-build receipt.

Before selecting the final candidate:

1. Provider delivery is verified and adopted: minimum 0.9.0, public build/hash,
   compatible public core pins and no source overlay. Re-run
   `dependency_preflight.py --release` before every build/installed/promotion route.
2. Build a local, unpublished candidate Conda file and install it in a separate
   clean environment. Generate the 0.3.11 frozen public card from that installed
   code, record its candidate/fixture/version/licence receipt in `temp_data/NOTICE.md`,
   and commit it. Do not freeze a card from the editable workspace.
3. Review the final notes and `CITATION.cff`, which follows the planned version
   and retains the concept/historical DOIs. Its optional publication date stays
   unset while qualifying the candidate; the release and archive record the actual
   publication date.
   Run local gates, inspect exact final-SHA CI/governance and confirm the registry
   coordinate before dispatching the staged build.
4. Inspect the staged archive and complete Linux/macOS/Windows × Python 3.11–3.14
   installed gates, including required-provider regressions.
5. Then publish the stable GitHub release, promote the tested file, verify a clean
   public install and archive the identical tag on Zenodo.

Broader source/result coverage, undeclared bibliography and Recorda integration
remain issue-backed work with explicit release limits. This bounded scope retains
the required traceability target without asserting full pipeline provenance.

## Preliminary 0.12.0 candidate (historical qualification)

Preliminary candidate `4ef9ddc7dc8a9e01ce430ef3d30f5d9cb94006a6` passed exact-SHA
CI 37159503827 (15/15) and governance 37159503801. Staging producer 37159798707
builds `sabueso-0.12.0-py_0.tar.bz2`, SHA-256
`8a3910eacd4f63945708d9fe6339cf578ae2a9d1958a02a391db2dbc23c6b347`.
Independent download verifies the receipts, embedded versions, resources and all
351 non-version Python/JSON files against that source. Installed workflow
37160115178 passes its producer check and every Linux/macOS-arm64/Windows ×
Python 3.11–3.14 lane, including 36 integration regressions and the public workflow
per lane. Independent clean Linux 3.14 also checks installed bytes, the frozen card
and pip metadata. The durable receipt is
`receipts/sabueso_0.12.0_staged_2026-10-03.json`.

On 2026-10-04 the maintainer requested RCSB traceability before stable publication.
This implementation change supersedes the preliminary source scope. Preserve `py_0`
and its historical receipts; select a new full SHA, build `py_1`, and repeat exact-SHA
CI, archive inspection and the full installed matrix with the RCSB tests and extended
public workflow. The stable tag must select the newly qualified SHA, and promotion
must preserve that new archive digest. Evidence-only follow-ups do not change it.
The subsequent RCSB candidate is published as 0.12.0/py_1; its completed receipt
is below. The old py_0 archive is historical and was never promoted.

## Published 0.12.0 with RCSB traceability

Qualified source/tag `7739317e40623d70513d4c2bb483f015b3f3247c` passes CI
37189004296 (15/15) and governance 37189004230. Producer 37190652548 builds
`sabueso-0.12.0-py_1.tar.bz2`, SHA-256
`8f18330174de99cd8a9c8ff3e281ad27f4e894b9ac9f692b6643253b64d65382`.
All 352 non-version Python/JSON files equal the source. Installed matrix
37190968604 passes producer evidence and all 12 OS/minor lanes, each with 56
integration cases and the public identity/literature/structures workflow.

The stable GitHub release selects that tag. Promotion 37191632488 preserves the
same archive and verifies its public labels/digest. An anonymous public download
matches the staging bytes. A fresh public-only Linux/Python 3.14.7 environment,
with a new package cache, passes installed bytes/origins/API, the frozen card,
56 cases, the workflow and pip check. Zenodo DOI `10.5281/zenodo.23134375` holds
1160 source files identical to the qualified tag; the Conda artifact is separate.
The complete receipt is `receipts/sabueso_0.12.0_public_2026-10-04.json`.

Post-publication metadata and receipt commits do not change the release tag or
archive. The preliminary `py_0` receipt remains historical; never overwrite it.

## Local diagnostic wheels

A local wheel is an installed-consumer diagnostic, not a published installation
route. Incremental setuptools builds can reuse stale `build/lib` modules when
cached timestamps are newer than the source (#113). Preserve/remove generated
build output before a clean build, then verify every packaged source module and
resource before installing it:
Generated root `sabueso.egg-info` can also shadow installed editable version metadata
inside the checkout. Preserve it outside the checkout after diagnostic builds and
verify editable runtime/distribution versions both inside and outside the checkout.

```bash
python -m pip wheel --no-deps --no-build-isolation --no-cache-dir . --wheel-dir /tmp/sabueso-wheels
python devtools/conda-build/check_local_wheel.py /tmp/sabueso-wheels/<exact-wheel-file>.whl
```

The guard rejects changed bytes, missing files and unexpected retired modules,
excluding only generated `_version.py`. Install the verified wheel in a separate
environment and run unchanged tests outside the checkout with the published
provider floor. A passing source suite cannot substitute for this artifact check.
The public Conda route continues using its independent clean-source, exact-archive,
installed-package and promotion gates above. Development remains editable.
