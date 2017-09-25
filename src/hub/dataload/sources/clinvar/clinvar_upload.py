from .clinvar_xml_parser import load_data as load_common
import biothings.hub.dataload.uploader as uploader
from ...uploader import SnpeffPostUpdateUploader


SRC_META = {
        "url" : "https://www.ncbi.nlm.nih.gov/clinvar/",
        "license_url" : "https://www.ncbi.nlm.nih.gov/clinvar/intro/",
        "license_url_short": "https://goo.gl/OaHML9"
        }

class ClinvarBaseUploader(SnpeffPostUpdateUploader):

    def get_pinfo(self):
        pinfo = super(ClinvarBaseUploader,self).get_pinfo()
        # clinvar parser has some memory requirements, ~1.5G
        pinfo.setdefault("__reqs__",{})["mem"] = 1.5 * (1024**3)
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
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "uniprot": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "cosmic": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "dbvar": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "gene": {
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "id": {
                                "type": "long"
                            }
                        }
                    },
                    "genotypeset": {
                        "properties": {
                            "type": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "genotype": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "type": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "rsid": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "include_in_all": True
                    },
                    "rcv": {
                        #"type": "nested",
                        #"include_in_parent": True,     # NOTE: this is not available in ES 2.x
                        "properties": {
                            "accession": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "clinical_significance": {
                                "type": "string"
                            },
                            "number_submitters": {
                                "type": "byte"
                            },
                            "review_status": {
                                "type": "string"
                            },
                            "last_evaluated": {
                                "type": "date"
                            },
                            "preferred_name": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "origin": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "conditions": {
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "synonyms": {
                                        "type": "string"
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
                    "cytogenic": {
                        "type": "string",
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
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "hgvs": {
                        "properties": {
                            "genomic": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "coding": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "non-coding": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "protein": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
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
            "mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : SRC_META,
            }

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        try:
            return load_common(data_folder,"hg19")
        except Exception as e:
            import traceback
            self.logger.error("Error while uploading, %s:\n%s" % (e,traceback.format_exc()))
            raise


class ClinvarHG38Uploader(ClinvarBaseUploader):

    name = "clinvar_hg38"
    main_source = "clinvar"
    __metadata__ = {
            "mapper" : 'observed',
            "assembly" : "hg38",
            "src_meta" : SRC_META,
            }

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        try:
            return load_common(data_folder,"hg38")
        except Exception as e:
            import traceback
            self.logger.error("Error while uploading, %s:\n%s" % (e,traceback.format_exc()))
            raise

