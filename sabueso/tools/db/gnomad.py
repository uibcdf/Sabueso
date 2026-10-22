"""gnomAD: population frequencies of a human gene's variants (#83).

gnomAD states, per variant, its allele count, allele number and frequency in exomes and
genomes, and its consequence on a transcript (``transcript_id``, with ``hgvsc`` and
``hgvsp``). Asked for a gene (the Ensembl gene id the UniProt entry cross-references),
it states each variant's consequence on one of the gene's transcripts, the one it
ranks most severe. Asked for a transcript, it states each variant's consequence on that
transcript, with the transcript's version (#85).

``variants(gene)`` returns ``{"retrieved_at", "version", "record": {"gene", "variants"}}``,
where ``gene`` keeps gnomAD's canonical and MANE Select transcripts and the gene's
transcripts it annotates (with their versions), and ``version`` the dataset asked (``gnomad_r4``); the API states no finer release.
``transcript_variants(transcript)`` returns the same shape with ``record: {"transcript",
"variants"}``. Both raise ``RecordNotFoundError`` when gnomAD has no such gene or
transcript. ``OnlineGnomADClient`` uses the GraphQL API (no key; data CC0 1.0, some
annotations under other terms, none of which Sabueso reads); ``FixtureGnomADClient``
reads ``<directory>/gnomad/<ENSG or ENST>.json``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError

from sabueso._private.argdigest import arg_digest
from sabueso.core.errors import ConnectorError, RecordNotFoundError
from sabueso.core.gnomad_acquisition import (
    note_completed,
    note_response,
    observe,
    validate_consequences,
    validate_fixture,
)
from sabueso.core.source_acquisition import capture_acquisitions, missing_fixture
from sabueso.tools.db._http import request, stamp, urlopen
from sabueso.tools.db._record import online, source_record

SOURCE = "gnomAD"
API = "https://gnomad.broadinstitute.org/api"
DATASET = "gnomad_r4"
QUERY = (
    """
query($gene: String!) {
  gene(gene_id: $gene, reference_genome: GRCh38) {
    gene_id symbol canonical_transcript_id
    mane_select_transcript { ensembl_id refseq_id }
    transcripts { transcript_id transcript_version }
    variants(dataset: %s) {
      variant_id consequence hgvsp hgvsc transcript_id flags
      exome { ac an af } genome { ac an af }
    }
  }
}
"""
    % DATASET
)
TRANSCRIPT_QUERY = (
    """
