def get_mapping():
    mapping = {
        "snpeff": {
            "properties": {
                "ann": {
                    "properties": {
                        "effect": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "putative_impact": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "gene_name": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "gene_id": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "feature_type": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "feature_id": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "transcript_biotype": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "rank": {
                            "type": "long"
                        },
                        "total": {
                            "type": "long"
                        },
                        "hgvs_c": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "hgvs_p": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "cdna": {
                            "properties": {
                                "position": {
                                    "type": "long"
                                },
                                "length": {
                                    "type": "long"
                                }
                            }
                        },
                        "cds": {
                            "properties": {
                                "position": {
                                    "type": "long"
                                },
                                "length": {
                                    "type": "long"
                                }
                            }
                        },
                        "protein": {
                            "properties": {
                                "position": {
                                    "type": "long"
                                },
                                "length": {
                                    "type": "long"
                                }
                            }
                        },
                        "distance_to_feature": {
                            "type": "long"
                        }
                    }
                },
                "lof": {
                    "properties": {
                        "gene_id": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "gene_name": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "number_of_transcripts_in_gene": {
                            "type": "integer"
                        },
                        "percent_of_transcripts_affected": {
                            "type": "float"
                        }
                    }
                },
                "nmd": {
                    "properties": {
                        "gene_id": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "gene_name": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "number_of_transcripts_in_gene": {
                            "type": "integer"
                        },
                        "percent_of_transcripts_affected": {
                            "type": "float"
                        }
                    }
                }
            }
        },
        "vcf": {
            "properties": {
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "position": {
                    "type": "long"
                }
            }
        }
    }
    return mapping
