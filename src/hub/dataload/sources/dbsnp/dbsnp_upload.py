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
                    "alleles": {
                        "properties": {
                            "freq": {
                                "properties": {
                                    "1000g": {
                                        "type": "float"
                                    },
                                    "alspac": {
                                        "type": "float"
                                    },
                                    "estonian": {
                                        "type": "float"
                                    },
                                    "exac": {
                                        "type": "float"
                                    },
                                    "gnomad": {
                                        "type": "float"
                                    },
                                    "gnomad_exomes": {
                                        "type": "float"
                                    },
                                    "goesp": {
                                        "type": "float"
                                    },
                                    "topmed": {
                                        "type": "float"
                                    },
                                    "twinsuk": {
                                        "type": "float"
                                    }
                                }
                            },
                            "allele": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "gene": {
                        "properties": {
                            "is_pseudo": {
                                "type": "boolean"
                            },
                            "rnas": {
                                "properties": {
                                    "refseq": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "so": {
                                        "properties": {
                                            "name": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "accession": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            }
                                        }
                                    },
                                    "protein_product": {
                                        "properties": {
                                            "refseq": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            }
                                        }
                                    },
                                    "codon_aligned_transcript_change": {
                                        "properties": {
                                            "seq_id": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "position": {
                                                "type": "integer"
                                            },
                                            "deleted_sequence": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            },
                                            "inserted_sequence": {
                                                "normalizer": "keyword_lowercase_normalizer",
                                                "type": "keyword"
                                            }
                                        }
                                    },
                                    "protein": {
                                        "properties": {
                                            "variant": {
                                                "properties": {
                                                    "spdi": {
                                                        "properties": {
                                                            "seq_id": {
                                                                "normalizer": "keyword_lowercase_normalizer",
                                                                "type": "keyword"
                                                            },
                                                            "position": {
                                                                "type": "integer"
                                                            },
                                                            "deleted_sequence": {
                                                                "normalizer": "keyword_lowercase_normalizer",
                                                                "type": "keyword"
                                                            },
                                                            "inserted_sequence": {
                                                                "normalizer": "keyword_lowercase_normalizer",
                                                                "type": "keyword"
                                                            }
                                                        }
                                                    }
                                                }
                                            },
                                            "sequence_ontology": {
                                                "properties": {
                                                    "name": {
                                                        "normalizer": "keyword_lowercase_normalizer",
                                                        "type": "keyword"
                                                    },
                                                    "accession": {
                                                        "normalizer": "keyword_lowercase_normalizer",
                                                        "type": "keyword"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "strand": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "geneid": {
                                "type": "integer"
                            },
                            "symbol": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                "copy_to": ["all"]
                            },
                            "so": {
                                "properties": {
                                    "name": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    },
                                    "accession": {
                                        "normalizer": "keyword_lowercase_normalizer",
                                        "type": "keyword"
                                    }
                                }
                            },
                            "name": {
                                "type": "text"
                            }
                        }
                    },
                    "hg19": {
                        "properties": {
                            "start": {
                                "type": "integer"
                            },
                            "end": {
                                "type": "integer"
                            }
                        }
                    },
                    "vartype": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "rsid": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": ["all"]
                    },
                    "dbsnp_build": {
                        "type": "integer"
                    },
                    "dbsnp_merges": {
                        "properties": {
                            "rsid": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword",
                                "copy_to": ["all"]
                            },
                            "date": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "rv": {
                                "type": "integer"
                            }
                        }
                    },
                    "citations": {
                        "type": "integer"
                    },
                    "chrom": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "ref": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "alt": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
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

