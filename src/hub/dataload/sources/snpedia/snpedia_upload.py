import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader

class SnpediaUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):
    """Originally downloaded from: http://www.snpedia.org/"""

    name = "snpedia"
    __metadata__ = {
        "mapper" : 'observed',
        "assembly" : "hg19",
        "src_meta" : {
            "url" : "https://www.snpedia.com/",
            "license" : "CC BY-NC-SA",
            "license_url" : "https://www.snpedia.com/index.php/SNPedia:General_disclaimer",
            "license_url_short": "http://bit.ly/2VJ3TeR"
        }
    }

    @classmethod
    def get_mapping(klass):
        mapping = {
            "snpedia": {
                "properties": {
                    "text": {
                        "type": "text"
                    }
                }
            }
        }
        return mapping

