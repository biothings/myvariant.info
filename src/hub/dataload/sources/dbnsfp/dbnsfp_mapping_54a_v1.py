start_pos_field = {"start": {"type": "integer"}}
end_pos_field = {"end": {"type": "integer"}}

score_field = {"score": {"type": "float"}}
converted_rankscore_field = {"converted_rankscore": {"type": "float"}}
rankscore_field = {"rankscore": {"type": "float"}}
keyword_value_field = {
    "type": "keyword",
    "normalizer": "keyword_lowercase_normalizer"
}
pred_field = {"pred": keyword_value_field}

allele_count_field = {"ac": {"type": "integer"}}
allele_num_field = {"an": {"type": "integer"}}
allele_freq_field = {"af": {"type": "float"}}

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
            "hs1": {  # new in dbNSFP 5.3.1 (T2T-CHM13 v2.0 coordinates)
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
            "ensembl_canonical": keyword_value_field,  # renamed from vep_canonical (source column VEP_canonical -> Ensembl_canonical) in dbNSFP 5.4
            "mane": keyword_value_field,  # new in dbNSFP 5.0
            "cds_strand": keyword_value_field,
            "ancestral_allele": keyword_value_field,
            "altai_neandertal": keyword_value_field,
            "denisova": keyword_value_field,
            "vindijia_neandertal": keyword_value_field,
            "chagyrskaya_neandertal": keyword_value_field,
            "clinvar": {
                "properties": {
                    "clinvar_id": keyword_value_field,
                    "clnsig": keyword_value_field,
                    "trait": keyword_value_field,
                    "review": keyword_value_field,
                    "hgvs": keyword_value_field,
                    "var_source": keyword_value_field,
                    "medgen": keyword_value_field,
                    "omim": keyword_value_field,
                    "orphanet": keyword_value_field
                }
            },
            "interpro": {
                "properties": {
                    "domain": {
                        "type": "text"
                    }
                }
            },
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
            # LRT retired by dbNSFP 5.0
            "mutationtaster": {
                # MutationTaster2021 (dbNSFP 5.0): MutationTaster_AAE retired, trees_benign/trees_deleterious added.
                # v1 has no per-transcript merge step for this field (unlike v2's "analysis" list), so it stays flat.
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field,
                    "model": keyword_value_field,
                    "trees_benign": {
                        "type": "integer"
                    },
                    "trees_deleterious": {
                        "type": "integer"
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
            # FATHMM retired by dbNSFP 5.0
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
            "mutpred2": {  # replaces MutPred (v1) in dbNSFP 5.2
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field,
                    "mechanisms": {
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
            "gmvp": {
                "properties": {
                    **score_field,
                    **rankscore_field
                }
            },
            "misfit": {  # new in dbNSFP 5.3
                "properties": {
                    "d": {
                        "properties": {
                            **score_field,
                            **rankscore_field,
                            "pred_lenient": keyword_value_field,
                            "pred_stringent": keyword_value_field
                        }
                    },
                    "s": {
                        "properties": {
                            **score_field,
                            **rankscore_field
                        }
                    }
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
                "properties": {
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
                }
            },
            "esm1b": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field,  # renamed from ESM1b_rankscore in dbNSFP 5.2
                    **pred_field
                }
            },
            # EVE retired by dbNSFP 5.0
            "alphamissense": {
                "properties": {
                    **score_field,
                    **rankscore_field,
                    **pred_field
                }
            },
            "phactboost": {
                "properties": {
                    **score_field,
                    **rankscore_field
                }
            },
            "mutformer": {
                "properties": {
                    **score_field,
                    **rankscore_field
                }
            },
            "mutscore": {  # new in dbNSFP 4.9a
                "properties": {
                    **score_field,
                    **rankscore_field
                }
            },
            "popeve": {  # new in dbNSFP 5.3.1
                "properties": {
                    **score_field,
                    **pred_field,
                    **converted_rankscore_field
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
                    "phred": {
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
            # fathmm-MKL retired by dbNSFP 5.0
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
            "gpn_msa": {  # new in dbNSFP 5.4
                "properties": {
                    **score_field,
                    **converted_rankscore_field,
                    **pred_field
                }
            },
            # GenoCanyon retired by dbNSFP 5.0
            # fitCons (integrated, GM12878, H1-hESC, HUVEC) retired by dbNSFP 5.0
            # LINSIGHT retired by dbNSFP 5.0
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
            "gerp": {
                "properties": {
                    "92_mammals": {  # renamed from 91_mammals in dbNSFP 5.3
                        "properties": {
                            **score_field,
                            **rankscore_field
                        }
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
                    "470way_mammalian": {
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
                    "470way_mammalian": {
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
            # SiPhy retired by dbNSFP 5.0
            "bstatistic": {
                "properties": {
                    **score_field,
                    **converted_rankscore_field
                }
            },
            "1000gp3": {
                "properties": {
                    **allele_count_field,
                    **allele_freq_field,
                    "afr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    "eur": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    "amr": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    "eas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    },
                    "sas": {
                        "properties": {
                            **allele_count_field,
                            **allele_freq_field
                        }
                    }
                }
            },
            # TWINSUK, ALSPAC, UK10K, ESP6500, ExAC, ExAC_nonTCGA, ExAC_nonpsych retired by dbNSFP 5.0
            # TOPMed freeze8, gnomAD2.1.1 exomes controls/non_neuro/non_cancer, gnomAD4.1 joint, All of Us, and
            # RegeneronME are in the file but not parsed here (counted in VALID_COLUMN_NO only), consistent with
            # gnomAD never being expanded into individual columns in earlier versions either (e.g. 4.8a)
            "alfa": {
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
            "dbnsfp_popmax": {  # new in dbNSFP 5.1
                "properties": {
                    **allele_freq_field,
                    **allele_count_field,
                    "pop": keyword_value_field
                }
            }
            # GTEx, eQTLGen, and Geuvadis eQTL columns retired by dbNSFP 5.0
        }
    }
}
