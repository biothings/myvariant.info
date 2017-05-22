
import biothings.dataload.uploader as uploader

class SnpeffBaseUploader(uploader.NoDataSourceUploader):

    main_source = "snpeff"

    def load_data(self,data_folder):
        self.logger.info("Skip Snpeff data load (it's a post-process)")
        return {}

    @classmethod
    def get_mapping(klass):
        mapping = {
            "snpeff": {
                "properties": {
                    "ann": {
                        "properties": {
                            "effect": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "putative_impact": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "gene_id": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "feature_type": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "feature_id": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "transcript_biotype": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "rank": {
                                "type": "integer"
                            },
                            "total": {
                                "type": "integer"
                            },
                            "hgvs_c": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "hgvs_p": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "cdna": {
                                "properties": {
                                    "position": {
                                        "type": "integer"
                                    },
                                    "length": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "cds": {
                                "properties": {
                                    "position": {
                                        "type": "integer"
                                    },
                                    "length": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "protein": {
                                "properties": {
                                    "position": {
                                        "type": "integer"
                                    },
                                    "length": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "distance_to_feature": {
                                "type": "integer"
                            }
                        }
                    },
                    "lof": {
                        "properties": {
                            "gene_id": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "number_of_transcripts_in_gene": {
                                "type": "integer"
                            },
                            "percent_of_transcripts_affected": {
                                "type": "float"
                            }
                        }
                    },
                    "nmd": {
                        "properties": {
                            "gene_id": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "number_of_transcripts_in_gene": {
                                "type": "integer"
                            },
                            "percent_of_transcripts_affected": {
                                "type": "float"
                            }
                        }
                    }
                }
            },
            "vcf": {
                "properties": {
                    "alt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "ref": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "position": {
                        "type": "integer"
                    }
                }
            },
            klass.__metadata__["assembly"]: {
                "properties": {
                    "start": {
                        "type": "integer"
                    },
                    "end": {
                        "type": "integer"
                    }
                }
            }
        }
        return mapping


class SnpeffHg19Uploader(SnpeffBaseUploader):
    name = "snpeff_hg19"
    __metadata__ = {"assembly" : "hg19"}


class SnpeffHg38Uploader(SnpeffBaseUploader):
    name = "snpeff_hg38"
    __metadata__ = {"assembly" : "hg38"}

