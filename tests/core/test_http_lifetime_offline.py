# HTTP response ownership survives retries, archives and source translation.

import io
import json
from contextlib import nullcontext
from datetime import timedelta
from email.message import Message
from urllib.error import HTTPError

import pytest

from sabueso import RetrievalArchive
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.tools.db import _http, klifs, mobidb, pubchem, uniprot


@pytest.fixture
def errors():
    owned = []

    def make(code=404, body=b"missing", headers=None):
        response = io.BytesIO(body)
        error = HTTPError(
            "https://example.invalid/offline",
            code,
            "status",
            headers or Message(),
            response,
        )
        owned.append(error)
        return error, response

    yield make
    for error in owned:
        error.close()


@pytest.mark.parametrize("code", [429, 500, 502, 503, 504])
def test_discarded_retry_is_closed_before_waiting(monkeypatch, errors, code):
    headers = Message()
    headers["Retry-After"] = "3"
    error, response = errors(code, headers=headers)
    answers = iter([error, "ok"])

    def open_once(*args, **kwargs):
        answer = next(answers)
        if isinstance(answer, HTTPError):
            raise answer
        return answer

    def wait(seconds):
        assert seconds == 3
        assert response.closed

    monkeypatch.setattr(_http, "_urlopen", open_once)
    with _http.noting_retries() as noted:
        assert _http.urlopen(error.url, sleep=wait) == "ok"
    assert [item["reason"] for item in noted] == [f"HTTP {code}"]


@pytest.mark.parametrize("interruption", ["note", "sleep"])
def test_retry_interruption_still_releases_discarded_response(
    monkeypatch, errors, interruption
):
    error, response = errors(503)
    failure = RuntimeError("interrupted retry")

    def fail(*args, **kwargs):
        raise error

    def interrupt(*args):
        raise failure

    monkeypatch.setattr(_http, "_urlopen", fail)
    if interruption == "note":
        monkeypatch.setattr(_http, "_note_retry", interrupt)
    with pytest.raises(RuntimeError) as caught:
        _http.urlopen(error.url, sleep=interrupt)
    assert caught.value is failure and response.closed


@pytest.mark.parametrize("observed", [False, True])
@pytest.mark.parametrize("code", [400, 404, 503])
def test_final_raw_error_keeps_native_identity_and_caller_owned_body(
    monkeypatch, errors, observed, code
):
    error, response = errors(code)

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(_http, "_urlopen", fail)
    monkeypatch.setattr(_http, "RETRIES", 0)
    with _http.observing_requests() if observed else nullcontext():
        with pytest.raises(HTTPError) as caught:
            _http.urlopen(error.url)
    assert caught.value is error
    assert not response.closed and error.read() == b"missing"
    error.close()
    assert response.closed


@pytest.mark.parametrize("failure", [None, "read", "record"])
def test_archive_releases_original_on_replacement_and_failure(
    tmp_path, monkeypatch, errors, failure
):
    error, response = errors()
    archive = RetrievalArchive(tmp_path / "retrieval.db")
    sentinel = RuntimeError("archive failed")

    def fail(*args, **kwargs):
        raise error

    def interrupt(*args, **kwargs):
        raise sentinel

    monkeypatch.setattr(_http, "_urlopen", fail)
    if failure == "read":
        monkeypatch.setattr(error, "read", interrupt)
    if failure == "record":
        monkeypatch.setattr(archive, "record", interrupt)
    with archive.recording():
        with pytest.raises(RuntimeError if failure else HTTPError) as caught:
            _http.urlopen(error.url)
    try:
        assert response.closed
        if failure:
            assert caught.value is sentinel
        else:
            assert caught.value is not error
            assert caught.value.code == 404 and caught.value.read() == b"missing"
            assert archive.stats()["records"] == 1
    finally:
        if isinstance(caught.value, HTTPError):
            caught.value.close()


@pytest.mark.parametrize("mode", ["direct", "recording", "replay", "reuse"])
@pytest.mark.parametrize("status", [404, 400])
def test_translated_source_error_closes_body_and_keeps_classification(
    tmp_path, monkeypatch, errors, mode, status
):
    error, response = errors(status)

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(_http, "_urlopen", fail)
    archive = RetrievalArchive(tmp_path / "retrieval.db")
    if mode in {"replay", "reuse"}:
        # Seed the exact source request through the ordinary recording route.
        with archive.recording(), pytest.raises((ConnectorError, RecordNotFoundError)):
            uniprot.OnlineUniProtClient().fetch_entry("P60174")
        monkeypatch.setattr(
            _http, "_urlopen", lambda *a, **k: pytest.fail("unexpected network")
        )
    context = {
        "direct": nullcontext,
        "recording": archive.recording,
        "replay": archive.replaying,
        "reuse": lambda: archive.reusing(timedelta(days=1)),
    }[mode]
    expected = RecordNotFoundError if status == 404 else ConnectorError
    with context(), pytest.raises(expected) as caught:
        uniprot.OnlineUniProtClient().fetch_entry("P60174")
    cause = caught.value.__cause__
    assert isinstance(cause, HTTPError) and cause.code == status
    assert cause.closed and response.closed
    if mode == "direct":
        assert cause is error


@pytest.mark.parametrize(
    "source,status,body,expected",
    [
        ("klifs", 400, [400, "unknown kinase"], RecordNotFoundError),
        ("klifs", 400, {}, ConnectorError),
        (
            "mobidb",
            404,
            {"error": {"code": "PROTEIN_NOT_FOUND", "parameter": "acc"}},
            RecordNotFoundError,
        ),
        ("mobidb", 404, {}, ConnectorError),
    ],
)
def test_source_reads_native_absence_body_before_closing(
    monkeypatch, errors, source, status, body, expected
):
    error, response = errors(status, json.dumps(body).encode())

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(_http, "_urlopen", fail)
    with pytest.raises(expected) as caught:
        if source == "klifs":
            klifs.OnlineKLIFSClient().kinase(1)
        else:
            mobidb.OnlineMobiDBClient().annotations("P60174")
    assert caught.value.__cause__ is error and response.closed


def test_pubchem_fault_body_remains_available_until_translation(monkeypatch, errors):
    error, response = errors(400, b'{"Fault":{"Message":"invalid structure"}}')

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setattr(_http, "_urlopen", fail)
    result = pubchem.OnlinePubChemClient().structure("smiles", "synthetic")
    assert result["cids"] == [] and result["fault"] == "invalid structure"
    assert response.closed
