import os
import os.path
import subprocess
import sys
import time
import re

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import unzipall


class SnpeffDumper(LastModifiedHTTPDumper):

    SRC_NAME = "snpeff"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SRC_URLS = ["http://myvariant-ids.s3-website-us-west-2.amazonaws.com/hg19_genome.pyobj",
                "http://myvariant-ids.s3-website-us-west-2.amazonaws.com/hg38_genome.pyobj",
                #"https://sourceforge.net/projects/snpeff/files/snpEff_latest_core.zip",
                "https://sourceforge.net/projects/snpeff/files/snpEff_v4_3k_core.zip",
               ]

    def set_release(self):
        self.release = re.match(".*v(.*)_core.*",
                                self.__class__.SRC_URLS[-1].split("/")[-1]
                          ).groups()[0].replace("_",".")

    def post_dump(self, *args, **kwargs):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        unzipall(self.new_data_folder)
        prev = os.path.abspath(os.curdir)
        try:
            os.chdir(os.path.join(self.new_data_folder,"snpEff"))
            self.logger.info("Downloading snpeff databases")
            subprocess.check_output(["java","-jar","snpEff.jar","download","hg19"])
            subprocess.check_output(["java","-jar","snpEff.jar","download","hg38"])
        finally:
            os.chdir(prev)
















