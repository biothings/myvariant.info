import biothings.dataload.uploader as uploader
from dataload.uploader import SnpeffPostUpdateUploader

class CosmicUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):

    name = "cosmic"
    __metadata__ = {"mapper" : 'observed',
                    "assembly" : "hg19"}

    @classmethod
    def get_mapping(klass):
        mapping = {
            "cosmic": {
                "properties": {
                    "chrom": {
                        "type": "string",
                        "analyzer": "string_lowercase"
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
                    "tumor_site": {
                        "type": "string"
                    },
                    "cosmic_id": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "mut_nt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "mut_freq": {
                        "type": "float"
                    },
                    "ref": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    }
                }
            }
        }
        return mapping

