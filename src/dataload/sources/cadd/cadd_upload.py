
from .cadd_parser import load_data
import biothings.dataload.uploader as uploader

class CADDUploader(uploader.BaseSourceUploader):

    name = "cadd"

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        return load_data(data_folder)

    @classmethod
    def get_mapping(self):
        mapping = {
            "cadd": {
                "properties": {
                    "annotype": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "anc": {
                        "type": "string",
                        "index": "no"
                    },
                    "length": {
                        "type": "integer",
                        "index": "no"
                    },
                    "istv": {
                        "type": "string",
                        "index": "no"
                    },
                    "isderived": {
                        "type": "string",
                        "index": "no"
                    },
                    "gc": {
                        "type": "float",
                        "index": "no"
                    },
                    "cpg": {
                        "type": "float",
                        "index": "no"
                    },
                    "mapability": {
                        "properties": {
                            "20bp": {
                                "type": "float",
                                "index": "no"
                            },
                            "35bp": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "scoresegdup": {
                        "type": "float",
                        "index": "no"
                    },
                    "phast_cons": {
                        "properties": {
                            "primate": {
                                "type": "float",
                                "index": "no"
                            },
                            "mammalian": {
                                "type": "float",
                                "index": "no"
                            },
                            "vertebrate": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "phylop": {
                        "properties": {
                            "primate": {
                                "type": "float",
                                "index": "no"
                            },
                            "mammalian": {
                                "type": "float",
                                "index": "no"
                            },
                            "vertebrate": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "gerp": {
                        "properties": {
                            "n": {
                                "type": "integer",
                                "index": "no"
                            },
                            "s": {
                                "type": "integer",
                                "index": "no"
                            },
                            "rs": {
                                "type": "float",
                                "index": "no"
                            },
                            "rs_pval": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "bstatistic": {
                        "type": "integer",
                        "index": "no"
                    },
                    "mutindex": {
                        "type": "integer",
                        "index": "no"
                    },
                    "dna": {
                        "properties": {
                            "helt": {
                                "type": "float",
                                "index": "no"
                            },
                            "mgw": {
                                "type": "float",
                                "index": "no"
                            },
                            "prot": {
                                "type": "float",
                                "index": "no"
                            },
                            "roll": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "mirsvr": {
                        "properties": {
                            "score": {
                                "type": "float",
                                "index": "no"
                            },
                            "e": {
                                "type": "float",
                                "index": "no"
                            },
                            "aln": {
                                "type": "integer",
                                "index": "no"
                            }
                        }
                    },
                    "targetscans": {
                        "type": "integer",
                        "index": "no"
                    },
                    "fitcons": {
                        "type": "float",
                        "index": "no"
                    },
                    "chmm": {
                        "properties": {
                            "tssa": {
                                "type": "float",
                                "index": "no"
                            },
                            "tssaflnk": {
                                "type": "float",
                                "index": "no"
                            },
                            "txflnk": {
                                "type": "float",
                                "index": "no"
                            },
                            "tx": {
                                "type": "float",
                                "index": "no"
                            },
                            "txwk": {
                                "type": "float",
                                "index": "no"
                            },
                            "enh": {
                                "type": "float",
                                "index": "no"
                            },
                            "znfrpts": {
                                "type": "float",
                                "index": "no"
                            },
                            "het": {
                                "type": "float",
                                "index": "no"
                            },
                            "tssbiv": {
                                "type": "float",
                                "index": "no"
                            },
                            "bivflnk": {
                                "type": "float",
                                "index": "no"
                            },
                            "enhbiv": {
                                "type": "float",
                                "index": "no"
                            },
                            "reprpc": {
                                "type": "float",
                                "index": "no"
                            },
                            "reprpcwk": {
                                "type": "float",
                                "index": "no"
                            },
                            "quies": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "encode": {
                        "properties": {
                            "exp": {
                                "type": "float",
                                "index": "no"
                            },
                            "h3k27ac": {
                                "type": "float",
                                "index": "no"
                            },
                            "h3k4me1": {
                                "type": "float",
                                "index": "no"
                            },
                            "h3k4me3": {
                                "type": "float",
                                "index": "no"
                            },
                            "nucleo": {
                                "type": "float",
                                "index": "no"
                            },
                            "occ": {
                                "type": "integer",
                                "index": "no"
                            },
                            "p_val": {
                                "properties": {
                                    "comb": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "dnas": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "faire": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "polii": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "ctcf": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "mycp": {
                                        "type": "float",
                                        "index": "no"
                                    }
                                }
                            },
                            "sig": {
                                "properties": {
                                    "dnase": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "faire": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "polii": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "ctcf": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "myc": {
                                        "type": "float",
                                        "index": "no"
                                    }
                                }
                            }
                        }
                    },
                    "segway": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "index": "no"
                    },
                    "motif": {
                        "properties": {
                            "toverlap": {
                                "type": "integer",
                                "index": "no"
                            },
                            "dist": {
                                "type": "float",
                                "index": "no"
                            },
                            "ecount": {
                                "type": "integer",
                                "index": "no"
                            },
                            "ename": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "index": "no"
                            },
                            "ehipos": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "index": "no"
                            },
                            "escorechng": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "tf": {
                        "properties": {
                            "bs": {
                                "type": "integer",
                                "index": "no"
                            },
                            "bs_peaks": {
                                "type": "integer",
                                "index": "no"
                            },
                            "bs_peaks_max": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "isknownvariant": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "index": "no"
                    },
                    "consequence": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "consscore": {
                        "type": "integer"
                    },
                    "consdetail": {
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
                    "type": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "esp": {
                        "properties": {
                            "af": {
                                "type": "float"
                            },
                            "afr": {
                                "type": "float",
                                "index": "no"
                            },
                            "eur": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "1000g": {
                        "properties": {
                            "af": {
                                "type": "float"
                            },
                            "asn": {
                                "type": "float",
                                "index": "no"
                            },
                            "amr": {
                                "type": "float",
                                "index": "no"
                            },
                            "afr": {
                                "type": "float",
                                "index": "no"
                            },
                            "eur": {
                                "type": "float",
                                "index": "no"
                            }
                        }
                    },
                    "min_dist_tss": {
                        "type": "integer"
                    },
                    "min_dist_tse": {
                        "type": "integer"
                    },
                    "gene": {
                        "properties": {
                            "gene_id": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "prot": {
                                "properties": {
                                    "protpos": {
                                        "type": "integer",
                                        "index": "no"
                                    },
                                    "rel_prot_pos": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "domain": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    }
                                }
                            },
                            "feature_id": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "index": "no"
                            },
                            "ccds_id": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "index": "no"
                            },
                            "cds": {
                                "properties": {
                                    "cdna_pos": {
                                        "type": "integer",
                                        "index": "no"
                                    },
                                    "cds_pos": {
                                        "type": "integer",
                                        "index": "no"
                                    },
                                    "rel_cdna_pos": {
                                        "type": "float",
                                        "index": "no"
                                    },
                                    "rel_cds_pos": {
                                        "type": "float",
                                        "index": "no"
                                    }
                                }
                            }
                        }
                    },
                    "dst2splice": {
                        "type": "integer"
                    },
                    "dst2spltype": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "exon": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "index": "no"
                    },
                    "intron": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "index": "no"
                    },
                    "oaa": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "index": "no"
                    },
                    "naa": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "index": "no"
                    },
                    "grantham": {
                        "type": "integer"
                    },
                    "polyphen": {
                        "properties": {
                            "cat": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "val": {
                                "type": "float"
                            }
                        }
                    },
                    "sift": {
                        "properties": {
                            "cat": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "val": {
                                "type": "float"
                            }
                        }
                    },
                    "rawscore": {
                        "type": "float"
                    },
                    "phred": {
                        "type": "float"
                    }
                }
            }
        }
        return mapping


