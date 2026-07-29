from hub.dataload.sources.civic.graphql_client import post_graphql


class GraphqlGeneVariant():

    OPERATION_NAME = "GeneVariant"

    QUERY = """
    query GeneVariant($variantId: Int!) {
        variant(id: $variantId) {
            id
            feature {
                id
                name
            }
            name
            molecularProfiles {
                nodes {
                    name
                    id
                    molecularProfileScore
                    molecularProfileAliases
                    variants {
                        id
                        name
                        link
                    }
                    evidenceItems {
                        edges {
                            node {
                                description
                                id
                                name
                                phenotypes {
                                    description
                                    hpoId
                                    id
                                    link
                                    name
                                    url
                                }
                                disease {
                                    myDiseaseInfo {
                                        omim
                                        mondoId
                                        mesh
                                        icd10
                                        icdo
                                        ncit
                                        doDef
                                    }
                                    name
                                    diseaseAliases
                                    diseaseUrl
                                    displayName
                                    doid
                                    id
                                    link
                                }
                                variantOrigin
                                evidenceDirection
                                evidenceLevel
                                evidenceRating
                                evidenceType
                                flagged
                                significance
                                molecularProfile {
                                    id
                                }
                                source {
                                    citation
                                    id
                                    name
                                    sourceUrl
                                    title
                                    sourceType
                                    link
                                    journal
                                    pmcId
                                    openAccess
                                    publicationDate
                                    retracted
                                    retractionDate
                                    retractionNature
                                    retractionReasons
                                    citationId
                                    authorString
                                    abstract
                                }
                                therapies {
                                    id
                                    name
                                    link
                                    deprecated
                                }
                            }
                        }
                        totalCount
                    }
                }
            }
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
        return post_graphql(
            api_url=api_url,
            payload=self.gql(variant_id=variant_id),
            operation_name=self.OPERATION_NAME,
        )
