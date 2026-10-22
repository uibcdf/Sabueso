"""Helpers shared by digesters (kept out of the digester package on purpose)."""

from __future__ import annotations

from typing import Any

from sabueso.core.errors import ArgumentError, _diagnostic_details_allowed

#: Knowledge store queries, where a relationship filter may be left out (None) and any
#: predicate Sabueso states is accepted, not only the curatable ones.
STORE_QUERIES = frozenset({"sabueso.core.knowledge_store.relationships"})
#: Callers that follow relationships (#91): one predicate or several.
EXPANSIONS = frozenset(
    {
        "sabueso.tools.navigate.expand",
        "sabueso.core.card.expand",
        "sabueso.core.deck.expand",
    }
)


def refuse(argument: str, value: Any, caller: str | None, reason: str) -> ArgumentError:
    return ArgumentError(argument=argument, value=value, caller=caller, reason=reason)


def boolean(argument: str, value: Any, caller: str | None) -> bool:
    if isinstance(value, bool):
        return value
    raise refuse(argument, value, caller, "expected True or False")


def client(argument: str, value: Any, caller: str | None) -> Any:
    """A source client is duck-typed: any object, or None for the online default.

    Its protocol is exercised by the call itself, and a failure there is recorded as a
    source outcome. A string is refused: it is a common slip (a URL or a source name
    where a client object was meant).
    """
    if isinstance(value, (str, bytes)):
        raise refuse(argument, value, caller, "expected a client object or None")
    return value


def options(
    argument: str, value: Any, caller: str | None, allowed: dict
) -> dict | None:
    """``None`` (source off) or a dict of the options the source's client accepts.

    ``allowed`` maps each option to a check returning a reason, or None when valid.
    """
    if value is None:
        return None
    if not isinstance(value, dict):
        raise refuse(argument, value, caller, "expected a dict of options, or None")
    unknown = sorted(set(value) - set(allowed))
    if unknown:
        raise refuse(
            argument,
            value,
            caller,
            f"unknown options {unknown}; accepted: {sorted(allowed)}"
            if _diagnostic_details_allowed()
            else "unknown options",
        )
    for key, check in allowed.items():
        if key in value:
            reason = check(value[key])
            if reason:
                raise refuse(argument, value, caller, f"{key}: {reason}")
    return dict(value)


def positive_int(value: Any) -> str | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        return "expected a positive integer"
    return None


def a_deck(argument: str, value: Any, caller: str | None) -> Any:
    from sabueso.core.deck import Deck

    if isinstance(value, Deck):
        return value
    raise refuse(argument, value, caller, "expected a Deck")


def field_path(argument: str, value: str, caller: str | None) -> str:
    """A dotted field path such as ``identifiers.uniprot``: no empty segment."""
    if not value or any(not part.strip() for part in value.split(".")):
        raise refuse(argument, value, caller, "expected a dotted field path")
    return value


def path_list(argument: str, value: Any, caller: str | None) -> list:
    """One field path, or an iterable of them, as a list.

    A single path is wrapped: iterating the string would otherwise look up one "field"
    per character, each silently absent, a plausible wrong result.
    """
    if isinstance(value, str):
        value = [value]
    try:
        paths = list(value)
    except TypeError:
        raise refuse(
            argument, value, caller, "expected a field path or a list of them"
        ) from None
    for path in paths:
        if not isinstance(path, str):
            reason = (
                f"not a field path: {path!r}"
                if _diagnostic_details_allowed()
                else "not a field path"
            )
            raise refuse(argument, value, caller, reason)
        field_path(argument, path, caller)
    return paths


def optional_text(argument: str, value: Any, caller: str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise refuse(argument, value, caller, "expected a non-empty text or None")
