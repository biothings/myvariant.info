from .cosmic_parser import load_data as _load_data


__METADATA__ = {
    "src_name": 'COSMIC',
    "src_url": 'http://cancer.sanger.ac.uk/cosmic',
    "version": '72',
    "field": "cosmic"
}


COSMIC_INPUT_FILE = ''


def load_data():
    cosmic_data = _load_data(COSMIC_INPUT_FILE)
    return cosmic_data


def get_mapping():
    mapping = {
        "cosmic": {
            "properties": {
                "tumor_site": {
                    "type": "string"
                },
                # "tomour_site": {
                #     "type": "string"
                # }
                "mut_freq": {
                    "type": "double"    # actual values are string type
                },
                "mut_nt": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "allele1": {
                    "type": "string",
                    "analyzer": "string_lowercase"
                },
                "allele2": {
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
                }
            }
        }
    }
    return mapping
