import os
import os.path
import sys
import time
import re
import requests
from ftplib import FTP
from bs4 import BeautifulSoup
import zipfile

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import GoogleDriveDumper, DumperException
from biothings.utils.common import unzipall


class DBNSFPDumper(GoogleDriveDumper):
    '''
    Mixed dumper (use FTP and HTTP/GoogleDrive) to dump dbNSFP:
    - FTP: to get the latest version
    - HTTP: to actually get the data (because their FTP server is sooo slow)
    '''

    SRC_NAME = "dbnsfp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    RELEASE_PAT = "dbNSFPv(\d+\.\d+a)\.zip" # "a" is for academic, not "c"ommercial

    SCHEDULE = "0 9 * * *"

    def get_newest_info(self):
        ftp = FTP('dbnsfp.softgenetics.com')
        ftp.login('dbnsfp','dbnsfp')
        releases = ftp.nlst()
        # get rid of readme files
        pat = re.compile(self.RELEASE_PAT)
        releases = [x for x in releases if pat.match(x)]
        # sort items based on date
        releases = sorted(releases)
        # get the last item in the list, which is the latest version
        self.newest_file = releases[-1]
        self.release = pat.match(releases[-1]).groups()[0]

    def new_release_available(self):
        current_release = self.src_doc.get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def get_drive_url(self,ftpname):
        # ok, so let's get the main page data. in this page there are links for both
        # FTP and Google Drive. We're assuming here that just after FTP link, there's
        # the corresponding one for Drive (parse will ensure we downloaded the correct
        # version, and also the correct licensed one - academic only)
        res = requests.get("https://sites.google.com/site/jpopgen/dbNSFP")
        html = BeautifulSoup(res.text,"html.parser")
        ftplink = html.findAll(attrs={"href":re.compile(ftpname)})
        if ftplink:
            ftplink = ftplink.pop()
        else:
            raise DumperException("Can't find a FTP link for '%s'" % ftpname)
        # let's cross fingers here...
        drivelink = ftplink.findNextSibling()
        href = drivelink.get("href")
        if href:
            return href
        else:
            raise DumperException("Can't find a href in drive link element: %s" % drivelink)


    def create_todump_list(self, force=False):
        self.get_newest_info()
        new_localfile = os.path.join(self.new_data_folder,os.path.basename(self.newest_file))
        try:
            current_localfile = os.path.join(self.current_data_folder,os.path.basename(self.newest_file))
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = new_localfile
        if force or not os.path.exists(current_localfile) or self.new_release_available():
            # register new release (will be stored in backend)
            self.release = self.release
            remote = self.get_drive_url(self.newest_file)
            self.to_dump.append({"remote": remote,"local":new_localfile})

    def post_download(self,remote,local):
        filename = os.path.basename(local)
        if not self.release in filename:
            raise DumperException("Weird, filename is wrong ('%s')" % filename)
        # make sure we downloaded to correct one, and that it's the academic version
        zf = zipfile.ZipFile(local)
        readme = None
        for f in zf.filelist:
            if "readme" in f.filename:
                readme = f
                break
        if not readme:
            raise DumperException("Can't find a readme in the archive (I was checking version/license)")
        if not self.release in readme.filename:
            raise DumperException("Version in readme filename ('%s') doesn't match expected version %s" % (readme.filename, self.release))
        assert self.release.endswith("a"), "Release '%s' isn't academic version (how possible ?)" % self.release
        # good to go...

    def post_dump(self, *args, **kwargs):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder)
        unzipall(self.new_data_folder)


def main():
    dumper = DBNSFPDumper()
    dumper.dump()

if __name__ == "__main__":
    main()
