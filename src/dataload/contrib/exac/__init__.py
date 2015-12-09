__METADATA__ = {
    "src_name": 'exac',
    "src_url": 'ftp://ftp.broadinstitute.org/pub/ExAC_release/release0.3/ExAC.r0.3.nonpsych.sites.vcf.gz',
    "version": '0.3',
    "field": 'exac'
}

def get_mapping():
    mapping = {
        "exac": {
            "properties": {
                "chrom": {
                    "type": "string",
		    "analyzer": "string_lowercase"
                },
                "pos": {
                    "type": "long"
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alleles": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "type": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "qual": {
                    "type": "float"
                },
                "filter": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "ac": {
                    "properties": {
                        "ac": {
                            "type": "integer"
                        },
                        "ac_afr": {
                            "type": "integer"
                        },
                        "ac_amr": {
                            "type": "integer"
                        },
                        "ac_adj": {
                            "type": "integer"
                        },
                        "ac_eas": {
                            "type": "integer"
                        },
                        "ac_fin": {
                            "type": "integer"
                        },
                        "ac_nfe": {
                            "type": "integer"
                        },
                        "ac_oth": {
                            "type": "integer"
                        },
                        "ac_sas": {
                            "type": "integer"
                        }
                    }
                },
                "af": {
                    "type": "float"
                },
                "an": {
                    "properties": {
                        "an": {
                            "type": "integer"
                        },
                        "an_afr": {
                            "type": "integer"
                        },
                        "an_amr": {
                            "type": "integer"
                        },
                        "an_adj": {
                            "type": "integer"
                        },
                        "an_eas": {
                            "type": "integer"
                        },
                        "an_fin": {
                            "type": "integer"
                        },
                        "an_nfe": {
                            "type": "integer"
                        },
                        "an_oth": {
                            "type": "integer"
                        },
                        "an_sas": {
                            "type": "integer"
                        }
                    }
                },
                "baseqranksum": {
                    "type": "float"
                },
                "clippingranksum": {
                    "type": "float"
                },
                "fs": {
                    "type": "float"
                },
                "dp": {
                    "type": "long"
                },
                "het": {
                    "properties": {
                        "het_afr": {
                            "type": "integer"
                        },
                        "het_amr": {
                            "type": "integer"
                        },
                        "het_eas": {
                            "type": "integer"
                        },
                        "het_fin": {
                            "type": "integer"
                        },
                        "het_nfe": {
                            "type": "integer"
                        },
                        "het_oth": {
                            "type": "integer"
                        },
                        "het_sas": {
                            "type": "integer"
                        },
                        "ac_het": {
                            "type": "integer"
                        }
                    }
                },
                "hom": {
                    "properties": {
                        "hom_afr": {
                            "type": "integer"
                        },
                        "hom_amr": {
                            "type": "integer"
                        },
                        "hom_eas": {
                            "type": "integer"
                        },
                        "hom_fin": {
                            "type": "integer"
                        },
                        "hom_nfe": {
                            "type": "integer"
                        },
                        "hom_oth": {
                            "type": "integer"
                        },
                        "hom_sas": {
                            "type": "integer"
                        },
                        "ac_hom": {
                            "type": "integer"
                        }
                    }
                },
                "inbreedingcoeff": {
                    "type": "float"
                },
                "mq": {
                    "properties": {
                        "mq": {
                            "type": "float"
                        },
                        "mq0": {
                            "type": "integer"
                        },
                        "mqranksum": {
                            "type": "float"
                        }
                    }
                },
                "ncc": {
                    "type": "long"
                },
                "qd": {
                    "type": "float"
                },
                "readposranksum": {
                    "type": "float"
                },
                "vqslod": {
                    "type": "float"
                },
                "culprit": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
