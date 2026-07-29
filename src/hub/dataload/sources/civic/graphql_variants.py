from hub.dataload.sources.civic.graphql_client import post_graphql


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
        return post_graphql(
            api_url=api_url,
            payload=self.gql(after=after),
            operation_name=self.OPERATION_NAME,
        )
