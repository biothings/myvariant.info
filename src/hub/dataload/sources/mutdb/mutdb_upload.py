import biothings.hub.dataload.uploader as uploader
from ...uploader import SnpeffPostUpdateUploader

class MutDBUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):
    """Originally downloaded from: http://www.mutdb.org/"""

    name = "mutdb"
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "http://www.mutdb.org/",
                "license_url" : "http://www.mutdb.org/",
                "license_url_short": "https://goo.gl/I4Ipa2"
                }
            }

    @classmethod
    def get_mapping(klass):
        mapping = {
            "mutdb": {
                "properties": {
                    "rsid": {
                        "type": "string",
                        "include_in_all": True,
                        "analyzer": "string_lowercase",
                    },
                    "ref": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
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
                    "hg19": {
                        "properties": {
                            "start": {
                                "type": "integer"
                            },
                            "end": {
                                "type": "integer"
                            }
                        }
                    },
                    "strand": {
                        "type": "string",
                        "index": "not_analyzed"
                    }
                }
            }
        }
        return mapping

