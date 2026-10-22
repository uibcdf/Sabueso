"""Core exception types for Sabueso.

They are SMonitor catalog exceptions (uibcdf/sabueso#31): each keeps the message written
where it is raised, and gains a stable code (``exc.code``) and structured context
(``exc.extra``) from ``sabueso/_private/smonitor/catalog.py``.
"""

from __future__ import annotations

from typing import Any, Dict

from smonitor.integrations import CatalogException

from sabueso._private.smonitor.catalog import CATALOG, META


def _diagnostic_details_allowed() -> bool:
    """Honor a caller's capture restrictions before constructing error text.

    Older supported SMonitor versions have no scoped API and retain detailed
    diagnostics. This does not introduce a second capture-policy mechanism.
    """
    try:
        from smonitor import get_capture_policy
    except ImportError:
        return True
    policy = get_capture_policy()
    return policy.arguments and policy.exception_text


class SabuesoError(CatalogException):
    """Base error for Sabueso."""

    catalog_key = "SabuesoError"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        extra: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, extra=extra, catalog=CATALOG, meta=META)


class ResolverError(SabuesoError):
    """Resolver failed to select or normalize values."""

    catalog_key = "ResolverError"


class SchemaError(SabuesoError):
    """Schema mismatch or validation failure."""

    catalog_key = "SchemaError"


class StorageError(SabuesoError):
    """Persistence/storage failure."""

    catalog_key = "StorageError"


class ConnectorError(SabuesoError):
    """External data source or connector failure."""

    catalog_key = "ConnectorError"


class NotArchivedError(ConnectorError):
    """An answer a retrieval archive does not hold, while replaying from it (#100): the
    source was not asked, which is neither its failure nor an absence."""

    catalog_key = "ConnectorError"


class OfflineError(ConnectorError):
    """A request made while working offline (``mirrors.using(mode="offline")``, #100):
    the source was not asked, which is neither its failure nor an absence."""

    catalog_key = "ConnectorError"


class RecordNotFoundError(SabuesoError):
    """A source was consulted and holds no record for the requested identifier.

    Distinct from ConnectorError: "not found" is an answer, a connector failure is not.
    ``version`` is the source release that was consulted, when the source states one:
    "not stated by S at release R" is a fact about a source that can be checked (#89).
    """

    catalog_key = "RecordNotFoundError"

    def __init__(
        self,
        message: str | None = None,
        *,
        version: Any = None,
        code: str | None = None,
        extra: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, extra=extra)
        self.version = None if version is None else str(version)


class MissingKeyError(SabuesoError):
    """A source answers only with a personal key, and none was given (#86).

    Distinct from ConnectorError: nothing was asked, so nothing failed. An enrichment
    records it as ``not_queried``, with the reason.
    """

    catalog_key = "MissingKeyError"


class ArgumentError(SabuesoError, ValueError):
    """An argument of a public function has a value the function cannot accept.

    Raised by the ArgDigest digesters in ``sabueso/_private/argdigest/argument/``
    (uibcdf/sabueso#31), before the function runs: a wrong value is refused rather than
    turned into a plausible wrong result. It is also a ValueError, which is what it is.
    """

    catalog_key = "ArgumentError"

    def __init__(
        self,
        message: str | None = None,
        *,
        argument: str | None = None,
        value: Any = None,
        caller: str | None = None,
        reason: str | None = None,
    ) -> None:
        if message is None:
            if _diagnostic_details_allowed():
                where = f" of {caller}" if caller else ""
                why = f": {reason}" if reason else ""
                message = f"Argument {argument!r}{where} cannot take {value!r}{why}."
            else:
                message = "An argument cannot take the supplied value."
        super().__init__(message, extra={"argument": argument, "caller": caller})


class LibraryNotFoundError(SabuesoError, ImportError):
    """An optional library a function needs is not installed (DepDigest, #46).

    Raised by ``@dep_digest`` with the library, the caller and install hints; also an
    ImportError, which is what it is.
    """

    catalog_key = "LibraryNotFoundError"

    def __init__(
        self,
        message: str | None = None,
        *,
        library: str | None = None,
        caller: str | None = None,
    ) -> None:
        if message is None:
            where = f" for {caller}" if caller else ""
            message = f"The optional library {library!r} is required{where}."
        super().__init__(message, extra={"library": library, "caller": caller})
