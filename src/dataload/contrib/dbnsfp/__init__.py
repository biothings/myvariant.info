# -*- coding: utf-8 -*-

from .dbnsfp_parser import load_data as _load_data

DBNSFP_INPUT_FILE = ''

def load_data():
    dbnsfp_data = _load_data(DBNSFP_INPUT_FILE)
    return dbnsfp_data