import biothings.dataload.uploader as uploader

class SnpediaUploader(uploader.DummySourceUploader):
    """Originally downloaded from: http://www.snpedia.org/"""

    name = "snpedia"

    def get_mapping(self):
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

