
from .dbsnp_dump import main as download
from .dbsnp_vcf_parser import load_data
import biothings.dataload.uploader as uploader

class DBSNPUploader(uploader.NoBatchIgnoreDuplicatedSourceUploader):

    name = "dbsnp"

    def load_data(self,data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        return load_data(data_folder=data_folder)

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
