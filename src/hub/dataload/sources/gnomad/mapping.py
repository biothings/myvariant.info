profile_sub_mapping = {
    "chrom": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    },
    "pos": {
        "type": "integer"
    },
    "filter": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    },
    "multi-allelic": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    },
    "ref": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    },
    "alt": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    },
    "alleles": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    },
    "type": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    },
    "rsid": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    }
}

site_quality_metrics_sub_mapping = {
    "baseqranksum": {
        "type": "float"
    },
    "clippingranksum": {
        "type": "float"
    },
    "dp": {
        "type": "float"
    },
    "fs": {
        "type": "float"
    },
    "inbreedingcoeff": {
        "type": "float"
    },
    "mq": {
        "properties": {
            "mq": {
                "type": "float"
            },
            "mqranksum": {
                "type": "float"
            }
        }
    },
    "pab_max": {
        "type": "float"
    },
    "qd": {
        "type": "float"
    },
    "readposranksum": {
        "type": "float"
    },
    "rf": {
        "type": "float"
    },
    "sor": {
        "type": "float"
    },
    "vqslod": {
        "type": "float"
    },
    "vqsr_culprit": {
        "normalizer": "keyword_lowercase_normalizer",
        "type": "keyword"
    }
}


exomes_mapping = {
    "gnomad_exome": {
        "properties": {
            **profile_sub_mapping,
            **site_quality_metrics_sub_mapping,
            "ac": {
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "ac_nfe_seu": {
                        "type": "integer"
                    },
                    "ac_raw": {
                        "type": "integer"
                    },
                    "ac_fin_female": {
                        "type": "integer"
                    },
                    "ac_nfe_bgr": {
                        "type": "integer"
                    },
                    "ac_sas_male": {
                        "type": "integer"
                    },
                    "ac_afr_male": {
                        "type": "integer"
                    },
                    "ac_afr": {
                        "type": "integer"
                    },
                    "ac_eas_female": {
                        "type": "integer"
                    },
                    "ac_afr_female": {
                        "type": "integer"
                    },
                    "ac_sas": {
                        "type": "integer"
                    },
                    "ac_nfe_onf": {
                        "type": "integer"
                    },
                    "ac_fin_male": {
                        "type": "integer"
                    },
                    "ac_nfe_female": {
                        "type": "integer"
                    },
                    "ac_amr": {
                        "type": "integer"
                    },
                    "ac_eas": {
                        "type": "integer"
                    },
                    "ac_asj_male": {
                        "type": "integer"
                    },
                    "ac_oth_female": {
                        "type": "integer"
                    },
                    "ac_nfe_swe": {
                        "type": "integer"
                    },
                    "ac_nfe_nwe": {
                        "type": "integer"
                    },
                    "ac_eas_jpn": {
                        "type": "integer"
                    },
                    "ac_female": {
                        "type": "integer"
                    },
                    "ac_eas_kor": {
                        "type": "integer"
                    },
                    "ac_eas_oea": {
                        "type": "integer"
                    },
                    "ac_nfe_est": {
                        "type": "integer"
                    },
                    "ac_eas_male": {
                        "type": "integer"
                    },
                    "ac_nfe": {
                        "type": "integer"
                    },
                    "ac_fin": {
                        "type": "integer"
                    },
                    "ac_nfe_male": {
                        "type": "integer"
                    },
                    "ac_sas_female": {
                        "type": "integer"
                    },
                    "ac_asj_female": {
                        "type": "integer"
                    },
                    "ac_asj": {
                        "type": "integer"
                    },
                    "ac_oth": {
                        "type": "integer"
                    },
                    "ac_male": {
                        "type": "integer"
                    },
                    "ac_amr_male": {
                        "type": "integer"
                    },
                    "ac_amr_female": {
                        "type": "integer"
                    },
                    "ac_oth_male": {
                        "type": "integer"
                    },
                    "ac_popmax": {
                        "type": "integer"
                    }
                }
            },
            "af": {
                "properties": {
                    "af": {
                        "type": "float"
                    },
                    "af_nfe_seu": {
                        "type": "float"
                    },
                    "af_raw": {
                        "type": "float"
                    },
                    "af_fin_female": {
                        "type": "float"
                    },
                    "af_nfe_bgr": {
                        "type": "float"
                    },
                    "af_sas_male": {
                        "type": "float"
                    },
                    "af_afr_male": {
                        "type": "float"
                    },
                    "af_afr": {
                        "type": "float"
                    },
                    "af_eas_female": {
                        "type": "float"
                    },
                    "af_afr_female": {
                        "type": "float"
                    },
                    "af_sas": {
                        "type": "float"
                    },
                    "af_nfe_onf": {
                        "type": "float"
                    },
                    "af_fin_male": {
                        "type": "float"
                    },
                    "af_nfe_female": {
                        "type": "float"
                    },
                    "af_amr": {
                        "type": "float"
                    },
                    "af_eas": {
                        "type": "float"
                    },
                    "af_asj_male": {
                        "type": "float"
                    },
                    "af_oth_female": {
                        "type": "float"
                    },
                    "af_nfe_swe": {
                        "type": "float"
                    },
                    "af_nfe_nwe": {
                        "type": "float"
                    },
                    "af_eas_jpn": {
                        "type": "float"
                    },
                    "af_female": {
                        "type": "float"
                    },
                    "af_eas_kor": {
                        "type": "float"
                    },
                    "af_eas_oea": {
                        "type": "float"
                    },
                    "af_nfe_est": {
                        "type": "float"
                    },
                    "af_eas_male": {
                        "type": "float"
                    },
                    "af_nfe": {
                        "type": "float"
                    },
                    "af_fin": {
                        "type": "float"
                    },
                    "af_nfe_male": {
                        "type": "float"
                    },
                    "af_sas_female": {
                        "type": "float"
                    },
                    "af_asj_female": {
                        "type": "float"
                    },
                    "af_asj": {
                        "type": "float"
                    },
                    "af_oth": {
                        "type": "float"
                    },
                    "af_male": {
                        "type": "float"
                    },
                    "af_amr_male": {
                        "type": "float"
                    },
                    "af_amr_female": {
                        "type": "float"
                    },
                    "af_oth_male": {
                        "type": "float"
                    },
                    "af_popmax": {
                        "type": "float"
                    }
                }
            },
            "an": {
                "properties": {
                    "an": {
                        "type": "integer"
                    },
                    "an_nfe_seu": {
                        "type": "integer"
                    },
                    "an_raw": {
                        "type": "integer"
                    },
                    "an_fin_female": {
                        "type": "integer"
                    },
                    "an_nfe_bgr": {
                        "type": "integer"
                    },
                    "an_sas_male": {
                        "type": "integer"
                    },
                    "an_afr_male": {
                        "type": "integer"
                    },
                    "an_afr": {
                        "type": "integer"
                    },
                    "an_eas_female": {
                        "type": "integer"
                    },
                    "an_afr_female": {
                        "type": "integer"
                    },
                    "an_sas": {
                        "type": "integer"
                    },
                    "an_nfe_onf": {
                        "type": "integer"
                    },
                    "an_fin_male": {
                        "type": "integer"
                    },
                    "an_nfe_female": {
                        "type": "integer"
                    },
                    "an_amr": {
                        "type": "integer"
                    },
                    "an_eas": {
                        "type": "integer"
                    },
                    "an_asj_male": {
                        "type": "integer"
                    },
                    "an_oth_female": {
                        "type": "integer"
                    },
                    "an_nfe_swe": {
                        "type": "integer"
                    },
                    "an_nfe_nwe": {
                        "type": "integer"
                    },
                    "an_eas_jpn": {
                        "type": "integer"
                    },
                    "an_female": {
                        "type": "integer"
                    },
                    "an_eas_kor": {
                        "type": "integer"
                    },
                    "an_eas_oea": {
                        "type": "integer"
                    },
                    "an_nfe_est": {
                        "type": "integer"
                    },
                    "an_eas_male": {
                        "type": "integer"
                    },
                    "an_nfe": {
                        "type": "integer"
                    },
                    "an_fin": {
                        "type": "integer"
                    },
                    "an_nfe_male": {
                        "type": "integer"
                    },
                    "an_sas_female": {
                        "type": "integer"
                    },
                    "an_asj_female": {
                        "type": "integer"
                    },
                    "an_asj": {
                        "type": "integer"
                    },
                    "an_oth": {
                        "type": "integer"
                    },
                    "an_male": {
                        "type": "integer"
                    },
                    "an_amr_male": {
                        "type": "integer"
                    },
                    "an_amr_female": {
                        "type": "integer"
                    },
                    "an_oth_male": {
                        "type": "integer"
                    },
                    "an_popmax": {
                        "type": "integer"
                    }
                }
            },
            "hom": {
                "properties": {
                    "hom": {
                        "type": "integer"
                    },
                    "hom_nfe_seu": {
                        "type": "integer"
                    },
                    "hom_raw": {
                        "type": "integer"
                    },
                    "hom_fin_female": {
                        "type": "integer"
                    },
                    "hom_nfe_bgr": {
                        "type": "integer"
                    },
                    "hom_sas_male": {
                        "type": "integer"
                    },
                    "hom_afr_male": {
                        "type": "integer"
                    },
                    "hom_afr": {
                        "type": "integer"
                    },
                    "hom_eas_female": {
                        "type": "integer"
                    },
                    "hom_afr_female": {
                        "type": "integer"
                    },
                    "hom_sas": {
                        "type": "integer"
                    },
                    "hom_nfe_onf": {
                        "type": "integer"
                    },
                    "hom_fin_male": {
                        "type": "integer"
                    },
                    "hom_nfe_female": {
                        "type": "integer"
                    },
                    "hom_amr": {
                        "type": "integer"
                    },
                    "hom_eas": {
                        "type": "integer"
                    },
                    "hom_asj_male": {
                        "type": "integer"
                    },
                    "hom_oth_female": {
                        "type": "integer"
                    },
                    "hom_nfe_swe": {
                        "type": "integer"
                    },
                    "hom_nfe_nwe": {
                        "type": "integer"
                    },
                    "hom_eas_jpn": {
                        "type": "integer"
                    },
                    "hom_female": {
                        "type": "integer"
                    },
                    "hom_eas_kor": {
                        "type": "integer"
                    },
                    "hom_eas_oea": {
                        "type": "integer"
                    },
                    "hom_nfe_est": {
                        "type": "integer"
                    },
                    "hom_eas_male": {
                        "type": "integer"
                    },
                    "hom_nfe": {
                        "type": "integer"
                    },
                    "hom_fin": {
                        "type": "integer"
                    },
                    "hom_nfe_male": {
                        "type": "integer"
                    },
                    "hom_sas_female": {
                        "type": "integer"
                    },
                    "hom_asj_female": {
                        "type": "integer"
                    },
                    "hom_asj": {
                        "type": "integer"
                    },
                    "hom_oth": {
                        "type": "integer"
                    },
                    "hom_male": {
                        "type": "integer"
                    },
                    "hom_amr_male": {
                        "type": "integer"
                    },
                    "hom_amr_female": {
                        "type": "integer"
                    },
                    "hom_oth_male": {
                        "type": "integer"
                    },
                    "hom_popmax": {
                        "type": "integer"
                    }
                }
            },
        }
    }
}


