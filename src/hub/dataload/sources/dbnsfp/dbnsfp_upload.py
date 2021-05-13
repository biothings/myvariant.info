import os
import glob

from .dbnsfp_mapping import mapping
from .dbnsfp_parser import load_data_file as load_common
import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader
from hub.dataload.storage import MyVariantIgnoreDuplicatedStorage


SRC_META = {
    "url": "https://sites.google.com/site/jpopgen/dbNSFP",
    "license_url": "https://sites.google.com/site/jpopgen/dbNSFP",
    "license_url_short": "http://bit.ly/2VLnQBz"
}


class DBNSFPBaseUploader(uploader.ParallelizedSourceUploader,
                         SnpeffPostUpdateUploader):

    storage_class = MyVariantIgnoreDuplicatedStorage
    GLOB_PATTERN = "dbNSFP*_variant.chr*"

    @classmethod
    def get_mapping(klass):
        return mapping

    def jobs(self):
        # tuple(input_file,version), where version is either hg38 or hg19)
        return map(lambda e: (e, self.__class__.__metadata__["assembly"]),
                   glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_PATTERN)))

    def load_data(self, input_file, hg):
        return load_common(input_file, version=hg)


class DBNSFPHG38Uploader(DBNSFPBaseUploader):

    name = "dbnsfp_hg38"
    main_source = "dbnsfp"
    __metadata__ = {
            "assembly": "hg38",
            "src_meta" : SRC_META
            }


class DBNSFPHG19Uploader(DBNSFPBaseUploader):

    name = "dbnsfp_hg19"
    main_source = "dbnsfp"
    __metadata__ = {
            "assembly": "hg19",
            "src_meta" : SRC_META
            }
