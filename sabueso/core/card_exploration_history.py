"""Historical comparison records over sealed captures, never live Card readers.

Expected records are private verifier inputs. They are never returned as new
knowledge or substituted for an original saved result. The frozen v1 predicates
retain the original decisions when the ordinary readers/catalogs later evolve.
"""

from copy import deepcopy

from .errors import StorageError
from .snapshot import canonical_json


class _ExpectedRule(dict):
    """Mark verifier-created rules without altering original source records."""


class _ExpectedQuantity(dict):
    """A declared result quantity; source lookalikes remain ordinary dictionaries."""


def _rule(rule, inputs=None, parameters=None):
    return _ExpectedRule(
        rule=rule,
        inputs=inputs or [],
        parameters=parameters or {},
        sabueso_version="original producer",
    )


def _matches(actual, expected):
    if isinstance(expected, _ExpectedQuantity):
        import pyunitwizard as puw
        from pyunitwizard import QuantityRecord

        original = QuantityRecord.from_dict(expected)
        retained = QuantityRecord.from_dict(actual)
        manifest = original.to_dict()["manifest"]
        field, unit = manifest["field"], manifest["unit"]
        first = retained.to_quantity(field=field, unit=unit)
        second = original.to_quantity(field=field, unit=unit)
        a = puw.get_value(first, to_unit=unit)
        b = puw.get_value(second, to_unit=unit)
        return retained.kind == original.kind and bool(
            (a == b).all() if hasattr(a, "all") else a == b
        )
    if isinstance(expected, _ExpectedRule):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            return False
        if not isinstance(actual.get("sabueso_version"), str):
            return False
        actual = {k: v for k, v in actual.items() if k != "sabueso_version"}
        expected = {k: v for k, v in expected.items() if k != "sabueso_version"}
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and set(actual) == set(expected)
            and all(_matches(actual[k], v) for k, v in expected.items())
        )
    if isinstance(expected, (list, tuple)):
        return (
            isinstance(actual, (list, tuple))
            and len(actual) == len(expected)
            and all(_matches(a, b) for a, b in zip(actual, expected))
        )
    return canonical_json(actual) == canonical_json(expected)


def _require_matches(actual, expected, scope):
    if not _matches(actual, expected):
        raise StorageError(f"Saved {scope} differs from its historical input binding.")


class _Records:
    def __init__(self, rows):
        self._rows = rows
        self._index = {row["id"]: row for row in rows}

    def get(self, key):
        return self._index.get(key)

    def to_list(self):
        return self._rows


class _HistoricalInput:
    """Only retained fields/records; no Card construction, stores or derivation API."""

    def __init__(self, capture):
        data = capture.data
        self.meta, self.sections, self.quality = (
            data["meta"],
            data["sections"],
            data["quality"],
        )
        self.id = self.meta.get("card_id")
        self._pin = capture.pin
        self.selection_rules = data.get("selection_rules", {})
        self.source_assertion_store = _Records(data["source_assertion_store"])
        self.relationship_store = _Records(data["relationship_store"])

    def pinned_ref(self):
        return self._pin

    def get(self, field_path):
        value = self.sections
        for key in field_path.split("."):
            if not isinstance(value, dict) or key not in value:
                return None
            value = value[key]
        return value

    def list_fields(self):
        result = []

        def walk(prefix, value):
            if isinstance(value, dict):
                for key, child in value.items():
                    path = f"{prefix}.{key}" if prefix else key
                    result.append(path)
                    walk(path, child)

        walk("", self.sections)
        return result

    def relationships(self, predicate=None, object_ref=None):
        return [
            row
            for row in self.relationship_store.to_list()
            if (predicate is None or row["predicate"] == predicate)
            and (object_ref is None or row["object_ref"] == object_ref)
        ]

    def explain(self, source_assertion_ids, skip_digestion=False):
        answers = {}
        for row in (self.quality.get("retrievals") or {}).get("records") or []:
            answers.setdefault(row.get("source"), []).append(row["ref"])
        result = []
        for key in source_assertion_ids:
            row = self.source_assertion_store.get(key)
            if row is None:
                result.append({"id": key, "found": False})
                continue
            source = row.get("source") or {}
            result.append(
                {
                    "id": key,
                    "found": True,
                    "field_path": row.get("field_path"),
                    "subject_ref": row.get("subject_ref"),
                    "source": source.get("name"),
                    "record": source.get("record_id"),
                    "version": source.get("version"),
                    "retrieved_at": row.get("retrieved_at"),
                    "asserted_value": row.get("asserted_value"),
                    "acquisition": dict(
                        row.get("acquisition") or {"method": "not_recorded"}
                    ),
                    **(
                        {
                            "retrievals": {
                                "basis": "source_in_build",
                                "refs": answers.get(source.get("name"), []),
                            }
                        }
                        if answers
                        else {}
                    ),
                    **(
                        {"source_metadata": row["source_metadata"]}
                        if row.get("source_metadata")
                        else {}
                    ),
                }
            )
        return deepcopy(result)
