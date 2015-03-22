# -*- coding: utf-8 -*-

from .evs_parser import load_data as _load_data

EVS_INPUT_FILE = '/opt/myvariant.info/load_archive/evs/ESP6500SI-V2-SSA137.GRCh38-liftover.chr*'

def load_data():
    evs_data = _load_data(EVS_INPUT_FILE)
    return evs_data

def get_mapping():
    mapping = {
        "evs": {
            "properties": {
                "clinical_info": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "function_gvs": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "grantham_score": {
                    "type": "float"
                },
                "rs_id": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping

