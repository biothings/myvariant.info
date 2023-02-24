import os
import os.path
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
    """
    Mixed dumper (use FTP and HTTP/GoogleDrive) to dump dbNSFP:
    - FTP: to get the latest version
    - HTTP: to actually get the data (because their FTP server is sooo slow)
    """

    SRC_NAME = "dbnsfp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SCHEDULE = "0 9 1 * *"  # 9AM every 1st day of month

    # Look for filenames ending with "a" (for Academic), not "c" (for Commercial).
    #   Also, sometimes there's a "v", sometimes not...
    FILENAME_PATTERN = re.compile("dbNSFPv?(\d+\..*\d+a)\.zip")
    # Check if a release is a beta release.
    # Tricky there, usually releases are like 4.0a, 4.0b1a, 4.0b2a.
    #   If sorted, 4.0b2a will be the "newest", but it's a beta (b2) and 4.0a is actually the newest there
    BETA_RELEASE_PATTERN = re.compile("(\d+\.\d+)\w\d(\w)")

    def get_newest_info(self):
        release_map = dict()  # a dict of <release_num, file_name>

        ftp = FTP('dbnsfp.softgenetics.com')
        ftp.login('dbnsfp', 'dbnsfp')
        for filename in ftp.nlst():
            filename_match = self.FILENAME_PATTERN.match(filename)
            if filename_match:
                release = filename_match.groups()[0]
                release_map[release] = filename

        newest_release = sorted(release_map.keys())[-1]

        beta_release_match = self.BETA_RELEASE_PATTERN.match(newest_release)
        if beta_release_match:
            # If the newest release is a beta release, infer its stable release
            stable_release = "".join(beta_release_match.groups())

            # If the inferred stable release is available, use it instead of the beta release
            if stable_release in release_map:
                self.logger.info("Found non-beta release '%s'" % stable_release)
                newest_release = stable_release
            # Otherwise just use the beta release
            # else:
            #     pass

        # get the last item in the list, which is the latest version
        self.release = newest_release
        self.newest_file = release_map[newest_release]

    def new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info("New release '%s' found" % self.release)
            return True
        else:
            self.logger.debug("No new release found")
            return False

    def get_drive_url(self, filename):
        # ok, so let's get the main page data. in this page there are links for both
        # FTP and Google Drive. We're assuming here that just after FTP link, there's
        # the corresponding one for Drive (parse will ensure we downloaded the correct
        # version, and also the correct licensed one - academic only)
        res = requests.get("https://sites.google.com/site/jpopgen/dbNSFP")
        html = BeautifulSoup(res.text, "html.parser")
        ftplink = html.findAll(attrs={"href": re.compile(filename)})
        if ftplink:
            ftplink = ftplink.pop()
        else:
            raise DumperException("Can't find a FTP link for '%s'" % filename)
        # let's cross fingers here...
        drivelink = ftplink.findNextSibling()
        href = drivelink.get("href")
        if href:
            return href
        else:
            raise DumperException("Can't find a href in drive link element: %s" % drivelink)

    def create_todump_list(self, force=False):
        self.get_newest_info()
        new_localfile = os.path.join(self.new_data_folder, os.path.basename(self.newest_file))
        try:
            current_localfile = os.path.join(self.current_data_folder, os.path.basename(self.newest_file))
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = new_localfile
        if force or not os.path.exists(current_localfile) or self.new_release_available():
            # register new release (will be stored in backend)
            self.release = self.release
            remote = self.get_drive_url(self.newest_file)
            self.to_dump.append({"remote": remote, "local": new_localfile})

    def post_download(self, remote, local):
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
