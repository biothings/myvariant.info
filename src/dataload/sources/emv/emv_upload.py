import os
import glob
import zipfile

from .emv_parser import load_data
import biothings.dataload.uploader as uploader

class EMVUploader(uploader.BaseSourceUploader):

    name = "emv"

    @uploader.ensure_prepared
    def load_data(self,data_folder):
        # there's one csv file there, let's get it
        input_file = glob.glob(os.path.join(data_folder,"EmVClass*.csv"))
        if len(input_file) != 1:
            raise uploader.ResourceError("Expecting only one CSV file, got: %s" % input_file)
        input_file = input_file.pop()
        self.logger.info("Load data from file '%s'" % input_file)
        return load_data(input_file)


    @classmethod
    def get_mapping(klass):
        mapping = {
            "emv": {
                "properties": {
                    "gene": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "include_in_all": True
                    },
                    "egl_variant": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "include_in_all": True
                    },
                    "egl_protein": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "egl_classification": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "hgvs": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "include_in_all": True
                    },
                    "clinvar_rcv": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "include_in_all": True
                    }
                }
            }
        }
        return mapping
