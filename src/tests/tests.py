# -*- coding: utf-8 -*-
'''
Nose tests
run as "nosetests tests"
    or "nosetests tests:test_main"
'''
import httplib2
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
import json
import sys
import os
from nose.tools import ok_, eq_
import variant_list

try:
    import msgpack
except ImportError:
    sys.stderr.write("Warning: msgpack is not available.")

host = os.getenv("MV_HOST")
if not host:
    #host = 'http://localhost:8000'
    #host = 'http://dev.myvariant.info:8000'
    host = 'http://myvariant.info'

api = host + '/v1'
sys.stderr.write('URL base: {}\n'.format(api))

h = httplib2.Http()
#h = httplib2.Http(disable_ssl_certificate_validation=True)
_d = json.loads    # shorthand for json decode
_e = json.dumps    # shorthand for json encode


#############################################################
# Hepler functions                                          #
#############################################################
def encode_dict(d):
    '''urllib.urlencode (python 2.x) cannot take unicode string.
       encode as utf-8 first to get it around.
    '''
    return dict([(key, val.encode('utf-8')) for key, val in d.items()
                 if isinstance(val, str)])


def truncate(s, limit):
    '''truncate a string.'''
    if len(s) <= limit:
        return s
    else:
        return s[:limit] + '...'


def json_ok(s, checkerror=True):
    d = _d(s.decode('utf-8'))
    if checkerror:
        ok_(not (isinstance(d, dict) and 'error' in d), truncate(str(d), 100))
    return d


def msgpack_ok(b, checkerror=True):
    d = msgpack.unpackb(b)
    if checkerror:
        ok_(not (isinstance(d, dict) and 'error' in d), truncate(str(d), 100))
    return d


def get_ok(url):
    res, con = h.request(url)
    eq_(res.status, 200)
    return con


def get_404(url):
    res, con = h.request(url)
    eq_(res.status, 404)


def get_405(url):
    res, con = h.request(url)
    eq_(res.status, 405)


def head_ok(url):
    res, con = h.request(url, 'HEAD')
    eq_(res.status, 200)


def post_ok(url, params):
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    res, con = h.request(url, 'POST', urlencode(encode_dict(params)), headers=headers)
    eq_(res.status, 200)
    return con


def setup_func():
    print(('Testing "%s"...' % host))


def teardown_func():
    pass


#############################################################
# Test functions                                            #
#############################################################
#@with_setup(setup_func, teardown_func)
def test_main():
    #/
    get_ok(host)


def test_variant_object():
    #test all fields are loaded in variant objects
    res = json_ok(get_ok(api + '/variant/chr1:g.218631822G>A'))
    attr_li = ['_id']
    for attr in attr_li:
        assert res.get(attr, None) is not None, 'Missing field "{}" in variant "chr1:g.218631822G>A"'.format(attr)

    # test for specific databases


def has_hits(q):
    d = json_ok(get_ok(api + '/query?q='+q))
    ok_(d.get('total', 0) > 0 and len(d.get('hits', [])) > 0)


def test_query():
    #public query api at /query via get
    has_hits('rs58991260')
    has_hits('chr1:69000-70000')
    has_hits('dbsnp.vartype:snp')
    has_hits('_exists_:dbnsfp')
    has_hits('dbnsfp.genename:BTK')
    has_hits('_exists_:wellderly%20AND%20cadd.polyphen.cat:possibly_damaging&fields=wellderly,cadd.polyphen')

    con = get_ok(api + '/query?q=rs58991260&callback=mycallback')
    ok_(con.startswith('mycallback('.encode('utf-8')))

    # testing non-ascii character
    res = json_ok(get_ok(api + '/query?q=54097\xef\xbf\xbd\xef\xbf\xbdmouse'))
    eq_(res['hits'], [])

    res = json_ok(get_ok(api + '/query'), checkerror=False)
    assert 'error' in res


