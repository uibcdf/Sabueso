"""The one way source clients reach the network (#82, #83, #86).

- **A named client.** Some servers refuse Python's default user agent (DISEASES's
  downloads, Reactome's Content Service answer 403). Every request carries Sabueso's
  name and version.
- **Retries for transient failures.** HTTP 429, 502, 503 and 504, and a refused or
  reset connection, are retried up to ``RETRIES`` times, waiting longer each time
  (``Retry-After`` is honoured, up to ``MAX_WAIT`` seconds). Every Sabueso request is a
  read (GraphQL posts too), so a retry changes nothing on the source.
- **What is not retried.** A timeout: the source has already had its time, and asking
  again would multiply it. Any other error reaches the client unchanged, which
  decides whether a source's 404 states absence or is a connector failure.
- **An unreadable answer** (#97). A client that reads JSON asks with
  ``expect_json=True``: a 200 whose body is empty or not JSON is asked again, the same
  number of times, since services sometimes answer a request with a page that is not the
  answer. A second failure reaches the client, which reports it as an error.
  A client may opt into an exactly empty HTTP 200 body when its source documents
  that absence form; other clients keep the default unreadable-body behavior.
- **Retries are recorded** (#97). Inside ``noting_retries()`` (a card's build), each
  retry is noted with its source and reason, and the card lists them
  (``quality.retries``): an answer that needed a retry is never silent.

Clients import ``urlopen`` from here instead of ``urllib.request``.

- **What was downloaded** (#100). While a retrieval archive is recording
  (``tools.db._archive``), every final answer, a 404 included, is kept there, and the
  client receives it as it would have.
- **When an answer was read** (``stamp``, #100). A client opens a stamp when it starts
  asking, and uses ``stamp.value`` as the retrieval time of what it returns: the time
  of its first answer when an archive is active (so that a record and the statements
  taken from it agree, and a replayed answer keeps its original time), else the time
  the client started.
- **Many requests to one service** (``gather``, #98). A source answered one record per
  request (UniChem, one compound at a time) is asked by a few threads at once, never
  faster than the pace the service asks for or Sabueso chooses to keep (``Pace``).
  Results come back in the order asked; a failure of one request is that request's
  answer, never the others'.
"""

from __future__ import annotations

import contextlib
import contextvars
import hashlib
import io
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Iterable, Iterator, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request
from urllib.request import urlopen as _urlopen

RETRIES = 2
BACKOFF = 1.5  # seconds, doubled on each retry
MAX_WAIT = 20.0
#: HTTP statuses retried. A 500 is a server error that often passes (ChEMBL's
#: document endpoint answered one on 2026-10-01 and the next request), and every
#: Sabueso request is a read.
TRANSIENT = {429, 500, 502, 503, 504}
_RETRIED: contextvars.ContextVar = contextvars.ContextVar(
    "sabueso_retried", default=None
)
_REQUESTS: contextvars.ContextVar = contextvars.ContextVar(
    "sabueso_requests", default=()
)
_REQUEST: contextvars.ContextVar = contextvars.ContextVar(
    "sabueso_request", default=None
)


@contextlib.contextmanager
def observing_requests():
    """Observe transport facts for a source call, without enabling an archive."""
    observed = []
    token = _REQUESTS.set((*_REQUESTS.get(), observed))
    try:
        yield observed
    finally:
        _REQUESTS.reset(token)


def _route_observed(route, record=None):
    observed = _REQUEST.get()
    if observed is not None:
        observed["route"] = route
        if record is not None:
            observed.update(
                retrieval_ref=record.get("ref"),
                retrieved_at=record.get("retrieved_at"),
                response_sha256=record.get("content_hash"),
                status=record.get("status"),
            )


class _ObservedAnswer:
    def __init__(self, answer, observed):
        self.answer, self.observed = answer, observed

    def __getattr__(self, name):
        return getattr(self.answer, name)

    def read(self, *args):
        try:
            content = self.answer.read(*args)
            self.observed["response_sha256"] = hashlib.sha256(content).hexdigest()
            return content
        except Exception as error:
            self.observed.update(outcome="failed", error=type(error).__name__)
            raise
        finally:
            self.observed["finished_at"] = _clock()

    def __enter__(self):
        self.answer.__enter__()
        return self

    def __exit__(self, *args):
        return self.answer.__exit__(*args)


