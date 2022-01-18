from biothings.hub.dataload.storage import BasicStorage, IgnoreDuplicatedStorage
from utils.hgvs import DocEncoder
from config import MAX_REF_ALT_LEN, MAX_ID_LENGTH
from collections import Mapping


class MyVariantBasicStorage(BasicStorage):
    """
    Extended from BasicStorage, providing new implementation of `check_doc_func()` method which encode long HGVS IDs.
    Long HGVS IDs whose lengths can go beyond the limits of our DB systems (MongoDB especially). This Storage should
    be used on every plugin where HGVS IDs are the `_id` of the docs.

    See https://github.com/biothings/myvariant.info/issues/91
    """
    def encode_long_hgvs_id(self, doc):
        """
        Encode long HGVS ID inside the doc
        """
        encoded, doc = DocEncoder.encode_long_hgvs_id(doc, max_len=MAX_ID_LENGTH)
        if encoded:
            # required to query _exists_:_seqhashed
            doc[DocEncoder.KEY_SEQ_MAP]["_flag"] = True
            self.logger.info("Encoded a long hgvs id. New id = {}".format(doc["_id"]))

        return doc

    def check_doc_func(self, doc):
        doc = self.encode_long_hgvs_id(doc)
        return doc


class MyVariantTrimmingStorage(MyVariantBasicStorage):
    """
    Based on `MyVariantBasicStorage`, this storage class further trims long `ref` and `alt` sequences in every doc.
    Long `ref` or `alt` sequences as keywords can be rejected by ElasticSearch. Currently this storage is only applied
    to ClinVar data source.

    See https://github.com/biothings/myvariant.info/issues/110
    """

    # Known fields in every doc that cannot have "ref" and "alt" sequences for sure
    # excluded_keys = {"_id", "_seqhashed"}
    excluded_keys = {DocEncoder.KEY_ID, DocEncoder.KEY_SEQ_MAP}

    def trim_long_ref_alt_seq(self, doc):
        """
        Trim long `ref` and `alt` sequences inside the doc.

        This method holds an assumption that each `doc` object is a dictionary of the following structure:

            {
                "_id": xxx,
                "_seqhashed": {...},

                "<source-name>": {
                    "alt": xxx
                    "ref": xxx
                    ...
                },

                "<additional-key>": {...},
                "<additional-key>": {...},
                ...
            }

        where "_seqhashed" is optional, "<additional-key>" fields are rare (but also looked into for "alt" and "ref"
        if existing), and "<source-name>" is the field where we anticipate the appearance of the "alt" and "ref"
        sequences.

        Code is borrowed from `SnpeffPostUpdateUploader.do_snpeff()` method, then modified according to
        `MyVariantBasicStorage.__encode_long_hgvs_id()` method.
        """
        included_keys = [key for key in doc if key not in self.excluded_keys]

        if len(included_keys) > 1:
            # We assume that if there is only one key left in `included_keys`, it must be the `<source-name>`
            #   and it's not necessary to check its type if so
            # If there are more than 1 keys in `included_keys`, we need to further exclude keys not mapped to dict.
            # The check `isinstance(var, collections.Mapping)` works for `dict()`, `collections.OrderedDict()`, and
            #   `collections.UserDict()`
            included_keys = [key for key in included_keys if isinstance(doc[key], Mapping)]

        for key in included_keys:
            encoded, doc = DocEncoder.encode_long_ref_alt_seq(doc, key, max_len=MAX_REF_ALT_LEN)
            if encoded:
                self.logger.info("Trimmed the ref/alt sequences in field {} for a variant with id = {}".
                                 format(key, doc["_id"]))

        return doc

    def check_doc_func(self, doc):
        doc = self.encode_long_hgvs_id(doc)
        doc = self.trim_long_ref_alt_seq(doc)
        return doc


class MyVariantIgnoreDuplicatedStorage(MyVariantBasicStorage, IgnoreDuplicatedStorage):
    pass
