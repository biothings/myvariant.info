from __future__ import print_function
import logging
logging.basicConfig()

from elasticsearch import Elasticsearch
from .mapping import mapping


es = Elasticsearch()
es_host = 'localhost:9200'
index_name = 'myvariant_all'
doc_type = 'variant'


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


def do_index(doc_li, step=1000):
    total = len(doc_li)
    for doc_batch in doc_feeder(doc_li, step=step):
        _li = []
        for doc in doc_batch:
            _li.append({
                "index": {
                    "_index": index_name,
                    "_type": doc_type,
                    "_id": doc['_id']
                }
                })
            _li.append(doc)
        es.bulk(body=_li)


