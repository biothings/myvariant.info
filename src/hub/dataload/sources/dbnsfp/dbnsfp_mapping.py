mapping = {
    "dbnsfp": {
        "properties": {
            "rsid": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
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
            "hgvsc": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "hgvsp": {
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
            "cds_strand": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "ancestral_allele": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "altai_neandertal": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "denisova": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "vindijia_neandertal": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "chagyrskaya_neandertal": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
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
                    "aae": {
                        "type": "text"
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
            "metarnn": {
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
            "m-cap": {
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
            "gmvp": {  # new in 4.4.a
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
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
            "bayesdel": {
                "properties": {
                    "add_af": {
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
                    "no_af": {
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
            "clinpred": {
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
            "list-s2": {
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
            "varity_r": {
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "varity_er": {
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "varity_r_loo": {
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "varity_er_loo": {
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "aloft": {
                "properties": {
                    "fraction_transcripts_affected": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
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
                    "confidence": {
                        "type": "text"
                    }
                }
            },
            "cadd": {
                # Only for "hg38"
                # No CADD fields will be included for "hg19"
                "properties": {
                    "raw_score": {
                        "type": "float"
                    },
                    "raw_rankscore": {
                        "type": "float"
                    },
                    "pred": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
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
                    "raw_coding_rankscore": {
                        "type": "float"
                    },
                    "phred_coding": {
                        "type": "float"
                    },
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
            # "integrated": {
            #     "properties": {
            #         "fitcons_score": {
            #             "type": "float"
            #         },
            #         "fitcons_rankscore": {
            #             "type": "float"
            #         },
            #         "confidence_value": {
            #             "type": "integer"
            #         }
            #     }
            # },
            # "gm12878": {
            #     "properties": {
            #         "fitcons_score": {
            #             "type": "float"
            #         },
            #         "fitcons_rankscore": {
            #             "type": "float"
            #         },
            #         "confidence_value": {
            #             "type": "integer"
            #         }
            #     }
            # },
            # "h1-hesc": {
            #     "properties": {
            #         "fitcons_score": {
            #             "type": "float"
            #         },
            #         "fitcons_rankscore": {
            #             "type": "float"
            #         },
            #         "confidence_value": {
            #             "type": "integer"
            #         }
            #     }
            # },
            # "huvec": {
            #     "properties": {
            #         "fitcons_score": {
            #             "type": "float"
            #         },
            #         "fitcons_rankscore": {
            #             "type": "float"
            #         },
            #         "confidence_value": {
            #             "type": "integer"
            #         }
            #     }
            # },
            "fitcons": {
                "properties": {
                    "integrated": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "int"
                            }
                        }
                    },
                    "gm12878": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "int"
                            }
                        }
                    },
                    "h1-hesc": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "int"
                            }
                        }
                    },
                    "huvec": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            },
                            "confidence_value": {
                                "type": "int"
                            }
                        }
                    },
                }
            },
            "linsight": {
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
            "phylop": {
                "properties": {
                    "100way_vertebrate": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "470way_mammalian": {  # replaced 30way_mammalian in 4.4.a
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "17way_primate": {
                        "properties": {
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
            "phastcons": {
                "properties": {
                    "100way_vertebrate": {
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "470way_mammalian": {  # replaced 30way_mammalian in 4.4.a
                        "properties": {
                            "score": {
                                "type": "float"
                            },
                            "rankscore": {
                                "type": "float"
                            }
                        }
                    },
                    "17way_primate": {
                        "properties": {
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
                    "logodds_score": {
                        "type": "float"
                    },
                    "logodds_rankscore": {
                        "type": "float"
                    }
                }
            },
            "bstatistic": {
                "properties": {
                    "score": {
                        "type": "integer"
                    },
                    "converted_rankscore": {
                        "type": "float"
                    }
                }
            },
            "1000gp3": {  # changed since 4.4.a
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "af": {
                        "type": "float"
                    },
                    # "afr_ac": {
                    #     "type": "integer"
                    # },
                    # "afr_af": {
                    #     "type": "float"
                    # },
                    "afr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "eur_ac": {
                    #     "type": "integer"
                    # },
                    # "eur_af": {
                    #     "type": "float"
                    # },
                    "eur": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "amr_ac": {
                    #     "type": "integer"
                    # },
                    # "amr_af": {
                    #     "type": "float"
                    # },
                    "amr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "eas_ac": {
                    #     "type": "integer"
                    # },
                    # "eas_af": {
                    #     "type": "float"
                    # },
                    "eas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "sas_ac": {
                    #     "type": "integer"
                    # },
                    # "sas_af": {
                    #     "type": "float"
                    # }
                    "sas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
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
            "esp6500": {  # changed since 4.4.a
                "properties": {
                    # "aa_ac": {
                    #     "type": "integer"
                    # },
                    # "aa_af": {
                    #     "type": "float"
                    # },
                    "aa": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "ea_ac": {
                    #     "type": "integer"
                    # },
                    # "ea_af": {
                    #     "type": "float"
                    # }
                    "ea": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                }
            },
            "exac": {  # changed since 4.4.a
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
                    # "afr_ac": {
                    #     "type": "integer"
                    # },
                    # "afr_af": {
                    #     "type": "float"
                    # },
                    "afr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "amr_ac": {
                    #     "type": "integer"
                    # },
                    # "amr_af": {
                    #     "type": "float"
                    # },
                    "amr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "eas_ac": {
                    #     "type": "integer"
                    # },
                    # "eas_af": {
                    #     "type": "float"
                    # },
                    "eas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "fin_ac": {
                    #     "type": "integer"
                    # },
                    # "fin_af": {
                    #     "type": "float"
                    # },
                    "fin": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "nfe_ac": {
                    #     "type": "integer"
                    # },
                    # "nfe_af": {
                    #     "type": "float"
                    # },
                    "nfe": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "sas_ac": {
                    #     "type": "integer"
                    # },
                    # "sas_af": {
                    #     "type": "float"
                    # }
                    "sas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    }
                }
            },
            "exac_nontcga": {  # changed since 4.4.a
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
                    # "afr_ac": {
                    #     "type": "integer"
                    # },
                    # "afr_af": {
                    #     "type": "float"
                    # },
                    "afr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "amr_ac": {
                    #     "type": "integer"
                    # },
                    # "amr_af": {
                    #     "type": "float"
                    # },
                    "amr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "eas_ac": {
                    #     "type": "integer"
                    # },
                    # "eas_af": {
                    #     "type": "float"
                    # },
                    "eas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "fin_ac": {
                    #     "type": "integer"
                    # },
                    # "fin_af": {
                    #     "type": "float"
                    # },
                    "fin": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "nfe_ac": {
                    #     "type": "integer"
                    # },
                    # "nfe_af": {
                    #     "type": "float"
                    # },
                    "nfe": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "sas_ac": {
                    #     "type": "integer"
                    # },
                    # "sas_af": {
                    #     "type": "float"
                    # }
                    "sas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    }
                }
            },
            "exac_nonpsych": {  # changed since 4.4.a
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
                    # "afr_ac": {
                    #     "type": "integer"
                    # },
                    # "afr_af": {
                    #     "type": "float"
                    # },
                    "afr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "amr_ac": {
                    #     "type": "integer"
                    # },
                    # "amr_af": {
                    #     "type": "float"
                    # },
                    "amr": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "eas_ac": {
                    #     "type": "integer"
                    # },
                    # "eas_af": {
                    #     "type": "float"
                    # },
                    "eas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "fin_ac": {
                    #     "type": "integer"
                    # },
                    # "fin_af": {
                    #     "type": "float"
                    # },
                    "fin": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "nfe_ac": {
                    #     "type": "integer"
                    # },
                    # "nfe_af": {
                    #     "type": "float"
                    # },
                    "nfe": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    # "sas_ac": {
                    #     "type": "integer"
                    # },
                    # "sas_af": {
                    #     "type": "float"
                    # }
                    "sas": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    }
                }
            },
            "alfa": {  # new in 4.4.a
                "properties": {
                    "european": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "african_others": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "east_asian": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "african_american": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "latin_american_1": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "latin_american_2": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "other_asian": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "south_asian": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "other": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "african": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "asian": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                    "total": {
                        "properties": {
                            "ac": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "af": {
                                "type": "float"
                            }
                        }
                    },
                }
            },
            "clinvar": {
                "properties": {
                    "clinvar_id": {
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
                    },
                    "medgen": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "omim": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "orphanet": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    }
                }
            },
            "interpro_domain": {
                "type": "text"
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
            "geuvadis_eqtl_target_gene": {
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            }
        }
    }
}
