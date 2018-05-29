import os, glob

import biothings.hub.dataload.uploader as uploader

from ...uploader import SnpeffPostUpdateUploader
from .parser import load_data


class ClingenUploader(SnpeffPostUpdateUploader,uploader.ParallelizedSourceUploader):
    name = "clingen"
    __metadata__ = {"mapper": 'observed',
            "assembly": "hg38",
            "src_meta": {
                "url": "https://www.clinicalgenome.org",
                "license_url": "https://www.clinicalgenome.org/about/terms-of-use",
                "license_url_short": "",
                "licence": "CC0 1.0",
                }
            }

    GLOB_PATTERN = "mvi_ca.split.*"

    def jobs(self):
        # tuple(input_file,) (only one arg, but still need a tuple
        return map(lambda e: (e, ),
                   glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_PATTERN)))

    def load_data(self,input_file):
        # there's one vcf file there, let's get it
        assert os.path.exists(input_file), "Can't find input file '%s'" % input_file
        self.logger.info("Load data from file '%s'" % input_file)
        return load_data(input_file)

    @classmethod
    def get_mapping(self):
        mapping = {}
        return mapping
