import os, time
import asyncio

import config
import biothings.hub.dataindex.indexer as indexer
from biothings.hub.dataexport.ids import export_ids, upload_ids
from biothings.utils.hub_db import get_src_build
from biothings.utils.es import ESIndexer
from utils.stats import update_stats


class BaseVariantIndexer(indexer.Indexer):
    
    def enrich_final_mapping(self,final_mapping):
        # enrich with myvariant specific stuff
        final_mapping["properties"]["chrom"] = {
            'analyzer': 'string_lowercase',
            'type': 'text'}
        final_mapping["properties"]["observed"] = {
            "type": "boolean"}
        final_mapping["properties"]["_seqhashed"] = {
            "type": "boolean"}

        return final_mapping

    def get_index_creation_settings(self):
        settings = super(BaseVariantIndexer,self).get_index_creation_settings()
        settings.setdefault("mapping",{}).setdefault("total_fields",{})["limit"] = 2000
        return settings

    def post_index(self, target_name, index_name, job_manager, steps=["index","post"], batch_size=10000, ids=None, mode=None): 
        # TODO: not tested yet
        self.logger.info("Sleeping for a bit while index is being fully updated...")
        time.sleep(3*60)
        idxer = ESIndexer(index=index_name,doc_type=self.doc_type,es_host=self.host)
        self.logger.info("Updating 'stats' by querying index '%s'" % index_name)
        assembly = self.build_config["assembly"]
        return update_stats(idxer,assembly)


class MyVariantIndexerManager(indexer.IndexerManager):

    def post_publish(self, snapshot, index, *args, **kwargs):
        # assuming build name == index name, and assuming demo index has
        # "demo" in its name...
        # assuming full index, not demo, guess name now
        bdoc = get_src_build().find_one({"_id" : index})
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

class ColdHotVariantIndexer(indexer.ColdHotIndexer,BaseVariantIndexer):
    pass
    
    
