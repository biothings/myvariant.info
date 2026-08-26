"""
Parses homo_sapiens_variation.txt.gz (see uniprot_dump.py for how it's
fetched) into 'uniprot' myvariant.info documents.

homo_sapiens_variation.txt.gz is a bulk protein-altering variant index (59M+
rows, mostly dbSNP/ClinVar-sourced, one row per variant per Ensembl
transcript/phenotype). Every unique genomic coordinate found in it becomes
one output document, populated with whatever 'source_db_id' /
'clinical_significance' / 'phenotype_disease' / 'phenotype_disease_source'
values UniProt reports at that position -- every source sharing the
coordinate (rs, RCV, or anything else), not just one.

Rows whose 'Chromosome Coordinate' isn't a recognized GRCh38 chromosome
accession are skipped: without a genomic coordinate there is no way to build
the 'chrN:g.posREF>ALT' _id myvariant.info requires.
"""
import glob
import gzip
import logging
import os

from biothings.utils.dataload import unlist

VARIATION_FILE_GLOB = "homo_sapiens_variation.txt.gz"

# GRCh38 RefSeq chromosome accession prefix (before the version suffix) ->
# myvariant.info chromosome name.
_NC_TO_CHROM = {("NC_%06d" % i): str(i) for i in range(1, 23)}
_NC_TO_CHROM["NC_000023"] = "X"
_NC_TO_CHROM["NC_000024"] = "Y"
_NC_TO_CHROM["NC_012920"] = "MT"


def nc_coordinate_to_hgvs_id(coordinate):
    """
    Convert a UniProt 'Chromosome Coordinate' value, e.g.
    'NC_000017.11:g.30178149A>G', into a myvariant.info _id, e.g.
    'chr17:g.30178149A>G'. Returns None if the accession isn't a recognized
    GRCh38 chromosome accession.
    """
    accession, sep, rest = coordinate.partition(":")
    if not sep:
        return None
    prefix = accession.split(".")[0]
    chrom = _NC_TO_CHROM.get(prefix)
    if not chrom:
        return None
    return "chr%s:%s" % (chrom, rest)


def _parse_variation_line(line):
    """
    Parse one homo_sapiens_variation.txt data line (tab-delimited, 14
    columns; see the file's own header for the full column list). Returns
    None for blank/malformed lines.
    """
    line = line.rstrip("\n")
    if not line:
        return None
    cols = line.split("\t")
    if len(cols) < 10:
        return None
    return {
        "source_db_id": cols[3],
        "clinical_significance": cols[5],
        "phenotype_disease": cols[6],
        "phenotype_disease_source": cols[7],
        "coordinate": cols[9],
    }


def parse_variation(lines):
    """Parse homo_sapiens_variation.txt(.gz) content (an iterable of lines),
    skipping the multi-line preamble/header. Yields one dict per data row."""
    started = False
    for line in lines:
        if line.startswith("___________"):
            started = True
            continue
        if not started:
            continue
        row = _parse_variation_line(line)
        if row:
            yield row


def build_variation_aggregate(rows):
    """
    Single pass over ALL homo_sapiens_variation.txt(.gz) rows (as produced by
    parse_variation()), aggregating every row by its genomic coordinate --
    every coordinate found here ends up as an output document.

    Returns {coordinate: {"source_db_id": set(), "clinical_significance": set(),
                           "phenotype_disease": set(), "phenotype_disease_source": set()}}
    """
    coordinate_info = {}
    for row in rows:
        coordinate = row["coordinate"]
        info = coordinate_info.get(coordinate)
        if info is None:
            info = {
                "source_db_id": set(),
                "clinical_significance": set(),
                "phenotype_disease": set(),
                "phenotype_disease_source": set(),
            }
            coordinate_info[coordinate] = info
        info["source_db_id"].add(row["source_db_id"])
        for key in ("clinical_significance", "phenotype_disease", "phenotype_disease_source"):
            value = row[key]
            if value and value != "-":
                info[key].add(value)
    return coordinate_info


def build_docs(coordinate_info):
    """
    Yield one 'uniprot' document per genomic coordinate in coordinate_info
    (i.e. per unique coordinate found in homo_sapiens_variation.txt.gz).
    """
    for coordinate, info in coordinate_info.items():
        _id = nc_coordinate_to_hgvs_id(coordinate)
        if not _id:
            continue

        doc = {"_id": _id, "uniprot": {}}
        for key in ("source_db_id", "clinical_significance", "phenotype_disease", "phenotype_disease_source"):
            values = info.get(key)
            if values:
                doc["uniprot"][key] = sorted(values)

        yield unlist(doc)


def merge_docs(docs):
    """
    Two distinct raw 'Chromosome Coordinate' strings can normalize to the
    same _id (e.g. differing only by RefSeq patch version), so build_docs()
    can still yield more than one document for the same _id even though it
    iterates coordinate_info's already-unique keys. Storage does a plain
    insert (not an upsert), so two documents with the same _id would crash
    the whole batch with a MongoDB duplicate key error.

    Groups by _id and merges each group into a single document, unioning the
    enrichment fields across all colliding rows.
    """
    grouped = {}
    for doc in docs:
        grouped.setdefault(doc["_id"], []).append(doc)

    for _id, group in grouped.items():
        if len(group) == 1:
            yield group[0]
            continue

        merged = {"_id": _id, "uniprot": {}}
        for key in ("source_db_id", "clinical_significance", "phenotype_disease", "phenotype_disease_source"):
            values = set()
            for d in group:
                value = d["uniprot"].get(key)
                if value is None:
                    continue
                values.update(value) if isinstance(value, list) else values.add(value)
            if values:
                merged["uniprot"][key] = sorted(values)
        yield unlist(merged)


def load_data(data_folder, logger=None):
    logger = logger or logging.getLogger(__name__)

    variation_files = glob.glob(os.path.join(data_folder, VARIATION_FILE_GLOB))
    assert len(variation_files) == 1, "Expecting exactly one file matching '%s', got: %s" % (
        VARIATION_FILE_GLOB, variation_files)
    variation_file = variation_files[0]

    with gzip.open(variation_file, "rt", encoding="utf-8", errors="replace") as f:
        coordinate_info = build_variation_aggregate(parse_variation(f))
    logger.info("Aggregated %d unique genomic coordinates from '%s'" %
                (len(coordinate_info), VARIATION_FILE_GLOB))

    raw_docs = list(build_docs(coordinate_info))
    logger.info("Built %d uniprot documents" % len(raw_docs))

    docs = list(merge_docs(raw_docs))
    if len(docs) != len(raw_docs):
        logger.info("Merged %d colliding documents sharing an _id down to %d" %
                    (len(raw_docs), len(docs)))
    return docs
