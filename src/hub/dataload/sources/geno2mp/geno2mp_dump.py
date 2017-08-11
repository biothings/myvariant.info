import os, sys, time, datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import gunzipall


class Geno2MPDumper(LastModifiedHTTPDumper):

    SRC_NAME = "geno2mp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # URL is always the same, but headers change
    SRC_URLS = ["http://geno2mp.gs.washington.edu/download/Geno2MP.variants.vcf.gz"]
    SCHEDULE = "0 9 * * *"

    def post_dump(self):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        gunzipall(self.new_data_folder)

