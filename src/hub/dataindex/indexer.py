import os
import asyncio
from boto import connect_s3

import config
import biothings.hub.dataindex.indexer as indexer
from biothings.utils.aws import send_s3_file


class VariantIndexer(indexer.Indexer):

    def get_mapping(self):
        mapping = super(VariantIndexer,self).get_mapping()
        # enrich with myvariant specific stuff
        mapping["properties"]["chrom"] = {
            'analyzer': 'string_lowercase',
            'type': 'text'}
        mapping["properties"]["observed"] = {
            "type": "boolean"}

        return mapping

    def get_index_creation_settings(self):
        settings = super(VariantIndexer,self).get_index_creation_settings()
        return settings

    # TODO: that should done during release publishing, whether it's from an index or diff
    #def post_index(self, target_name, index_name, job_manager, steps=["index","post"], batch_size=10000, ids=None, mode=None):
    #    # cache file should be named the same as target_name
    #    asyncio.set_event_loop(job_manager.loop)
    #    cache_file = os.path.join(config.CACHE_FOLDER,target_name)
    #    if getattr(config,"CACHE_FORMAT",None):
    #        cache_file += "." + config.CACHE_FORMAT
    #    if not os.path.exists(cache_file):
    #        raise FileNotFoundError("Can't find cache file '%s'" % cache_file)
    #    self.logger.info("Upload _id cache file '%s' to s3" % cache_file)
    #    try:
    #        s3path = os.path.basename(cache_file)
    #        send_s3_file(cache_file, s3path, overwrite=True)
    #        # make the file public
    #        s3 = connect_s3(config.AWS_KEY, config.AWS_SECRET) 
    #        bucket = s3.get_bucket(config.S3_BUCKET)
    #        s3key = bucket.get_key(s3path)
    #        s3key.set_acl("public-read")
    #        # update permissions and redirect metadata
    #        if "hg19" in s3path:
    #            k = bucket.get_key("myvariant_hg19_ids.xz")
    #        else:
    #            k = bucket.get_key("myvariant_hg38_ids.xz")
    #        k.set_redirect("/%s" % s3path)
    #        k.set_acl("public-read")
    #        self.logger.info("Cache file '%s' uploaded to s3" % cache_file, extra={"notify":True})
    #    except Exception as e:
    #        self.logger.error("Failed to upload cache file '%s' to s3: %s" % (cache_file,e), extra={"notify":True})
    #        raise

