#ES mapping
import importlib

def get_mapping():
    #sources = ['cadd', 'clinvar', 'cosmic2', 'dbnsfp', 'dbsnp', 'drugbank', 'emv', 'evs', 'grasp']
    sources = ['dbsnp', 'dbnsfp']
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

    for extra_mapping in [mapping_snpedia, mapping_wellderly]:
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
