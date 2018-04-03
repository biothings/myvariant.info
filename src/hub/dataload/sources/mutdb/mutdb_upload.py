import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader

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
                        "type": "text",
                        "copy_to" : ["all"],
                        "analyzer": "string_lowercase",
                    },
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "uniprot_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "mutpred_score": {
                        "type": "double"
                    },
                    "cosmic_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "text",
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
                        # not_analyzed
                        "type": "keyword",
                    }
                }
            }
        }
        return mapping

