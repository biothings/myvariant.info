import os
import glob
import zipfile

from .geno2mp_parser import load_data
import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader

class Geno2MPUploader(SnpeffPostUpdateUploader):

    name = "geno2mp"
    __metadata__ = {
        "mapper" : 'observed',
        "assembly" : "hg19",
        "src_meta" : {
            "url" : "http://geno2mp.gs.washington.edu",
            "license_url" : "http://geno2mp.gs.washington.edu/Geno2MP/#/terms",
            "license_url_short": "http://bit.ly/2QyGCIN"
        }
    }

    def load_data(self,data_folder):
        # there's one vcf file there, let's get it
        input_file = glob.glob(os.path.join(data_folder,"*.vcf"))
        if len(input_file) != 1:
            raise uploader.ResourceError("Expecting only one VCF file, got: %s" % input_file)
        input_file = input_file.pop()
        self.logger.info("Load data from file '%s'" % input_file)
        return load_data(input_file)


    @classmethod
    def get_mapping(klass):
        mapping = {
            "geno2mp": {
                "properties": {
                    "hpo_count": {
                        "type": "integer",
                    },
                }
            }
        }
        return mapping

