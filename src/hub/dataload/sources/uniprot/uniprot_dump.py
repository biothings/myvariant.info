import os

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper


class UniprotDumper(LastModifiedHTTPDumper):
    """
    Downloads the UniProtKB "current_release" variant files backing the
    'uniprot' myvariant.info source (see UniprotUploader.get_mapping()):

      - humsavar.txt: manually curated human missense variants (Swiss-Prot AC,
        FTId, ACMG/AMP-style variant category, disease name), used to populate
        the 'humsavar' sub-fields.
      - homo_sapiens_variation.txt.gz: protein-altering variants imported from
        Ensembl Variation/dbSNP/ClinVar/COSMIC, one row per variant per
        transcript/phenotype. Used to populate 'source_db_id',
        'clinical_significance', 'phenotype_disease' and
        'phenotype_disease_source'.

    Both files live at a stable URL that UniProt updates in place with each
    release, so there's no version-specific filename to look for; the release
    is tracked from the HTTP Last-Modified header instead.
    """

    SRC_NAME = "uniprot"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = [
        "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/variants/humsavar.txt",
        "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/variants/homo_sapiens_variation.txt.gz",
    ]

    SCHEDULE = "0 9 * * *"
