import os
import os.path
import sys, re
import time

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.dataload.dumper import FTPDumper
from biothings.utils.common import gunzipall


class ExacDumper(FTPDumper):

    SRC_NAME = "exac"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    FTP_HOST = 'ftp.broadinstitute.org'
    CWD_DIR = 'pub/ExAC_release'
    FILE_PATTERN = ".*ExAC.r%s\.sites.*\.vcf\.gz$" # need release number

    SCHEDULE = None # version is forced so no need to schedule that one anyway

    def get_newest_info(self):
        # there's a "current" symlink to latest, but we want to detect new releases
        # so we need to parse directory names
        releases = self.client.nlst()
        # get rid of files
        releases = [x for x in releases if x.startswith('release0')]
        # sort items based on k
        releases = sorted(releases)
        latest_release_dir = releases[-1]
        self.release = latest_release_dir.replace("release","")
        contents = self.client.nlst(latest_release_dir)
        pat = re.compile(self.__class__.FILE_PATTERN % self.release)
        self.newest_file = [f for f in contents if pat.match(f)][-1]

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
            self.release = self.release
            self.to_dump.append({"remote": self.newest_file,"local":new_localfile})
            # also download nonTCGA
            subdir = "release%s/subsets/" % self.release
            # split: b/c newest_file includes releaseX.Y.Z directory
            nontcga = re.sub("^ExAC\.","ExAC_nonTCGA.",self.newest_file.split("/")[-1])
            local_nontcga = os.path.join(self.new_data_folder,nontcga)
            self.to_dump.append({"remote": os.path.join(subdir,nontcga), "local":local_nontcga})

    def post_dump(self):
        self.logger.info("Uncompressing files in '%s'" % self.new_data_folder) 
        gunzipall(self.new_data_folder)


def main():
    dumper = ExacDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
