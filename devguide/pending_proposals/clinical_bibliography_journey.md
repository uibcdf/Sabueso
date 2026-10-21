---
summary: Explicit saved indication, trial-reference and publication-metadata journey.
issue: uibcdf/sabueso#108
status: open
opened: 2026-10-21
closed:
verification: measured
area: [source_access, attribution, bibliography, user_journeys]
blocked_by: []
supersedes: []
related: [uibcdf/sabueso#112, uibcdf/sabueso#132]
---

# Bounded clinical bibliography journey

The separate `examples/user_journeys/clinical_bibliography.py` implements the
approved next clinical slice. The new example-local
`sabueso.clinical_bibliography_example@1` uses existing public SDK APIs and
unchanged, declared public fixtures. It changes no card/source/schema contract
and does not qualify a new published artifact.

## Scientific and execution scope

The original `molecule_target_example@1` producer creates its own historical
cards, relationships, SourceAssertions and workflow in `molecules/`. The clinical
augmentation pins that manifest and keeps every indication that explicitly cites
NCT00123916. Distinct disease identities remain distinct even with a shared MeSH
heading. Fifteen other cited trials remain unqueried.

One explicit registry-reference operation preserves identification/update metadata
and all native reference forms. Three explicit Europe PMC metadata selections
(PMID 18585495, 26323937 and 19753491) require the corresponding returned registry
PMID statement. Free citations never supply inferred identifiers or authors.
Websites, retractions, participant-data links and any unselected references remain
unfollowed. Trial status, design/results, full text, efficacy, protocol curation
and project Evidence are outside scope.

Original source envelopes retain their acquisition traces; a separate observation
list binds them to the clinical workflow and CSL/BibTeX exports. The molecular
workflow stays beside its original input: it is not replayed or credited as part
of the new clinical operations. The local linkage is named
`explicit_clinical_bibliography_links@1`, not stored as a SourceAssertion or claimed
as runtime-observed scientific derivation.

## Saved reading and refresh

Separate reader processes use no fixtures or source clients, SDK scientific views
or new credits. They validate exact pinned indication support, requested scopes,
returned/native metadata, observed operations, original bibliography and complete
report/rendering consistency. This checks internal consistency, not authenticity
of arbitrarily rewritten source records or live source availability.

Clinical-only reacquisition records a distinct execution and retrieval label;
the original molecule/card/selection remains fixed. Original reports, sidecars
and exports remain byte-identical. Existing molecular `@1` and disease `@1`–`@5`
formats and their unqueried clinical scope remain unchanged.

## Acceptance and remaining work

Twenty-one new cases and 182 selected clinical/article/molecular/disease cases
pass in 161.14 seconds with Python 3.14, twelve workers and pytest-receptor.
Ruff, fixture delivery (51 repository/37 protected), registry, dependency preflight,
local governance, canonical guide equality, local Markdown targets and warning-fatal
Sphinx pass. All **6,326 local-original cases pass in 559.65 seconds**, with thirteen
expected fixture warnings and fatal SQLite/unraisable guards.

The [exact-source receipt](clinical_bibliography_journey_checkpoint.json) qualifies
`2d294d8434c9cf74968b42ddd793c9709fee2305`: [CI 15/15](https://github.com/uibcdf/sabueso/actions/runs/39654562157)
and [governance 1/1](https://github.com/uibcdf/sabueso/actions/runs/39654562115).
All full-capture member hashes and thirteen test summaries are independently
verified: nine public lanes pass 4,773 cases each (ten native skips, 26 online
deselections), and four installed public-Ackredit lanes pass 1,431 each. Seven
participating imports and all fourteen installed registered suite members are
verified editable outside the checkout. Coverage publication passes; external
service visibility is not independently qualified.

Completed task-owned local test output is removed. One complete original/later
public fixture demonstration, receptor reports, source hashes and remote captures
remain useful evidence with an owner and a next-substantial-release review trigger.
Targeted tests include independent original/read/
reacquire/read, missing local registry/article files, failed registry access,
missing PMID/module versus returned empty references, preserved collective authors
and rehashed semantic alterations. Negative controls regenerate Markdown and
isolate the original stage so unrelated bindings cannot mask the intended guard.
CI public-Ackredit and staged installed selectors include the new module and its
standalone example dependencies.

Broader #108/#112 remain open: this bounded metadata journey neither establishes
clinical completeness nor replaces human scientific/consumer-owned acceptance.
The published 0.14.0 APIs remain available; this example's development-source
qualification is separate from future installed release delivery.
