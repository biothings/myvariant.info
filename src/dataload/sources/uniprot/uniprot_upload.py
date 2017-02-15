import biothings.dataload.uploader as uploader
from dataload.uploader import SnpeffPostUpdateUploader

class UniprotUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):

    name = "uniprot"
    __metadata__ = {"mapper" : 'observed',
                    "assembly" : "hg38"}

    @classmethod
    def get_mapping(klass):
        mapping = {}
        return mapping

