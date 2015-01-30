# -*- coding: utf-8 -*-

from .clinvar_parser import load_data as _load_data

CLINVAR_INPUT_FILE = '/opt/myvariant.info/load_archive/clinvar/variant_summary.txt'

def load_data():
    clinvar_data = _load_data(CLINVAR_INPUT_FILE)
    return clinvar_data

