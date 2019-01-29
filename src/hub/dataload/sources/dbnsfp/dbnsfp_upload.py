import os, sys
import glob
import asyncio
import concurrent.futures
import logging

from .dbnsfp_parser import load_data_file as load_common
import biothings.hub.dataload.uploader as uploader
from biothings.hub.dataload.storage import IgnoreDuplicatedStorage
from hub.dataload.uploader import SnpeffPostUpdateUploader


SRC_META = {
    "url" : "https://sites.google.com/site/jpopgen/dbNSFP",
    "license_url" : "https://sites.google.com/site/jpopgen/dbNSFP",
    "license_url_short": "http://bit.ly/2VLnQBz"
}


class DBNSFPBaseUploader(uploader.IgnoreDuplicatedSourceUploader,
                         uploader.ParallelizedSourceUploader,
                         SnpeffPostUpdateUploader):

    GLOB_PATTERN = "dbNSFP*_variant.chr*"

    @classmethod
    def get_mapping(klass):
        mapping = {
            "dbnsfp": {
                "properties": {
                    "rsid": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "copy_to" : ["all"]
                    },
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "hg18": {
                        "properties": {
                            "start": {
                                "type": "integer"
                            },
                            "end": {
                                "type": "integer"
                            }
                        }
                    },
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
                    "ref": {
                        "type": "text"
                    },
                    "alt": {
                        "type": "text"
                    },
                    "aa": {
                        "properties": {
                            "alt": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "ref": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "pos": {
                                "type": "integer"
                            },
                            "refcodon": {
                                "type": "text"
                            },
                            "codonpos": {
                                "type": "integer"
                            },
                            "codon_degeneracy": {
                                "type": "integer"
                            }
                        }
                    },
                    "genename": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "copy_to" : ["all"]
                    },
                    "uniprot": {
                        "properties": {
                            "acc": {
                                "type": "text"
                            },
                            "pos": {
                                "type": "text"
                            }
                        }
                    },
                    "interpro_domain": {
                        "type": "text"
                    },
                    "cds_strand": {
                        "type": "text"
                    },
                    "ancestral_allele": {
                        "type": "text"
                    },
                    "ensembl": {
                        "properties": {
                            "transcriptid": {
                                "type": "text"
                            },
                            "geneid": {
                                "type": "text"
                            },
                            "proteinid": {
                                "type": "text"
                            }
                        }
                    },
                    "sift": {
                        "properties": {
                            "converted_rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            }
                        }
                    },
                    "polyphen2": {
                        "properties": {
                            "hdiv": {
                                "properties": {
                                    "pred": {
                                        "type": "text"
                                    },
                                    "score": {
                                        "type": "float"
                                    },
                                    "rankscore": {
                                        "type": "float"
                                    }
                                }
                            },
                            "hvar": {
                                "properties": {
                                    "pred": {
                                        "type": "text"
                                    },
                                    "score": {
                                        "type": "float"
                                    },
                                    "rankscore": {
                                        "type": "float"
                                    }
                                }
                            }
                        }
                    },
                    "lrt": {
                        "properties": {
                            "converted_rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            },
                            "omega": {
                                "type": "float"
                            }
                        }
                    },
                    "mutationtaster": {
                        "properties": {
                            "converted_rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            },
                            "model": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "AAE": {
                                "type": "text"
                            }
                        }
                    },
                    "mutationassessor": {
                        "properties": {
                            "pred": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "fathmm": {
                        "properties": {
                            "pred": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "provean": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "text"
                            }
                        }
                    },
                    "vest4": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "fathmm-mkl": {
                        "properties": {
                            "coding_score": {
                                "type": "float"
                            },
                            "coding_rankscore": {
                                "type": "float"
                            },
                            "coding_pred": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "coding_group": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "eigen": {
                        "properties": {
                            "raw": {
                                "type": "float"
                            },
                            "phred": {
                                "type": "float"
                            },
                            "raw_rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "eigen-pc": {
                        "properties": {
                            "raw": {
                                "type": "float"
                            },
                            "raw_rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "genocanyon": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "metasvm": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "text"
                            }
                        }
                    },
                    "metalr": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "text"
                            }
                        }
                    },
                    "reliability_index": {
                        "type": "integer"
                    },
                    "dann": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "gerp++": {
                        "properties": {
                            "rs_rankscore": {
                                "type": "float"
                            },
                            "nr": {
                                "type": "float"
                            },
                            "rs": {
                                "type": "float"
                            }
                        }
                    },
                    "revel": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "mutpred": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "accession": {
                                "type": "text"
                            },
                            "aa_change": {
                                "type": "text"
                            },
                            "pred": {
                                "properties": {
                                    "mechanism": {
                                        "type": "text"
                                    },
                                    "p_val": {
                                        "type": "float"
                                    }
                                }
                            }
                        }
                    },
                    "integrated": {
                        "properties": {
                            "fitcons_score": {
                                "type": "float"
                            },
                            "fitcons_rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "float"
                            }
                        }
                    },
                    "gm12878": {
                        "properties": {
                            "fitcons_score": {
                                "type": "float"
                            },
                            "fitcons_rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "float"
                            }
                        }
                    },
                    "h1-hesc": {
                        "properties": {
                            "fitcons_score": {
                                "type": "float"
                            },
                            "fitcons_rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "float"
                            }
                        }
                    },
                    "huvec": {
                        "properties": {
                            "fitcons_score": {
                                "type": "float"
                            },
                            "fitcons_rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "float"
                            }
                        }
                    },
                    "phylo": {
                        "properties": {
                            "p100way": {
                                "properties": {
                                    "vertebrate": {
                                        "type": "float"
                                    },
                                    "vertebrate_rankscore": {
                                        "type": "float"
                                    }
                                }
                            },
                            "p20way": {
                                "properties": {
                                    "mammalian": {
                                        "type": "float"
                                    },
                                    "mammalian_rankscore": {
                                        "type": "float"
                                    }
                                }
                            }
                        }
                    },
                    "phastcons": {
                        "properties": {
                            "100way": {
                                "properties": {
                                    "vertebrate": {
                                        "type": "float"
                                    },
                                    "vertebrate_rankscore": {
                                        "type": "float"
                                    }
                                }
                            },
                            "20way": {
                                "properties": {
                                    "mammalian": {
                                        "type": "float"
                                    },
                                    "mammalian_rankscore": {
                                        "type": "float"
                                    }
                                }
                            }
                        }
                    },
                    "siphy_29way": {
                        "properties": {
                            "pi": {
                                "properties": {
                                    "a": {
                                        "type": "float",
                                    },
                                    "c": {
                                        "type": "float",
                                    },
                                    "t": {
                                        "type": "float",
                                    },
                                    "g": {
                                        "type": "float",
                                    },
                                }
                            },
                            "logodds": {
                                "type": "float"
                            },
                            "logodds_rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "1000gp3": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            },
                            "afr_af": {
                                "type": "float"
                            },
                            "afr_ac": {
                                "type": "integer"
                            },
                            "eur_ac": {
                                "type": "integer"
                            },
                            "eur_af": {
                                "type": "float"
                            },
                            "amr_ac": {
                                "type": "integer"
                            },
                            "amr_af": {
                                "type": "float"
                            },
                            "eas_af": {
                                "type": "float"
                            },
                            "eas_ac": {
                                "type": "integer"
                            },
                            "sas_af": {
                                "type": "float"
                            },
                            "sas_ac": {
                                "type": "integer"
                            },
                        }
                    },
                    "exac": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            },
                            "adj_af": {
                                "type": "float"
                            },
                            "adj_ac": {
                                "type": "integer"
                            },
                            "afr_ac": {
                                "type": "integer"
                            },
                            "afr_af": {
                                "type": "float"
                            },
                            "amr_ac": {
                                "type": "integer"
                            },
                            "amr_af": {
                                "type": "float"
                            },
                            "eas_af": {
                                "type": "float"
                            },
                            "eas_ac": {
                                "type": "integer"
                            },
                            "fin_ac": {
                                "type": "integer"
                            },
                            "fin_af": {
                                "type": "float"
                            },
                            "nfe_ac": {
                                "type": "integer"
                            },
                            "nfe_af": {
                                "type": "float"
                            },
                            "sas_af": {
                                "type": "float"
                            },
                            "sas_ac": {
                                "type": "integer"
                            },
                        }
                    },
                    "exac_nontcga": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            },
                            "adj_af": {
                                "type": "float"
                            },
                            "adj_ac": {
                                "type": "integer"
                            },
                            "afr_ac": {
                                "type": "integer"
                            },
                            "afr_af": {
                                "type": "float"
                            },
                            "amr_ac": {
                                "type": "integer"
                            },
                            "amr_af": {
                                "type": "float"
                            },
                            "eas_af": {
                                "type": "float"
                            },
                            "eas_ac": {
                                "type": "integer"
                            },
                            "fin_ac": {
                                "type": "integer"
                            },
                            "fin_af": {
                                "type": "float"
                            },
                            "nfe_ac": {
                                "type": "integer"
                            },
                            "nfe_af": {
                                "type": "float"
                            },
                            "sas_af": {
                                "type": "float"
                            },
                            "sas_ac": {
                                "type": "integer"
                            },
                        }
                    },
                    "exac_nonpsych": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            },
                            "adj_af": {
                                "type": "float"
                            },
                            "adj_ac": {
                                "type": "integer"
                            },
                            "afr_ac": {
                                "type": "integer"
                            },
                            "afr_af": {
                                "type": "float"
                            },
                            "amr_ac": {
                                "type": "integer"
                            },
                            "amr_af": {
                                "type": "float"
                            },
                            "eas_af": {
                                "type": "float"
                            },
                            "eas_ac": {
                                "type": "integer"
                            },
                            "fin_ac": {
                                "type": "integer"
                            },
                            "fin_af": {
                                "type": "float"
                            },
                            "nfe_ac": {
                                "type": "integer"
                            },
                            "nfe_af": {
                                "type": "float"
                            }
                        }
                    },
                    "twinsuk": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "alspac": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "esp6500": {
                        "properties": {
                            "ea_af": {
                                "type": "float"
                            },
                            "aa_af": {
                                "type": "float"
                            },
                            "ea_ac": {
                                "type": "integer"
                            },
                            "aa_ac": {
                                "type": "integer"
                            }
                        }
                    },
                    "clinvar": {
                        "properties": {
                            "rs": {
                                "type": "text",
                                "copy_to" : ["all"]
                            },
                             "clinsig": {
                                 "type": "integer"
                             },
                             'golden_stars': {
                                 "type" : "integer"
                             },
                            "trait": {
                                "type": "text"
                            }
                        }
                    },
                    "gtex": {
                        "properties": {
                            "gene": {
                                "type": "text"
                            },
                            "tissue": {
                                "type": "text"
                            }
                        }
                    }
                }
            }
        }
        return mapping

    def jobs(self):
        # tuple(input_file,version), where version is either hg38 or hg19)
        return map(lambda e: (e, self.__class__.__metadata__["assembly"]),
                   glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_PATTERN)))

    def load_data(self, input_file, hg):
        return load_common(input_file, version=hg)


class DBNSFPHG38Uploader(DBNSFPBaseUploader):

    name = "dbnsfp_hg38"
    main_source = "dbnsfp"
    __metadata__ = {
            "assembly": "hg38",
            "src_meta" : SRC_META
            }


class DBNSFPHG19Uploader(DBNSFPBaseUploader):

    name = "dbnsfp_hg19"
    main_source = "dbnsfp"
    __metadata__ = {
            "assembly": "hg19",
            "src_meta" : SRC_META
            }
