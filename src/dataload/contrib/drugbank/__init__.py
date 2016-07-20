# -*- coding: utf-8 -*-

# DRUGBANK_URL = "http://www.drugbank.ca/genobrowse/snp-adr?page="

# def load_data():
#    drugbank_data = _load_data(DRUGBANK_URL)
#    return drugbank_data


def get_mapping():
    mapping = {
        "drugbank": {
            "properties": {
                "adverse_reaction": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "defining_change": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "drug": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "interacting_gene_or_enzyme": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "snp_rs_id": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
