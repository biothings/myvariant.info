import os
import glob
import zipfile

from .evs_parser import load_data
import biothings.dataload.uploader as uploader
from dataload.uploader import SnpeffPostUpdateUploader


class EVSBaseUploader(SnpeffPostUpdateUploader):

    def load_data(self,data_folder):
        #self.prepare()
        self.logger.info("Load data from '%s'" % data_folder)
        return load_data(data_folder,
                         self.__class__.__metadata__["assembly"])

    @classmethod
    def get_mapping(klass):
        mapping = {
            "evs": {
                "properties": {
                    "chrom": {
                        "type": "string"
                    },
                    "hg19": {
                        "properties": {
                            "start": {
                                "type": "long"
                            },
                            "end": {
                                "type": "long"
                            }
                        }
                    },
                    "hg38": {
                        "properties": {
                            "start": {
                                "type": "long"
                            },
                            "end": {
                                "type": "long"
                            }
                        }
                    },
                    "ref": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "gene": {
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "accession": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "hgvs": {
                        "properties": {
                            "coding": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "protein": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            }
                        }
                    },
                    "clinical_info": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "function_gvs": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "grantham_score": {
                        "type": "float"
                    },
                    "rsid": {
                        "type": "string",
                        "analyzer": "string_lowercase",
                        "include_in_all": True
                    }
                }
            }
        }
        return mapping

class EVSHg19Uploader(EVSBaseUploader):
    name = "evs_hg19"
    main_source = "evs"
    __metadata__ = {"mapper" : 'observed',
                    "assembly" : "hg19"}


class EVSHg38Uploader(EVSBaseUploader):
    name = "evs_hg38"
    main_source = "evs"
    __metadata__ = {"mapper" : 'observed',
                    "assembly" : "hg38"}

