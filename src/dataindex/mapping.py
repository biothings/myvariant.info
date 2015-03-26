#ES mapping
import importlib


def get_mapping(sources=None):
    if sources is None:
        #sources = ['cadd', 'clinvar', 'cosmic2', 'dbnsfp', 'dbsnp', 'drugbank', 'emv', 'evs', 'grasp']
        sources = sources or ['dbsnp', 'dbnsfp', 'cosmic']
        extra_mapping_li = [mapping_snpedia, mapping_wellderly]
    else:
        extra_mapping_li = []

    if isinstance(sources, str):
        sources = [sources]
    m = {
        "variant": {
            "include_in_all": False,
            "dynamic": False,
            "properties": {}
        }
    }

    for src in sources:
        src_m = importlib.import_module('dataload.contrib.' + src + '.__init__')
        _m = src_m.get_mapping()
        m['variant']['properties'].update(_m)

    for extra_mapping in extra_mapping_li:
        m['variant']['properties'].update(extra_mapping)

    return m


'''
mapping = {
    "mappings": {
        "_default_": {
        #    "_all": { "enabled":  false }
        },
        "variant": {
            "include_in_all": False,
            "dynamic": False,
            "dynamic_templates": [
            #     { "es": {
            #           "match":              "*_es",
            #           "match_mapping_type": "string",
            #           "mapping": {
            #               "type":           "string",
            #               "analyzer":       "spanish"
            #           }
            #     }},
                {
                    "lowercase_keyword": {
                        "match": "*",
                        "match_mapping_type": "string",
                        "mapping": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                }
            ]
        }
    }
}
'''

mapping_snpedia = {
    "snpedia": {
        "properties": {
            "text": {
                "type": "string"
            }
        }
    }
}


mapping_wellderly = {
    "wellderly": {
        "properties": {
            "chr": {
                "type": "string",
                "analyzer": "string_lowercase"
            },
            "pos": {
                "type": "long"
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
