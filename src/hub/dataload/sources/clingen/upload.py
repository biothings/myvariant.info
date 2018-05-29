import os

from ...uploader import SnpeffPostUpdateUploader
from .parser import load_data


class ClingenUploader(SnpeffPostUpdateUploader):
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

    def load_data(self,data_folder):
        # there's one vcf file there, let's get it
        input_file = os.path.join(data_folder,"mvi_ca")
        assert os.path.exists(input_file), "Can't find input file '%s'" % input_file
        self.logger.info("Load data from file '%s'" % input_file)
        return load_data(input_file)

    @classmethod
    def get_mapping(self):
        mapping = {}
        return mapping
