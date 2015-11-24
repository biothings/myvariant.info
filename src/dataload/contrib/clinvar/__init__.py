# -*- coding: utf-8 -*-
__METADATA__ = {
    "src_name": 'clinvar',
    "src_url": 'ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/',
    "release": '2015-11',
    "field": 'clinvar'
}

def get_mapping():
    mapping = {
        "clinvar": {
            "properties": {
                "hg19": {
                    "properties": {
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
                "chrom": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "gene": {
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "id": {
                            "type": "long"
                        }
                    }
                },
                "type": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "rsid": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "rcv": {
                    "type": "nested",
                    "properties": {
                        "accession": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "clinical_significance": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "number_submitters": {
                            "type": "byte"
                        },
                        "review_status": {
                            "type": "string"
                        },
                        "conditions": {
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "analyzer": "string_lowercase"
                                },
                                "synonyms": {
                                    "type": "string",
                                    "analyzer": "string_lowercase"
                                },
                                "identifiers": {
                                    "properties": {
                                        "efo": {
                                            "type": "string",
                                            "analyzer": "string_lowercase"
                                        },
                                        "gene": {
                                            "type": "string",
                                            "analyzer": "string_lowercase"
                                        },
                                        "medgen": {
                                            "type": "string",
                                            "analyzer": "string_lowercase"
                                        },
                                        "omim": {
                                            "type": "string",
                                            "analyzer": "string_lowercase"
                                        },
                                        "orphanet": {
                                            "type": "string",
                                            "analyzer": "string_lowercase"
                                        },
                                        "human_phenotype_ontology": {
                                            "type": "string",
                                            "analyzer": "string_lowercase"
                                        }
                                    }
                                },
                                "age_of_onset": {
                                    "type": "string",
                                    "analyzer": "string_lowercase"
                                }
                            }
                        }
                    }
                },
                "xref": {
                    "properties": {
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "breast_cancer_information_core_(bic)_(brca1)": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "breast_cancer_information_core_(bic)_(brca2)": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "cosmic": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "dbrbc": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "dbvar": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "gucy2c_database": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "leiden_muscular_dystrophy_(cav3)": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "leiden_muscular_dystrophy_(dag1)": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "leiden_muscular_dystrophy_(dpm3)": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "leiden_muscular_dystrophy_(myl2)": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "brca1-hci": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                },
                "cytogenic": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "allele_id": {
                    "type": "string",
                    "index": "no"
                },
                "coding_hgvs_only": {
                    "type": "boolean"
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
