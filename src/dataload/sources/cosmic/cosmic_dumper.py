import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import DummyDumper


class CosmicDumper(DummyDumper):
    SRC_NAME = "cosmic"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

def main():
    dumper = CosmicDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
