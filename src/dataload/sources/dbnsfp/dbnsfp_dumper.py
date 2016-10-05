import os
import os.path
import sys
import time
import re

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import FTPDumper


class DBNSFPDumper(FTPDumper):

    SRC_NAME = "dbnsfp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'dbnsfp.softgenetics.com'
    CWD_DIR = '/'
    FTP_USER = 'dbnsfp'
    FTP_PASSWD = 'dbnsfp'

    RELEASE_PAT = "dbNSFPv(\d+\.\d+a)\.zip" # "a" is for academic, not "c"ommercial

    def get_newest_info(self):
        releases = self.client.nlst()
        # get rid of readme files
        pat = re.compile(self.RELEASE_PAT)
        releases = [x for x in releases if pat.match(x)]
        # sort items based on date
        releases = sorted(releases)
        # get the last item in the list, which is the latest version
        self.newest_file = releases[-1]
        self.newest_release = pat.match(releases[-1]).groups()[0]

    def new_release_available(self):
        current_release = self.src_doc.get("release")
        if not current_release or self.newest_release > current_release:
            self.logger.info("New release '%s' found" % self.newest_release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def create_todump_list(self, force=False):
        self.get_newest_info()
        new_localfile = os.path.join(self.new_data_folder,os.path.basename(self.newest_file))
        try:
            current_localfile = os.path.join(self.current_data_folder,os.path.basename(self.newest_file))
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = new_localfile
        if force or not os.path.exists(current_localfile) or self.remote_is_better(self.newest_file,current_localfile) or self.new_release_available():
            # register new release (will be stored in backend)
            self.release = self.newest_release
            self.to_dump.append({"remote": self.newest_file,"local":new_localfile})

def main():
    dumper = DBNSFPDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
