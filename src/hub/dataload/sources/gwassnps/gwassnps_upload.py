import biothings.hub.dataload.uploader as uploader
from ...uploader import SnpeffPostUpdateUploader

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
                        "type": "string"
                    },
                    "pubmed": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "rsid": {
                        "type": "string",
                        "include_in_all": True,
                        "analyzer": "string_lowercase"
                    },
                    "title": {
                        "type": "string"
                    },
                    "region": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "genename": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "risk_allele": {
                        "type": "string"
                    },
                    "risk_allele_freq": {
                        "type": "float"
                    },
                    "pvalue": {
                        "type": "float",
                        "index": "no"
                    },
                    "pvalue_desc": {
                        "type": "string",
                        "index": "no"
                    }
                }
            }
        }
        return mapping

