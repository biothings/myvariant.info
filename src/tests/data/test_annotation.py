"""
MyVariant Data-Aware Tests
"""

import logging

import pytest
import requests

from biothings.tests.web import BiothingsDataTest


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestMyvariant(BiothingsDataTest):
    prefix = "v1"
    host = "myvariant.info"

    # override
    def query(self, *args, **kwargs):
        morethan = kwargs.pop("morethan", None)
        res = super().query(*args, **kwargs)
        if morethan:  # feature only defined for GETs
            assert isinstance(res, dict)
            assert res["total"] > morethan
        return res

    def test_010_annotation(self):
        # test all fields are loaded in variant objects
        res = self.request("variant/chr1:g.218631822G>A").json()
        attr_li = ["_id"]
        for attr in attr_li:
            assert attr in res
            assert res[attr]

    def test_011_annotation(self):
        res = self.request("variant/chr16:g.28883241A>G").json()
        assert res["_id"] == "chr16:g.28883241A>G"

    def test_012_annotation(self):
        res = self.request("variant/chr1:g.35367G>A").json()
        assert res["_id"] == "chr1:g.35367G>A"

    def test_013_annotation(self):
        res = self.request("variant/chr7:g.55241707G>T").json()
        assert res["_id"] == "chr7:g.55241707G>T"

    def test_020_annotation(self):
        # testing non-ascii character
        self.request(
            "variant/" + "chr7:g.55241707G>T\xef\xbf\xbd\xef\xbf\xbdmouse", expect=404
        )

    def test_021_annotation(self):
        # testing filtering parameters
        res = self.request(
            "variant/chr16:g.28883241A>G?fields=dbsnp,dbnsfp,cadd"
        ).json()
        assert set(res) == set(["_id", "_version", "dbnsfp", "cadd", "dbsnp"])

    def test_022_annotation(self):
        res = self.request("variant/chr16:g.28883241A>G?fields=wellderly").json()
        assert set(res) == set(["_id", "_version", "wellderly"])

    def test_023_annotation(self):
        res = self.request("variant/chr9:g.107620835G>A?fields=dbsnp").json()
        assert set(res) == set(["_id", "_version", "dbsnp"])

    def test_024_annotation(self):
        res = self.request(
            "variant/chr1:g.31349647C>T?fields=dbnsfp.clinvar,dbsnp.gmaf,clinvar.hgvs"
        ).json()
        assert set(res) == set(["_id", "_version", "clinvar", "dbnsfp"])

    def test_030_annotation(self):
        self.request("variant", expect=400)

    def test_031_annotation(self):
        self.request("variant/", expect=400)

    def test_040_annotation_post(self):
        res = self.request(
            "variant", method="POST", data={"ids": "chr16:g.28883241A>G"}
        ).json()
        assert len(res) == 1
        assert res[0]["_id"] == "chr16:g.28883241A>G"

    def test_041_annotation_post(self):
        res = self.request(
            "variant",
            method="POST",
            data={"ids": "chr16:g.28883241A>G, chr8:g.19813529A>G"},
        ).json()
        assert len(res) == 2
        assert res[0]["_id"] == "chr16:g.28883241A>G"
        assert res[1]["_id"] == "chr8:g.19813529A>G"

    def test_042_annotation_post(self):
        res = self.request(
            "variant",
            method="POST",
            data={"ids": "chr16:g.28883241A>G, chr8:g.19813529A>G", "fields": "dbsnp"},
        ).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(["_id", "_version", "query", "dbsnp"])

    def test_043_annotation_post(self):
        # TODO redo this test, doesn't test much really....
        res = self.request(
            "variant",
            method="POST",
            data={
                "ids": "chr16:g.28883241A>G,chr8:g.19813529A>G",
                "fields": "dbsnp.chrom",
            },
        ).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(["_id", "query", "dbsnp", "_version"])

    @pytest.mark.heavy
    def test_044_annotation_post(self):
        """
        Test a large variant post
        """
        from variant_list import VARIANT_POST_LIST
        res = self.request(
            "variant", method="POST", data={"ids": VARIANT_POST_LIST}
        ).json()
        assert len(res) == 999

    def test_050_annotation_multihit(self):
        res = self.request("variant/rs2267").json()
        assert isinstance(res, list)
        assert len(res) == 2



