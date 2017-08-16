import os
import os.path
import sys
import time
import requests

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import unzipall

class CGIDumper(LastModifiedHTTPDumper):

    SRC_NAME = "cgi"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SCHEDULE = "0 9 * * *"
    # URL is always the same, but headers change
    SRC_URLS = ["https://www.cancergenomeinterpreter.org/data/cgi_biomarkers_latest.zip"]

    def prepare_client(self):
        self.client = requests.Session()
        self.client.verify = False

    def post_dump(self):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder) 
        unzipall(self.new_data_folder)

