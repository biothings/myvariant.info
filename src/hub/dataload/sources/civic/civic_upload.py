import glob, os

import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader

from .civic_parser import load_data

class CivicUploader(uploader.IgnoreDuplicatedSourceUploader,SnpeffPostUpdateUploader):

    name = "civic"
    __metadata__ = {
        "mapper" : 'observed',
        "assembly" : "hg19",
        "src_meta" : {
            "url" : "https://civicdb.org",
            "license_url" : "https://creativecommons.org/publicdomain/zero/1.0/",
            "license_url_short": "http://bit.ly/2FqS871",
            "licence" : "CC0 1.0 Universal"
        }
    }

    def load_data(self, data_folder):
        self.logger.info("Load data from '%s'" % data_folder)
        return load_data(data_folder)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "civic": {
                "properties": {
                    "entrez_name": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "entrez_id": {
                        "type": "integer"
                    },
                    "name": {
                        "type": "text"
                    },
                    "description": {
                        "type": "text"
                    },
                    "gene_id": {
                        "type": "integer"
                    },
                    "type": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "variant_types": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "so_id": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "url": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "display_name": {
                                "type": "text"
                            },
                            "description": {
                                "type": "text"
                            }
                        }
                    },
                    "civic_actionability_score": {
                        "type": "float"
                    },
                    "coordinates": {
                        "properties": {
                            "chromosome": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "representative_transcript": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "chromosome2": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "start2": {
                                "type": "integer"
                            },
                            "stop2": {
                                "type": "integer"
                            },
                            "representative_transcript2": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "ensembl_version": {
                                "type": "integer"
                            },
                            "reference_build": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "reference_bases": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "variant_bases": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            }
                        }
                    },
                    "evidence_items": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "url": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
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
                                    }
                                }
                            },
                            "rating": {
                                "type": "integer"
                            },
                            "evidence_level": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "evidence_type": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "status": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "open_change_count": {
                                "type": "integer"
                            },
                            "type": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                                        "type": "text"
                                    },
                                    "source_url": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
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
                                        "type": "text"
                                    },
                                    "full_journal_title": {
                                        "type": "text"
                                    },
                                    "status": {
                                        "type": "text"
                                    },
                                    "is_review": {
                                        "type": "boolean"
                                    },
                                    "pubmed": {
                                        "type": "integer"
                                    },
                                    "open_access": {
                                        "type": "boolean"
                                    },
                                    "pmc_id": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "clinical_trials": {
                                        "properties": {
                                            "nct_id": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "name": {
                                                "type": "text"
                                            },
                                            "description": {
                                                "type": "text"
                                            },
                                            "clinical_trial_url": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            }
                                        }
                                    },
                                    "asco_abstract_id": {
                                        "type": "integer"
                                    },
                                    "asco": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "variant_id": {
                                "type": "integer"
                            },
                            "drug_interaction_type": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "phenotypes": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "hpo_id": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "url": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "hpo_class": {
                                        "type": "text"
                                    }
                                }
                            },
                            "evidence_direction": {
                                "type": "text"
                            },
                            "clinical_significance": {
                                "type": "text"
                            },
                            "description": {
                                "type": "text"
                            },
                            "variant_origin": {
                                "type": "text"
                            }
                        }
                    },
                    "variant_aliases": {
                        "type": "text"
                    },
                    "sources": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "citation_id": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "source_type": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "source_url": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
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
                            "is_review": {
                                "type": "boolean"
                            },
                            "open_access": {
                                "type": "boolean"
                            },
                            "pmc_id": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "name": {
                                "type": "text"
                            },
                            "citation": {
                                "type": "text"
                            },
                            "journal": {
                                "type": "text"
                            },
                            "full_journal_title": {
                                "type": "text"
                            },
                            "status": {
                                "type": "text"
                            }
                        }
                    },
                    "variant_id": {
                        "type": "integer"
                    },
                    "assertions": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "type": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "name": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "gene": {
                                "properties": {
                                    "name": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "variant": {
                                "properties": {
                                    "name": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                }
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
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "url": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    }
                                }
                            },
                            "drugs": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    }
                                }
                            },
                            "evidence_type": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "evidence_direction": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "clinical_significance": {
                                "type": "text"
                            },
                            "evidence_item_count": {
                                "type": "integer"
                            },
                            "fda_regulatory_approval": {
                                "type": "boolean"
                            },
                            "status": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "open_change_count": {
                                "type": "integer"
                            },
                            "pending_evidence_count": {
                                "type": "integer"
                            },
                            "summary": {
                                "type": "text"
                            },
                            "description": {
                                "type": "text"
                            }
                        }
                    },
                    "variant_groups": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "variants": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "entrez_name": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "entrez_id": {
                                        "type": "integer"
                                    },
                                    "gene_id": {
                                        "type": "integer"
                                    },
                                    "type": {
                                        "type": "keyword",
                                        "normalizer": "keyword_lowercase_normalizer"
                                    },
                                    "variant_types": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "so_id": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "url": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "display_name": {
                                                "type": "text"
                                            },
                                            "description": {
                                                "type": "text"
                                            }
                                        }
                                    },
                                    "civic_actionability_score": {
                                        "type": "float"
                                    },
                                    "coordinates": {
                                        "properties": {
                                            "chromosome": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "start": {
                                                "type": "integer"
                                            },
                                            "stop": {
                                                "type": "integer"
                                            },
                                            "representative_transcript": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "chromosome2": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "start2": {
                                                "type": "integer"
                                            },
                                            "stop2": {
                                                "type": "integer"
                                            },
                                            "representative_transcript2": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "ensembl_version": {
                                                "type": "integer"
                                            },
                                            "reference_build": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "reference_bases": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            },
                                            "variant_bases": {
                                                "type": "keyword",
                                                "normalizer": "keyword_lowercase_normalizer"
                                            }
                                        }
                                    },
                                    "name": {
                                        "type": "text"
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "type": {
                                "type": "keyword",
                                "normalizer": "keyword_lowercase_normalizer"
                            },
                            "name": {
                                "type": "text"
                            },
                            "description": {
                                "type": "text"
                            }
                        }
                    },
                    "clinvar_entries": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "provisional_values": {
                        "properties": {
                            "description": {
                                "properties": {
                                    "value": {
                                        "type": "text"
                                    },
                                    "revision_id": {
                                        "type": "integer"
                                    }
                                }
                            }
                        }
                    },
                    "hgvs_expressions": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    },
                    "allele_registry_id": {
                        "type": "keyword",
                        "normalizer": "keyword_lowercase_normalizer"
                    }
                }
            }
        }

        return mapping

