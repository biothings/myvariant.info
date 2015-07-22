#ES mapping
import importlib


def get_mapping(sources=None):
    if sources is None:
        #sources = ['cadd', 'clinvar', 'cosmic2', 'dbnsfp', 'dbsnp', 'drugbank', 'emv', 'evs', 'grasp']
        sources = sources or ['dbsnp', "cadd", "evs", "snpedia", "wellderly",
                              'dbnsfp', 'emv', 'mutdb', 'docm', 'cosmic',
                              'clinvar', 'gwassnps','exac','grasp','snpeff']
        # extra_mapping_li = [mapping_snpedia, mapping_wellderly]
        extra_mapping_li = []
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


# this is a minimal mapping for myvariant_merged index
# each data source field just need to index one common field
# (that is, this field need to exist in every documents)
minimal_field_d = {
    "dbsnp": "chrom",
    "dbnsfp": "chrom",
    "cadd": "chrom",
    "clinvar": "type",
    "mutdb": "chrom",
    "gwassnps": "chrom",
    "cosmic": "chrom",
    "docm": "chrom",     # TODO: change chromosome_name to chrom
    "snpedia": "text",
    "evs": "chrom",
    "emv": "egl_classification",
    "wellderly": "chrom"  # TODO: change chr to chrom
}

mapping_merged = {}

for _src in minimal_field_d:
    _field = minimal_field_d[_src]
    _type = 'string'
    mapping_merged[_src] = {
        "properties": {
            _field: {
                "type": _type
            }
        }
    }

mapping_merged = {
    "variant": {
        "include_in_all": False,
        "dynamic": False,
        "properties": mapping_merged
    }
}
