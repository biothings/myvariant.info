'''
    MyVariant Data-Aware Tests
'''

from biothings.tests.web import BiothingsDataTest


class TestMyvariant(BiothingsDataTest):
    prefix = 'v1'
    host = 'myvariant.info'

    # override
    def query(self, *args, **kwargs):
        morethan = kwargs.pop('morethan', None)
        res = super().query(*args, **kwargs)
        if morethan:  # feature only defined for GETs
            assert isinstance(res, dict)
            assert res['total'] > morethan
        return res

    def test_010_annotation(self):
        # test all fields are loaded in variant objects
        res = self.request('variant/chr1:g.218631822G>A').json()
        attr_li = ['_id']
        for attr in attr_li:
            assert attr in res
            assert res[attr]

    def test_011_annotation(self):
        res = self.request('variant/chr16:g.28883241A>G').json()
        assert res['_id'] == "chr16:g.28883241A>G"

    def test_012_annotation(self):
        res = self.request('variant/chr1:g.35367G>A').json()
        assert res['_id'] == "chr1:g.35367G>A"

    def test_013_annotation(self):
        res = self.request('variant/chr7:g.55241707G>T').json()
        assert res['_id'] == "chr7:g.55241707G>T"

    def test_020_annotation(self):
        # testing non-ascii character
        self.request('variant/' +
                     'chr7:g.55241707G>T\xef\xbf\xbd\xef\xbf\xbdmouse', expect=404)

    def test_021_annotation(self):
        # testing filtering parameters
        res = self.request('variant/chr16:g.28883241A>G?fields=dbsnp,dbnsfp,cadd').json()
        assert set(res) == set(['_id', '_version', 'dbnsfp', 'cadd', 'dbsnp'])

    def test_022_annotation(self):
        res = self.request('variant/chr16:g.28883241A>G?fields=wellderly').json()
        assert set(res) == set(['_id', '_version', 'wellderly'])

    def test_023_annotation(self):
        res = self.request('variant/chr9:g.107620835G>A?fields=dbsnp').json()
        assert set(res) == set(['_id', '_version', 'dbsnp'])

    def test_024_annotation(self):
        res = self.request(
            'variant/chr1:g.31349647C>T?fields=dbnsfp.clinvar,dbsnp.gmaf,clinvar.hgvs').json()
        assert set(res) == set(['_id', '_version', 'clinvar', 'dbnsfp'])

    def test_030_annotation(self):
        self.request('variant', expect=400)

    def test_031_annotation(self):
        self.request('variant/', expect=400)

    def test_040_annotation_post(self):
        res = self.request("variant", method='POST', data={'ids': 'chr16:g.28883241A>G'}).json()
        assert len(res) == 1
        assert res[0]['_id'] == "chr16:g.28883241A>G"

    def test_041_annotation_post(self):
        res = self.request("variant", method='POST', data={
                           'ids': 'chr16:g.28883241A>G, chr8:g.19813529A>G'}).json()
        assert len(res) == 2
        assert res[0]['_id'] == 'chr16:g.28883241A>G'
        assert res[1]['_id'] == 'chr8:g.19813529A>G'

    def test_042_annotation_post(self):
        res = self.request(
            "variant", method='POST',
            data={'ids': 'chr16:g.28883241A>G, chr8:g.19813529A>G', 'fields': 'dbsnp'}).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(['_id', '_version', 'query', 'dbsnp'])

    def test_043_annotation_post(self):
        # TODO redo this test, doesn't test much really....
        res = self.request("variant", method='POST',
                           data={'ids': 'chr16:g.28883241A>G,chr8:g.19813529A>G',
                                 'fields': 'dbsnp.chrom'}).json()
        assert len(res) == 2
        for _g in res:
            assert set(_g) == set(['_id', 'query', 'dbsnp', '_version'])

    def test_044_annotation_post(self):
        # Test a large variant post
        # # too slow
        # res = self.request("variant", method='POST', data={'ids': VARIANT_POST_LIST}).json()
        # assert len(res) == 999
        pass  # TODO

    def test_050_annotation_multihit(self):
        res = self.request("variant/rs2267").json()
        assert isinstance(res, list)
        assert len(res) == 2
