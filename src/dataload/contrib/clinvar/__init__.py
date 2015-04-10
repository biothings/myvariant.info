from .clinvar_parser import load_data as _load_data


__METADATA__ = {
    "src_name": 'ClinVar',
    "src_url": 'http://www.ncbi.nlm.nih.gov/clinvar/',
    "version": '20150323',
    "field": "clinvar"
}


CLINVAR_INPUT_FILE = '/opt/myvariant.info/load_archive/clinvar/variant_summary.txt'


def load_data():
    clinvar_data = _load_data(CLINVAR_INPUT_FILE)
    return clinvar_data


def get_mapping():
    mapping = {
        "clinvar": {
            "properties": {
                "clinical_significance": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "hg19": {
                    "properties": {
                        "chr": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
                "gene": {
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                },
                "type": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "origin": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "rsid": {
                    "type": "string"
                },
                "variant_id": {
                    "type": "long"
                }
            }
        }
    }
    return mapping
