import os
import os.path
import sys, re
import time
from datetime import datetime

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT, logger as logging
from biothings.dataload.dumper import FTPDumper

class DBSNPDumper(FTPDumper):
    SRC_NAME = "dbsnp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
    CWD_DIR = '/snp/organisms'
    DATADIR_RE_PATTERN = '''human_9606_(.\d+)_GRCh\d\dp\d+'''
    FILE_RE = 'All_\d{8}.vcf.gz'

    SCHEDULE = "0 9 * * *"

    def find_latest_human_dirs(self):
        # list all orgs
        orgs = self.client.nlst()
        humans = {}
        for org in orgs:
            m = re.match(self.DATADIR_RE_PATTERN,org)
            if m:
                humans.setdefault(m.groups()[0],[]).append(org)
        # get latest
        self.release = sorted(humans)[-1]
        latest_human_dirs = humans[self.release]
        return latest_human_dirs

    def create_todump_list(self, force=False):
        latest_remote_dirs = self.find_latest_human_dirs()
        pat = re.compile(".*" + self.FILE_RE + "$")
        for one_dir in latest_remote_dirs:
            filenames = [fn for fn in self.client.nlst(one_dir + "/VCF") if pat.match(fn)]
            self.logger.info(filenames + [fn + ".tbi" for fn in filenames])
            for filename in filenames + [fn + ".tbi" for fn in filenames]:
                new_localfile = os.path.join(self.new_data_folder,filename)
                try:
                    current_localfile = os.path.join(self.current_data_folder,filename)
                except TypeError:
                    # current data folder doesn't even exist
                    current_localfile = new_localfile
                if force or not os.path.exists(current_localfile) or self.remote_is_better(filename, current_localfile):
                    self.to_dump.append({"remote":filename, "local":new_localfile})

def main():
    dumper = DBSNPDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
