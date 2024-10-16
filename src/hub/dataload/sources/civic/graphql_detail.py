import logging
import requests


class GraphqlVariantDetail():

    OPERATION_NAME = "VariantDetail"

    QUERY = """
    query VariantDetail($variantId: Int!) {
        variant(id: $variantId) {
            ...VariantDetailFields
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
            }
        }
        feature {
            id
            name
            link
            deprecated
            flagged
        }
        variantAliases
        flags(state: OPEN) {
            totalCount
        }
        openRevisionCount
        comments {
            totalCount
        }
    }

    fragment parsedCommentFragment on CommentBodySegment {
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
            }
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
            }
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
            }
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
            }
        }
        ... on CommentTextSegment {
            text
        }
        ... on User {
            id
            displayName
            role
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

    def fetch(self, api_url: str, variant_id: int):
        try:
            response = requests.post(
                api_url,
                json=self.gql(variant_id=variant_id)
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error in {self.OPERATION_NAME}: {e}")
            raise
