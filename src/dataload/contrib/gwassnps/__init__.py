__METADATA__ = {
    "requirements": [
        "MySQL-python>=1.2.5",
    ],
    "src_name": 'gwassnps',
    "src_url": None,
    "version": None,
    "field": "gwassnps"
}


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
                "pubmed": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "rsid": {
                    "type": "string",
                    "include_in_all": True,
                    "analyzer": "string_lowercase"
                },
                "title": {
                    "type": "string"
                },
                "region": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "genename": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "risk_allele": {
                    "type": "string"
                },
                "risk_allele_freq": {
                    "type": "float"
                },
                "pvalue": {
                    "type": "float",
                    "index": "no"
                },
                "pvalue_desc": {
                    "type": "string",
                    "index": "no"
                }
            }
        }
    }
    return mapping
