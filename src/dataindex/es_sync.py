from __future__ import print_function
import glob
from biothings.utils.common import iter_n
from time import sleep, time
import os.path
import jsonpatch
import config
from elasticsearch.helpers import bulk
from utils.es import ESIndexer, get_es
from biothings.utils.mongo import get_src_db
#from utils.diff import apply_patch, diff_collections, get_backend
from utils.diff_update import apply_patch, diff_collections, get_backend
from biothings.utils.common import loadobj, get_random_string, timesofar
from dataload import load_source


class ESSyncer():
    def __init__(self, index=None, doc_type=None, es_host=None, step=5000):
        self._es = get_es(es_host)
        self._index = index or config.ES_INDEX_NAME
        self._doc_type = doc_type or config.ES_DOC_TYPE
        self._esi = ESIndexer(es_host=es_host)
        self._esi._index = self._index
        self._src = get_src_db()
        self.step = step

    def add(self, collection, ids):
        # compare id_list with current index, get list of ids with true/false indicator
        cnt_update = 0
        cnt_create = 0
		for ids_chunk in iter_n(ids, 100):
		    id_list_all = self._esi.mexists(ids_chunk, verbose=False)
		    for _id, _exists in id_list_all:
			_doc = self._src[collection].find_one({'_id': _id})
			_doc.pop('_id')
			# case one: this id exists in current index, then just update
			if _exists:
			    es_info = {
				'_op_type': 'update',
				'_index': self._index,
				'_type': self._doc_type,
				'_id': _id,
				'doc': _doc
			    }
			    cnt_update += 1
			# case two: this id not exists in current index, then create a new one
			else:
			    es_info = {
				'_op_type': 'create',
				'_index': self._index,
				'_type': self._doc_type,
				"_id": _id,
				'_source': _doc
			    }
			    cnt_create += 1
			yield es_info
		print('items updated: ', cnt_update)
		print('items newly created: ', cnt_create)

	    def delete(self, field, ids):
		cnt_update = 0
		cnt_delete = 0
		for _id in ids:
		    # get doc from index based on id
		    if self._esi.exists(_id):
			doc = self._esi.get_variant(_id)['_source']
                        doc.pop('_id', None)
                # case one: only exist target field, or target field/snpeff/vcf, then we need to delete this item
                if len(set(doc) - set([field, 'snpeff', 'vcf', 'hg19', 'hg38', 'chrom'])) == 0:
                    es_info = {
                        '_op_type': 'delete',
                        '_index': self._index,
                        '_type': self._doc_type,
                        "_id": _id,
                    }
                    cnt_delete += 1
                # case two: exists fields other than snpeff, vcf and target field
                else:
                    # get rid of the target field, delete original doc, update the new doc
                    # plus count
                    # this requires enabling ElasticSearch dynamic scripting
                    es_info = {
                        '_op_type': 'update',
                        '_index': self._index,
                        '_type': self._doc_type,
                        '_id': _id,
                        "script": 'ctx._source.remove("{}");ctx._source.remove("_id")'.format(field)
                    }
                    cnt_update += 1
                yield es_info
            else:
                print('id not exists: ', _id)
        print('items updated: ', cnt_update)
        print('items deleted: ', cnt_delete)

    '''
    def _update_one(self, _id, _patch):
        doc = self._esi.get_variant(_id)['_source']
        try:
            doc = apply_patch(doc, _patch)
        except jsonpatch.JsonPatchConflict as e:
            pass
        es_info = {
            '_op_type': 'index',
            '_index': self._index,
            '_type': self._doc_type,
            "_id": _id,
            '_source': doc
        }
        return es_info
    '''

    def _update_one(self, _id, _patch, collection, source_collection):
        doc_es = self._esi.get_variant(_id)['_source']
        doc_mongo = self._src[source_collection].find_one(_id)
        doc_es[collection] = doc_mongo[collection]
        doc_es.pop('_id', None)
        es_info = {
            '_op_type': 'index',
            '_index': self._index,
            '_type': self._doc_type,
            "_id": _id,
            '_source': doc_es
        }
        return es_info

    def update(self, id_patchs, collection, source_collection):
        for _id_patch in id_patchs:
            _id = _id_patch['_id']
            _patch = _id_patch['patch']
            if self._esi.exists(_id):
                _es_info = self._update_one(_id, _patch, collection=collection, source_collection=source_collection)
                yield _es_info
            else:
                print('id does not exist:', _id)

    def update2(self, id_patchs, collection, source_collection):
        from utils import backend

        _es = backend.GeneDocESBackend(self._esi)
        _db = backend.GeneDocMongoDBBackend(source_collection)

        for _id_chunk in iter_n(id_patchs, 100):
            es_docs = _es.mget_from_ids(_id_chunk, step=100)
            db_docs = _db.mget_from_ids(_id_chunk)
            es_docs = dict([(doc['_id'], doc) for doc in es_docs])
            db_docs = dict([(doc['_id'], doc) for doc in db_docs])
            for _id in es_docs:
                doc_es = es_docs[_id]
                doc_mongo = db_docs.get(_id, None)
                if doc_mongo:
                    doc_es[collection] = doc_mongo[collection]
                else:
                    print('id does not exist in mongodb collection:', _id)
                doc_es.pop('_id', None)
                es_info = {
                    '_op_type': 'index',
                    '_index': self._index,
                    "_id": _id,
                    '_type': self._doc_type,
                    '_source': doc_es
                }
                yield es_info

