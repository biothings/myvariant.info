from __future__ import print_function
import time
import datetime
from utils.common import get_timestamp, get_random_string, timesofar
from utils.mongo import get_src_db, get_src_master


def load_source(collection_name, src_module=None, src_data=None, inbatch=True, new_collection=True):
    '''save src data into mongodb collection.
       if src_module is provided, src_data = src_module.load_data()
       if new_collection is True, it requires the target collection is empty.
       else, use src_data directly, should be a iterable.
    '''
    src_db = get_src_db()
    target_coll = src_db[collection_name]
    if new_collection and target_coll.count() > 0:
        print("Error: target collection {} exists.".format(collection_name))
        return

    t0 = time.time()
    cnt = 0
    if src_module:
        src_data = src_module.load_data()
    if src_data:
        doc_list = []
        for doc in src_data:
            cnt += 1
            if not inbatch:
                target_coll.insert(doc, manipulate=False, check_keys=False, w=0)
            else:
                doc_list.append(doc)
                if len(doc_list) == 100:
                    target_coll.insert(doc_list, manipulate=False, check_keys=False, w=0)
                    doc_list = []
            if cnt % 100000 == 0:
                print(cnt, timesofar(t0))
        if doc_list:
            target_coll.insert(doc_list, manipulate=False, check_keys=False, w=0)

        print("successfully loaded %s into mongodb" % collection_name)
        print("total docs: {}; total time: {}".format(cnt, timesofar(t0)))
    else:
        print("Error: no src data to load.")


class DataSource:
    def __init__(self, src_module):
        self.src_module = src_module
        self.src_name = src_module.__METADATA__['src_name']
        self.src_db = get_src_db()
        self.temp_collection = None

    def make_temp_collection(self):
        '''Create a temp collection for dataloading.'''

        new_collection = None
        while 1:
            new_collection = self.src_name + '_temp_' + get_random_string()
            if new_collection not in self.src_db.collection_names():
                break
        self.temp_collection = self.src_db[new_collection]
        return new_collection

    def switch_collection(self):
        '''after a successful loading, rename temp_collection to regular collection name,
           and renaming existing collection to a temp name for archiving purpose.
        '''
        if self.temp_collection and self.temp_collection.count() > 0:
            if self.src_db[self.src_name].count() > 0:
                new_name = '_'.join([self.src_name, 'archive', get_timestamp(), get_random_string()])
                self.src_db[self.src_name].rename(new_name, dropTarget=True)
            self.temp_collection.rename(self.src_name)
        else:
            return None

    def load(self, src_module=None, src_data=None, update_data=True, update_master=True):
        if not self.temp_collection:
            self.make_temp_collection()

        self.temp_collection.drop()

        if update_data:
            load_source(self.temp_collection.name, src_module=src_module, src_data=src_data)

        self.switch_collection()

        if update_master:
            # update src_master collection
                _doc = {
                    '_id': self.src_name,
                    'name': self.src_name,
                    'timestamp': datetime.datetime.now()
                }
                src_master = get_src_master()
                src_master.save(_doc)
