"""Stored identifier coverage, never inferred from a source-wide count (#144)."""

from copy import deepcopy
from types import SimpleNamespace

from .disease_grouping import _sources, identity_paths
from .relationship_store import make_derivation

RULE = "disease_identity_coverage@1"
COMPLETED = {"added", "not_found"}
NEGATIVE = {"no_stated_equivalence", "obsolete_term"}


def reason(states):
    """Retain mixed scopes instead of choosing one source outcome silently."""
    states = set(states)
    return {
        frozenset({"not_queried"}): "identity_not_queried",
        frozenset({"unavailable"}): "identity_unavailable",
        frozenset({"unknown"}): "identity_scope_unknown",
        frozenset({"not_stated"}): "no_stated_equivalence",
        frozenset({"obsolete"}): "obsolete_term",
    }.get(frozenset(states), "mixed_identity_coverage")


class IdentityCoverage:
    """Positive stored paths and exact negative diagnostics have distinct bases.

    Failure/blocked request records without identifier scope describe access
    availability, not proof that this identifier was queried. Historical missing
    scope remains unknown. No acquisition trace is required or reconstructed.
    """

    def __init__(self, card):
        self.card = card
        self._steps = {}
        self._paths = {}
        self.records = list(card.quality.get("enrichments") or [])
        self.links = {r["id"]: r for r in card.relationships("same_as")}
        self.completed = SimpleNamespace(
            quality={
                "enrichments": [r for r in self.records if r.get("status") in COMPLETED]
            },
            relationships=card.relationships,
        )

    def _step(self, source, identifier):
        key = (source, identifier)
        if key in self._steps:
            return deepcopy(self._steps[key])
        indexed = [
            (i, r) for i, r in enumerate(self.records) if r.get("source") == source
        ]
        outcomes = sorted(
            {
                d["reason"]
                for _, r in indexed
                if r.get("status") in COMPLETED
                for d in r.get("ungrouped") or []
                if d.get("curie") == identifier and d.get("reason") in NEGATIVE
            }
        )
        matched = [
            i
            for i, r in indexed
            if r.get("status") in COMPLETED
            and any(
                d.get("curie") == identifier and d.get("reason") in NEGATIVE
                for d in r.get("ungrouped") or []
            )
        ]
        if source == "MedGen":
            matched = [
                i
                for i, r in indexed
                if r.get("status") in COMPLETED
                and any(
                    c in {identifier, identifier.removeprefix("MEDGEN:")}
                    for c in r.get("missing") or []
                )
            ]
            outcomes = ["no_stated_uid"] if matched else []
        statuses = {r.get("status") for _, r in indexed}
        if outcomes:
            state = (
                "mixed"
                if len(outcomes) > 1
                else "obsolete"
                if outcomes == ["obsolete_term"]
                else "not_stated"
            )
        elif not indexed or statuses <= {"not_queried", "not_applicable"}:
            state = "not_queried"
        elif statuses & {"error", "unavailable"}:
            state = "unavailable"
        else:
            state = "unknown"
        result = {
            "source": source,
            "identifier": identifier,
            "state": state,
            "scope": "identifier_diagnostic" if outcomes else "not_recorded",
            "outcomes": outcomes,
            "enrichment_indexes": matched if outcomes else [i for i, _ in indexed],
            "recorded_request_states": sorted(s for s in statuses if s is not None),
        }

        self._steps[key] = result
        return deepcopy(result)

    def paths(self, identifier):
        if identifier in self._paths:
            return deepcopy(self._paths[identifier])
        paths = identity_paths(self.completed, identifier)
        for path in paths:
            if path["term"] is None:
                target = self.links[path["relationship_ids"][-1]]["object_ref"]
                path["reason"] = reason([self._step("MONDO", target)["state"]])
        self._paths[identifier] = paths
        return deepcopy(paths)

    def _stored_step(self, source, identifier, links):
        step = self._step(source, identifier)
        return {
            **step,
            "state": "identity_stated",
            "scope": "stored_identity_path",
            "relationship_ids": sorted(links),
        }

    def row(self, identifier):
        paths = self.paths(identifier)
        positive = [p for p in paths if p["term"]]
        steps = []
        if identifier.startswith("MEDGEN:C"):
            direct_links = sorted(
                {
                    i
                    for p in positive
                    if p["basis"] == "same_as"
                    for i in p["relationship_ids"]
                }
            )
            uid_links = [
                r
                for r in self.links.values()
                if r["subject_ref"] == identifier and "MedGen" in _sources(r)
            ]
            if not uid_links and direct_links:
                steps = [self._stored_step("MONDO", identifier, direct_links)]
                state = "identity_stated"
            elif not uid_links:
                upstream = self._step("MedGen", identifier)
                steps = [
                    upstream,
                    {
                        "source": "MONDO",
                        "identifier": None,
                        "state": "not_queried",
                        "scope": "missing_prerequisite",
                        "detail": "No stored MedGen UID names this concept",
                        "enrichment_indexes": [],
                        "outcomes": [],
                        "recorded_request_states": [],
                    },
                ]
                state = (
                    "unavailable"
                    if upstream["state"] == "unavailable"
                    else "unknown"
                    if upstream["state"] == "unknown"
                    else "not_queried"
                )
            else:
                steps.append(
                    self._stored_step(
                        "MedGen", identifier, [r["id"] for r in uid_links]
                    )
                )
                for link in sorted(uid_links, key=lambda r: r["id"]):
                    uid = link["object_ref"]
                    targets = [
                        r["id"]
                        for r in self.links.values()
                        if r["subject_ref"] == uid and "MONDO" in _sources(r)
                    ]
                    steps.append(
                        self._stored_step("MONDO", uid, targets)
                        if targets
                        else self._step("MONDO", uid)
                    )
                if direct_links:
                    steps.append(self._stored_step("MONDO", identifier, direct_links))
                states = {s["state"] for s in steps[1:]}
                state = next(iter(states)) if len(states) == 1 else "mixed"
        elif positive:
            identifiers = sorted({i for p in positive for i in p["relationship_ids"]})
            step = self._stored_step("MONDO", identifier, identifiers)
            if not identifiers:
                step["scope"] = "identifier_named_by_upstream_source"
            steps, state = [step], "identity_stated"
        else:
            step = self._step("MONDO", identifier)
            steps, state = [step], step["state"]
        if len({p["term"] for p in positive}) > 1:
            state = "conflicting_identity"
        elif positive and any(p["term"] is None for p in paths):
            state = "mixed"
        return {"id": identifier, "state": state, "steps": steps}

    def statement(self, statement):
        return {
            "rule": make_derivation(
                RULE,
                inputs=[
                    "quality.enrichments",
                    "relationships.same_as",
                    "relationships.associated_with",
                    "annotations.disease",
                    "annotations.clinical_variants",
                ],
                parameters={"identifiers": sorted(set(statement["curies"]))},
            ),
            "rows": [self.row(c) for c in sorted(set(statement["curies"]))],
        }

    def reason(self, coverage):
        return reason([r["state"] for r in coverage["rows"]])

    def context(self, pin):
        return deepcopy(
            {
                "card_ref": pin,
                "quality_path": "quality.enrichments",
                "enrichments": [
                    {"index": i, "record": r}
                    for i, r in enumerate(self.records)
                    if r.get("source") in {"MONDO", "MedGen"}
                ],
                "scope": "exact stored indexes; unrecorded identifier request scope stays unknown",
            }
        )
