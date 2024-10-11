import logging
import requests


class GraphqlVariants():

    OPERATION_NAME = "BrowseVariants"

    QUERY = """
        query BrowseVariants($variantName: String, $sortBy: VariantsSort, $first: Int, $last: Int, $before: String, $after: String) {
            browseVariants(
                variantName: $variantName
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
        }
    """

    def gql(self):
        query = {
            "operationName": self.OPERATION_NAME,
            "query": self.QUERY
        }
        return query

    def fetch(self, api_url: str):
        try:
            response = requests.post(
                api_url,
                json=self.gql()
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error in {self.OPERATION_NAME}: {e}")
            raise
