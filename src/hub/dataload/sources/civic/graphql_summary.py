import logging
import requests


class GraphqlVariantSummary():

    OPERATION_NAME = "VariantSummary"

    QUERY = """
        query VariantSummary($variantId: Int!) {
        variant(id: $variantId) {
            ...VariantSummaryFields
            __typename
        }
        }

        fragment VariantSummaryFields on VariantInterface {
        id
        name
        feature {
            __typename
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
            __typename
        }
        flags(state: OPEN) {
            totalCount
            __typename
        }
        revisions(status: NEW) {
            totalCount
            __typename
        }
        comments {
            totalCount
            __typename
        }
        lastSubmittedRevisionEvent {
            originatingUser {
            id
            displayName
            role
            profileImagePath(size: 32)
            __typename
            }
            __typename
        }
        lastAcceptedRevisionEvent {
            originatingUser {
            id
            displayName
            role
            profileImagePath(size: 32)
            __typename
            }
            __typename
        }
        creationActivity {
            user {
            id
            displayName
            role
            profileImagePath(size: 32)
            __typename
            }
            createdAt
            __typename
        }
        deprecationActivity {
            user {
            id
            displayName
            role
            profileImagePath(size: 32)
            __typename
            }
            createdAt
            __typename
        }
        ... on GeneVariant {
            ...GeneVariantSummaryFields
            __typename
        }
        ... on FactorVariant {
            ...FactorVariantSummaryFields
            __typename
        }
        ... on FusionVariant {
            ...FusionVariantSummaryFields
            __typename
        }
        __typename
        }

        fragment GeneVariantSummaryFields on GeneVariant {
        alleleRegistryId
        openCravatUrl
        maneSelectTranscript
        hgvsDescriptions
        clinvarIds
        coordinates {
            ...CoordinateFields
            __typename
        }
        myVariantInfo {
            ...MyVariantInfoFields
            __typename
        }
        __typename
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
        __typename
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
        __typename
        }

        fragment FactorVariantSummaryFields on FactorVariant {
        ncitId
        ncitDetails {
            ...NcitDetails
            __typename
        }
        __typename
        }

        fragment NcitDetails on NcitDetails {
        synonyms {
            name
            source
            __typename
        }
        definitions {
            definition
            source
            __typename
        }
        __typename
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
            __typename
            }
            threePrimePartnerStatus
            threePrimeGene {
            id
            name
            link
            deprecated
            flagged
            __typename
            }
            __typename
        }
        fivePrimeCoordinates {
            ...CoordinateFields
            __typename
        }
        threePrimeCoordinates {
            ...CoordinateFields
            __typename
        }
        fivePrimeStartExonCoordinates {
            ...ExonCoordinateFields
            __typename
        }
        fivePrimeEndExonCoordinates {
            ...ExonCoordinateFields
            __typename
        }
        threePrimeStartExonCoordinates {
            ...ExonCoordinateFields
            __typename
        }
        threePrimeEndExonCoordinates {
            ...ExonCoordinateFields
            __typename
        }
        __typename
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
        __typename
        }
    """

    def get_query(self, variant_id: int):
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
