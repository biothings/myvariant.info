"""
Parses the two UniProtKB variant files (see uniprot_dump.py for how they're
fetched) into 'uniprot' myvariant.info documents, loading ALL columns from
BOTH files and connecting records that relate to each other:

  - homo_sapiens_variation.txt.gz: bulk protein-altering variant index (59M+
    rows, mostly dbSNP/ClinVar-sourced). Every unique genomic coordinate
    found here becomes one output document, populated with every column
    UniProt reports at that position -- gene name, AC, AA change, source_db_id,
    consequence_type, clinical_significance, phenotype_disease,
    phenotype_disease_source, cytogenetic_band, and the Ensembl gene/
    transcript/translation ids and evidence sources -- aggregated across
    every row sharing the coordinate (e.g. multiple Ensembl transcripts, or
    multiple sources like rs/RCV at one position), not just one row.
  - humsavar.txt: manually curated missense variants, ~85K records, with
    gene name, Swiss-Prot AC, FTId, AA change, variant category, and disease
    name. It has no genomic coordinate of its own (only a dbSNP id). When a
    record's dbSNP id matches one of a coordinate's source_db_id values, its
    fields are attached to that coordinate's document -- so some documents
    end up with data from both files. When a record's dbSNP id doesn't match
    anything in the variation file (or it has no dbSNP id at all -- about
    17% of humsavar.txt), it still becomes its own standalone document
    (humsavar-only, no genomic coordinate to derive a real _id from, so it
    gets a random one instead) rather than being dropped: every humsavar
    record ends up as a document somewhere, matched or not.

Variation-file rows whose 'Chromosome Coordinate' isn't a recognized GRCh38
chromosome accession are skipped: without a genomic coordinate there is no
way to build the 'chrN:g.posREF>ALT' _id myvariant.info uses elsewhere.
"""
import glob
import gzip
import logging
import os
import uuid

from biothings.utils.dataload import unlist

HUMSAVAR_FILE = "humsavar.txt"
VARIATION_FILE_GLOB = "homo_sapiens_variation.txt.gz"

# GRCh38 RefSeq chromosome accession prefix (before the version suffix) ->
# myvariant.info chromosome name.
_NC_TO_CHROM = {("NC_%06d" % i): str(i) for i in range(1, 23)}
_NC_TO_CHROM["NC_000023"] = "X"
_NC_TO_CHROM["NC_000024"] = "Y"
_NC_TO_CHROM["NC_012920"] = "MT"

# homo_sapiens_variation.txt.gz columns that get aggregated (unioned as a set
# per coordinate, since multiple rows -- e.g. different Ensembl transcripts --
# can share the same coordinate). source_db_id is aggregated the same way but
# handled separately below since, unlike these, it's never a '-' placeholder.
_VARIATION_SET_FIELDS = (
    "gene_name", "swiss_prot_ac", "aa_change", "consequence_type",
    "clinical_significance", "phenotype_disease", "phenotype_disease_source",
    "cytogenetic_band", "ensembl_gene_id", "ensembl_transcript_id",
    "ensembl_translation_id", "evidence",
)
_ALL_VARIATION_FIELDS = ("source_db_id",) + _VARIATION_SET_FIELDS


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
    gene_name, swiss_prot_ac, ftid, aa_change, type_of_variant, dbsnp_id = parts[:6]
    disease_name = parts[6] if len(parts) == 7 else "-"
    return {
        "gene_name": gene_name,
        "swiss_prot_ac": swiss_prot_ac,
        "ftid": ftid,
        "aa_change": aa_change,
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
    columns): Gene Name, AC, Variant AA Change, Source DB ID, Consequence
    Type, Clinical Significance, Phenotype/Disease, Phenotype/Disease
    Source, Cytogenetic Band, Chromosome Coordinate, Ensembl gene ID,
    Ensembl transcript ID, Ensembl translation ID, Evidence.
    Returns None for blank/malformed lines.
    """
    line = line.rstrip("\n")
    if not line:
        return None
    cols = line.split("\t")
    if len(cols) < 14:
        return None
    return {
        "gene_name": cols[0],
        "swiss_prot_ac": cols[1],
        "aa_change": cols[2],
        "source_db_id": cols[3],
        "consequence_type": cols[4],
        "clinical_significance": cols[5],
        "phenotype_disease": cols[6],
        "phenotype_disease_source": cols[7],
        "cytogenetic_band": cols[8],
        "coordinate": cols[9],
        "ensembl_gene_id": cols[10],
        "ensembl_transcript_id": cols[11],
        "ensembl_translation_id": cols[12],
        "evidence": cols[13],
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
    every coordinate found here ends up as an output document. Every column
    is aggregated as a set (source_db_id unconditionally; the rest skip '-'
    placeholder values), since multiple rows -- e.g. different Ensembl
    transcripts -- can share the same coordinate with different values.

    Returns {coordinate: {field: set(), ...}} with one set per field in
    _ALL_VARIATION_FIELDS.
    """
    coordinate_info = {}
    for row in rows:
        coordinate = row["coordinate"]
        info = coordinate_info.get(coordinate)
        if info is None:
            info = {key: set() for key in _ALL_VARIATION_FIELDS}
            coordinate_info[coordinate] = info
        info["source_db_id"].add(row["source_db_id"])
        for key in _VARIATION_SET_FIELDS:
            value = row[key]
            if value and value != "-":
                info[key].add(value)
    return coordinate_info


