import os
import glob
import zipfile

from .grasp_parser import load_data
import biothings.hub.dataload.uploader as uploader
import biothings.hub.dataload.storage as storage
from ...uploader import SnpeffPostUpdateUploader

class GraspUploader(uploader.IgnoreDuplicatedSourceUploader,
                    SnpeffPostUpdateUploader):

    name = "grasp"
    strorage_class = storage.IgnoreDuplicatedStorage
    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "https://grasp.nhlbi.nih.gov/Updates.aspx",
                "license_url" : "https://grasp.nhlbi.nih.gov/Terms.aspx",
                "license_url_short": "https://goo.gl/0V1pj5"
                }
            }

    def load_data(self,data_folder):
        # there's one zip there, let's get the zipped filename
        zgrasp = glob.glob(os.path.join(data_folder,"*.zip"))
        if len(zgrasp) != 1:
            raise uploader.ResourceError("Expecting one zip only, got: %s" % repr(zgrasp))
        zgrasp = zgrasp.pop()
        zf = zipfile.ZipFile(zgrasp)
        content = [e.filename for e in zf.filelist]
        if len(content) != 1:
            raise uploader.ResourceError("Expecting only one file in the archive, got: %s" % content)
        input_file = content.pop()
        input_file = os.path.join(data_folder,"sorted")#input_file)
        self.logger.info("Load data from file '%s'" % input_file)
        res = load_data(input_file)
        return res


    @classmethod
    def get_mapping(klass):
        mapping = {
            "grasp": {
                "properties": {
                    "hg19": {
                        "properties": {
                            "chr": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "pos": {
                                "type": "long"
                            }
                        }
                    },
                    "srsid": {
                        "type": "long"
                    },
                    "hugfield": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "publication": {
                        "properties": {
                            "journal": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "title": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "pmid": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "snpid": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "location_within_paper": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "p_value": {
                                "type": "float"
                            },
                            "phenotype": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "paper_phenotype_description": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            },
                            "paper_phenotype_categories": {
                                "type": "string",
                                "analyzer": "string_lowercase"
                            }
                        }
                    },
                    "includes_male_female_only_analyses": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "exclusively_male_female": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "initial_sample_description": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "replication_sample_description": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "platform_snps_passing_qc": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "gwas_ancestry_description": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "discovery": {
                        "properties": {
                            "total_samples": {
                                "type": "integer"
                            },
                            "european": {
                                "type": "integer"
                            },
                            "african": {
                                "type": "integer"
                            },
                            "east_asian": {
                                "type": "integer"
                            },
                            "indian_south_asian": {
                                "type": "integer"
                            },
                            "hispanic": {
                                "type": "integer"
                            },
                            "native": {
                                "type": "integer"
                            },
                            "micronesian": {
                                "type": "integer"
                            },
                            "arab_me": {
                                "type": "integer"
                            },
                            "mixed": {
                                "type": "integer"
                            },
                            "unspecified": {
                                "type": "integer"
                            },
                            "filipino": {
                                "type": "integer"
                            },
                            "indonesian": {
                                "type": "integer"
                            }
                        }
                    },
                    "replication": {
                        "properties": {
                            "total_samples": {
                                "type": "integer"
                            },
                            "european": {
                                "type": "integer"
                            },
                            "african": {
                                "type": "integer"
                            },
                            "east_asian": {
                                "type": "integer"
                            },
                            "indian_south_asian": {
                                "type": "integer"
                            },
                            "hispanic": {
                                "type": "integer"
                            },
                            "native": {
                                "type": "integer"
                            },
                            "micronesian": {
                                "type": "integer"
                            },
                            "arab_me": {
                                "type": "integer"
                            },
                            "mixed": {
                                "type": "integer"
                            },
                            "unspecified": {
                                "type": "integer"
                            },
                            "filipino": {
                                "type": "integer"
                            },
                            "indonesian": {
                                "type": "integer"
                            }
                        }
                    },
                    "in_gene": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "nearest_gene": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "in_mirna": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "in_mirna_bs": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "oreg_anno": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "human_enhancer": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "rna_edit": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "polyphen2": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "sift": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "uniprot": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    },
                    "eqtl_meth_metab_study": {
                        "type": "string",
                        "analyzer": "string_lowercase"
                    }
                }
            }
        }
        return mapping

