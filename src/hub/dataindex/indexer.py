import os
import asyncio

import config
import biothings.hub.dataindex.indexer as indexer
from biothings.hub.dataexport.ids import export_ids, upload_ids
from biothings.utils.hub_db import get_src_build


class BaseVariantIndexer(indexer.Indexer):
    
    def enrich_final_mapping(self,final_mapping):
        # enrich with myvariant specific stuff
        final_mapping["properties"]["chrom"] = {
            'analyzer': 'string_lowercase',
            'type': 'text'}
        final_mapping["properties"]["observed"] = {
            "type": "boolean"}
        return final_mapping

    def get_index_creation_settings(self):
        settings = super(BaseVariantIndexer,self).get_index_creation_settings()
        settings.setdefault("mapping",{}).setdefault("total_fields",{})["limit"] = 2000
        return settings


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
    
    
