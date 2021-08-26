import time
import asyncio

import config
from biothings.hub.dataindex.indexer import Indexer, IndexManager, ColdHotIndexer, _BuildDoc
from biothings.hub.dataexport.ids import export_ids, upload_ids
from biothings.utils.hub_db import get_src_build
from biothings.utils.es import ESIndexer
from utils.stats import update_stats

from elasticsearch import JSONSerializer, SerializationError
from elasticsearch.compat import string_types

import orjson

class MyVariantJSONSerializer(JSONSerializer):
    """
    MyVariantJSONSerializer is an extension to JSONSerializer. Its `loads` and `dumps` code structures are logically the same 
    with JSONSerializer, except that `orjson` is used as the underlying serializer instead of `json` or `simplejson`.

    `orjson` is used to encode infinity values `float("inf")` or `float("-inf")` into `None`, instead of into "Infinity" or 
    "-Infinity" strings.
    ElasticSearch's underlying `JsonParser` module cannot convert "Infinity" or "-Infinity" strings back into infinity values

    See https://github.com/elastic/elasticsearch-py/blob/master/elasticsearch/serializer.py
    """

    def loads(self, s):
        try:
            # return json.loads(s)
            return orjson.loads(s)
        except (ValueError, TypeError) as e:
            raise SerializationError(s, e)

    def dumps(self, data):
        # don't serialize strings
        if isinstance(data, string_types):
            return data

        try:
            """
            `json.dumps()` behaviors:

            ensure_ascii: If true (the default), the output is guaranteed to have all incoming non-ASCII characters escaped. 
                          If false, these characters will be output as-is.
            separators: an (item_separator, key_separator) tuple, specifying the separators in the output.
            """
            # return json.dumps(
            #     data, default=self.default, ensure_ascii=False, separators=(",", ":")
            # )
            
            """
            `orjson.dumps()` will escape all incoming non-ASCII characters and output the encoded bytestrings.
            We decode the output bytestrings into string, and as a result, those escaped characters are un-escaped.
            In Python 3, the default encoding is "utf-8" (see https://docs.python.org/3/library/stdtypes.html#bytes.decode).

            `orjson.dumps()` will output compact JSON representation, effectively the same behavior with json.dumps(separators=(",", ":"))
            """
            return orjson.dumps(
                data, default=self.default
            ).decode()
        except (ValueError, TypeError) as e:
            raise SerializationError(data, e)


class BaseVariantIndexer(Indexer):

    def __init__(self, build_doc, indexer_env, index_name):
        super().__init__(build_doc, indexer_env, index_name)

        # Changing the `es_client_args` object might affect top level config serialization.
        # we have an endpoint to print the config, it might be safer to avoid changing the `es_client_args` object.
        self.es_client_args = dict(self.es_client_args)
        self.es_client_args["serializer"] = MyVariantJSONSerializer()

        self.es_index_mappings["properties"]["chrom"] = {
            'analyzer': 'string_lowercase',
            'type': 'text'
        }
        self.es_index_mappings["properties"]["observed"] = {
            "type": "boolean"
        }
        self.es_index_mappings["properties"]["_seqhashed"] = {
            "type": "object",
            "properties": {
                "_flag": {
                    "type": "boolean"
                }
            }
        }
        self.es_index_settings["mapping"] = {
            "total_fields": {
                "limit": 2000
            }
        }
        self.assembly = build_doc["build_config"]["assembly"]

    @asyncio.coroutine
    def post_index(self, *args, **kwargs):
        # Migrated from Sebastian's commit 1a7b7a
        # It was orginally marked "Not Tested Yet".
        self.logger.info("Sleeping for a bit while index is being fully updated...")
        yield from asyncio.sleep(3*60)
        idxer = ESIndexer(
            index=self.es_index_name,
            es_host=self.es_client_args.get('hosts'))
        self.logger.info("Updating 'stats' by querying index '%s'" % self.es_index_name)
        return update_stats(idxer, self.assembly)


class MyVariantIndexerManager(IndexManager):

    # New Hub Command

    def post_publish(self, snapshot, index, *args, **kwargs):
        # assuming build name == index name, and assuming demo index has
        # "demo" in its name...
        # assuming full index, not demo, guess name now
        bdoc = get_src_build().find_one({"_id": index})
        assert bdoc, "Can't find build doc associated with index '%s' (should be named the same)" % index
        ids_file = export_ids(index)
        if "hg19" in index or "hg19" in snapshot:
            redir = "hg19_ids.xz"
        else:
            redir = "hg38_ids.xz"
        if "demo" in index or "demo" in snapshot:
            redir = "demo_%s" % redir
        upload_ids(ids_file, redir,
                   s3_bucket=config.IDS_S3_BUCKET,
                   aws_key=config.AWS_KEY,
                   aws_secret=config.AWS_SECRET)


class VariantIndexer(BaseVariantIndexer):
    pass


class ColdHotVariantIndexer(ColdHotIndexer):
    def __init__(self, build_doc, indexer_env, index_name):
        hot_build_doc = _BuildDoc(build_doc)
        cold_build_doc = hot_build_doc.extract_coldbuild()

        self.hot = BaseVariantIndexer(hot_build_doc, indexer_env, index_name)
        self.cold = BaseVariantIndexer(cold_build_doc, indexer_env, self.hot.es_index_name)
