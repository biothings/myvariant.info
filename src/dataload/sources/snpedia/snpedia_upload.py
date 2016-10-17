import biothings.dataload.uploader as uploader

class SnpediaUploader(uploader.DummySourceUploader):
    """Originally downloaded from: http://www.snpedia.org/"""

    name = "snpedia"

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

