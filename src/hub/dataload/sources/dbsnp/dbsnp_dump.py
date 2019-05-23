import os
import os.path
import sys, re
import time
from datetime import datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.hub.dataload.dumper import FTPDumper

class DBSNPDumper(FTPDumper):
    SRC_NAME = "dbsnp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
    CWD_DIR = '/snp/latest_release/JSON'
    VERSIONS_DIR = '/snp/archive'
    FILE_RE = 'refsnp-chr*.json.bz2'
    MAX_PARALLEL_DUMP = 10

    SCHEDULE = "0 9 * * *"

    def set_release(self):
        try:
            self.client.cwd(self.__class__.VERSIONS_DIR)
            versions = self.client.nlst()
            # get latest
            self.release = sorted(versions)[-1].replace("b","")
        finally:
            self.client.cwd(self.__class__.CWD_DIR)


    def create_todump_list(self, force=False):
        self.set_release()
        filenames = [fn for fn in self.client.nlst(self.__class__.FILE_RE)]
        assert len(filenames) == 25, "Expected 25 files, got %s" % len(filenames)
        for filename in filenames:
            new_localfile = os.path.join(self.new_data_folder,filename)
            try:
                current_localfile = os.path.join(self.current_data_folder,filename)
            except TypeError:
                # current data folder doesn't even exist
                current_localfile = new_localfile
            if force or not os.path.exists(current_localfile) or self.remote_is_better(filename, current_localfile):
                self.to_dump.append({"remote":filename, "local":new_localfile})