genomes_mapping = {
    "gnomad_genome": {
        "properties": {
            **profile_sub_mapping,
            **site_quality_metrics_sub_mapping,
            "ac": {
                "properties": {
                    "ac": {
                        "type": "integer"
                    },
                    "ac_nfe_seu": {
                        "type": "integer"
                    },
                    "ac_raw": {
                        "type": "integer"
                    },
                    "ac_fin_female": {
                        "type": "integer"
                    },
                    "ac_afr_male": {
                        "type": "integer"
                    },
                    "ac_afr": {
                        "type": "integer"
                    },
                    "ac_eas_female": {
                        "type": "integer"
                    },
                    "ac_afr_female": {
                        "type": "integer"
                    },
                    "ac_nfe_onf": {
                        "type": "integer"
                    },
                    "ac_fin_male": {
                        "type": "integer"
                    },
                    "ac_nfe_female": {
                        "type": "integer"
                    },
                    "ac_amr": {
                        "type": "integer"
                    },
                    "ac_eas": {
                        "type": "integer"
                    },
                    "ac_asj_male": {
                        "type": "integer"
                    },
                    "ac_oth_female": {
                        "type": "integer"
                    },
                    "ac_nfe_nwe": {
                        "type": "integer"
                    },
                    "ac_female": {
                        "type": "integer"
                    },
                    "ac_nfe_est": {
                        "type": "integer"
                    },
                    "ac_eas_male": {
                        "type": "integer"
                    },
                    "ac_nfe": {
                        "type": "integer"
                    },
                    "ac_fin": {
                        "type": "integer"
                    },
                    "ac_nfe_male": {
                        "type": "integer"
                    },
                    "ac_asj_female": {
                        "type": "integer"
                    },
                    "ac_asj": {
                        "type": "integer"
                    },
                    "ac_oth": {
                        "type": "integer"
                    },
                    "ac_male": {
                        "type": "integer"
                    },
                    "ac_amr_male": {
                        "type": "integer"
                    },
                    "ac_amr_female": {
                        "type": "integer"
                    },
                    "ac_oth_male": {
                        "type": "integer"
                    },
                    "ac_popmax": {
                        "type": "integer"
                    }
                }
            },
            "af": {
                "properties": {
                    "af_raw": {
                        "type": "float"
                    },
                    "af": {
                        "type": "float"
                    },
                    "af_fin_female": {
                        "type": "float"
                    },
                    "af_afr_male": {
                        "type": "float"
                    },
                    "af_afr": {
                        "type": "float"
                    },
                    "af_afr_female": {
                        "type": "float"
                    },
                    "af_nfe_onf": {
                        "type": "float"
                    },
                    "af_fin_male": {
                        "type": "float"
                    },
                    "af_nfe_female": {
                        "type": "float"
                    },
                    "af_amr": {
                        "type": "float"
                    },
                    "af_nfe_nwe": {
                        "type": "float"
                    },
                    "af_female": {
                        "type": "float"
                    },
                    "af_nfe_est": {
                        "type": "float"
                    },
                    "af_nfe": {
                        "type": "float"
                    },
                    "af_fin": {
                        "type": "float"
                    },
                    "af_nfe_male": {
                        "type": "float"
                    },
                    "af_male": {
                        "type": "float"
                    },
                    "af_amr_female": {
                        "type": "float"
                    },
                    "af_asj_male": {
                        "type": "float"
                    },
                    "af_oth_female": {
                        "type": "float"
                    },
                    "af_asj": {
                        "type": "float"
                    },
                    "af_oth": {
                        "type": "float"
                    },
                    "af_oth_male": {
                        "type": "float"
                    },
                    "af_popmax": {
                        "type": "float"
                    },
                    "af_eas": {
                        "type": "float"
                    },
                    "af_eas_male": {
                        "type": "float"
                    },
                    "af_eas_female": {
                        "type": "float"
                    },
                    "af_amr_male": {
                        "type": "float"
                    },
                    "af_asj_female": {
                        "type": "float"
                    },
                    "af_nfe_seu": {
                        "type": "float"
                    }
                }
            },
            "an": {
                "properties": {
                    "an": {
                        "type": "integer"
                    },
                    "an_nfe_seu": {
                        "type": "integer"
                    },
                    "an_raw": {
                        "type": "integer"
                    },
                    "an_fin_female": {
                        "type": "integer"
                    },
                    "an_afr_male": {
                        "type": "integer"
                    },
                    "an_afr": {
                        "type": "integer"
                    },
                    "an_eas_female": {
                        "type": "integer"
                    },
                    "an_afr_female": {
                        "type": "integer"
                    },
                    "an_nfe_onf": {
                        "type": "integer"
                    },
                    "an_fin_male": {
                        "type": "integer"
                    },
                    "an_nfe_female": {
                        "type": "integer"
                    },
                    "an_amr": {
                        "type": "integer"
                    },
                    "an_eas": {
                        "type": "integer"
                    },
                    "an_asj_male": {
                        "type": "integer"
                    },
                    "an_oth_female": {
                        "type": "integer"
                    },
                    "an_nfe_nwe": {
                        "type": "integer"
                    },
                    "an_female": {
                        "type": "integer"
                    },
                    "an_nfe_est": {
                        "type": "integer"
                    },
                    "an_eas_male": {
                        "type": "integer"
                    },
                    "an_nfe": {
                        "type": "integer"
                    },
                    "an_fin": {
                        "type": "integer"
                    },
                    "an_nfe_male": {
                        "type": "integer"
                    },
                    "an_asj_female": {
                        "type": "integer"
                    },
                    "an_asj": {
                        "type": "integer"
                    },
                    "an_oth": {
                        "type": "integer"
                    },
                    "an_male": {
                        "type": "integer"
                    },
                    "an_amr_male": {
                        "type": "integer"
                    },
                    "an_amr_female": {
                        "type": "integer"
                    },
                    "an_oth_male": {
                        "type": "integer"
                    },
                    "an_popmax": {
                        "type": "integer"
                    }
                }
            },
            "hom": {
                "properties": {
                    "hom": {
                        "type": "integer"
                    },
                    "hom_nfe_seu": {
                        "type": "integer"
                    },
                    "hom_raw": {
                        "type": "integer"
                    },
                    "hom_fin_female": {
                        "type": "integer"
                    },
                    "hom_nfe_bgr": {
                        "type": "integer"
                    },
                    "hom_sas_male": {
                        "type": "integer"
                    },
                    "hom_afr_male": {
                        "type": "integer"
                    },
                    "hom_afr": {
                        "type": "integer"
                    },
                    "hom_eas_female": {
                        "type": "integer"
                    },
                    "hom_afr_female": {
                        "type": "integer"
                    },
                    "hom_sas": {
                        "type": "integer"
                    },
                    "hom_nfe_onf": {
                        "type": "integer"
                    },
                    "hom_fin_male": {
                        "type": "integer"
                    },
                    "hom_nfe_female": {
                        "type": "integer"
                    },
                    "hom_amr": {
                        "type": "integer"
                    },
                    "hom_eas": {
                        "type": "integer"
                    },
                    "hom_asj_male": {
                        "type": "integer"
                    },
                    "hom_oth_female": {
                        "type": "integer"
                    },
                    "hom_nfe_swe": {
                        "type": "integer"
                    },
                    "hom_nfe_nwe": {
                        "type": "integer"
                    },
                    "hom_eas_jpn": {
                        "type": "integer"
                    },
                    "hom_female": {
                        "type": "integer"
                    },
                    "hom_eas_kor": {
                        "type": "integer"
                    },
                    "hom_eas_oea": {
                        "type": "integer"
                    },
                    "hom_nfe_est": {
                        "type": "integer"
                    },
                    "hom_eas_male": {
                        "type": "integer"
                    },
                    "hom_nfe": {
                        "type": "integer"
                    },
                    "hom_fin": {
                        "type": "integer"
                    },
                    "hom_nfe_male": {
                        "type": "integer"
                    },
                    "hom_sas_female": {
                        "type": "integer"
                    },
                    "hom_asj_female": {
                        "type": "integer"
                    },
                    "hom_asj": {
                        "type": "integer"
                    },
                    "hom_oth": {
                        "type": "integer"
                    },
                    "hom_male": {
                        "type": "integer"
                    },
                    "hom_amr_male": {
                        "type": "integer"
                    },
                    "hom_amr_female": {
                        "type": "integer"
                    },
                    "hom_oth_male": {
                        "type": "integer"
                    },
                    "hom_popmax": {
                        "type": "integer"
                    }
                }
            },
        }
    }
}
