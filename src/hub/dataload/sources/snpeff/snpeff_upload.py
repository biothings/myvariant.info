import biothings.hub.dataload.uploader as uploader


SRC_META = {
        "url" : "http://snpeff.sourceforge.net/",
        "license" : "LGPLv3",
        "license_url" : "http://snpeff.sourceforge.net/download.html",
        "license_url_short": "http://bit.ly/2suyRKt"
        }


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
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "putative_impact": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "gene_id": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "feature_type": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "feature_id": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "transcript_biotype": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "rank": {
                                "type": "integer"
                            },
                            "total": {
                                "type": "integer"
                            },
                            "hgvs_c": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "hgvs_p": {
                                "type": "text",
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
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "text",
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
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "text",
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
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "ref": {
                        "type": "text",
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
    __metadata__ = {
            "assembly" : "hg19",
            "src_meta" : SRC_META,
            }


class SnpeffHg38Uploader(SnpeffBaseUploader):
    name = "snpeff_hg38"
    __metadata__ = {
            "assembly" : "hg38",
            "src_meta" : SRC_META,
            }

