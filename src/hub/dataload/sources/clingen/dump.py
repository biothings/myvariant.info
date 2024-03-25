import os
import os.path
import sys
import time
import requests
import subprocess

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import gunzipall

class ClingenDumper(LastModifiedHTTPDumper):

    SRC_NAME = "clingen"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # Datasource no longer maintained; shedule cancelled
    # SCHEDULE = "0 9 * * *"

    SRC_URLS = ["http://reg.genome.network/temp/mvi_ca.gz"]
    CHUNK_SIZE = 10000000 # number of lines


    def post_dump(self, *args, **kwargs):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder) 
        gunzipall(self.new_data_folder)
        input_file = os.path.join(self.new_data_folder,"mvi_ca")
        self.logger.info("Split file in chunks")
        subprocess.check_call(["split","-l","%s" % self.__class__.CHUNK_SIZE,input_file,"%s.split." % input_file])



