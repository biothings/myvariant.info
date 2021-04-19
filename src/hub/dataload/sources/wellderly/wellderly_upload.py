import os
import glob
from biothings.hub.dataload.uploader import ParallelizedSourceUploader
from hub.dataload.uploader import SnpeffPostUpdateUploader
from .wellderly_parser import WellderlyTsvReader


class WellderlyUploader(ParallelizedSourceUploader, SnpeffPostUpdateUploader):
    """Data originally coming from: http://www.stsiweb.org/wellderly"""

    name = "wellderly"

    __metadata__ = {
        "mapper": 'observed',
        "assembly": "hg19",
        "src_meta": {
            "url": "https://www.scripps.edu/science-and-medicine/translational-institute/translational-research/genomic-medicine/wellderly",
            "license_url": "https://redcapstsi.scripps.edu/redcap/surveys/?s=NT4N7A3KJD",
            "license_url_short": "https://bit.ly/32tpCvP"
        }
    }

    def jobs(self):
        """
        this method will be called by self.update_data() and then generate arguments for self.load.data() method,
        allowing parallelization
        """
        tsv_filename_pattern = "Wellderly.chr*.g.vcf.gz.tsv"
        tsv_file_collection = glob.glob(os.path.join(self.data_folder, tsv_filename_pattern))

        assembly = self.__metadata__["assembly"]

        return [(tsv_file, assembly) for tsv_file in tsv_file_collection]

    def load_data(self, file, assembly):
        """load data from an input file"""
        self.logger.info("Load data from file {} (assembly: {})".format(file, assembly))

        return WellderlyTsvReader.load_data(file, assembly)

    @classmethod
    def get_mapping(klass):
        mapping = {
            "wellderly": {
                "properties": {
                    "chrom": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "pos": {
                        "type": "long"
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
                    "ref": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alt": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "vartype": {
                        "type": "text",
                        "analyzer": "string_lowercase"
                    },
                    "alleles": {
                        "properties": {
                            "allele": {
                                "type": "text",
                                "analyzer": "string_lowercase"
                            },
                            "freq": {
                                "type": "float"
                            }
                        }
                    }
                }
            }
        }
        return mapping
