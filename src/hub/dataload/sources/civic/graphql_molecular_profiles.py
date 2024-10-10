import logging
import requests


class GraphqlMolecularProfiles():

    OPERATION_NAME = "BrowseMolecularProfiles"

    QUERY = """
        query BrowseMolecularProfiles($molecularProfileName: String, $variantName: String, $variantId: Int, $featureName: String, $diseaseName: String, $therapyName: String, $molecularProfileAlias: String, $sortBy: MolecularProfilesSort, $first: Int, $last: Int, $before: String, $after: String) {
        browseMolecularProfiles(
            molecularProfileName: $molecularProfileName
            variantName: $variantName
            variantId: $variantId
            featureName: $featureName
            diseaseName: $diseaseName
            therapyName: $therapyName
            molecularProfileAlias: $molecularProfileAlias
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
                ...BrowseMolecularProfilesFields
                __typename
            }
            __typename
            }
            lastUpdated
            filteredCount
            pageCount
            __typename
        }
        }

        fragment BrowseMolecularProfilesFields on BrowseMolecularProfile {
        id
        name
        evidenceItemCount
        molecularProfileScore
        assertionCount
        variantCount
        aliases {
            name
            __typename
        }
        variants {
            id
            name
            link
            matchText
            feature {
            id
            link
            name
            __typename
            }
            __typename
        }
        therapies {
            id
            name
            link
            deprecated
            __typename
        }
        diseases {
            id
            name
            link
            deprecated
            __typename
        }
        link
        deprecated
        __typename
        }
    """

    def gql(self, variant_id: int):
        query = {
            "operationName": self.OPERATION_NAME,
            "query": self.QUERY,
            "variables": {"first": 35, "variantId": variant_id},
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
