import logging
import requests


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
        try:
            response = requests.post(
                api_url,
                json=self.gql(variant_id=variant_id)
            )
            return response.json()
        except Exception as e:
            logging.error(f"Error in {self.OPERATION_NAME}: {e}")
            raise
