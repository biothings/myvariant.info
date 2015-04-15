from __future__ import print_function
import time
try:
    from mongokit import Connection
except:
    from pymongo import MongoClient as Connection
from config import (DATA_SRC_SERVER, DATA_SRC_PORT, DATA_SRC_DATABASE,
                    DATA_SERVER_USERNAME, DATA_SERVER_PASSWORD)
from utils.common import timesofar, ask


def get_src_db(conn=None):
    uri = "mongodb://{}:{}@{}:{}/{}".format(DATA_SERVER_USERNAME,
                                            DATA_SERVER_PASSWORD,
                                            DATA_SRC_SERVER,
                                            DATA_SRC_PORT,
                                            DATA_SRC_DATABASE)
    conn = Connection(uri)
    return conn[DATA_SRC_DATABASE]


def doc_feeder(collection, step=1000, s=None, e=None, inbatch=False, query=None, batch_callback=None, fields=None):
    '''A iterator for returning docs in a collection, with batch query.
       additional filter query can be passed via "query", e.g.,
       doc_feeder(collection, query={'taxid': {'$in': [9606, 10090, 10116]}})
       batch_callback is a callback function as fn(cnt, t), called after every batch
       fields is optional parameter passed to find to restrict fields to return.
    '''
    cur = collection.find(query, timeout=False, fields=fields)
    n = cur.count()
    s = s or 0
    e = e or n
    print('Retrieving {} documents from database "{}".'.format(n, collection.name))
    t0 = time.time()
    if inbatch:
        doc_li = []
    cnt = 0
    t1 = time.time()
    try:
        if s:
            cur.skip(s)
            cnt = s
            print("Skipping {} documents.".format(s))
        if e:
            cur.limit(e - (s or 0))
        cur.batch_size(step)
        print("Processing {}-{} documents...".format(cnt + 1, min(cnt + step, e)), end='')
        for doc in cur:
            if inbatch:
                doc_li.append(doc)
            else:
                yield doc
            cnt += 1
            if cnt % step == 0:
                if inbatch:
                    yield doc_li
                    doc_li = []
                print('Done.[%.1f%%,%s]' % (cnt * 100. / n, timesofar(t1)))
                if batch_callback:
                    batch_callback(cnt, time.time()-t1)
                if cnt < e:
                    t1 = time.time()
                    print("Processing {}-{} documents...".format(cnt + 1, min(cnt + step, e)), end='')
        if inbatch and doc_li:
            #Important: need to yield the last batch here
            yield doc_li

        #print 'Done.[%s]' % timesofar(t1)
        print('Done.[%.1f%%,%s]' % (cnt * 100. / n, timesofar(t1)))
        print("=" * 20)
        print('Finished.[total time: {}]'.format(timesofar(t0)))
    finally:
        cur.close()


def merge(src, target, step=10000, confirm=True):
    """Merging docs from src collection into target collection."""
    cnt = src.count()
    if not (confirm and ask('Continue to update {} docs from "{}" into "{}"?'.format(cnt, src.name, target.name)) == 'Y'):
        return

    for doc in doc_feeder(src, step=step):
        _id = doc['_id']
        target.update_one({"_id": _id}, {'$set': doc}, upsert=True)
