from __future__ import print_function
import time
import json
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch import helpers

import config
from utils.common import iter_n, timesofar, ask
from dataindex.mapping import get_mapping

# setup ES logging
import logging
formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
es_logger = logging.getLogger('elasticsearch')
es_logger.setLevel(logging.WARNING)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
es_logger.addHandler(ch)

es_tracer = logging.getLogger('elasticsearch.trace')
es_tracer.setLevel(logging.WARNING)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
es_tracer.addHandler(ch)


def verify_ids(doc_iter, step=100000, index=None, doc_type=None):
    '''verify how many docs from input interator/list overlapping with existing docs.'''

    index = index or config.ES_INDEX_NAME
    doc_type = doc_type or config.ES_DOC_TYPE
    es = get_es()
    q = {'query': {'ids': {"values": []}}}
    total_cnt = 0
    found_cnt = 0
    out = []
    for doc_batch in iter_n(doc_iter, n=step):
        id_li = [doc['_id'] for doc in doc_batch]
        # id_li = [doc['_id'].replace('chr', '') for doc in doc_batch]
        q['query']['ids']['values'] = id_li
        xres = es.search(index=index, doc_type=doc_type, body=q, _source=False)
        found_cnt += xres['hits']['total']
        total_cnt += len(id_li)
        print(xres['hits']['total'], found_cnt, total_cnt)
        out.extend([x['_id'] for x in xres['hits']['hits']])
    return out


def get_es(es_host=None):
    es_host = es_host or config.ES_HOST
    es = Elasticsearch(es_host, timeout=120)
    return es


def wrapper(func):
    '''this wrapper allows passing index and doc_type from wrapped method.'''
    def outter_fn(*args, **kwargs):
        self = args[0]
        index = kwargs.pop('index', self._index)
        doc_type = kwargs.pop('doc_type', self._doc_type)
        self._index = index
        self._doc_type = doc_type
        return func(*args, **kwargs)
    outter_fn.__doc__ = func.__doc__
    return outter_fn


