import asyncio

import config
from biothings.hub.dataindex.indexer import Indexer, IndexManager, ColdHotIndexer
from biothings.hub.dataexport.ids import export_ids, upload_ids
from biothings.utils.hub_db import get_src_build
from utils.es import ElasticsearchIndexingService

from elasticsearch import JSONSerializer, SerializationError, Elasticsearch
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

        # TODO should we use _BuildDoc to wrap build_doc?
        # TODO or should we make Indexer._build_doc a visible member?
        self.build_doc = build_doc

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

    async def post_index(self, *args, **kwargs):
        # No idea how come the decision to sleep for 3 minutes
        # Migrated from Sebastian's commit 1a7b7a. It was orginally marked "Not Tested Yet".
        self.logger.info("Sleeping for a bit while index is being fully updated...")
        await asyncio.sleep(3 * 60)

        # update _meta.stats in ES mapping
        with Elasticsearch(**self.es_client_args) as es_client:
            es_service = ElasticsearchIndexingService(client=es_client, index_name=self.es_index_name)
            meta_stats = es_service.update_mapping_meta_stats(assembly=self.assembly)
            self.logger.info(f"_meta.stats updated to {meta_stats} for index {self.es_index_name}")

        # update _meta.stats in myvariant_hubdb.src_build

        # DO NOT use the following client because the `_build_doc.parse_backend()` in Indexer.__init__() won't work
        #   for a MyVariant build_doc. It results in `self.mongo_database_name` equal to "myvariant" and
        #   `self.mongo_collection_name` equal to `self.build_doc["_id"]`
        #
        #   mongo_client = MongoClient(**self.mongo_client_args)
        #   mongo_database = mongo_client[self.mongo_database_name]
        #   mongo_collection = mongo_database[self.mongo_collection_name]
        #
        # TODO revise if https://github.com/biothings/biothings.api/issues/238 fixed
        src_build_collection = get_src_build()
        self.logger.debug(f"{src_build_collection.database.client}")
        self.logger.debug(f"{src_build_collection.full_name}")

        self.logger.info(f"_meta.stats of document {self.build_doc['_id']} is {self.build_doc['_meta']['stats']} "
                         f"before post-index update")
        self.build_doc["_meta"]["stats"] = meta_stats
        result = src_build_collection.replace_one({"_id": self.build_doc["_id"]}, self.build_doc)

        if result.matched_count != 1:
            raise ValueError(f"cannot find document {self.build_doc['_id']} "
                             f"in collection {src_build_collection.full_name}")

        if result.modified_count != 1:
            raise ValueError(f"failed to update _meta.stats for document {self.build_doc['_id']} "
                             f"in collection {src_build_collection.full_name}")

        self.logger.info(f"_meta.stats updated to {meta_stats} for document {self.build_doc['_id']} "
                         f"in collection {src_build_collection.full_name}")

        return meta_stats


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
    INDEXER = BaseVariantIndexer
