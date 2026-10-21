# Clinical layer

A molecule card can hold what its sources state about the molecule's clinical use: the
indications ChEMBL records, with their maximum phase, and the registered trials those
indications cite.

```{note}
The clinical layer is available since release 0.6.0.
```

```python
import sabueso

card, _ = sabueso.resolve("chembl:CHEMBL110", trials={})  # benznidazole
view = card.clinical()
view["max_phase"]  # 4.0, ChEMBL's maximum phase for the molecule
for indication in view["indications"]:
    print(indication["disease"], indication["disease_term"], indication["max_phase"])
for trial in view["trials"][:3]:
    print(trial["trial"], trial["status"], trial.get("phases"), trial["cited_for"])
```

## Options

- `indications=True` adds ChEMBL's drug indications of the molecule's ChEMBL records.
- `trials={}`, or `trials={"limit": 50}`, also adds the ClinicalTrials.gov studies those
  indications cite, by NCT id. It implies `indications`. By default every cited trial
  is fetched, up to 5000, and a cut is reported with a warning.

## What it holds

- **Indications** (`investigated_for`):
  - the disease term as ChEMBL states it (EFO, MONDO, DOID…) and its MeSH heading;
  - the maximum phase for that indication. Phase 4 is approval, as ChEMBL states it;
    phases 1 to 3 are investigational;
  - the references ChEMBL cites: ClinicalTrials.gov, ATC, FDA, EMA, DailyMed.

  Two terms that share a MeSH heading stay two rows. Benznidazole has two for Chagas
  disease, `efo:EFO:0008559` and `mondo:MONDO:0001444`, because ChEMBL states both.
- **Trials** (`tested_in`): what ClinicalTrials.gov states about each trial:
  - status, phases, study type and enrolment;
  - dates, conditions and lead sponsor;
  - the interventions, as written.

  `cited_for` names the indications that cite the trial. A cited id that
  ClinicalTrials.gov does not return after a complete query is kept, with
  `registry: not_found`. Failed or unavailable access does not establish absence.
- **Not fetched.** `not_fetched` lists cited trials the card did not fetch, because
  trials were not requested or were past the limit.

## Why trials come only through ChEMBL

A trial names its interventions as text: a drug name, a brand name, a code. Matching
that text to a molecule would join identities by name, which Sabueso never does. So
Sabueso asks only for the trials ChEMBL cites for the molecule's indications. The link's
basis is ChEMBL's statement, recorded on every trial (`basis:
chembl_drug_indication`).

DrugBank's clinical content is not used: its licence (CC BY-NC 4.0) does not allow
redistribution across MOLI.

## Native registry references

`clinicaltrials.get_study_references(nct_id)` retrieves native registry bibliography
separately from card clinical fields. It preserves declared PMID and links without
following them. To obtain article metadata, query Europe PMC explicitly and retain
both operations' original attribution; see {doc}`attribution`. Registry statements
are source assertions, not proof of efficacy. The explicit reference and article
metadata APIs are available in public 0.14.0.

The development checkout also provides the saved
[clinical bibliography example](https://github.com/uibcdf/sabueso/tree/main/examples/user_journeys#clinical-bibliography).
It selects one source-cited NCT and three explicitly declared PMID, preserves the
original molecular card and records each metadata operation separately. Its reader
uses only saved inputs; reacquisition leaves original reports and citations intact.
Other trials, linked websites, full text and efficacy remain outside that scope.
This example is separate from published-package qualification.