class ESIndexer():
    def __init__(self, index=None, doc_type=None, es_host=None, step=10000):
        self._es = get_es(es_host)
        self._index = index or config.ES_INDEX_NAME
        self._doc_type = doc_type or config.ES_DOC_TYPE
        self.number_of_shards = config.ES_NUMBER_OF_SHARDS      # set number_of_shards when create_index
        self.step = step  # the bulk size when doing bulk operation.
        self.s = None   # optionally, can specify number of records to skip,
                        # useful to continue indexing after an error.

    def check(self):
        '''print out ES server info for verification.'''
        print("Servers:", self._es.transport.hosts)
        print("Default indices:", self._index)
        print("Default doc_type:", self._doc_type)

    @wrapper
    def get_variant(self, vid, **kwargs):
        return self._es.get(index=self._index, id=vid, doc_type=self._doc_type, **kwargs)

    @wrapper
    def exists(self, vid):
        """return True/False if a variant id exists or not."""
        try:
            doc = self.get_variant(vid, fields=None)
            return doc['found']
        except NotFoundError:
            return False

    @wrapper
    def mexists(self, vid_list):
        q = {
            "query": {
                "ids": {
                    "values": vid_list
                }
            }
        }
        res = self._es.search(index=self._index, doc_type=self._doc_type, body=q, fields=None, size=len(vid_list))
        id_set = set([doc['_id'] for doc in res['hits']['hits']])
        print('..', len(id_set), end='')   # print out # of matching hits
        return [(vid, vid in id_set) for vid in vid_list]

    @wrapper
    def count(self, q=None, raw=False):
        _res = self._es.count(self._index, self._doc_type, q)
        return _res if raw else _res['count']

    @wrapper
    def count_src(self, src):
        if isinstance(src, str):
            src = [src]
        cnt_d = {}
        for _src in src:
            q = {
                "query": {
                    "constant_score": {
                        "filter": {
                            "exists": {"field": _src}
                        }
                    }
                }
            }
            cnt_d[_src] = self.count(q)
        return cnt_d

    @wrapper
    def create_index(self, mapping=None):
        if not self._es.indices.exists(self._index):
            body = {
                'settings': {
                    'number_of_shards': self.number_of_shards,
                    "number_of_replicas": 0,    # set this to 0 to boost indexing
                                                # after indexing, set "auto_expand_replicas": "0-all",
                                                #   to make additional replicas.
                }
            }
            if mapping:
                mapping = {"mappings": mapping}
                body.update(mapping)
            print(self._es.indices.create(index=self._index, body=body))

    @wrapper
    def exists_index(self):
        return self._es.indices.exists(self._index)

    def index(self, doc, id=None):
        '''add a doc to the index. If id is not None, the existing doc will be
           updated.
        '''
        return self._es.index(self.ES_INDEX_NAME, self.ES_INDEX_TYPE, doc, id=id)

    def index_bulk(self, docs, step=None):
        index_name = self._index
        doc_type = self._doc_type
        step = step or self.step

        def _get_bulk(doc):
            doc.update({
                "_index": index_name,
                "_type": doc_type,
            })
            return doc
        actions = (_get_bulk(doc) for doc in docs)
        return helpers.bulk(self._es, actions, chunk_size=step)

    def delete_doc(self, id):
        '''delete a doc from the index based on passed id.'''
        return self._es.delete(self._index, self._doc_type, id)

    def delete_docs(self, ids, step=None):
        '''delete a list of docs in bulk.'''
        index_name = self._index
        doc_type = self._doc_type
        step = step or self.step

        def _get_bulk(_id):
            doc = {
                '_op_type': 'delete',
                "_index": index_name,
                "_type": doc_type,
                "_id": _id
            }
            return doc
        actions = (_get_bulk(_id) for _id in ids)
        return helpers.bulk(self._es, actions, chunk_size=step, stats_only=True, raise_on_error=False)

    def update(self, id, extra_doc, upsert=True):
        '''update an existing doc with extra_doc.
           allow to set upsert=True, to insert new docs.
        '''
        body = {'doc': extra_doc}
        if upsert:
            body['doc_as_upsert'] = True
        return self._es.update(self._index, self._doc_type, id, body)

    def update_docs(self, partial_docs, upsert=True, step=None, **kwargs):
        '''update a list of partial_docs in bulk.
           allow to set upsert=True, to insert new docs.
        '''
        index_name = self._index
        doc_type = self._doc_type
        step = step or self.step

        def _get_bulk(doc):
            doc = {
                '_op_type': 'update',
                "_index": index_name,
                "_type": doc_type,
                "_id": doc['_id'],
                "doc": doc
            }
            if upsert:
                doc['doc_as_upsert'] = True
            return doc
        actions = (_get_bulk(doc) for doc in partial_docs)
        return helpers.bulk(self._es, actions, chunk_size=step, **kwargs)

    def update_mapping(self, m):
        assert list(m) == [self._doc_type]
        # assert m[self._doc_type].keys() == ['properties']
        assert 'properties' in m[self._doc_type]
        print(json.dumps(m, indent=2))
        if ask("Continue to update above mapping?") == 'Y':
            print(self._es.indices.put_mapping(index=self._index, doc_type=self._doc_type, body=m))

    #def build_index(self, collection, update_mapping=False, verbose=False, query=None):
    @wrapper
    def build_index(self, collection, verbose=True, query=None, bulk=True, update=False, allow_upsert=True):
        index_name = self._index

        #self.verify_mapping(update_mapping=update_mapping)

        # update some settings for bulk indexing
        if verbose:
            print("Update index settings...", end="")
        body = {
            "index": {
                "refresh_interval": "-1",              # disable refresh temporarily
                "auto_expand_replicas": "0-all",
                #"number_of_replicas": 0,
                #"refresh_interval": "30s",
            }
        }
        res = self._es.indices.put_settings(body, index_name)
        if verbose:
            print(res)

        try:
            print('Building index "{}"...'.format(index_name))
            cnt = self._build_index_sequential(collection, verbose, query=query, bulk=bulk, update=update, allow_upsert=True)
        finally:
            # restore some settings after bulk indexing is done.
            body = {
                "index": {
                    "refresh_interval": "1s"              # default settings
                }
            }
            self._es.indices.put_settings(body, index_name)

            try:
                res = self._es.indices.flush()
                if verbose:
                    print("Flushing...", res)
                res = self._es.indices.refresh()
                if verbose:
                    print("Refreshing...", res)
            except:
                pass

            time.sleep(1)
            print("Validating...", end='')
            src_cnt = collection.find(query).count()
            es_cnt = self.count()
            if src_cnt == es_cnt:
                print("OK [total count={}]".format(src_cnt))
            else:
                print("\nWarning: total count of gene documents does not match [{}, should be {}]".format(es_cnt, src_cnt))

        if cnt:
            print('Done! - {} docs indexed.'.format(cnt))

            # No longer do optimization after indexing
            # since it does not run async since ES v1.5
            # run optimize manually if needed.

            # if verbose:
            #     print("Optimizing...", end="")
            # res = self.optimize()
            # if verbose:
            #     print(res)

    def _build_index_sequential(self, collection, verbose=False, query=None, bulk=True, update=False, allow_upsert=True):
        from utils.mongo import doc_feeder

        def rate_control(cnt, t):
            delay = 0
            if t > 90:
                delay = 30
            elif t > 60:
                delay = 10
            if delay:
                print("\tPausing for {}s...".format(delay), end='')
                time.sleep(delay)
                print("done.")

        src_docs = doc_feeder(collection, step=self.step, s=self.s, batch_callback=rate_control, query=query)
        if bulk:
            if update:
                # input doc will update existing one
                # if allow_upsert, create new one if not exist
                res = self.update_docs(src_docs, upsert=allow_upsert)
            else:
                # input doc will overwrite existing one
                res = self.index_bulk(src_docs)
            if len(res[1]) > 0:
                print("Error: {} docs failed indexing.".format(len(res[1])))
            return res[0]
        else:
            cnt = 0
            for doc in src_docs:
                self.index(doc)
                cnt += 1
                if verbose:
                    print(cnt, ':', doc['_id'])
            return cnt

    @wrapper
    def optimize(self, max_num_segments=1):
        '''optimize the default index.'''
        params = {
            # since 1.5 this no longer work
            # optimization does not run async anymore
            # "wait_for_merge": False,
            "max_num_segments": max_num_segments
        }
        return self._es.indices.optimize(index=self._index, params=params)

    def clean_field(self, field, dryrun=True, step=5000):
        '''remove a top-level field from ES index, if the field is the only field of the doc,
           remove the doc as well.
           step is the size of bulk update on ES
           try first with dryrun turned on, and then perform the actual updates with dryrun off.
        '''
        q = {
            "query": {
                "constant_score": {
                    "filter": {
                        "exists": {
                            "field": field
                        }
                    }
                }
            }
        }
        cnt_orphan_doc = 0
        cnt = 0
        _li = []
        for doc in self.doc_feeder(query=q):
            if set(doc) == set(['_id', field]):
                cnt_orphan_doc += 1
                # delete orphan doc
                _li.append({
                    "delete": {
                        "_index": self._index,
                        "_type": self._doc_type,
                        "_id": doc['_id']
                    }
                })
            else:
                # otherwise, just remove the field from the doc
                _li.append({
                    "update": {
                        "_index": self._index,
                        "_type": self._doc_type,
                        "_id": doc['_id']
                    }
                })
                # this script update requires "script.disable_dynamic: false" setting
                # in elasticsearch.yml
                _li.append({"script": 'ctx._source.remove("{}")'.format(field)})

            cnt += 1
            if len(_li) == step:
                if not dryrun:
                    self._es.bulk(body=_li)
                _li = []
        if _li:
            if not dryrun:
                self._es.bulk(body=_li)

        print("Total {} documents found:".format(cnt))
        print("\t{} documents are updated.".format(cnt - cnt_orphan_doc))
        print("\t{} documents are deleted.".format(cnt_orphan_doc))
        if dryrun:
            print("This is a dryrun, so no actual document operations.")

    @wrapper
    def doc_feeder(self, step=10000, verbose=True, query=None, scroll='10m', **kwargs):
        q = query if query else {'query': {'match_all': {}}}
        _q_cnt = self.count(q=q, raw=True)
        n = _q_cnt['count']
        n_shards = _q_cnt['_shards']['total']
        assert n_shards == _q_cnt['_shards']['successful']
        _size = int(step / n_shards)
        assert _size * n_shards == step
        cnt = 0
        t0 = time.time()
        if verbose:
            print('\ttotal docs: {}'.format(n))
            t1 = time.time()

        res = self._es.search(self._index, self._doc_type, body=q,
                              size=_size, search_type='scan', scroll=scroll, **kwargs)
        # double check initial scroll request returns no hits
        assert len(res['hits']['hits']) == 0

        while 1:
            if verbose:
                t1 = time.time()
                if cnt < n:
                    print('\t{}-{}...'.format(cnt+1, min(cnt+step, n)), end='')
            res = self._es.scroll(res['_scroll_id'], scroll=scroll)
            if len(res['hits']['hits']) == 0:
                break
            else:
                for doc in res['hits']['hits']:
                    yield doc['_source']
                    cnt += 1
                if verbose:
                    print('done.[%.1f%%,%s]' % (min(cnt, n)*100./n, timesofar(t1)))

        if verbose:
            print("Finished! [{}]".format(timesofar(t0)))

        assert cnt == n, "Error: scroll query terminated early [{}, {}], please retry.\nLast response:\n{}".format(cnt, n, res)

    @wrapper
    def get_id_list(self, step=100000, verbose=True):
        cur = self.doc_feeder(step=step, _source=False, verbose=verbose)
        id_li = [doc['_id'] for doc in cur]
        return id_li

    def find_biggest_doc(self, fields_li, min=5, return_doc=False):
        """return the doc with the max number of fields from fields_li."""
        import itertools
        for n in range(len(fields_li), min - 1, -1):
            print('>>>>', n)
            for field_set in itertools.combinations(fields_li, n):
                q = ' AND '.join(["_exists_:" + field for field in field_set])
                q = {'query': {"query_string": {"query": q}}}
                cnt = self.count(q)
                if cnt > 0:
                    print("\nFound {} docs with {} fields".format(cnt, len(field_set)))
                    if return_doc:
                        res = self._es.search(index=self._index, doc_type=self._doc_type, body=q, size=cnt)
                        return res
                    else:
                        return (cnt, q)
                else:
                    print('.', end='')
            print()


