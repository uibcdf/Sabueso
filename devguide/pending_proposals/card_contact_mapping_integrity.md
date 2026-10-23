---
summary: Bind original RCSB contact inputs and prevent unidentified or ambiguous joins.
issue: uibcdf/sabueso#148
status: open
opened: 2026-10-23
closed:
verification: tested
area: [knowledge-integrity, structures, human-exploration, schema]
blocked_by: []
supersedes: []
---

# Original contact mapping and instance scope

This is the RCSB prerequisite for the
[complete exploration design](card_exploration_completion_0150.md), not completion
of annotation/region/assembly navigation. It corrects knowledge integrity in new
mappings and current native interpretation while preserving original stored history.

## Reproduced defects

Execution of the prior mapper from `18b3b6e` on explicitly synthetic inputs
confirms two defects: missing `ligand_asym_id` values join unrelated neighbours
under `(component, None)`, and competing source alignments select the first
accession instead of reporting ambiguity. Further regression cases establish that
equal residue/chain labels in different source polymer instances must not collapse
contact distances; conflicting bound flags cannot silently retain the first flag.
The native instance view also previously collected positions without their UniProt
axis, admitting foreign or unknown-axis numbers into the focal sequence list.
These are Sabueso mapping/interpretation defects, not demonstrated provider defects.

## New mapping rule and retained inputs

`mappings/rcsb_ligand_contacts_v1.py` defines `rcsb_ligand_contacts@1`:

- A declared component/ligand-asym pair identifies an instance within the structure.
  An unidentified neighbour remains a separate occurrence; no shared instance is
  inferred from component, chain, residue number or proximity.
- Repeated neighbours take a minimum distance only within the same original
  polymer-entity/instance/residue scope. Units remain PyUnitWizard quantity nodes.
- Coordinates are placed only when the source alignments yield one unique
  `(UniProt accession, position)`. Every competing candidate is retained in the
  scoped ambiguity diagnostic; no match remains unplaced.
- Missing/null/empty/malformed neighbour declarations, unidentified occurrences,
  missing chains, invalid distances and conflicting bound flags remain explicit.
  Conflicting flags yield unknown, preserving both source values and locators.

New RCSB assertions retain original polymer-entity records under
`asserted_value.ligand_contact_inputs.polymer_entities`, canonically ordered as a
collection without changing the source values. Those records include original
alignment regions, polymer-instance identifiers and neighbour rows. Mapped contact
instances are removed from the assertion's projected `nonpolymer_entities`; they
belong to relationship qualifiers. No derived contact finding is a SourceAssertion.
Native access still returns the original provider response unchanged.

`has_structure.derivation` names the rule, original assertion input and Sabueso
version. Its parameters name `qualifier_paths: ["ligands[].instances"]`, the exact
`input_path`, and diagnostics whose indices address the retained original inputs.
This scope does not claim lineage for coverage, constructs, mutations, assemblies
or other qualifiers. Contact replay needs those original inputs, never a present
Card sequence substituted for a historical mapping input.

## Native interpretation and history

`ligand_instance_scope@1` is carried by native ligand-site items. Instance position
lists carry `sequence_ref` and include only exact source-stated focal UniProt
positions; `unplaced_contacts` retains complete foreign/unknown-axis contacts.
Recorded chains have explicit `chain_scope`. Unidentified instances cannot prove
chain spanning; incomplete identity/chain scope yields unknown when no known
positive span is retained. Original chains/unplaced values are detached from the
Card. Absence of a recorded span is not a claim about every unqueried structure.
Native instances name their exact structure relationship; item-level
`structure_support.relationship_ids` also retains the input for investigation
flags when no instance rows are present. Packet support/terms can therefore follow
the RCSB input rather than crediting only the aggregate-site source.

The optional stored derivation accumulates in unpublished schema 0.3.14, with its
shape and `SCHEMA_CHANGES` entry. Migration reports missing contact basis only for
applicable RCSB-enriched structures. It does not manufacture provenance, change
old assertions/contacts or rewrite frozen schemas/cards/capsules. Refresh with
structures can acquire the new original inputs. Current live native interpretation
is distinct from inert reading of an original saved result.

New packets use `packet_aspects@8`, keeping the existing query/acquisition areas
and declaring `ligand_instance_scope@1` beside `annotated_site_overlap@2` in their
indexes. Mappings `@6`/`@7` keep the frozen native projection copied from `18b3b6e`;
their original full facts, index rule lists and terms reconstruction never use the
new instance reader. Cross-mapping knowledge equivalence remains indeterminate,
not silently equal. The packet envelope format is unchanged. Consumer coordination
belongs to MOLI #36; no shared architecture/terminology rule is redefined.
Full and index terms at `@8` include these exact structure inputs, including the
flag-only case. Historical terms retain their original scope; they do not acquire
new support retroactively.

Source views retain the exact original relationship-level support and expose the
captured derivation in `item.support`/`explain()`. Saved instance reading validates
original membership without reconstructing Cards or rerunning the contact mapper.
The explorer does not independently certify arbitrary claimed mapping metadata.

## Qualification and remaining scope

The final source passes **6,920 local-original offline cases / 606.39 seconds**,
with twelve pytest-receptor workers, thirteen expected fixture warnings and fatal
SQLite/unraisable guards. The preceding focused mapping and packet gates also
pass, with fatal runtime guards. Twenty-eight new regression cases cover contact
scope and historical/current packet support. The first full run's two coordination
failures (index rule inventory and an expected migration-gap list) are corrected;
only the final complete receipt qualifies this source. Exact-SHA remote CI/
governance receipts belong to #148; interrupted/failed runs are not passing receipts.
The independent public instance reader reopens its original support without
fixtures, Card reconstruction or a live contact mapper. Original source inputs,
frozen schemas/cards and historical capsules remain unchanged. Canonical UTF-8
mapping output adds 19,097 / 20,883 / 18,907 bytes for public fixtures 1SUX / 1HTI /
2OMA respectively; these bounded source-output measurements do not qualify Card/
session/RSS/token or general workload performance. Useful original-input/source/environment hashes,
old-mapper reproduction, logs and independent saved examples live in
`recovered_work/rcsb_contact_lineage_20261023/`, owner #148, review at the next
exploration checkpoint or release. Remove owned disposable test/build resources
after their last use.

AlphaFold match/isoform input binding remains the next prerequisite. Historical
missing context, whole-structure derivation, aggregate/assembly/region transitions,
compact scientific parity and researcher acceptance remain open. No release,
source availability, installed-artifact or human-usability claim follows from
these source-level checks. Assess the published-version integrity impact under
the existing release coordination; this work does not resume 0.15.0 consolidation.

A separate confirmed core follow-up is owned by
[#156](https://github.com/uibcdf/sabueso/issues/156), consuming #148: adding a second
derived occurrence with different parameters through `RelationshipStore.add`
retains both source references and alternative qualifier values but drops the
incoming derivation metadata. An exact synthetic reproduction is retained in
`merge-followup.json` with owner #156. This block qualifies one scoped mapping occurrence; it does
not claim complete merged derivation history. Resolve that core support path
before combining derived occurrences in broader navigation/comparison.

Consumer coordination is observable in
[MOLI #36](https://github.com/uibcdf/moli/issues/36#issuecomment-6373150846), with
public mapping/support scope only and no private pilot material. Exact published
source and qualification updates follow through that same issue and #148.
