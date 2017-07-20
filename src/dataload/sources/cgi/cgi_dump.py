import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import ManualDumper
from biothings.utils.common import unzipall


class CGIDumper(ManualDumper):

    SRC_NAME = "cgi"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(CGIDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: https://www.cancergenomeinterpreter.org/biomarkers
""")

    def post_dump(self):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder) 
        unzipall(self.new_data_folder)