class TestMyVariantCurieIdParsing(BiothingsDataTest):
    host = "myvariant.info"
    prefix = "v1"

    def test_001_curie_id_annotation_endpoint_GET(self):
        """
        Tests the annotation endpoint support for the biolink CURIE ID.

        If support is enabled then we should retrieve the exact same document
        for all the provided queries
        """
        curie_id_testing_collection = [
            (
                "chr19:g.11576858T>C?assembly=hg38",
                "clingen.caid:CA305359245?assembly=hg38",
                "CAID:CA305359245?assembly=hg38",
                "caid:CA305359245?assembly=hg38",
                "CaiD:CA305359245?assembly=hg38"
            ),
            (
                "chr18:g.23536742C>T?assembly=hg38",
                "dbsnp.rsid:rs771000314?assembly=hg38",
                "DBSNP:rs771000314?assembly=hg38",
                "dbsnp:rs771000314?assembly=hg38",
                "DBsnP:rs771000314?assembly=hg38"
            ),
            (
                "chr19:g.39424249C>A?assembly=hg38",
                "clinvar.variant_id:1992548?assembly=hg38",
                "CLINVAR:1992548?assembly=hg38",
                "clinvar:1992548?assembly=hg38",
                "ClinVAR:1992548?assembly=hg38"
            )
        ]
        aggregation_query_groups = []
        endpoint = "variant"
        for query_collection in curie_id_testing_collection:
            query_result_storage = []
            for similar_query in query_collection:
                query_result = self.request(f"{endpoint}/{similar_query}", expect=200)
                query_result = self.request(f"{endpoint}/{similar_query}")
                assert isinstance(query_result, requests.models.Response)
                query_result_storage.append(query_result.json())

            results_aggregation = [
                query == query_result_storage[0] for query in query_result_storage[1:]
            ]

            if all(results_aggregation):
                logger.info(f"Query group {query_collection} succeeded")
            else:
                logger.info(f"Query group {query_collection} failed")

            aggregation_query_groups.append(all(results_aggregation))
        assert all(aggregation_query_groups)


    def test_002_curie_id_annotation_endpoint_POST(self):
        """
        Tests the annotations endpoint support for the biolink CURIE ID.

        Batch query testing against the POST endpoint to verify that the CURIE ID can work with
        multiple

        If support is enabled then we should retrieve the exact same document for all the provided
        queries
        """
        curie_id_testing_collection = [
            (
                "chr19:g.11576858T>C?assembly=hg38",
                "clingen.caid:CA305359245?assembly=hg38",
                "CAID:CA305359245?assembly=hg38",
                "caid:CA305359245?assembly=hg38",
                "CaiD:CA305359245?assembly=hg38"
            ),
            (
                "chr18:g.23536742C>T?assembly=hg38",
                "dbsnp.rsid:rs771000314?assembly=hg38",
                "DBSNP:rs771000314?assembly=hg38",
                "dbsnp:rs771000314?assembly=hg38",
                "DBsnP:rs771000314?assembly=hg38"
            ),
            (
                "chr19:g.39424249C>A?assembly=hg38",
                "clinvar.variant_id:1992548?assembly=hg38",
                "CLINVAR:1992548?assembly=hg38",
                "clinvar:1992548?assembly=hg38",
                "ClinVAR:1992548?assembly=hg38"
            )
        ]

        results_aggregation = []
        endpoint = "variant"
        for query_collection in curie_id_testing_collection:
            base_result = self.request(f"{endpoint}/{query_collection[0]}", expect=200)

            delimiter = ","
            data_mapping = {
                "ids": delimiter.join([f'"{query}"' for query in query_collection])
            }

            query_results = self.request(
                endpoint, method="POST", data=data_mapping
            ).json()
            assert len(query_results) == len(query_collection)

            batch_result = []
            for query_result, query_entry in zip(query_results, query_collection):
                return_query_field = query_result.pop("query")
                assert return_query_field == str(query_entry)
                batch_result.append(base_result.json() == query_result)

            aggregate_result = all(results_aggregation)

            if aggregate_result:
                logger.info(f"Query group {query_collection} succeeded")
            else:
                logger.info(f"Query group {query_collection} failed")

            results_aggregation.append(aggregate_result)
        assert all(results_aggregation)
