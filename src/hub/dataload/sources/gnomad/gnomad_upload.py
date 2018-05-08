import os
import glob
import zipfile

import biothings.hub.dataload.uploader as uploader
import biothings.hub.dataload.storage as storage

from .gnomad_parser_genomes import load_data as load_data_genomes
from .gnomad_parser_exomes import load_data as load_data_exomes
from hub.dataload.uploader import SnpeffPostUpdateUploader


class GnomadBaseUploader(uploader.IgnoreDuplicatedSourceUploader,SnpeffPostUpdateUploader):

    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "http://gnomad.broadinstitute.org",
                "license_url" : "http://gnomad.broadinstitute.org/terms",
                "license_url_short": "http://bit.ly/2I1cl1I",
                "license" : "ODbL"
                }
            }


class GnomadExomesUploader(GnomadBaseUploader):

    main_source = "gnomad"
    name = "gnomad_exomes"

    def load_data(self,data_folder):
        files = glob.glob(os.path.join(data_folder,"exomes","*.vcf"))
        if len(files) != 1:
            raise uploader.ResourceError("Expecting only one VCF file, got: %s" % files)
        input_file = files.pop()
        assert os.path.exists("%s.gz.tbi" % input_file)
        self.logger.info("Load data from file '%s'" % input_file)
        res = load_data_exomes(input_file)
        return res

    @classmethod
    def get_mapping(klass):
        mapping = {
            "gnomad_exome": {
                "properties": {
                    "fs": {
                        "type": "float"
                    },
                    "pos": {
                        "type": "integer"
                    },
                    "inbreedingcoeff": {
                        "type": "float"
                    },
                    "af": {
                        "properties": {
                            "af": {
                                "type": "float"
                            },
                            "af_eas": {
                                "type": "float"
                            },
                            "af_sas_male": {
                                "type": "float"
                            },
                            "af_fin_female": {
                                "type": "float"
                            },
                            "af_oth_male": {
                                "type": "float"
                            },
                            "af_raw": {
                                "type": "float"
                            },
                            "af_eas_female": {
                                "type": "float"
                            },
                            "af_amr": {
                                "type": "float"
                            },
                            "af_sas": {
                                "type": "float"
                            },
                            "af_fin": {
                                "type": "float"
                            },
                            "af_asj_female": {
                                "type": "float"
                            },
                            "af_amr_male": {
                                "type": "float"
                            },
                            "af_afr_male": {
                                "type": "float"
                            },
                            "af_amr_female": {
                                "type": "float"
                            },
                            "af_male": {
                                "type": "float"
                            },
                            "af_oth": {
                                "type": "float"
                            },
                            "af_fin_male": {
                                "type": "float"
                            },
                            "af_oth_female": {
                                "type": "float"
                            },
                            "af_female": {
                                "type": "float"
                            },
                            "af_asj_male": {
                                "type": "float"
                            },
                            "af_eas_male": {
                                "type": "float"
                            },
                            "af_popmax": {
                                "type": "float"
                            },
                            "af_afr": {
                                "type": "float"
                            },
                            "af_sas_female": {
                                "type": "float"
                            },
                            "af_asj": {
                                "type": "float"
                            },
                            "af_afr_female": {
                                "type": "float"
                            },
                            "af_nfe_female": {
                                "type": "float"
                            },
                            "af_nfe": {
                                "type": "float"
                            },
                            "af_nfe_male": {
                                "type": "float"
                            }
                        }
                    },
                    "baseqranksum": {
                        "type": "float"
                    },
                    "ac": {
                        "properties": {
                            "ac_nfe_female": {
                                "type": "integer"
                            },
                            "ac_amr_female": {
                                "type": "integer"
                            },
                            "ac_fin_male": {
                                "type": "integer"
                            },
                            "ac": {
                                "type": "integer"
                            },
                            "ac_afr": {
                                "type": "integer"
                            },
                            "ac_fin": {
                                "type": "integer"
                            },
                            "ac_eas_male": {
                                "type": "integer"
                            },
                            "ac_male": {
                                "type": "integer"
                            },
                            "ac_raw": {
                                "type": "integer"
                            },
                            "ac_sas": {
                                "type": "integer"
                            },
                            "ac_oth_female": {
                                "type": "integer"
                            },
                            "ac_female": {
                                "type": "integer"
                            },
                            "ac_oth": {
                                "type": "integer"
                            },
                            "ac_asj_female": {
                                "type": "integer"
                            },
                            "ac_afr_male": {
                                "type": "integer"
                            },
                            "ac_afr_female": {
                                "type": "integer"
                            },
                            "ac_asj_male": {
                                "type": "integer"
                            },
                            "ac_nfe": {
                                "type": "integer"
                            },
                            "ac_oth_male": {
                                "type": "integer"
                            },
                            "ac_sas_male": {
                                "type": "integer"
                            },
                            "ac_fin_female": {
                                "type": "integer"
                            },
                            "ac_amr": {
                                "type": "integer"
                            },
                            "ac_nfe_male": {
                                "type": "integer"
                            },
                            "ac_eas": {
                                "type": "integer"
                            },
                            "ac_popmax": {
                                "type": "integer"
                            },
                            "ac_eas_female": {
                                "type": "integer"
                            },
                            "ac_sas_female": {
                                "type": "integer"
                            },
                            "ac_asj": {
                                "type": "integer"
                            },
                            "ac_amr_male": {
                                "type": "integer"
                            }
                        }
                    },
                    "type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "an": {
                        "properties": {
                            "an_asj_male": {
                                "type": "integer"
                            },
                            "an_asj_female": {
                                "type": "integer"
                            },
                            "an_oth": {
                                "type": "integer"
                            },
                            "an_sas_male": {
                                "type": "integer"
                            },
                            "an_male": {
                                "type": "integer"
                            },
                            "an_popmax": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "an_fin_male": {
                                "type": "integer"
                            },
                            "an_amr": {
                                "type": "integer"
                            },
                            "an_afr": {
                                "type": "integer"
                            },
                            "an_amr_female": {
                                "type": "integer"
                            },
                            "an_nfe": {
                                "type": "integer"
                            },
                            "an_afr_female": {
                                "type": "integer"
                            },
                            "an_eas": {
                                "type": "integer"
                            },
                            "an_fin_female": {
                                "type": "integer"
                            },
                            "an_sas": {
                                "type": "integer"
                            },
                            "an_raw": {
                                "type": "integer"
                            },
                            "an_afr_male": {
                                "type": "integer"
                            },
                            "an_nfe_female": {
                                "type": "integer"
                            },
                            "an_eas_female": {
                                "type": "integer"
                            },
                            "an_oth_male": {
                                "type": "integer"
                            },
                            "an_sas_female": {
                                "type": "integer"
                            },
                            "an_fin": {
                                "type": "integer"
                            },
                            "an_female": {
                                "type": "integer"
                            },
                            "an_oth_female": {
                                "type": "integer"
                            },
                            "an_asj": {
                                "type": "integer"
                            },
                            "an_eas_male": {
                                "type": "integer"
                            },
                            "an_nfe_male": {
                                "type": "integer"
                            },
                            "an_amr_male": {
                                "type": "integer"
                            }
                        }
                    },
                    "filter": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "vqsr_culprit": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "clippingranksum": {
                        "type": "float"
                    },
                    "hom": {
                        "properties": {
                            "hom_nfe": {
                                "type": "integer"
                            },
                            "hom_amr": {
                                "type": "integer"
                            },
                            "hom_eas": {
                                "type": "integer"
                            },
                            "hom_oth": {
                                "type": "integer"
                            },
                            "hom_raw": {
                                "type": "integer"
                            },
                            "hom_fin": {
                                "type": "integer"
                            },
                            "hom_male": {
                                "type": "integer"
                            },
                            "hom_asj": {
                                "type": "integer"
                            },
                            "hom_female": {
                                "type": "integer"
                            },
                            "hom_afr": {
                                "type": "integer"
                            },
                            "hom": {
                                "type": "integer"
                            },
                            "hom_sas": {
                                "type": "integer"
                            }
                        }
                    },
                    "mq": {
                        "properties": {
                            "mqranksum": {
                                "type": "float"
                            },
                            "mq": {
                                "type": "float"
                            }
                        }
                    },
                    "hemi": {
                        "properties": {
                            "hemi_raw": {
                                "type": "integer"
                            },
                            "hemi": {
                                "type": "integer"
                            },
                            "hemi_nfe": {
                                "type": "integer"
                            },
                            "hemi_eas": {
                                "type": "integer"
                            },
                            "hemi_fin": {
                                "type": "integer"
                            },
                            "hemi_oth": {
                                "type": "integer"
                            },
                            "hemi_asj": {
                                "type": "integer"
                            },
                            "hemi_sas": {
                                "type": "integer"
                            },
                            "hemi_afr": {
                                "type": "integer"
                            },
                            "hemi_amr": {
                                "type": "integer"
                            }
                        }
                    },
                    "vqslod": {
                        "type": "float"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "qd": {
                        "type": "float"
                    },
                    "readposranksum": {
                        "type": "float"
                    },
                    "alleles": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "multi-allelic": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "rsid": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    #"gc": {
                    #    "properties": {
                    #        "gc_eas_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_asj_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_oth": {
                    #            "type": "integer"
                    #        },
                    #        "gc_amr_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_fin_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_nfe_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_fin_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_eas_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_amr": {
                    #            "type": "integer"
                    #        },
                    #        "gc_raw": {
                    #            "type": "integer"
                    #        },
                    #        "gc": {
                    #            "type": "integer"
                    #        },
                    #        "gc_nfe": {
                    #            "type": "integer"
                    #        },
                    #        "gc_sas_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_oth_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_eas": {
                    #            "type": "integer"
                    #        },
                    #        "gc_afr": {
                    #            "type": "integer"
                    #        },
                    #        "gc_sas": {
                    #            "type": "integer"
                    #        },
                    #        "gc_afr_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_amr_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_fin": {
                    #            "type": "integer"
                    #        },
                    #        "gc_nfe_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_afr_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_asj": {
                    #            "type": "integer"
                    #        },
                    #        "gc_asj_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_sas_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_oth_male": {
                    #            "type": "integer"
                    #        }
                    #    }
                    #}
                }
            }
        }
        return mapping


