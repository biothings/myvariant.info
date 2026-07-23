import hashlib
import os
import zipfile

import requests

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper, DumperException
from biothings.utils.common import unzipall

try:
    from config import DBNSFP_RELEASE, DBNSFP_DOWNLOAD_URL
except ImportError:
    DBNSFP_RELEASE = None
    DBNSFP_DOWNLOAD_URL = None


class DBNSFPDumper(HTTPDumper):
    """
    Dumper for dbNSFP.

    dbNSFP moved to a registration-gated download model starting with the 5.x
    series (see https://www.dbnsfp.org/download): a human must submit an
    institutional email via a Google Form to get an access code, then submit
    a second Google Form (email + access code) to receive a release-specific
    download link by email. There is no API and no predictable URL pattern
    for this, so - unlike the old S3-bucket-listing + Box-link-scraping flow
    this dumper used through 4.9a (dbnsfp.s3.amazonaws.com no longer exists;
    the scraped page, sites.google.com/site/jpopgen/dbNSFP, is now explicitly
    the "legacy" 1.x-4.x site and has no 5.x releases) - the release version
    and download URL can no longer be auto-discovered.

    They must be set in config.py (gitignored, not committed - the URL is
    tied to a specific request) as DBNSFP_RELEASE and DBNSFP_DOWNLOAD_URL,
    refreshed by hand each time a new dbNSFP release is obtained via the two
    forms above.
    """

    SRC_NAME = "dbnsfp"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    SCHEDULE = "0 9 1 * *"  # 9AM every 1st day of month; no-ops until DBNSFP_RELEASE/DBNSFP_DOWNLOAD_URL are updated

    def create_todump_list(self, force=False, **kwargs):
        if not DBNSFP_RELEASE or not DBNSFP_DOWNLOAD_URL:
            raise DumperException(
                "DBNSFP_RELEASE and DBNSFP_DOWNLOAD_URL must be set in config.py. dbNSFP now requires a manual "
                "request for a release-specific download link: register at https://www.dbnsfp.org/download, then "
                "submit the 'Request download' form; there is no way to auto-discover them."
            )
        self.release = DBNSFP_RELEASE

        filename = os.path.basename(DBNSFP_DOWNLOAD_URL)
        new_localfile = os.path.join(self.new_data_folder, filename)
        try:
            current_localfile = os.path.join(self.current_data_folder, filename)
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = new_localfile

        if force or not os.path.exists(current_localfile) or self.new_release_available():
            self.to_dump.append({"remote": DBNSFP_DOWNLOAD_URL, "local": new_localfile})

    def new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info(f"New release {self.release} available, over current release {current_release}.")
            return True
        else:
            self.logger.debug(f"No new release available over current release {current_release}.")
            return False

    def post_download(self, remote, local):
        """
        Run some sanity checks after downloading
        """

        """
        Check #1: MD5 checksum, if the source publishes a "<file>.md5" next to the download URL.
        """
        md5_url = remote + ".md5"
        try:
            md5_response = requests.get(md5_url, timeout=30)
            md5_response.raise_for_status()
        except requests.RequestException as e:
            self.logger.warning(f"Could not fetch {md5_url} to verify checksum, skipping: {e}")
        else:
            expected_md5 = md5_response.text.split()[0].strip()
            with open(local, "rb") as f:
                actual_md5 = hashlib.md5(f.read()).hexdigest()
            if expected_md5 != actual_md5:
                raise DumperException(f"MD5 mismatch for {os.path.basename(local)}: expected {expected_md5}, got {actual_md5}.")

        """
        Check #2: The filename of the downloaded archive must contain the release tag.
        """
        filename = os.path.basename(local)
        if self.release not in filename:
            raise DumperException(f"Weird, filename is wrong ({filename}); should contain release tag {self.release}.")

        """
        Check #3: The downloaded archive must contain a README whole filename must contain the release tag.
        """
        zf = zipfile.ZipFile(local)
        readme = None
        for f in zf.filelist:
            if "readme" in f.filename:
                readme = f
                break
        if readme is None:
            raise DumperException(f"Can't find a README in the archive {local} (for the purpose of checking version/license).")
        if self.release not in readme.filename:
            raise DumperException(f"Version in readme filename ({readme.filename}) doesn't match release tag {self.release}.")

        """
        Check #4: Must be a academic release.
        """
        assert self.release.endswith("a"), f"Release {self.release} isn't academic version (how possible?)"

        # More checks go here...

    def post_dump(self, *args, **kwargs):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder)
        unzipall(self.new_data_folder)
