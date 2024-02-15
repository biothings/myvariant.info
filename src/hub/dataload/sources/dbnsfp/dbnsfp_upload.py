import os
import glob

# from .dbnsfp_mapping_44a_v1 import mapping as mapping_v1
# from .dbnsfp_parser_44a_v1 import load_file as load_file_v1
# from .dbnsfp_mapping_44a_v2 import mapping as mapping_v2
# from .dbnsfp_parser_44a_v2 import load_file as load_file_v2
from .dbnsfp_mapping_45a_v1 import mapping as mapping_v1
from .dbnsfp_parser_45a_v1 import load_file as load_file_v1

import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader
from hub.dataload.storage import MyVariantIgnoreDuplicatedStorage


SRC_META = {
    "url": "https://sites.google.com/site/jpopgen/dbNSFP",
    "license_url": "https://sites.google.com/site/jpopgen/dbNSFP",
    "license_url_short": "http://bit.ly/2VLnQBz"
}


class DBNSFPBaseUploaderV1(uploader.ParallelizedSourceUploader, SnpeffPostUpdateUploader):

    storage_class = MyVariantIgnoreDuplicatedStorage
    GLOB_PATTERN = "dbNSFP*_variant.chr*"

    @classmethod
    def get_mapping(cls):
        return mapping_v1

    def jobs(self):
        paths = glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_PATTERN))
        assembly = self.__class__.__metadata__["assembly"]
        return map(lambda path: (path, assembly), paths)

    def load_data(self, path, assembly):
        self.logger.debug("loading file " + path)
        return load_file_v1(path, assembly=assembly)


class DBNSFPBaseUploaderV2(uploader.ParallelizedSourceUploader, SnpeffPostUpdateUploader):

    storage_class = MyVariantIgnoreDuplicatedStorage
    GLOB_PATTERN = "dbNSFP*_variant.chr*"

    @classmethod
    def get_mapping(cls):
        return mapping_v1

    def jobs(self):
        paths = glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_PATTERN))
        assembly = self.__class__.__metadata__["assembly"]
        return map(lambda path: (path, assembly), paths)

    def load_data(self, path, assembly):
        self.logger.debug("loading file " + path)
        return load_file_v2(path, assembly=assembly)


class DBNSFPHG38UploaderV1(DBNSFPBaseUploaderV1):
    name = "dbnsfp_hg38_v1"
    main_source = "dbnsfp"
    __metadata__ = {
        "assembly": "hg38",
        "src_meta": SRC_META
    }


class DBNSFPHG19UploaderV1(DBNSFPBaseUploaderV1):
    name = "dbnsfp_hg19_v1"
    main_source = "dbnsfp"
    __metadata__ = {
        "assembly": "hg19",
        "src_meta": SRC_META
    }


class DBNSFPHG38UploaderV2(DBNSFPBaseUploaderV2):
    name = "dbnsfp_hg38_v2"
    main_source = "dbnsfp"
    __metadata__ = {
        "assembly": "hg38",
        "src_meta": SRC_META
    }


class DBNSFPHG19UploaderV2(DBNSFPBaseUploaderV2):
    name = "dbnsfp_hg19_v2"
    main_source = "dbnsfp"
    __metadata__ = {
        "assembly": "hg19",
        "src_meta": SRC_META
    }
