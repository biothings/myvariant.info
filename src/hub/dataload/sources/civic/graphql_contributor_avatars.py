from hub.dataload.sources.civic.graphql_client import post_graphql


class GraphqlContributorAvatars():

    OPERATION_NAME = "ContributorAvatars"

    QUERY = """
    query ContributorAvatars($subscribable: SubscribableInput!) {
        contributors(subscribable: $subscribable) {
            editors {
                ...ContributorFields
            }
            curators {
                ...ContributorFields
            }
        }
    }

    fragment ContributorFields on ContributingUser {
        user {
            id
            profileImagePath(size: 12)
        }
        uniqueActions {
            action
            count
        }
        lastActionDate
        totalActionCount
    }
    """

    def gql(self, variant_id: int):
        query = {
            "operationName": self.OPERATION_NAME,
            "query": self.QUERY,
            "variables": {
                "subscribable": {"id": variant_id, "entityType": "VARIANT"}
            }
        }
        return query

    def fetch(self, api_url: str, variant_id: int):
        return post_graphql(
            api_url=api_url,
            payload=self.gql(variant_id=variant_id),
            operation_name=self.OPERATION_NAME,
        )
