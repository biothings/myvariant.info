import logging
import requests


class GraphqlVariants():

    OPERATION_NAME = "BrowseVariants"

    QUERY = """
        query BrowseVariants($variantName: String, $featureName: String, $diseaseName: String, $therapyName: String, $variantAlias: String, $variantTypeId: Int, $variantGroupId: Int, $variantTypeName: String, $hasNoVariantType: Boolean, $variantCategory: VariantCategories, $sortBy: VariantsSort, $first: Int, $last: Int, $before: String, $after: String) {
        browseVariants(
            variantName: $variantName
            featureName: $featureName
            diseaseName: $diseaseName
            therapyName: $therapyName
            variantAlias: $variantAlias
            variantTypeId: $variantTypeId
            variantGroupId: $variantGroupId
            variantTypeName: $variantTypeName
            hasNoVariantType: $hasNoVariantType
            category: $variantCategory
            sortBy: $sortBy
            first: $first
            last: $last
            before: $before
            after: $after
        ) {
            pageInfo {
            endCursor
            hasNextPage
            startCursor
            hasPreviousPage
            __typename
            }
            edges {
            cursor
            node {
                ...BrowseVariantsFields
                __typename
            }
            __typename
            }
            totalCount
            filteredCount
            pageCount
            lastUpdated
            __typename
        }
        }

        fragment BrowseVariantsFields on BrowseVariant {
        id
        name
        link
        featureId
        featureName
        featureLink
        category
        featureDeprecated
        featureFlagged
        diseases {
            id
            name
            link
            deprecated
            __typename
        }
        therapies {
            id
            name
            link
            deprecated
            __typename
        }
        aliases {
            name
            __typename
        }
        variantTypes {
            id
            name
            link
            __typename
        }
        deprecated
        flagged
        __typename
        }
    """

    def gql(self):
        query = {
            "operationName": self.OPERATION_NAME,
            "query": self.QUERY
        }
        return query

    def fetch(self):
        try:
            response = requests.post(
                'https://civicdb.org/api/graphql',
                json=self.gql()
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error in {self.OPERATION_NAME}: {e}")
            raise
