import biothings.dataload.uploader as uploader
from dataload.uploader import SnpeffPostUpdateUploader

class UniprotUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):

    name = "uniprot"
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg38",
            "src_meta" : {
                "url" : "http://www.uniprot.org/",
                "license" : "CC BY-ND 3.0",
                "license_url" : "http://www.uniprot.org/help/license",
                }
            }

    @classmethod
    def get_mapping(klass):
        mapping = {
            "uniprot": {
                "properties": {
                    "source_db_id": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "clinical_significance": {
                        "type": "string",
                    },
                    "phenotype_disease": {
                        "type": "string",
                    },
                    "phenotype_disease_source": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "humsavar": {
                        "properties": {
                            "swiss_prot_ac": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "ftid": {
                                "include_in_all": True,
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "type_of_variant": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "disease_name": {
                                "type": "string",
                            }
                        }
                    }
                }
            }
        }
        return mapping

