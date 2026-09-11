from hub.dataload.uploader import SnpeffPostUpdateUploader
from hub.dataload.sources.uniprot import uniprot_parser

class UniprotUploader(SnpeffPostUpdateUploader):

    name = "uniprot"
    __metadata__ = {
        "mapper" : 'observed',
        "assembly" : "hg38",
        "src_meta" : {
            "url" : "http://www.uniprot.org/",
            "license" : "CC BY 4.0",
            "license_url" : "http://www.uniprot.org/help/license",
            "license_url_short": "http://bit.ly/2RMp2Wa"
        }
    }

    def load_data(self, data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        return uniprot_parser.load_data(data_folder, logger=self.logger)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "uniprot": {
                "properties": {
                    "gene_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "swiss_prot_ac": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "aa_change": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "source_db_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "consequence_type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "clinical_significance": {
                        "type": "text",
                    },
                    "phenotype_disease": {
                        "type": "text",
                    },
                    "phenotype_disease_source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "cytogenetic_band": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "ensembl_gene_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "ensembl_transcript_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "ensembl_translation_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "evidence": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "humsavar": {
                        "properties": {
                            "gene_name": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "swiss_prot_ac": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "ftid": {
                                "copy_to" : ["all"],
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "aa_change": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "type_of_variant": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "disease_name": {
                                "type": "text",
                            }
                        }
                    }
                }
            }
        }
        return mapping
