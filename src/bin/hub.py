#!/usr/bin/env python

import os, logging
from functools import partial

# shut some mouths...
logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("boto").setLevel(logging.ERROR)
logging.getLogger("parso.cache").setLevel(logging.ERROR)


import config, biothings
from biothings.utils.version import set_versions
app_folder,_src = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
set_versions(config,app_folder)
biothings.config_for_app(config)

from biothings.hub import HubServer
import biothings.hub.databuild.builder as builder
import biothings.hub.databuild.differ as differ
import biothings.hub.databuild.syncer as syncer

from hub.databuild.builder import MyVariantDataBuilder, MyVariantShardedDataBuilder
from hub.dataindex.indexer import MyVariantIndexerManager
from hub.databuild.differ import MyVariantDifferManager
from hub.databuild.mapper import TagObserved, TagObservedAndSkipLongId
from hub.databuild.syncer import MyVariantThrottledESColdHotJsonDiffSelfContainedSyncer, MyVariantThrottledESJsonDiffSelfContainedSyncer, \
                                 MyVariantESColdHotJsonDiffSelfContainedSyncer, MyVariantESJsonDiffSelfContainedSyncer

from biothings.hub import CommandDefinition
import biothings.utils.mongo as mongo


class MyVariantHubServer(HubServer):

    # specific commands
    def snpeff(self, build_name=None, sources=[], force_use_cache=True):
        """
        Shortcut to run snpeff on all sources given a build_name
        or a list of source names will process sources one by one
        Since it's particularly useful when snpeff data needs reprocessing

        force_use_cache=True is used to make sure all cache files are used to
        speed up, while source is actually being postprocessed. We're assuming
        data hasn't changed and there's no new _ids since the last time source
        was processed.
        """
        if build_name:
            sources = mongo.get_source_fullnames(self.managers["build_manager"].list_sources(build_name))
        else:
            sources = mongo.get_source_fullnames(sources)
        # remove any snpeff related collection
        sources = [src for src in sources if not src.startswith("snpeff")]
        self.logger.info("Sequentially running snpeff on %s" % repr(sources))
        @asyncio.coroutine
        def do(srcs):
            for src in srcs:
                self.logger.info("Running snpeff on '%s'" % src)
                job = self.managers["upload_manager"].upload_src(src,steps="post",force_use_cache=force_use_cache)
                yield from asyncio.wait(job)
        task = asyncio.ensure_future(do(sources))
        return task

    def rebuild_cache(self, build_name=None, sources=None, target=None, force_build=False):
        """Rebuild cache files for all sources involved in build_name, as well as 
        the latest merged collection found for that build"""
        if build_name:
            sources = mongo.get_source_fullnames(self.managers["build_manager"].list_sources(build_name))
            target = mongo.get_latest_build(build_name)
        elif sources:
            sources = mongo.get_source_fullnames(sources)
        if not sources and not target:
            raise Exception("No valid sources found")

        def rebuild(col):
            cur = mongo.id_feeder(col,batch_size=10000,logger=self.logger,force_build=force_build)
            [i for i in cur] # just iterate

        @asyncio.coroutine
        def do(srcs,tgt):
            pinfo = {"category" : "cache",
                    "source" : None,
                    "step" : "rebuild",
                    "description" : ""}
            self.logger.info("Rebuild cache for sources: %s, target: %s" % (srcs,tgt))
            for src in srcs:
                # src can be a full name (eg. clinvar.clinvar_hg38) but id_feeder knows only name (clinvar_hg38)
                if "." in src:
                    src = src.split(".")[1]
                self.logger.info("Rebuilding cache for source '%s'" % src)
                col = mongo.get_src_db()[src]
                pinfo["source"] = src
                job = yield from self.managers["job_manager"].defer_to_thread(pinfo, partial(rebuild,col))
                yield from job
                self.logger.info("Done rebuilding cache for source '%s'" % src)
            if tgt:
                self.logger.info("Rebuilding cache for target '%s'" % tgt)
                col = mongo.get_target_db()[tgt]
                pinfo["source"] = tgt
                job = self.managers["job_manager"].defer_to_thread(pinfo, partial(rebuild,col))
                yield from job

        task = asyncio.ensure_future(do(sources,target))
        return task

    def configure_build_manager(self):
        observed = TagObserved(name="observed")
        observed_skipidtoolong = TagObservedAndSkipLongId(name="observed_skipidtoolong")
        mvbuilder = partial(MyVariantDataBuilder,mappers=[observed,observed_skipidtoolong])
        sharded_mvbuilder = partial(MyVariantShardedDataBuilder,mappers=[observed,observed_skipidtoolong])
        build_manager = builder.BuilderManager(
                builder_class=[mvbuilder,sharded_mvbuilder],
                job_manager=self.managers["job_manager"])
        build_manager.configure()
        self.managers["build_manager"] = build_manager
        self.logger.info("Using custom builder %s" % MyVariantDataBuilder)

    def configure_diff_manager(self):
        diff_manager = MyVariantDifferManager(job_manager=self.managers["job_manager"],
                poll_schedule="* * * * * */10")
        diff_manager.configure([differ.ColdHotSelfContainedJsonDiffer,differ.SelfContainedJsonDiffer])
        # autmoate release note generation when a diff has been generated,
        # but don't necessarily trigger a diff once a merge has been built, it may be too big
        # and may not qualify for a diff release
        diff_manager.poll("release_note",lambda doc: diff_manager.release_note(old=None,new=doc["_id"]))
        self.managers["diff_manager"] = diff_manager
        self.logger.info("Using custom diff_manager %s" % diff_manager)

    def configure_sync_manager(self):
        sync_manager_prod = syncer.SyncerManager(job_manager=self.managers["job_manager"])
        sync_manager_prod.configure(klasses=[partial(MyVariantThrottledESColdHotJsonDiffSelfContainedSyncer,config.MAX_SYNC_WORKERS),
                                               partial(MyVariantThrottledESJsonDiffSelfContainedSyncer,config.MAX_SYNC_WORKERS)])
        self.managers["sync_manager"] = sync_manager_prod
        sync_manager_test = syncer.SyncerManager(job_manager=self.managers["job_manager"])
        sync_manager_test.configure(klasses=[MyVariantESColdHotJsonDiffSelfContainedSyncer,MyVariantESJsonDiffSelfContainedSyncer])
        self.managers["sync_manager_test"] = sync_manager_test
        self.logger.info("Using custom syncer, prod(throttled): %s, test: %s" % (sync_manager_prod,sync_manager_test))

    def configure_commands(self):
        super().configure_commands() # keep all originals...
        # custom
        self.commands["snpeff"] = self.snpeff
        self.commands["rebuild_cache"] = self.rebuild_cache
        # merge
        self.commands["premerge"] = partial(self.managers["build_manager"].merge,steps=["merge","metadata"])
        # sync

        def select_index(env, asm):
            return [idx for idx in config.INDEX_CONFIG["env"][env]["index"] if asm in idx][0]

        # first test index from config
        test_index_hg19 = select_index("local","hg19")
        test_index_hg38 = select_index("local","hg38")
        self.commands["es_sync_hg19_test"] = partial(self.managers["sync_manager_test"].sync,"es",
                                                target_backend=(config.INDEX_CONFIG["env"]["local"]["host"],
                                                                test_index_hg19["index"],
                                                                test_index_hg19["doc_type"]))
        self.commands["es_sync_hg38_test"] = partial(self.managers["sync_manager_test"].sync,"es",
                                                target_backend=(config.INDEX_CONFIG["env"]["local"]["host"],
                                                                test_index_hg38["index"],
                                                                test_index_hg38["doc_type"]))

        # first prod index from config
        prod_index_hg19 = select_index("prod","hg19")
        prod_index_hg38 = select_index("prod","hg38")
        self.commands["es_sync_hg19_prod"] = partial(self.managers["sync_manager"].sync,"es",
                                                target_backend=(config.INDEX_CONFIG["env"]["prod"]["host"],
                                                                prod_index_hg19["index"],
                                                                prod_index_hg19["doc_type"]))
        self.commands["es_sync_hg38_prod"] = partial(self.managers["sync_manager"].sync,"es",
                                                target_backend=(config.INDEX_CONFIG["env"]["prod"]["host"],
                                                                prod_index_hg38["index"],
                                                                prod_index_hg38["doc_type"]))
        # snapshot, diff & publish
        #self.commands["snapshot_demo"] = partial(self.managers["index_manager"].snapshot,repository=config.SNAPSHOT_REPOSITORY + "-demo")
        ## override with diff type
        #self.commands["diff_prod"] = partial(self.managers["diff_manager"].diff,differ.ColdHotSelfContainedJsonDiffer.diff_type)
        #self.commands["diff_demo"] = partial(self.managers["diff_manager"].diff,differ.SelfContainedJsonDiffer.diff_type)
        #self.commands["publish_diff_hg19"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER + "-hg19")
        #self.commands["publish_diff_hg38"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER + "-hg38")
        #self.commands["publish_snapshot_hg19"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER + "-hg19")
        #self.commands["publish_snapshot_hg38"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER + "-hg38")
        #self.commands["publish_diff_demo_hg19"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER + "-demo_hg19",
        #                                        s3_bucket=config.S3_DIFF_BUCKET + "-demo")
        #self.commands["publish_diff_demo_hg38"] = partial(self.managers["diff_manager"].publish_diff,config.S3_APP_FOLDER + "-demo_hg38",
        #                                        s3_bucket=config.S3_DIFF_BUCKET + "-demo")
        #self.commands["publish_snapshot_demo_hg19"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER + "-demo_hg19",
        #                                                                                repository=config.READONLY_SNAPSHOT_REPOSITORY + "-demo")
        #self.commands["publish_snapshot_demo_hg38"] = partial(self.managers["index_manager"].publish_snapshot,s3_folder=config.S3_APP_FOLDER + "-demo_hg38",
        #                                                                        repository=config.READONLY_SNAPSHOT_REPOSITORY + "-demo")


import hub.dataload
# pass explicit list of datasources (no auto-discovery)
server = MyVariantHubServer(config.ACTIVE_DATASOURCES, name="MyVariant.info")


if __name__ == "__main__":
    server.start()

