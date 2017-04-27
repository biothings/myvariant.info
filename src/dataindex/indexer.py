import os
import asyncio

import config
import biothings.dataindex.indexer as indexer
from biothings.utils.aws import send_s3_file


class VariantIndexer(indexer.Indexer):

    def get_mapping(self, enable_timestamp=True):
        mapping = super(VariantIndexer,self).get_mapping(enable_timestamp=enable_timestamp)
        # enrich with myvariant specific stuff
        mapping["properties"]["chrom"] = {
            'analyzer': 'string_lowercase',
            'include_in_all': False,
            'type': 'string'}
        mapping["properties"]["observed"] = {
            "type": "boolean",
            'include_in_all': False}

        return mapping

    def get_index_creation_settings(self):
        return {"codec" : "best_compression"}

    def post_index(self, target_name, index_name, job_manager, steps=["index","post"], batch_size=10000, ids=None, mode=None):
        # cache file should be named the same as target_name
        asyncio.set_event_loop(job_manager.loop)
        cache_file = os.path.join(config.CACHE_FOLDER,target_name)
        if getattr(config,"CACHE_FORMAT",None):
            cache_file += "." + config.CACHE_FORMAT
        if not os.path.exists(cache_file):
            raise FileNotFoundError("Can't find cache file '%s'" % cache_file)
        self.logger.info("Upload _id cache file '%s' to s3" % cache_file)
        try:
            send_s3_file(cache_file,os.path.join(config.S3_FOLDER,os.path.basename(cache_file)),overwrite=True)
            self.logger.info("Cache file '%s' uploaded to s3" % cache_file, extra={"notify":True})
        except Exception as e:
            self.logger.error("Failed to upload cache file '%s' to s3: %s" % (cache_file,e), extra={"notify":True})
            raise