def sync_from_one_diff(index, collection, diff_filepath, validate=False, wait=60, dryrun=False, returncnt=False, save2file=None):
    sync = ESSyncer(index=index)
    #sync._index = index
    #sync._esi._index = index
    diff = loadobj(diff_filepath)
    source_collection = diff['source']
    add_iter = sync.add(source_collection, diff['add'])
    delete_iter = sync.delete(collection, diff['delete'])
    update_iter = sync.update2(diff['update'], collection, source_collection)
    t00 = time()
    if save2file:
        from itertools import chain
        import json
        for op in chain(add_iter, delete_iter, update_iter):
            json.dump(op, save2file)
        print("="*20)
        print("Finished! [{}]".format(timesofar(t00)))
        return

    print('Adding new {} docs...'.format(len(diff['add'])))
    t0 = time()
    if not dryrun:
        try:
            bulk(sync._es, add_iter)
        except:
            pass
    print("Done. [{}]".format(timesofar(t0)))

    print('Deleting {} docs'.format(len(diff['delete'])))
    t0 = time()
    if not dryrun:
        bulk(sync._es, delete_iter)
    print("Done. [{}]".format(timesofar(t0)))

    print('Updating {} docs'.format(len(diff['update'])))
    t0 = time()
    if not dryrun:
        bulk(sync._es, update_iter)
    print("Done. [{}]".format(timesofar(t0)))

    # add flush and refresh
    try:
        res = sync._es.indices.flush()
        print("Flushing...", res)
        res = sync._es.indices.refresh()
        print("Refreshing...", res)
    except:
        pass

    print("="*20)
    print("Finished! [{}]".format(timesofar(t00)))

    if returncnt:
        cnt = {
            'add': len(diff['add']),
            'delete': len(diff['delete']),
            'update': len(diff['update'])
        }
        return cnt

    if validate:
        print('Waiting {}s to let ES to finish...'.format(wait), end="")
        sleep(wait)
        print("Done.")
        print("Validating...")
        t0 = time()
        q = {
            "query": {
                "constant_score": {
                    "filter": {
                        "exists": {
                            "field": 'clinvar'
                        }
                    }
                }
            }
        }
        data = sync._esi.doc_feeder(query=q, _source=collection)
        temp_collection = collection + '_temp_' + get_random_string()
        sync._src[temp_collection].drop()
        load_source(temp_collection, src_data=data)
        c1 = get_backend(source_collection, 'mongodb')
        c2 = get_backend(temp_collection, 'mongodb')
        diff_result = diff_collections(c1, c2, use_parallel=False)
        sync._src[temp_collection].drop()
        print("Done. [{}]".format(t0))
        return diff_result

def sync_from_folder(index, collection, diff_folder, validate=False, wait=60, save2file=None):
    cnt_add = 0
    cnt_delete = 0
    cnt_update = 0
    if save2file:
        dump_f = open(save2file, 'w')
    else:
        dump_f = None
    for input_file in sorted(glob.glob(os.path.join(diff_folder, '*.pyobj'))):
        print("*"*50)
        print("Start processing {} from {}".format(input_file, diff_folder))
        cnt = sync_from_one_diff(index, collection, input_file, validate=validate, wait=wait, returncnt=True, save2file=dump_f)
        if cnt:
            cnt_add += cnt['add']
            cnt_delete += cnt['delete']
            cnt_update += cnt['update']
    if dump_f:
        dump_f.close()
