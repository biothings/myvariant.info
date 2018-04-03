import biothings.hub.dataload.uploader as uploader
from hub.dataload.uploader import SnpeffPostUpdateUploader

class DOCMUploader(uploader.DummySourceUploader,SnpeffPostUpdateUploader):
    """Originally downloaded from: http://docm.genome.wustl.edu/"""

    name = "docm"
    __metadata__ = {"mapper" : 'observed',
                    "assembly" : "hg19"}

    @classmethod
    def get_mapping(klass):
        mapping = {
            "docm": {
                "properties": {
                    "domain": {
                        "type": "text"
                    },
                    "all_domains": {
                        "type": "text"
                    },
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "primary": {
                        "type": "byte"           # just 0 or 1
                    },
                    "transcript_species": {
                        "type": "text",
                        "index" : False
                    },
                    "ensembl_gene_id": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "transcript_version": {
                        "type": "text",
                        "index" : False
                    },
                    "transcript_source": {
                        "type": "text",
                        "index" : False
                    },
                    "source": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "pubmed_id": {
                        # not_analyzed
                        "type":"keyword",
                    },
                    "type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "doid": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "c_position": {
                        "type": "text",
                        "analyzer": "string_lowercase"
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
                    "strand": {
                        "type": "byte",
                        "index" : False
                    },
                    "deletion_substructures": {
                        "type": "text",
                        "index" : False
                    },
                    "genename_source": {
                        "type": "text",
                        "index" : False
                    },
                    "default_gene_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "aa_change": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "url": {
                        "type": "text",
                        "index" : False
                    },
                    "transcript_status": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "trv_type": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "disease": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "transcript_name": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "chrom": {
                        "type": "text",                 # actual value is integer
                        "analyzer": "string_lowercase"
                    },
                    "transcript_error": {
                        "type": "text",
                        "index" : False
                    },
                    "genename": {
                        "type": "text",
                        "analyzer": "string_lowercase",
                        "copy_to" : ["all"]
                    },
                    "ucsc_cons": {
                        "type": "double"
                    }
                }
            }
        }
        return mapping

