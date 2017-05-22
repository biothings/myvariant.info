import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import ManualDumper
from biothings.utils.common import unzipall


class SnpeffDumper(ManualDumper):

    SRC_NAME = "snpeff"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(SnpeffDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download of Snpeff tools ,from: https://sourceforge.net/projects/snpeff/files/
- snpEff_latest_core.zip
""")

    def post_dump(self):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        unzipall(self.new_data_folder)


def main(data_folder):
    dumper = SnpeffDumper()
    dumper.dump(data_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Specify a directory where data file was downloaded")
        sys.exit(255)
    main(sys.argv[1])
