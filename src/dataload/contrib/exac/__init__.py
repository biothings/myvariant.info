def get_mapping():
    mapping = {
        "exac": {
            "properties": {
                "chrom": {
                    "type": "integer"
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
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "qual": {
                    "type": "string",
                    "analyzer": "string_lowercase"
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
                    "type": "integer"
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
                    "type": "integer"
                },
                "clippingranksum": {
                    "type": "integer"
                },
                "fs": {
                    "type": "integer"
                },
                "dp": {
                    "type": "integer"
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
                    "type": "integer"
                },
                "mq": {
                    "properties": {
                        "mq": {
                            "type": "integer"
                        },
                        "mq0": {
                            "type": "integer"
                        },
                        "mqranksum": {
                            "type": "integer"
                        }
                    }
                },
                "ncc": {
                    "type": "long"
                },
                "qd": {
                    "type": "long"
                },
                "readposranksum": {
                    "type": "integer"
                },
                "vqslod": {
                    "type": "integer"
                },
                "culprit": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
