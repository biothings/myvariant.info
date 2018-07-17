import os, json
import asyncio
from functools import partial

import biothings.hub.databuild.syncer as syncer
from biothings.hub.databuild.backend import create_backend
from utils.stats import update_stats

class MyVariantBaseSyncer(syncer.BaseSyncer):

    def post_sync_cols(self, diff_folder, batch_size, mode, force, target_backend,steps):
        assert self.target_backend_type == "es", "Only support ElasticSearch backend (got: %s)" % self.target_backend_type
        assert not self._meta is None, "Metadata not loaded (use load_metadata(diff_folder))"
        backend_info = self.get_target_backend()
        self.logger.info("Updating 'stats' by querying index '%s'" % backend_info[1])
        indexer = create_backend(backend_info).target_esidxer
        # compute stats using ES index
        assembly = self._meta["build_config"]["assembly"]
        return update_stats(indexer,assembly)

class MyVariantThrottledESJsonDiffSelfContainedSyncer(MyVariantBaseSyncer,syncer.ThrottledESJsonDiffSelfContainedSyncer):
    pass

class MyVariantThrottledESColdHotJsonDiffSelfContainedSyncer(MyVariantBaseSyncer,syncer.ThrottledESColdHotJsonDiffSelfContainedSyncer):
    pass

class MyVariantESColdHotJsonDiffSelfContainedSyncer(MyVariantBaseSyncer,syncer.ESColdHotJsonDiffSelfContainedSyncer):
    pass

class MyVariantESJsonDiffSelfContainedSyncer(MyVariantBaseSyncer,syncer.ESJsonDiffSelfContainedSyncer):
    pass
