import itertools, glob, os

from .dbsnp_dump import main as download
from .dbsnp_vcf_parser import load_data
import biothings.dataload.uploader as uploader
from dataload.uploader import SnepffPostUpdateUploader


class DBSNPUploader(uploader.IgnoreDuplicatedSourceUploader,
                    uploader.ParallelizedSourceUploader,
                    SnepffPostUpdateUploader):

    name = "dbsnp"
    storage_class = uploader.IgnoreDuplicatedStorage

    GLOB_PATTERN = "human_9606_*_GRCh*/VCF/00-All.vcf.gz"

    def jobs(self):
        files = glob.glob(os.path.join(self.data_folder,self.__class__.GLOB_PATTERN))
        if len(files) != 2:
            raise uploader.ResourceError("Expected 2 files, got: %s" % files)
        chrom_list = [str(i) for i in range(1, 23)] + ['X', 'Y', 'MT']
        return list(itertools.product(files,chrom_list))

    def load_data(self,input_file,chrom):
        self.logger.info("Load data from '%s' for chr %s" % (input_file,chrom))
        return load_data(input_file,chrom)

    def post_update_data(self):
        super(DBSNPUploader,self).post_update_data()
        self.logger.info("Indexing 'rsid'")
        # background=true or it'll lock the whole database...
        self.collection.create_index("dbsnp.rsid",background=True)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "dbsnp": {
                "properties": {
                    "allele_origin": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "class": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "flags": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "gmaf": {
                        "type": "float"
                    },
                    "hg19": {
                        "properties": {
                            "end": {
                                "type": "long"
                            },
                            "start": {
                                "type": "long"
                            }
                        }
                    },
                    "ref": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "rsid": {
                        "type": "string",
                        "include_in_all": True,
                        "analyzer": "string_lowercase"
                    },
                    "var_subtype": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "vartype": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "validated": {
                        "type": "boolean"
                    },
                    "gene": {
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "analyzer": "string_lowercase",
                                "include_in_all": True
                            },
                            "geneid": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            }
                        }
                    }
                }
            }
        }
        return mapping
