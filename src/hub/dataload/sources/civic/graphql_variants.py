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
                }
                edges {
                    cursor
                        node {
                            ...BrowseVariantsFields
                        }
                }
                totalCount
                filteredCount
                pageCount
                lastUpdated
            }
        }

        fragment BrowseVariantsFields on BrowseVariant {
            id
            name
        }
    """

    def gql(self, after: str):
        query = {
            "operationName": self.OPERATION_NAME,
            "query": self.QUERY,
            "variables": {"after": after},
        }
        return query

    def fetch(self, after: str, api_url: str):
        try:
            response = requests.post(
                api_url,
                json=self.gql(after=after)
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error in {self.OPERATION_NAME}: {e}")
            raise
