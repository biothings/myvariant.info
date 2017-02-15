import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import ManualDumper
from biothings.utils.common import untargzall


class EVSDumper(ManualDumper):

    SRC_NAME = "evs"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(EVSDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: http://evs.gs.washington.edu/EVS/
- ESP6500SI-V2-SSA137.GRCh38-liftover.chr*
""")

    def post_dump(self):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        untargzall(self.new_data_folder)


def main(data_folder):
    dumper = EVSDumper()
    dumper.dump(data_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Specify a directory where data file was downloaded")
        sys.exit(255)
    main(sys.argv[1])