def duplicate_index_with_new_settings(old_index, new_index, settings):
    ''' This function will create a new index and copy the mappings from the old index
    with the settings dict, you can change any of the settings, e.g. number of primary
    shards.'''
    m = es.indices.get_mapping(index=old_index)
    mappings = m[old_index]['mappings']
    es.indices.create(index=new_index, body='{"settings":' + json.dumps(settings) + ', "mappings":' + json.dumps(mappings) + '}')


def reindex(old_index, new_index, s):
    ''' Function to reindex by scan and scroll combined with a bulk insert.
    old_index is the index to take docs from, new_index is the one the docs go to.
    s is the size of each bulk insert - should set this as high as the RAM
    on the machine you run it on allows.  500-1000 seems reasonable for t2.medium '''
    def create_bulk_insert_string(results, index):
        ret_str = ''
        for hit in results:
            ret_str += '{"create":{"_index":"' + index + '","_type":"variant","_id":"' + hit['_id'] + '"}}\n'
            ret_str += json.dumps(hit) + '\n'
        return ret_str

    es = Elasticsearch('localhost:9200')
    s = es.search(index=old_index, body='{"query": {"match_all": {}}}', search_type='scan', scroll='5m', size=s)
    curr_done = 0

    try:
        while True:  # do this loop until failure
            r = es.scroll(s['_scroll_id'], scroll='5m')
            this_l = [res['_source'] for res in r['hits']['hits']]
            this_str = create_bulk_insert_string(this_l, new_index)
            es.bulk(body=this_str, index=new_index, doc_type='variant')
            curr_done += len(this_l)
    except:
        print('{} documents inserted'.format(curr_done))


def get_metadata(index):
    m = get_mapping()
    data_src = m['variant']['properties'].keys()
    stats = {}
    t = ESIndexer()
    t._index = index
    m['total'] = t.count()

    for _src in data_src:
        stats[_src] = t.count_src(_src)[_src]
    return stats