query($transcript: String!) {
  transcript(transcript_id: $transcript, reference_genome: GRCh38) {
    transcript_id transcript_version gene_id
    variants(dataset: %s) {
      variant_id consequence hgvsp hgvsc transcript_id transcript_version flags
      exome { ac an af } genome { ac an af }
    }
  }
}
"""
    % DATASET
)
#: pext (proportion expressed across transcripts, #102): per coding region of the gene,
#: the share of the gene's expression in each GTEx v10 tissue that includes it, as
#: gnomAD computes it from GTEx's isoform quantifications (GRCh38).
PEXT_QUERY = """
query($gene: String!) {
  gene(gene_id: $gene, reference_genome: GRCh38) {
    gene_id symbol chrom strand
    pext { flags regions { start stop mean tissues { tissue value } } }
    transcripts { transcript_id transcript_version exons { feature_type start stop } }
  }
}
"""
PEXT_VERSION = "gnomad_r4 pext (GTEx v10)"
#: A variant's consequence on every transcript it touches, asked for many variants at
#: once through GraphQL aliases (#102): gnomAD answers bursts with HTTP 429.
CONSEQUENCE_FIELDS = (
    "variant_id transcript_consequences { transcript_id transcript_version hgvsp "
    "hgvsc major_consequence }"
)
CONSEQUENCES_PER_REQUEST = 25


def _objects(value: Any, field: str) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ConnectorError(f"gnomAD response does not state a {field} list")
    return value


class OnlineGnomADClient:
    def __init__(self, timeout: float = 120.0) -> None:
        self.timeout = timeout

    def _ask(
        self, query: str, kind: str, identifier: str, variants: bool = True
    ) -> Dict[str, Any]:
        retrieval = stamp(SOURCE)
        body = json.dumps({"query": query, "variables": {kind: identifier}}).encode(
            "utf-8"
        )
        try:
            with urlopen(  # nosec - trusted endpoint
                request(API, data=body, headers={"Content-Type": "application/json"}),
                timeout=self.timeout,
                expect_json=True,
            ) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                note_response(
                    data, query={"query": query, "variables": {kind: identifier}}
                )
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            if isinstance(exc, HTTPError):
                exc.close()
            raise ConnectorError(f"gnomAD request failed: {exc}") from exc
        if not isinstance(data, dict):
            raise ConnectorError("gnomAD response does not state a GraphQL object")
        errors = data.get("errors")
        envelope = data.get("data")
        if errors:
            # Retain the source's explicit not-found error form, but never treat a
            # mixed error or a partial record as successful/absent knowledge.
            absent = envelope is None or (
                isinstance(envelope, dict)
                and kind in envelope
                and envelope[kind] is None
            )
            if (
                absent
                and isinstance(errors, list)
                and all(
                    isinstance(error, dict)
                    and "not found" in str(error.get("message", "")).lower()
                    for error in errors
                )
            ):
                note_completed(
                    {},
                    kind=kind,
                    absence="explicit_GraphQL_not_found_error; existing_client_message_policy",
                )
                raise RecordNotFoundError(f"gnomAD has no {kind} {identifier}")
            raise ConnectorError(f"gnomAD answered with errors: {errors}")
        if not isinstance(envelope, dict) or kind not in envelope:
            raise ConnectorError(f"gnomAD response does not answer {kind} {identifier}")
        found = envelope[kind]
        if found is None:
            note_completed({}, kind=kind, absence="explicit_null_GraphQL_entity")
            raise RecordNotFoundError(f"gnomAD has no {kind} {identifier}")
        if not isinstance(found, dict):
            raise ConnectorError(f"gnomAD response does not state a {kind} object")
        if not variants:
            return {"retrieved_at": retrieval.value, "record": found}
        listed = _objects(found.get("variants"), "variants")
        found.pop("variants")
        note_completed({kind: found, "variants": listed}, kind=kind)
        return {
            "retrieved_at": retrieval.value,
            "version": DATASET,
            "record": {kind: found, "variants": listed},
        }

    @observe("gnomad_variants")
    def variants(self, gene: str) -> Dict[str, Any]:
        return self._ask(QUERY, "gene", gene)

    @observe("gnomad_transcript_variants")
    def transcript_variants(self, transcript: str) -> Dict[str, Any]:
        return self._ask(TRANSCRIPT_QUERY, "transcript", transcript)

    @observe("gnomad_consequences")
    def consequences(self, variant_ids: Iterable[str]) -> Dict[str, Any]:
        """``{variant_id: [consequence on each transcript]}``; a variant gnomAD does not
        hold is left out."""
        wanted = sorted({v for v in variant_ids if v})
        retrieval = stamp(SOURCE)
        found: Dict[str, Any] = {}
        for i in range(0, len(wanted), CONSEQUENCES_PER_REQUEST):
            chunk = wanted[i : i + CONSEQUENCES_PER_REQUEST]
            parts = " ".join(
                f'v{n}: variant(variantId: "{v}", dataset: {DATASET}) '
                f"{{ {CONSEQUENCE_FIELDS} }}"
                for n, v in enumerate(chunk)
            )
            body = json.dumps({"query": f"query {{ {parts} }}"}).encode("utf-8")
            try:
                with urlopen(  # nosec - trusted endpoint
                    request(
                        API, data=body, headers={"Content-Type": "application/json"}
                    ),
                    timeout=self.timeout,
                    expect_json=True,
                ) as resp:
                    response = json.loads(resp.read().decode("utf-8"))
                    note_response(
                        response,
                        query={"query": f"query {{ {parts} }}", "variant_ids": chunk},
                    )
            except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                if isinstance(exc, HTTPError):
                    exc.close()
                raise ConnectorError(f"gnomAD request failed: {exc}") from exc
            if (
                not isinstance(response, dict)
                or response.get("errors")
                or not isinstance(response.get("data"), dict)
                or set(response["data"]) != {f"v{n}" for n in range(len(chunk))}
            ):
                raise ConnectorError(
                    "gnomAD response does not answer the consequence batch"
                )
            batch, absent, native_ids = {}, [], {}
            for n, identifier in enumerate(chunk):
                answer = response["data"][f"v{n}"]
                if answer is None:
                    absent.append(identifier)
                    continue
                if not isinstance(answer, dict):
                    raise ConnectorError(
                        "gnomAD response does not state a variant object"
                    )
                batch[identifier] = _objects(
                    answer.get("transcript_consequences"), "transcript consequences"
                )
                native_ids[identifier] = answer.get("variant_id")
            note_completed(
                batch,
                kind="consequences",
                absent_ids=absent,
                native_variant_ids=native_ids,
            )
            found.update(batch)
        return {"retrieved_at": retrieval.value, "version": DATASET, "record": found}

    @observe("gnomad_pext")
    def pext(self, gene: str) -> Dict[str, Any]:
        answer = self._ask(PEXT_QUERY, "gene", gene, variants=False)
        found = answer["record"]
        if "pext" not in found:
            raise ConnectorError("gnomAD response does not answer the pext query")
        pext = found.pop("pext")
        if pext is None:
            note_completed({}, kind="pext", absence="explicit_null_pext")
            raise RecordNotFoundError(f"gnomAD states no pext for gene {gene}")
        if not isinstance(pext, dict):
            raise ConnectorError("gnomAD response does not state a pext object")
        if not _objects(pext.get("regions"), "pext regions"):
            note_completed({}, kind="pext", absence="explicit_empty_pext_regions")
            raise RecordNotFoundError(f"gnomAD states no pext for gene {gene}")
        note_completed({"gene": found, "pext": pext}, kind="pext")
        return {
            "retrieved_at": answer["retrieved_at"],
            "version": PEXT_VERSION,
            "record": {"gene": found, "pext": pext},
        }


class FixtureGnomADClient:
    def __init__(
        self,
        directory: str | Path = "temp_data",
        retrieved_at: str = "fixture",
        failing: set[str] | None = None,
    ) -> None:
        self.directory = Path(directory) / "gnomad"
        self.retrieved_at = retrieved_at
        self.failing = set(failing or ())

    def _read(self, kind: str, identifier: str) -> Dict[str, Any]:
        if identifier in self.failing:
            raise ConnectorError(f"gnomAD request for {identifier} failed (simulated)")
        path = self.directory / f"{identifier}.json"
        if not path.is_file():
            raise missing_fixture(f"gnomAD fixture is unavailable: {identifier}")
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConnectorError(
                f"gnomAD fixture cannot be read: {identifier}"
            ) from exc
        note_response(saved, fixture=True)
        validate_fixture(saved, kind)
        note_completed(saved["record"], kind=kind, fixture_version=saved.get("version"))
        return {"retrieved_at": self.retrieved_at, **saved}

    @observe("gnomad_variants", fixture=True)
    def variants(self, gene: str) -> Dict[str, Any]:
        return self._read("gene", gene)

    @observe("gnomad_transcript_variants", fixture=True)
    def transcript_variants(self, transcript: str) -> Dict[str, Any]:
        return self._read("transcript", transcript)

    @observe("gnomad_pext", fixture=True)
    def pext(self, gene: str) -> Dict[str, Any]:
        return self._read("pext", f"pext_{gene}")

    @observe("gnomad_consequences", fixture=True)
    def consequences(self, variant_ids: Iterable[str]) -> Dict[str, Any]:
        path = self.directory / "consequences.json"
        if "consequences" in self.failing:
            raise ConnectorError("gnomAD request for consequences failed (simulated)")
        if not path.is_file():
            raise missing_fixture("gnomAD consequence fixture is unavailable")
        try:
            saved = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConnectorError("gnomAD consequence fixture cannot be read") from exc
        note_response(saved, fixture=True)
        validate_consequences(saved)
        selected = {v: saved[v] for v in variant_ids if v in saved}
        note_completed(
            saved,
            kind="consequences",
            absent_ids=[v for v in variant_ids if v not in saved],
        )
        return {
            "retrieved_at": self.retrieved_at,
            "version": DATASET,
            "record": selected,
        }


# --- Public source access (uibcdf/sabueso#49) -----------------------------------------


@arg_digest()
@capture_acquisitions
def get_variants(identifier: str, client: Any = None, skip_digestion: bool = False):
    """gnomAD's variants of a gene (an Ensembl gene id), with their frequencies."""
    response = online(client, OnlineGnomADClient).variants(identifier)
    return source_record(
        SOURCE,
        "variants",
        {"ensembl_gene": identifier, "dataset": DATASET},
        response.get("retrieved_at"),
        response.get("version"),
        response["record"],
    )


@arg_digest()
@capture_acquisitions
def get_transcript_variants(
    identifier: str, client: Any = None, skip_digestion: bool = False
):
    """gnomAD's variants of a transcript (an Ensembl transcript id), each with its
    consequence on that transcript, and their frequencies."""
    response = online(client, OnlineGnomADClient).transcript_variants(identifier)
    return source_record(
        SOURCE,
        "transcript_variants",
        {"ensembl_transcript": identifier, "dataset": DATASET},
        response.get("retrieved_at"),
        response.get("version"),
        response["record"],
    )


@arg_digest()
@capture_acquisitions
def get_pext(identifier: str, client: Any = None, skip_digestion: bool = False):
    """gnomAD's pext of a gene (an Ensembl gene id): per coding region, the share of the
    gene's expression in each GTEx v10 tissue that includes it (GRCh38)."""
    response = online(client, OnlineGnomADClient).pext(identifier)
    return source_record(
        SOURCE,
        "pext",
        {"ensembl_gene": identifier},
        response.get("retrieved_at"),
        response.get("version"),
        response["record"],
    )
