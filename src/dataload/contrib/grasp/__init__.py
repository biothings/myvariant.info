# -*- coding: utf-8 -*-

from .grasp_parser import load_data as _load_data

GRASP_INPUT_FILE = '/opt/myvariant.info/load_archive/grasp/GRASP2fullDataset'

def load_data():
    grasp_data = _load_data(GRASP_INPUT_FILE)
    return grasp_data


def get_mapping():
	mapping = {
	    "grasp": {
	        "properties": {
	            "hg19": {
	                "properties": {
	                    "chr": {
	                        "type": "string",
	                        "analyzer": "string_lowercase"
	                    },
	                    "pos": {
	                        "type": "long"
	                    }
	                }
	            },
	            "srsid": {
	                "type": "long"
	            }
	        }
	    }
	}
	return mapping