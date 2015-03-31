def load_data():
    '''gwassnps data are preloaded in our db.'''
    raise NotImplementedError


def get_mapping():
    mapping = {
        "gwassnps": {
            "properties": {
                "trait": {
                    "type": "string"
                },
                "pubmedID": {
                    "type": "long"
                },
                "rsid": {
                    "type": "string",
                    "include_in_all": True,
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
