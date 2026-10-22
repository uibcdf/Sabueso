"""BindingDB as a local mirror: its monthly release, indexed by protein (#100, #98).

BindingDB publishes its whole dataset every month as one TSV (``BindingDB_All_<yyyymm>
_tsv.zip``, about 600 MB, 9 GB unpacked) with an MD5. Each row is one measurement, with
the ligand as BindingDB states it (SMILES, InChIKey, monomer id, ChEMBL and PubChem
ids), the affinities (Ki, IC50, Kd, EC50, in nM), the publication, where the row came
from (``Curation/DataSource``), and the UniProt ids of every chain of the target.

``BindingDBMirror`` installs a release: it downloads the file, checks its MD5, and
indexes the measurements by UniProt accession (every chain's SwissProt and TrEMBL
primary id) in ``index.sqlite``. The download is removed once indexed.

``MirrorBindingDBClient`` answers ``ligands(accession, cutoff, limit)`` from the index
with the records the REST service gives (monomer id, SMILES, affinity type and value,
PubMed id, DOI), one per stated affinity, plus what the REST service does not state:
the InChIKey, ChEMBL and PubChem ids BindingDB gives the ligand, and the row's data
source.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
import sys
import zipfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List
from urllib.error import HTTPError

from sabueso.core.bindingdb_acquisition import note_response, observe
from sabueso.core.errors import ConnectorError, RecordNotFoundError, StorageError

SOURCE = "BindingDB"
DOWNLOADS = "https://www.bindingdb.org/rwd/bind/chemsearch/marvin/Download.jsp"
FILES = "https://www.bindingdb.org/rwd/bind/downloads"
RELEASE_FILE = re.compile(r"BindingDB_All_(\d{6})_tsv\.zip")
AFFINITIES = ("Ki", "IC50", "Kd", "EC50")
INDEX = "index.sqlite"

SCHEMA = """
CREATE TABLE records (
    accession TEXT NOT NULL,
    monomerid INTEGER NOT NULL,
    smile TEXT,
    inchikey TEXT,
    affinity_type TEXT NOT NULL,
    affinity TEXT NOT NULL,
    pmid TEXT,
    doi TEXT,
    chembl_id TEXT,
    pubchem_cid TEXT,
    data_source TEXT,
    reactant_set TEXT
);
"""


def _column(header: List[str], name: str) -> int:
    return header.index(name)


def _numeric(affinity: str) -> float | None:
    try:
        return float(affinity.strip().lstrip("<>~="))
    except ValueError:
        return None


def rows(tsv: io.TextIOBase) -> Iterator[tuple]:
    """``(accession, monomerid, smile, inchikey, type, affinity, pmid, doi, chembl,
    cid, data source, reactant set)`` per protein and stated affinity of each row."""
    reader = csv.reader(tsv, delimiter="\t", quoting=csv.QUOTE_NONE)
    header = next(reader)
    col = {name: _column(header, name) for name in header}
    accessions = [
        i
        for i, name in enumerate(header)
        if re.match(
            r"UniProt \((SwissProt|TrEMBL)\) Primary ID of Target Chain \d+$", name
        )
    ]
    affinity = {kind: col[f"{kind} (nM)"] for kind in AFFINITIES}
    for row in reader:
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        monomer = row[col["BindingDB MonomerID"]].strip()
        if not monomer.isdigit():
            continue
        proteins = {row[i].strip() for i in accessions if row[i].strip()}
        stated = [(k, row[i]) for k, i in affinity.items() if row[i].strip()]
        if not proteins or not stated:
            continue
        common = (
            int(monomer),
            row[col["Ligand SMILES"]] or None,
            row[col["Ligand InChI Key"]] or None,
        )
        tail = (
            row[col["PMID"]] or None,
            row[col["Article DOI"]] or None,
            row[col["ChEMBL ID of Ligand"]] or None,
            row[col["PubChem CID"]] or None,
            row[col["Curation/DataSource"]] or None,
            row[col["BindingDB Reactant_set_id"]] or None,
        )
        for accession in sorted(proteins):
            for kind, value in stated:
                yield (accession, *common, kind, value, *tail)


class BindingDBMirror:
    """Install BindingDB's monthly release as a mirror; see the module docstring."""

    source = "bindingdb"
    source_name = SOURCE

    def latest(self) -> str:
        """The newest release BindingDB publishes (``yyyymm``)."""
        from sabueso.tools.db._http import urlopen

        try:
            with urlopen(DOWNLOADS, timeout=60) as resp:
                page = resp.read().decode("utf-8", "replace")
        except OSError as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"BindingDB downloads page failed: {exc}") from exc
        found = sorted(set(RELEASE_FILE.findall(page)))
        if not found:
            raise RecordNotFoundError("BindingDB's downloads page names no release")
        return found[-1]

    def install(
        self,
        release: str,
        directory: Path,
        from_file: str | Path | None = None,
        md5: str | None = None,
    ) -> Dict[str, Any]:
        """Download (or take ``from_file``), check and index one release. ``md5`` is
        the published checksum when it is already known; otherwise it is fetched."""
        from sabueso.tools.db._http import download, urlopen

        directory.mkdir(parents=True, exist_ok=True)
        name = f"BindingDB_All_{release}_tsv.zip"
        url = f"{FILES}/{name}"
        published = md5
        if published is None:
            with urlopen(
                f"{FILES}/BindingDB_All_{release}_tsv.md5", timeout=60
            ) as resp:
                published = resp.read().decode("utf-8").split()[0]
        published = published.strip().lower()
        archive = directory / name
        if from_file is not None:
            import hashlib

            archive = Path(from_file)
            digest = hashlib.md5()  # nosec - compared with the published checksum
            with open(archive, "rb") as handle:
                for block in iter(lambda: handle.read(1 << 20), b""):
                    digest.update(block)
            got = digest.hexdigest()
        else:
            got = download(url, archive)
        if got != published:
            raise StorageError(
                f"BindingDB {release}: MD5 {got} does not match the published {published}"
            )
        index = directory / INDEX
        partial = index.with_name(INDEX + ".part")
        partial.unlink(missing_ok=True)
        count = 0
        # closing(): a connection's context manager commits but does not close, and
        # Windows cannot rename a file that is still open.
        with closing(sqlite3.connect(partial)) as conn, conn:
            conn.execute("PRAGMA journal_mode = OFF")
            conn.execute("PRAGMA synchronous = OFF")
            conn.executescript(SCHEMA)
            with zipfile.ZipFile(archive) as z:
                (member,) = [i for i in z.namelist() if i.endswith(".tsv")]
                with z.open(member) as raw:
                    text = io.TextIOWrapper(raw, encoding="utf-8", errors="replace")
                    # A C long is 32 bits on Windows.
                    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
                    batch = []
                    for row in rows(text):
                        batch.append(row)
                        if len(batch) >= 50_000:
                            conn.executemany(
                                "INSERT INTO records VALUES "
                                "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                batch,
                            )
                            count += len(batch)
                            batch = []
                    conn.executemany(
                        "INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        batch,
                    )
                    count += len(batch)
            conn.execute("CREATE INDEX records_by_accession ON records (accession)")
        partial.replace(index)
        if from_file is None:
            archive.unlink()
        info = {
            "source": self.source,
            "source_name": SOURCE,
            "release": release,
            "url": url,
            "md5": got,
            "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "records": count,
            "index": INDEX,
        }
        (directory / "release.json").write_text(json.dumps(info, indent=1) + "\n")
        return info

    def client(self, directory: Path) -> "MirrorBindingDBClient":
        return MirrorBindingDBClient(directory)


