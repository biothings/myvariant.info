import biothings.dataload.uploader as uploader

class CosmicUploader(uploader.DummySourceUploader):

    name = "cosmic"

    @classmethod
    def get_mapping(klass):
        mapping = {
            "cosmic": {
                "properties": {
                    "tumor_site": {
                        "type": "string"
                    },
                    # "tomour_site": {
                    #     "type": "string"
                    # }
                    "mut_freq": {
                        "type": "double"    # actual values are string type
                    },
                    "mut_nt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "allele1": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "allele2": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "chromStart": {
                        "type": "long"
                    },
                    "chromEnd": {
                        "type": "long"
                    }
                }
            }
        }
        return mapping

