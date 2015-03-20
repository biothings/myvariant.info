# -*- coding: utf-8 -*-
from .emv_parser import load_data as _load_data

EMV_INPUT_FILE = '/opt/myvariant.info/load_archive/emv/EmVClass.2014-3.csv'

def load_data():
    emv_data = _load_data(emv_INPUT_FILE)
    return emv_data

