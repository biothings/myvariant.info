start_pos_field = {"start": {"type": "integer"}}
end_pos_field = {"end": {"type": "integer"}}

score_field = {"score": {"type": "float"}}
converted_rankscore_field = {"converted_rankscore": {"type": "float"}}
rankscore_field = {"rankscore": {"type": "float"}}
confidence_value_field = {"confidence_value": {"type": "integer"}}
keyword_value_field = {
    "type": "keyword",
    "normalizer": "keyword_lowercase_normalizer"
}
pred_field = {"pred": keyword_value_field}

allele_count_field = {"ac": {"type": "integer"}}
allele_num_field = {"an": {"type": "integer"}}
allele_freq_field = {"af": {"type": "float"}}
adj_allele_count_field = {"adj_ac": {"type": "integer"}}
adj_allele_freq_field = {"adj_af": {"type": "float"}}

mapping = {
    "dbnsfp": {
        "properties": {
            "rsid": keyword_value_field,
            "chrom": keyword_value_field,
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
            "ref": keyword_value_field,
            "alt": keyword_value_field,
            "aa": {
                "properties": {
                    "ref": keyword_value_field,
                    "alt": keyword_value_field,
                    "pos": keyword_value_field,
                    "refcodon": keyword_value_field,
                    "codonpos": keyword_value_field,
                    "codon_degeneracy": keyword_value_field
                }
            },
            "genename": keyword_value_field,
            "ensembl": {
                "properties": {
                    "geneid": keyword_value_field,
                    "transcriptid": keyword_value_field,
                    "proteinid": keyword_value_field
                }
            },
            "uniprot": {
                "properties": {
                    "acc": keyword_value_field,
                    "entry": keyword_value_field
                }
            },
            "hgvsc": keyword_value_field,
            "hgvsp": keyword_value_field,
            "appris": keyword_value_field,
            "gencode_basic": keyword_value_field,
            "tsl": {
                "type": "integer"
            },
            "vep_canonical": keyword_value_field,
            "cds_strand": keyword_value_field,
            "ancestral_allele": keyword_value_field,
            "altai_neandertal": keyword_value_field,
            "denisova": keyword_value_field,
            "vindijia_neandertal": keyword_value_field,
            "chagyrskaya_neandertal": keyword_value_field,
            "sift": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field,
                    **pred_field
                }
            },
            "sift4g": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field,
                    **pred_field
                }
            },
            "polyphen2": {
                "properties": {
                    "hdiv": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **pred_field
                        }
                    },
                    "hvar": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            **pred_field
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
                    **converted_rankscore_field,
                    "analysis": {  # see prune_mutation_taster()
                        "properties": {
                            **pred_field,
                            **score_field,
                            "model": keyword_value_field,
                            "aae": {
                                "type": "text"
                            }
                        }
                    }
                }
            },
            "mutationassessor": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field,
                }
            },
            "fathmm": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field,
                    **pred_field
                }
            },
            "provean": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field,
                    **pred_field
                }
            },
            "vest4": {
                "properties": {
                    **score_field,
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
                    **score_field,
                    **rankscore_field
                }
            },
            "mutpred": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    "accession": keyword_value_field,
                    "aa_change": keyword_value_field,
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
                    **score_field,
                    **rankscore_field
                }
            },
            "gmvp": {  # new in 4.4.a
                "properties": {
                    **score_field,
                    **rankscore_field
                }
            },
            "mpc": {
                "properties": {
                    **score_field,
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
            "aloft": {
                "properties": {
                    "fraction_transcripts_affected": keyword_value_field,
                    "prob_tolerant": keyword_value_field,
                    "prob_recessive": keyword_value_field,
                    "prob_dominant": keyword_value_field,
                    "pred": keyword_value_field,
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
                    "coding_pred": keyword_value_field,
                    "coding_group": keyword_value_field
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
                    "coding_pred": keyword_value_field
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
                    "clinvar_id": keyword_value_field,
                    "clinsig": keyword_value_field,
                    "trait": keyword_value_field,
                    "review": keyword_value_field,
                    "hgvs": keyword_value_field,
                    "var_source": keyword_value_field,
                    "medgen": keyword_value_field,
                    "omim": keyword_value_field,
                    "orphanet": keyword_value_field
                }
            },
            "interpro_domain": {
                "type": "text"
            },
            "geuvadis_eqtl_target_gene": keyword_value_field,
            "esm1b": {  # new in 4.5.a
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "eve": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    "class10_pred": keyword_value_field,
                    "class20_pred": keyword_value_field,
                    "class25_pred": keyword_value_field,
                    "class30_pred": keyword_value_field,
                    "class40_pred": keyword_value_field,
                    "class50_pred": keyword_value_field,
                    "class60_pred": keyword_value_field,
                    "class70_pred": keyword_value_field,
                    "class75_pred": keyword_value_field,
                    "class80_pred": keyword_value_field,
                    "class90_pred": keyword_value_field
                }
            },
            "alphamissense": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "gtex": {  # new in 4.6.a
                "properties": {
                    "eqtl": {
                        "properties": {
                            "gene": keyword_value_field,
                            "tissue": {
                                "type": "text"
                            }
                        }
                    },
                    "sqtl": {
                        "properties": {
                            "gene": keyword_value_field,
                            "tissue": {
                                "type": "text"
                            }
                        }
                    }
                }
            },
            "eqtlgen": {
                "properties": {
                    "snp_id": keyword_value_field,
                    "gene_id": keyword_value_field,
                    "gene_symbol": keyword_value_field,
                    "cis_or_trans": keyword_value_field
                }
            }
        }
    }
}
