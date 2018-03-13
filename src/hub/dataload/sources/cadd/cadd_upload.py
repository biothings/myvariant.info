
from .cadd_parser import load_data
import biothings.hub.dataload.uploader as uploader
from ...uploader import SnpeffPostUpdateUploader

class CADDUploader(uploader.DummySourceUploader, SnpeffPostUpdateUploader):

    keep_archive = 1

    name = "cadd"
    __metadata__ = {
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "http://cadd.gs.washington.edu/home",
                "license_url" : "http://cadd.gs.washington.edu/contact",
                "license_url_short": "http://goo.gl/bkpNhq"
                }
            }

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        return load_data(data_folder)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "cadd": {
                "properties": {
                    "annotype": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "anc": {
                        "type": "text",
                        "index" : False
                    },
                    "length": {
                        "type": "integer",
                        "index" : False
                    },
                    "istv": {
                        "type": "text",
                        "index" : False
                    },
                    "isderived": {
                        "type": "text",
                        "index" : False
                    },
                    "gc": {
                        "type": "float",
                        "index" : False
                    },
                    "cpg": {
                        "type": "float",
                        "index" : False
                    },
                    "mapability": {
                        "properties": {
                            "20bp": {
                                "type": "float",
                                "index" : False
                            },
                            "35bp": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "scoresegdup": {
                        "type": "float",
                        "index" : False
                    },
                    "phast_cons": {
                        "properties": {
                            "primate": {
                                "type": "float",
                                "index" : False
                            },
                            "mammalian": {
                                "type": "float",
                                "index" : False
                            },
                            "vertebrate": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "phylop": {
                        "properties": {
                            "primate": {
                                "type": "float",
                                "index" : False
                            },
                            "mammalian": {
                                "type": "float",
                                "index" : False
                            },
                            "vertebrate": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "gerp": {
                        "properties": {
                            "n": {
                                "type": "integer",
                                "index" : False
                            },
                            "s": {
                                "type": "integer",
                                "index" : False
                            },
                            "rs": {
                                "type": "float",
                                "index" : False
                            },
                            "rs_pval": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "bstatistic": {
                        "type": "integer",
                        "index" : False
                    },
                    "mutindex": {
                        "type": "integer",
                        "index" : False
                    },
                    "dna": {
                        "properties": {
                            "helt": {
                                "type": "float",
                                "index" : False
                            },
                            "mgw": {
                                "type": "float",
                                "index" : False
                            },
                            "prot": {
                                "type": "float",
                                "index" : False
                            },
                            "roll": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "mirsvr": {
                        "properties": {
                            "score": {
                                "type": "float",
                                "index" : False
                            },
                            "e": {
                                "type": "float",
                                "index" : False
                            },
                            "aln": {
                                "type": "integer",
                                "index" : False
                            }
                        }
                    },
                    "targetscans": {
                        "type": "integer",
                        "index" : False
                    },
                    "fitcons": {
                        "type": "float",
                        "index" : False
                    },
                    "chmm": {
                        "properties": {
                            "tssa": {
                                "type": "float",
                                "index" : False
                            },
                            "tssaflnk": {
                                "type": "float",
                                "index" : False
                            },
                            "txflnk": {
                                "type": "float",
                                "index" : False
                            },
                            "tx": {
                                "type": "float",
                                "index" : False
                            },
                            "txwk": {
                                "type": "float",
                                "index" : False
                            },
                            "enh": {
                                "type": "float",
                                "index" : False
                            },
                            "znfrpts": {
                                "type": "float",
                                "index" : False
                            },
                            "het": {
                                "type": "float",
                                "index" : False
                            },
                            "tssbiv": {
                                "type": "float",
                                "index" : False
                            },
                            "bivflnk": {
                                "type": "float",
                                "index" : False
                            },
                            "enhbiv": {
                                "type": "float",
                                "index" : False
                            },
                            "reprpc": {
                                "type": "float",
                                "index" : False
                            },
                            "reprpcwk": {
                                "type": "float",
                                "index" : False
                            },
                            "quies": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "encode": {
                        "properties": {
                            "exp": {
                                "type": "float",
                                "index" : False
                            },
                            "h3k27ac": {
                                "type": "float",
                                "index" : False
                            },
                            "h3k4me1": {
                                "type": "float",
                                "index" : False
                            },
                            "h3k4me3": {
                                "type": "float",
                                "index" : False
                            },
                            "nucleo": {
                                "type": "float",
                                "index" : False
                            },
                            "occ": {
                                "type": "integer",
                                "index" : False
                            },
                            "p_val": {
                                "properties": {
                                    "comb": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "dnas": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "faire": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "polii": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "ctcf": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "mycp": {
                                        "type": "float",
                                        "index" : False
                                    }
                                }
                            },
                            "sig": {
                                "properties": {
                                    "dnase": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "faire": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "polii": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "ctcf": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "myc": {
                                        "type": "float",
                                        "index" : False
                                    }
                                }
                            }
                        }
                    },
                    "segway": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "index" : False
                    },
                    "motif": {
                        "properties": {
                            "toverlap": {
                                "type": "integer",
                                "index" : False
                            },
                            "dist": {
                                "type": "float",
                                "index" : False
                            },
                            "ecount": {
                                "type": "integer",
                                "index" : False
                            },
                            "ename": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "index" : False
                            },
                            "ehipos": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "index" : False
                            },
                            "escorechng": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "tf": {
                        "properties": {
                            "bs": {
                                "type": "integer",
                                "index" : False
                            },
                            "bs_peaks": {
                                "type": "integer",
                                "index" : False
                            },
                            "bs_peaks_max": {
                                "type": "float",
                                "index" : False
                            }
                        }
                    },
                    "isknownvariant": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "index" : False
                    },
                    "consequence": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "consscore": {
                        "type": "integer"
                    },
                    "consdetail": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "pos": {
                        "type": "long"
                    },
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "esp": {
                        "properties": {
                            "af": {
                                "type": "float"
                            },
                            "afr": {
                                "type": "float",
                                "index" : False
                            },
                            "eur": {
                                "type": "float",
                                "index" : False
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
                                "index" : False
                            },
                            "amr": {
                                "type": "float",
                                "index" : False
                            },
                            "afr": {
                                "type": "float",
                                "index" : False
                            },
                            "eur": {
                                "type": "float",
                                "index" : False
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
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "genename": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to": ["all"],
                            },
                            "prot": {
                                "properties": {
                                    "protpos": {
                                        "type": "integer",
                                        "index" : False
                                    },
                                    "rel_prot_pos": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "domain": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    }
                                }
                            },
                            "feature_id": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "index" : False
                            },
                            "ccds_id": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "index" : False
                            },
                            "cds": {
                                "properties": {
                                    "cdna_pos": {
                                        "type": "integer",
                                        "index" : False
                                    },
                                    "cds_pos": {
                                        "type": "integer",
                                        "index" : False
                                    },
                                    "rel_cdna_pos": {
                                        "type": "float",
                                        "index" : False
                                    },
                                    "rel_cds_pos": {
                                        "type": "float",
                                        "index" : False
                                    }
                                }
                            }
                        }
                    },
                    "dst2splice": {
                        "type": "integer"
                    },
                    "dst2spltype": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "exon": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "index" : False
                    },
                    "intron": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "index" : False
                    },
                    "oaa": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "index" : False
                    },
                    "naa": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "index" : False
                    },
                    "grantham": {
                        "type": "integer"
                    },
                    "polyphen": {
                        "properties": {
                            "cat": {
                                "type": "text",
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
                                "type": "text",
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


