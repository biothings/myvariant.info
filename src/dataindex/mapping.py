#ES mapping

def get_mapping():
    m = {
        "variant": {
            "include_in_all": False,
            "dynamic": False,
            "properties": {}
        }
    }
    for _m in [mapping_dbsnp, mapping_mutdb, mapping_snpedia,
               mapping_gwassnps, mapping_cosmic, mapping_docm,
               mapping_dbnsfp, mapping_emv, mapping_clinvar,
               mapping_evs]:
        m['variant']['properties'].update(_m)
    return m


mapping = {
    'mappings': {
        "_default_": {
        #    "_all": { "enabled":  false }
        },
        'variant': {
            "include_in_all": False,
            "dynamic": False,
            "dynamic_templates": [
            #     { "es": {
            #           "match":              "*_es",
            #           "match_mapping_type": "string",
            #           "mapping": {
            #               "type":           "string",
            #               "analyzer":       "spanish"
            #           }
            #     }},
                {
                    "lowercase_keyword": {
                        "match": "*",
                        "match_mapping_type": "string",
                        "mapping": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                }
            ]
        }
    }
}

mapping_dbsnp = {
    "dbsnp": {
        "properties": {
            "rsid": {
                "type": "string",
                "include_in_all": True,
                "analyzer": "string_lowercase"
            },
            "func": {
                "type": "string"
            },
            "snpclass": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "allele1": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "allele2": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chrom": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chromStart": {
                "type": "long"
            },
            "chromEnd": {
                "type": "long"
            },
            "strand": {
                "type": "string",
                "index": "not_analyzed"
            }
        }
    }
}

mapping_mutdb = {
    "mutdb": {
        "properties": {
            "dbsnp_id": {
                "type": "string",
                "include_in_all": True,
                "analyzer": "string_lowercase",
            },
            "allele1": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "allele2": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "uniprot_id": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "mutpred_score": {
                "type": "double"
            },
            "cosmic_id": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chrom": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chromStart": {
                "type": "long"
            },
            "chromEnd": {
                "type": "long"
            },
            "strand": {
                "type": "string",
                "index": "not_analyzed"
            }
        }
    }
}

mapping_snpedia = {
    "snpedia": {
        "properties": {
            "text": {
                "type": "string"
            }
        }
    }
}

mapping_cosmic = {
    "cosmic": {
        "properties": {
            "tumor_site": {
                "type": "string"
            },
            # "tomour_site": {
            #     "type": "string"
            # }
            "mut_freq": {
                "type": "double"    # actual values are string type
            },
            "mut_nt": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "allele1": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "allele2": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chrom": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chromStart": {
                "type": "long"
            },
            "chromEnd": {
                "type": "long"
            }
        }
    }
}

mapping_gwassnps = {
    "gwassnps": {
        "properties": {
            "trait": {
                "type": "string"
            },
            "pubmedID": {
                "type": "long"
            },
            "rsid": {
                "type": "string",
                "include_in_all": True,
                "analyzer": "string_lowercase"
            },
            "allele1": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "allele2": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chrom": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chromStart": {
                "type": "long"
            },
            "chromEnd": {
                "type": "long"
            }
        }
    }
}

mapping_docm = {
    "docm": {
        "properties": {
            "domain": {
                "type": "string"
            },
            "all_domains": {
                "type": "string"
            },
            "reference": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "variant": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "primary": {
                "type": "byte"           # just 0 or 1
            },
            "transcript_species": {
                "type": "string",
                "index": "no"
            },
            "ensembl_gene_id": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "transcript_version": {
                "type": "string",
                "index": "no"
            },
            "transcript_source": {
                "type": "string",
                "index": "no"
            },
            "source": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "pubmed_id": {
                "type": "string",
                "index": "not_analyzed"
            },
            "type": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "DOID": {
                "type": "string",
                "analyzer": "string_lowercase",
                "index_name": "doid"
            },
            "c_position": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "start": {
                "type": "long"
            },
            "stop": {
                "type": "long"
            },
            "strand": {
                "type": "byte",
                "index": "no"
            },
            "deletion_substructures": {
                "type": "string",
                "index": "no"
            },
            "gene_name_source": {
                "type": "string",
                "index": "no"
            },
            "default_gene_name": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "amino_acid_change": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "url": {
                "type": "string",
                "index": "no"
            },
            "transcript_status": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "trv_type": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "disease": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "transcript_name": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "chromosome_name": {
                "type": "string",                 # actual value is integer
                "analyzer": "string_lowercase"
            },
            "transcript_error": {
                "type": "string",
                "index": "no"
            },
            "gene_name": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "ucsc_cons": {
                "type": "double"
            }
        }
    }
}


mapping_dbnsfp = {
    "dbnsfp": {
        "properties": {
            "aa": {
                "properties": {
                    "alt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "ref": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "genename": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "slr_test_statistic": {
                "type": "double"
            },
            "mutationassessor": {
                "properties": {
                    "pred": {
                        "type": "string"
                    },
                    "score": {
                        "type": "double"
                    },
                    "rankscore": {
                        "type": "double"
                    }
                }
            },
            "polyphen2": {
                "properties": {
                    "hdiv": {
                        "properties": {
                            "pred": {
                                "type": "string"
                            },
                            "score": {
                                "type": "double"
                            },
                            "rankscore": {
                                "type": "double"
                            }
                        }
                    },
                    "hvar": {
                        "properties": {
                            "pred": {
                                "type": "string"
                            },
                            "score": {
                                "type": "double"
                            },
                            "rankscore": {
                                "type": "double"
                            }
                        }
                    }
                }
            },
            "phastcons46way": {
                "properties": {
                    "primate_rankscore": {
                        "type": "double"
                    },
                    "primate": {
                        "type": "double"
                    },
                    "vertebrate": {
                        "type": "double"
                    },
                    "vertebrate_rankscore": {
                        "type": "double"
                    },
                    "placental_rankscore": {
                        "type": "double"
                    },
                    "placental": {
                        "type": "double"
                    }
                }
            },
            "aapos": {
                "type": "long"
            },
            "cadd": {
                "properties": {
                    "phred": {
                        "type": "double"
                    },
                    "raw": {
                        "type": "double"
                    },
                    "raw_rankscore": {
                        "type": "double"
                    }
                }
            },
            "siphy_29way_pi_logodds_rankscore": {
                "type": "double"
            },
            "phylop46way": {
                "properties": {
                    "primate_rankscore": {
                        "type": "double"
                    },
                    "primate": {
                        "type": "double"
                    },
                    "vertebrate": {
                        "type": "double"
                    },
                    "vertebrate_rankscore": {
                        "type": "double"
                    },
                    "placental_rankscore": {
                        "type": "double"
                    },
                    "placental": {
                        "type": "double"
                    }
                }
            },
            "lrt_omega": {
                "type": "double"
            },
            "vest3": {
                "properties": {
                    "score": {
                        "type": "double"
                    },
                    "rankscore": {
                        "type": "double"
                    }
                }
            },
            "interpro_domain": {
                "type": "string"
            },
            "reliability_index": {
                "type": "long"
            },
            "fathmm": {
                "properties": {
                    "pred": {
                        "type": "string"
                    },
                    "score": {
                        "type": "double"
                    },
                    "rankscore": {
                        "type": "double"
                    }
                }
            },
            "mutationtaster": {
                "properties": {
                    "converted_rankscore": {
                        "type": "double"
                    },
                    "pred": {
                        "type": "string"
                    },
                    "score": {
                        "type": "double"
                    }
                }
            },
            "lr": {
                "properties": {
                    "pred": {
                        "type": "string"
                    },
                    "score": {
                        "type": "double"
                    },
                    "rankscore": {
                        "type": "double"
                    }
                }
            },
            "esp6500": {
                "properties": {
                    "ea_af": {
                        "type": "double"
                    },
                    "aa_af": {
                        "type": "double"
                    }
                }
            },
            "refcodon": {
                "type": "string"
            },
            "ancestral_allele": {
                "type": "string"
            },
            "uniprot": {
                "properties": {
                    "acc": {
                        "type": "string"
                    },
                    "pos": {
                        "type": "string"
                    }
                }
            },
            "aapos_sift": {
                "type": "string"
            },
            "allele2": {
                "type": "string"
            },
            "allele1": {
                "type": "string"
            },
            "fold-degenerate": {
                "type": "long"
            },
            "aapos_fathmm": {
                "type": "string"
            },
            "sift": {
                "properties": {
                    "converted_rankscore": {
                        "type": "double"
                    },
                    "pred": {
                        "type": "string"
                    },
                    "score": {
                        "type": "long"
                    }
                }
            },
            "lrt": {
                "properties": {
                    "converted_rankscore": {
                        "type": "double"
                    },
                    "pred": {
                        "type": "string"
                    },
                    "score": {
                        "type": "double"
                    }
                }
            },
            "chrom": {
                "type": "string"
            },
            "1000gp1": {
                "properties": {
                    "eur_af": {
                        "type": "double"
                    },
                    "ac": {
                        "type": "long"
                    },
                    "eur_ac": {
                        "type": "long"
                    },
                    "af": {
                        "type": "double"
                    },
                    "amr_ac": {
                        "type": "long"
                    },
                    "asn_af": {
                        "type": "double"
                    },
                    "afr_af": {
                        "type": "double"
                    },
                    "amr_af": {
                        "type": "double"
                    },
                    "afr_ac": {
                        "type": "long"
                    },
                    "asn_ac": {
                        "type": "long"
                    }
                }
            },
            "radialsvm": {
                "properties": {
                    "pred": {
                        "type": "string"
                    },
                    "score": {
                        "type": "double"
                    },
                    "rankscore": {
                        "type": "double"
                    }
                }
            },
            "siphy_29way_pi_logodds": {
                "type": "double"
            },
            "siphy_29way_pi": {
                "properties": {
                    "a": {
                        "type": "double"
                    },
                    "c": {
                        "type": "double"
                    },
                    "t": {
                        "type": "double"
                    },
                    "g": {
                        "type": "double"
                    }
                }
            },
            "codonpos": {
                "type": "long"
            },
            "gerp++": {
                "properties": {
                    "rs_rankscore": {
                        "type": "double"
                    },
                    "nr": {
                        "type": "double"
                    },
                    "rs": {
                        "type": "double"
                    }
                }
            },
            "ensembl": {
                "properties": {
                    "transcriptid": {
                        "type": "string"
                    },
                    "geneid": {
                        "type": "string"
                    }
                }
            },
            "hg18": {
                "properties": {
                    "start": {
                        "type": "long"
                    },
                    "end": {
                        "type": "long"
                    }
                }
            },
            "hg19": {
                "properties": {
                    "start": {
                        "type": "long"
                    },
                    "end": {
                        "type": "long"
                    }
                }
            },
            "cds_strand": {
                "type": "string"
            },
            "unisnp_ids": {
                "type": "string"
            }
        }
    }
}

mapping_emv = {
    "emv": {
        "properties": {
            "egl_classification": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "egl_protein": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "egl_variant": {
                "type": "string",
                "analyzer": "string_lowercase",
                "include_in_all": True
            },
            "gene": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "variant_aka_list": {
                "type": "string",
                "analyzer": "string_lowercase",
                "include_in_all": True
            }
        }
    }
}

mapping_clinvar = {
    "clinvar": {
        "properties": {
            "clinical_significance": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "genome": {
                "properties": {
                    "chr": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "start": {
                        "type": "long"
                    },
                    "end": {
                        "type": "long"
                    }
                }
            },
            "gene": {
                "properties": {
                    "symbol": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    }
                }
            },
            "type": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "origin": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "variant_id": {
                "type": "long"
            }
        }
    }
}

mapping_evs = {
    "evs": {
        "properties": {
            "clinical_info": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "function_gvs": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "grantham_score": {
                "type": "float"
            },
            "rs_id": {
                "type": "string",
                "analyzer": "string_lowercase"
            }
        }
    }
}
