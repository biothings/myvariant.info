import os
import glob

from .dbnsfp_mapping import mapping
from .dbnsfp_parser import load_file
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
    def get_mapping(cls):
        return mapping

    def jobs(self):
        paths = glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_PATTERN))
        assembly = self.__class__.__metadata__["assembly"]
        return map(lambda path: (path, assembly), paths)

    def load_data(self, path, assembly):
        self.logger.debug("loading file " + path)
        return load_file(path, version=assembly)


class DBNSFPHG38Uploader(DBNSFPBaseUploader):
    name = "dbnsfp_hg38"
    main_source = "dbnsfp"
    __metadata__ = {
        "assembly": "hg38",
        "src_meta": SRC_META
    }


class DBNSFPHG19Uploader(DBNSFPBaseUploader):
    name = "dbnsfp_hg19"
    main_source = "dbnsfp"
    __metadata__ = {
        "assembly": "hg19",
        "src_meta": SRC_META
    }
