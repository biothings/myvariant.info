import biothings.hub.dataload.uploader as uploader
from ...uploader import SnpeffPostUpdateUploader

class CivicUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):

    name = "civic"
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "https://civic.genome.wustl.edu/home",
                "license_url" : "https://civic.genome.wustl.edu/faq",
                "license_url_short": "https://goo.gl/gPCAyH",
                "licence" : "CC0 1.0 Universal",
                }
            }

    @classmethod
    def get_mapping(klass):
        mapping = {
            "civic": {
                "properties": {
                    "variant_id": {
                        "type": "integer"
                    },
                    "entrez_name": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "include_in_all": True
                    },
                    "entrez_id": {
                        "type": "integer"
                    },
                    "name": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "description": {
                        "type": "string"
                    },
                    "gene_id": {
                        "type": "integer"
                    },
                    "type": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "variant_types": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "display_name": {
                                "type": "string"
                            },
                            "so_id": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "description": {
                                "type": "string"
                            },
                            "url": {
                                "index": "no",
                                "type": "string",
                            }
                        }
                    },
                    "coordinates": {
                        "properties": {
                            "chromosome": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "reference_bases": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "variant_bases": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "representative_transcript": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "chromosome2": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "start2": {
                                "type": "integer"
                            },
                            "stop2": {
                                "type": "integer"
                            },
                            "representative_transcript2": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "ensembl_version": {
                                "type": "integer"
                            },
                            "reference_build": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "evidence_items": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "description": {
                                "type": "string"
                            },
                            "disease": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "display_name": {
                                        "type": "string"
                                    },
                                    "doid": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "url": {
                                        "index": "no",
                                        "type": "string"
                                    }
                                }
                            },
                            "drugs": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "pubchem_id": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    }
                                }
                            },
                            "rating": {
                                "type": "integer"
                            },
                            "evidence_level": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "clinical_siginificance": {
                                "type": "string"
                            },
                            "evidence_direction": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "variant_origin": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "drug_interaction_type": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "status": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "open_change_count": {
                                "type": "integer"
                            },
                            "type": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "source": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "string"
                                    },
                                    "citation": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "pubmed_id": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "source_url": {
                                        "index": "no",
                                        "type": "string",
                                    },
                                    "open_access": {
                                        "type": "boolean"
                                    },
                                    "pmc_id": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "publication_date": {
                                        "properties": {
                                            "year": {
                                                "type": "integer"
                                            },
                                            "month": {
                                                "type": "integer"
                                            },
                                            "day": {
                                                "type": "integer"
                                            }
                                        }
                                    },
                                    "journal": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "full_journal_title": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "status": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "is_review": {
                                        "type": "boolean"
                                    }
                                }
                            },
                            "variant_id": {
                                "type": "integer"
                            }
                        }
                    },
                    "variant_groups": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "variants": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "entrez_name": {
                                        "type": "string",
                                        "analyzer": "string_lowercase",
                                        "include_in_all": True
                                    },
                                    "entrez_id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "description": {
                                        "type": "string"
                                    },
                                    "gene_id": {
                                        "type": "integer"
                                    },
                                    "type": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "variant_types": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "display_name": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "so_id": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "description": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "url": {
                                                "index": "no",
                                                "type": "string",
                                            }
                                        }
                                    },
                                    "coordinates": {
                                        "properties": {
                                            "chromosome": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "start": {
                                                "type": "integer"
                                            },
                                            "stop": {
                                                "type": "integer"
                                            },
                                            "reference_bases": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "variant_bases": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "representative_transcript": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "chromosome2": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "start2": {
                                                "type": "integer"
                                            },
                                            "stop2": {
                                                "type": "integer"
                                            },
                                            "representative_transcript2": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "ensembl_version": {
                                                "type": "integer"
                                            },
                                            "reference_build": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            }
                                        }
                                    }
                                }
                            },
                            "type": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "variant_aliases": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "hgvs_expressions": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "clinvar_entries": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "lifecycle_actions": {
                        "properties": {
                            "last_modified": {
                                "properties": {
                                    "order": {
                                        "type": "integer"
                                    },
                                    "timestamp": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "user": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "last_seen_at": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "username": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "role": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "avatar_url": {
                                                "index": "no",
                                                "type": "string",
                                            },
                                            #"avatars": {
                                            #    "index": "no",
                                            #},
                                            "area_of_expertise": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "orcid": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "display_name": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "created_at": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "url": {
                                                "index": "no",
                                                "type": "string",
                                            },
                                            "twitter_handle": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "facebook_profile": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "linkedin_profile": {
                                                "index":"no",
                                                "type":"string",
                                            },
                                            "bio": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "featured_expert": {
                                                "type": "boolean"
                                            },
                                            "affiliation": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "organization": {
                                                "properties": {
                                                    "id": {
                                                        "type": "integer"
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "analyzer": "string_lowercase"
                                                    },
                                                    "url": {
                                                        "index": "no",
                                                        "type": "string",
                                                    },
                                                    "description": {
                                                        "type": "string",
                                                        "analyzer": "string_lowercase"
                                                    },
                                                    #"profile_image": {
                                                    #    "index":"no",
                                                    #}
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "last_reviewed": {
                                "properties": {
                                    "order": {
                                        "type": "integer"
                                    },
                                    "timestamp": {
                                        "type": "string",
                                        "analyzer": "string_lowercase"
                                    },
                                    "user": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "last_seen_at": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "username": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "role": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "avatar_url": {
                                                "index": "no",
                                                "type": "string",
                                            },
                                            #"avatars": {
                                            #    "index": "no",
                                            #},
                                            "area_of_expertise": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "orcid": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "display_name": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "created_at": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "url": {
                                                "index": "no",
                                                "type":"string",
                                            },
                                            "twitter_handle": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "facebook_profile": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "linkedin_profile": {
                                                "index": "no",
                                                "type":"string",
                                            },
                                            "bio": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "featured_expert": {
                                                "type": "boolean"
                                            },
                                            "affiliation": {
                                                "type": "string",
                                                "analyzer": "string_lowercase"
                                            },
                                            "organization": {
                                                "properties": {
                                                    "id": {
                                                        "type": "integer"
                                                    },
                                                    "name": {
                                                        "type": "string",
                                                        "analyzer": "string_lowercase"
                                                    },
                                                    "url": {
                                                        "index": "no",
                                                        "type":"string",
                                                    },
                                                    "description": {
                                                        "type": "string",
                                                        "analyzer": "string_lowercase"
                                                    },
                                                    #"profile_image": {
                                                    #    "index":"no",
                                                    #}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return mapping