class MirrorBindingDBClient:
    """``ligands(accession, cutoff, limit)`` from an installed release; see the module
    docstring."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        info = json.loads((self.directory / "release.json").read_text("utf-8"))
        self.release = info["release"]
        self.installed_at = info["installed_at"]
        self._release_info = info

    @observe(mirror=True)
    def ligands(
        self, accession: str, cutoff: float | None = None, limit: int | None = None
    ) -> Dict[str, Any]:
        from sabueso.tools.db.bindingdb import (
            DEFAULT_CUTOFF,
            DEFAULT_LIMIT,
            _kept,
        )

        cutoff = DEFAULT_CUTOFF if cutoff is None else cutoff
        with closing(
            sqlite3.connect(f"file:{self.directory / INDEX}?mode=ro", uri=True)
        ) as conn:
            found = conn.execute(
                "SELECT monomerid, smile, inchikey, affinity_type, affinity, pmid, doi, "
                "chembl_id, pubchem_cid, data_source FROM records WHERE accession = ?",
                (accession,),
            ).fetchall()
        records = []
        for (
            monomer,
            smile,
            inchikey,
            kind,
            value,
            pmid,
            doi,
            chembl,
            cid,
            origin,
        ) in found:
            number = _numeric(value)
            if number is not None and number > cutoff:
                continue
            records.append(
                {
                    "query": accession,
                    "monomerid": monomer,
                    "smile": smile,
                    "affinity_type": kind,
                    "affinity": value,
                    "pmid": pmid,
                    "doi": doi,
                    "inchikey": inchikey,
                    "chembl_id": chembl,
                    "pubchem_cid": cid,
                    "data_source": origin,
                }
            )
        note_response({"getLindsByUniprotsResponse": {"affinities": records}})
        if not records:
            raise RecordNotFoundError(
                f"BindingDB {self.release} has no affinities for {accession}",
                version=self.release,
            )
        kept = _kept(accession, self.installed_at, records, limit or DEFAULT_LIMIT)
        return {**kept, "version": self.release, "access": "mirror"}
