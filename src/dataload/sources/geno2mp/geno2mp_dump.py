import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import ManualDumper
from biothings.utils.common import gunzipall


class Geno2MPDumper(ManualDumper):

    SRC_NAME = "geno2mp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(Geno2MPDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: http://geno2mp.gs.washington.edu/Geno2MP
- Geno2MP.variants.vcf.gz
""")

    def post_dump(self):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        gunzipall(self.new_data_folder)


def main(data_folder):
    dumper = Geno2MPDumper()
    dumper.dump(data_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Specify a directory where data file was downloaded")
        sys.exit(255)
    main(sys.argv[1])

