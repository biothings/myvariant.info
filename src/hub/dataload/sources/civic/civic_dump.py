import os
import json
import logging
import datetime

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper

from hub.dataload.sources.civic.graphql_dump import GraphqlDump


class CivicDumper(HTTPDumper):

    SRC_NAME = "civic"
    API_URL = "https://civicdb.org/api/graphql"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    SCHEDULE = "0 22 1 * *"
    MAX_PARALLEL_DUMP = 5
    SLEEP_BETWEEN_DOWNLOAD = 0.1

    def set_release(self):
        self.release = datetime.date.today().strftime("%Y-%m-%d")

    def create_todump_list(self, force=False, **kwargs):

        self.logger.info("Find all available variant IDS")
        ids = GraphqlDump().get_variants_list(api_url=self.API_URL)

        self.logger.info("Now download files")
        for variant_id in ids:
            logging.info("### variant_id")
            logging.info(variant_id)

            if (
                force
                or not self.src_doc
                or not self.release
                or (
                    self.src_doc
                    and self.src_doc.get("download", {}).get("release") < self.release
                )
            ):
                data_url = variant_id
                file_name = f"variant_{str(variant_id)}.json"
                self.set_release()
                data_folder = os.path.join(self.SRC_ROOT_FOLDER, self.release)
                local = os.path.join(data_folder, file_name)
                logging.info(local)
                self.to_dump.append({"remote": data_url, "local": local})

    def download(self, remoteurl, localfile, headers={}):
        self.prepare_local_folders(localfile)
        variant_id = remoteurl

        self.logger.info(f"Downloading data for variant id: {variant_id}")
        variant_data = GraphqlDump().dump_variant(variant_id=variant_id, api_url=self.API_URL)

        with open(localfile, "w") as f:
            json.dump(variant_data, f)

        return variant_data


def __init__(self, *args, **kwargs):
    super(CivicDumper, self).__init__(*args, **kwargs)
    self.logger.info("Starting dump.")
    self.dump()
