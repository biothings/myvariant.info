import os, sys, time, datetime
import bs4

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper
from biothings.utils.common import unzipall


class CivicDumper(HTTPDumper):

    SRC_NAME = "civic"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    API_PAGE = 'https://civic.genome.wustl.edu/api/variants/'
    SCHEDULE = "0 22 1 * *"
    IGNORE_HTTP_CODE = [404] # some variants are 
    MAX_PARALLEL_DUMP = 1
    SLEEP_BETWEEN_DOWNLOAD = 1.0

    def set_release(self):
        self.release = datetime.date.today().strftime("%Y-%m-%d")

    def create_todump_list(self, force=False):
        self.set_release() # so we can generate new_data_folder
        # first check total number of variants. It's not continuous, so it's not
        # because total_count = 2088 that the last variant is 2088, some have been deleted
        # or at least give 404. Any 404 adds to the end...
        ids = []
        self.logger.info("Find all available variant IDS")
        total_pages = self.client.get(self.API_PAGE + "?count=100").json()["_meta"]["total_pages"]
        for p in range(1,total_pages+1):
            self.logger.debug("Analyzing page %s/%s" % (p,total_pages))
            doc = self.client.get(self.API_PAGE + "?count=100&page=%s" % p).json()
            for rec in doc["records"]:
                ids.append(rec["id"])
        self.logger.info("Now generate download URLs")
        for i in ids:
            remote_file = self.API_PAGE + str(i)
            local_file = os.path.join(self.new_data_folder,"variant_%s.json" % i)
            self.to_dump.append({"remote":remote_file,"local":local_file})
