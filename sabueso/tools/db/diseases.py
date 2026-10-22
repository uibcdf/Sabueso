"""DISEASES (Jensen lab): human gene–disease associations, by channel (#82, #83).

DISEASES keeps three channels apart, each with its own score:

- ``knowledge``: associations curated by other resources (MedlinePlus, UniProtKB
  keywords…), with the resource and a confidence (stars, 0 to 5);
- ``experiments``: associations from experimental resources (e.g. TIGA for GWAS), with
  the resource's own score and a confidence;
- ``textmining``: co-mentions found by text mining, with a z-score and a confidence.
  Text mining links names, not molecules: a parasite enzyme named like a human one is
  counted for the human gene.

Genes are Ensembl proteins (``ENSP…``) and diseases Disease Ontology terms (``DOID:…``).
The files are published as whole downloads (CC BY 4.0), updated in place, so the
version recorded is each file's publication date (its ``Last-Modified``).

``OnlineDISEASESClient`` downloads a channel's filtered file once per process, or keeps
it in a cache directory when one is given (``cache_dir=``, ``$SABUESO_CACHE_DIR``; see
``devguide/CACHE_POLICY.md``). ``FixtureDISEASESClient`` reads
``<directory>/diseases/<channel>.tsv`` and ``versions.json``.

``associations(proteins, channels)`` returns ``{"retrieved_at", "version": {channel:
date}, "record": {channel: [row, ...]}, "missing": [...]}``: the rows naming any of the
Ensembl proteins, and the proteins no channel names.
"""

from __future__ import annotations

import json
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.diseases_acquisition import (
    ObservedIndex,
    note_channel,
    observe,
    origin,
)
from sabueso.core.errors import ConnectorError
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db import _release
from sabueso.tools.db._http import observing_requests, stamp, urlopen
from sabueso.tools.db._http import request as http_request
from sabueso.tools.db._record import online, source_record

SOURCE = "DISEASES"
DOWNLOADS = "https://download.jensenlab.org"
CHANNELS = ("knowledge", "experiments", "textmining")
#: Columns of each channel's filtered file, after gene id, gene name, disease id and
#: disease name.
COLUMNS = {
    "knowledge": ("source_database", "statement_type", "confidence"),
    "experiments": ("source_database", "source_score", "confidence"),
    "textmining": ("z_score", "confidence", "url"),
}


def parse_channel(text: str, channel: str) -> Dict[str, List[Dict[str, Any]]]:
    """A channel's file as rows per Ensembl protein (``ENSP…`` entries only)."""
    index: Dict[str, List[Dict[str, Any]]] = {}
    for line in text.splitlines():
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 4 + len(COLUMNS[channel]) or not parts[0].startswith("ENSP"):
            continue
        row = {
            "protein": parts[0],
            "gene_name": parts[1],
            "disease": parts[2],
            "disease_name": parts[3],
            **dict(zip(COLUMNS[channel], parts[4:])),
        }
        index.setdefault(parts[0], []).append(row)
    return index


def _select(
    indexes: Dict[str, Dict[str, List[Dict[str, Any]]]], proteins: List[str]
) -> Dict[str, Any]:
    record = {
        channel: [row for p in proteins for row in index.get(p, [])]
        for channel, index in indexes.items()
    }
    named = {row["protein"] for rows in record.values() for row in rows}
    return {"record": record, "missing": [p for p in proteins if p not in named]}


def _parse_document(payload, channel):
    text = payload.decode("utf-8")
    # A filtered download is TSV, not an HTML error page with HTTP 200.
    for line in text.splitlines():
        if line.strip() and len(line.split("\t")) < 4 + len(COLUMNS[channel]):
            raise ValueError("invalid filtered TSV row")
    return parse_channel(text, channel)


def _validate_index(index):
    if not isinstance(index, dict) or not all(
        isinstance(protein, str)
        and isinstance(rows, list)
        and all(
            isinstance(row, dict)
            and row.get("protein") == protein
            and isinstance(row.get("disease"), str)
            for row in rows
        )
        for protein, rows in index.items()
    ):
        raise ValueError("invalid cached channel index")


