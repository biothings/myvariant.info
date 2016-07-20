__METADATA__ = {
    "src_name": 'SNPedia',
    "src_url": 'http://www.snpedia.org/',
    "version": None,
    "field": "snpedia"
}


def load_data():
    '''snpedia data are pre-loaded in our db.'''
    raise NotImplementedError


def get_mapping():
    mapping = {
        "snpedia": {
            "properties": {
                "text": {
                    "type": "string"
                }
            }
        }
    }
    return mapping
