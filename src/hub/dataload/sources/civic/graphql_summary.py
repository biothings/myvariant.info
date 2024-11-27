import logging
import requests


class GraphqlVariantSummary():

    OPERATION_NAME = "VariantSummary"

    QUERY = """
    query VariantSummary($variantId: Int!) {
        variant(id: $variantId) {
            ...VariantSummaryFields
        }
    }

    fragment VariantSummaryFields on VariantInterface {
        id
        name
        feature {
            id
            name
            link
            deprecated
            flagged
        }
        variantAliases
        variantTypes {
            id
            link
            soid
            name
        }
        flags(state: OPEN) {
            totalCount
        }
        revisions(status: NEW) {
            totalCount
        }
        comments {
            totalCount
        }
        lastSubmittedRevisionEvent {
            originatingUser {
                id
                displayName
                role
                profileImagePath(size: 32)
            }
        }
        lastAcceptedRevisionEvent {
            originatingUser {
                id
                displayName
                role
                profileImagePath(size: 32)
            }
        }
        creationActivity {
            user {
                id
                displayName
                role
                profileImagePath(size: 32)
            }
            createdAt
        }
        deprecationActivity {
            user {
                id
                displayName
                role
                profileImagePath(size: 32)
            }
            createdAt
        }
        ... on GeneVariant {
            ...GeneVariantSummaryFields
        }
        ... on FactorVariant {
            ...FactorVariantSummaryFields
        }
        ... on FusionVariant {
            ...FusionVariantSummaryFields
        }
    }

    fragment GeneVariantSummaryFields on GeneVariant {
        alleleRegistryId
        openCravatUrl
        maneSelectTranscript
        hgvsDescriptions
        clinvarIds
        coordinates {
            ...CoordinateFields
        }
        myVariantInfo {
            ...MyVariantInfoFields
        }
    }

    fragment CoordinateFields on VariantCoordinate {
        referenceBuild
        ensemblVersion
        chromosome
        representativeTranscript
        start
        stop
        referenceBases
        variantBases
        coordinateType
    }

    fragment MyVariantInfoFields on MyVariantInfo {
        myVariantInfoId
        caddConsequence
        caddDetail
        caddScore
        caddPhred
        clinvarClinicalSignificance
        clinvarHgvsCoding
        clinvarHgvsGenomic
        clinvarHgvsNonCoding
        clinvarHgvsProtein
        clinvarId
        clinvarOmim
        cosmicId
        dbnsfpInterproDomain
        dbsnpRsid
        eglClass
        eglHgvs
        eglProtein
        eglTranscript
        exacAlleleCount
        exacAlleleFrequency
        exacAlleleNumber
        fathmmMklPrediction
        fathmmMklScore
        fathmmPrediction
        fathmmScore
        fitconsScore
        gerp
        gnomadExomeAlleleCount
        gnomadExomeAlleleFrequency
        gnomadExomeAlleleNumber
        gnomadExomeFilter
        gnomadGenomeAlleleCount
        gnomadGenomeAlleleFrequency
        gnomadGenomeAlleleNumber
        gnomadGenomeFilter
        lrtPrediction
        lrtScore
        metalrPrediction
        metalrScore
        metasvmPrediction
        metasvmScore
        mutationassessorPrediction
        mutationassessorScore
        mutationtasterPrediction
        mutationtasterScore
        phastcons100way
        phastcons30way
        phyloP100way
        phyloP30way
        polyphen2HdivPrediction
        polyphen2HdivScore
        polyphen2HvarPrediction
        polyphen2HvarScore
        proveanPrediction
        proveanScore
        revelScore
        siftPrediction
        siftScore
        siphy
        snpeffSnpEffect
        snpeffSnpImpact
    }

    fragment FactorVariantSummaryFields on FactorVariant {
        ncitId
        ncitDetails {
            ...NcitDetails
        }
    }

    fragment NcitDetails on NcitDetails {
        synonyms {
            name
            source
        }
        definitions {
            definition
            source
        }
    }

    fragment FusionVariantSummaryFields on FusionVariant {
        viccCompliantName
        fusion {
            fivePrimePartnerStatus
            fivePrimeGene {
                id
                name
                link
                deprecated
                flagged
            }
            threePrimePartnerStatus
            threePrimeGene {
                id
                name
                link
                deprecated
                flagged
            }
        }
        fivePrimeCoordinates {
            ...CoordinateFields
        }
        threePrimeCoordinates {
            ...CoordinateFields
        }
        fivePrimeStartExonCoordinates {
            ...ExonCoordinateFields
        }
        fivePrimeEndExonCoordinates {
            ...ExonCoordinateFields
        }
        threePrimeStartExonCoordinates {
            ...ExonCoordinateFields
        }
        threePrimeEndExonCoordinates {
            ...ExonCoordinateFields
        }
    }

    fragment ExonCoordinateFields on ExonCoordinate {
        referenceBuild
        ensemblVersion
        chromosome
        representativeTranscript
        start
        stop
        exon
        exonOffset
        exonOffsetDirection
        ensemblId
        strand
        coordinateType
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