class GnomadGenomesUploader(GnomadBaseUploader, uploader.ParallelizedSourceUploader):

    main_source = "gnomad"
    name = "gnomad_genomes"
    GLOB_PATTERN = "gnomad.genomes.*.vcf"

    def jobs(self):
        # tuple(input_file,version), where version is either hg38 or hg19)
        files = [(e,) for e in glob.glob(os.path.join(self.data_folder, "genomes", self.__class__.GLOB_PATTERN))]
        assert len(files) > 23, "Expecting at least 23 VCF files, got: %s" % files
        return files

    def load_data(self, input_file):
        self.logger.info("Load data from file '%s'" % input_file)
        res = load_data_genomes(input_file)
        return res

    @classmethod
    def get_mapping(klass):
        mapping = {
            "gnomad_genome": {
                "properties": {
                    "hemi": {
                        "properties": {
                            "hemi": {
                                "type": "integer"
                            },
                            "hemi_fin": {
                                "type": "integer"
                            },
                            "hemi_afr": {
                                "type": "integer"
                            },
                            "hemi_raw": {
                                "type": "integer"
                            },
                            "hemi_asj": {
                                "type": "integer"
                            },
                            "hemi_nfe": {
                                "type": "integer"
                            },
                            "hemi_amr": {
                                "type": "integer"
                            },
                            "hemi_eas": {
                                "type": "integer"
                            },
                            "hemi_oth": {
                                "type": "integer"
                            }
                        }
                    },
                    "af": {
                        "properties": {
                            "af": {
                                "type": "float"
                            },
                            "af_nfe_female": {
                                "type": "float"
                            },
                            "af_afr_male": {
                                "type": "float"
                            },
                            "af_asj_female": {
                                "type": "float"
                            },
                            "af_nfe_male": {
                                "type": "float"
                            },
                            "af_afr_female": {
                                "type": "float"
                            },
                            "af_fin_male": {
                                "type": "float"
                            },
                            "af_fin_female": {
                                "type": "float"
                            },
                            "af_eas": {
                                "type": "float"
                            },
                            "af_amr": {
                                "type": "float"
                            },
                            "af_afr": {
                                "type": "float"
                            },
                            "af_male": {
                                "type": "float"
                            },
                            "af_eas_male": {
                                "type": "float"
                            },
                            "af_oth": {
                                "type": "float"
                            },
                            "af_nfe": {
                                "type": "float"
                            },
                            "af_oth_female": {
                                "type": "float"
                            },
                            "af_female": {
                                "type": "float"
                            },
                            "af_asj": {
                                "type": "float"
                            },
                            "af_amr_female": {
                                "type": "float"
                            },
                            "af_fin": {
                                "type": "float"
                            },
                            "af_popmax": {
                                "type": "float"
                            },
                            "af_asj_male": {
                                "type": "float"
                            },
                            "af_oth_male": {
                                "type": "float"
                            },
                            "af_raw": {
                                "type": "float"
                            },
                            "af_amr_male": {
                                "type": "float"
                            },
                            "af_eas_female": {
                                "type": "float"
                            }
                        }
                    },
                    "rsid": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    #"gc": {
                    #    "properties": {
                    #        "gc_nfe": {
                    #            "type": "integer"
                    #        },
                    #        "gc": {
                    #            "type": "integer"
                    #        },
                    #        "gc_eas": {
                    #            "type": "integer"
                    #        },
                    #        "gc_eas_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_eas_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_fin_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_raw": {
                    #            "type": "integer"
                    #        },
                    #        "gc_afr_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_oth_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_fin_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_oth": {
                    #            "type": "integer"
                    #        },
                    #        "gc_asj_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_amr_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_oth_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_asj": {
                    #            "type": "integer"
                    #        },
                    #        "gc_nfe_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_fin": {
                    #            "type": "integer"
                    #        },
                    #        "gc_amr_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_afr_male": {
                    #            "type": "integer"
                    #        },
                    #        "gc_asj_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_afr": {
                    #            "type": "integer"
                    #        },
                    #        "gc_nfe_female": {
                    #            "type": "integer"
                    #        },
                    #        "gc_amr": {
                    #            "type": "integer"
                    #        }
                    #    }
                    #},
                    "filter": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "vqslod": {
                        "type": "float"
                    },
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "mq": {
                        "properties": {
                            "mq": {
                                "type": "float"
                            },
                            "mqranksum": {
                                "type": "float"
                            }
                        }
                    },
                    "readposranksum": {
                        "type": "float"
                    },
                    "multi-allelic": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "clippingranksum": {
                        "type": "float"
                    },
                    "fs": {
                        "type": "float"
                    },
                    "type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "ac": {
                        "properties": {
                            "ac_nfe_male": {
                                "type": "integer"
                            },
                            "ac_amr_female": {
                                "type": "integer"
                            },
                            "ac_afr_female": {
                                "type": "integer"
                            },
                            "ac_oth_female": {
                                "type": "integer"
                            },
                            "ac_amr_male": {
                                "type": "integer"
                            },
                            "ac_popmax": {
                                "type": "integer"
                            },
                            "ac_afr_male": {
                                "type": "integer"
                            },
                            "ac_fin_male": {
                                "type": "integer"
                            },
                            "ac_eas": {
                                "type": "integer"
                            },
                            "ac_asj_female": {
                                "type": "integer"
                            },
                            "ac_oth_male": {
                                "type": "integer"
                            },
                            "ac": {
                                "type": "integer"
                            },
                            "ac_fin_female": {
                                "type": "integer"
                            },
                            "ac_nfe_female": {
                                "type": "integer"
                            },
                            "ac_female": {
                                "type": "integer"
                            },
                            "ac_raw": {
                                "type": "integer"
                            },
                            "ac_fin": {
                                "type": "integer"
                            },
                            "ac_oth": {
                                "type": "integer"
                            },
                            "ac_afr": {
                                "type": "integer"
                            },
                            "ac_asj_male": {
                                "type": "integer"
                            },
                            "ac_nfe": {
                                "type": "integer"
                            },
                            "ac_asj": {
                                "type": "integer"
                            },
                            "ac_eas_male": {
                                "type": "integer"
                            },
                            "ac_eas_female": {
                                "type": "integer"
                            },
                            "ac_male": {
                                "type": "integer"
                            },
                            "ac_amr": {
                                "type": "integer"
                            }
                        }
                    },
                    "qd": {
                        "type": "float"
                    },
                    "an": {
                        "properties": {
                            "an_nfe": {
                                "type": "integer"
                            },
                            "an_amr_male": {
                                "type": "integer"
                            },
                            "an_afr_male": {
                                "type": "integer"
                            },
                            "an_fin": {
                                "type": "integer"
                            },
                            "an_nfe_female": {
                                "type": "integer"
                            },
                            "an_oth_female": {
                                "type": "integer"
                            },
                            "an_asj_male": {
                                "type": "integer"
                            },
                            "an_asj": {
                                "type": "integer"
                            },
                            "an": {
                                "type": "integer"
                            },
                            "an_fin_female": {
                                "type": "integer"
                            },
                            "an_eas_male": {
                                "type": "integer"
                            },
                            "an_amr_female": {
                                "type": "integer"
                            },
                            "an_raw": {
                                "type": "integer"
                            },
                            "an_amr": {
                                "type": "integer"
                            },
                            "an_female": {
                                "type": "integer"
                            },
                            "an_oth_male": {
                                "type": "integer"
                            },
                            "an_eas_female": {
                                "type": "integer"
                            },
                            "an_afr_female": {
                                "type": "integer"
                            },
                            "an_afr": {
                                "type": "integer"
                            },
                            "an_oth": {
                                "type": "integer"
                            },
                            "an_popmax": {
                                "type": "integer"
                            },
                            "an_male": {
                                "type": "integer"
                            },
                            "an_nfe_male": {
                                "type": "integer"
                            },
                            "an_fin_male": {
                                "type": "integer"
                            },
                            "an_asj_female": {
                                "type": "integer"
                            },
                            "an_eas": {
                                "type": "integer"
                            }
                        }
                    },
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alleles": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "pos": {
                        "type": "integer"
                    },
                    "baseqranksum": {
                        "type": "float"
                    },
                    "vqsr_culprit": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "hom": {
                        "properties": {
                            "hom_fin": {
                                "type": "integer"
                            },
                            "hom_raw": {
                                "type": "integer"
                            },
                            "hom_eas": {
                                "type": "integer"
                            },
                            "hom": {
                                "type": "integer"
                            },
                            "hom_nfe": {
                                "type": "integer"
                            },
                            "hom_afr": {
                                "type": "integer"
                            },
                            "hom_male": {
                                "type": "integer"
                            },
                            "hom_female": {
                                "type": "integer"
                            },
                            "hom_asj": {
                                "type": "integer"
                            },
                            "hom_oth": {
                                "type": "integer"
                            },
                            "hom_amr": {
                                "type": "integer"
                            }
                        }
                    },
                    "inbreedingcoeff": {
                        "type": "float"
                    }
                }
            }
        }
        return mapping

