# Sabueso — Diagnostics (SMonitor)

Sabueso reports through SMonitor, the UIBCDF diagnostics layer, as required by MOLI's
support-library policy (uibcdf/sabueso#31).

[Application-owned receiving](DIAGNOSTIC_RECEIVING.md) records #150's import,
bootstrap and caller-selected scoped-capture decisions and qualification limits.

Structural machine selectors (#148) use `ArgumentError` for bad columns, typed
equalities, units, duplicate or foreign item references and unsupported order.
These are caller errors, never source absence. Legitimate display no-match keeps
the underlying scientific outcome and reports zero selected rows in the request.
Saved variants not retained are `not_saved`; unavailable policy versions or invalid
saved decision/support bindings are `StorageError`.

## Principle: outcomes are data first

Every source outcome is recorded on the result: `card.quality["enrichments"]`,
`deck.meta["sources"]` and `deck.meta["unanchored"]`. Diagnostics are **derived from
those same records** (`sabueso/_private/smonitor/outcomes.py`), so what a user is told
and what a card stores cannot diverge. SMonitor is the user-facing channel; it never
replaces the recorded outcome.

- **Reported:** a source that could not be consulted (`status: "error"`), a truncated
  result (`truncated: true`), and records left out of a deck because they have no
  standard InChIKey.
- **Not reported:** `not_found`. "The source holds no record" is an answer, not a
  failure, and it stays data only.

## Codes

| Code | Class | When |
|---|---|---|
| `SABUESO-W-ATTRIBUTION-001` | `AttributionTrackingWarning` | automatic tracking, stored-support attribution or acquisition recording failed; the scientific result/exception and host failure record remain available (#108) |
| `SABUESO-E-LIBRARY-001` | `LibraryNotFoundError` | an optional library a function needs is not installed (DepDigest; also an `ImportError`), with install hints |
| `SABUESO-W-ENRICH-001` | `EnrichmentFailedWarning` | a source failed; the result was built without it |
| `SABUESO-W-ENRICH-002` | `EnrichmentTruncatedWarning` | a source returned fewer records than it holds |
| `SABUESO-W-ENRICH-003` | `EnrichmentPartialWarning` | a source answered only part of a record, e.g. RCSB without instance-level fields (#74) |
| `SABUESO-W-IDENTITY-001` | `UnanchoredRecordsWarning` | records without a standard InChIKey were left out of a deck |
| `SABUESO-W-CURATION-001` | `CuratedDisagreementWarning` | a curated literature assertion differs from what other sources state about the same item (#41); both are kept |
| `SABUESO-E-GENERIC-001` | `SabuesoError` | base error |
| `SABUESO-E-RESOLVE-001` | `ResolverError` | |
| `SABUESO-E-SCHEMA-001` | `SchemaError` | |
| `SABUESO-E-STORAGE-001` | `StorageError` | |
| `SABUESO-E-SOURCE-001` | `ConnectorError` | a source could not answer |
| `SABUESO-E-SOURCE-002` | `RecordNotFoundError` | a source answered that it holds no such record |
| `SABUESO-E-SOURCE-003` | `MissingKeyError` | a source answers only with a personal key, and none was given (#86); an enrichment records it as `not_queried` |
| `SABUESO-E-ARG-001` | `ArgumentError` | an argument of a public function has a value it cannot accept (ArgDigest; also a `ValueError`) |

The warnings are catalog warnings: they emit a structured SMonitor event and raise an
ordinary Python warning, so `warnings.filterwarnings` and `pytest.warns` work as usual.
Tests that simulate a source failure assert the warning (`pytest.warns`).

Development literal Card access uses the existing argument/storage catalog codes.
An envelope too large for its requested bound raises `ArgumentError` with
`extra["argument"]="max_bytes"` and
`extra["reason"]="response_budget_too_small"`. An individual blocked item is
page data (`page.blocked`), not scientific absence. Clients inspect structured
state instead of parsing rendered exception messages.

In detailed mode, exceptions keep the message written where they are raised (template `{message}`)
and gain `exc.code` and `exc.extra`. Catching code should read `exc.code`, not parse the
message.

## Layout

- `sabueso/_smonitor.py`: configuration and profiles. It must stay inside the package,
  so that it is installed with it.
- `sabueso/_private/smonitor/`: `catalog.py` (the single source of message templates),
  `warnings.py`, `emitter.py`, `outcomes.py` and `meta.py`.
- `sabueso/__init__.py` calls `ensure_configured(PACKAGE_ROOT)` on import.
- `@signal` decorates `resolve_protein_card`, `resolve_molecule_card` and `ligand_deck`.
- `tests/core/test_smonitor_integration_offline.py` holds the five mandatory checks of
  the SMonitor guide. The first one runs `smonitor --validate-config` against the
  package.

## Known issues

- `@signal` (SMonitor) and `@arg_digest` (ArgDigest) each wrap a public function in
  extra frames, so a warning raised inside it points at their decorator module unless the
  stack level skips those frames. `outcomes.py` used to count them by hand
  (`_CALLER = 4`), and it broke the day ArgDigest's wrapper was added. It now measures the
  level: the first frame outside `sabueso`, `smonitor` and `argdigest`
  (`_user_stacklevel`).
  - SMonitor 0.17.0 resolved uibcdf/smonitor#23: `DiagnosticBundle.warn` now skips
    SMonitor's own frames when it applies `stacklevel`. Sabueso therefore requires
    SMonitor >= 0.17.0, and `_user_stacklevel` passes over SMonitor frames without
    counting them.
  - Counting them too pointed warnings into pytest's own code. CI caught it on
    2026-09-26, eight minutes after 0.17.0 was published.
  - Sabueso and ArgDigest frames are still counted until ArgDigest offers the same.
  - The attribution test in `test_smonitor_integration_offline.py` guards it.
- The guide's check 2 walks only the grouped catalog shape, so on a flat catalog it
  passes while checking nothing (uibcdf/smonitor#22). Sabueso's catalog is grouped, and
  our check also asserts that it found the full set of codes.
- A development environment with an older SMonitor (before 0.17.0) is not supported;
  `devtools/conda-envs/development_env.yaml` requires `>=0.17.0`.

Human literal exploration (#148) reuses those argument/storage diagnostics. Wrong
paths, foreign item/context references and unsupported display columns are errors,
not empty scientific answers. Natures without an implemented scientific question
catalog report `unsupported`; literal null/empty values never imply source absence.
Protein questions report missing canonical context as `missing_prerequisite` and
unsupported sequence axes as `unsupported`; invalid keys/options/regions use the
existing SMonitor argument diagnostic. No such outcome starts acquisition.

Structural exploration returns `not_applicable` for other Card natures and
`missing_prerequisite` for a protein without a pinned identity. An empty admitted
inventory retains original exclusions/source scope. Bad projections, scientific
options and quantity dimensions use the existing argument diagnostic; they never
become biological absence. Paging/explanation reads only materialized content.

Nature-specific exploration (#148) keeps unsupported generic question catalogs,
wrong-nature topics (`not_applicable`), no retained rows (`empty`) and missing pinned
coverage identity (`missing_prerequisite`) distinct. Original knowledge-state
classification and scoped explanation keep their existing rules/outcomes; display
filtering never turns missing requests into biological absence. Raw quality remains
available separately. Invalid record selection and ignored-looking option typos are
argument errors rather than empty source answers.

Contextual navigation (#148) reports `context_not_supplied` for a known target
without a captured Card, `ambiguous` for multiple supported pins, and
`missing_prerequisite` for unavailable identity basis or a missing record in an
explicitly supplied pin. It never chooses another revision or turns an operational
gap into source-stated absence. Context-only views have no destination explorer.
`follow` on a non-link view or a foreign result item uses the existing argument
diagnostic, including when digestion is skipped.

Saved exploration (#148) uses existing `StorageError` diagnostics for failed atomic
writes, invalid digests/seals/locations/values, foreign membership, missing required
support and unsupported required historical verification. Unsupported derived saves
are explicit through `capabilities["save"]` and `StorageError`; optional unretained
operations return `not_saved`. Saved representations/mode and `view.validation`
separate recorded content, verified source bindings and unestablished authenticity
or scientific truth. Scientific format @2 additionally reports the named historical
rules actually checked; the literal @1 reader remains supported. Unknown required
historical versions fail explicitly. No error starts acquisition or changes a prior output.
