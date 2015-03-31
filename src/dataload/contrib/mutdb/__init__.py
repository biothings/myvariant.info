def load_data():
    '''mutdb data are preloaded in our db.'''
    raise NotImplementedError


def get_mapping():
    mapping = {
        "mutdb": {
            "properties": {
                "dbsnp_id": {
                    "type": "string",
                    "include_in_all": True,
                    "analyzer": "string_lowercase",
                },
                "allele1": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "allele2": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "uniprot_id": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "mutpred_score": {
                    "type": "double"
                },
                "cosmic_id": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "chrom": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "chromStart": {
                    "type": "long"
                },
                "chromEnd": {
                    "type": "long"
                },
                "strand": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }
    return mapping
