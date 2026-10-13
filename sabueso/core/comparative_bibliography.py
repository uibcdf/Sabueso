"""Verified offline resource/method descriptions; no entry or release inference.

Provider declarations and primary bibliographic metadata, checked 2026-10-13,
are linked in devguide/pending_proposals/comparative_bibliography.md.
These descriptions never establish a queried row's study or method revision.
"""

from copy import deepcopy

GNOMAD = {
    "id": "doi:10.1038/s41586-023-06045-0",
    "type": "article",
    "title": "A genomic mutational constraint map using variation in 76,156 human genomes",
    "authors": [
        "Chen, Siwei",
        "Francioli, Laurent C",
        "Goodrich, Julia K",
        "Collins, Ryan L",
        "Kanai, Masahiro",
        "Wang, Qingbo",
        "Alföldi, Jessica",
        "Watts, Nicholas A",
        "Vittal, Christopher",
        "Gauthier, Laura D",
        "Poterba, Timothy",
        "Wilson, Michael W",
        "Tarasova, Yekaterina",
        "Phu, William",
        "Grant, Riley",
        "Yohannes, Mary T",
        "Koenig, Zan",
        "Farjoun, Yossi",
        "Banks, Eric",
        "Donnelly, Stacey",
        "Gabriel, Stacey",
        "Gupta, Namrata",
        "Ferriera, Steven",
        "Tolonen, Charlotte",
        "Novod, Sam",
        "Bergelson, Louis",
        "Roazen, David",
        "Ruano-Rubio, Valentin",
        "Covarrubias, Miguel",
        "Llanwarne, Christopher",
        "Petrillo, Nikelle",
        "Wade, Gordon",
        "Jeandet, Thibault",
        "Munshi, Ruchi",
        "Tibbetts, Kathleen",
        {"literal": "Genome Aggregation Database Consortium"},
        "O'Donnell-Luria, Anne",
        "Solomonson, Matthew",
        "Seed, Cotton",
        "Martin, Alicia R",
        "Talkowski, Michael E",
        "Rehm, Heidi L",
        "Daly, Mark J",
        "Tiao, Grace",
        "Neale, Benjamin M",
        "MacArthur, Daniel G",
        "Karczewski, Konrad J",
    ],
    "year": 2024,
    "journal": "Nature",
    "volume": "625",
    "number": "7993",
    "pages": "92-100",
    "doi": "10.1038/s41586-023-06045-0",
    "url": "https://doi.org/10.1038/s41586-023-06045-0",
    "note": "Provider-recommended flagship resource description; published online 2023-12-06, journal issue 2024. Author correction: doi:10.1038/s41586-024-07050-7. Not proof of a queried release or entry's study.",
}
GTEX = {
    "id": "doi:10.1126/science.aaz1776",
    "type": "article",
    "title": "The GTEx Consortium atlas of genetic regulatory effects across human tissues",
    "authors": [{"literal": "GTEx Consortium"}],
    "year": 2020,
    "journal": "Science",
    "volume": "369",
    "number": "6509",
    "pages": "1318-1330",
    "doi": "10.1126/science.aaz1776",
    "url": "https://doi.org/10.1126/science.aaz1776",
    "note": "GTEx Consortium resource description (v8 analyses); not a declaration of the revision or study underlying a queried tissue row or later dataset.",
}
PEXT = {
    "id": "doi:10.1038/s41586-020-2329-2",
    "type": "article",
    "title": "Transcript expression-aware annotation improves rare variant interpretation",
    "authors": [
        "Cummings, Beryl B",
        "Karczewski, Konrad J",
        "Kosmicki, Jack A",
        "Seaby, Eleanor G",
        "Watts, Nicholas A",
        "Singer-Berk, Moriel",
        "Mudge, Jonathan M",
        "Karjalainen, Juha",
        "Satterstrom, F Kyle",
        "O'Donnell-Luria, Anne H",
        "Poterba, Timothy",
        "Seed, Cotton",
        "Solomonson, Matthew",
        "Alföldi, Jessica",
        {"literal": "Genome Aggregation Database Production Team"},
        {"literal": "Genome Aggregation Database Consortium"},
        "Daly, Mark J",
        "MacArthur, Daniel G",
    ],
    "year": 2020,
    "journal": "Nature",
    "volume": "581",
    "number": "7809",
    "pages": "452-458",
    "doi": "10.1038/s41586-020-2329-2",
    "url": "https://doi.org/10.1038/s41586-020-2329-2",
    "note": "Description of upstream pext methodology (original study uses GTEx v7); reuse of supplied annotations does not execute that method or prove a row's implementation/dataset revision or study membership.",
}


def resource_descriptions(source):
    """Resource-level background, independent of native release/entry claims."""
    item = {"gnomAD": GNOMAD, "GTEx": GTEX}.get(source)
    return deepcopy([item] if item else [])


def method_descriptions(source, *, operation=None, field_path=None):
    """Scope the upstream pext description to the actual access or stored input."""
    if source != "gnomAD" or not (
        operation == "gnomad_pext" or field_path == "annotations.exon_usage_by_tissue"
    ):
        return [], None
    return deepcopy([PEXT]), {
        "rule": "pext_reference_scope@1",
        "source": source,
        "operation": operation,
        "field_path": field_path,
        "basis": "verified_offline_description_of_upstream_annotation_method",
        "method_execution": "not_performed",
        "native_method_revision": {"value": None, "basis": "not_stated"},
        "native_dataset_revision_binding": "not_inferred",
        "entry_publication_membership": "not_established",
    }
