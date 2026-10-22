"""Protein–molecule bioactivities: derived activity classes and the card view.

A ProteinCard carries measured bioactivities as ``has_bioactivity`` Relationships, one per
source measurement (uibcdf/sabueso#23, ``devguide/archive/chembl_bioactivities.md``).
This module reads them. The activity class of a measurement ("active", "weak", ...) and the
test concentration of a single-point measurement are derived knowledge. They are computed
here, from the stated rule and thresholds, and never stored as SourceAssertions.

Rule ``bioactivity_class@3`` (``@2`` made thresholds and concentrations quantities,
uibcdf/sabueso#32; ``@3`` classifies ranges, #37):

- a potency measure (IC50, Ki, Kd, ...) with relation ``=`` is "active" up to
  ``active_max``, "weak" up to ``weak_max`` and "inactive" beyond;
- an upper bound (``<``, ``<=``) is "active" or "weak" when the bound falls in those bands,
  and "inconclusive" otherwise;
- a lower bound (``>``, ``>=``) is "inactive" when it reaches ``weak_max``, and
  "inconclusive" otherwise;
- a range (ChEMBL ``standard_upper_value``, or a range read in a paper) takes the class
  of its band when both ends fall in the same one, and is "inconclusive" when it spans
  a threshold. Treating it as its lower end would read a range as an exact potency;
- a stated uncertainty does not change the class, which is read from the central value;
- a single-point % inhibition reads as an IC50 bound: an inhibition of at least
  ``single_point_min`` at concentration c means IC50 <= c, and less than that means
  IC50 > c. This assumes a standard dose response. c comes from the assay
  description, and a measurement without c is "inconclusive";
- "Not Determined" measurements are "not_determined", and ChEMBL "Not Active" or
  "Inactive" comments are "inactive";
- other measurement types are "unclassified".

By default, only assays whose target assignment is direct (ChEMBL relationship type
``D``) are included. Homology-assigned measurements (``H``: measured on an ortholog) and
other assignments are excluded, and the exclusion is reported, never silent.

Two consistency checks are derived as well, and reported as measurement flags (#32):

- ``pchembl_consistency@1``: a stated pChEMBL must equal -log10 of the normalized molar
  potency to within one unit of its last stated decimal (ChEMBL states two). ChEMBL does
  not round half up: 26000 nM gives 4.58503 and ChEMBL states 4.58, so half a unit
  would be too strict. A failure is flagged ``pchembl_inconsistent``; pChEMBL itself is
  kept as ChEMBL states it.
- ``unit_scale_discrepancy@1``: two equivalent measurements of one molecule (same type,
  relation ``=``, both in nanomolar) that differ by exactly 3 or 6 orders of magnitude
  are flagged ``scale_discrepancy:<orders>:<other activity_id>``, the signature of a unit
  slip (ChEMBL's "Potential transcription error"). Neither value is corrected.

Potencies are read from each measurement's normalized node (nanomolar, stored with the
card), or normalized through the same explicit ChEMBL unit vocabulary when a measurement
has none. Every conversion names its target unit; the session's unit policy plays no
part (uibcdf/moli#11).
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Tuple

from .labels import molecule_label
from .quantities import (
    CHEMBL_UNITS,
    CONCENTRATION_UNIT,
    canonical_unit,
    converted,
    is_quantity_node,
    normalized_measurement,
    quantity_node,
    scale_discrepancy,
    to_quantity,
)

BIOACTIVITY_CLASS_RULE = "bioactivity_class@3"
PCHEMBL_RULE = "pchembl_consistency@1"
SCALE_RULE = "unit_scale_discrepancy@1"
#: ChEMBL states pChEMBL with two decimals; the tolerance is one unit of the last one.
PCHEMBL_TOLERANCE = 0.01
#: Default thresholds. A threshold is a quantity; a bare number would leave its unit to
#: be guessed (uibcdf/sabueso#32).
DEFAULT_THRESHOLDS: Dict[str, Tuple[float, str]] = {
    "active_max": (10.0, "micromolar"),
    "weak_max": (100.0, "micromolar"),
    "single_point_min": (50.0, "percent"),
}
_THRESHOLD_UNIT = {
    "active_max": CONCENTRATION_UNIT,
    "weak_max": CONCENTRATION_UNIT,
    "single_point_min": "percent",
}
POTENCY_TYPES = frozenset(
    {"IC50", "Ki", "Kd", "EC50", "ED50", "AC50", "XC50", "Potency", "Kb"}
)
SINGLE_POINT_TYPES = frozenset({"Inhibition"})
CLASS_ORDER = (
    "active",
    "weak",
    "inactive",
    "inconclusive",
    "not_determined",
    "unclassified",
)
DIRECT_ASSIGNMENT = "D"
TEST_CONCENTRATION = re.compile(
    r"\bat\s+(?:a\s+concentration\s+of\s+)?(\d+(?:\.\d+)?|\.\d+)\s*(pM|nM|uM|µM|mM|M)\b"
)
NOT_DETERMINED = {"not determined", "nd", "not tested"}
INACTIVE_COMMENTS = {"not active", "inactive"}


def _value_in(node: Dict[str, Any], unit: str) -> float:
    """A quantity node's value in ``unit``, converted explicitly."""
    import pyunitwizard as puw

    if node["unit"] == canonical_unit(unit):
        return float(node["value"])
    q = puw.quantity(float(node["value"]), node["unit"], form="pint")
    return converted(float(puw.convert(q, to_unit=unit, to_type="value")))


