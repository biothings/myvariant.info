import os
import os.path
import sys
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import FTPDumper


class ClinvarDumper(FTPDumper):

    SRC_NAME = "clinvar"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.ncbi.nlm.nih.gov'
    CWD_DIR = '/pub/clinvar/xml'

    def get_newest_info(self):
        releases = self.client.nlst()
        # get rid of readme files
        releases = [x for x in releases if x.startswith('ClinVarFullRelease') and x.endswith('gz')]
        # sort items based on date
        releases = sorted(releases)
        # get the last item in the list, which is the latest version
        self.newest_file = releases[-1]
        self.release = releases[-1].split('.')[0].split('_')[1]

    def new_release_available(self):
        current_release = self.src_doc.get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
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
            self.to_dump.append({"remote": self.newest_file,"local":new_localfile})
            # schema
            xsd = "clinvar_public.xsd"
            localxsdfile = os.path.join(self.new_data_folder,xsd)
            self.to_dump.append({"remote": "../%s" % xsd, "local":localxsdfile})

def main():
    dumper = ClinvarDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
