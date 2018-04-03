import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader

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
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "copy_to": ["all"],
                    },
                    "entrez_id": {
                        "type": "integer"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "description": {
                        "type": "text"
                    },
                    "gene_id": {
                        "type": "integer"
                    },
                    "type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "variant_types": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "display_name": {
                                "type": "text"
                            },
                            "so_id": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "description": {
                                "type": "text"
                            },
                            "url": {
                                "index" : False,
                                "type": "text",
                            }
                        }
                    },
                    "coordinates": {
                        "properties": {
                            "chromosome": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "reference_bases": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "variant_bases": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "representative_transcript": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "chromosome2": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "start2": {
                                "type": "integer"
                            },
                            "stop2": {
                                "type": "integer"
                            },
                            "representative_transcript2": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "ensembl_version": {
                                "type": "integer"
                            },
                            "reference_build": {
                                "type": "text",
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
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "description": {
                                "type": "text"
                            },
                            "disease": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "text"
                                    },
                                    "display_name": {
                                        "type": "text"
                                    },
                                    "doid": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "url": {
                                        "index" : False,
                                        "type": "text"
                                    }
                                }
                            },
                            "drugs": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "text"
                                    },
                                    "pubchem_id": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    }
                                }
                            },
                            "rating": {
                                "type": "integer"
                            },
                            "evidence_level": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "clinical_siginificance": {
                                "type": "text"
                            },
                            "evidence_direction": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "variant_origin": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "drug_interaction_type": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "status": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "open_change_count": {
                                "type": "integer"
                            },
                            "type": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "source": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "text"
                                    },
                                    "citation": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "pubmed_id": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "source_url": {
                                        "index" : False,
                                        "type": "text",
                                    },
                                    "open_access": {
                                        "type": "boolean"
                                    },
                                    "pmc_id": {
                                        "type": "text",
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
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "full_journal_title": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "status": {
                                        "type": "text",
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
                                "type": "text"
                            },
                            "description": {
                                "type": "text"
                            },
                            "variants": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "entrez_name": {
                                        "type": "text",
                                        "analyzer": "string_lowercase",
                                        "copy_to": ["all"],
                                    },
                                    "entrez_id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "description": {
                                        "type": "text"
                                    },
                                    "gene_id": {
                                        "type": "integer"
                                    },
                                    "type": {
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "variant_types": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "display_name": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "so_id": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "description": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "url": {
                                                "index": False,
                                                "type": "text",
                                            }
                                        }
                                    },
                                    "coordinates": {
                                        "properties": {
                                            "chromosome": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "start": {
                                                "type": "integer"
                                            },
                                            "stop": {
                                                "type": "integer"
                                            },
                                            "reference_bases": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "variant_bases": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "representative_transcript": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "chromosome2": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "start2": {
                                                "type": "integer"
                                            },
                                            "stop2": {
                                                "type": "integer"
                                            },
                                            "representative_transcript2": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "ensembl_version": {
                                                "type": "integer"
                                            },
                                            "reference_build": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            }
                                        }
                                    }
                                }
                            },
                            "type": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "variant_aliases": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "hgvs_expressions": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "clinvar_entries": {
                        "type": "text",
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
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "user": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "last_seen_at": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "username": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "role": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "avatar_url": {
                                                "index" : False,
                                                "type": "text",
                                            },
                                            #"avatars": {
                                            #    "index" : False,
                                            #},
                                            "area_of_expertise": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "orcid": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "display_name": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "created_at": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "url": {
                                                "index" : False,
                                                "type": "text",
                                            },
                                            "twitter_handle": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "facebook_profile": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "linkedin_profile": {
                                                "index" : False,
                                                "type":"text",
                                            },
                                            "bio": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "featured_expert": {
                                                "type": "boolean"
                                            },
                                            "affiliation": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "organization": {
                                                "properties": {
                                                    "id": {
                                                        "type": "integer"
                                                    },
                                                    "name": {
                                                        "type": "text",
                                                        "analyzer": "string_lowercase"
                                                    },
                                                    "url": {
                                                        "index" : False,
                                                        "type": "text",
                                                    },
                                                    "description": {
                                                        "type": "text",
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
                                        "type": "text",
                                        "analyzer": "string_lowercase"
                                    },
                                    "user": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "last_seen_at": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "username": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "role": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "avatar_url": {
                                                "index" : False,
                                                "type": "text",
                                            },
                                            #"avatars": {
                                            #    "index" : False,
                                            #},
                                            "area_of_expertise": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "orcid": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "display_name": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "created_at": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "url": {
                                                "index" : False,
                                                "type":"text",
                                            },
                                            "twitter_handle": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "facebook_profile": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "linkedin_profile": {
                                                "index" : False,
                                                "type":"text",
                                            },
                                            "bio": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "featured_expert": {
                                                "type": "boolean"
                                            },
                                            "affiliation": {
                                                "type": "text",
                                                "analyzer": "string_lowercase"
                                            },
                                            "organization": {
                                                "properties": {
                                                    "id": {
                                                        "type": "integer"
                                                    },
                                                    "name": {
                                                        "type": "text",
                                                        "analyzer": "string_lowercase"
                                                    },
                                                    "url": {
                                                        "index" : False,
                                                        "type":"text",
                                                    },
                                                    "description": {
                                                        "type": "text",
                                                        "analyzer": "string_lowercase"
                                                    },
                                                    #"profile_image": {
                                                    #    "index":False,
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

