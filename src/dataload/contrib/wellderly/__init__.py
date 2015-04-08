
__METADATA__ = {
    "src_name": 'Wellderly',
    "src_url": 'http://www.stsiweb.org/wellderly/',
    "version": None,
    "field": "wellderly"
}


def load_data():
    '''wellderly data are pre-loaded in our db.'''
    raise NotImplementedError


def get_mapping():
    mapping = {
        "wellderly": {
            "properties": {
                "chrom": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "pos": {
                    "type": "long"
                },
                "hg19": {
                    "properties": {
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "vartype": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                # "alleles": {
                #     "properties": {
                #         "allele": {
                #             "type": "string",
                #             "analyzer": "string_lowercase"
                #         },
                #         "allele": {
                #             "type": "float"
                #         }
                #     }
                # },
                "gene": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "coding_impact": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "polyphen": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "sift": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
