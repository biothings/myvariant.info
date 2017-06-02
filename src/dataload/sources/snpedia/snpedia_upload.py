import biothings.dataload.uploader as uploader
from dataload.uploader import SnpeffPostUpdateUploader

class SnpediaUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):
    """Originally downloaded from: http://www.snpedia.org/"""

    name = "snpedia"
    __metadata__ = {
            "mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "https://www.snpedia.com/",
                "licence" : "CC BY-NC-SA",
                "licence_url" : "https://www.snpedia.com/index.php/SNPedia:General_disclaimer",
                }
            }

    @classmethod
    def get_mapping(klass):
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

