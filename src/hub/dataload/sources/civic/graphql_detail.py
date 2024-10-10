import logging
import requests


class GraphqlVariantDetail():

    OPERATION_NAME = "VariantDetail"

    QUERY = """
        query VariantDetail($variantId: Int!) {
        variant(id: $variantId) {
            ...VariantDetailFields
            __typename
        }
        }

        fragment VariantDetailFields on VariantInterface {
        id
        name
        deprecated
        deprecationReason
        deprecationActivity {
            parsedNote {
            ...parsedCommentFragment
            __typename
            }
            __typename
        }
        feature {
            id
            name
            link
            deprecated
            flagged
            __typename
        }
        variantAliases
        flags(state: OPEN) {
            totalCount
            __typename
        }
        openRevisionCount
        comments {
            totalCount
            __typename
        }
        __typename
        }

        fragment parsedCommentFragment on CommentBodySegment {
        __typename
        ... on CommentTagSegment {
            entityId
            displayName
            tagType
            link
            revisionSetId
            feature {
            id
            name
            link
            deprecated
            flagged
            __typename
            }
            __typename
        }
        ... on CommentTagSegmentFlagged {
            entityId
            displayName
            tagType
            flagged
            link
            revisionSetId
            feature {
            id
            name
            link
            deprecated
            flagged
            __typename
            }
            __typename
        }
        ... on CommentTagSegmentFlaggedAndWithStatus {
            entityId
            displayName
            tagType
            status
            flagged
            link
            revisionSetId
            feature {
            id
            name
            link
            deprecated
            flagged
            __typename
            }
            __typename
        }
        ... on CommentTagSegmentFlaggedAndDeprecated {
            entityId
            displayName
            tagType
            flagged
            deprecated
            link
            revisionSetId
            feature {
            id
            name
            link
            deprecated
            flagged
            __typename
            }
            __typename
        }
        ... on CommentTextSegment {
            text
            __typename
        }
        ... on User {
            id
            displayName
            role
            __typename
        }
        }
    """

    def gql(self, variant_id: int):
        query = {
            "operationName": self.OPERATION_NAME,
            "query": self.QUERY,
            "variables": {"variantId": variant_id},
        }
        return query

    def fetch(self, variant_id: int):
        try:
            response = requests.post(
                'https://civicdb.org/api/graphql',
                json=self.gql(variant_id=variant_id)
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error in {self.OPERATION_NAME}: {e}")
            raise
