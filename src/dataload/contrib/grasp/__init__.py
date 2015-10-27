# -*- coding: utf-8 -*-

from .grasp_parser import load_data as _load_data

GRASP_INPUT_FILE = '/opt/myvariant.info/load_archive/grasp/GRASP2fullDataset'

__METADATA__ = {
    "src_name": 'grasp',
    "src_url": 'https://s3.amazonaws.com/NHLBI_Public/GRASP/GraspFullDataset2.zip',
    "version": '2.0.0.0',
    "field": 'grasp'
}

def load_data():
    grasp_data = _load_data(GRASP_INPUT_FILE)
    return grasp_data


def get_mapping():
    mapping = {
        "grasp": {
            "properties": {
                "hg19": {
                    "properties": {
                        "chr": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "pos": {
                            "type": "long"
                        }
                    }
                },
                "srsid": {
                    "type": "long"
                },
                "hugfield": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "publication": {
                    "properties": {
                        "journal": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "title": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "pmid": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "snpid": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "location_within_paper": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "p_value": {
                            "type": "float"
                        },
                        "phenotype": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "paper_phenotype_description": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "paper_phenotype_categories": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                },
                "includes_male_female_only_analyses": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "exclusively_male_female": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "initial_sample_description": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "replication_sample_description": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "platform_snps_passing_qc": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "gwas_ancestry_description": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "discovery": {
                    "properties": {
                        "total_samples": {
                            "type": "integer"
                        },
                        "european": {
                            "type": "integer"
                        },
                        "african": {
                            "type": "integer"
                        },
                        "east_asian": {
                            "type": "integer"
                        },
                        "indian_south_asian": {
                            "type": "integer"
                        },
                        "hispanic": {
                            "type": "integer"
                        },
                        "native": {
                            "type": "integer"
                        },
                        "micronesian": {
                            "type": "integer"
                        },
                        "arab_me": {
                            "type": "integer"
                        },
                        "mixed": {
                            "type": "integer"
                        },
                        "unspecified": {
                            "type": "integer"
                        },
                        "filipino": {
                            "type": "integer"
                        },
                        "indonesian": {
                            "type": "integer"
                        }
                    }
                },
                "replication": {
                    "properties": {
                        "total_samples": {
                            "type": "integer"
                        },
                        "european": {
                            "type": "integer"
                        },
                        "african": {
                            "type": "integer"
                        },
                        "east_asian": {
                            "type": "integer"
                        },
                        "indian_south_asian": {
                            "type": "integer"
                        },
                        "hispanic": {
                            "type": "integer"
                        },
                        "native": {
                            "type": "integer"
                        },
                        "micronesian": {
                            "type": "integer"
                        },
                        "arab_me": {
                            "type": "integer"
                        },
                        "mixed": {
                            "type": "integer"
                        },
                        "unspecified": {
                            "type": "integer"
                        },
                        "filipino": {
                            "type": "integer"
                        },
                        "indonesian": {
                            "type": "integer"
                        }
                    }
                },
                "in_gene": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "nearest_gene": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "in_mirna": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "in_mirna_bs": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "oreg_anno": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "human_enhancer": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "rna_edit": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "polyphen2": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "sift": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "uniprot": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "eqtl_meth_metab_study": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
