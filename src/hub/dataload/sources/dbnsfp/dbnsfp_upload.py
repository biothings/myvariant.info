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
                    "chrom": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
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
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "alt": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "aa": {
                        "properties": {
                            "ref": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "alt": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "pos": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "refcodon": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "codonpos": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "codon_degeneracy": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "genename": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "uniprot": {
                        "properties": {
                            "acc": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "entry": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "ancestral_allele": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "appris": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "genecode_basic": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "tsl": {
                        "type": "integer"
                    },
                    "vep_canonical": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "ensembl": {
                        "properties": {
                            "geneid": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "transcriptid": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "proteinid": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "bstatistic": {
                        "properties": {
                            "score": {
                                "type": "integer"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "mutationtaster": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "converted_rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "model": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "AAE": {
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
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "coding_group": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "eigen": {
                        "properties": {
                            "raw_coding": {
                                "type": "float"
                            },
                            "raw_coding_rankscore": {
                                "type": "float"
                            },
                            "phred_coding": {
                                "type": "float"
                            }
                        }
                    },
                    "eigen-pc": {
                        "properties": {
                            "raw_coding": {
                                "type": "float"
                            },
                            "phred_coding": {
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
                    "integrated": {
                        "properties": {
                            "fitcons_score": {
                                "type": "float"
                            },
                            "fitcons_rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "integer"
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
                                "type": "integer"
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
                                "type": "integer"
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
                                "type": "integer"
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
                            "p30way": {
                                "properties": {
                                    "mammalian": {
                                        "type": "float"
                                    },
                                    "mammalian_rankscore": {
                                        "type": "float"
                                    }
                                }
                            },
                            "p17way": {
                                "properties": {
                                    "primate": {
                                        "type": "float"
                                    },
                                    "primate_rankscore": {
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
                            "30way": {
                                "properties": {
                                    "mammalian": {
                                        "type": "float"
                                    },
                                    "mammalian_rankscore": {
                                        "type": "float"
                                    }
                                }
                            },
                            "p17way": {
                                "properties": {
                                    "primate": {
                                        "type": "float"
                                    },
                                    "primate_rankscore": {
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
                                        "type": "float"
                                    },
                                    "c": {
                                        "type": "float"
                                    },
                                    "g": {
                                        "type": "float"
                                    },
                                    "t": {
                                        "type": "float"
                                    }
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
                    "rsid": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "1000gp3": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            },
                            "afr_ac": {
                                "type": "integer"
                            },
                            "afr_af": {
                                "type": "float"
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
                            "eas_ac": {
                                "type": "integer"
                            },
                            "eas_af": {
                                "type": "float"
                            },
                            "sas_ac": {
                                "type": "integer"
                            },
                            "sas_af": {
                                "type": "float"
                            }
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
                            "adj_ac": {
                                "type": "integer"
                            },
                            "adj_af": {
                                "type": "float"
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
                            "eas_ac": {
                                "type": "integer"
                            },
                            "eas_af": {
                                "type": "float"
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
                            "sas_ac": {
                                "type": "integer"
                            },
                            "sas_af": {
                                "type": "float"
                            }
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
                            "adj_ac": {
                                "type": "integer"
                            },
                            "adj_af": {
                                "type": "float"
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
                            "eas_ac": {
                                "type": "integer"
                            },
                            "eas_af": {
                                "type": "float"
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
                            "sas_ac": {
                                "type": "integer"
                            },
                            "sas_af": {
                                "type": "float"
                            }
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
                            "adj_ac": {
                                "type": "integer"
                            },
                            "adj_af": {
                                "type": "float"
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
                            "eas_ac": {
                                "type": "integer"
                            },
                            "eas_af": {
                                "type": "float"
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
                            "sas_ac": {
                                "type": "integer"
                            },
                            "sas_af": {
                                "type": "float"
                            }
                        }
                    },
                    "sift4g": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "converted_rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "mvp": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "primateai": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "deogen2": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "fathmm-xf": {
                        "properties": {
                            "coding_score": {
                                "type": "float"
                            },
                            "coding_rankscore": {
                                "type": "float"
                            },
                            "coding_pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "reliability_index": {
                        "type": "integer"
                    },
                    "m_cap_score": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                    "clinvar": {
                        "properties": {
                            "rs": {
                                "type": "integer"
                            },
                            "clinsig": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "trait": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "review": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "hgvs": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "var_source": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "gtex": {
                        "properties": {
                            "gene": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "tissue": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "esp6500": {
                        "properties": {
                            "aa_ac": {
                                "type": "integer"
                            },
                            "aa_af": {
                                "type": "float"
                            },
                            "ea_ac": {
                                "type": "integer"
                            },
                            "ea_af": {
                                "type": "float"
                            }
                        }
                    },
                    "gerp++": {
                        "properties": {
                            "nr": {
                                "type": "float"
                            },
                            "rs": {
                                "type": "float"
                            },
                            "rs_rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "mutationassessor": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "aa_change": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "pred": {
                                "properties": {
                                    "p_val": {
                                        "type": "float"
                                    },
                                    "mechanism": {
                                        "type": "text"
                                    }
                                }
                            }
                        }
                    },
                    "polyphen2": {
                        "properties": {
                            "hdiv": {
                                "properties": {
                                    "score": {
                                        "type": "float"
                                    },
                                    "rankscore": {
                                        "type": "float"
                                    },
                                    "pred": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    }
                                }
                            },
                            "hvar": {
                                "properties": {
                                    "score": {
                                        "type": "float"
                                    },
                                    "rankscore": {
                                        "type": "float"
                                    },
                                    "pred": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    }
                                }
                            }
                        }
                    },
                    "sift": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "converted_rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "mpc": {
                        "properties": {
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
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "interpro_domain": {
                        "type": "text"
                    },
                    "cds_strand": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "lrt": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "converted_rankscore": {
                                "type": "float"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "omega": {
                                "type": "float"
                            }
                        }
                    },
                    "aloft": {
                        "properties": {
                            "prob_tolerant": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "prob_recessive": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "prob_dominant": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "pred": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "fraction_transcripts_affected": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "confidence": {
                                "type": "text"
                            }
                        }
                    },
                    "vindijia_neandertal": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
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
                    "uk10k": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "geuvadis_eqtl_target_gene": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
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