@contextlib.contextmanager
def noting_retries() -> Iterator[List[Dict[str, Any]]]:
    """The retries made inside the block (a card's build): ``[{source, reason, url}]``."""
    outer = _RETRIED.get()
    noted: List[Dict[str, Any]] = []
    token = _RETRIED.set(noted)
    try:
        yield noted
    finally:
        _RETRIED.reset(token)
        if outer is not None:
            outer.extend(noted)


def _note_retry(url: str, reason: str) -> None:
    noted = _RETRIED.get()
    if noted is not None:
        noted.append({"source": _source(), "reason": reason, "url": _safe_url(url)})
    observed = _REQUEST.get()
    if observed is not None:
        observed["retries"].append(reason)


def retries_summary(noted: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """What a card records of its build's retries (``quality.retries``): per source and
    reason, how many."""
    counts: Dict[Tuple[Any, str], int] = {}
    for item in noted:
        key = (item.get("source"), item["reason"])
        counts[key] = counts.get(key, 0) + 1
    return [
        {"source": source, "reason": reason, "count": count}
        for (source, reason), count in sorted(
            counts.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])
        )
    ]


def user_agent() -> str:
    from sabueso import __version__

    return f"Sabueso/{__version__} (+https://github.com/uibcdf/sabueso)"


def request(
    url: str, data: bytes | None = None, headers: Dict[str, str] | None = None
) -> Request:
    """A ``Request`` carrying Sabueso's user agent (and any other headers)."""
    return Request(
        url, data=data, headers={"User-Agent": user_agent(), **(headers or {})}
    )


def _named(target: Any) -> Request:
    if isinstance(target, Request):
        if not target.has_header("User-agent"):
            target.add_header("User-Agent", user_agent())
        return target
    return request(str(target))


def _wait(attempt: int, error: Exception) -> float:
    retry_after = getattr(error, "headers", None) and error.headers.get("Retry-After")
    if retry_after and str(retry_after).isdigit():
        return min(float(retry_after), MAX_WAIT)
    return min(BACKOFF * (2**attempt), MAX_WAIT)


def _timed_out(error: URLError) -> bool:
    return isinstance(error.reason, TimeoutError) or "timed out" in str(error.reason)


_STAMP: contextvars.ContextVar = contextvars.ContextVar("sabueso_stamp", default=None)


def _clock() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Stamp:
    """The retrieval time of one client call, and the source it asks; see the module
    docstring."""

    def __init__(self, source: str | None = None) -> None:
        self.started = _clock()
        self.first: str | None = None
        self.source = source

    @property
    def value(self) -> str:
        return self.first or self.started

    def __str__(self) -> str:
        return self.value


def stamp(source: str | None = None) -> Stamp:
    """Open the stamp of a client call: the answers it receives next date it, and are
    archived as ``source``'s (the name its SourceAssertions carry)."""
    opened = Stamp(source)
    _STAMP.set(opened)
    return opened


def _source() -> str | None:
    opened = _STAMP.get()
    return opened.source if opened is not None else None


def _answered_at(when: str) -> None:
    opened = _STAMP.get()
    if opened is not None and opened.first is None:
        opened.first = when


class Answer:
    """A response read whole, as a client uses it: ``read()``, ``status``, ``headers``,
    and as a context manager. What an archive keeps is what the client received."""

    def __init__(self, content: bytes, status: int, headers: Any, retrieved_at: str):
        self._content, self.status, self.headers = content, status, headers
        self.retrieved_at = retrieved_at

    def read(self, *_: Any) -> bytes:
        return self._content

    def getcode(self) -> int:
        return self.status

    def __enter__(self) -> "Answer":
        return self

    def __exit__(self, *_: Any) -> None:
        return None


def _kept(headers: Any) -> Dict[str, str]:
    from sabueso.tools.db._archive import KEPT_HEADERS

    return {k: headers.get(k) for k in KEPT_HEADERS if headers and headers.get(k)}


