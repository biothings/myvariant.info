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


class GraphqlDump():

    def get_variants_list(self, api_url: str):
        ids = []
        hasNextPage = True
        # previousPageEnd = None
        # loop through all the pages
        while hasNextPage:
            response_data = GraphqlVariants().fetch(api_url=api_url)
            print("### response_data")
            print(response_data)
            if "data" in response_data:
                for variant in response_data["data"]["browseVariants"]["edges"]:
                    ids.append(variant["node"]["id"])
                hasNextPage = response_data["data"]["browseVariants"]["pageInfo"][
                    "hasNextPage"
                ]
                hasNextPage = False  # TODO: Remove to get all pages
        return ids

    def dump_variant(self, api_url: str, variant_id: int):
        res_summary = GraphqlVariantSummary().fetch(
            api_url=api_url, variant_id=variant_id
        )
        res_detail = GraphqlVariantDetail().fetch(
            api_url=api_url, variant_id=variant_id
        )
        res_molecular_profiles = GraphqlMolecularProfiles().fetch(
            api_url=api_url, variant_id=variant_id
        )
        res_contributor_avatars = GraphqlContributorAvatars().fetch(
            api_url=api_url, variant_id=variant_id
        )
        res_gene_variant = GraphqlGeneVariant().fetch(
            api_url=api_url, variant_id=variant_id
        )

        variant_data = {}
        variant_data = self.merge_dicts(variant_data, res_molecular_profiles["data"])
        variant_data = self.merge_dicts(variant_data, res_contributor_avatars["data"])
        variant_data = self.merge_dicts(variant_data, res_gene_variant["data"]["variant"])
        variant_data = self.merge_dicts(variant_data, res_detail["data"]["variant"])
        variant_data = self.merge_dicts(variant_data, res_summary["data"]["variant"])

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
