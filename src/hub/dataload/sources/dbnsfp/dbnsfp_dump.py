import os
import re
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import zipfile
import xml.etree.ElementTree as ET

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper, DumperException
from biothings.utils.common import unzipall


class DBNSFPDumper(HTTPDumper):
    """
    Mixed dumper (use FTP and HTTP) to dump dbNSFP:
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
        # Fetch the response from the endpoint
        response = requests.get("https://dbnsfp.s3.amazonaws.com/")
        response_content = response.content

        # Parse the XML response
        root = ET.fromstring(response_content)

        # Namespace for the XML
        namespace = {'ns': 'http://s3.amazonaws.com/doc/2006-03-01/'}

        # Look for filenames ending with "a" (for Academic), not "c" (for Commercial).
        #   Also, sometimes there's a "v", sometimes not...
        FILENAME_PATTERN = re.compile("dbNSFPv?(\d+\..*\d+a)\.zip")
        # Check if a release is a beta release.
        # Tricky there, usually releases are like 4.0a, 4.0b1a, 4.0b2a.
        #   If sorted, 4.0b2a will be the "newest", but it's a beta (b2) and 4.0a is actually the newest there
        BETA_RELEASE_PATTERN = re.compile("(\d+\.\d+)\w\d(\w)")

        release_map = dict()  # a dict of <release_num, file_name>

        # Iterate through each Contents element in the XML
        for contents in root.findall('ns:Contents', namespace):
            key = contents.find('ns:Key', namespace).text

            filename_match = self.FILENAME_PATTERN.match(key)
            if filename_match:
                release = filename_match.groups()[0]
                release_map[release] = key

                # get the last item in the list, which is the latest version
                newest_release = sorted(release_map.keys())[-1]

                beta_release_match = self.BETA_RELEASE_PATTERN.match(newest_release)
                if beta_release_match:
                    # If the newest release is a beta release, infer its stable release
                    stable_release = "".join(beta_release_match.groups())

                    # If the inferred stable release is available, use it instead of the beta release
                    if stable_release in release_map:
                        self.logger.info(f"Stable release {stable_release} detected; beta release {newest_release} discarded.")
                        newest_release = stable_release
                    # Otherwise just use the beta release
                    # else:
                    #     pass

                self.release = newest_release
                self.newest_file = release_map[newest_release]

    def new_release_available(self):
        current_release = self.src_doc.get("download", {}).get("release")
        if not current_release or self.release > current_release:
            self.logger.info(f"New release {self.release} available, over current release {current_release}.")
            return True
        else:
            self.logger.debug(f"No new release available over current release {current_release}.")
            return False

    @classmethod
    def get_box_url(cls, filename):
        """
        Given a filename, find its Box download link from parsing the index page.

        dbNSFP main page provides 3 types of downloads for each release, in the following order:
        1. Amazon AWS (somehow cannot access)
        2. Box (direct link, or wrapped in www.google.com/url?q=<Box_URL>)
        3. Google Drive (a download page, not direct link)

        However only the Amazon AWS download URL will contain the filename. E.g. "dbNSFP4.3a.zip" and
        "https://www.google.com/url?q=https%3A%2F%2Fdbnsfp.s3.amazonaws.com%2FdbNSFP4.3a.zip&amp;sa=D&amp;sntz=1&amp;usg=AOvVaw2jxs6oSlLKGuD0pfWzazXd".

        The algorithm here is:
        1. Find the Amazon AWS download URL containing the filename.
        2. Find the first Box download URL right after the above Amazon AWS URL.

        Note: The above algorithm may fail once the HTML structure of the main page changed.
        """

        amazon_anchor_text = "Amazon"
        box_anchor_text = "Box"
        # google_drive_anchor_text = "googledrive"
        # to find anchor elements containing text "Amazon", or "Box"
        anchor_text_pattern = re.compile(f"^{amazon_anchor_text}|{box_anchor_text}$")

        html_response = requests.get("https://sites.google.com/site/jpopgen/dbNSFP")
        html_text = html_response.text
        soup = BeautifulSoup(html_text, "html.parser")
        anchors = soup.find_all("a", href=True, text=anchor_text_pattern)

        amazon_anchor_index = None
        for index, anchor in enumerate(anchors):
            if filename in anchor["href"] and anchor.text == amazon_anchor_text:
                amazon_anchor_index = index

        if amazon_anchor_index is None:
            raise DumperException(f"Cannot find an {amazon_anchor_text} anchor element containing filename {filename}.")

        box_anchor = None
        for anchor in anchors[amazon_anchor_index:]:
            if anchor.text == box_anchor_text:
                box_anchor = anchor
                break

        if box_anchor is None:
            raise DumperException(f"Cannot find a {box_anchor_text} anchor element after the {amazon_anchor_text} anchor of "
                                  f"{anchors[amazon_anchor_index]['href']}.")

        box_url = box_anchor["href"]

        # The Box download URL might be a "www.google.com/url" URL wrapping the true Box URL. E.g.
        # "https://www.google.com/url?q=https%3A%2F%2Fusf.box.com%2Fshared%2Fstatic%2Fq1kufbnww5dy3fs2t1yp5ay0w93eufq7"
        box_url_parse_result = urlparse(box_url)
        if box_url_parse_result.netloc == "www.google.com":
            qs_result = parse_qs(box_url_parse_result.query)
            q = qs_result.get("q", None)
            if q is None:
                raise DumperException(f"Cannot find q in the query string of {box_url} for {filename}.")
            return q[0]  # The wrapped Box URL should be the only element in "q"
        elif box_url_parse_result.netloc.endswith("box.com"):  # direct Box.com download link
            return box_url
        else:
            raise DumperException(f"Cannot recognized the Box download URL {box_url} for {filename}.")

    def create_todump_list(self, force=False, **kwargs):
        self.get_newest_info()

        new_localfile = os.path.join(self.new_data_folder, os.path.basename(self.newest_file))
        try:
            current_localfile = os.path.join(self.current_data_folder, os.path.basename(self.newest_file))
        except TypeError:
            # current data folder doesn't even exist
            current_localfile = new_localfile

        if force or not os.path.exists(current_localfile) or self.new_release_available():
            remote = self.get_box_url(self.newest_file)
            self.to_dump.append({"remote": remote, "local": new_localfile})

    def post_download(self, remote, local):
        """
        Run some sanity checks after downloading
        """

        """
        Check #1: The filename of the downloaded archive must contain the release tag.
        """
        filename = os.path.basename(local)
        if self.release not in filename:
            raise DumperException(f"Weird, filename is wrong ({filename}); should contain release tag {self.release}.")

        """
        Check #2: The downloaded archive must contain a README whole filename must contain the release tag.
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
        Check #3: Must be a academic release. 
        """
        assert self.release.endswith("a"), f"Release {self.release} isn't academic version (how possible?)"

        # More checks go here...

    def post_dump(self, *args, **kwargs):
        self.logger.info("Unzipping files in '%s'" % self.new_data_folder)
        unzipall(self.new_data_folder)
