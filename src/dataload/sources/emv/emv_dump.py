import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import ManualDumper


class EMVDumper(ManualDumper):

    SRC_NAME = "emv"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(EMVDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: http://geneticslab.emory.edu/emvclass/emvclass.php
- EmVClass.*.csv
""")


def main(data_folder):
    dumper = EMVDumper()
    dumper.dump(data_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Specify a directory where data file was downloaded")
    main(sys.argv[1])
