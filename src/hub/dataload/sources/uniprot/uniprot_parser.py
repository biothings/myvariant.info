"""
Parses the two UniProtKB variant files (see uniprot_dump.py for how they're
fetched) into 'uniprot' myvariant.info documents:

  - humsavar.txt: manually curated missense variants. This drives which
    variants end up in this source -- every output document corresponds to
    exactly one humsavar.txt record.
  - homo_sapiens_variation.txt.gz: bulk protein-altering variant index (59M+
    rows, mostly dbSNP/ClinVar-sourced). humsavar.txt has no genomic
    coordinate of its own (only a dbSNP id), so this file is used purely to
    look up that coordinate and to enrich the record with whatever
    'source_db_id' / 'clinical_significance' / 'phenotype_disease' /
    'phenotype_disease_source' values UniProt reports at that genomic
    position -- not just the one dbSNP id humsavar happens to reference, but
    every source (rs, RCV, or anything else) sharing that same coordinate.

humsavar.txt records with no dbSNP id, or whose dbSNP id can't be found in
homo_sapiens_variation.txt.gz, are skipped: without a genomic coordinate there
is no way to build the 'chrN:g.posREF>ALT' _id myvariant.info requires.
"""
import glob
import gzip
import logging
import os

from biothings.utils.dataload import unlist

HUMSAVAR_FILE = "humsavar.txt"
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


def _parse_humsavar_line(line):
    """
    Parse one humsavar.txt data line (fixed-width/whitespace separated, NOT
    tab-delimited):
        A1BG        P04217     VAR_018369  p.His52Arg     LB/B     rs893184       -
    Columns: gene name, Swiss-Prot AC, FTId, AA change, variant category,
    dbSNP id, disease name (free text, may itself contain spaces).
    Returns None for blank/malformed lines.
    """
    line = line.rstrip("\n")
    if not line.strip():
        return None
    parts = line.split(None, 6)
    if len(parts) < 6:
        return None
    _gene_name, swiss_prot_ac, ftid, _aa_change, type_of_variant, dbsnp_id = parts[:6]
    disease_name = parts[6] if len(parts) == 7 else "-"
    return {
        "swiss_prot_ac": swiss_prot_ac,
        "ftid": ftid,
        "type_of_variant": type_of_variant,
        "dbsnp_id": None if dbsnp_id == "-" else dbsnp_id,
        "disease_name": None if disease_name == "-" else disease_name,
    }


def parse_humsavar(lines):
    """Parse humsavar.txt content (an iterable of lines), skipping the
    multi-line preamble/header. Yields one dict per data row."""
    started = False
    for line in lines:
        if line.startswith("_________"):
            started = True
            continue
        if not started:
            continue
        row = _parse_humsavar_line(line)
        if row:
            yield row


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


def build_variation_index(iter_rows_factory, needed_dbsnp_ids):
    """
    Two-pass scan over the (huge) variation file, via `iter_rows_factory`: a
    zero-arg callable returning a fresh iterator of parsed variation rows
    (as produced by parse_variation()) each time it's called, since this
    needs to scan the rows twice without holding all of them in memory.

    Pass 1 finds the genomic coordinate for each dbSNP id in
    `needed_dbsnp_ids`. Pass 2 collects every row sharing one of those
    coordinates -- regardless of that row's own source_db_id -- so a
    variant's enrichment fields reflect everything UniProt reports at that
    genomic position, not just the one dbSNP id that happened to link it to
    humsavar.

    Returns (dbsnp_to_coordinate, coordinate_info):
      - dbsnp_to_coordinate: {dbsnp_id: coordinate}
      - coordinate_info: {coordinate: {"source_db_id": set(), "clinical_significance": set(),
                                        "phenotype_disease": set(), "phenotype_disease_source": set()}}
    """
    remaining = set(needed_dbsnp_ids)
    dbsnp_to_coordinate = {}
    for row in iter_rows_factory():
        if not remaining:
            break
        if row["source_db_id"] in remaining:
            dbsnp_to_coordinate[row["source_db_id"]] = row["coordinate"]
            remaining.discard(row["source_db_id"])

    relevant_coordinates = set(dbsnp_to_coordinate.values())
    coordinate_info = {}
    for row in iter_rows_factory():
        coordinate = row["coordinate"]
        if coordinate not in relevant_coordinates:
            continue
        info = coordinate_info.setdefault(coordinate, {
            "source_db_id": set(),
            "clinical_significance": set(),
            "phenotype_disease": set(),
            "phenotype_disease_source": set(),
        })
        info["source_db_id"].add(row["source_db_id"])
        for key in ("clinical_significance", "phenotype_disease", "phenotype_disease_source"):
            value = row[key]
            if value and value != "-":
                info[key].add(value)

    return dbsnp_to_coordinate, coordinate_info


def build_docs(humsavar_rows, dbsnp_to_coordinate, coordinate_info):
    """
    Yield one 'uniprot' document per humsavar row that could be resolved to a
    genomic coordinate. Rows with no dbSNP id, or whose dbSNP id has no match
    in the variation file, are skipped.
    """
    for row in humsavar_rows:
        if not row["dbsnp_id"]:
            continue
        coordinate = dbsnp_to_coordinate.get(row["dbsnp_id"])
        if not coordinate:
            continue
        _id = nc_coordinate_to_hgvs_id(coordinate)
        if not _id:
            continue

        humsavar = {
            "swiss_prot_ac": row["swiss_prot_ac"],
            "ftid": row["ftid"],
            "type_of_variant": row["type_of_variant"],
        }
        if row["disease_name"]:
            humsavar["disease_name"] = row["disease_name"]

        doc = {"_id": _id, "uniprot": {"humsavar": humsavar}}
        info = coordinate_info.get(coordinate, {})
        for key in ("source_db_id", "clinical_significance", "phenotype_disease", "phenotype_disease_source"):
            values = info.get(key)
            if values:
                doc["uniprot"][key] = sorted(values)

        yield unlist(doc)


def load_data(data_folder, logger=None):
    logger = logger or logging.getLogger(__name__)

    humsavar_file = os.path.join(data_folder, HUMSAVAR_FILE)
    variation_files = glob.glob(os.path.join(data_folder, VARIATION_FILE_GLOB))
    assert len(variation_files) == 1, "Expecting exactly one file matching '%s', got: %s" % (
        VARIATION_FILE_GLOB, variation_files)
    variation_file = variation_files[0]

    with open(humsavar_file, encoding="utf-8", errors="replace") as f:
        humsavar_rows = list(parse_humsavar(f))
    needed_dbsnp_ids = {row["dbsnp_id"] for row in humsavar_rows if row["dbsnp_id"]}
    logger.info("Parsed %d humsavar.txt records (%d with a dbSNP id to resolve)" %
                (len(humsavar_rows), len(needed_dbsnp_ids)))

    def _iter_variation_file():
        f = gzip.open(variation_file, "rt", encoding="utf-8", errors="replace")
        try:
            yield from parse_variation(f)
        finally:
            f.close()

    dbsnp_to_coordinate, coordinate_info = build_variation_index(_iter_variation_file, needed_dbsnp_ids)
    logger.info("Resolved %d/%d dbSNP ids to a genomic coordinate in '%s'" %
                (len(dbsnp_to_coordinate), len(needed_dbsnp_ids), VARIATION_FILE_GLOB))

    docs = list(build_docs(humsavar_rows, dbsnp_to_coordinate, coordinate_info))
    logger.info("Built %d uniprot documents (%d humsavar records skipped: no dbSNP id or unresolved)" %
                (len(docs), len(humsavar_rows) - len(docs)))
    return docs
