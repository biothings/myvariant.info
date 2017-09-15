import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import ManualDumper
from biothings.utils.common import unzipall


class GraspDumper(ManualDumper):

    SRC_NAME = "grasp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(GraspDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: https://grasp.nhlbi.nih.gov/Updates.aspx
- GraspFullDataset*.zip
""")

    def post_dump(self, *args, **kwargs):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder) 
        unzipall(self.new_data_folder)


def main(data_folder):
    dumper = GraspDumper()
    dumper.dump(data_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Specify a directory where data file was downloaded")
    main(sys.argv[1])
