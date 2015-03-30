# -*- coding: utf-8 -*-
from .emv_parser import load_data as _load_data

## must convert column 3, the coding HGVS nomenclature, to genomic.
## paste new column to file before loading data
EMV_INPUT_FILE = '/opt/myvariant.info/load_archive/emv.csv*'

def load_data():
    emv_data = _load_data(EMV_INPUT_FILE)
    return emv_data

def get_mapping():
    mapping = {
        "emv": {
            "properties": {
                "egl_classification": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "egl_protein": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "egl_variant": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    "include_in_all": True
                },
                "gene": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "variant_aka_list": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    "include_in_all": True
                }
            }
        }
    }
    return mapping


