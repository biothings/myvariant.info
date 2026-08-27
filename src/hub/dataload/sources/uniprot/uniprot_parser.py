"""
Loads humsavar.txt and homo_sapiens_variation.txt.gz as-is into 'uniprot'
documents: one document per line in either file, verbatim. There is no
deduplication, no merging of rows, and no correlation between the two files
-- each line becomes its own independent document, identified by a random id
(not a computed/genomic one).

Every document needs an explicit "_id" here, even though its value carries
no meaning: this project's MyVariantBasicStorage (see
hub/dataload/storage.py) always looks at doc["_id"] before insert, to check
whether it's a genomic HGVS id long enough to need shortening. Leaving "_id"
unset (to let MongoDB assign one on insert) makes that lookup raise
AssertionError for every document, since it runs before the insert ever
happens.

Column names already used elsewhere in this mapping are reused
(source_db_id, clinical_significance, phenotype_disease,
phenotype_disease_source, swiss_prot_ac, ftid, type_of_variant,
disease_name); every other column is stored under a name derived from its
own header (see _HUMSAVAR_FIELDS / _VARIATION_FIELDS below).
"""
import glob
import gzip
import os
import uuid

HUMSAVAR_FILE = "humsavar.txt"
VARIATION_FILE_GLOB = "homo_sapiens_variation.txt.gz"

# humsavar.txt columns, in file order: Main gene name | Swiss-Prot AC | FTId |
# AA change | Variant category | dbSNP | Disease name
_HUMSAVAR_FIELDS = [
    "gene_name", "swiss_prot_ac", "ftid", "aa_change", "type_of_variant", "dbsnp", "disease_name",
]

# homo_sapiens_variation.txt.gz columns, in file order: Gene Name | AC |
# Variant AA Change | Source DB ID | Consequence Type | Clinical
# Significance | Phenotype/Disease | Phenotype/Disease Source | Cytogenetic
# Band | Chromosome Coordinate | Ensembl gene ID | Ensembl transcript ID |
# Ensembl translation ID | Evidence
_VARIATION_FIELDS = [
    "gene_name", "swiss_prot_ac", "aa_change", "source_db_id", "consequence_type",
    "clinical_significance", "phenotype_disease", "phenotype_disease_source",
    "cytogenetic_band", "chromosome_coordinate", "ensembl_gene_id",
    "ensembl_transcript_id", "ensembl_translation_id", "evidence",
]


def parse_humsavar(lines):
    """Yield one {"uniprot": {...}} document per humsavar.txt data line,
    verbatim, skipping the multi-line preamble/header."""
    started = False
    for line in lines:
        if line.startswith("_________"):
            started = True
            continue
        if not started:
            continue
        line = line.rstrip("\n")
        if not line.strip():
            continue
        values = line.split(None, 6)
        if len(values) < 6:
            continue
        if len(values) == 6:
            values.append("-")
        yield {"_id": uuid.uuid4().hex, "uniprot": dict(zip(_HUMSAVAR_FIELDS, values))}


def parse_variation(lines):
    """Yield one {"uniprot": {...}} document per homo_sapiens_variation.txt
    data line, verbatim, skipping the multi-line preamble/header."""
    started = False
    for line in lines:
        if line.startswith("___________"):
            started = True
            continue
        if not started:
            continue
        line = line.rstrip("\n")
        if not line:
            continue
        values = line.split("\t")
        if len(values) < len(_VARIATION_FIELDS):
            continue
        yield {"_id": uuid.uuid4().hex, "uniprot": dict(zip(_VARIATION_FIELDS, values))}


def load_data(data_folder, logger=None):
    humsavar_file = os.path.join(data_folder, HUMSAVAR_FILE)
    variation_files = glob.glob(os.path.join(data_folder, VARIATION_FILE_GLOB))
    assert len(variation_files) == 1, "Expecting exactly one file matching '%s', got: %s" % (
        VARIATION_FILE_GLOB, variation_files)
    variation_file = variation_files[0]

    if logger:
        logger.info("Loading '%s'" % HUMSAVAR_FILE)
    with open(humsavar_file, encoding="utf-8", errors="replace") as f:
        yield from parse_humsavar(f)

    if logger:
        logger.info("Loading '%s'" % VARIATION_FILE_GLOB)
    with gzip.open(variation_file, "rt", encoding="utf-8", errors="replace") as f:
        yield from parse_variation(f)
