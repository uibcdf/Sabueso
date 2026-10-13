# Sabueso — Diagnostics (SMonitor)

Sabueso reports through SMonitor, the UIBCDF diagnostics layer, as required by MOLI's
support-library policy (uibcdf/sabueso#31).

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

The exceptions keep the message written where they are raised (template `{message}`)
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
