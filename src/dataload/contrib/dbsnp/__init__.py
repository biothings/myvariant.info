from __future__ import print_function
from .dbsnp_vcf_parser import parse_vcf


__METADATA__ = {
    "requirements": [
        "PyVCF>=0.6.7",
    ],
    "src_name": 'dbSNP',
    "src_url": 'http://www.ncbi.nlm.nih.gov/SNP/',
    "version": '142',
    "field": "dbsnp"
}


infile = "/home/kevinxin/dbsnp/00-All.vcf.gz"


def load_data():
    chrom_list = [str(i) for i in range(1, 23)] + ['X', 'Y', 'MT']
    for chrom in chrom_list:
        print("Processing chr{}...".format(chrom))
        snpdoc_iter = parse_vcf(infile, compressed=True, verbose=False, by_id=True, reference=chrom)
        for doc in snpdoc_iter:
            _doc = {'dbsnp': doc}
            _doc['_id'] = doc['_id']
            del doc['_id']
            yield _doc


def get_mapping():
    mapping = {
        "dbsnp": {
            "properties": {
                "allele_origin": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "chrom": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "class": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "flags": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "gmaf": {
                    "type": "float"
                },
                "hg19": {
                    "properties": {
                        "end": {
                            "type": "long"
                        },
                        "start": {
                            "type": "long"
                        }
                    }
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "rsid": {
                    "type": "string",
                    "include_in_all": True,
                    "analyzer": "string_lowercase"
                },
                "var_subtype": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "vartype": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "validated": {
                    "type": "boolean"
                },
                "gene": {
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "analyzer": "string_lowercase",
                            "include_in_all": True
                        },
                        "geneid": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                }
            }
        }
    }
    return mapping
