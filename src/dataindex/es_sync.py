from __future__ import print_function
from time import sleep, time
import config
from elasticsearch.helpers import bulk
from utils.es import ESIndexer, get_es
from utils.mongo import get_src_db
from utils.diff import apply_patch, diff_collections, get_backend
from utils.common import loadobj, get_random_string, timesofar
from dataload.__init__ import load_source


class ESSyncer():
    def __init__(self, index=None, doc_type=None, es_host=None, step=5000):
        self._es = get_es(es_host)
        self._index = index or config.ES_INDEX_NAME
        self._doc_type = doc_type or config.ES_DOC_TYPE
        self._esi = ESIndexer()
        self._esi._index = self._index
        self._src = get_src_db()
        self.step = step

    def add(self, collection, ids):
        # compare id_list with current index, get list of ids with true/false indicator
        id_list = []
        id_list_all = []
        cnt = 0
        for _id in ids:
            id_list.append(_id)
            cnt += 1
            if len(id_list) == 100:
                id_list_all += self._esi.mexists(id_list, verbose=False)
                id_list = []
        if id_list:
            id_list_all += self._esi.mexists(id_list, verbose=False)
        cnt_update = 0
        cnt_create = 0
        for _id, _exists in id_list_all:
            # case one: this id exists in current index, then just update
            if _exists:
                es_info = {
                    '_op_type': 'update',
                    '_index': self._index,
                    '_type': self._doc_type,
                    '_id': _id,
                    'doc': self._src[collection].find_one({'_id': _id})
                }
                cnt_update += 1
            # case two: this id not exists in current index, then create a new one
            else:
		_doc = self._src[collection].find_one({'_id': _id})
		_doc.pop('_id')
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
                doc.pop('_id')
                # case one: only exist target field, or target field/snpeff/vcf, then we need to delete this item
                if set(doc) == set([field]) or set(doc) == set([field, 'snpeff', 'vcf']) or set(doc) == set([field, 'snpeff', 'vcf', 'hg19']):
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
                    es_info = {
                        '_op_type': 'update',
                        '_index': self._index,
                        '_type': self._doc_type,
                        '_id': _id,
                        "script": 'ctx._source.remove("{}")'.format(field)
                    }
                    cnt_update += 1
                yield es_info
            else:
                print('id not exists: ', _id)
        print('items updated: ', cnt_update)
        print('items deleted: ', cnt_delete)

    def _update_one(self, _id, _patch):
        doc = self._esi.get_variant(_id)['_source']
        doc = apply_patch(doc, _patch)
        es_info = {
            '_op_type': 'index',
            '_index': self._index,
            '_type': self._doc_type,
            "_id": _id,
            '_source': doc
        }
        return es_info

    def update(self, id_patchs):
        for _id_patch in id_patchs:
            _id = _id_patch['_id']
            _patch = _id_patch['patch']
            if self._esi.exists(_id):
                _es_info = self._update_one(_id, _patch)
                yield _es_info
            else:
                print('id not exists:', _id)

    def update1(self, id_patchs):
        for _id_patch in id_patchs:
            _id = _id_patch['_id']
            _patch = _id_patch['patch']
            if self._esi.exists(_id):
                _es_info = self._update_one(_id, _patch)
                self._esi.delete_doc(_id)
                yield _es_info
            else:
                print('id not exists:', _id)

    def main(self, index, collection, diff_filepath, validate=False, wait=60):
        self._index = index
        self._esi._index = index
        diff = loadobj(diff_filepath)
        source_collection = diff['source']
        add_list = self.add(source_collection, diff['add'])
        delete_list = self.delete(collection, diff['delete'])
        update_list = self.update(diff['update'])
        t00 = time()
        print('Adding new {} docs...'.format(len(diff['add'])))
        t0 = time()
        bulk(self._es, add_list)
        print("Done. [{}]".format(timesofar(t0)))
        print('Deleting {} docs'.format(len(diff['delete'])))
        t0 = time()
        bulk(self._es, delete_list)
        print("Done. [{}]".format(timesofar(t0)))
        print('Updating {} docs'.format(len(diff['update'])))
        t0 = time()
        bulk(self._es, update_list)
        print("Done. [{}]".format(timesofar(t0)))
        print("="*20)
        print("Finished! [{}]".format(timesofar(t00)))
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
                                "field": collection
                            }
                        }
                    }
                }
            }
            data = self._esi.doc_feeder(query=q, _source=collection)
            temp_collection = collection + '_temp_' + get_random_string()
            self._src[temp_collection].drop()
            load_source(temp_collection, src_data=data)
            c1 = get_backend(source_collection, 'mongodb')
            c2 = get_backend(temp_collection, 'mongodb')
            diff_result = diff_collections(c1, c2, use_parallel=False)
            self._src[temp_collection].drop()
            print("Done. [{}]".format(t0))
            return diff_result
