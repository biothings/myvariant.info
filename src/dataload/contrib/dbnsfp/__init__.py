# -*- coding: utf-8 -*-

from .dbnsfp_parser import load_data as _load_data

DBNSFP_INPUT_FILE = '/opt/myvariant.info/load_archive/dbnsfp/dbNSFP2.9_variant*'

def load_data():
    dbnsfp_data = _load_data(DBNSFP_INPUT_FILE)
    return dbnsfp_data

def get_mapping():
    mapping = {
        "dbnsfp": {
            "properties": {
                "aa": {
                    "properties": {
                        "alt": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "ref": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                },
                "genename": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "slr_test_statistic": {
                    "type": "double"
                },
                "mutationassessor": {
                    "properties": {
                        "pred": {
                            "type": "string"
                        },
                        "score": {
                            "type": "double"
                        },
                        "rankscore": {
                            "type": "double"
                        }
                    }
                },
                "polyphen2": {
                    "properties": {
                        "hdiv": {
                            "properties": {
                                "pred": {
                                    "type": "string"
                                },
                                "score": {
                                    "type": "double"
                                },
                                "rankscore": {
                                    "type": "double"
                                }
                            }
                        },
                        "hvar": {
                            "properties": {
                                "pred": {
                                    "type": "string"
                                },
                                "score": {
                                    "type": "double"
                                },
                                "rankscore": {
                                    "type": "double"
                                }
                            }
                        }
                    }
                },
                "phastcons46way": {
                    "properties": {
                        "primate_rankscore": {
                            "type": "double"
                        },
                        "primate": {
                            "type": "double"
                        },
                        "vertebrate": {
                            "type": "double"
                        },
                        "vertebrate_rankscore": {
                            "type": "double"
                        },
                        "placental_rankscore": {
                            "type": "double"
                        },
                        "placental": {
                            "type": "double"
                        }
                    }
                },
                "aapos": {
                    "type": "long"
                },
                "cadd": {
                    "properties": {
                        "phred": {
                            "type": "double"
                        },
                        "raw": {
                            "type": "double"
                        },
                        "raw_rankscore": {
                            "type": "double"
                        }
                    }
                },
                "siphy_29way_pi_logodds_rankscore": {
                    "type": "double"
                },
                "phylop46way": {
                    "properties": {
                        "primate_rankscore": {
                            "type": "double"
                        },
                        "primate": {
                            "type": "double"
                        },
                        "vertebrate": {
                            "type": "double"
                        },
                        "vertebrate_rankscore": {
                            "type": "double"
                        },
                        "placental_rankscore": {
                            "type": "double"
                        },
                        "placental": {
                            "type": "double"
                        }
                    }
                },
                "lrt_omega": {
                    "type": "double"
                },
                "vest3": {
                    "properties": {
                        "score": {
                            "type": "double"
                        },
                        "rankscore": {
                            "type": "double"
                        }
                    }
                },
                "interpro_domain": {
                    "type": "string"
                },
                "reliability_index": {
                    "type": "long"
                },
                "fathmm": {
                    "properties": {
                        "pred": {
                            "type": "string"
                        },
                        "score": {
                            "type": "double"
                        },
                        "rankscore": {
                            "type": "double"
                        }
                    }
                },
                "mutationtaster": {
                    "properties": {
                        "converted_rankscore": {
                            "type": "double"
                        },
                        "pred": {
                            "type": "string"
                        },
                        "score": {
                            "type": "double"
                        }
                    }
                },
                "lr": {
                    "properties": {
                        "pred": {
                            "type": "string"
                        },
                        "score": {
                            "type": "double"
                        },
                        "rankscore": {
                            "type": "double"
                        }
                    }
                },
                "esp6500": {
                    "properties": {
                        "ea_af": {
                            "type": "double"
                        },
                        "aa_af": {
                            "type": "double"
                        }
                    }
                },
                "refcodon": {
                    "type": "string"
                },
                "ancestral_allele": {
                    "type": "string"
                },
                "uniprot": {
                    "properties": {
                        "acc": {
                            "type": "string"
                        },
                        "pos": {
                            "type": "string"
                        }
                    }
                },
                "aapos_sift": {
                    "type": "string"
                },
                "allele2": {
                    "type": "string"
                },
                "allele1": {
                    "type": "string"
                },
                "fold-degenerate": {
                    "type": "long"
                },
                "aapos_fathmm": {
                    "type": "string"
                },
                "sift": {
                    "properties": {
                        "converted_rankscore": {
                            "type": "double"
                        },
                        "pred": {
                            "type": "string"
                        },
                        "score": {
                            "type": "long"
                        }
                    }
                },
                "lrt": {
                    "properties": {
                        "converted_rankscore": {
                            "type": "double"
                        },
                        "pred": {
                            "type": "string"
                        },
                        "score": {
                            "type": "double"
                        }
                    }
                },
                "chrom": {
                    "type": "string"
                },
                "1000gp1": {
                    "properties": {
                        "eur_af": {
                            "type": "double"
                        },
                        "ac": {
                            "type": "long"
                        },
                        "eur_ac": {
                            "type": "long"
                        },
                        "af": {
                            "type": "double"
                        },
                        "amr_ac": {
                            "type": "long"
                        },
                        "asn_af": {
                            "type": "double"
                        },
                        "afr_af": {
                            "type": "double"
                        },
                        "amr_af": {
                            "type": "double"
                        },
                        "afr_ac": {
                            "type": "long"
                        },
                        "asn_ac": {
                            "type": "long"
                        }
                    }
                },
                "radialsvm": {
                    "properties": {
                        "pred": {
                            "type": "string"
                        },
                        "score": {
                            "type": "double"
                        },
                        "rankscore": {
                            "type": "double"
                        }
                    }
                },
                "siphy_29way_pi_logodds": {
                    "type": "double"
                },
                "siphy_29way_pi": {
                    "properties": {
                        "a": {
                            "type": "double"
                        },
                        "c": {
                            "type": "double"
                        },
                        "t": {
                            "type": "double"
                        },
                        "g": {
                            "type": "double"
                        }
                    }
                },
                "codonpos": {
                    "type": "long"
                },
                "gerp++": {
                    "properties": {
                        "rs_rankscore": {
                            "type": "double"
                        },
                        "nr": {
                            "type": "double"
                        },
                        "rs": {
                            "type": "double"
                        }
                    }
                },
                "ensembl": {
                    "properties": {
                        "transcriptid": {
                            "type": "string"
                        },
                        "geneid": {
                            "type": "string"
                        }
                    }
                },
                "hg18": {
                    "properties": {
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
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
                "cds_strand": {
                    "type": "string"
                },
                "unisnp_ids": {
                    "type": "string"
                }
            }
        }
    }
    return mapping

