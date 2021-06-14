from .gnomad_v2_parser import population_frequency_parser as pfp_v2
from .gnomad_v3_parser import population_frequency_parser as pfp_v3

population_frequency_sub_mapping_v2 = {
    "ac": {
        "properties": {
            pfp_v2.get_field_name(key): {"type": "integer"} for key in pfp_v2.keys["AC"]
        }
    },
    "an": {
        "properties": {
            pfp_v2.get_field_name(key): {"type": "integer"} for key in pfp_v2.keys["AN"]
        }
    },
    "hom": {
        "properties": {
            pfp_v2.get_field_name(key): {"type": "integer"} for key in pfp_v2.keys["nhomalt"]
        }
    },
    "af": {
        "properties": {
            pfp_v2.get_field_name(key): {"type": "float"} for key in pfp_v2.keys["AF"]
        }
    }
}

population_frequency_sub_mapping_v3 = {
    "ac": {
        "properties": {
            pfp_v3.get_field_name(key): {"type": "integer"} for key in pfp_v3.keys["AC"]
        }
    },
    "an": {
        "properties": {
            pfp_v3.get_field_name(key): {"type": "integer"} for key in pfp_v3.keys["AN"]
        }
    },
    "hom": {
        "properties": {
            pfp_v3.get_field_name(key): {"type": "integer"} for key in pfp_v3.keys["nhomalt"]
        }
    },
    "af": {
        "properties": {
            pfp_v3.get_field_name(key): {"type": "float"} for key in pfp_v3.keys["AF"]
        }
    }
}

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

site_quality_metrics_sub_mapping_v2 = {
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

site_quality_metrics_sub_mapping_v3 = {
    "inbreedingcoeff": {
        "type": "float"
    },
    "as_fs": {
        "type": "float"
    },
    "as_mq": {
        "properties": {
            "as_mq": {
                "type": "float"
            },
            "as_mqranksum": {
                "type": "float"
            }
        }
    },
    "as_pab_max": {
        "type": "float"
    },
    "as_qd": {
        "type": "float"
    },
    "as_readposranksum": {
        "type": "float"
    },
    "as_sor": {
        "type": "float"
    },
    "as_vqslod": {
        "type": "float"
    }
}


exomes_mapping_v2 = {
    "gnomad_exome": {
        "properties": {
            **profile_sub_mapping,

            **site_quality_metrics_sub_mapping_v2,
            **population_frequency_sub_mapping_v2
        }
    }
}


genomes_mapping_v2 = {
    "gnomad_genome": {
        "properties": {
            **profile_sub_mapping,

            **site_quality_metrics_sub_mapping_v2,
            **population_frequency_sub_mapping_v2
        }
    }
}

genomes_mapping_v3 = {
    "gnomad_genome": {
        "properties": {
            **profile_sub_mapping,

            **site_quality_metrics_sub_mapping_v3,
            **population_frequency_sub_mapping_v3
        }
    }
}
