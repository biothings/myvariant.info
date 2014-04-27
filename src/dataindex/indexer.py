from __future__ import print_function
import logging
logging.basicConfig()
import json
import time

from elasticsearch import Elasticsearch
from .mapping import mapping


es = Elasticsearch()
es_host = 'localhost:9200'
index_name = 'myvariant_all'
doc_type = 'variant'


def timesofar(t0, clock=0):
    '''return the string(eg.'3m3.42s') for the passed real time/CPU time so far
       from given t0 (return from t0=time.time() for real time/
       t0=time.clock() for CPU time).'''
    if clock:
        t = time.clock() - t0
    else:
        t = time.time() - t0
    h = int(t / 3600)
    m = int((t % 3600) / 60)
    s = round((t % 3600) % 60, 2)
    t_str = ''
    if h != 0:
        t_str += '%sh' % h
    if m != 0:
        t_str += '%sm' % m
    t_str += '%ss' % s
    return t_str


def get_test_doc_li(n):
    import random
    out = []
    for i in range(n):
        out.append({
            '_id': 'chr1:g.{}A>C'.format(random.randint(1, 10000000)),
            'aaa': 'bbb'
            })
    return out


def doc_feeder(doc_li, step=1000):
    total = len(doc_li)
    for i in range(0, total, step):
        print('\t{}-{}...'.format(i, min(i+step, total)), end='')
        yield doc_li[i: i+step]
        print('Done.')


def create_index():
    es.indices.create(index=index_name, body=mapping)


def do_index(doc_li, step=1000, update=False):
    total = len(doc_li)
    for doc_batch in doc_feeder(doc_li, step=step):
        _li = []
        for doc in doc_batch:
            if update:
                _li.append({
                    "update": {
                        "_index": index_name,
                        "_type": doc_type,
                        "_id": doc['_id']
                    }
                    })
                _li.append({'doc': doc, 'doc_as_upsert': True})
            else:
                _li.append({
                    "index": {
                        "_index": index_name,
                        "_type": doc_type,
                        "_id": doc['_id']
                    }
                    })
                _li.append(doc)
        es.bulk(body=_li)


def index_dbsnp():
    total = 0
    t0 = time.time()
    with file('../../data/snp130_42514') as fp:
        for line in fp:
            doc_li = json.loads(line).values()
            out = []
            for doc in doc_li:
                _doc = {}
                _doc['dbsnp'] = doc
                _doc['_id'] = doc['_id']
                del _doc['dbsnp']['_id']
                out.append(_doc)
            print('>', len(out))
            total += len(out)
            do_index(out, step=10000)
    print(total, timesofar(t0))

def index_from_file(infile, node, test=True):
    t0 = time.time()
    with file(infile) as fp:
        doc_li = json.load(fp).values()
        out = []
        for doc in doc_li:
            _doc = {}
            _doc[node] = doc
            _doc['_id'] = doc['_id']
            del _doc[node]['_id']
            out.append(_doc)
        print('>', len(out))
        if not test:
            do_index(out, step=10000, update=True)
    print(len(out), timesofar(t0))
    if test:
        return out
