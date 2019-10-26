from biothings.hub.dataload.storage import BaseStorage, BasicStorage, IgnoreDuplicatedStorage
from utils.hgvs import encode_long_hgvs_id


class EncodeLongHGVSIDStorage(BaseStorage):
    """
    BasicStorage including long HGVC ID encoding
    """

    def check_doc_func(self, doc):
        doc = encode_long_hgvs_id(doc)
        if doc.get("_seqhashed"):
            # required to query _exists_:_seqhashed
            doc["_seqhashed"]["_flag"] = True

        return doc

class MyVariantBasicStorage(EncodeLongHGVSIDStorage, BasicStorage): pass
class MyVariantIgnoreDuplicatedStorage(EncodeLongHGVSIDStorage, IgnoreDuplicatedStorage): pass

