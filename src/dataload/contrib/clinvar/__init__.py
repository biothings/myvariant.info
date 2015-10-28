# -*- coding: utf-8 -*-
__METADATA__ = {
    "src_name": 'clinvar',
    "src_url": 'ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/',
    "release": '2015-09',
    "field": 'clinvar'
}

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
                        "start": {
                            "type": "long"
                        },
                        "end": {
                            "type": "long"
                        }
                    }
                },
                "chrom": {
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
                        "id": {
                            "type": "long"
                        }
                    }
                },
                "type": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "name": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "origin": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "rsid": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                    "include_in_all": True
                },
                "rcv_accession": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    "include_in_all": True
                },
                "cytogenic": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "review_status": {
                    "type": "string"
                },
                "hgvs": {
                    "properties": {
                        "genomic": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "coding": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "non-coding": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        },
                        "protein": {
                            "type": "string",
                            "analyzer": "string_lowercase"
                        }
                    }
                },
                "number_submitters": {
                    "type": "byte"
                },
                "last_evaluated": {
                    "type": "string",
                    "index": "no"
                },
                "other_ids": {
                    "type": "string"
                },
                "allele_id": {
                    "type": "string",
                    "index": "no"
                },
                "clinvar_id": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    "include_in_all": True
                },
                "coding_hgvs_only": {
                    "type": "boolean"
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                }
            }
        }
    }
    return mapping
