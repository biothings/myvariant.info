import biothings.dataload.uploader as uploader
from dataload.uploader import SnpeffPostUpdateUploader

class SnpediaUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):
    """Originally downloaded from: http://www.snpedia.org/"""

    name = "snpedia"
    __metadata__ = {"mapper" : 'observed'}

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

