
__sources_dict__ = {
        'clinvar' : [
            'clinvar.clinvar_hg19',
            'clinvar.clinvar_hg38',
            ],
        'dbsnp' : [
            'dbsnp',
            ],
        }


import sys, time
import biothings.dataload.uploader as uploader
from pymongo.errors import DuplicateKeyError

class VariantDocSource(uploader.DocSource):

    def update_data(self, doc_d, step):
        doc_d = doc_d or self.load_data()
        print("doc_d mem: %s" % sys.getsizeof(doc_d))

        print("Uploading to the DB...", end='')
        t0 = time.time()
        for doc_li in self.doc_iterator(doc_d, batch=True, step=step):
            try:
                self.temp_collection.insert(doc_li, manipulate=False, check_keys=False)
            except DuplicateKeyError:
                pass
        print('Done[%s]' % timesofar(t0))
        self.switch_collection()
        self.post_update_data()


class MyVariantSourceUploader(uploader.SourceUploader):
    __doc_source_class__ = VariantDocSource
