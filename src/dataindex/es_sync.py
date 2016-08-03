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
                                                                              61,9          41%
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
                                                                               61,9          41%
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
                                                                                61,9          41%
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
                                                                                 61,9          41%
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

                                                                                  61,9          41%
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

                                                                                   61,9          41%
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

                                                                                    61,9          41%
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

                                                                                     61,9          41%
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

                                                                                      61,9          41%
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

                                                                                       61,9          41%
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

                                                                                        61,9          41%
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

                                                                                          61,9          41%
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
                                                                                           61,9          41%
                    # plus count
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
                                                                                             61,9          41%
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
                                                                                              61,9          41%
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
                                                                                               61,9          41%
                    es_info = {
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
                                                                                                61,9          41%

▽
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
"indexer.py" 320L, 9544C                                                                        1,1           Top
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
                                                                                                36,9          12%
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
                                                                                                71,1          24%
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
                                                                                                106,5         37%
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
                    "_id": doc.pop('_id')
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

                                                                                                141,13        49%
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
                                                                                                165,9         57%
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
                                                                                                199,13        69%

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
                                                                                                200,13        57%
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


▽
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
"es_sync.py" 181L, 6974C                                                                        1,1           Top
