__METADATA__ = {
    "src_name": 'DOCM',
    "src_url": 'http://docm.genome.wustl.edu/',
    "version": None,
    "field": "docm"
}


def load_data():
    '''docm data are pre-loaded in our db.'''
    raise NotImplementedError


def get_mapping():
    mapping = {
        "docm": {
            "properties": {
                "domain": {
                    "type": "string"
                },
                "all_domains": {
                    "type": "string"
                },
                "ref": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "alt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "primary": {
                    "type": "byte"           # just 0 or 1
                },
                "transcript_species": {
                    "type": "string",
                    "index": "no"
                },
                "ensembl_gene_id": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "transcript_version": {
                    "type": "string",
                    "index": "no"
                },
                "transcript_source": {
                    "type": "string",
                    "index": "no"
                },
                "source": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "pubmed_id": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "type": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "DOID": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    "index_name": "doid"
                },
                "c_position": {
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
                "strand": {
                    "type": "byte",
                    "index": "no"
                },
                "deletion_substructures": {
                    "type": "string",
                    "index": "no"
                },
                "genename_source": {
                    "type": "string",
                    "index": "no"
                },
                "default_gene_name": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "aa_change": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "url": {
                    "type": "string",
                    "index": "no"
                },
                "transcript_status": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "trv_type": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "disease": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "transcript_name": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "chrom": {
                    "type": "string",                 # actual value is integer
                    "analyzer": "string_lowercase"
                },
                "transcript_error": {
                    "type": "string",
                    "index": "no"
                },
                "genename": {
                    "type": "string",
                    "analyzer": "string_lowercase",
                    "include_in_all": True
                },
                "ucsc_cons": {
                    "type": "double"
                }
            }
        }
    }
    return mapping
