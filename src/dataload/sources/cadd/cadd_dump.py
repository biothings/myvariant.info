import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import ManualDumper


class CADDDumper(ManualDumper):

    SRC_NAME = "cadd"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(CADDDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: http://cadd.gs.washington.edu
of files (.tsv.gz and .tsv.gz.tbi) looking like:
- HumanExome-12v1-1_A_inclAn"no"
- 1000G_inclAn"no"
- ExAC.r0.2_inclAn"no
- ESP6500SI_inclAn"no"
""")

def main():
    dumper = CADDDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
