"""Curated literature assertions on existing card fields (uibcdf/sabueso#41, part 2).

A person reads a publication and records what it states as a
SourceAssertion: ``source.type = "literature"``, the publication as the record
(``pubmed:<id>`` or ``doi:<doi>``), and the curation in ``source_metadata.curation``
(curator, date, locator, optional short quote). Sabueso does not read the paper. It
checks the claim's shape against the field, stores it, and compares it mechanically
with what other sources state:

An agent-prepared reading remains a draft until human review. A tool/model
extraction retains its own acquisition method, even after human validation;
using a curator's name does not turn extraction into human curation (#92/#105).

- a **scalar** field (``properties.physchem.*``) is resolved again from all its
  assertions. "Literature" is not in any priority list, so a curated value is selected
  only when nothing else states the field;
- a **list** field compares items by an identity (``ITEM_IDENTITY``), for example
  position and substitution for a mutagenesis. An item with the same identity and the
  same content corroborates; the same identity with a different content **differs**.
  Sabueso cannot tell whether "abolishes homodimer" and "Loss of dimerization" mean the
  same thing, so a difference is flagged for a reader, never judged a contradiction;
- free-text lists (``annotations.function``, ``subunit``...) have no identity: the item
  is added and marked ``not_compared``.

Nothing is discarded or overridden. Every outcome is recorded in
``quality.curation``; a difference also goes to ``quality.conflicts`` and raises
``CuratedDisagreementWarning``. How a curated assertion bears on a project's hypotheses
is Nextia Evidence, not Sabueso's (SourceAssertion ≠ Evidence).
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Tuple

from .errors import SchemaError
from .quantities import FIELD_UNITS, canonical_unit, converted, is_quantity_node
from .source_assertion_store import (
    assertion_value,
    generate_source_assertion_id,
    make_source_assertion,
)

LITERATURE = "Literature"

SCALAR_FIELDS = frozenset(
    {
        "properties.physchem.aromatic_rings",
        "properties.physchem.formula",
        "properties.physchem.hba",
        "properties.physchem.hbd",
        "properties.physchem.logp",
        "properties.physchem.molecular_weight",
        "properties.physchem.molecule_type",
        "properties.physchem.rotatable_bonds",
        "properties.physchem.tpsa",
    }
)


def _positions(item: Dict[str, Any]) -> Tuple[int, ...]:
    sequence = (item.get("location") or {}).get("sequence") or {}
    spans = sequence.get("fragments") or [
        {"start": sequence.get("start"), "end": sequence.get("end")}
    ]
    return tuple(
        sorted(
            {
                p
                for s in spans
                if s.get("start") is not None
                for p in range(s["start"], (s.get("end") or s["start"]) + 1)
            }
        )
    )


#: Biological context of a target (#60): per field, the keys an item may state, and
#: those it must. Values are text, kept as stated: a phenotype or a role is never turned
#: into a category, and "essential" is recorded only as the authors' own ``call``. The
#: organism is the card's: a result on an ortholog is curated on the ortholog's card.
CONTEXT_KEYS: Dict[str, Tuple[Tuple[str, ...], Tuple[str, ...]]] = {
    "annotations.stage_expression": (
        ("stage", "observation"),
        ("host", "method", "level", "note"),
    ),
    "annotations.essentiality": (
        ("method", "phenotype"),
        ("stage", "host", "condition", "call", "note"),
    ),
    "annotations.accessibility": (
        ("compartment",),
        ("exposure", "stage", "host", "method", "note"),
    ),
    "annotations.metabolic_role": (
        ("pathway", "role"),
        ("stage", "host", "method", "note"),
    ),
}
CONTEXT_FIELDS = tuple(CONTEXT_KEYS)


def _context_key(*keys: str) -> Callable[[Any], Any]:
    return lambda i: tuple((i.get(k) or "").strip().casefold() for k in keys)


def _substitution(item: Dict[str, Any]) -> tuple:
    """A deletion (``missing``, #80) is its own substitution, never an unstated one."""
    s = item.get("substitution") or {}
    return (
        s.get("original"),
        tuple(s.get("alternatives") or []),
        bool(s.get("missing")),
    )


#: How two items of a list field are recognised as the same item. None: free text,
#: which cannot be compared without reading it.
ITEM_IDENTITY: Dict[str, Callable[[Any], Any] | None] = {
    "features_positional.mutagenesis": lambda i: (_positions(i), _substitution(i)),
    "features_positional.natural_variant": lambda i: (_positions(i), _substitution(i)),
    "features_positional.binding_site": lambda i: (
        _positions(i),
        ((i.get("ligand") or {}).get("name") or "").lower(),
    ),
    "features_positional.active_site": _positions,
    "features_positional.disulfide_bond": _positions,
    "features_positional.glycosylation": _positions,
    "features_positional.modified_residue": _positions,
    "annotations.disease": lambda i: i.get("accession") or i.get("name", "").lower(),
    "annotations.catalytic_activity": lambda i: i.get("rhea_id") or i.get("reaction"),
    "annotations.subcellular_location": lambda i: (i.get("location") or "").lower(),
    # Biological context (#60): the same statement is the same condition (stage, host,
    # method...); a different observation there differs.
    "annotations.stage_expression": _context_key("stage", "host", "method"),
    "annotations.essentiality": _context_key("method", "stage", "host", "condition"),
    "annotations.accessibility": _context_key("compartment", "stage", "host"),
    "annotations.metabolic_role": _context_key("pathway", "stage", "host"),
    # A name a publication uses for the protein, e.g. a paralog's "TIM2" (#55). Resolving
    # by that name through a curation store anchors it to this entry.
    "names.synonyms": lambda i: (i.get("name") or "").strip().casefold(),
    # A typed free-text claim (#43): recorded and listed by topic, never compared.
    "literature.claims": None,
    "annotations.function": None,
    "annotations.pathway": None,
    "annotations.subunit": None,
    "annotations.ptm": None,
    "annotations.polymorphism": None,
    "annotations.tissue_specificity": None,
}
LIST_FIELDS = frozenset(ITEM_IDENTITY)
CURATABLE_FIELDS = SCALAR_FIELDS | LIST_FIELDS

#: Predicates a curated assertion may state. Not identity links (same_as...), not
#: has_structure (the PDB states structures), not described_in (citing is not a claim),
#: and not has_bioactivity yet: telling a curated measurement from the ChEMBL record of
#: the same paper needs its own design (uibcdf/sabueso#44).
CURATABLE_PREDICATES = frozenset(
    {
        "interacts_with",
        "functionally_associated_with",
        "annotated_with",
        "classified_in",
        "has_ligand_site",
        "has_interface_with",
    }
)

#: Keys an item must state, per list field (beyond a location for positional fields).
REQUIRED_KEYS = {
    "features_positional.mutagenesis": ("substitution", "description"),
    "features_positional.natural_variant": ("substitution",),
    "annotations.disease": ("name",),
    "annotations.catalytic_activity": ("reaction",),
    "annotations.subcellular_location": ("location",),
    "names.synonyms": ("name",),
}


def _key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _subject(card: Any) -> str:
    card_id = card.meta.get("card_id") or ""
    entity_type = card.meta.get("entity_type") or ""
    prefix = f"sabueso:{entity_type}:"
    if not card_id.startswith(prefix):
        raise SchemaError("A curated assertion needs a card with a stable card_id.")
    return card_id[len(prefix) :]


def _sequence_id(subject: str) -> str | None:
    namespace, _, record = subject.partition(":")
    return f"UniProt:{record}" if namespace == "uniprot" else None


#: Topics of free-text claims (#43). Sabueso's own, provisional vocabulary: a new topic
#: is an additive schema change, and a vocabulary shared with Praxis or Nextia would be
#: agreed in uibcdf/moli. When claims of one topic recur, they should become a structured
#: field (migrated with ``migrate_card``), as biological context did (#60,
#: ``CONTEXT_FIELDS``); a claim on those topics stays possible as free text.
CLAIM_TOPICS = (
    "interface",
    "mechanism",
    "selectivity",
    "stability",
    "inhibition",
    "structure",
    "dynamics",
    "localization",
    "expression",
    "essentiality",
    "pathway",
    "other",
)


def _claim(value: Any) -> Dict[str, Any]:
    """A claim item ``{topic, text, about}``, or SchemaError."""
    if not isinstance(value, dict):
        raise SchemaError("A claim is {'topic', 'text', 'about'?}.")
    unknown = sorted(set(value) - {"topic", "text", "about"})
    if unknown:
        raise SchemaError(f"A claim takes topic, text and about, not {unknown}.")
    topic, text = value.get("topic"), value.get("text")
    if topic not in CLAIM_TOPICS:
        raise SchemaError(
            f"Unknown claim topic {topic!r}; expected one of {list(CLAIM_TOPICS)}."
        )
    if not isinstance(text, str) or not text.strip():
        raise SchemaError("A claim states its text.")
    about = value.get("about") or []
    if not isinstance(about, (list, tuple)) or not all(
        isinstance(a, str) and ":" in a and a.strip() for a in about
    ):
        raise SchemaError(
            "about lists references such as 'chembl:CHEMBL123', 'pdb:1SUX' or "
            "'residues:14,96'."
        )
    item: Dict[str, Any] = {"topic": topic, "text": text.strip()}
    if about:
        item["about"] = sorted({a.strip() for a in about})
    return item


def _item(field_path: str, value: Any, subject: str) -> Any:
    """The item as it will be stored, or SchemaError if its shape does not fit."""
    if field_path == "literature.claims":
        return _claim(value)
    if ITEM_IDENTITY[field_path] is None:
        if not isinstance(value, str) or not value.strip():
            raise SchemaError(f"{field_path} takes a non-empty text.")
        return value.strip()
    if not isinstance(value, dict):
        raise SchemaError(f"{field_path} takes a dict item.")
    item = dict(value)
    if field_path.startswith("features_positional."):
        if "location" not in item:
            # Shorthand: {"start": 105} or {"start": 12, "end": 14}, in the card's
            # UniProt numbering.
            if not isinstance(item.get("start"), int):
                raise SchemaError(
                    f"{field_path} needs a location, or 'start' in UniProt numbering."
                )
            start = item.pop("start")
            end = item.pop("end", start)
            item["location"] = {
                "kind": "sequence",
                "sequence": {
                    "sequence_id": _sequence_id(subject),
                    "start": start,
                    "end": end,
                    "indexing": "1-based",
                },
            }
        if not _positions(item):
            raise SchemaError(f"{field_path} needs at least one sequence position.")
    if field_path in CONTEXT_KEYS:
        required, optional = CONTEXT_KEYS[field_path]
        unknown = sorted(set(item) - set(required) - set(optional))
        if unknown:
            raise SchemaError(
                f"{field_path} items take {list(required + optional)}, not {unknown}."
            )
        for key, value in item.items():
            if not isinstance(value, str) or not value.strip():
                raise SchemaError(f"{field_path}: {key} is a non-empty text.")
            item[key] = value.strip()
        missing = [k for k in required if k not in item]
        if missing:
            raise SchemaError(f"{field_path} items need {missing}.")
        return item
    missing = [k for k in REQUIRED_KEYS.get(field_path, ()) if not item.get(k)]
    if missing:
        raise SchemaError(f"{field_path} items need {missing}.")
    return item


def _decimals(text: str) -> int | None:
    match = re.match(r"\s*[-+]?(\d+)(?:\.(\d+))?(?![\d.eE])", text)
    if match is None:
        return None
    return len(match.group(2) or "")


def _scalar(field_path: str, value: Any) -> Tuple[Any, Any, int | None]:
    """``(asserted, normalized, stated decimals in the field's unit)``.

    A quantity field takes a quantity in any PyUnitWizard form, never a bare number. It
    is converted explicitly to the field's negotiated unit. The value is kept as written
    (a string stays verbatim), and its stated precision is carried into the field's
    unit: "0.9 kDa" states hundreds of daltons, "824.97 Da" hundredths.
    """
    unit = FIELD_UNITS.get(field_path)
    if unit is None:
        if isinstance(value, bool) or not isinstance(value, (int, float, str)):
            raise SchemaError(f"{field_path} takes a number or a text.")
        return value, value, None
    import pyunitwizard as puw

    if is_quantity_node(value):
        q = puw.quantity(float(value["value"]), value["unit"], form="pint")
        asserted, text = dict(value), repr(value["value"])
    elif isinstance(value, str) or puw.is_quantity(value):
        try:
            q = puw.convert(value, to_form="pint")
        except Exception:
            raise SchemaError(
                f"{field_path} takes a quantity, not {value!r}."
            ) from None
        if isinstance(value, str):
            asserted, text = value, value
        else:
            stated_value, stated_unit = puw.get_value_and_unit(q)
            asserted = {"value": float(stated_value), "unit": str(stated_unit)}
            text = repr(float(stated_value))
    else:
        raise SchemaError(
            f"{field_path} is a quantity in {unit}: give its unit, not a bare number."
        )
    try:
        number = converted(float(puw.convert(q, to_unit=unit, to_type="value")))
        factor = float(
            puw.convert(
                puw.quantity(1.0, str(puw.get_unit(q)), form="pint"),
                to_unit=unit,
                to_type="value",
            )
        )
    except Exception:
        raise SchemaError(f"{field_path} must be convertible to {unit}.") from None
    decimals = _decimals(text)
    power = math.log10(factor) if factor > 0 else float("nan")
    if decimals is not None and abs(power - round(power)) < 1e-9:
        decimals -= round(power)
    else:
        decimals = None  # not a decimal scale change: compare exactly
    return asserted, number, decimals


def _field_assertions(card: Any, field_path: str) -> List[Dict]:
    """Every assertion about the field. A card's field assertions are all about its
    entity, whatever record they came from (a small molecule's ChEMBL and PubChem
    records): the aggregator admits no other."""
    return [
        a
        for a in card.source_assertion_store.to_list()
        if a.get("field_path") == field_path
    ]


def _replace(records: List[Dict], field_path: str, new: Dict | None) -> List[Dict]:
    kept = [r for r in records if r.get("field") != field_path]
    return kept + ([new] if new else [])


def add_literature_assertion(
    card: Any,
    field_path: str,
    value: Any,
    publication: str,
    curator: str,
    locator: str | None = None,
    quote: str | None = None,
    method: str | None = None,
    eco_code: str | None = None,
    curated_at: str | None = None,
) -> Dict[str, Any]:
    """Record what ``publication`` states about ``field_path``; see the module docstring.

    Returns the curation record also appended to ``card.quality["curation"]``:
    ``{"field", "publication", "source_assertion_id", "outcome", "compared_with"}`` where
    ``outcome`` is ``new``, ``corroborates``, ``differs``, ``not_comparable`` or
    ``not_compared``.
    """
    if field_path not in CURATABLE_FIELDS:
        raise SchemaError(f"{field_path} cannot take curated literature assertions.")
    subject = _subject(card)
    curated_at = curated_at or datetime.now(timezone.utc).date().isoformat()

    decimals = None
    if field_path in SCALAR_FIELDS:
        asserted, normalized, decimals = _scalar(field_path, value)
    else:
        asserted = normalized = _item(field_path, value, subject)

    assertion = _literature_assertion(
        field_path,
        asserted,
        publication,
        subject,
        curator,
        locator,
        quote,
        eco_code,
        curated_at,
        method=method,
        decimals=decimals,
    )
    if normalized != asserted:
        assertion["normalized_value"] = normalized
    if card.source_assertion_store.get(assertion["id"]) is not None:
        previous = next(
            (
                r
                for r in card.quality.get("curation", [])
                if r["source_assertion_id"] == assertion["id"]
            ),
            None,
        )
        # The same statement, already recorded.
        return previous or {
            "field": field_path,
            "publication": publication,
            "source_assertion_id": assertion["id"],
            "outcome": "already_recorded",
            "compared_with": [],
        }
    others = _field_assertions(card, field_path)
    card.source_assertion_store.add(assertion)

    if field_path in SCALAR_FIELDS:
        record = _resolve_scalar(card, field_path, assertion, others)
    else:
        record = _add_item(card, field_path, assertion, others)
    record = {
        "field": field_path,
        "publication": publication,
        "source_assertion_id": assertion["id"],
        **record,
    }
    card.quality.setdefault("curation", []).append(record)
    return record


def _resolve_scalar(card, field_path, assertion, others) -> Dict[str, Any]:
    from sabueso.resolver import load_selection_rules, resolve_field

    rules = card.selection_rules or load_selection_rules()
    result = resolve_field(field_path, others + [assertion], rules)
    card.set(
        field_path,
        result.get("selected_value"),
        result.get("source_assertion_ids", []),
    )
    conflict, alternatives = result.get("conflict"), result.get("alternatives")
    card.quality["conflicts"] = _replace(
        card.quality.get("conflicts", []),
        field_path,
        {"field": field_path, **conflict} if conflict else None,
    )
    card.quality["alternatives"] = _replace(
        card.quality.get("alternatives", []),
        field_path,
        {"field": field_path, **alternatives} if alternatives else None,
    )
    for key in ("conflicts", "alternatives"):
        if not card.quality[key]:
            del card.quality[key]
    compared = [a["id"] for a in others]
    by_id = {a["id"]: a for a in others}
    # The assertions stating the curated value: its conflict group, or the selected
    # support when there is no conflict.
    groups = (conflict or {}).get("source_assertion_ids") or []
    mine = next((g for g in groups if assertion["id"] in g), None)
    if mine is None and assertion["id"] in result.get("source_assertion_ids", []):
        mine = result["source_assertion_ids"]
    agreeing = [i for i in mine or [] if i != assertion["id"] and i in by_id]
    if not others:
        outcome = "new"
    elif any(_is_database(by_id[i]) for i in agreeing):
        outcome = "corroborates"  # another source states the same value
    elif mine is not None and conflict:
        outcome = "differs"
    elif agreeing:
        outcome = "corroborates"  # only other curated assertions agree
    elif alternatives:
        outcome = "not_comparable"  # e.g. another or an unstated method
    else:
        outcome = "differs"
    return {"outcome": outcome, "compared_with": compared}


def _is_database(assertion: Dict[str, Any]) -> bool:
    return (assertion.get("source") or {}).get("type") != "literature"


#: Keys a source adds to its items to describe them, not to state them: an item that
#: differs from another only in these is the same item (UniProt's synonym ``kind``).
DESCRIPTOR_KEYS = {"names.synonyms": ("kind",)}


def _stated(field_path: str, item: Any) -> str:
    drop = DESCRIPTOR_KEYS.get(field_path, ())
    if isinstance(item, dict) and drop:
        item = {k: v for k, v in item.items() if k not in drop}
    return _key(item)


def _add_item(card, field_path, assertion, others) -> Dict[str, Any]:
    item = assertion_value(assertion)
    node = card.get(field_path) or {"value": [], "source_assertion_ids": []}
    items = list(node.get("value") or [])
    if _stated(field_path, item) not in {_stated(field_path, i) for i in items}:
        items.append(item)
    card.set(
        field_path,
        items,
        list(node.get("source_assertion_ids") or []) + [assertion["id"]],
    )
    identity = ITEM_IDENTITY[field_path]
    if identity is None:
        return {"outcome": "not_compared", "compared_with": []}
    same = [a for a in others if identity(assertion_value(a)) == identity(item)]
    if not same:
        return {"outcome": "new", "compared_with": []}
    compared = [a["id"] for a in same]
    if any(
        _stated(field_path, assertion_value(a)) == _stated(field_path, item)
        for a in same
    ):
        return {"outcome": "corroborates", "compared_with": compared}
    card.quality.setdefault("conflicts", []).append(
        {
            "field": field_path,
            "type": "curated_difference",
            "values": [assertion_value(a) for a in same] + [item],
            "source_assertion_ids": [[a["id"]] for a in same] + [[assertion["id"]]],
        }
    )
    return {"outcome": "differs", "compared_with": compared}


#: Scheme of curated SourceAssertion ids. Scheme 1 (releases up to 0.2.0) left the
#: subject out; curation stores re-identify such records (``CurationStore``).
CURATED_ID_SCHEME = 2


def curated_id(
    publication: str, field_path: str, asserted: Any, locator: Any, subject: str
) -> str:
    return generate_source_assertion_id(
        LITERATURE,
        publication,
        field_path,
        {"value": asserted, "locator": locator, "subject": subject},
    )


def legacy_curated_id(assertion: Dict[str, Any]) -> str:
    """The scheme-1 id of a curated assertion (without its subject)."""
    return generate_source_assertion_id(
        LITERATURE,
        assertion["source"]["record_id"],
        assertion["field_path"],
        {
            "value": assertion["asserted_value"],
            "locator": (
                (assertion.get("source_metadata") or {}).get("curation") or {}
            ).get("locator"),
        },
    )


def _literature_assertion(
    field_path,
    asserted,
    publication,
    subject,
    curator,
    locator,
    quote,
    eco_code,
    curated_at,
    method=None,
    decimals=None,
):
    assertion = make_source_assertion(
        field_path,
        asserted,
        LITERATURE,
        publication,
        curated_at,
        source_type="literature",
        subject_ref=subject,
        acquisition={"method": "curation"},
    )
    # Two statements of the same value in two places of a paper are two assertions, and
    # so are the same statement about two entities (#55: without the subject, a review
    # stating "homodimer" of two proteins gave one id, and the store kept one of them).
    assertion["id"] = curated_id(publication, field_path, asserted, locator, subject)
    curation = {"curator": curator, "curated_at": curated_at, "locator": locator}
    if quote:
        curation["quote"] = quote
    metadata: Dict[str, Any] = {"curation": curation}
    if method:
        metadata["method"] = method
    if decimals is not None:
        metadata["stated_decimals"] = decimals  # in the field's unit
    if eco_code:
        metadata["eco"] = [{"code": eco_code, "source": "Literature"}]
    assertion["source_metadata"] = metadata
    return assertion


def add_literature_relationship(
    card: Any,
    predicate: str,
    object_ref: str,
    qualifiers: Dict[str, Any] | None,
    publication: str,
    curator: str,
    locator: str | None = None,
    quote: str | None = None,
    eco_code: str | None = None,
    curated_at: str | None = None,
) -> Dict[str, Any]:
    """Record a relationship a publication states (``CURATABLE_PREDICATES``).

    The relationship merges with the same relationship stated by other sources (same
    subject, predicate and object). Qualifiers the curated assertion states differently
    become ``qualifier_conflicts`` on the relationship, and the outcome is ``differs``;
    nothing is overridden. Outcomes and records as in ``add_literature_assertion``.
    """
    from .relationship_store import make_relationship

    if predicate not in CURATABLE_PREDICATES:
        raise SchemaError(f"{predicate} cannot take curated literature assertions.")
    subject = _subject(card)
    curated_at = curated_at or datetime.now(timezone.utc).date().isoformat()
    qualifiers = dict(qualifiers or {})
    field_path = f"relationships.{predicate}"
    assertion = _literature_assertion(
        field_path,
        {"object_ref": object_ref, "qualifiers": qualifiers},
        publication,
        subject,
        curator,
        locator,
        quote,
        eco_code,
        curated_at,
    )
    base = {
        "field": field_path,
        "publication": publication,
        "source_assertion_id": assertion["id"],
    }
    if card.source_assertion_store.get(assertion["id"]) is not None:
        previous = next(
            (
                r
                for r in card.quality.get("curation", [])
                if r["source_assertion_id"] == assertion["id"]
            ),
            None,
        )
        return previous or {**base, "outcome": "already_recorded", "compared_with": []}

    relationship = make_relationship(
        subject,
        predicate,
        object_ref,
        qualifiers,
        source_assertion_ids=[assertion["id"]],
    )
    existing = card.relationship_store.get(relationship["id"])
    before = json.loads(_key((existing or {}).get("qualifier_conflicts") or {}))
    compared = list((existing or {}).get("source_assertion_ids") or [])
    card.source_assertion_store.add(assertion)
    card.relationship_store.add(relationship)
    stored = card.relationship_store.get(relationship["id"])
    after = stored.get("qualifier_conflicts") or {}
    differing = {
        k: v for k, v in after.items() if k in qualifiers and v != before.get(k)
    }
    if existing is None:
        outcome = "new"
    elif differing:
        outcome = "differs"
        card.quality.setdefault("conflicts", []).append(
            {
                "field": field_path,
                "type": "curated_difference",
                "relationship_id": relationship["id"],
                "qualifiers": differing,
                "source_assertion_ids": [compared, [assertion["id"]]],
            }
        )
    else:
        outcome = "corroborates"
    record = {
        **base,
        "relationship_id": relationship["id"],
        "outcome": outcome,
        "compared_with": compared,
    }
    card.quality.setdefault("curation", []).append(record)
    return record


# --- Curated bioactivity measurements (uibcdf/sabueso#44) ------------------------------

RELATIONS = ("=", "<", "<=", ">", ">=", "~")
#: How a publication states an uncertainty (#37). ``sd``, ``sem`` and ``unspecified``
#: (a bare "±") give a half-width; ``ci`` gives the interval's ends and its level.
HALF_WIDTH_KINDS = ("sd", "sem", "unspecified")
UNCERTAINTY_KINDS = (*HALF_WIDTH_KINDS, "ci")
TARGET_ASSIGNMENTS = {"direct": "D", "homology": "H"}
_NUMBER_AND_UNIT = re.compile(r"\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*(.*?)\s*$")


def molecule_identity(molecule: Any) -> Dict[str, Any]:
    """``{"inchikey", "records", "as_given"}`` of a molecule: the standard InChIKey it is anchored at
    and every record linked to it (ChEMBL, PubChem, PDB component, ChEBI...).

    ``molecule`` is a small-molecule Card, an identity already recorded, or an
    identifier (``chembl:``, ``pubchem:``, ``pdb.ligand:``, ``inchikey:``) that Sabueso
    resolves online.
    """
    if isinstance(molecule, dict):
        if not molecule.get("inchikey") or not isinstance(
            molecule.get("records"), list
        ):
            raise SchemaError("A molecule identity needs 'inchikey' and 'records'.")
        return {
            "inchikey": molecule["inchikey"],
            "records": sorted(molecule["records"]),
            "as_given": molecule.get("as_given"),
        }
    card = molecule
    as_given = None
    if isinstance(molecule, str):
        as_given = molecule
        from sabueso.tools.card.small_molecule import resolve_molecule_card

        card, resolution = resolve_molecule_card(molecule)
        if card is None:
            raise SchemaError(
                f"Molecule {molecule!r} did not resolve ({resolution.status})."
            )
    node = card.get("identifiers.inchikey") or {}
    if card.meta.get("entity_type") != "small_molecule" or not node.get("value"):
        raise SchemaError("Expected the card of a small molecule, with its InChIKey.")
    records = sorted({r["subject_ref"] for r in card.relationships("same_as")})
    return {"inchikey": node["value"], "records": records, "as_given": as_given}


def _measured(value: Any) -> Tuple[Dict[str, Any], Dict[str, Any], int | None]:
    """``(as written, normalized node, stated decimals in the normalized unit)`` for a
    potency (a concentration, normalized to nanomolar) or a percentage."""
    import pyunitwizard as puw

    from .quantities import CONCENTRATION_UNIT, quantity_node

    if isinstance(value, str):
        match = _NUMBER_AND_UNIT.fullmatch(value)
        if not match or not match.group(2):
            raise SchemaError(f"A measured value needs its unit: {value!r}.")
        # The number is kept as written, so its stated precision survives re-application.
        number, unit = match.group(1), match.group(2)
        written = {"value": number, "unit": unit}
        text = number
    elif (
        isinstance(value, dict)
        and isinstance(value.get("unit"), str)
        and isinstance(value.get("value"), (str, int, float))
        and not isinstance(value.get("value"), bool)
    ):
        written = {"value": value["value"], "unit": value["unit"]}
        raw = value["value"]
        text = raw if isinstance(raw, str) else repr(raw)
    elif puw.is_quantity(value):
        v, u = puw.get_value_and_unit(value)
        written, text = {"value": float(v), "unit": str(u)}, repr(float(v))
    else:
        raise SchemaError(f"A measured value needs its unit, not {value!r}.")
    unit = "percent" if written["unit"].strip() in ("%", "percent") else written["unit"]
    try:
        q = puw.quantity(float(written["value"]), unit, form="pint")
    except Exception:
        raise SchemaError(f"Unknown unit {written['unit']!r}.") from None
    for target in (CONCENTRATION_UNIT, "percent"):
        try:
            number = converted(float(puw.convert(q, to_unit=target, to_type="value")))
            factor = float(
                puw.convert(
                    puw.quantity(1.0, unit, form="pint"),
                    to_unit=target,
                    to_type="value",
                )
            )
        except Exception:
            continue
        decimals = _decimals(text)
        power = math.log10(factor) if factor > 0 else float("nan")
        decimals = (
            decimals - round(power)
            if decimals is not None and abs(power - round(power)) < 1e-9
            else None
        )
        return written, quantity_node(number, target), decimals
    raise SchemaError(
        f"{written['unit']!r} is neither a concentration nor a percentage."
    )


def _unit_of(written: Dict[str, Any]) -> str:
    unit = written["unit"].strip()
    return canonical_unit("percent" if unit in ("%", "percent") else unit)


def _written_only(written: Dict[str, Any]) -> Dict[str, Any]:
    return {"value": written["value"], "unit": written["unit"]}


def _uncertainty(
    uncertainty: Dict[str, Any], normalized: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """``(as written, normalized)`` of a stated uncertainty, checked against the value.

    The normalized parts are quantity nodes in the measurement's normalized unit.
    """
    if not isinstance(uncertainty, dict):
        raise SchemaError(
            "An uncertainty is a dict such as {'kind': 'sd', 'value': '3 nM'} or "
            "{'kind': 'ci', 'lower': '8 nM', 'upper': '18 nM', 'level': 0.95}."
        )
    kind = uncertainty.get("kind")
    if kind not in UNCERTAINTY_KINDS:
        raise SchemaError(
            f"Unknown uncertainty kind {kind!r}; expected one of {list(UNCERTAINTY_KINDS)}."
        )
    parts = ("value",) if kind in HALF_WIDTH_KINDS else ("lower", "upper")
    allowed = {"kind", *parts, "n", *(("level",) if kind == "ci" else ())}
    unknown = sorted(set(uncertainty) - allowed)
    if unknown or any(uncertainty.get(part) is None for part in parts):
        raise SchemaError(
            f"A {kind} uncertainty takes {sorted(allowed)}; got {sorted(uncertainty)}."
        )
    written: Dict[str, Any] = {"kind": kind}
    stored: Dict[str, Any] = {"kind": kind}
    for part in parts:
        as_written, node, _ = _measured(uncertainty[part])
        if node["unit"] != normalized["unit"]:
            raise SchemaError(
                f"The uncertainty ({as_written['unit']}) and the value "
                f"({normalized['unit']}) are not the same kind of quantity."
            )
        written[part] = _written_only(as_written)
        stored["half_width" if part == "value" else part] = node
    if kind in HALF_WIDTH_KINDS and stored["half_width"]["value"] < 0:
        raise SchemaError("An uncertainty's half-width cannot be negative.")
    if kind == "ci":
        low, high = stored["lower"]["value"], stored["upper"]["value"]
        if not low <= normalized["value"] <= high:
            raise SchemaError(
                "A confidence interval must contain the value it is stated for."
            )
        level = uncertainty.get("level")
        if level is not None and not (
            isinstance(level, (int, float))
            and not isinstance(level, bool)
            and 0 < level < 1
        ):
            raise SchemaError(
                f"A confidence level is a fraction, e.g. 0.95, not {level!r}."
            )
        if level is not None:
            written["level"] = stored["level"] = level
    n = uncertainty.get("n")
    if n is not None:
        if not isinstance(n, int) or isinstance(n, bool) or n < 1:
            raise SchemaError(f"n is a number of replicates, not {n!r}.")
        written["n"] = stored["n"] = n
    return written, stored


def _agrees(a: float, b: float, decimals: int | None) -> bool:
    if decimals is None:
        return math.isclose(a, b, rel_tol=1e-9)
    return abs(a - b) <= 0.5 * 10.0**-decimals + 1e-9


def _same_measurement(
    rel: Dict[str, Any],
    relation: str,
    normalized: Dict[str, Any],
    decimals: int | None,
    upper: Tuple[Dict[str, Any], Dict[str, Any], int | None] | None,
) -> bool:
    """Whether a ChEMBL measurement states what the curator read, at its precision.

    A point and a range never agree: ChEMBL recording one end of a range reported in
    the paper, or a range where the paper gives a value, is a difference (#37). A stated
    uncertainty plays no part: both are readings of the same publication, and agreement
    is about the number reported, not about the spread of the measurement.
    """
    from .bioactivities import is_range, upper_node

    m = rel["qualifiers"]["measurement"]
    node = m.get("normalized") or {}
    if (m.get("relation") or "=") != relation or node.get("unit") != normalized["unit"]:
        return False
    if not _agrees(float(node["value"]), float(normalized["value"]), decimals):
        return False
    if is_range(m) != (upper is not None):
        return False
    if upper is None:
        return True
    theirs = upper_node(m) or {}
    return theirs.get("unit") == upper[1]["unit"] and _agrees(
        float(theirs["value"]), float(upper[1]["value"]), upper[2]
    )


def add_literature_bioactivity(
    card: Any,
    molecule: Any,
    measurement_type: str,
    value: Any,
    publication: str,
    curator: str,
    target_assignment: str,
    relation: str = "=",
    assay_description: str | None = None,
    locator: str | None = None,
    quote: str | None = None,
    eco_code: str | None = None,
    curated_at: str | None = None,
    upper_value: Any = None,
    uncertainty: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Record a bioactivity a publication reports, and compare it with ChEMBL.

    ``upper_value`` makes the measurement a range, from ``value`` to ``upper_value``,
    written in the same unit. ``uncertainty`` is what the paper states around the value
    (see ``UNCERTAINTY_KINDS``). Both are part of the statement, and so of its id (#37).

    The measurement becomes a ``has_bioactivity`` relationship of its own (its
    ``activity_id`` is ``curated:<digest>``), carrying the molecule's identity. It is
    compared with the ChEMBL measurements of the same publication (by PubMed id or DOI),
    the same molecule (any of its records) and the same type: a value agreeing at the
    precision it was stated with corroborates; none agreeing differs; none to compare
    with is new. Nothing is overridden.
    """
    from .relationship_store import make_relationship

    subject = _subject(card)
    curated_at = curated_at or datetime.now(timezone.utc).date().isoformat()
    identity = molecule_identity(molecule)
    written, normalized, decimals = _measured(value)
    upper = None
    if upper_value is not None:
        if relation not in ("=", "~"):
            raise SchemaError(
                f"A range states both of its ends; relation {relation!r} does not apply."
            )
        upper = _measured(upper_value)
        written_upper, normalized_upper, _ = upper
        if _unit_of(written_upper) != _unit_of(written):
            raise SchemaError(
                "Both ends of a range are written in the same unit "
                f"({written['unit']} and {written_upper['unit']})."
            )
        if normalized_upper["value"] < normalized["value"]:
            raise SchemaError("A range's upper end cannot be below its lower end.")
    written_uncertainty = stored_uncertainty = None
    if uncertainty is not None:
        written_uncertainty, stored_uncertainty = _uncertainty(uncertainty, normalized)
    # What the curator states: the molecule as given and its InChIKey. The records
    # UniChem links belong to the card's glossary, not to the statement (#52).
    asserted = {
        "molecule": {
            "inchikey": identity["inchikey"],
            "as_given": identity["as_given"],
        },
        "measurement": {
            "type": measurement_type,
            "relation": relation,
            **written,
            **({"upper": _written_only(upper[0])} if upper else {}),
            **({"uncertainty": written_uncertainty} if written_uncertainty else {}),
        },
        "target_assignment": target_assignment,
        "assay_description": assay_description,
    }
    field_path = "relationships.has_bioactivity"
    assertion = _literature_assertion(
        field_path,
        asserted,
        publication,
        subject,
        curator,
        locator,
        quote,
        eco_code,
        curated_at,
        decimals=decimals,
    )
    base = {
        "field": field_path,
        "publication": publication,
        "source_assertion_id": assertion["id"],
    }
    if card.source_assertion_store.get(assertion["id"]) is not None:
        previous = next(
            (
                r
                for r in card.quality.get("curation", [])
                if r["source_assertion_id"] == assertion["id"]
            ),
            None,
        )
        return previous or {**base, "outcome": "already_recorded", "compared_with": []}

    records = identity["records"]
    shown = next(
        (
            r
            for namespace in ("chembl:", "pdb.ligand:", "pubchem:")
            for r in records
            if r.startswith(namespace)
        ),
        f"inchikey:{identity['inchikey']}",
    )
    kind, _, number = publication.partition(":")
    document = {
        "id": None,
        "year": None,
        "journal": None,
        "pubmed": number if kind == "pubmed" else None,
        "doi": number if kind == "doi" else None,
        "title": None,
    }
    relationship = make_relationship(
        subject,
        "has_bioactivity",
        shown,
        qualifiers={
            "activity_id": "curated:" + assertion["id"].rsplit("_", 1)[-1],
            "parent_molecule": shown,
            "molecule_ref": f"inchikey:{identity['inchikey']}",
            "measurement": {
                "type": measurement_type,
                "relation": relation,
                "value": float(written["value"]),
                "units": written["unit"],
                "normalized": normalized,
                **(
                    {
                        "upper_value": float(upper[0]["value"]),
                        "normalized_upper": upper[1],
                    }
                    if upper
                    else {}
                ),
                **(
                    {"normalized_uncertainty": stored_uncertainty}
                    if stored_uncertainty
                    else {}
                ),
                "pchembl": None,
                "curated": True,
            },
            "assay": {
                "id": None,
                "description": assay_description,
                "relationship_type": TARGET_ASSIGNMENTS[target_assignment],
                "organism": None,
                "curated": True,
            },
            "document": document,
        },
        source_assertion_ids=[assertion["id"]],
    )

    same = []
    for rel in card.relationships("has_bioactivity"):
        q = rel.get("qualifiers", {})
        if (q.get("assay") or {}).get("curated"):
            continue
        doc = q.get("document") or {}
        if not (
            (document["pubmed"] and doc.get("pubmed") == document["pubmed"])
            or (
                document["doi"]
                and (doc.get("doi") or "").lower() == document["doi"].lower()
            )
        ):
            continue
        refs = {rel["object_ref"], q.get("parent_molecule")}
        if (
            not refs & set(records)
            or (q.get("measurement") or {}).get("type") != measurement_type
        ):
            continue
        same.append(rel)
    agreeing = [
        rel
        for rel in same
        if _same_measurement(rel, relation, normalized, decimals, upper)
    ]
    card.source_assertion_store.add(assertion)
    card.relationship_store.add(relationship)
    card.register_identity(
        f"inchikey:{identity['inchikey']}",
        records,
        "small_molecule",
        {"by": "curation", "at": curated_at},
    )
    compared = [r["id"] for r in same]
    if not same:
        outcome = "new"
    elif agreeing:
        outcome = "corroborates"
    else:
        outcome = "differs"
        card.quality.setdefault("conflicts", []).append(
            {
                "field": field_path,
                "type": "curated_difference",
                "relationship_id": relationship["id"],
                "values": [r["qualifiers"]["measurement"]["normalized"] for r in same]
                + [normalized],
                "relationship_ids": [compared, [relationship["id"]]],
            }
        )
    record = {
        **base,
        "relationship_id": relationship["id"],
        "outcome": outcome,
        "compared_with": compared,
    }
    card.quality.setdefault("curation", []).append(record)
    return record


#: How a publication says a compound acts on the residues it names (#61).
MECHANISMS = (
    "covalent",
    "non_covalent",
    "allosteric",
    "interface_disruption",
    "unspecified",
)
_THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}  # fmt: skip


def _engaged_residues(card: Any, residues: Any) -> List[Dict[str, Any]]:
    """``[{position, residue}]`` checked against the card's sequence.

    A residue may be given as a position, or as ``{"position", "residue"}`` with a one-
    or three-letter code, which must match the card's sequence at that position.
    """
    sequence = (card.get("sequence.primary") or {}).get("value") or ""
    if not isinstance(residues, (list, tuple)) or not residues:
        raise SchemaError("An engagement names at least one residue.")
    out: Dict[int, Dict[str, Any]] = {}
    for given in residues:
        if isinstance(given, int) and not isinstance(given, bool):
            position, stated = given, None
        elif isinstance(given, dict) and isinstance(given.get("position"), int):
            position, stated = given["position"], given.get("residue")
        else:
            raise SchemaError(
                f"A residue is a position or {{'position', 'residue'}}, not {given!r}."
            )
        if position < 1 or (sequence and position > len(sequence)):
            raise SchemaError(
                f"Position {position} is outside the sequence ({len(sequence)} residues)."
            )
        actual = sequence[position - 1] if sequence else None
        if stated is not None:
            code = str(stated).strip().upper()
            code = _THREE_TO_ONE.get(code, code)
            if actual is not None and code != actual:
                raise SchemaError(
                    f"The paper's residue {stated} at {position} is {actual} in this "
                    "entry's sequence: check the numbering (UniProt, 1-based)."
                )
        out[position] = {"position": position, "residue": actual or stated}
    return [out[p] for p in sorted(out)]


def add_literature_engagement(
    card: Any,
    molecule: Any,
    residues: Any,
    mechanism: str,
    publication: str,
    curator: str,
    covalent_residue: int | None = None,
    method: str | None = None,
    locator: str | None = None,
    quote: str | None = None,
    eco_code: str | None = None,
    curated_at: str | None = None,
) -> Dict[str, Any]:
    """Record the residues a publication says a compound acts on, and how (#61).

    The engagement is an ``engages`` relationship anchored by the molecule's InChIKey.
    It is compared with the ligand sites observed in structures (PDBe-KB
    ``has_ligand_site``) of the same molecule: shared residues corroborate; different
    residues do not contradict by themselves (a site can differ between states or
    constructs) and are ``not_comparable``; no observed site is ``new``.
    """
    from .relationship_store import make_relationship

    if mechanism not in MECHANISMS:
        raise SchemaError(
            f"Unknown mechanism {mechanism!r}; expected one of {list(MECHANISMS)}."
        )
    subject = _subject(card)
    curated_at = curated_at or datetime.now(timezone.utc).date().isoformat()
    engaged = _engaged_residues(card, residues)
    positions = [r["position"] for r in engaged]
    if mechanism == "covalent":
        if covalent_residue not in positions:
            raise SchemaError(
                "A covalent engagement names its modified residue (covalent_residue), "
                "among the residues."
            )
    elif covalent_residue is not None:
        raise SchemaError("covalent_residue applies to covalent engagements only.")
    identity = molecule_identity(molecule)
    asserted: Dict[str, Any] = {
        "molecule": {
            "inchikey": identity["inchikey"],
            "as_given": identity["as_given"],
        },
        "residues": positions,
        "mechanism": mechanism,
    }
    if covalent_residue is not None:
        asserted["covalent_residue"] = covalent_residue
    if method:
        asserted["method"] = method
    field_path = "relationships.engages"
    assertion = _literature_assertion(
        field_path,
        asserted,
        publication,
        subject,
        curator,
        locator,
        quote,
        eco_code,
        curated_at,
    )
    base = {
        "field": field_path,
        "publication": publication,
        "source_assertion_id": assertion["id"],
    }
    if card.source_assertion_store.get(assertion["id"]) is not None:
        previous = next(
            (
                r
                for r in card.quality.get("curation", [])
                if r["source_assertion_id"] == assertion["id"]
            ),
            None,
        )
        return previous or {**base, "outcome": "already_recorded", "compared_with": []}

    records = identity["records"]
    shown = next(
        (
            r
            for namespace in ("pdb.ligand:", "chembl:", "pubchem:")
            for r in records
            if r.startswith(namespace)
        ),
        f"inchikey:{identity['inchikey']}",
    )
    observed = [
        rel
        for rel in card.relationships("has_ligand_site")
        if rel["object_ref"] in set(records)
        and not (rel.get("qualifiers") or {}).get("curated")
    ]
    seen = {
        p
        for rel in observed
        for r in (rel.get("qualifiers") or {}).get("residues") or []
        for p in range(r.get("start") or 0, (r.get("end") or r.get("start") or 0) + 1)
        if p
    }
    shared = sorted(seen & set(positions))
    if not observed:
        outcome = "new"
    elif shared:
        outcome = "corroborates"
    else:
        outcome = "not_comparable"

    relationship = make_relationship(
        subject,
        "engages",
        shown,
        qualifiers={
            "statement_id": "curated:" + assertion["id"].rsplit("_", 1)[-1],
            "molecule_ref": f"inchikey:{identity['inchikey']}",
            "residues": engaged,
            "mechanism": mechanism,
            "covalent_residue": covalent_residue,
            "method": method,
            "publication": publication,
            "curated": True,
        },
        source_assertion_ids=[assertion["id"]],
    )
    card.source_assertion_store.add(assertion)
    card.relationship_store.add(relationship)
    card.register_identity(
        f"inchikey:{identity['inchikey']}",
        records,
        "small_molecule",
        {"by": "curation", "at": curated_at},
    )
    record = {
        **base,
        "relationship_id": relationship["id"],
        "outcome": outcome,
        "compared_with": [rel["id"] for rel in observed],
        "shared_positions": shared,
    }
    card.quality.setdefault("curation", []).append(record)
    return record
