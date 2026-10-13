# Archive

Resolved, withdrawn, and superseded durable reports are preserved here. Archive meaningful
history rather than deleting it. Each archived document starts with a note saying what
superseded it, when it was archived for that reason.

## Original plans (superseded, still tracked)

Their objectives are not dropped: `devguide/ROADMAP.md` tracks the status of each.

- `ROADMAP_original_2026-01.md`: the first roadmap, phases 0–5.
- `SOURCES_original_plan.md`: the first source plan and its priorities; every source is
  now an entry of `devguide/sources/registry.yaml`.
- `future_direction_2026-09-23.md`: the design conversation on long-term direction
  (Spanish, verbatim); restated in `devguide/SCIENTIFIC_POTENTIAL.md`.
- `NEXT_STEPS_2026-09-23.md`: next steps as of 2026-09-23, all done.

## Superseded working documents

- [consolidation_2026-10-08/README.md](consolidation_2026-10-08/README.md): complete
  pre-consolidation checkpoint, roadmap, API, source and test guidance. Current
  entry documents replace these snapshots; source-specific contracts remain in
  living `devguide/sources/` references.
- [local_work_2026-07/README.md](local_work_2026-07/README.md): triage and current
  recovery of 91 pre-pull local paths, original stash and 87-file local export.
  The current architecture/schema supersede the original prototypes; active APIs
  are described in `devguide/PUBLIC_API.md` and the user notebook guide.

- `CHECKPOINT_log_to_0.4.0.md`: the checkpoint as a log, from Phase 0 to release 0.4.0.
- `QUALITY_AND_TESTS_2026-01.md`: first quality notes, merged into `devguide/TESTS.md`.
- `EVAL_CARDS.md`: decision templates, never used.

## Design reports (resolved)

- `entity_resolver.md`: from source subjects to Sabueso entities (#6).
- `legacy_entity_paths.md`: card paths that merged or mistyped entities (#21).
- `uniprot_mapping_drops_annotations.md`: the UniProt mapping dropped annotations (#13).
- `chembl_bioactivities.md`: bioactivities as relationships (#23).
- `physchem_normalization.md`: cross-source physicochemical properties (#10).
- `molecule_identity.md`: small-molecule identity anchored at the InChIKey (#25).
- `quantities.md`: physical quantities (#32).
- `ligand_binding_sites.md`: ligand binding sites (#28).
- `card_versioning_snapshots.md`: card versioning and snapshots (#7).
- `native_store.md`: the native read/write store (#27).
- `measurement_identity.md`: one measurement across bioactivity sources (#66).
- `moli_ruff_baseline.md`: adopting MOLI's Ruff baseline (#11).

## Infrastructure incidents (resolved)

- [codecov_tls_coverage_upload_2026-10-05.md](codecov_tls_coverage_upload_2026-10-05.md):
  required coverage publication recovered for four exact-SHA checkpoints (#119).

## Source integrity corrections (resolved on development main)

- [uniref_pagination.md](uniref_pagination.md): exact-URL cycle detection and a
  finite logical-page budget (#140); [exact-source receipt](uniref_pagination_checkpoint.json).
  Published 0.14.0 retains the original loop.

- [source_prerequisites.md](source_prerequisites.md): six built-in prerequisite
  gates report unqueried input before client construction (#143), including named
  conditions without queryable MONDO identity;
  [exact-source receipt](source_prerequisites_checkpoint.json). Historical grouping
  coverage is corrected separately under [#144](disease_identity_coverage.md).

- [disease_identity_coverage.md](disease_identity_coverage.md): versioned grouping/
  explanation @3 and coverage @1 distinguish identifier scope without rewriting
  historical rules/pins; packet mapping @7 keeps the original @6 terms adapter
  (#144); [exact-source receipt](disease_identity_coverage_checkpoint.json).