class OnlineDISEASESClient:
    def __init__(self, timeout: float = 300.0, cache_dir: str | Path | None = None):
        self.timeout = timeout
        self.cache_dir = _release.cache_directory("diseases", cache_dir)

    def _fetch(self, channel: str) -> tuple:
        """``(version, rows per protein)`` of a channel's filtered file."""
        url = f"{DOWNLOADS}/human_disease_{channel}_filtered.tsv"
        # The server refuses Python's default user agent; Sabueso names itself.
        request = http_request(url)
        try:
            with (
                observing_requests() as requests,
                urlopen(request, timeout=self.timeout) as resp,
            ):  # nosec - trusted
                modified = resp.headers.get("Last-Modified")
                version = (
                    parsedate_to_datetime(modified).date().isoformat()
                    if modified
                    else None
                )
                kept = _release.recall(SOURCE, (channel, version))
                if version is not None and kept is not None:
                    _validate_index(kept)
                    note_channel(channel, version, kept, access="memory")
                    return version, kept
                cached = (
                    self.cache_dir / f"{channel}_{version}.json"
                    if self.cache_dir is not None and version
                    else None
                )
                if cached is not None and cached.is_file():
                    index = json.loads(cached.read_text(encoding="utf-8"))
                    _validate_index(index)
                    access = "disk"
                else:
                    payload = resp.read()
                    index = ObservedIndex(
                        _parse_document(payload, channel),
                        origin(payload, stamp_time(requests), requests),
                    )
                    access = "download"
                    if cached is not None:
                        _release.write_file(cached, json.dumps(index))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"DISEASES {channel} download failed: {exc}") from exc
        if version is not None:
            _release.keep(SOURCE, (channel, version), index)
        note_channel(channel, version, index, access=access)
        return version, index

    @observe()
    def associations(
        self, proteins: Iterable[str], channels: Iterable[str] = CHANNELS
    ) -> Dict[str, Any]:
        ids = sorted({p.split(".")[0] for p in proteins if p})
        retrieval = stamp(SOURCE)
        versions, indexes = {}, {}
        for channel in channels:
            versions[channel], indexes[channel] = self._fetch(channel)
        dates = [
            (getattr(index, "origin", None) or {}).get("retrieved_at")
            for index in indexes.values()
        ]
        return {
            "retrieved_at": min(dates) if dates and all(dates) else retrieval.value,
            "version": versions,
        } | _select(indexes, ids)


class FixtureDISEASESClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "diseases"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    @observe(fixture=True)
    def associations(
        self, proteins: Iterable[str], channels: Iterable[str] = CHANNELS
    ) -> Dict[str, Any]:
        ids = sorted({p.split(".")[0] for p in proteins if p})
        if self.failing & set(ids):
            raise ConnectorError(f"DISEASES request for {ids} failed (simulated)")
        indexes = {}
        try:
            versions = json.loads((self.directory / "versions.json").read_text())
            if not isinstance(versions, dict) or any(
                value is not None and not isinstance(value, str)
                for value in versions.values()
            ):
                raise ValueError("invalid channel dates")
            for channel in channels:
                payload = (self.directory / f"{channel}.tsv").read_bytes()
                indexes[channel] = ObservedIndex(
                    _parse_document(payload, channel),
                    origin(payload, self.retrieved_at, fixture=True),
                )
                note_channel(
                    channel, versions.get(channel), indexes[channel], access="fixture"
                )
        except FileNotFoundError as error:
            raise missing_fixture(
                f"DISEASES channel fixture is unavailable: {error.filename}"
            ) from error
        except (OSError, ValueError) as error:
            raise ConnectorError(
                f"DISEASES channel fixture is invalid: {error}"
            ) from error
        return {
            "retrieved_at": self.retrieved_at,
            "version": {c: versions.get(c) for c in channels},
        } | _select(indexes, ids)


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_associations(
    identifiers: Any, client: Any = None, skip_digestion: bool = False
):
    """DISEASES's gene–disease rows naming Ensembl proteins (``ENSP…``), per channel."""
    response = online(client, OnlineDISEASESClient).associations(identifiers)
    return source_record(
        SOURCE,
        "associations",
        {"ensembl_proteins": list(identifiers)},
        response.get("retrieved_at"),
        "; ".join(f"{c} {v}" for c, v in sorted(response["version"].items()) if v)
        or None,
        {"associations": response["record"], "missing": response["missing"]},
    )


def stamp_time(requests):
    from sabueso.tools.db._http import _STAMP

    return next(
        (r.get("retrieved_at") for r in requests if r.get("retrieved_at")),
        _STAMP.get().value,
    )
