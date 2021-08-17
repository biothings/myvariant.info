import time
import asyncio

import config
from biothings.hub.dataindex.indexer import Indexer, IndexManager, ColdHotIndexer
from biothings.hub.dataexport.ids import export_ids, upload_ids
from biothings.utils.hub_db import get_src_build
from biothings.utils.es import ESIndexer
from utils.stats import update_stats


class BaseVariantIndexer(Indexer):

    def __init__(self, build_doc, indexer_env, index_name):
        super().__init__(build_doc, indexer_env, index_name)

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
    def post_index(self):
        # Migrated from Sebastian's commit 1a7b7a
        # It was orginally marked "Not Tested Yet".
        self.logger.info("Sleeping for a bit while index is being fully updated...")
        yield from time.sleep(3*60)
        idxer = ESIndexer(
            index=self.es_index_name,
            doc_type=self.doc_type,
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


class ColdHotVariantIndexer(ColdHotIndexer, BaseVariantIndexer):
    pass
