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
            }
        }

        return mapping