def build_humsavar_index(humsavar_rows):
    """
    {dbsnp_id: [humsavar_row, ...]} -- a dbSNP id can be shared by more than
    one humsavar record (real case: ABCA1's VAR_009147 and VAR_062487 both
    cite rs137854496, an un-cleaned-up UniProt curation duplicate), so each
    dbSNP id maps to a list rather than a single record. Rows with no dbSNP
    id at all aren't included here -- they can never match a coordinate, so
    build_docs() handles them separately, as standalone documents.
    """
    index = {}
    for row in humsavar_rows:
        if not row["dbsnp_id"]:
            continue
        index.setdefault(row["dbsnp_id"], []).append(row)
    return index


def _humsavar_record(row):
    record = {
        "gene_name": row["gene_name"],
        "swiss_prot_ac": row["swiss_prot_ac"],
        "ftid": row["ftid"],
        "aa_change": row["aa_change"],
        "type_of_variant": row["type_of_variant"],
    }
    if row["disease_name"]:
        record["disease_name"] = row["disease_name"]
    return record


def build_docs(coordinate_info, humsavar_rows):
    """
    Yield one document per genomic coordinate in coordinate_info (i.e. per
    unique coordinate found in homo_sapiens_variation.txt.gz), 'humsavar'
    attached whenever one of that coordinate's source_db_id values matches a
    dbSNP id in humsavar_rows -- these are the documents with data from both
    files.

    Then yield one standalone document for every humsavar_rows record that
    never got attached to a coordinate this way (no dbSNP id at all, or a
    dbSNP id that never appears in homo_sapiens_variation.txt.gz) -- every
    humsavar record must end up as a document somewhere. These get a random
    _id (a uuid4 hex string), since there's no genomic coordinate to derive
    a real one from.
    """
    humsavar_index = build_humsavar_index(humsavar_rows)
    used_ftids = set()

    for coordinate, info in coordinate_info.items():
        _id = nc_coordinate_to_hgvs_id(coordinate)
        if not _id:
            continue

        doc = {"_id": _id, "uniprot": {}}
        for key in _ALL_VARIATION_FIELDS:
            values = info.get(key)
            if values:
                doc["uniprot"][key] = sorted(values)

        matched = {}
        for source_id in info["source_db_id"]:
            for row in humsavar_index.get(source_id, []):
                matched[row["ftid"]] = row
        if matched:
            used_ftids.update(matched)
            records = [_humsavar_record(row) for row in matched.values()]
            doc["uniprot"]["humsavar"] = records[0] if len(records) == 1 else records

        yield unlist(doc)

    for row in humsavar_rows:
        if row["ftid"] in used_ftids:
            continue
        yield {"_id": uuid.uuid4().hex, "uniprot": {"humsavar": _humsavar_record(row)}}


def merge_docs(docs):
    """
    Two distinct raw 'Chromosome Coordinate' strings can normalize to the
    same _id (e.g. differing only by RefSeq patch version), so build_docs()
    can still yield more than one document for the same _id even though it
    iterates coordinate_info's already-unique keys. Storage does a plain
    insert (not an upsert), so two documents with the same _id would crash
    the whole batch with a MongoDB duplicate key error. (Standalone
    humsavar-only documents use a random _id, so they never collide here.)

    Groups by _id and merges each group into a single document: when more
    than one distinct humsavar record ends up attached to the same _id,
    'humsavar' becomes a list of records (as build_docs() already does for
    multiple matches within one coordinate) and the enrichment fields are
    unioned across all colliding rows.
    """
    grouped = {}
    for doc in docs:
        grouped.setdefault(doc["_id"], []).append(doc)

    for _id, group in grouped.items():
        if len(group) == 1:
            yield group[0]
            continue

        merged = {"_id": _id, "uniprot": {}}

        humsavar_by_ftid = {}
        for d in group:
            humsavar = d["uniprot"].get("humsavar")
            if humsavar is None:
                continue
            records = humsavar if isinstance(humsavar, list) else [humsavar]
            for record in records:
                humsavar_by_ftid[record["ftid"]] = record
        if humsavar_by_ftid:
            records = list(humsavar_by_ftid.values())
            merged["uniprot"]["humsavar"] = records[0] if len(records) == 1 else records

        for key in _ALL_VARIATION_FIELDS:
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

    humsavar_file = os.path.join(data_folder, HUMSAVAR_FILE)
    variation_files = glob.glob(os.path.join(data_folder, VARIATION_FILE_GLOB))
    assert len(variation_files) == 1, "Expecting exactly one file matching '%s', got: %s" % (
        VARIATION_FILE_GLOB, variation_files)
    variation_file = variation_files[0]

    with open(humsavar_file, encoding="utf-8", errors="replace") as f:
        humsavar_rows = list(parse_humsavar(f))
    logger.info("Parsed %d humsavar.txt records" % len(humsavar_rows))

    with gzip.open(variation_file, "rt", encoding="utf-8", errors="replace") as f:
        coordinate_info = build_variation_aggregate(parse_variation(f))
    logger.info("Aggregated %d unique genomic coordinates from '%s'" %
                (len(coordinate_info), VARIATION_FILE_GLOB))

    raw_docs = list(build_docs(coordinate_info, humsavar_rows))
    with_humsavar = sum(1 for d in raw_docs if "humsavar" in d["uniprot"])
    standalone_humsavar = sum(1 for d in raw_docs if set(d["uniprot"].keys()) == {"humsavar"})
    logger.info("Built %d documents (%d with a humsavar match, %d humsavar-only with no genomic match)" %
                (len(raw_docs), with_humsavar, standalone_humsavar))

    docs = list(merge_docs(raw_docs))
    if len(docs) != len(raw_docs):
        logger.info("Merged %d colliding documents sharing an _id down to %d" %
                    (len(raw_docs), len(docs)))
    return docs
