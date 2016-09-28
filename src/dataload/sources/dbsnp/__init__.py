from .dbsnp_vcf_parser import parse_vcf

__metadata__ = {
    "name": 'dbsnp',
    'uploader' : 'biothings.dataload.uploader.NoBatchIgnoreDuplicatedSourceUploader',
}


from .dbsnp_dump import main as download
from .dbsnp_vcf_parser import load_data


def get_mapping(self=None):
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
