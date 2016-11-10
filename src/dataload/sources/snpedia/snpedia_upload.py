import biothings.dataload.uploader as uploader
from dataload.uploader import SnepffPostUpdateUploader

class SnpediaUploader(uploader.DummySourceUploader,SnepffPostUpdateUploader):
    """Originally downloaded from: http://www.snpedia.org/"""

    name = "snpedia"
    id_type = 'observed'

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

