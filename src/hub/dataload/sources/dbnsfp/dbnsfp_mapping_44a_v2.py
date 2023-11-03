start_pos_field = {"start": {"type": "integer"}}
end_pos_field = {"end": {"type": "integer"}}

score_field = {"score": {"type": "float"}}
converted_rankscore_field = {"converted_rankscore": {"type": "float"}}
rankscore_field = {"rankscore": {"type": "float"}}
confidence_value_field = {"confidence_value": {"type": "int"}}
pred_field = {
    "pred": {
        "type": "keyword",
        "normalizer": "keyword_lowercase_normalizer"
    }
}

allele_count_field = {"ac": {"type": "integer"}}
allele_num_field = {"an": {"type": "integer"}}
allele_freq_field = {"af": {"type": "float"}}
adj_allele_count_field = {"adj_ac": {"type": "integer"}}
adj_allele_freq_field = {"adj_af": {"type": "float"}}

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
                    **start_pos_field,
                    **end_pos_field
                }
            },
            "hg18": {
                "properties": {
                    **start_pos_field,
                    **end_pos_field
                }
            },
            "hg38": {
                "properties": {
                    **start_pos_field,
                    **end_pos_field
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

                }
            },
            "protein": {
                "properties": {
                    "aa": {
                        "properties": {
                            "pos": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },

                        }
                    },
                    "genename": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
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
                        "properties": {
                            "annovar": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "snpeff": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "vep": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "hgvsp": {
                        "properties": {
                            "annovar": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "snpeff": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "vep": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "appris": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "gencode_basic": {
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
                    },
                    "sift": {
                        "properties": {
                            **score_field,
                            **pred_field
                        }
                    },
                    "sift4g": {
                        "properties": {
                            **score_field,
                            **pred_field
                        }
                    },
                    "polyphen2": {
                        "properties": {
                            "hdiv": {
                                "properties": {
                                    **score_field,
                                    **pred_field
                                }
                            },
                            "hvar": {
                                "properties": {
                                    **score_field,
                                    **pred_field
                                }
                            }
                        }
                    },
                    "mutationassessor": {
                        "properties": {
                            **score_field,
                            **pred_field,
                        }
                    },
                    "fathmm": {
                        "properties": {
                            **score_field,
                            **pred_field
                        }
                    },
                    "provean": {
                        "properties": {
                            **score_field,
                            **pred_field
                        }
                    },
                    "vest4": {
                        "properties": {
                            **score_field,
                        }
                    },
                    "revel": {
                        "properties": {
                            **score_field,
                        }
                    },
                    "mvp": {
                        "properties": {
                            **score_field,
                        }
                    },
                    "gmvp": {  # new in 4.4.a
                        "properties": {
                            **score_field,
                        }
                    },
                    "mpc": {
                        "properties": {
                            **score_field,
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
                }
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
                    **converted_rankscore_field,
                }
            },
            "sift4g": {
                "properties": {
                    **converted_rankscore_field,
                }
            },
            "polyphen2": {
                "properties": {
                    "hdiv": {
                        "properties": {
                            **rankscore_field,
                        }
                    },
                    "hvar": {
                        "properties": {
                            **rankscore_field,
                        }
                    }
                }
            },
            "lrt": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field,
                    **pred_field,
                    "omega": {
                        "type": "float"
                    }
                }
            },
            "mutationtaster": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field,
                    **pred_field,
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
                    **rankscore_field,
                }
            },
            "fathmm": {
                "properties": {
                    **converted_rankscore_field,
                }
            },
            "provean": {
                "properties": {
                    **converted_rankscore_field,
                }
            },
            "vest4": {
                "properties": {
                    **rankscore_field
                }
            },
            "metasvm": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "metalr": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "reliability_index": {
                "type": "integer"
            },
            "metarnn": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "m-cap": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "revel": {
                "properties": {
                    **rankscore_field
                }
            },
            "mutpred": {
                "properties": {
                    **score_field,
                    **rankscore_field,
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
                    **rankscore_field
                }
            },
            "gmvp": {  # new in 4.4.a
                "properties": {
                    **rankscore_field
                }
            },
            "mpc": {
                "properties": {
                    **rankscore_field
                }
            },
            "primateai": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "deogen2": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "bayesdel": {
                "properties": {
                    "add_af": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **pred_field
                        }
                    },
                    "no_af": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **pred_field
                        }
                    }
                }
            },
            "clinpred": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "list-s2": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "varity": {
                "r": {
                    "properties": {
                        **score_field,
                        **rankscore_field
                    }
                },
                "er": {
                    "properties": {
                        **score_field,
                        **rankscore_field
                    }
                },
                "r_loo": {
                    "properties": {
                        **score_field,
                        **rankscore_field
                    }
                },
                "er_loo": {
                    "properties": {
                        **score_field,
                        **rankscore_field
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
                        "type": "float"  # CADD phred-like scores, not as other predications of string type
                    }
                }
            },
            "dann": {
                "properties": {
                    **score_field,
                    **rankscore_field
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
                    **score_field,
                    **rankscore_field
                }
            },
            # "integrated": {
            #     "properties": {
            #         "fitcons_score": { "type": "float" },
            #         "fitcons_rankscore": { "type": "float" },
            #         "confidence_value": { "type": "integer" }
            #     }
            # },
            # "gm12878": {
            #     "properties": {
            #         "fitcons_score": { "type": "float" },
            #         "fitcons_rankscore": { "type": "float" },
            #         "confidence_value": { "type": "integer" }
            #     }
            # },
            # "h1-hesc": {
            #     "properties": {
            #         "fitcons_score": { "type": "float" },
            #         "fitcons_rankscore": { "type": "float" },
            #         "confidence_value": { "type": "integer" }
            #     }
            # },
            # "huvec": {
            #     "properties": {
            #         "fitcons_score": { "type": "float" },
            #         "fitcons_rankscore": { "type": "float" },
            #         "confidence_value": { "type": "integer" }
            #     }
            # },
            "fitcons": {
                "properties": {
                    "integrated": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **confidence_value_field
                        }
                    },
                    "gm12878": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **confidence_value_field
                        }
                    },
                    "h1-hesc": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **confidence_value_field
                        }
                    },
                    "huvec": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **confidence_value_field
                        }
                    },
                }
            },
            "linsight": {
                "properties": {
                    **score_field,
                    **rankscore_field
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
                            **score_field,
                            **rankscore_field
                        }
                    },
                    "470way_mammalian": {  # replaced 30way_mammalian in 4.4.a
                        "properties": {
                            **score_field,
                            **rankscore_field
                        }
                    },
                    "17way_primate": {
                        "properties": {
                            **score_field,
                            **rankscore_field
                        }
                    }
                }
            },
            "phastcons": {
                "properties": {
                    "100way_vertebrate": {
                        "properties": {
                            **score_field,
                            **rankscore_field
                        }
                    },
                    "470way_mammalian": {  # replaced 30way_mammalian in 4.4.a
                        "properties": {
                            **score_field,
                            **rankscore_field
                        }
                    },
                    "17way_primate": {
                        "properties": {
                            **score_field,
                            **rankscore_field
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
                    **score_field,
                    **converted_rankscore_field
                }
            },
            "1000gp3": {  # changed since 4.4.a
                "properties": {
                    **allele_count_field,
                    **allele_freq_field,
                    # "afr_ac": { "type": "integer" },
                    # "afr_af": { "type": "float" },
                    "afr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "eur_ac": { "type": "integer" },
                    # "eur_af": { "type": "float" },
                    "eur": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "amr_ac": { "type": "integer" },
                    # "amr_af": { "type": "float" },
                    "amr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "eas_ac": { "type": "integer" },
                    # "eas_af": { "type": "float" },
                    "eas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "sas_ac": { "type": "integer" },
                    # "sas_af": { "type": "float"}
                    "sas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    }
                }
            },
            "twinsuk": {
                "properties": {
                    **allele_count_field,
                    **allele_freq_field
                }
            },
            "alspac": {
                "properties": {
                    **allele_count_field,
                    **allele_freq_field
                }
            },
            "uk10k": {
                "properties": {
                    **allele_count_field,
                    **allele_freq_field
                }
            },
            "esp6500": {  # changed since 4.4.a
                "properties": {
                    # "aa_ac": { "type": "integer" },
                    # "aa_af": { "type": "float" },
                    "aa": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "ea_ac": { "type": "integer" },
                    # "ea_af": { "type": "float" }
                    "ea": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                }
            },
            "exac": {  # changed since 4.4.a
                "properties": {
                    **allele_count_field,
                    **allele_freq_field,
                    **adj_allele_count_field,
                    **adj_allele_freq_field,
                    # "afr_ac": { "type": "integer" },
                    # "afr_af": { "type": "float" },
                    "afr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "amr_ac": { "type": "integer" },
                    # "amr_af": { "type": "float" },
                    "amr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "eas_ac": { "type": "integer" },
                    # "eas_af": { "type": "float" },
                    "eas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "fin_ac": { "type": "integer" },
                    # "fin_af": { "type": "float" },
                    "fin": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "nfe_ac": { "type": "integer" },
                    # "nfe_af": { "type": "float" },
                    "nfe": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "sas_ac": { "type": "integer" },
                    # "sas_af": { "type": "float" }
                    "sas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    }
                }
            },
            "exac_nontcga": {  # changed since 4.4.a
                "properties": {
                    **allele_count_field,
                    **allele_freq_field,
                    **adj_allele_count_field,
                    **adj_allele_freq_field,
                    # "afr_ac": { "type": "integer" },
                    # "afr_af": { "type": "float" },
                    "afr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "amr_ac": { "type": "integer" },
                    # "amr_af": { "type": "float" },
                    "amr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "eas_ac": { "type": "integer" },
                    # "eas_af": { "type": "float" },
                    "eas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "fin_ac": { "type": "integer" },
                    # "fin_af": { "type": "float" },
                    "fin": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "nfe_ac": { "type": "integer" },
                    # "nfe_af": { "type": "float" },
                    "nfe": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "sas_ac": { "type": "integer" },
                    # "sas_af": { "type": "float" }
                    "sas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    }
                }
            },
            "exac_nonpsych": {  # changed since 4.4.a
                "properties": {
                    **allele_count_field,
                    **allele_freq_field,
                    **adj_allele_count_field,
                    **adj_allele_freq_field,
                    # "afr_ac": { "type": "integer" },
                    # "afr_af": { "type": "float" },
                    "afr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "amr_ac": { "type": "integer" },
                    # "amr_af": { "type": "float" },
                    "amr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "eas_ac": { "type": "integer" },
                    # "eas_af": { "type": "float" },
                    "eas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "fin_ac": { "type": "integer" },
                    # "fin_af": { "type": "float" },
                    "fin": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "nfe_ac": { "type": "integer" },
                    # "nfe_af": { "type": "float" },
                    "nfe": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    # "sas_ac": { "type": "integer" },
                    # "sas_af": { "type": "float" }
                    "sas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    }
                }
            },
            "alfa": {  # new in 4.4.a
                "properties": {
                    "european": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "african_others": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "east_asian": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "african_american": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "latin_american_1": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "latin_american_2": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "other_asian": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "south_asian": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "other": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "african": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "asian": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
                        }
                    },
                    "total": {
                        "properties": {
                            **allele_count_field,
                            **allele_num_field,
                            **allele_freq_field
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
