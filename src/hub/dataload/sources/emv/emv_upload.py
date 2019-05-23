import os
import glob

from .emv_parser import load_data
import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader


SRC_META = {
    "url" : "http://www.egl-eurofins.com/emvclass/emvclass.php",
    "license_url" : "http://www.egl-eurofins.com/emvclass/emvclass.php",
    "license_url_short": "http://bit.ly/2RieoY1"
}


class EMVBaseUploader(SnpeffPostUpdateUploader):

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        return load_data(data_folder,self.__class__.__metadata__["assembly"])


    @classmethod
    def get_mapping(klass):
        mapping = {
            "emv": {
                "properties": {
                    "gene": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "variant_id": {
                        "type": "integer"
                    },
                    "exon": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "egl_variant": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "hgvs": {
                        "type": "text"
                    },
                    "egl_classification": {
                        "type": "text"
                    },
                    "egl_protein": {
                        "type": "text"
                    }
                }
            }
        }
        return mapping


class EMVHg19Uploader(EMVBaseUploader):

    name = "emv_hg19"
    main_source = "emv"
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : SRC_META,
            }


class EMVHg38Uploader(EMVBaseUploader):

    name = "emv_hg38"
    main_source = "emv"
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg38",
            "src_meta" : SRC_META,
            }
