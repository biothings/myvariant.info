import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader

class GwassnpsUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):

    name = "gwassnps"
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "http://www.ebi.ac.uk/gwas/",
                "license_url" : "http://www.ebi.ac.uk/gwas/docs/about",
                "license_url_short": "https://goo.gl/Zy0C5e"
                }
            }

    @classmethod
    def get_mapping(klass):
        mapping = {
            "gwassnps": {
                "properties": {
                    "trait": {
                        "type": "text"
                    },
                    "pubmed": {
                        # not_analyzed
                        "type": "keyword",
                    },
                    "rsid": {
                        "type": "text",
                        "copy_to" : ["all"],
                        "analyzer": "string_lowercase"
                    },
                    "title": {
                        "type": "text"
                    },
                    "region": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "genename": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "risk_allele": {
                        "type": "text"
                    },
                    "risk_allele_freq": {
                        "type": "float"
                    },
                    "pvalue": {
                        "type": "float",
                        "index" : False
                    },
                    "pvalue_desc": {
                        "type": "text",
                        "index" : False
                    }
                }
            }
        }
        return mapping

