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
            "sift": {  # Column 37-39
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
            "sift4g": {  # Column 40-42
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
            "polyphen2": {  # Column 43-48
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
            "lrt": {  # Column 49-52
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
            "mutationtaster": {  # Column 53-57
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
            "mutationassessor": {  # Column 58-60
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
            "fathmm": {  # Column 61-63
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
            "provean": {  # Column 64-66
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
            "vest4": {  # Column 67-68
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "metasvm": {  # Column 69-71
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
            "metalr": {  # Column 72-74
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
            "reliability_index": {  # Column 75
                "type": "integer"
            },
            "metarnn": {  # Column 76-78
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
            "m-cap": {  # Column 79-81
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
            "revel": {  # Column 82-83
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "mutpred": {  # Column 84-88
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
            "mvp": {  # Column 89-90
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "mpc": {  # Column 91-92
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "primateai": {  # Column 93-95
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
            "deogen2": {  # Column 96-98
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
            "bayesdel": {  # Column 43-48
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
            "clinpred": {  # Column 105-107
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
            "list-s2": {  # Column 108-110
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
            "aloft": {  # Column 111-116
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
            "cadd": {  # Column 117-119
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
            "dann": {  # Column 123-124
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "fathmm-mkl": {  # Column 125-128
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
            "fathmm-xf": {  # Column 129-131
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
            "eigen": {  # Column 132-134
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
            "eigen-pc": {  # Column 135-137
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
            "genocanyon": {  # Column 138-139
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "integrated": {  # Column 140-142
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
            "gm12878": {  # Column 143-145
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
            "h1-hesc": {  # Column 146-148
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
            "huvec": {  # Column 149-151
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
            "linsight": {  # Column 152-153
                "properties": {
                    "score": {
                        "type": "float"
                    },
                    "rankscore": {
                        "type": "float"
                    }
                }
            },
            "gerp++": {  # Column 154-156
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
            "phylop": {  # Column 157-162
                "properties": {
                    "vertebrate": {
                        "properties": {
                            "track": {
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
                    "mammal": {
                        "properties": {
                            "track": {
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
                    "primate": {
                        "properties": {
                            "track": {
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
            "phastcons": {  # Column 163-168
                "properties": {
                    "vertebrate": {
                        "properties": {
                            "track": {
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
                    "mammal": {
                        "properties": {
                            "track": {
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
                    "primate": {
                        "properties": {
                            "track": {
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
            "siphy": {  # Column 169-171
                "properties": {
                    "mammal": {
                        "properties": {
                            "track": {
                                "type": "text"
                            },
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
                    }
                }
            },
            "bstatistic": {  # Column 172-173
                "properties": {
                    "score": {
                        "type": "integer"
                    },
                    "converted_rankscore": {
                        "type": "float"
                    }
                }
            },
            "1000gp3": {  # Column 174-185
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
            "twinsuk": {  # Column 186-187
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "af": {
                        "type": "float"
                    }
                }
            },
            "alspac": {  # Column 188-189
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "af": {
                        "type": "float"
                    }
                }
            },
            "uk10k": {  # Column 190-191
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "af": {
                        "type": "float"
                    }
                }
            },
            "esp6500": {  # Column 192-195
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
            "exac": {  # Column 196-211
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
            "exac_nontcga": {  # Column 212-227
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
            "exac_nonpsych": {  # Column 228-243
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
            # Column 245-629 are gnomAD_* columns. Skipped.
            "clinvar": {  # Column 630-638
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
            "interpro_domain": {  # Column 639
                "type": "text"
            },
            "gtex": {  # Column 640-641
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
            "geuvadis_eqtl_target_gene": {  # Column 642
                "type": "keyword",
                "normalizer": "keyword_lowercase_normalizer"
            }
        }
    }
}