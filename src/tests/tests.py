# -*- coding: utf-8 -*-
'''
Nose tests
Need to run under src folder as:

    nosetests tests.tests
    nosetests tests.tests -vv

    # to run a single test
    nosetests tests.tests:MyVariantTestTornadoClient.test_status_endpoint -vv

    # to run using an alternative myvariant api server
    MV_HOST="http://localhost:9000";nosetests tests.tests.MyVariantTest -vv

'''
import httplib2
import sys
import os
from nose.tools import ok_, eq_

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from .variant_list import VARIANT_POST_LIST
from biothings.tests.test_helper import BiothingTestHelperMixin, TornadoRequestHelper
from www.settings import MyVariantWebSettings


class MyVariantTest(BiothingTestHelperMixin):

    host = os.getenv("MV_HOST", "")
    host = host.rstrip('/')
    api = host + '/v1'
    if host:
        sys.stderr.write("Testing on host: {}...\n".format(api))
    else:
        sys.stderr.write("Testing on build-in server: {}...\n".format(api))
    h = httplib2.Http()

    def test_variant_object(self):
        #test all fields are loaded in variant objects
        res = self.json_ok(self.get_ok(self.api + '/variant/chr1:g.218631822G>A'))
        attr_li = ['_id']
        for attr in attr_li:
            assert res.get(attr, None) is not None, 'Missing field "{}" in variant "chr1:g.218631822G>A"'.format(attr)

        # test for specific databases

    def has_hits(self, q, morethan=0):
        d = self.json_ok(self.get_ok(self.api + '/query?q='+q))
        ok_(d.get('total', 0) > morethan and len(d.get('hits', [])) > 0)
        ok_('_id' in d['hits'][0])

    def test_query(self):
        #public query self.api at /query via get
        self.has_hits('rs58991260')
        self.has_hits('rcv000149017')
        self.has_hits('RCV000149017')
        self.has_hits('BTK', morethan=8000)

        self.has_hits('chr1:69000-70000', morethan=2000)
        self.has_hits('dbsnp.vartype:snp')
        # Too slow
        ##self.has_hits('_exists_:dbnsfp')
        self.has_hits('dbnsfp.genename:BTK', morethan=5000)
        self.has_hits('snpeff.ann.genename:BTK', morethan=8000)
        self.has_hits('_exists_:wellderly%20AND%20cadd.polyphen.cat:possibly_damaging&fields=wellderly,cadd.polyphen')

        con = self.get_ok(self.api + '/query?q=rs58991260&callback=mycallback')
        ok_(con.startswith('mycallback('.encode('utf-8')))

        # testing non-ascii character
        res = self.json_ok(self.get_ok(self.api + '/query?q=54097\xef\xbf\xbd\xef\xbf\xbdmouse'))
        eq_(res['hits'], [])

        res = self.json_ok(self.get_ok(self.api + '/query'), checkerror=False)
        assert 'error' in res

    def test_query_post(self):
        #/query via post
        self.json_ok(self.post_ok(self.api + '/query', {'q': 'rs58991260'}))

        res = self.json_ok(self.post_ok(self.api + '/query', {'q': 'rs58991260',
                                                              'scopes': 'dbsnp.rsid'}))
        eq_(len(res), 1)
        eq_(res[0]['_id'], 'chr1:g.218631822G>A')

        res = self.json_ok(self.post_ok(self.api + '/query', {'q': 'rs58991260,rs2500',
                                                              'scopes': 'dbsnp.rsid'}))
        eq_(len(res), 2)
        eq_(res[0]['_id'], 'chr1:g.218631822G>A')
        eq_(res[1]['_id'], 'chr11:g.66397320A>G')

        res = self.json_ok(self.post_ok(self.api + '/query', {'q': 'rs58991260',
                                                              'scopes': 'dbsnp.rsid',
                                                              'fields': 'dbsnp.chrom,dbsnp.alleles'}))
        assert len(res) == 1, (res, len(res))
        res = self.json_ok(self.post_ok(self.api + '/query', {}), checkerror=False)
        assert 'error' in res, res

        # TODO fix this test query
        #res = self.json_ok(self.post_ok(self.api + '/query', {'q': '[rs58991260, "chr11:66397000-66398000"]',
        #                                       'scopes': 'dbsnp.rsid'}))
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

        res = self.json_ok(self.get_ok(self.api + '/query?q=t*'))
        eq_(len(res['hits']), 10)    # default
        res = self.json_ok(self.get_ok(self.api + '/query?q=t*&size=1000'))
        eq_(len(res['hits']), 1000)
        res = self.json_ok(self.get_ok(self.api + '/query?q=t*&size=1001'))
        eq_(len(res['hits']), 1000)
        res = self.json_ok(self.get_ok(self.api + '/query?q=t*&size=2000'))
        eq_(len(res['hits']), 1000)

    def test_variant(self):
        # TODO
        res = self.json_ok(self.get_ok(self.api + '/variant/chr16:g.28883241A>G'))
        eq_(res['_id'], "chr16:g.28883241A>G")

        res = self.json_ok(self.get_ok(self.api + '/variant/chr1:g.35367G>A'))
        eq_(res['_id'], "chr1:g.35367G>A")

        res = self.json_ok(self.get_ok(self.api + '/variant/chr7:g.55241707G>T'))
        eq_(res['_id'], "chr7:g.55241707G>T")

        # testing non-ascii character
        self.get_404(self.api + '/variant/' + 'chr7:g.55241707G>T\xef\xbf\xbd\xef\xbf\xbdmouse')

        # testing filtering parameters
        res = self.json_ok(self.get_ok(self.api + '/variant/chr16:g.28883241A>G?fields=dbsnp,dbnsfp,cadd'))
        eq_(set(res), set(['_id', '_version', 'dbnsfp', 'cadd', 'dbsnp']))
        res = self.json_ok(self.get_ok(self.api + '/variant/chr16:g.28883241A>G?fields=wellderly'))
        eq_(set(res), set(['_id', '_version', 'wellderly']))
        res = self.json_ok(self.get_ok(self.api + '/variant/chr9:g.107620835G>A?fields=dbsnp'))
        eq_(set(res), set(['_id', '_version', 'dbsnp']))
        res = self.json_ok(self.get_ok(self.api + '/variant/chr1:g.31349647C>T?fields=dbnsfp.clinvar,dbsnp.gmaf,clinvar.hgvs.coding'))
        eq_(set(res), set(['_id', '_version', 'dbsnp', 'clinvar']))

        self.get_404(self.api + '/variant')
        self.get_404(self.api + '/variant/')

    def test_variant_post(self):
        res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': 'chr16:g.28883241A>G'}))
        eq_(len(res), 1)
        eq_(res[0]['_id'], "chr16:g.28883241A>G")

        res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G'}))
        eq_(len(res), 2)
        eq_(res[0]['_id'], 'chr16:g.28883241A>G')
        eq_(res[1]['_id'], 'chr11:g.66397320A>G')

        res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'fields': 'dbsnp'}))
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', 'query', 'dbsnp']))

        # TODO redo this test, doesn't test much really....
        res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': 'chr16:g.28883241A>G,chr11:g.66397320A>G', 'filter': 'dbsnp.chrom'}))
        eq_(len(res), 2)
        for _g in res:
            eq_(set(_g), set(['_id', 'query', 'dbsnp']))

        # Test a large variant post
        # # too slow
        # res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': VARIANT_POST_LIST}))
        # eq_(len(res), 999)

    def test_metadata(self):
        self.get_ok(self.api + '/metadata')

    def test_query_facets(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=cadd.gene.gene_id:ENSG00000113368&facets=cadd.polyphen.cat&size=0'))
        assert 'facets' in res and 'cadd.polyphen.cat' in res['facets']

    def test_unicode(self):
        s = '基因'

        self.get_404(self.api + '/variant/' + s)

        res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': s}))
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)
        res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': 'rs2500, ' + s}))
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

        res = self.json_ok(self.get_ok(self.api + '/query?q=' + s))
        eq_(res['hits'], [])

        res = self.json_ok(self.post_ok(self.api + '/query', {"q": s, "scopes": 'dbsnp'}))
        eq_(res[0]['notfound'], True)
        eq_(len(res), 1)

        res = self.json_ok(self.post_ok(self.api + '/query', {"q": 'rs2500+' + s}))
        eq_(res[1]['notfound'], True)
        eq_(len(res), 2)

    def test_get_fields(self):
        res = self.json_ok(self.get_ok(self.api + '/metadata/fields'))
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
        res = self.json_ok(self.get_ok(self.api + '/query?q=' + q))
        assert '_scroll_id' in res

        # get one set of results
        res2 = self.json_ok(self.get_ok(self.api + '/query?scroll_id=' + res['_scroll_id']))
        assert 'hits' in res2
        ok_(len(res2['hits']) == 1000)

    def test_msgpack(self):
        res = self.json_ok(self.get_ok(self.api + '/variant/chr11:g.66397320A>G'))
        res2 = self.msgpack_ok(self.get_ok(self.api + '/variant/chr11:g.66397320A>G?msgpack=true'))
        ok_(res, res2)

        res = self.json_ok(self.get_ok(self.api + '/query?q=rs2500'))
        res2 = self.msgpack_ok(self.get_ok(self.api + '/query?q=rs2500&msgpack=true'))
        ok_(res, res2)

        res = self.json_ok(self.get_ok(self.api + '/metadata'))
        res2 = self.msgpack_ok(self.get_ok(self.api + '/metadata?msgpack=true'))
        ok_(res, res2)

    # Too slow
    def test_licenses(self):
        # cadd license
        res = self.json_ok(self.get_ok(self.api + '/variant/chr17:g.61949543G>A'))
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
        res = self.json_ok(self.get_ok(self.api + '/variant/chr11:g.66397320A>G?jsonld=true'))
        assert '@context' in res
        assert '@id' in res

        # Check some subfields - INVALIDATED BY NEW JSON-LD STRUCTURE
        #assert 'snpeff' in res and '@context' in res['snpeff']

        #assert 'ann' in res['snpeff'] and '@context' in res['snpeff']['ann'][0]

        # Check a post with jsonld
        res = self.json_ok(self.post_ok(self.api + '/variant', {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'jsonld': 'true'}))
        for r in res:
            assert '@context' in r
            assert '@id' in r

        # Check a query get with jsonld
        res = self.json_ok(self.get_ok(self.api + '/query?q=_exists_:clinvar&fields=clinvar&size=1&jsonld=true'))

        assert '@context' in res['hits'][0]
        assert '@id' in res['hits'][0]

        # subfields
        #assert 'clinvar' in res['hits'][0] and '@context' in res['hits'][0]['clinvar']
        # TODO: fix test
        #assert 'gene' in res['hits'][0]['clinvar'] and '@context' in res['hits'][0]['clinvar']['gene']

        # Check query post with jsonld
        res = self.json_ok(self.post_ok(self.api + '/query', {'q': 'rs58991260,rs2500',
                                                              'scopes': 'dbsnp.rsid',
                                                              'jsonld': 'true'}))

        assert len(res) == 2
        assert '@context' in res[0] and '@context' in res[1]
        assert '@id' in res[0] and '@id' in res[1]
        #assert 'snpeff' in res[1] and '@context' in res[1]['snpeff']
        #assert 'ann' in res[1]['snpeff'] and '@context' in res[1]['snpeff']['ann'][0]

    def test_genome_assembly(self):
        res = self.json_ok(self.get_ok(self.api + '/query?q=clinvar.ref:C%20AND%20chr11:56319006%20AND%20clinvar.alt:A&assembly=hg38'))
        eq_(res["hits"][0]["_id"], "chr11:g.56319006C>A")

    def test_HGVS_redirect(self):
        res = self.json_ok(self.get_ok(self.api + '/variant/chr11:66397320A>G'))
        res2 = self.json_ok(self.get_ok(self.api + '/variant/chr11:g66397320A>G'))
        res3 = self.json_ok(self.get_ok(self.api + '/variant/chr11:.66397320A>G'))
        res4 = self.json_ok(self.get_ok(self.api + '/variant/chr11:g.66397320A>G'))

        eq_(res, res2)
        eq_(res2, res3)
        eq_(res3, res4)
        eq_(res["_id"], 'chr11:g.66397320A>G')

    def test_status_endpoint(self):
        self.get_ok(self.host + '/status')
        # (testing failing status would require actually loading tornado app from there
        #  and deal with config params...)


class MyVariantTestTornadoClient(AsyncHTTPTestCase, MyVariantTest):
    __test__ = True

    def __init__(self, methodName='runTest', **kwargs):
        super(AsyncHTTPTestCase, self).__init__(methodName, **kwargs)
        self.h = TornadoRequestHelper(self)
        self._settings = MyVariantWebSettings(config='config')

    def get_app(self):
        return Application(self._settings.generate_app_list())
