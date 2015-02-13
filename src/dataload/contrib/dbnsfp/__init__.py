# -*- coding: utf-8 -*-

from .dbnsfp_parser import load_data as _load_data

DBNSFP_INPUT_FILE = '/opt/myvariant.info/load_archive/dbnsfp/dbNSFP2.9_variant*'

def load_data():
    dbnsfp_data = _load_data(DBNSFP_INPUT_FILE)
    return dbnsfp_data