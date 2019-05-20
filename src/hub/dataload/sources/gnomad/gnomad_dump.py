import os
import os.path
import glob
import sys
import time
import asyncio

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import ManualDumper
from biothings.utils.common import aiogunzipall


class GnomadDumper(ManualDumper):

    SRC_NAME = "gnomad"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(GnomadDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: http://gnomad.broadinstitute.org/downloads
Under version directory, there should be 2 sub-directories, containing VCF and .tbi files:
- exomes/
- genomes/
""")

