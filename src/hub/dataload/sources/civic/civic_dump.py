import os
import json
import logging
import datetime

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper

from hub.dataload.sources.civic.graphql_variants import GraphqlVariants
from hub.dataload.sources.civic.graphql_molecular_profiles import (
    GraphqlMolecularProfiles,
)
from hub.dataload.sources.civic.graphql_detail import GraphqlVariantDetail
from hub.dataload.sources.civic.graphql_contributor_avatars import (
    GraphqlContributorAvatars,
)
from hub.dataload.sources.civic.graphql_summary import GraphqlVariantSummary
from hub.dataload.sources.civic.graphql_gene import GraphqlGeneVariant


class CivicDumper(HTTPDumper):

    SRC_NAME = "civic"
    API_URL = "https://civicdb.org/api/graphql"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    # API_PAGE = 'https://civicdb.org/api/variants/'
    SCHEDULE = "0 22 1 * *"
    # IGNORE_HTTP_CODE = [404]
    # MAX_PARALLEL_DUMP = 1
    # SLEEP_BETWEEN_DOWNLOAD = 1.0

    def set_release(self):
        self.release = datetime.date.today().strftime("%Y-%m-%d")

    def create_todump_list(self, force=False, **kwargs):
        ids = []
        self.logger.info("Find all available variant IDS")

        hasNextPage = True
        # previousPageEnd = None
        # loop through all the pages
        while hasNextPage:
            response_data = GraphqlVariants().fetch(api_url=self.API_URL)
            print("### response_data")
            print(response_data)
            if "data" in response_data:
                for variant in response_data["data"]["browseVariants"]["edges"]:
                    ids.append(variant["node"]["id"])
                hasNextPage = response_data["data"]["browseVariants"]["pageInfo"][
                    "hasNextPage"
                ]
                hasNextPage = False  # TODO: Remove to get all pages
                # previousPageEnd = response_data['data']['browseVariants']['pageInfo']['endCursor']

        self.logger.info("Now download files")
        for variant_id in ids[:5]:  # TODO: Remove the top 5 [:5]
            logging.info("### variant_id")
            logging.info(variant_id)

            if (
                force
                or not self.src_doc
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

    def download(self, remoteurl, localfile, headers={}):  # noqa: B006
        self.prepare_local_folders(localfile)
        variant_id = remoteurl

        self.logger.debug("Downloading '%s' as '%s'" % (remoteurl, localfile))
        res_summary = GraphqlVariantSummary().fetch(
            api_url=self.API_URL, variant_id=variant_id
        )
        res_detail = GraphqlVariantDetail().fetch(
            api_url=self.API_URL, variant_id=variant_id
        )
        res_molecular_profiles = GraphqlMolecularProfiles().fetch(
            api_url=self.API_URL, variant_id=variant_id
        )
        res_contributor_avatars = GraphqlContributorAvatars().fetch(
            api_url=self.API_URL, variant_id=variant_id
        )
        res_gene_variant = GraphqlGeneVariant().fetch(
            api_url=self.API_URL, variant_id=variant_id
        )

        variant_data = self.merge_dicts(res_summary["data"]["variant"], res_detail["data"]["variant"])
        variant_data = self.merge_dicts(variant_data, res_molecular_profiles["data"])
        variant_data = self.merge_dicts(variant_data, res_contributor_avatars["data"])
        variant_data = self.merge_dicts(variant_data, res_gene_variant["data"])

        with open(localfile, "w") as f:
            json.dump(variant_data, f)

        return variant_data

    def merge_dicts(self, d1, d2):
        merged = d1.copy()
        for key, value in d2.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = self.merge_dicts(merged[key], value)
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key] = merged[key] + value  # Concatenate lists
                else:
                    merged[key] = value  # Overwrite value
            else:
                merged[key] = value
        return merged


def __init__(self, *args, **kwargs):
    super(CivicDumper, self).__init__(*args, **kwargs)
    self.logger.info("Starting dump.")
    self.dump()
