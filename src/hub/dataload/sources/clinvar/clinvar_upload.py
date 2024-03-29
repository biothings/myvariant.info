from .clinvar_xml_parser import load_data as load_common
from hub.dataload.uploader import SnpeffPostUpdateUploader
from hub.dataload.storage import MyVariantTrimmingStorage


SRC_META = {
    "url": "https://www.ncbi.nlm.nih.gov/clinvar/",
    "license_url": "https://www.ncbi.nlm.nih.gov/clinvar/intro/",
    "license_url_short": "http://bit.ly/2SQdcI0"
}


class ClinvarBaseUploader(SnpeffPostUpdateUploader):
    storage_class = MyVariantTrimmingStorage

    def get_pinfo(self):
        pinfo = super(ClinvarBaseUploader,self).get_pinfo()
        # clinvar parser has some memory requirements, ~1.5G
        pinfo.setdefault("__reqs__", {})["mem"] = 1.5 * (1024**3)
        return pinfo

    @classmethod
    def get_mapping(klass):
        mapping = {
            "clinvar": {
                "properties": {
                    "hg19": {
                        "properties": {
                            "start": {
                                "type": "integer"
                            },
                            "end": {
                                "type": "integer"
                            }
                        }
                    },
                    "hg38": {
                        "properties": {
                            "start": {
                                "type": "integer"
                            },
                            "end": {
                                "type": "integer"
                            }
                        }
                    },
                    "omim": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "uniprot": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "cosmic": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "dbvar": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "gene": {
                        "properties": {
                            "symbol": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to" : ["all"],
                            },
                            "id": {
                                "type": "long"
                            }
                        }
                    },
                    "genotypeset": {
                        "properties": {
                            "type": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "genotype": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "rsid": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "copy_to" : ["all"],
                    },
                    "rcv": {
                        #"type": "nested",
                        #"include_in_parent": True,     # NOTE: this is not available in ES 2.x
                        "properties": {
                            "accession": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to" : ["all"],
                            },
                            "clinical_significance": {
                                "type": "text"
                            },
                            "number_submitters": {
                                "type": "byte"
                            },
                            "review_status": {
                                "type": "text"
                            },
                            "last_evaluated": {
                                "type": "date"
                            },
                            "preferred_name": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "origin": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "conditions": {
                                "properties": {
                                    "name": {
                                        "type": "text"
                                    },
                                    "synonyms": {
                                        "type": "text"
                                    },
                                    "identifiers": {
                                        "properties": {
                                            "efo": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "gene": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "medgen": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "omim": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "orphanet": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "human_phenotype_ontology": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "mondo": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "mesh": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            }
                                        }
                                    },
                                    "age_of_onset": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    }
                                }
                            }
                        }
                    },
                    "cytogenic": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "allele_id": {
                        "type": "integer"
                    },
                    "variant_id": {
                        "type": "integer"
                    },
                    "coding_hgvs_only": {
                        "type": "boolean"
                    },
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "hgvs": {
                        "properties": {
                            "genomic": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to" : ["all"],
                            },
                            "coding": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to" : ["all"],
                            },
                            "non-coding": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to" : ["all"],
                            },
                            "protein": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to" : ["all"],
                            }
                        }
                    }
                }
            }
        }
        return mapping


class ClinvarHG19Uploader(ClinvarBaseUploader):

    name = "clinvar_hg19"
    main_source = "clinvar"
    __metadata__ = {
        "mapper": 'observed_skipidtoolong',
        "assembly": "hg19",
        "src_meta": SRC_META,
    }

    def load_data(self, data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        try:
            return load_common(data_folder, "hg19")
        except Exception as e:
            import traceback
            self.logger.error("Error while uploading, %s:\n%s" % (e, traceback.format_exc()))
            raise


class ClinvarHG38Uploader(ClinvarBaseUploader):

    name = "clinvar_hg38"
    main_source = "clinvar"
    __metadata__ = {
        "mapper": 'observed_skipidtoolong',
        "assembly": "hg38",
        "src_meta": SRC_META,
    }

    def load_data(self, data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        try:
            return load_common(data_folder, "hg38")
        except Exception as e:
            import traceback
            self.logger.error("Error while uploading, %s:\n%s" % (e,traceback.format_exc()))
            raise
