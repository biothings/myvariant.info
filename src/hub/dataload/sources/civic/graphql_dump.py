import time

from hub.dataload.sources.civic.graphql_variants import GraphqlVariants
from hub.dataload.sources.civic.graphql_detail import GraphqlVariantDetail
from hub.dataload.sources.civic.graphql_contributor_avatars import (
    GraphqlContributorAvatars,
)
from hub.dataload.sources.civic.graphql_summary import GraphqlVariantSummary
from hub.dataload.sources.civic.graphql_gene import GraphqlGeneVariant


class GraphqlDump():

    def get_variants_list(self, api_url: str):
        ids = []
        hasNextPage = True
        end_cursor = None
        while hasNextPage:
            response_data = GraphqlVariants().fetch(after=end_cursor, api_url=api_url)
            if "data" in response_data:
                for variant in response_data["data"]["browseVariants"]["edges"]:
                    ids.append(variant["node"]["id"])
                hasNextPage = response_data["data"]["browseVariants"]["pageInfo"]["hasNextPage"]
                end_cursor = response_data["data"]["browseVariants"]['pageInfo']['endCursor']
            print(f"INFO:dump_civic:Count variant IDs = {len(ids)}")
            time.sleep(1)
        return ids

    def dump_variant(self, api_url: str, variant_id: int):
        res_summary = GraphqlVariantSummary().fetch(
            api_url=api_url, variant_id=variant_id
        )
        res_detail = GraphqlVariantDetail().fetch(
            api_url=api_url, variant_id=variant_id
        )
        res_contributor_avatars = GraphqlContributorAvatars().fetch(
            api_url=api_url, variant_id=variant_id
        )
        res_gene_variant = GraphqlGeneVariant().fetch(
            api_url=api_url, variant_id=variant_id
        )

        variant_data = {
            "VariantSummary": res_summary,
            "VariantDetail": res_detail,
            "ContributorAvatars": res_contributor_avatars,
            "GeneVariant": res_gene_variant
        }

        return variant_data
