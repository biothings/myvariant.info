# -*- coding: utf-8 -*-

from .drugbank_parser import load_data as _load_data

DRUGBANK_URL = "http://www.drugbank.ca/genobrowse/snp-adr?page="

def load_data():
    drugbank_data = _load_data(DRUGBANK_URL)
    return drugbank_data