def urlopen(
    target: Any,
    timeout: float = 30.0,
    sleep=time.sleep,
    expect_json: bool = False,
    allow_empty_body: bool = False,
):
    """``urllib.request.urlopen`` with Sabueso's user agent and retries for transient
    failures, and the answer archived when an archive is recording; with
    ``expect_json``, a 200 whose body is not JSON is asked again. See the module
    docstring. ``allow_empty_body`` accepts only an exactly empty HTTP 200 body
    when a source documents that form; all other JSON checks and retries remain.
    """
    if not expect_json:
        return _urlopen_once(target, timeout, sleep)
    for attempt in range(RETRIES + 1):
        answer = _urlopen_once(target, timeout, sleep)
        with answer:
            content = answer.read()
            status = getattr(answer, "status", 200)
            headers = answer.headers
        declared_empty = allow_empty_body and status == 200 and content == b""
        if declared_empty or _readable_json(content) or attempt == RETRIES:
            return Answer(content, status, headers, getattr(answer, "retrieved_at", ""))
        _note_retry(_named(target).full_url, "unreadable_body")
        if isinstance(answer, _ObservedAnswer):
            answer.observed["retries"].append("unreadable_body")
        sleep(_wait(attempt, None))
    raise AssertionError("unreachable")  # pragma: no cover


def _readable_json(content: bytes) -> bool:
    try:
        json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return False
    return True


def _safe_url(url: str) -> str:
    """Keep transport credentials out of observations and archive request identity."""
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

    parts = urlsplit(url)
    fields = parse_qsl(parts.query, keep_blank_values=True)
    if not any(name.lower() == "api_key" for name, _ in fields):
        return url
    return urlunsplit(
        parts._replace(
            query=urlencode(
                [
                    (name, "<key>" if name.lower() == "api_key" else value)
                    for name, value in fields
                ]
            )
        )
    )


def _urlopen_once(target: Any, timeout: float, sleep):
    collectors = _REQUESTS.get()
    if not collectors:
        return _urlopen_transport(target, timeout, sleep)
    named = _named(target)
    observed = {
        "method": named.get_method(),
        "url": _safe_url(named.full_url),
        "request_sha256": hashlib.sha256(named.data).hexdigest()
        if named.data is not None
        else None,
        "route": "not_reached",
        "network_attempts": 0,
        "started_at": _clock(),
        "retries": [],
    }
    for collector in collectors:
        collector.append(observed)
    token = _REQUEST.set(observed)
    try:
        answer = _urlopen_transport(named, timeout, sleep)
        observed.update(outcome="received", status=getattr(answer, "status", None))
        return _ObservedAnswer(answer, observed)
    except Exception as error:
        observed.update(outcome="failed", error=type(error).__name__)
        if isinstance(error, HTTPError):
            observed["status"] = error.code
        raise
    finally:
        observed["finished_at"] = _clock()
        _REQUEST.reset(token)


def _urlopen_transport(target: Any, timeout: float, sleep):
    from sabueso.tools.db import _archive, _mirror

    mode = _archive.active()
    if mode is None:
        _refuse_offline(target)
        return _open(target, timeout, sleep)
    archive = mode.archive
    named = _named(target)
    method, url, body = named.get_method(), _safe_url(named.full_url), named.data
    if mode.name in ("replay", "reuse"):
        planned = mode.planned(method, url, body)
        kept = (
            archive.get(planned)
            if planned
            else archive.find(
                method, url, body, mode.max_age if mode.name == "reuse" else None
            )
        )
        if kept is not None:
            _route_observed(mode.name, kept)
            return _from_archive(kept)
        if mode.name == "replay":
            from sabueso.core.errors import NotArchivedError

            raise NotArchivedError(
                f"Not in the retrieval archive {archive.path.name}: {method} {url}"
            )
    if _mirror.offline():
        _refuse_offline(named)
    retrieved_at = _archive._now()
    try:
        response = _open(named, timeout, sleep)
    except HTTPError as exc:
        # An HTTP answer is an answer (a 404 is "not found"): kept, then raised again.
        with exc:
            content = exc.read() if exc.fp is not None else b""
        record = archive.record(
            method,
            url,
            body,
            exc.code,
            _kept(exc.headers),
            content,
            retrieved_at,
            source=_source(),
        )
        _archive.note(record)
        _route_observed("network", record)
        _answered_at(retrieved_at)
        raise HTTPError(
            exc.url, exc.code, exc.msg, exc.headers, io.BytesIO(content)
        ) from None
    with response:
        content = response.read()
        status = getattr(response, "status", 200)
        headers = response.headers
    record = archive.record(
        method, url, body, status, _kept(headers), content, retrieved_at, _source()
    )
    _archive.note(record)
    _route_observed("network", record)
    _answered_at(retrieved_at)
    return Answer(content, status, headers, retrieved_at)


