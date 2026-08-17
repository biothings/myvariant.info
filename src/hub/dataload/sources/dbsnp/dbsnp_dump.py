import hashlib
import io
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
    CHECKSUMS_FILE = 'CHECKSUMS'
    MAX_PARALLEL_DUMP = 1   # reduced from 10 to 1 to prevent download timeout
    # these files are 1-38GB each and can take hours to download; NCBI's FTP server
    # can go quiet for several minutes at a time during such long transfers, and the
    # 10-minute default is aggressive enough to kill an otherwise-healthy download.
    # Since retrbinary() has no resume support, any timeout means restarting that
    # file from scratch, so it's worth tolerating longer stalls here.
    FTP_TIMEOUT = 30 * 60.0

    SCHEDULE = "0 9 * * *"

    def set_release(self):
        try:
            self.client.cwd(self.__class__.VERSIONS_DIR)
            versions = self.client.nlst()
            # get latest
            self.release = sorted(versions)[-1].replace("b","")
        finally:
            self.client.cwd(self.__class__.CWD_DIR)

    def _fetch_checksums(self):
        """Fetch and parse the remote CHECKSUMS file (md5sum-style lines:
        '<md5>  <filename>') so each download can be verified in post_download().
        Returns {} (skipping verification) if it can't be fetched, rather than
        failing the whole dump over a 1.7KB file."""
        buf = io.BytesIO()
        try:
            self.client.retrbinary("RETR %s" % self.__class__.CHECKSUMS_FILE, buf.write)
        except Exception as e:
            self.logger.warning("Couldn't fetch '%s', downloads won't be checksum-verified: %s" %
                                 (self.__class__.CHECKSUMS_FILE, e))
            return {}
        expected_md5s = {}
        for line in buf.getvalue().decode().splitlines():
            line = line.strip()
            if not line:
                continue
            md5sum, filename = line.split(None, 1)
            expected_md5s[filename] = md5sum
        return expected_md5s

    def create_todump_list(self, force=False):
        self.set_release()
        self._expected_md5s = self._fetch_checksums()
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

    def post_download(self, remotefile, localfile):
        expected_md5 = getattr(self, "_expected_md5s", {}).get(remotefile)
        if not expected_md5:
            # CHECKSUMS couldn't be fetched, or has no entry for this file
            return
        actual_md5 = hashlib.md5()
        with open(localfile, "rb") as f:
            for chunk in iter(lambda: f.read(64 * 1024 * 1024), b""):
                actual_md5.update(chunk)
        actual_md5 = actual_md5.hexdigest()
        if actual_md5 != expected_md5:
            os.remove(localfile)
            raise ValueError(
                "Checksum mismatch for '%s': expected %s, got %s (file removed, will retry on next run)" %
                (remotefile, expected_md5, actual_md5))
        self.logger.info("Checksum verified for '%s'" % remotefile)

