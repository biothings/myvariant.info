import glob, os

import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader
from hub.dataload.storage import MyVariantIgnoreDuplicatedStorage

from .civic_parser import load_data

class CivicUploader(SnpeffPostUpdateUploader):

    name = "civic"
    storage_class = MyVariantIgnoreDuplicatedStorage
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
            "clinvar": {
                "properties": {
                    "allele_id": {
                        "type": "integer"
                    },
                    "chrom": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
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
                    "type": {
                        "type": "text"
                    },
                    "gene": {
                        "properties": {
                            "id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "symbol": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "rcv": {
                        "properties": {
                            "accession": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "number_submitters": {
                                "type": "integer"
                            },
                            "last_evaluated": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "conditions": {
                                "properties": {
                                    "synonyms": {
                                        "type": "text"
                                    },
                                    "identifiers": {
                                        "properties": {
                                            "mondo": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "medgen": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "orphanet": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "omim": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "mesh": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "human_phenotype_ontology": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "gene": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "efo": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            }
                                        }
                                    },
                                    "name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "origin": {
                                "type": "text"
                            },
                            "preferred_name": {
                                "type": "text"
                            },
                            "clinical_significance": {
                                "type": "text"
                            },
                            "review_status": {
                                "type": "text"
                            }
                        }
                    },
                    "rsid": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "cytogenic": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "hgvs": {
                        "properties": {
                            "genomic": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "text"
                            },
                            "coding": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "text"
                            },
                            "protein": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "text"
                            },
                            "non-coding": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "ref": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "alt": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "variant_id": {
                        "type": "integer"
                    },
                    "omim": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "uniprot": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "genotypeset": {
                        "properties": {
                            "type": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "genotype": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "dbvar": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "cosmic": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "coding_hgvs_only": {
                        "type": "boolean"
                    }
                }
            },
            "observed": {
                "type": "boolean"
            },
            "chrom": {
                "normalizer": "keyword_lowercase_normalizer",
                "type": "keyword"
            },
            "geno2mp": {
                "properties": {
                    "hpo_count": {
                        "type": "integer"
                    }
                }
            },
            "emv": {
                "properties": {
                    "gene": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "variant_id": {
                        "type": "integer"
                    },
                    "exon": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "egl_variant": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "egl_classification_date": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "hgvs": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "text"
                    },
                    "egl_classification": {
                        "type": "text"
                    },
                    "egl_protein": {
                        "type": "text"
                    }
                }
            },
            "_seqhashed": {
                "properties": {
                    "5a21cf84e3a3e4af232feff295ee633a": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "_flag": {
                        "type": "boolean"
                    },
                    "78b0b513aa8eb34923b286a3f0ca701d": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "405a1d903d4f3a36f5539f25f8683249": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "3f519fe63c5b559640b1c4f6bfb0a679": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "b90e716ad05b07dc447b5518b3eb0477": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "3e2c783bc2e14e7de924b6c883bdd306": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "1313e0def30bc4edbd118bec7d203fb8": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "747ec6db2b9ebf18f0b97a391d9d5dd0": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "284427e1eca1d0e83a020aafa68876d5": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "c58354303f41353943eb8a8810e1aa11": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "adf7574e78e79c17459be352a7393328": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "fb5db2f0237a002afbcace53db5d3432": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "0f6f8c2f73969dbb7db1817184d9d9e4": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "02ce1b5fcf372de6bd92bd39cf445422": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "442c06338cdfb26311fe627eaa680e6b": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "825a02344ce11a0dd0eb1722aa6b6e0e": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "a23c64fa372ecc697b8ce37adae16faf": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "ec307c5205ae6883b4fe0e1b36a1e964": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "b982aea1997ac85b0cd440bbf522df1d": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "c12e792ab0a1707d0c16122e05de2c12": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "d5197641182c8e4316d4bd40d1827ff1": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    }
                }
            },
            "civic": {
                "properties": {
                    "contributors": {
                        "properties": {
                            "editors": {
                                "properties": {
                                    "user": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "profileImagePath": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            }
                                        }
                                    },
                                    "uniqueActions": {
                                        "properties": {
                                            "action": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "count": {
                                                "type": "integer"
                                            }
                                        }
                                    },
                                    "lastActionDate": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "totalActionCount": {
                                        "type": "integer"
                                    }
                                }
                            },
                            "curators": {
                                "properties": {
                                    "user": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "profileImagePath": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            }
                                        }
                                    },
                                    "uniqueActions": {
                                        "properties": {
                                            "action": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "count": {
                                                "type": "integer"
                                            }
                                        }
                                    },
                                    "lastActionDate": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "totalActionCount": {
                                        "type": "integer"
                                    }
                                }
                            }
                        }
                    },
                    "id": {
                        "type": "integer"
                    },
                    "feature": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "text"
                            },
                            "link": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "deprecated": {
                                "type": "boolean"
                            },
                            "flagged": {
                                "type": "boolean"
                            }
                        }
                    },
                    "name": {
                        "type": "text"
                    },
                    "molecularProfiles": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "molecularProfileScore": {
                                "type": "float"
                            },
                            "molecularProfileAliases": {
                                "type": "text"
                            },
                            "variants": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "link": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "evidenceItems": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "disease": {
                                        "properties": {
                                            "myDiseaseInfo": {
                                                "properties": {
                                                    "mondoId": {
                                                        "normalizer": "keyword_lowercase_normalizer",
                                                        "type": "keyword"
                                                    },
                                                    "icdo": {
                                                        "normalizer": "keyword_lowercase_normalizer",
                                                        "type": "keyword"
                                                    },
                                                    "ncit": {
                                                        "normalizer": "keyword_lowercase_normalizer",
                                                        "type": "keyword"
                                                    },
                                                    "mesh": {
                                                        "type": "text"
                                                    },
                                                    "doDef": {
                                                        "type": "text"
                                                    },
                                                    "icd10": {
                                                        "type": "text"
                                                    }
                                                }
                                            },
                                            "name": {
                                                "type": "text"
                                            },
                                            "diseaseAliases": {
                                                "type": "text"
                                            },
                                            "diseaseUrl": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "displayName": {
                                                "type": "text"
                                            },
                                            "doid": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "id": {
                                                "type": "integer"
                                            },
                                            "link": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            }
                                        }
                                    },
                                    "variantOrigin": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "evidenceDirection": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "evidenceLevel": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "evidenceRating": {
                                        "type": "integer"
                                    },
                                    "evidenceType": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "flagged": {
                                        "type": "boolean"
                                    },
                                    "significance": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "molecularProfile": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            }
                                        }
                                    },
                                    "source": {
                                        "properties": {
                                            "citation": {
                                                "type": "text"
                                            },
                                            "id": {
                                                "type": "integer"
                                            },
                                            "name": {
                                                "type": "text"
                                            },
                                            "sourceUrl": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "title": {
                                                "type": "text"
                                            },
                                            "sourceType": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "link": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "journal": {
                                                "type": "text"
                                            },
                                            "openAccess": {
                                                "type": "boolean"
                                            },
                                            "publicationDate": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "retracted": {
                                                "type": "boolean"
                                            },
                                            "citationId": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "authorString": {
                                                "type": "text"
                                            },
                                            "abstract": {
                                                "type": "text"
                                            },
                                            "pmcId": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "retractionDate": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "retractionNature": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "retractionReasons": {
                                                "type": "text"
                                            }
                                        }
                                    },
                                    "therapies": {
                                        "properties": {
                                            "id": {
                                                "type": "integer"
                                            },
                                            "link": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "deprecated": {
                                                "type": "boolean"
                                            },
                                            "name": {
                                                "type": "text"
                                            }
                                        }
                                    },
                                    "phenotypes": {
                                        "properties": {
                                            "hpoId": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "id": {
                                                "type": "integer"
                                            },
                                            "link": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "url": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "description": {
                                                "type": "text"
                                            },
                                            "name": {
                                                "type": "text"
                                            }
                                        }
                                    },
                                    "description": {
                                        "type": "text"
                                    }
                                }
                            },
                            "name": {
                                "type": "text"
                            }
                        }
                    },
                    "deprecated": {
                        "type": "boolean"
                    },
                    "variantAliases": {
                        "type": "text"
                    },
                    "flags": {
                        "properties": {
                            "totalCount": {
                                "type": "integer"
                            }
                        }
                    },
                    "openRevisionCount": {
                        "type": "integer"
                    },
                    "comments": {
                        "properties": {
                            "totalCount": {
                                "type": "integer"
                            }
                        }
                    },
                    "variantTypes": {
                        "properties": {
                            "id": {
                                "type": "integer"
                            },
                            "link": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "soid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "name": {
                                "type": "text"
                            }
                        }
                    },
                    "revisions": {
                        "properties": {
                            "totalCount": {
                                "type": "integer"
                            }
                        }
                    },
                    "lastSubmittedRevisionEvent": {
                        "properties": {
                            "originatingUser": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "displayName": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "role": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "profileImagePath": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            }
                        }
                    },
                    "lastAcceptedRevisionEvent": {
                        "properties": {
                            "originatingUser": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "displayName": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "role": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "profileImagePath": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            }
                        }
                    },
                    "creationActivity": {
                        "properties": {
                            "user": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "displayName": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "role": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "profileImagePath": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            },
                            "createdAt": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "viccCompliantName": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "fusion": {
                        "properties": {
                            "fivePrimePartnerStatus": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "fivePrimeGene": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "link": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "deprecated": {
                                        "type": "boolean"
                                    },
                                    "flagged": {
                                        "type": "boolean"
                                    }
                                }
                            },
                            "threePrimePartnerStatus": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "threePrimeGene": {
                                "properties": {
                                    "id": {
                                        "type": "integer"
                                    },
                                    "name": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "link": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "deprecated": {
                                        "type": "boolean"
                                    },
                                    "flagged": {
                                        "type": "boolean"
                                    }
                                }
                            }
                        }
                    },
                    "fivePrimeCoordinates": {
                        "properties": {
                            "referenceBuild": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "ensemblVersion": {
                                "type": "integer"
                            },
                            "chromosome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "representativeTranscript": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "coordinateType": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "threePrimeCoordinates": {
                        "properties": {
                            "referenceBuild": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "ensemblVersion": {
                                "type": "integer"
                            },
                            "chromosome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "representativeTranscript": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "coordinateType": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "fivePrimeStartExonCoordinates": {
                        "properties": {
                            "referenceBuild": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "ensemblVersion": {
                                "type": "integer"
                            },
                            "chromosome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "representativeTranscript": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "exon": {
                                "type": "integer"
                            },
                            "ensemblId": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "strand": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "coordinateType": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "fivePrimeEndExonCoordinates": {
                        "properties": {
                            "referenceBuild": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "ensemblVersion": {
                                "type": "integer"
                            },
                            "chromosome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "representativeTranscript": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "exon": {
                                "type": "integer"
                            },
                            "ensemblId": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "strand": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "coordinateType": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "exonOffset": {
                                "type": "integer"
                            },
                            "exonOffsetDirection": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "threePrimeStartExonCoordinates": {
                        "properties": {
                            "referenceBuild": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "ensemblVersion": {
                                "type": "integer"
                            },
                            "chromosome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "representativeTranscript": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "exon": {
                                "type": "integer"
                            },
                            "ensemblId": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "strand": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "coordinateType": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "threePrimeEndExonCoordinates": {
                        "properties": {
                            "referenceBuild": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "ensemblVersion": {
                                "type": "integer"
                            },
                            "chromosome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "representativeTranscript": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "exon": {
                                "type": "integer"
                            },
                            "ensemblId": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "strand": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "coordinateType": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "coordinates": {
                        "properties": {
                            "referenceBuild": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "coordinateType": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "chromosome": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "start": {
                                "type": "integer"
                            },
                            "stop": {
                                "type": "integer"
                            },
                            "variantBases": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "ensemblVersion": {
                                "type": "integer"
                            },
                            "representativeTranscript": {
                                "type": "text"
                            },
                            "referenceBases": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "clinvarIds": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "alleleRegistryId": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "openCravatUrl": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "maneSelectTranscript": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "hgvsDescriptions": {
                        "type": "text"
                    },
                    "ncitId": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "ncitDetails": {
                        "properties": {
                            "synonyms": {
                                "properties": {
                                    "source": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "definitions": {
                                "properties": {
                                    "source": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "definition": {
                                        "type": "text"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "cgi": {
                "properties": {
                    "region": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "cdna": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "transcript": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "gene": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "protein_change": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "association": {
                        "type": "text"
                    },
                    "source": {
                        "type": "text"
                    },
                    "evidence_level": {
                        "type": "text"
                    },
                    "primary_tumor_type": {
                        "type": "text"
                    },
                    "drug": {
                        "type": "text"
                    }
                }
            }
        }

        return mapping
