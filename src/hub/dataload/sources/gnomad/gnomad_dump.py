import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import ManualDumper
from biothings.utils.common import gunzipall


class GnomadDumper(ManualDumper):

    SRC_NAME = "gnomad"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(GnomadDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: http://gnomad.broadinstitute.org/downloads
Under version directory, there should be 2 sub-directories, containing VCF and .tbi files:
- exomes/
- genomes/
""")

    def post_dump(self, *args, **kwargs):
        genomes_dir = os.path.join(self.new_data_folder,"genomes")
        self.logger.info("Unzipping files in '%s'" % genomes_dir) 
        gunzipall(genomes_dir)
        self.logger.info("Unzipping files in '%s'" % exomes_dir) 
        exomes_dir = os.path.join(self.new_data_folder,"exomes")
        gunzipall(exomes_dir)

