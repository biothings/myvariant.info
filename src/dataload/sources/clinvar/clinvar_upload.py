
from .clinvar_xml_parser import load_data as load_common
from . import get_mapping
import biothings.dataload.uploader as uploader

class ClinvarHG19Uploader(uploader.BaseSourceUploader):

    name = "clinvar_hg19"
    main_source = "clinvar"

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        return load_common(self,hg19=True,data_folder=data_folder)

    def get_mapping(self):
        return get_mapping()


class ClinvarHG38Uploader(uploader.BaseSourceUploader):

    name = "clinvar_hg38"
    main_source = "clinvar"

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        return load_common(self,hg19=False,data_folder=data_folder)

    def get_mapping(self):
        return get_mapping()
