'''
    MyVariant Data-Aware Tests
'''
import os

from nose.core import runmodule
from nose.tools import eq_, ok_

from biothings.tests import BiothingsTestCase


class MyVariantRemoteTest(BiothingsTestCase):
    '''
        Test against server specified in environment variable BT_HOST
        or MyVariant.info production server if BT_HOST is not specified
        BT_HOST must start with its protocol like http://myvariant.info
    '''
    __test__ = True

    host = os.getenv("BT_HOST", "http://myvariant.info")
    host = host.rstrip('/')
    api = '/v1'

    def test_variant_object(self):
        # test all fields are loaded in variant objects
        res = self.request('variant/chr1:g.218631822G>A').json()
        attr_li = ['_id']
        for attr in attr_li:
            assert res.get(
                attr, None) is not None, 'Missing field "{}" in variant "chr1:g.218631822G>A"'.format(attr)

        # test for specific databases

    def has_hits(self, q, morethan=0):
        d = self.request('query?q='+q).json()
        ok_(d.get('total', 0) > morethan and len(d.get('hits', [])) > 0)
        ok_('_id' in d['hits'][0])

    def test_query(self):
        # public query self.api at /query via get
        # check if gnomad_exome.hom field exists
        self.has_hits('_exists_:gnomad_exome.hom&fields=gnomad_exome.hom')
        self.has_hits('_exists_:gnomad_genome.hom&fields=gnomad_genome.hom')
        self.has_hits('rs58991260')
        self.has_hits('rcv000149017')
        self.has_hits('RCV000149017')
        self.has_hits('BTK', morethan=6000)

        self.has_hits('chr1:69000-70000', morethan=2000)
        self.has_hits('dbsnp.vartype:snv')
        # Too slow
        # self.has_hits('_exists_:dbnsfp')
        self.has_hits('dbnsfp.genename:BTK', morethan=5000)
        self.has_hits('snpeff.ann.genename:BTK', morethan=8000)
        self.has_hits(
            '_exists_:wellderly%20AND%20cadd.polyphen.cat:possibly_damaging&fields=wellderly,cadd.polyphen')

        con = self.request("query?q=rs58991260&callback=mycallback").content
        ok_(con.startswith('mycallback('.encode('utf-8')))

        # testing non-ascii character
        res = self.request('query?q=54097\xef\xbf\xbd\xef\xbf\xbdmouse').json()
        eq_(res['hits'], [])

        self.request("query", expect_status=400)

    def test_query_post(self):
        # /query via post
        self.request("query", method='POST', data={'q': 'rs58991260'}).json()

        res = self.request("query", method='POST', data={'q': 'rs58991260',
                                                              'scopes': 'dbsnp.rsid'}).json()
        eq_(len(res), 1)
        eq_(res[0]['_id'], 'chr1:g.218631822G>A')

        res = self.request("query", method='POST', data={'q': 'rs58991260,rs2500',
                                                              'scopes': 'dbsnp.rsid'}).json()
        print(res)
        eq_(len(res), 2)
        eq_(res[0]['_id'], 'chr1:g.218631822G>A')
        eq_(res[1]['_id'], 'chr11:g.66397320A>G')

        res = self.request("query", method='POST',
                           data={'q': 'rs58991260', 'scopes': 'dbsnp.rsid',
                                 'fields': 'dbsnp.chrom,dbsnp.alleles'}).json()
        assert len(res) == 1, (res, len(res))

        self.request(self.api + '/query', method='POST', expect_status=400)

        # TODO fix this test query
        # res = self.request("query", method='POST', data={'q': '[rs58991260, "chr11:66397000-66398000"]',
        #                                       'scopes': 'dbsnp.rsid'}).json()
        #eq_(len(res), 2)
        #eq_(res[0]['_id'], 'chr1:g.218631822G>A')
        #eq_(res[1]['_id'], 'chr11:g.66397320A>G')

    def test_query_interval(self):
        self.has_hits('chr1:10000-100000', morethan=30000)
        self.has_hits('chr11:45891937')
        self.has_hits('chr11:45891937&assembly=hg19')
        self.has_hits('chr6:128883143&assembly=hg38')

    def test_query_size(self):
        # TODO: port other tests (refactor to biothing.self.api ?)

        res = self.request('query?q=t*').json()
        eq_(len(res['hits']), 10)    # default
        res = self.request('query?q=t*&size=1000').json()
        eq_(len(res['hits']), 1000)
        res = self.request('query?q=t*&size=1001').json()
        eq_(len(res['hits']), 1000)
        res = self.request('query?q=t*&size=2000').json()
        eq_(len(res['hits']), 1000)

    def test_variant(self):
        # TODO
        res = self.request('variant/chr16:g.28883241A>G').json()
        eq_(res['_id'], "chr16:g.28883241A>G")

        res = self.request('variant/chr1:g.35367G>A').json()
        eq_(res['_id'], "chr1:g.35367G>A")

        res = self.request('variant/chr7:g.55241707G>T').json()
        eq_(res['_id'], "chr7:g.55241707G>T")

        # testing non-ascii character
        self.request('variant/' +
                     'chr7:g.55241707G>T\xef\xbf\xbd\xef\xbf\xbdmouse', expect_status=404)

        # testing filtering parameters
        res = self.request('variant/chr16:g.28883241A>G?fields=dbsnp,dbnsfp,cadd').json()
        eq_(set(res), set(['_id', '_version', 'dbnsfp', 'cadd', 'dbsnp']))
        res = self.request('variant/chr16:g.28883241A>G?fields=wellderly').json()
        eq_(set(res), set(['_id', '_version', 'wellderly']))
        res = self.request('variant/chr9:g.107620835G>A?fields=dbsnp').json()
        eq_(set(res), set(['_id', '_version', 'dbsnp']))
        res = self.request(
            'variant/chr1:g.31349647C>T?fields=dbnsfp.clinvar,dbsnp.gmaf,clinvar.hgvs').json()
        eq_(set(res), set(['_id', '_version', 'clinvar', 'dbnsfp']))

        self.request('variant', expect_status=404)
        self.request('variant/', expect_status=404)

    def test_variant_post(self):
        res = self.request("variant", method='POST', data={'ids': 'chr16:g.28883241A>G'}).json()
        eq_(len(res), 1)
        eq_(res[0]['_id'], "chr16:g.28883241A>G")

        res = self.request("variant", method='POST', data={
                           'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G'}).json()
        eq_(len(res), 2)
        eq_(res[0]['_id'], 'chr16:g.28883241A>G')
        eq_(res[1]['_id'], 'chr11:g.66397320A>G')

        res = self.request(
            "variant", method='POST',
            data={'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'fields': 'dbsnp'}).json()
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', 'query', 'dbsnp']))

        # TODO redo this test, doesn't test much really....
        res = self.request("variant", method='POST',
                           data={'ids': 'chr16:g.28883241A>G,chr11:g.66397320A>G',
                                 'filter': 'dbsnp.chrom'}).json()
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', 'query', 'dbsnp']))

        # Test a large variant post
        # # too slow
        # res = self.request("variant", method='POST', data={'ids': VARIANT_POST_LIST}).json()
        # eq_(len(res), 999)

    def test_metadata(self):
        self.request("metadata").content

    def test_query_facets(self):
        res = self.request(
            'query?q=cadd.gene.gene_id:ENSG00000113368&facets=cadd.polyphen.cat&size=0').json()
        assert 'facets' in res and 'cadd.polyphen.cat' in res['facets']

    def test_unicode(self):
        s = '基因'

        self.request('variant/' + s, expect_status=404)

        res = self.request("variant", method='POST', data={'ids': s}).json()
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)
        res = self.request("variant", method='POST', data={'ids': 'rs2500, ' + s}).json()
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

        res = self.request('query?q=' + s).json()
        eq_(res['hits'], [])

        res = self.request("query", method='POST', data={"q": s, "scopes": 'dbsnp'}).json()
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)

        res = self.request("query", method='POST', data={"q": 'rs2500+' + s}).json()
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

    def test_get_fields(self):
        res = self.request('metadata/fields').json()
        # Check to see if there are enough keys
        ok_(len(res) > 480)

        # Check some specific keys
        assert 'cadd' in res
        assert 'dbnsfp' in res
        assert 'dbsnp' in res
        assert 'wellderly' in res
        assert 'clinvar' in res

    def test_fetch_all(self):
        q = '_exists_:wellderly%20AND%20cadd.polyphen.cat:possibly_damaging&fields=wellderly,cadd.polyphen&fetch_all=TRUE'
        res = self.request('query?q=' + q).json()
        assert '_scroll_id' in res

        # get one set of results
        res2 = self.request('query?scroll_id=' + res['_scroll_id']).json()
        assert 'hits' in res2
        ok_(len(res2['hits']) == 1000)

    def test_msgpack(self):
        res = self.request('variant/chr11:g.66397320A>G').json()
        res2 = self.msgpack_ok(self.request("variant/chr11:g.66397320A>G?format=msgpack").content)
        ok_(res, res2)

        res = self.request('query?q=rs2500').json()
        res2 = self.msgpack_ok(self.request("query?q=rs2500&format=msgpack").content)
        ok_(res, res2)

        res = self.request('metadata').json()
        res2 = self.msgpack_ok(self.request("metadata?format=msgpack").content)
        ok_(res, res2)

    # Too slow
    def test_licenses(self):
        # cadd license
        res = self.request('variant/chr17:g.61949543G>A').json()
        if 'cadd' in res:
            assert '_license' in res['cadd']
            assert res['cadd']['_license']
        if 'comsic' in res:
            assert '_license' in res['cosmic']
            assert res['cosmic']['_license']
        if 'dbsnp' in res:
            assert '_license' in res['dbsnp']
            assert res['dbsnp']['_license']
        if 'snpeff' in res:
            assert '_license' in res['snpeff']
            assert res['snpeff']['_license']

    def test_jsonld(self):
        res = self.request('variant/chr11:g.66397320A>G?jsonld=true').json()
        assert '@context' in res
        assert '@id' in res

        # Check some subfields - INVALIDATED BY NEW JSON-LD STRUCTURE
        #assert 'snpeff' in res and '@context' in res['snpeff']

        #assert 'ann' in res['snpeff'] and '@context' in res['snpeff']['ann'][0]

        # Check a post with jsonld
        res = self.request(
            "variant", method='POST',
            data={'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'jsonld': 'true'}).json()
        for r in res:
            assert '@context' in r
            assert '@id' in r

        # Check a query get with jsonld
        res = self.request('query?q=_exists_:clinvar&fields=clinvar&size=1&jsonld=true').json()

        assert '@context' in res['hits'][0]
        assert '@id' in res['hits'][0]

        # subfields
        #assert 'clinvar' in res['hits'][0] and '@context' in res['hits'][0]['clinvar']
        # TODO: fix test
        #assert 'gene' in res['hits'][0]['clinvar'] and '@context' in res['hits'][0]['clinvar']['gene']

        # Check query post with jsonld
        res = self.request("query", method='POST', data={'q': 'rs58991260,rs2500',
                                                              'scopes': 'dbsnp.rsid',
                                                              'jsonld': 'true'}).json()

        assert len(res) == 2
        assert '@context' in res[0] and '@context' in res[1]
        assert '@id' in res[0] and '@id' in res[1]
        #assert 'snpeff' in res[1] and '@context' in res[1]['snpeff']
        #assert 'ann' in res[1]['snpeff'] and '@context' in res[1]['snpeff']['ann'][0]

    def test_genome_assembly(self):
        res = self.request(
            'query?q=clinvar.ref:C%20AND%20chr11:56319006%20AND%20clinvar.alt:A&assembly=hg38').json()
        eq_(res["hits"][0]["_id"], "chr11:g.56319006C>A")

    def test_HGVS_redirect(self):
        res = self.request('variant/chr11:66397320A>G').json()
        res2 = self.request('variant/chr11:g66397320A>G').json()
        res3 = self.request('variant/chr11:.66397320A>G').json()
        res4 = self.request('variant/chr11:g.66397320A>G').json()

        eq_(res, res2)
        eq_(res2, res3)
        eq_(res3, res4)
        eq_(res["_id"], 'chr11:g.66397320A>G')

    def test_status_endpoint(self):
        self.request(self.host + '/status')
        # (testing failing status would require actually loading tornado app from there
        #  and deal with config params...)


if __name__ == '__main__':
    print()
    print('MyVariant Remote Test:', MyVariantRemoteTest.host)
    print('-'*70)
    runmodule(argv=['', '--logging-level=INFO', '-v'])