def resolve_thresholds(
    thresholds: Dict[str, Any] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """The thresholds in force, as quantity nodes: the defaults, overridden by
    ``thresholds`` ({name: PyUnitWizard quantity or {value, unit} node}).

    Raises ArgumentError for an unknown name, a bare number, or a quantity of the wrong
    dimension.
    """
    import pyunitwizard as puw

    from .errors import ArgumentError, _diagnostic_details_allowed

    resolved = {
        name: quantity_node(value, unit)
        for name, (value, unit) in DEFAULT_THRESHOLDS.items()
    }
    for name, given in (thresholds or {}).items():
        if name not in DEFAULT_THRESHOLDS:
            raise ArgumentError(
                argument="thresholds",
                value=thresholds,
                reason=f"unknown threshold {name!r}; known: {sorted(DEFAULT_THRESHOLDS)}"
                if _diagnostic_details_allowed()
                else "unknown threshold",
            )
        if is_quantity_node(given):
            q = puw.quantity(float(given["value"]), given["unit"], form="pint")
        elif puw.is_quantity(given):  # any form, including a string such as "20 uM"
            q = puw.convert(given, to_form="pint")
        else:
            raise ArgumentError(
                argument="thresholds",
                value=thresholds,
                reason=f"{name!r} must be a quantity (e.g. puw.quantity(1, 'uM')), not a bare number",
            )
        target = _THRESHOLD_UNIT[name]
        try:
            puw.convert(q, to_unit=target)
        except Exception:
            raise ArgumentError(
                argument="thresholds",
                value=thresholds,
                reason=f"{name!r} must be convertible to {target}",
            ) from None
        value, unit = puw.get_value_and_unit(q)
        resolved[name] = quantity_node(float(value), str(unit))
    return resolved


def single_point_concentration(description: str | None) -> Dict[str, Any] | None:
    """The single-point test concentration stated in an assay description, as a quantity
    node in the stated unit (read through the explicit ChEMBL vocabulary)."""
    match = TEST_CONCENTRATION.search(description or "")
    if not match:
        return None
    return quantity_node(float(match.group(1)), CHEMBL_UNITS[match.group(2)])


def _band(value_nM: float, t: Dict[str, float]) -> str:
    if value_nM <= t["active_max"]:
        return "active"
    if value_nM <= t["weak_max"]:
        return "weak"
    return "inactive"


def _bounded(relation: str, value_nM: float, t: Dict[str, float]) -> str:
    if relation in ("=", "~"):
        return _band(value_nM, t)
    if relation in ("<", "<="):
        band = _band(value_nM, t)
        return band if band != "inactive" else "inconclusive"
    if relation in (">", ">="):
        return "inactive" if value_nM >= t["weak_max"] else "inconclusive"
    return "inconclusive"


def classify_measurement(
    measurement: Dict[str, Any],
    assay_description: str | None = None,
    thresholds: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """``{"class", "basis", "test_concentration"?}`` for one measurement.

    ``test_concentration`` is a PyUnitWizard quantity.
    """
    from .quantities import to_quantity

    nodes = resolve_thresholds(thresholds)
    t = {
        "active_max": _value_in(nodes["active_max"], CONCENTRATION_UNIT),
        "weak_max": _value_in(nodes["weak_max"], CONCENTRATION_UNIT),
        "single_point_min": _value_in(nodes["single_point_min"], "percent"),
    }
    kind = measurement.get("type")
    value = measurement.get("value")
    relation = measurement.get("relation") or "="
    comment = (measurement.get("activity_comment") or "").strip().lower()
    if value is None:
        if comment in NOT_DETERMINED:
            return {"class": "not_determined", "basis": "activity_comment"}
        if comment in INACTIVE_COMMENTS:
            return {"class": "inactive", "basis": "activity_comment"}
        return {"class": "inconclusive", "basis": "no_value"}
    if kind in POTENCY_TYPES:
        node = measurement.get("normalized") or normalized_measurement(
            value, measurement.get("units")
        )
        if node is None or node["unit"] != CONCENTRATION_UNIT:
            return {"class": "inconclusive", "basis": "unknown_units"}
        if is_range(measurement):
            upper = upper_node(measurement)
            if upper is None or upper["unit"] != CONCENTRATION_UNIT:
                return {"class": "inconclusive", "basis": "unknown_units"}
            if relation not in ("=", "~"):
                return {"class": "inconclusive", "basis": "potency_range"}
            low = _band(float(node["value"]), t)
            high = _band(float(upper["value"]), t)
            return {
                "class": low if low == high else "inconclusive",
                "basis": "potency_range",
            }
        return {
            "class": _bounded(relation, float(node["value"]), t),
            "basis": "potency",
        }
    if kind in SINGLE_POINT_TYPES and measurement.get("units") == "%":
        if is_range(measurement):
            return {"class": "inconclusive", "basis": "single_point_range"}
        concentration = single_point_concentration(assay_description)
        if concentration is None:
            return {"class": "inconclusive", "basis": "single_point_no_concentration"}
        c_nM = _value_in(concentration, CONCENTRATION_UNIT)
        if relation in ("<", "<=") and value >= t["single_point_min"]:
            return {
                "class": "inconclusive",
                "basis": "single_point",
                "test_concentration": to_quantity(concentration),
            }
        ic50_relation = "<=" if value >= t["single_point_min"] else ">"
        return {
            "class": _bounded(ic50_relation, c_nM, t),
            "basis": "single_point",
            "test_concentration": to_quantity(concentration),
        }
    return {"class": "unclassified", "basis": "measurement_type"}


def bioactivity_derivation(thresholds: Dict[str, Any] | None = None) -> Dict[str, Any]:
    from .relationship_store import make_derivation

    return make_derivation(
        BIOACTIVITY_CLASS_RULE,
        inputs=["has_bioactivity.measurement", "has_bioactivity.assay.description"],
        parameters={
            **resolve_thresholds(thresholds),
            "potency_types": sorted(POTENCY_TYPES),
            "single_point_types": sorted(SINGLE_POINT_TYPES),
            "test_concentration": "assay description text",
            "ranges": "both ends in one band: that band; across a threshold: inconclusive",
            "uncertainty": "not used; the class is read from the central value",
        },
    )


def _flags(q: Dict[str, Any]) -> List[str]:
    m, assay = q.get("measurement", {}), q.get("assay", {})
    flags = []
    if m.get("data_validity_comment"):
        flags.append(f"data_validity:{m['data_validity_comment']}")
    if m.get("potential_duplicate"):
        flags.append("potential_duplicate")
    if assay.get("relationship_type") is None:
        flags.append("missing_assay_metadata")
    if "unknown origin" in (assay.get("description") or "").lower():
        flags.append("assay_organism_unknown_origin")
    if assay.get("variant_mutation"):
        flags.append(f"variant:{assay['variant_mutation']}")
    return flags


def is_range(m: Dict[str, Any]) -> bool:
    """Whether a measurement is stated as a range (it has an upper end)."""
    return m.get("upper_value") is not None or bool(m.get("normalized_upper"))


def upper_node(m: Dict[str, Any]) -> Dict[str, Any] | None:
    """The normalized upper end of a range, from the card or the explicit vocabulary.

    Cards written before schema 0.3.2 keep ChEMBL's upper value only verbatim.
    """
    if m.get("normalized_upper"):
        return m["normalized_upper"]
    return normalized_measurement(m.get("upper_value"), m.get("units"))


def _uncertainty(m: Dict[str, Any]) -> Dict[str, Any] | None:
    """A stated uncertainty with PyUnitWizard quantities, or None."""
    node = m.get("normalized_uncertainty")
    if not node:
        return None
    return {
        key: to_quantity(value) if is_quantity_node(value) else value
        for key, value in node.items()
    }


def _potency_node(m: Dict[str, Any]) -> Dict[str, Any] | None:
    """The measurement's normalized node, from the card or the explicit vocabulary."""
    return m.get("normalized") or normalized_measurement(m.get("value"), m.get("units"))


def pchembl_consistent(pchembl: Any, node: Dict[str, Any] | None, relation: Any):
    """True/False when a stated pChEMBL can be checked against the normalized potency,
    None when it cannot (no pChEMBL, no nanomolar value, or a bound)."""
    if (
        pchembl is None
        or node is None
        or node["unit"] != CONCENTRATION_UNIT
        or (relation or "=") != "="
        or node["value"] <= 0
    ):
        return None
    expected = 9.0 - math.log10(float(node["value"]))
    return abs(float(pchembl) - expected) <= PCHEMBL_TOLERANCE + 1e-9


def _scale_flags(measurements: List[Dict[str, Any]], potencies: List[Any]) -> None:
    """Flag pairs of equivalent measurements that differ by exactly 3 or 6 orders."""
    for i, a in enumerate(measurements):
        for j in range(i + 1, len(measurements)):
            b = measurements[j]
            if potencies[i] is None or potencies[j] is None:
                continue
            if a["type"] != b["type"] or (a["relation"] or "=") != "=":
                continue
            if (b["relation"] or "=") != "=":
                continue
            orders = scale_discrepancy(potencies[i], potencies[j])
            if orders:
                a["flags"].append(f"scale_discrepancy:{orders}:{b['activity_id']}")
                b["flags"].append(f"scale_discrepancy:{orders}:{a['activity_id']}")


def consistency_checks() -> List[Dict[str, Any]]:
    from .relationship_store import make_derivation

    return [
        make_derivation(
            PCHEMBL_RULE,
            inputs=["has_bioactivity.measurement.pchembl", "measurement.normalized"],
            parameters={
                "expected": "9 - log10(potency / nanomolar)",
                "tolerance": PCHEMBL_TOLERANCE,
                "flag": "pchembl_inconsistent",
            },
        ),
        make_derivation(
            SCALE_RULE,
            inputs=["has_bioactivity.measurement.normalized"],
            parameters={
                "orders": [3, 6],
                "equivalent": "same molecule, same type, relation '=', nanomolar",
                "flag": "scale_discrepancy:<orders>:<other activity_id>",
            },
        ),
    ]


def _activity_order(item: Dict[str, Any]) -> tuple:
    """ChEMBL activity ids (numbers) first, in order; curated ids (text) after them."""
    activity_id = item.get("activity_id")
    if isinstance(activity_id, int):
        return (0, activity_id, "")
    return (1, 0, str(activity_id or ""))


def _stated_smiles(card: Any, rel: Dict[str, Any]) -> str | None:
    """SMILES of the tested molecule as stated in the supporting activity record."""
    for sa_id in rel.get("source_assertion_ids", []):
        sa = card.source_assertion_store.get(sa_id) or {}
        activity = (sa.get("asserted_value") or {}).get("activity")
        if isinstance(activity, dict) and activity.get("canonical_smiles"):
            return activity["canonical_smiles"]
    return None


def bioactivities_view(
    card: Any,
    include_indirect: bool = False,
    thresholds: Dict[str, Any] | None = None,
    *,
    _support=None,
) -> Dict[str, Any]:
    """Molecule-centric summary of the card's ``has_bioactivity`` relationships.

    Returns ``{"items", "excluded", "documents", "scope", "classification", "checks"}``.
    Each measurement keeps the source's ``value`` and ``units`` verbatim and adds
    ``normalized``, a PyUnitWizard quantity (nanomolar or percent) or None. ``items`` has one
    entry per parent molecule, holding all its measurements and its strongest class.
    Measurements from assays that were not assigned directly to the target are excluded
    unless ``include_indirect``, and they are listed in ``excluded``.
    """
    from .measurements import _molecules, measurement_groups, record_source

    molecules: Dict[str, Dict[str, Any]] = {}
    excluded: List[Dict[str, Any]] = []
    documents: Dict[str, int] = {}
    # One measurement stated by several sources is one group (#66): classes and counts
    # are per measurement, never per record.
    identity_support = {} if _support is not None else None
    identity = measurement_groups(card, _support=identity_support)
    record_decisions, group_decisions = [], []
    group_of = identity["group_of"]
    # A molecule another source names differently (bindingdb:…) joins the ChEMBL entry of
    # the same entity, through the card's glossary.
    entity_of = _molecules(card)
    preferred: Dict[str, str] = {}
    for rel in card.relationships(predicate="has_bioactivity"):
        q = rel.get("qualifiers") or {}
        if record_source(q) != "ChEMBL":
            continue
        chembl_key = q.get("parent_molecule") or rel["object_ref"]
        preferred.setdefault(entity_of.get(chembl_key, chembl_key), chembl_key)
    for rel in card.relationships(predicate="has_bioactivity"):
        q = rel.get("qualifiers", {})
        m, assay, doc = (
            q.get("measurement", {}),
            q.get("assay", {}),
            q.get("document", {}),
        )
        assignment = assay.get("relationship_type")
        if not include_indirect and assignment != DIRECT_ASSIGNMENT:
            excluded.append(
                {
                    "activity_id": q.get("activity_id"),
                    "molecule_ref": rel["object_ref"],
                    "assay": assay.get("id"),
                    "reason": f"target_assignment:{assignment}",
                    "assay_organism": assay.get("organism"),
                }
            )
            record_decisions.append(
                {
                    "relationship_id": rel["id"],
                    "included": False,
                    "reason": f"target_assignment:{assignment}",
                }
            )
            continue
        derived = classify_measurement(m, assay.get("description"), thresholds)
        node = _potency_node(m)
        flags = _flags(q)
        ranged = is_range(m)
        upper = upper_node(m) if ranged else None
        # A range has no single potency: no pChEMBL check, no scale comparison.
        if (
            not ranged
            and pchembl_consistent(m.get("pchembl"), node, m.get("relation")) is False
        ):
            flags.append("pchembl_inconsistent")
        measurement = {
            "relationship_id": rel["id"],
            "activity_id": q.get("activity_id"),
            "molecule_ref": rel["object_ref"],
            "type": m.get("type"),
            "relation": m.get("relation"),
            "value": m.get("value"),
            "units": m.get("units"),
            "normalized": to_quantity(node) if node else None,
            "normalized_upper": to_quantity(upper) if upper else None,
            "uncertainty": _uncertainty(m),
            "pchembl": m.get("pchembl"),
            **derived,
            "assay": assay.get("id"),
            "assay_organism": assay.get("organism"),
            "target_assignment": assignment,
            "document": doc.get("id")
            or (f"pubmed:{doc['pubmed']}" if doc.get("pubmed") else None)
            or (f"doi:{doc['doi']}" if doc.get("doi") else None),
            "year": doc.get("year"),
            "flags": flags,
            # Read in a paper and recorded by a curator, not a ChEMBL record (#44).
            "curated": bool(assay.get("curated")),
            "source": record_source(q),
            "group": group_of.get(rel["id"], rel["id"]),
            # A declared copy (#68): it never votes for its group's class when the
            # original is there, since its table may drop the relation (">").
            "copy": bool(q.get("copy_of")),
        }
        if doc.get("id"):
            documents[doc["id"]] = documents.get(doc["id"], 0) + 1
        key = q.get("parent_molecule") or rel["object_ref"]
        if record_source(q) != "ChEMBL":
            for ref in (q.get("molecule_ref"), rel["object_ref"]):
                entity = entity_of.get(ref) if ref else None
                if entity in preferred:
                    key = preferred[entity]
                    break
        entry = molecules.setdefault(
            key,
            {
                "molecule_ref": key,
                "tested_forms": set(),
                "name": None,
                "smiles": None,
                "measurements": [],
                "potencies": [],
            },
        )
        entry["tested_forms"].add(rel["object_ref"])
        if entry["smiles"] is None or rel["object_ref"] == key:  # prefer the parent
            entry["name"] = q.get("molecule_name") or entry["name"]
            entry["smiles"] = _stated_smiles(card, rel) or entry["smiles"]
        entry["measurements"].append(measurement)
        record_decisions.append(
            {"relationship_id": rel["id"], "included": True, "molecule_ref": key}
        )
        entry["potencies"].append(
            node["value"]
            if node and node["unit"] == CONCENTRATION_UNIT and not ranged
            else None
        )

    items = []
    for entry in molecules.values():
        _scale_flags(entry["measurements"], entry["potencies"])
        measurements = sorted(entry["measurements"], key=_activity_order)
        by_group: Dict[str, List[Dict[str, Any]]] = {}
        for x in measurements:
            by_group.setdefault(x["group"], []).append(x)
        classes: Dict[str, int] = {}
        for group_id, members in by_group.items():
            voters = [x for x in members if not x["copy"]] or members
            found = {x["class"] for x in voters}
            # Sources of one measurement that classify it differently: inconclusive.
            cls = found.pop() if len(found) == 1 else "inconclusive"
            group_decisions.append(
                {
                    "molecule_ref": entry["molecule_ref"],
                    "group": group_id,
                    "records": [x["relationship_id"] for x in members],
                    "voters": [x["relationship_id"] for x in voters],
                    "voter_classes": sorted({x["class"] for x in voters}),
                    "class": cls,
                    "basis": "non_copy_records"
                    if any(not x["copy"] for x in members)
                    else "copies_only",
                }
            )
            classes[cls] = classes.get(cls, 0) + 1
        pchembls = [x["pchembl"] for x in measurements if x["pchembl"] is not None]
        items.append(
            {
                "molecule_ref": entry["molecule_ref"],
                **dict(
                    zip(
                        ("label", "label_source"),
                        molecule_label(
                            entry["name"],
                            [entry["molecule_ref"], *sorted(entry["tested_forms"])],
                            entry["molecule_ref"],
                        ),
                    )
                ),
                "tested_forms": sorted(entry["tested_forms"]),
                "name": entry["name"],
                "smiles": entry["smiles"],
                "class": min(classes, key=CLASS_ORDER.index),
                "classes": classes,
                "discordant": bool({"active", "weak"} & classes.keys())
                and "inactive" in classes,
                "best_pchembl": max(pchembls) if pchembls else None,
                "measurement_count": len(by_group),
                "record_count": len(measurements),
                "sources": sorted({x["source"] for x in measurements}),
                "documents": sorted(
                    {x["document"] for x in measurements if x["document"]}
                ),
                "measurements": measurements,
            }
        )
    items.sort(
        key=lambda i: (
            CLASS_ORDER.index(i["class"]),
            -(i["best_pchembl"] or 0.0),
            i["molecule_ref"],
        )
    )
    if _support is not None:
        _support.update(
            identity=identity,
            identity_support=identity_support,
            records=record_decisions,
            groups=group_decisions,
        )
    return {
        "items": items,
        "excluded": sorted(excluded, key=_activity_order),
        "documents": dict(sorted(documents.items(), key=lambda kv: (-kv[1], kv[0]))),
        "scope": {
            "target_assignment": "any" if include_indirect else DIRECT_ASSIGNMENT
        },
        "classification": bioactivity_derivation(thresholds),
        "checks": consistency_checks(),
        "measurement_identity": {
            k: identity[k] for k in ("rule", "groups", "ambiguous", "review")
        },
    }
