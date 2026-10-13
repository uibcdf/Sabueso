# Public scientific dossier (#112, #132)

The bounded question is which stored TcTIM/HsTIM structures and assay records
meet declared illustrative criteria, and which located literature support is
available. The executable [example](../../examples/user_journeys/scientific_dossier.py)
uses existing public inspection, fixture, acquisition, attribution and persistence
APIs. Its [user instructions](../../examples/user_journeys/README.md)
describe production, independent reading and reacquisition. No source adapter,
SDK API, card schema, frozen fixture or shared MOLI contract changes.

Named example rules `public_structure_review_criteria@1` and
`public_assay_record_review_criteria@1` retain inputs, outcomes and exact
relationship/SourceAssertion pins. Relationship support is not represented as
individual qualifier lineage. Criteria are illustrative, not a pilot question
or selection strategy. Derived rule outputs are not SourceAssertions.

## Retained scientific scope

- Structure review retains resolution quantities, sequence differences, coverage,
  source assemblies and disagreements, canonical/author numbering and supported
  active-site positions. Met, not met and unknown are distinct. The fixture
  examples include eligible reference structures, a mutant, a fragment and an
  author/software assembly disagreement. The explicit requested PDB list and
  original outcomes retain missing responses; absence from a row is not external
  absence. Modeling, alignment and project model selection are not performed.
- Assay review retains every admitted relationship, original measurement/type/unit,
  normalized quantity, censored/ranged values, target assignment and conditions.
  Direct-target IC50 equality/concentration eligibility does not establish a
  common assay or selectivity. Both providers are explicitly capped at 25; original
  partial knowledge states and query reports remain inspectable.
- Located literature retains an actual P60174 figure occurrence from the declared
  Europe PMC public annotation fixture, including returned text fragment, location,
  publication and assertion support. Native bibliography is retained separately.
  The requested subject annotations return no located match; this is not a claim
  about the article's full contents. No curated mechanistic claim or project
  Evidence is created. Fragment source/date/rights remain in `temp_data/NOTICE.md`.

## Persistence and receiving boundary

`sabueso.scientific_dossier_example@1` is example-local. Markdown is generated from
saved JSON, with quantities serialized as `{value, unit}`. Original producer SDK/
Ackredit versions and the executable example hash accompany the results. The
scientific store retains original and later pins. Runtime sidecars preserve
source acquisitions and original workflow credit; dossier derivation observation
is explicitly absent. Original CSL/BibTeX exports remain producer-owned.

The independent reader performs no source acquisition, SDK scientific view,
reclassification or new credit. It verifies closed membership, exact input pins,
source support, native values/context, declared scopes, recorded decision
consistency, original workflow union and byte-consistent human output. Rehashed
manifests do not make altered measurements, units, support or interpretation
valid. Hashes detect inconsistent artifacts and do not authenticate a source.

Sixteen new cases exercise separate producer/read/reacquire processes outside
the checkout, original producer versions under a different reader label, exact
retained pins and bibliography, explicit partial/unknown scope and deliberately
modified artifacts. They also run in public-source CI and installed public-
Ackredit receiving. Their execution is technical qualification; a scientist's
acceptance remains separate.

MOLI PR #67 receives the existing comparative example only. This new dossier is
not automatically accepted by Recorda, ProjectRecord or Nextia. Broader located
statement curation remains #92, execution/bibliography #108, consumer usefulness
#132 and coordinated delivery #112. The proposed 0.15.0 release retains its own
staged build and installed-artifact route.

## Local checkpoint

Python 3.14.7 in the existing editable workspace passes the 16 new cases and
all 6,282 local-original offline cases with twelve pytest-receptor workers
(153.75 seconds, nine expected fixture warnings; fatal unclosed-SQLite and
unraisable guards). Ruff format/check, fixture delivery, dependency preflight,
canonical MOLI guide equality, local governance and warning-fatal Sphinx pass.
All seven participating editable imports and distribution/module versions agree
outside the checkout, including DepDigest 0.15.1 and SMonitor 0.20.0.

## Hosted source checkpoint

The [receipt](scientific_dossier_checkpoint.json) qualifies exact source
`6e35c1d584bd6f946cb044c470001590c0b8447e`, published without `[skip ci]`.
[CI](https://github.com/uibcdf/sabueso/actions/runs/38478553072) passes 15/15 and
[governance](https://github.com/uibcdf/sabueso/actions/runs/38478553014) passes 1/1.
Complete gh-run-receptor captures have every member hash independently checked;
all thirteen test summaries are inspected. Nine public OS/minor lanes pass
4,729 cases each, with ten native skips and 26 online deselections. Four installed
public-Ackredit 0.9.0 lanes pass 1,387 cases each. Ruff and coverage publication
pass; external coverage-service visibility is not independently qualified.
Earlier source and release receipts retain their original SHA and scope. This is
development-source/receiving qualification, separate from a staged release artifact.
