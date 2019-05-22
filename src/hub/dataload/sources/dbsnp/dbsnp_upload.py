import itertools, glob, os

from .dbsnp_json_parser import load_data_file
import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader


SRC_META = {
        "url" : "https://www.ncbi.nlm.nih.gov/projects/SNP/",
        "license_url" : "https://www.ncbi.nlm.nih.gov/home/about/policies/",
        "license_url_short": "http://bit.ly/2AqoLOc"
        }


class DBSNPBaseUploader(uploader.IgnoreDuplicatedSourceUploader,
                    uploader.ParallelizedSourceUploader,
                    SnpeffPostUpdateUploader):

    def jobs(self):
        files = glob.glob(os.path.join(self.data_folder,"refsnp-chr*.json.bz2"))
        return [(f,) for f in files]

    def load_data(self,input_file):
        self.logger.info("Load data from '%s'",input_file)
        return load_data_file(input_file,self.__class__.__metadata__["assembly"])

    def post_update_data(self, *args, **kwargs):
        super(DBSNPBaseUploader,self).post_update_data(*args,**kwargs)
        self.logger.info("Indexing 'rsid'")
        # background=true or it'll lock the whole database...
        self.collection.create_index("dbsnp.rsid",background=True)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "dbsnp": {
                "properties": {
                    "allele_origin": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "class": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "flags": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "gmaf": {
                        "type": "float"
                    },
                    klass.__metadata__["assembly"]: {
                        "properties": {
                            "end": {
                                "type": "integer"
                            },
                            "start": {
                                "type": "integer"
                            }
                        }
                    },
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "rsid": {
                        "type": "text",
                        "copy_to" : ["all"],
                        "analyzer": "string_lowercase"
                    },
                    "var_subtype": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "vartype": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "validated": {
                        "type": "boolean"
                    },
                    "gene": {
                        "properties": {
                            "symbol": {
                                "type": "text",
                                "analyzer": "string_lowercase",
                                "copy_to" : ["all"]
                            },
                            "geneid": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            }
                        }
                    }
                }
            }
        }
        return mapping


class DBSNPHg19Uploader(DBSNPBaseUploader):

    main_source = "dbsnp"
    name = "dbsnp_hg19"
    __metadata__ = {
            "mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : SRC_META
            }


class DBSNPHg38Uploader(DBSNPBaseUploader):

    main_source = "dbsnp"
    name = "dbsnp_hg38"
    __metadata__ = {
            "mapper" : 'observed',
            "assembly" : "hg38",
            "src_meta" : SRC_META
            }

