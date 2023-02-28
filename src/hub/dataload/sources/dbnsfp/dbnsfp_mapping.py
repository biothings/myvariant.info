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
            "genename": {  # Column 13
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "ensembl": {  # Column 14-16
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
            "uniprot": {  # Column 17-18
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
            "hgvsc": {  # Column 19-21
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "hgvsp": {  # Column 22-24
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "appris": {  # Column 25
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "genecode_basic": {  # Column 26
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "tsl": {  # Column 27
                "type": "integer"
            },
            "vep_canonical": {  # Column 28
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "cds_strand": {  # Column 29
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "ancestral_allele": {  # Column 33
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "altai_neandertal": {  # Column 34
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "denisova": {  # Column 35
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "vindijia_neandertal": {  # Column 36
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "chagyrskaya_neandertal": {  # Column 37
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            },
            "sift": {  # Column 38-40
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
            "sift4g": {  # Column 41-43
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
            "polyphen2": {  # Column 44-49
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
            "lrt": {  # Column 50-53
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
            "mutationtaster": {  # Column 54-58
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
            "mutationassessor": {  # Column 59-61
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
            "fathmm": {  # Column 62-64
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
            "provean": {  # Column 65-67
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
            "vest4": {  # Column 68-69
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "metasvm": {  # Column 70-72
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
            "metalr": {  # Column 73-75
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
            "reliability_index": {  # Column 76
                "type": "integer"
            },
            "metarnn": {  # Column 77-79
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
            "m-cap": {  # Column 80-82
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
            "revel": {  # Column 83-84
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "mutpred": {  # Column 85-89
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
            "mvp": {  # Column 90-91
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "mpc": {  # Column 92-93
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "primateai": {  # Column 94-96
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
            "deogen2": {  # Column 97-99
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
            "bayesdel": {  # Column 100-105
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
            "clinpred": {  # Column 106-108
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
            "list-s2": {  # Column 109-111
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
            "aloft": {  # Column 112-117
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
            "cadd": {
                # Column 118-123
                #   Column 118-120 are hg38
                #   Column 121-123 are hg19
                # Only column 117-119 will be included in the document for "hg38"
                # No CADD fields will be included when "hg19"
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
            "dann": {  # Column 124-125
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "fathmm-mkl": {  # Column 126-129
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
            "fathmm-xf": {  # Column 130-132
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
            "eigen": {  # Column 133-135
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
            "eigen-pc": {  # Column 136-138
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
            "genocanyon": {  # Column 139-140
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "integrated": {  # Column 141-143
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
            "gm12878": {  # Column 144-146
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
            "h1-hesc": {  # Column 147-149
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
            "huvec": {  # Column 150-152
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
            "linsight": {  # Column 153-154
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "gerp++": {  # Column 155-157
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
            "phylop": {  # Column 158-163
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
                    "30way_mammalian": {
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
            "phastcons": {  # Column 164-169
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
                    "30way_mammalian": {
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
            "siphy_29way": {  # Column 170-172
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
            "bstatistic": {  # Column 173-174
                "properties": {
                    "score": {
                        "type": "integer"
                    },
                    "converted_rankscore": {
                        "type": "float"
                    }
                }
            },
            "1000gp3": {  # Column 175-186
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
            "twinsuk": {  # Column 187-188
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "af": {
                        "type": "float"
                    }
                }
            },
            "alspac": {  # Column 189-190
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "af": {
                        "type": "float"
                    }
                }
            },
            "uk10k": {  # Column 191-192
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "af": {
                        "type": "float"
                    }
                }
            },
            "esp6500": {  # Column 193-196
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
            "exac": {  # Column 197-212
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
            "exac_nontcga": {  # Column 213-228
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
            "exac_nonpsych": {  # Column 229-244
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

            # Column 245-630 are gnomAD_* columns. Skipped.

            "clinvar": {  # Column 631-639
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
                    "medgen": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "orphanet": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "var_source": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    }
                }
            },
            "interpro_domain": {  # Column 640
                "type": "text"
            },
            "gtex": {  # Column 641-642
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
            "geuvadis_eqtl_target_gene": {  # Column 643
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            }
        }
    }
}