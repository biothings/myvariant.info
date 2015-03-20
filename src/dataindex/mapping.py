#ES mapping
import importlib

def get_mapping():
    sources = ['cadd', 'clinvar', 'cosmic2', 'dbnsfp', 'dbsnp', 'drugbank', 'emv', 'evs', 'grasp']

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
        
    return m


mapping = {
    'mappings': {
        "_default_": {
        #    "_all": { "enabled":  false }
        },
        'variant': {
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

