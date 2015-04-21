# -*- coding: utf-8 -*-
'''
Nose tests
run as "nosetests tests"
    or "nosetests tests:test_main"
'''
import httplib2
import urllib.request, urllib.parse, urllib.error
import json
import sys
from nose.tools import ok_, eq_

try:
    import msgpack
except ImportError:
    sys.stderr.write("Warning: msgpack is not available.")


#host = 'http://localhost:9000'
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
    d = _d(s)
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
    res, con = h.request(url, 'POST', urllib.parse.urlencode(encode_dict(params)), headers=headers)
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
    res = json_ok(get_ok(api+ '/variant/'))
    
    attr_li = ['_id']
    for attr in attr_li:
        assert res.get(attr, None) is not None, 'Missing field "{}" in gene "1017"'.format(attr)
        
    # test for specific databases


def has_hits(q):
    d = json_ok(get_ok(api + '/query?q='+q))
    ok_(d.get('total', 0) > 0 and len(d.get('hits', [])) > 0)


def test_query():
    #public query api at /query via get
    # json_ok(get_ok(api + '/query?q=cdk2'))
    # json_ok(get_ok(api + '/query?q=GO:0004693'))
    # json_ok(get_ok(api + '/query?q=211803_at'))
    has_hits('rs58991260')
    has_hits('chr1:69000-70000')
    has_hits('dbsnp.vartype:snp')

    con = get_ok(api + '/query?q=rs58991260&callback=mycallback')
    ok_(con.startswith('mycallback('))

    # testing non-ascii character
    res = json_ok(get_ok(api + '/query?q=54097\xef\xbf\xbd\xef\xbf\xbdmouse'))
    eq_(res['hits'], [])

    res = json_ok(get_ok(api + '/query'), checkerror=False)
    assert 'error' in res

    res = json_ok(get_ok(api + '/query?q=tRNA:Y1:85Ae'), checkerror=False)
    assert 'error' in res


