# -*- coding: utf-8 -*-

from .cadd_parser import load_contig

def get_mapping():
	mapping = {
	    "cadd": {
	        "properties": {
	            "annotype": {
	                "type": "string",
	                "analyzer": "string_lowercase"
	            },
	            "chrom": {
	                "type": "string",
	                "analyzer": "string_lowercase"
	            },
	            "consequence": {
	                "type": "string",
	                "analyzer": "string_lowercase"
	            },
	            "pos": {
	                "type": "long"
	            },
	            "ref": {
	                "type": "string",
	                "analyzer": "string_lowercase"
	            },
	            "type": {
	                "type": "string",
	                "analyzer": "string_lowercase"
	            }
	        }

	    }
	}
	return mapping


def plus():
	return 5