OFFLINE = "Not asked: working offline"


def _refuse_offline(target: Any) -> None:
    from sabueso.tools.db import _mirror

    if _mirror.offline():
        from sabueso.core.errors import OfflineError

        url = target.full_url if isinstance(target, Request) else str(target)
        raise OfflineError(f"{OFFLINE}: {_safe_url(url)}")


def _from_archive(kept: Dict[str, Any]):
    """An archived answer, served as the source served it, with its original time."""
    from email.message import Message

    from sabueso.tools.db import _archive

    headers = Message()
    for key, value in kept["headers"].items():
        headers[key] = value
    _archive.note(_archive.summary(kept))
    _answered_at(kept["retrieved_at"])
    if kept["status"] >= 400:
        raise HTTPError(
            kept["url"],
            kept["status"],
            "archived",
            headers,
            io.BytesIO(kept["content"]),
        )
    return Answer(kept["content"], kept["status"], headers, kept["retrieved_at"])


def _open(target: Any, timeout: float, sleep):
    named = _named(target)
    for attempt in range(RETRIES + 1):
        try:
            _route_observed("network")
            observed = _REQUEST.get()
            if observed is not None:
                observed["network_attempts"] += 1
            return _urlopen(named, timeout=timeout)
        except HTTPError as exc:
            if exc.code not in TRANSIENT or attempt == RETRIES:
                raise
            try:
                _note_retry(named.full_url, f"HTTP {exc.code}")
                wait = _wait(attempt, exc)
            finally:
                exc.close()
            sleep(wait)
        except URLError as exc:
            if _timed_out(exc) or attempt == RETRIES:
                raise
            _note_retry(named.full_url, "connection")
            sleep(_wait(attempt, exc))
    raise AssertionError("unreachable")  # pragma: no cover


class Pace:
    """At most ``per_second`` requests start per second, across threads."""

    def __init__(
        self, per_second: float, sleep=time.sleep, clock=time.monotonic
    ) -> None:
        self.interval = 1.0 / per_second
        self._lock = threading.Lock()
        self._next = 0.0
        self._sleep, self._clock = sleep, clock

    def wait(self) -> None:
        with self._lock:
            now = self._clock()
            start = max(now, self._next)
            self._next = start + self.interval
        if start > now:
            self._sleep(start - now)


def gather(
    call: Callable[[Any], Any],
    items: Iterable[Any],
    workers: int = 4,
    per_second: float | None = None,
    expected: Tuple[type, ...] = (),
) -> List[Tuple[Any, Any]]:
    """``[(item, answer)]`` in the order of ``items``: ``call(item)``'s result, or the
    exception it raised when that exception is ``expected`` (a source's not found or
    failure). Any other exception is a fault, and is raised.

    ``workers`` threads ask at once, and no more than ``per_second`` requests start per
    second (unpaced when None).
    """
    items = list(items)
    pace = Pace(per_second) if per_second else None

    def one(item: Any) -> Any:
        if pace is not None:
            pace.wait()
        try:
            return call(item)
        except expected as exc:
            return exc

    if workers <= 1 or len(items) <= 1:
        return [(item, one(item)) for item in items]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        # Each request runs in a copy of the caller's context, so an archive that is
        # recording, and the build collecting its records, see it (#100).
        futures = [
            pool.submit(contextvars.copy_context().run, one, item) for item in items
        ]
        return list(zip(items, (f.result() for f in futures)))


def download(url: str, path: Any, timeout: float = 600.0, chunk: int = 1 << 20) -> str:
    """Stream a release file to ``path`` (written next to it, then renamed) and return
    its MD5. For whole releases (mirrors, #100): not kept by a retrieval archive, since
    the file itself is kept and checked against the checksum its source publishes."""
    import hashlib
    from pathlib import Path

    target = Path(path)
    partial = target.with_name(target.name + ".part")
    md5 = hashlib.md5()  # nosec - compared with the checksum the source publishes
    with _open(url, timeout, time.sleep) as response, open(partial, "wb") as out:
        while True:
            block = response.read(chunk)
            if not block:
                break
            md5.update(block)
            out.write(block)
    partial.replace(target)
    return md5.hexdigest()