def test_query_post():
    #/query via post
    json_ok(post_ok(api + '/query', {'q': '1017'}))

    res = json_ok(post_ok(api + '/query', {'q': '1017',
                                           'scopes': 'entrezgene'}))
    eq_(len(res), 1)
    eq_(res[0]['_id'], '1017')

    res = json_ok(post_ok(api + '/query', {'q': '211803_at,1018',
                                           'scopes': 'reporter,entrezgene'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], '1017')
    eq_(res[1]['_id'], '1018')

    res = json_ok(post_ok(api + '/query', {'q': 'CDK2',
                                           'species': 'human,10090,frog,pig',
                                           'scopes': 'symbol',
                                           'fields': 'name,symbol'}))
    assert len(res) == 4, (res, len(res))
    res = json_ok(post_ok(api + '/query', {}), checkerror=False)
    assert 'error' in res, res

    res = json_ok(post_ok(api + '/query', {'q': '[1017, "1018"]',
                                           'scopes': 'entrezgene',
                                           'jsoninput': 'true'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], '1017')
    eq_(res[1]['_id'], '1018')


def test_query_interval():
    res = json_ok(get_ok(api + '/query?q=chr1:1000-100000&species=human'))
    ok_(len(res['hits']) > 1)
    ok_('_id' in res['hits'][0])


def test_query_size():
    res = json_ok(get_ok(api + '/query?q=cdk?'))
    eq_(len(res['hits']), 10)  # default is 10
    ok_(res['total'] > 10)

    res = json_ok(get_ok(api + '/query?q=cdk?&size=0'))
    eq_(len(res['hits']), 0)

    res = json_ok(get_ok(api + '/query?q=cdk?&limit=20'))
    eq_(len(res['hits']), 20)

    res1 = json_ok(get_ok(api + '/query?q=cdk?&from=0&size=20'))
    #res2 = json_ok(get_ok(api + '/query?q=cdk*&from=0&size=20'))
    res = json_ok(get_ok(api + '/query?q=cdk?&skip=10&size=20'))
    #eq_([x['_id'] for x in res1['hits']],[x['_id'] for x in res2['hits']])
    eq_(len(res['hits']), 20)
    #print res1['hits'].index(res['hits'][0])
    #print [x['_id'] for x in res1['hits']]
    eq_(res['hits'][0], res1['hits'][10])

    #assert 1==0
    res = json_ok(get_ok(api + '/query?q=cdk?&size=1a'), checkerror=False)  # invalid size parameter
    assert 'error' in res


def test_gene():
    res = json_ok(get_ok(api + '/gene/1017'))
    eq_(res['entrezgene'], 1017)

    # testing non-ascii character
    get_404(api + '/gene/' + '54097\xef\xbf\xbd\xef\xbf\xbdmouse')

    # commented out this test, as no more
    #allow dot in the geneid
    #res = json_ok(get_ok(api + '/gene/Y105C5B.255'))

    # testing filtering parameters
    res = json_ok(get_ok(api + '/gene/1017?fields=symbol,name,entrezgene'))
    eq_(set(res), set(['_id', 'symbol', 'name', 'entrezgene']))
    res = json_ok(get_ok(api + '/gene/1017?filter=symbol,go.MF'))
    eq_(set(res), set(['_id', 'symbol', 'go.MF']))
    #eq_(res['go'].keys(), ['MF'])

    get_404(api + '/gene')
    get_404(api + '/gene/')

    #res = json_ok(get_ok(api + '/boc/bgps/gene/1017'))
    #ok_('SpeciesList' in res)


def test_gene_post():
    res = json_ok(post_ok(api + '/gene', {'ids': '1017'}))
    eq_(len(res), 1)
    eq_(res[0]['entrezgene'], 1017)

    res = json_ok(post_ok(api + '/gene', {'ids': '1017, 1018'}))
    eq_(len(res), 2)
    eq_(res[0]['_id'], '1017')
    eq_(res[1]['_id'], '1018')

    res = json_ok(post_ok(api + '/gene', {'ids': '1017,1018', 'fields': 'symbol,name,entrezgene'}))
    eq_(len(res), 2)
    for _g in res:
        eq_(set(_g), set(['_id', 'query', 'symbol', 'name', 'entrezgene']))

    res = json_ok(post_ok(api + '/gene', {'ids': '1017,1018', 'filter': 'symbol,go.MF'}))
    eq_(len(res), 2)
    for _g in res:
        eq_(set(_g), set(['_id', 'query', 'symbol', 'go.MF']))


def test_metadata():
    get_ok(host + '/metadata')
    get_ok(api + '/metadata')


def test_query_facets():
    res = json_ok(get_ok(api + '/query?q=cdk?&facets=taxid'))
    ok_('facets' in res)
    ok_('taxid' in res['facets'])
    eq_(res['facets']['taxid']['total'], res['total'])
    eq_(res['facets']['taxid']['other'], 0)
    eq_(res['facets']['taxid']['missing'], 0)

    res2 = json_ok(get_ok(api + '/query?q=cdk?&facets=taxid&species_facet_filter=human'))
    eq_(res2['facets']['taxid']['total'], res['total'])
    eq_(res2['facets']['taxid'], res['facets']['taxid'])
    eq_([x["count"] for x in res2['facets']['taxid']['terms'] if x["term"] == 9606][0], res2['total'])


def test_query_userfilter():
    res1 = json_ok(get_ok(api + '/query?q=cdk'))
    res2 = json_ok(get_ok(api + '/query?q=cdk&userfilter=bgood_cure_griffith'))
    ok_(res1['total'] > res2['total'])

    res2 = json_ok(get_ok(api + '/query?q=cdk&userfilter=aaaa'))   # nonexisting user filter gets ignored.
    eq_(res1['total'], res2['total'])


def test_existsfilter():
    res1 = json_ok(get_ok(api + '/query?q=cdk'))
    res2 = json_ok(get_ok(api + '/query?q=cdk&exists=pharmgkb'))
    ok_(res1['total'] > res2['total'])
    res3 = json_ok(get_ok(api + '/query?q=cdk&exists=pharmgkb,pdb'))
    ok_(res2['total'] > res3['total'])


def test_missingfilter():
    res1 = json_ok(get_ok(api + '/query?q=cdk'))
    res2 = json_ok(get_ok(api + '/query?q=cdk&missing=pdb'))
    ok_(res1['total'] > res2['total'])
    res3 = json_ok(get_ok(api + '/query?q=cdk&missing=pdb,MIM'))
    ok_(res2['total'] > res3['total'])


def test_unicode():
    s = '基因'

    get_404(api + '/gene/' + s)

    res = json_ok(post_ok(api + '/gene', {'ids': s}))
    eq_(res[0]['notfound'], True)
    eq_(len(res), 1)
    res = json_ok(post_ok(api + '/gene', {'ids': '1017, ' + s}))
    eq_(res[1]['notfound'], True)
    eq_(len(res), 2)

    res = json_ok(get_ok(api + '/query?q=' + s))
    eq_(res['hits'], [])

    res = json_ok(post_ok(api + '/query', {"q": s, "scopes": 'symbol'}))
    eq_(res[0]['notfound'], True)
    eq_(len(res), 1)

    res = json_ok(post_ok(api + '/query', {"q": 'cdk2+' + s}))
    eq_(res[1]['notfound'], True)
    eq_(len(res), 2)


def test_msgpack():
    res = json_ok(get_ok(api + '/variant/1017'))
    res2 = msgpack_ok(get_ok(api + '/variant/1017?msgpack=true'))
    ok_(res, res2)

    res = json_ok(get_ok(api + '/variant/?q=cdk'))
    res2 = msgpack_ok(get_ok(api + '/variant/?q=cdk&msgpack=true'))
    ok_(res, res2)

    res = json_ok(get_ok(api + '/metadata'))
    res2 = msgpack_ok(get_ok(api + '/metadata?msgpack=true'))
    ok_(res, res2)

