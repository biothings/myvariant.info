import os
import os.path
import sys
import time
import requests

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import LastModifiedHTTPDumper
from biothings.utils.common import unzipall

class CGIDumper(LastModifiedHTTPDumper):

    SRC_NAME = "cgi"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    # Datasource no longer maintained; shedule cancelled
    # SCHEDULE = "0 9 * * *"

    VERIFY_CERT = False
    # URL is always the same, but headers change
    SRC_URLS = ["https://www.cancergenomeinterpreter.org/data/biomarkers/cgi_biomarkers_latest.tsv"]
