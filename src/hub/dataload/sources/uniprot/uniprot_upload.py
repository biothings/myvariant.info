import biothings.hub.dataload.uploader as uploader
from ...uploader import SnpeffPostUpdateUploader

class UniprotUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):

    name = "uniprot"
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg38",
            "src_meta" : {
                "url" : "http://www.uniprot.org/",
                "license" : "CC BY-ND 3.0",
                "license_url" : "http://www.uniprot.org/help/license",
                "license_url_short": "https://goo.gl/4CUyQv"
                }
            }

    @classmethod
    def get_mapping(klass):
        mapping = {
            "uniprot": {
                "properties": {
                    "source_db_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "clinical_significance": {
                        "type": "text",
                    },
                    "phenotype_disease": {
                        "type": "text",
                    },
                    "phenotype_disease_source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "humsavar": {
                        "properties": {
                            "swiss_prot_ac": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "ftid": {
                                "copy_to" : ["all"],
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "type_of_variant": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "disease_name": {
                                "type": "text",
                            }
                        }
                    }
                }
            }
        }
        return mapping

