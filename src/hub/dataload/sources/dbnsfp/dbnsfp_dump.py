import hashlib
import os
import time
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

    # The full academic archive is ~45GiB; connections to it are prone to breaking
    # mid-transfer (seen in practice: ChunkedEncodingError/IncompleteRead partway
    # through). The source (Cloudflare-fronted) advertises "Accept-Ranges: bytes",
    # so on failure we resume from the last byte written instead of restarting.
    # dbNSFP's own download instructions suggest "curl --http1.1 -C -" for this;
    # "-C -" (resume from the local file's size) is what this override does, and
    # "--http1.1" is moot here since plain requests/urllib3 has no HTTP/2 support
    # to begin with (confirmed: a real request to the source negotiates HTTP/1.1).
    MAX_DOWNLOAD_ATTEMPTS = 5
    RETRY_WAIT_SECONDS = 15

    def download(self, remoteurl, localfile, headers=None):
        """
        Like HTTPDumper.download(), but retries on a broken connection by
        resuming from the last successfully-written byte (HTTP Range), instead
        of restarting the whole ~45GiB transfer from scratch.
        """
        self.prepare_local_folders(localfile)
        base_headers = dict(headers or {})

        last_exception = None
        for attempt in range(1, self.MAX_DOWNLOAD_ATTEMPTS + 1):
            resume_from = os.path.getsize(localfile) if os.path.exists(localfile) else 0
            attempt_headers = dict(base_headers)
            mode = "wb"
            if resume_from:
                attempt_headers["Range"] = f"bytes={resume_from}-"
                mode = "ab"

            try:
                res = self.client.get(remoteurl, stream=True, headers=attempt_headers, timeout=(30, 120))

                if resume_from and res.status_code == 416:
                    # Range not satisfiable: the file already on disk is already complete.
                    self.logger.info(f"{localfile} is already fully downloaded ({resume_from} bytes); skipping.")
                    return res
                if resume_from and res.status_code == 200:
                    # Server ignored our Range request; restart clean rather than risk corrupting the file.
                    self.logger.warning(f"Server ignored Range request for {remoteurl}; restarting download from scratch.")
                    mode = "wb"
                elif res.status_code not in (200, 206):
                    if res.status_code in self.__class__.IGNORE_HTTP_CODE:
                        self.logger.info("Remote URL %s gave http code %s, ignored" % (remoteurl, res.status_code))
                        return res
                    raise DumperException(
                        "Error while downloading '%s' (status: %s, reason: %s)" % (remoteurl, res.status_code, res.reason)
                    )

                self.logger.debug(f"Downloading '{remoteurl}' as '{localfile}' (attempt {attempt}, resuming from byte {resume_from})")
                with open(localfile, mode) as fout:
                    for chunk in res.iter_content(chunk_size=512 * 1024):
                        if chunk:
                            fout.write(chunk)
                return res
            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_exception = e
                downloaded = os.path.getsize(localfile) if os.path.exists(localfile) else 0
                if attempt < self.MAX_DOWNLOAD_ATTEMPTS:
                    self.logger.warning(
                        f"Download of {remoteurl} broke after {downloaded} bytes on attempt {attempt}/"
                        f"{self.MAX_DOWNLOAD_ATTEMPTS} ({e}); will resume from there in {self.RETRY_WAIT_SECONDS}s."
                    )
                    time.sleep(self.RETRY_WAIT_SECONDS)
                else:
                    self.logger.error(f"Download of {remoteurl} failed after {self.MAX_DOWNLOAD_ATTEMPTS} attempts ({e}).")

        raise DumperException(
            f"Failed to download {remoteurl} after {self.MAX_DOWNLOAD_ATTEMPTS} attempts."
        ) from last_exception

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
