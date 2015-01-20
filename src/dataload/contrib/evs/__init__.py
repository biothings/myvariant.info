# -*- coding: utf-8 -*-

from .evs_parser import load_data as _load_data

EVS_INPUT_FILE = ''

def load_data():
    evs_data = _load_data(EVS_INPUT_FILE)
    return evs_data