def test_query_post():
    #/query via post
    json_ok(post_ok(api + '/query', {'q': 'rs58991260'}))

    res = json_ok(post_ok(api + '/query', {'q': 'rs58991260',
                                           'scopes': 'dbsnp.rsid'}))
    eq_(len(res), 1)
    eq_(res[0]['_id'], 'chr1:g.218631822G>A')

    res = json_ok(post_ok(api + '/query', {'q': 'rs58991260,rs2500',
                                           'scopes': 'dbsnp.rsid'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], 'chr1:g.218631822G>A')
    eq_(res[1]['_id'], 'chr11:g.66397320A>G')

    res = json_ok(post_ok(api + '/query', {'q': 'rs58991260',
                                           'scopes': 'dbsnp.rsid',
                                           'fields': 'dbsnp.chrom,dbsnp.alleles'}))
    assert len(res) == 1, (res, len(res))
    res = json_ok(post_ok(api + '/query', {}), checkerror=False)
    assert 'error' in res, res

    # TODO fix this test query
    #res = json_ok(post_ok(api + '/query', {'q': '[rs58991260, "chr11:66397000-66398000"]',
    #                                       'scopes': 'dbsnp.rsid'}))
    #eq_(len(res), 2)
    #eq_(res[0]['_id'], 'chr1:g.218631822G>A')
    #eq_(res[1]['_id'], 'chr11:g.66397320A>G')


def test_query_interval():
    res = json_ok(get_ok(api + '/query?q=chr1:10000-100000'))
    ok_(len(res['hits']) > 1)
    ok_('_id' in res['hits'][0])


def test_query_size():
    # TODO
    pass


def test_variant():
    # TODO
    res = json_ok(get_ok(api + '/variant/chr16:g.28883241A>G'))
    eq_(res['_id'], "chr16:g.28883241A>G")

    res = json_ok(get_ok(api + '/variant/chr1:g.35367G>A'))
    eq_(res['_id'], "chr1:g.35367G>A")

    res = json_ok(get_ok(api + '/variant/chr7:g.55241707G>T'))
    eq_(res['_id'], "chr7:g.55241707G>T")

    # testing non-ascii character
    get_404(api + '/variant/' + 'chr7:g.55241707G>T\xef\xbf\xbd\xef\xbf\xbdmouse')

    # testing filtering parameters
    res = json_ok(get_ok(api + '/variant/chr16:g.28883241A>G?fields=dbsnp,dbnsfp,cadd'))
    eq_(set(res), set(['_id', '_version', 'dbnsfp', 'cadd', 'dbsnp']))
    res = json_ok(get_ok(api + '/variant/chr16:g.28883241A>G?fields=wellderly'))
    eq_(set(res), set(['_id', '_version', 'wellderly']))
    res = json_ok(get_ok(api + '/variant/chr9:g.107620835G>A?fields=dbsnp'))
    eq_(set(res), set(['_id', '_version', 'dbsnp']))
    res = json_ok(get_ok(api + '/variant/chr1:g.31349647C>T?fields=dbnsfp.clinvar,dbsnp.gmaf,clinvar.hgvs.coding'))
    eq_(set(res), set(['_id', '_version', 'dbsnp', 'dbnsfp', 'clinvar']))

    get_404(api + '/variant')
    get_404(api + '/variant/')


def test_variant_post():
    res = json_ok(post_ok(api + '/variant', {'ids': 'chr16:g.28883241A>G'}))
    eq_(len(res), 1)
    eq_(res[0]['_id'], "chr16:g.28883241A>G")

    res = json_ok(post_ok(api + '/variant', {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], 'chr16:g.28883241A>G')
    eq_(res[1]['_id'], 'chr11:g.66397320A>G')

    res = json_ok(post_ok(api + '/variant', {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'fields': 'dbsnp'}))
    eq_(len(res), 2)
    for _g in res:
        eq_(set(_g), set(['_id', '_score', 'query', 'dbsnp']))

    # TODO redo this test, doesn't test much really....
    res = json_ok(post_ok(api + '/variant', {'ids': 'chr16:g.28883241A>G,chr11:g.66397320A>G', 'filter': 'dbsnp.chrom'}))
    eq_(len(res), 2)
    for _g in res:
        eq_(set(_g), set(['_id', '_score', 'query', 'dbsnp']))

    # Test a large variant post
    res = json_ok(post_ok(api + '/variant', {'ids': variant_list.VARIANT_POST_LIST}))
    eq_(len(res), 999)


def test_metadata():
    #get_ok(host + '/metadata')
    get_ok(api + '/metadata')


def test_query_facets():
    pass


def test_unicode():
    s = '基因'

    get_404(api + '/gene/' + s)

    res = json_ok(post_ok(api + '/variant', {'ids': s}))
    eq_(res[0]['notfound'], True)
    eq_(len(res), 1)
    res = json_ok(post_ok(api + '/variant', {'ids': 'rs2500, ' + s}))
    eq_(res[1]['notfound'], True)
    eq_(len(res), 2)

    res = json_ok(get_ok(api + '/query?q=' + s))
    eq_(res['hits'], [])

    res = json_ok(post_ok(api + '/query', {"q": s, "scopes": 'dbsnp'}))
    eq_(res[0]['notfound'], True)
    eq_(len(res), 1)

    res = json_ok(post_ok(api + '/query', {"q": 'rs2500+' + s}))
    eq_(res[1]['notfound'], True)
    eq_(len(res), 2)


def test_get_fields():
    res = json_ok(get_ok(api + '/metadata/fields'))
    # Check to see if there are enough keys
    ok_(len(res) > 480)

    # Check some specific keys
    assert 'cadd' in res
    assert 'dbnsfp' in res
    assert 'dbsnp' in res
    assert 'wellderly' in res
    assert 'clinvar' in res


def test_fetch_all():
    res = json_ok(get_ok(api + '/query?q=_exists_:wellderly%20AND%20cadd.polyphen.cat:possibly_damaging&fields=wellderly,cadd.polyphen&fetch_all=TRUE'))
    assert '_scroll_id' in res

    # get one set of results
    res2 = json_ok(get_ok(api + '/query?scroll_id=' + res['_scroll_id']))
    assert 'hits' in res2
    ok_(len(res2['hits']) == 1000)


def test_msgpack():
    res = json_ok(get_ok(api + '/variant/chr11:g.66397320A>G'))
    res2 = msgpack_ok(get_ok(api + '/variant/chr11:g.66397320A>G?msgpack=true'))
    ok_(res, res2)

    res = json_ok(get_ok(api + '/query?q=rs2500'))
    res2 = msgpack_ok(get_ok(api + '/query?q=rs2500&msgpack=true'))
    ok_(res, res2)

    res = json_ok(get_ok(api + '/metadata'))
    res2 = msgpack_ok(get_ok(api + '/metadata?msgpack=true'))
    ok_(res, res2)


def test_licenses():
    # cadd license
    res = json_ok(get_ok(api + '/query?q=_exists_:cadd&size=1&fields=cadd'))
    assert '_license' in res['hits'][0]['cadd']
    assert res['hits'][0]['cadd']['_license']


def test_jsonld():
    res = json_ok(get_ok(api + '/variant/chr11:g.66397320A>G?jsonld=true'))
    assert '@context' in res

    res = json_ok(post_ok(api + '/variant', {'ids': 'chr16:g.28883241A>G, chr11:g.66397320A>G', 'jsonld': 'true'}))
    for r in res:
        assert '@context' in r
