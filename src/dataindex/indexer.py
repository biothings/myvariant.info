from __future__ import print_function
import logging
logging.basicConfig()
import json
import time

from .mapping import get_mapping
import config
import utils.es
import utils.mongo


es_host = config.ES_HOST
es = utils.es.get_es(es_host)
index_name = config.ES_INDEX_NAME
doc_type = config.ES_DOC_TYPE
logger = logging.getLogger()
logger.setLevel(logging.ERROR)


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


def docs_feeder2(infile):
    total = 0
    t0 = time.time()
    with open(infile) as fp:
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
            yield out
    print(total, timesofar(t0))


def doc_feeder(doc_li, step=1000, verbose=True):
    total = len(doc_li)
    for i in range(0, total, step):
        if verbose:
            print('\t{}-{}...'.format(i, min(i+step, total)), end='')
        yield doc_li[i: i+step]
        if verbose:
            print('Done.')


def verify_doc_li(doc_li, return_ids=False, step=10000):
    esi = utils.es.ESIndexer()
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    if return_ids:
        stats = {True: [], False: []}
    else:
        stats = {True: 0, False: 0}
    doc_cnt = len(doc_li)
    for i in range(0, doc_cnt, step):
        j = min(doc_cnt, i + step)
        print(i, '...', j)
        res = esi.mexists([doc['_id'] for doc in doc_li[i:j]])
        for _id, exists in res:
            if return_ids:
                stats[exists].append(_id)
            else:
                stats[exists] += 1
    logger.setLevel(logging.INFO)
    if return_ids:
        print({True: len(stats[True]), False: len(stats[False])})
    return stats


def verify_collection(collection, return_ids=False, step=10000):
    esi = utils.es.ESIndexer()
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    if return_ids:
        stats = {True: [], False: []}
    else:
        stats = {True: 0, False: 0}
    for doc_li in utils.mongo.doc_feeder(collection, step=step, fields={'_id': 1}, inbatch=True):
        res = esi.mexists([doc['_id'] for doc in doc_li])
        for _id, exists in res:
            if return_ids:
                stats[exists].append(_id)
            else:
                stats[exists] += 1
    logger.setLevel(logging.INFO)
    if return_ids:
        print({True: len(stats[True]), False: len(stats[False])})
    return stats


def create_index(index_name, mapping=None):
    body = {'settings': {'number_of_shards': 20}}
    mapping = mapping or get_mapping()
    mapping = {"mappings": mapping}
    body.update(mapping)
    es.indices.create(index=index_name, body=body)


def _index_doc_batch(doc_batch, index_name, doc_type, update=True, bulk_size=10000):
    _li = []
    cnt = 0
    for doc in doc_batch:
        if update:
            # _li.append({
            #     "update": {
            #         "_index": index_name,
            #         "_type": doc_type,
            #         "_id": doc['_id']
            #     }
            #     })
            # _li.append({'script': 'ctx._source.remove("cosmic")'})
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

        cnt += 1
        if cnt >= bulk_size:
            es.bulk(body=_li)
            _li = []

    if _li:
        es.bulk(body=_li)


def do_index(doc_li, index_name, doc_type, step=1000, update=True, verbose=True):
    for doc_batch in doc_feeder(doc_li, step=step, verbose=verbose):
        _index_doc_batch(doc_batch, index_name, doc_type, update=update)


def do_index_from_collection_0(collection, index_name, doc_type, skip, step=10000, update=True):
    from utils.mongo import doc_feeder

    for doc_batch in doc_feeder(collection, step=step, s=skip, inbatch=True):
        _index_doc_batch(doc_batch, index_name, doc_type, update=update)


def do_index_from_collection(collection, index_name, doc_type=None, skip=0, step=10000, update=True):
    esi = utils.es.ESIndexer(index=index_name, doc_type=doc_type, step=step)
    esi.s = skip
    esi.build_index(collection, verbose=True, query=None, bulk=True, update=update)


def index_dbsnp():
    '''deprecated'''
    total = 0
    t0 = time.time()
    with open('../../data/snp130_42514') as fp:
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


def index_cosmic():
    '''deprecated'''
    total = 0
    t0 = time.time()
    with open('../../data/cosmicsnps_42714_fix') as fp:
        for line in fp:
            doc_li = json.loads(line).values()
            out = []
            for doc in doc_li:
                _doc = {}
                _doc['cosmic'] = doc
                _doc['_id'] = doc['_id']
                del _doc['cosmic']['_id']
                out.append(_doc)
            print('>', len(out))
            total += len(out)
            do_index(out, step=10000, update=True)
    print(total, timesofar(t0))


def index_from_file(infile, node, test=True):
    t0 = time.time()
    with open(infile) as fp:
        doc_li = json.load(fp)
        if isinstance(doc_li, dict):
            doc_li = doc_li.values()
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


def index_dbnsfp(path, step=10000, test=True):
    from dataload.contrib import dbnsfp
    vdoc_generator = dbnsfp.load_data(path)
    vdoc_batch = []
    cnt = 0
    t0 = time.time()
    t1 = time.time()
    for vdoc in vdoc_generator:
        cnt += 1
        vdoc_batch.append(vdoc)
        if len(vdoc_batch) >= step:
            if not test:
                do_index(vdoc_batch, "myvariant_current_1", "variant", update=True, step=step, verbose=False)  # ###
            print(cnt, timesofar(t1))
            vdoc_batch = []
            t1 = time.time()

    if vdoc_batch:
        if not test:
            do_index(vdoc_batch, "myvariant_current_1", "variant", update=True, step=step, verbose=False)  # ###
    print(cnt, timesofar(t1))
    print("Finished! [Total time: {}]".format(timesofar(t0)))


def clone_index(createidx=False, test=True):
    if test:
        return
    from utils.es import ESIndexer
    from utils.common import iter_n

    new_idx = 'myvariant_current_3'
    step = 10000
    if createidx:
        from mapping import get_mapping
        m = get_mapping()
        body = {'settings': {'number_of_shards': 10}}    # ###
        es.indices.create(new_idx, body=body)
        es.indices.put_mapping(index=new_idx, doc_type='variant', body=m)
    # helpers.reindex(es, source_index='myvariant_all',
    #                 target_index= new_idx, chunk_size=10000)
    esi = ESIndexer()
    doc_iter = esi.doc_feeder(index='myvariant_all_1', doc_type='variant', step=step)

    for doc_batch in iter_n(doc_iter, step):
        do_index(doc_batch, index_name=new_idx, doc_type='variant', step=step, verbose=False, update=True)


def get_es_stats():
    cnt_li = []
    total = es.count(index=index_name, doc_type=doc_type)['count']
    cnt_li.append(('total', total))
    src_li = ['dbnsfp', 'dbsnp', 'clinvar', 'mutdb', 'gwassnps',
              'cosmic', 'docm', 'snpedia', 'emv']
    for src in src_li:
        body = {
            "query": {
                "constant_score": {
                    "filter": {
                        "exists": {
                            "field": src
                        }
                    }
                }
            }
        }
        cnt = es.count(index=index_name, doc_type=doc_type, body=body)['count']
        cnt_li.append((src, cnt))
    return cnt_li
