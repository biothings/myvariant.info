from utils.mongo import get_src_db
from utils.common import loadobj


class MongoSync():
    def __init__(self):
        self._src = get_src_db()

    def add_update(self, source, merge_collection, ids):
        for _id in ids:
            doc = self._src[source].get_from_id(_id)
            self._src[merge_collection].update({'_id': _id}, {'$set': doc}, upsert=True)

    def delete(self, merge_collection, field, ids):
        for _id in ids:
            doc = self._src[merge_collection].get_from_id(_id)
            if set(doc) == set(['_id', field]) or set(doc) == set(['_id', field, 'snpeff', 'vcf']):
                self._src[merge_collection].remove(_id)
            else:
                self._src[merge_collection].update({'_id': _id}, {'$unset': {field: 1}})

    def main(self, diff_filepath, merge_collection, field):
        diff = loadobj(diff_filepath)
        source_collection = diff['source']
        add_ids = diff['add']
        delete_ids = diff['delete']
        update_ids = [_doc['_id'] for _doc in diff['update']]
        self.add_update(source_collection, merge_collection, add_ids)
        self.add_update(source_collection, merge_collection, update_ids)
        self.delete(merge_collection, field, delete_ids)
