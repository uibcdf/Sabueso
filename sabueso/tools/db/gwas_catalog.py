"""Read one bounded native GWAS Catalog standard mapped-gene association page."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from smonitor import signal

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError
from sabueso.core.snapshot import canonical_json, digest
from sabueso.core.source_acquisition import (
    _terminal,
    acquisition,
    capture_acquisitions,
    missing_fixture,
)
from sabueso.mappings.gwas_catalog import (
    URL,
    page_is_partial,
    page_rows,
    response_query,
    validate_page,
)
from sabueso.tools.db._http import stamp, urlopen
from sabueso.tools.db._record import online, source_record
from sabueso.tools.source_snapshot import _json, load_source_snapshot


def _summarize(result, query, fixture, requests):
    if isinstance(result, Exception):
        return {"outcome": _terminal(result, fixture, requests)}
    record = validate_page(
        result["record"], query["identifier"], query["limit"], query["page"]
    )
    out = {
        "outcome": "received" if page_rows(record) else "empty",
        "count": len(page_rows(record)),
        "retrieved_at": result.get("retrieved_at"),
        "source_version": {
            "value": None,
            "basis": "dataset_association_assembly_and_sequence_revisions_not_stated",
        },
        "response_identity": {
            "basis": "decoded_native_HAL_mapped_gene_association_page",
            "hash": digest(canonical_json(record)),
        },
        "native_page": deepcopy(record["page"]),
        "coverage": "one_standard_mapped_gene_page; no_implicit_pagination_or_absence_claim",
        "truncated": page_is_partial(record),
    }
    if "download_sha256" in result:
        out["download_sha256"] = result["download_sha256"]
    if "snapshot_receipt" in result:
        out.update(
            access="supplied_file",
            snapshot_receipt=deepcopy(result["snapshot_receipt"]),
        )
    return out


class OnlineGwasCatalogClient:
    def __init__(self, timeout=30.0):
        self.timeout = timeout

    @acquisition("GWAS Catalog", "mapped_gene_associations", summarize=_summarize)
    def associations(self, identifier, limit, page):
        query = response_query(identifier, limit, page)
        retrieval = stamp("GWAS Catalog")
        try:
            with urlopen(
                URL + "?" + urlencode(query), timeout=self.timeout, expect_json=True
            ) as response:
                raw = response.read()
                payload = _json(raw.decode("utf-8"))
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as error:
            if isinstance(error, HTTPError):
                error.close()
            raise ConnectorError(f"GWAS Catalog access failed: {error}") from error
        validate_page(payload, identifier, limit, page)
        return {
            "record": payload,
            "retrieved_at": retrieval.value,
            "version": None,
            "download_sha256": hashlib.sha256(raw).hexdigest(),
        }


class SnapshotGwasCatalogClient:
    def __init__(self, path, *, source_metadata, expected_sha256=None):
        self.path, self.source_metadata = path, deepcopy(source_metadata)
        self.expected_sha256 = expected_sha256

    @acquisition(
        "GWAS Catalog", "mapped_gene_associations", fixture=True, summarize=_summarize
    )
    def associations(self, identifier, limit, page):
        query = response_query(identifier, limit, page)
        try:
            result = load_source_snapshot(
                self.path,
                source_metadata=self.source_metadata,
                expected_sha256=self.expected_sha256,
            )
        except OSError as error:
            raise missing_fixture(
                f"Supplied GWAS Catalog snapshot is unavailable: {self.path}"
            ) from error
        if (
            result["source"] != "GWAS Catalog"
            or result["kind"] != "mapped_gene_associations"
            or result["query"] != query
            or response_query(
                result["query"].get("mapped_gene"),
                result["query"].get("size"),
                result["query"].get("page"),
            )
            != query
            or result["version"] is not None
        ):
            raise ConnectorError(
                "Supplied GWAS Catalog source/kind/query/revision differ from the request."
            )
        validate_page(result["record"], identifier, limit, page)
        return result


class FixtureGwasCatalogClient:
    def __init__(self, directory="temp_data", retrieved_at=None):
        self.directory = Path(directory) / "gwas_catalog"
        self.retrieved_at = retrieved_at

    def associations(self, identifier, limit, page):
        query = response_query(identifier, limit, page)
        return SnapshotGwasCatalogClient(
            self.directory
            / f"associations__{identifier}__size{limit}__page{page}.json",
            source_metadata={
                "source": "GWAS Catalog",
                "kind": "mapped_gene_associations",
                "query": query,
                "retrieved_at": self.retrieved_at,
            },
        ).associations(identifier, limit, page)


@signal(tags=["api", "source"])
@arg_digest()
@capture_acquisitions
def get_associations(identifier, limit=20, page=0, client=None, skip_digestion=False):
    """Receive one explicit standard mapped-gene page, retaining native support.

    ``identifier`` is a literal gene symbol, not a biological identity resolution.
    ``page`` is zero-based; limits 1 to 500 are a local reader bound. API v2 gene
    mappings do not establish causal genes, protein function or sequence axes.
    Original statistics/text/alleles remain native; no inferred units, ranking,
    summary-statistics acquisition, page following, job or card intake occurs.
    """
    query = response_query(identifier, limit, page)
    result = online(client, OnlineGwasCatalogClient).associations(
        identifier, limit, page
    )
    if (
        not isinstance(result, dict)
        or result.get("version") is not None
        or ("source" in result and result["source"] != "GWAS Catalog")
        or ("kind" in result and result["kind"] != "mapped_gene_associations")
        or ("query" in result and result["query"] != query)
    ):
        raise ConnectorError(
            "GWAS Catalog client response/revision/query is unsupported."
        )
    if (
        "query" in result
        and response_query(
            result["query"].get("mapped_gene"),
            result["query"].get("size"),
            result["query"].get("page"),
        )
        != query
    ):
        raise ConnectorError("GWAS Catalog client query types differ from the request.")
    record = validate_page(result.get("record"), identifier, limit, page)
    cut = page_is_partial(record)
    if "truncated" in result and result["truncated"] is not cut:
        raise ConnectorError(
            "GWAS Catalog client cut differs from native page coverage."
        )
    envelope = source_record(
        "GWAS Catalog",
        "mapped_gene_associations",
        query,
        result.get("retrieved_at"),
        None,
        deepcopy(record),
        truncated=cut,
    )
    for k in ("snapshot_receipt", "download_sha256"):
        if k in result:
            envelope[k] = deepcopy(result[k])
    return envelope
