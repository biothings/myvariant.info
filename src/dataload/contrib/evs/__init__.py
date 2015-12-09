from .evs_parser import load_data as _load_data


__METADATA__ = {
    "src_name": 'EVS',
    "src_url": 'http://evs.gs.washington.edu/EVS/',
    "version": "2",
    "field": "evs"
}


EVS_INPUT_FILE = '/opt/myvariant.info/load_archive/evs/ESP6500SI-V2-SSA137.GRCh38-liftover.chr*'


def load_data():
    evs_data = _load_data(EVS_INPUT_FILE)
    return evs_data


def get_mapping():
    mapping = {
        "evs": {
            "properties": {
                "chrom": {
                    "type": "string"
                },
                "hg19": {
                    "properties": {
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
                "hg38": {
                    "properties": {
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "gene": {
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "analyzer": "string_lowercase",
                            "include_in_all": True
                        },
                        "accession": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                },
                "hgvs": {
                    "properties": {
                        "coding": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "protein": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                },
                "clinical_info": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "function_gvs": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "grantham_score": {
                    "type": "float"
                },
                "rsid": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    "include_in_all": True
                }
            }
        }
    }
    return mapping
