from biothings.tests.web import BiothingsDataTest

import pytest


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

    def test_101_query_exists_(self):
        # check if gnomad_exome.hom field exists
        self.query(q="_exists_:gnomad_exome.hom", fields="gnomad_exome.hom")

    def test_102_query_exists_(self):
        self.query(q="_exists_:gnomad_genome.hom", fields="gnomad_genome.hom")

    @pytest.mark.xfail(reason="dbnsfp mapping is not updated")
    def test_110_query_exists_(self):
        self.query(q="_exists_:dbnsfp.hgvsp&fields=dbnsfp.hgvsp")
        self.query(q="_exists_:dbnsfp.hgvsc&fields=dbnsfp.hgvsc")
        self.query(q="_exists_:dbnsfp.clinvar.clinvar_id&fields=dbnsfp.clinvar")
        self.query(q="_exists_:dbnsfp.clinvar.omim&fields=dbnsfp.clinvar")
        self.query(q="_exists_:dbnsfp.clinvar.medgen&fields=dbnsfp.clinvar")

    def test_121_query(self):
        breakpoint()
        self.query(q="rs58991260")

    def test_122_query(self):
        self.query(q="rcv000149017")

    def test_123_query(self):
        self.query(q="RCV000149017")

    def test_124_query(self):
        self.query(q="BTK", morethan=6000)

    def test_125_query(self):
        self.query(q="chr1:69000-70000", morethan=2000)

    def test_126_query(self):
        self.query(q="dbsnp.vartype:snv")

    @pytest.mark.skip(reason="Slow Test")
    def test_127_query(self):
        self.query(q="_exists_:dbnsfp")

    def test_128_query(self):
        self.query(q="dbnsfp.genename:BTK", morethan=5000)

    def test_129_query(self):
        self.query(q="snpeff.ann.genename:BTK", morethan=8000)

    def test_130_query(self):
        self.query(
            q="_exists_:wellderly AND cadd.polyphen.cat:possibly_damaging",
            fields="wellderly,cadd.polyphen",
        )

    @pytest.mark.xfail(reason="feature removed in biothings 0.7.0")
    def test_131_query_jsonld(self):
        con = self.request("query?q=rs58991260&callback=mycallback").content
        assert con.startswith("mycallback(".encode("utf-8"))

    def test_141_query_invalid(self):
        # testing non-ascii character
        res = self.request("query?q=54097\xef\xbf\xbd\xef\xbf\xbdmouse").json()
        assert res["hits"] == []

    def test_142_query_invalid(self):
        self.request("query")

    def test_143_clingen(self):
        # self.request("variant/CA9996207?assembly=hg38")
        self.request("variant/CA321211?assembly=hg38")

    def test_144_clingen(self):
        # self.request("hg38/CA9996207")
        self.request("hg38/CA321211")

    def test_150_query_post(self):
        # /query via post
        self.request("query", method="POST", data={"q": "rs58991260"}).json()

    def test_151_query_post(self):
        res = self.request(
            "query", method="POST", data={"q": "rs58991260", "scopes": "dbsnp.rsid"}
        ).json()
        assert len(res) == 1
        assert res[0]["_id"] == "chr1:g.218631822G>A"

    def test_152_query_post(self):
        res = self.request(
            "query",
            method="POST",
            data={"q": "rs58991260,rs268", "scopes": "dbsnp.rsid"},
        ).json()
        assert len(res) == 2
        assert res[0]["_id"] == "chr1:g.218631822G>A"
        assert res[1]["_id"] == "chr8:g.19813529A>G"

    def test_153_query_post(self):
        res = self.request(
            "query",
            method="POST",
            data={
                "q": "rs58991260",
                "scopes": "dbsnp.rsid",
                "fields": "dbsnp.chrom,dbsnp.alleles",
            },
        ).json()
        assert len(res) == 1, (res, len(res))

    def test_154_query_post(self):
        self.request("query", method="POST", expect=400)

    @pytest.mark.xfail(reason="Unknown query failure. Investigate why this is failing")
    def test_155_query_post(self):
        res = self.request(
            "query",
            method="POST",
            data={
                "q": '[rs58991260, "chr11:66397000-66398000"]',
                "scopes": "dbsnp.rsid",
            },
        ).json()
        assert len(res) == 2
        assert res[0]["_id"] == "chr1:g.218631822G>A"
        assert res[1]["_id"] == "chr8:g.19813529A>G"

    def test_160_query_interval(self):
        self.query(q="chr1:10000-100000", morethan=30000)

    def test_161_query_interval(self):
        self.query(q="chr11:45891937")

    def test_162_query_interval(self):
        self.query(q="chr11:45891937", assembly="hg19")

    def test_163_query_interval(self):
        self.query(q="chr6:128883143", assembly="hg38")

    def test_170_query_size(self):
        res = self.request("query?q=t*").json()
        assert len(res["hits"]) == 10  # default

    def test_171_query_size(self):
        res = self.request("query?q=t*&size=1000").json()
        assert len(res["hits"]) == 1000

    def test_172_query_size(self):
        res = self.request("query?q=t*&size=1001", expect=400)

    def test_173_query_size(self):
        res = self.request("query?q=t*&size=2000", expect=400)

    def test_180_query_facets(self):
        res = self.request(
            "query?q=cadd.gene.gene_id:ENSG00000113368&facets=cadd.polyphen.cat&size=0"
        ).json()
        assert "facets" in res and "cadd.polyphen.cat" in res["facets"]

    def test_190_query_unicode(self):
        s = "基因"
        self.request("variant/" + s, expect=404)

    def test_191_query_unicode(self):
        s = "基因"
        res = self.request("variant", method="POST", data={"ids": s}).json()
        assert res[0]["notfound"]
        assert len(res) == 1

    def test_192_query_unicode(self):
        s = "基因"
        res = self.request(
            "variant", method="POST", data={"ids": "rs2500, " + s}
        ).json()
        assert res[1]["notfound"]
        assert len(res) == 2

    def test_193_query_unicode(self):
        s = "基因"
        res = self.request("query?q=" + s).json()
        assert res["hits"] == []

    def test_194_query_unicode(self):
        s = "基因"
        res = self.request(
            "query", method="POST", data={"q": s, "scopes": "dbsnp"}
        ).json()
        assert res[0]["notfound"]
        assert len(res) == 1

    def test_195_query_unicode(self):
        s = "基因"
        res = self.request("query", method="POST", data={"q": "rs2500+" + s}).json()
        assert res[1]["notfound"]
        assert len(res) == 2

    def test_200_fetch_all(self):
        q = "_exists_:wellderly%20AND%20cadd.polyphen.cat:possibly_damaging&fields=wellderly,cadd.polyphen&fetch_all=TRUE"
        res = self.request("query?q=" + q).json()
        assert "_scroll_id" in res

        # get one set of results
        res2 = self.request("query?scroll_id=" + res["_scroll_id"]).json()
        assert "hits" in res2
        assert len(res2["hits"]) == 1000

    def test_201_msgpack(self):
        res = self.request("variant/chr8:g.19813529A>G").json()
        res2 = self.msgpack_ok(
            self.request("variant/chr8:g.19813529A>G?format=msgpack").content
        )
        assert res, res2

    def test_202_msgpack(self):

        res = self.request("query?q=rs2500").json()
        res2 = self.msgpack_ok(self.request("query?q=rs2500&format=msgpack").content)
        assert res, res2

    def test_203_msgpack(self):
        res = self.request("metadata").json()
        res2 = self.msgpack_ok(self.request("metadata?format=msgpack").content)
        assert res, res2

    # Too slow
    def test_210_licenses(self):
        # cadd license
        res = self.request("variant/chr17:g.61949543G>A").json()
        if "cadd" in res:
            assert "_license" in res["cadd"]
            assert res["cadd"]["_license"]
        if "comsic" in res:
            assert "_license" in res["cosmic"]
            assert res["cosmic"]["_license"]
        if "dbsnp" in res:
            assert "_license" in res["dbsnp"]
            assert res["dbsnp"]["_license"]
        if "snpeff" in res:
            assert "_license" in res["snpeff"]
            assert res["snpeff"]["_license"]

    @pytest.mark.xfail(reason="feature removed in biothings 0.7.0")
    def test_220_jsonld(self):
        res = self.request("variant/chr8:g.19813529A>G?jsonld=true").json()
        assert "@context" in res
        assert "@id" in res

        # Check some subfields - INVALIDATED BY NEW JSON-LD STRUCTURE
        # assert 'snpeff' in res and '@context' in res['snpeff']

        # assert 'ann' in res['snpeff'] and '@context' in res['snpeff']['ann'][0]

        # Check a post with jsonld
        res = self.request(
            "variant",
            method="POST",
            data={"ids": "chr16:g.28883241A>G, chr8:g.19813529A>G", "jsonld": "true"},
        ).json()
        for r in res:
            assert "@context" in r
            assert "@id" in r

        # Check a query get with jsonld
        res = self.request(
            "query?q=_exists_:clinvar&fields=clinvar&size=1&jsonld=true"
        ).json()

        assert "@context" in res["hits"][0]
        assert "@id" in res["hits"][0]

        # subfields
        # assert 'clinvar' in res['hits'][0] and '@context' in res['hits'][0]['clinvar']
        # TODO: fix test
        # assert 'gene' in res['hits'][0]['clinvar'] and '@context' in res['hits'][0]['clinvar']['gene']

        # Check query post with jsonld
        res = self.request(
            "query",
            method="POST",
            data={"q": "rs58991260,rs268", "scopes": "dbsnp.rsid", "jsonld": "true"},
        ).json()

        assert len(res) == 2
        assert "@context" in res[0] and "@context" in res[1]
        assert "@id" in res[0] and "@id" in res[1]
        # assert 'snpeff' in res[1] and '@context' in res[1]['snpeff']
        # assert 'ann' in res[1]['snpeff'] and '@context' in res[1]['snpeff']['ann'][0]

    def test_230_assembly(self):
        res = self.query(
            q="clinvar.ref:C AND chr11:56319006 AND clinvar.alt:A", assembly="hg38"
        )
        assert res["hits"][0]["_id"] == "chr11:g.56319006C>A"

    def test_240_HGVS_redirect(self):

        res = self.request("variant/chr8:19813529A>G").json()
        res2 = self.request("variant/chr8:g19813529A>G").json()
        res3 = self.request("variant/chr8:.19813529A>G").json()
        res4 = self.request("variant/chr8:g.19813529A>G").json()

        assert res == res2
        assert res2 == res3
        assert res3 == res4
        assert res["_id"] == "chr8:g.19813529A>G"

    def test_241_HGVS_long(self):
        # test_seqhashed_long_hgvs_id
        res = self.request("query?q=_exists_:_seqhashed&fields=_seqhashed").json()
        assert "_seqhashed_" in res["hits"][0]["_id"]
        h = res["hits"][0]["_id"].split("_seqhashed_")[-1]
        assert h in res["hits"][0]["_seqhashed"]

    def test_250_nested_match(self):
        payload = {
            "q": [["CDK2", "c.314A>T"]],
            "scopes": [
                ["dbsnp.gene.symbol", "snpeff.ann.genename"],
                "snpeff.ann.hgvs_c",
            ],
        }
        ans = self.query(method="POST", json=payload)
        assert ans[0]["_id"] == "chr12:g.56361952A>T"
        assert ans[1]["_id"] == "chr12:g.56362638A>T"

    def test_251_nested_match(self):
        payload = {
            "q": [["CDK2", "c.314A>T"], ["CXCR4", "c.535G>C"]],
            "scopes": [
                ["dbsnp.gene.symbol", "snpeff.ann.genename"],
                "snpeff.ann.hgvs_c",
            ],
            "fields": ["dbsnp.gene.symbol", "snpeff.ann.genename", "snpeff.ann.hgvs_c"],
        }
        ans = self.query(method="POST", json=payload)
        assert ans[0]["_id"] == "chr12:g.56361952A>T"
        assert ans[1]["_id"] == "chr12:g.56362638A>T"
        assert ans[2]["_id"] == "chr2:g.136872975C>G"
        assert ans[3]["_id"] == "chr2:g.136872963C>G"
