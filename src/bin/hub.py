#!/usr/bin/env python

import asyncio, asyncssh, sys, os
import concurrent.futures
from functools import partial
from collections import OrderedDict

import config, biothings
biothings.config_for_app(config)

import logging
# shut some mouths...
logging.getLogger("elasticsearch").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("boto").setLevel(logging.ERROR)

logging.info("Hub DB backend: %s" % biothings.config.HUB_DB_BACKEND)
logging.info("Hub database: %s" % biothings.config.DATA_HUB_DB_DATABASE)

from biothings.utils.manager import JobManager
loop = asyncio.get_event_loop()
process_queue = concurrent.futures.ProcessPoolExecutor(max_workers=config.HUB_MAX_WORKERS)
thread_queue = concurrent.futures.ThreadPoolExecutor()
loop.set_default_executor(process_queue)
job_manager = JobManager(loop,num_workers=config.HUB_MAX_WORKERS,
                      max_memory_usage=config.HUB_MAX_MEM_USAGE)

import hub.dataload
import biothings.hub.dataload.uploader as uploader
import biothings.hub.dataload.dumper as dumper
import biothings.hub.databuild.builder as builder
import biothings.hub.databuild.differ as differ
import biothings.hub.databuild.syncer as syncer
import biothings.hub.dataindex.indexer as indexer
from hub.databuild.builder import MyVariantDataBuilder
from hub.databuild.mapper import TagObserved
from hub.dataindex.indexer import VariantIndexer

# will check every 10 seconds for sources to upload
upload_manager = uploader.UploaderManager(poll_schedule = '* * * * * */10', job_manager=job_manager)
upload_manager.register_sources(hub.dataload.__sources_dict__)
upload_manager.poll('upload',lambda doc: upload_manager.upload_src(doc["_id"]))

dmanager = dumper.DumperManager(job_manager=job_manager)
dmanager.register_sources(hub.dataload.__sources_dict__)
dmanager.schedule_all()

observed = TagObserved(name="observed")
build_manager = builder.BuilderManager(
        builder_class=partial(MyVariantDataBuilder,mappers=[observed]),
        job_manager=job_manager)
build_manager.configure()

differ_manager = differ.DifferManager(job_manager=job_manager)
differ_manager.configure()
syncer_manager = syncer.SyncerManager(job_manager=job_manager)
syncer_manager.configure()

pindexer = partial(VariantIndexer,es_host=config.ES_HOST,
                   timeout=config.ES_TIMEOUT,max_retries=config.ES_MAX_RETRY,
                   retry_on_timeout=config.ES_RETRY)
index_manager = indexer.IndexerManager(pindexer=pindexer,
        job_manager=job_manager)
index_manager.configure()

import biothings.utils.mongo as mongo
def snpeff(build_name=None,sources=[], force_use_cache=True):
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
        sources = mongo.get_source_fullnames(build_manager.list_sources(build_name))
    else:
        sources = mongo.get_source_fullnames(sources)
    # remove any snpeff related collection
    sources = [src for src in sources if not src.startswith("snpeff")]
    config.logger.info("Sequentially running snpeff on %s" % repr(sources))
    @asyncio.coroutine
    def do(srcs):
        for src in srcs:
            config.logger.info("Running snpeff on '%s'" % src)
            job = upload_manager.upload_src(src,steps="post",force_use_cache=force_use_cache)
            yield from asyncio.wait(job)
    task = asyncio.ensure_future(do(sources))
    return task

def rebuild_cache(build_name=None,sources=None,target=None,force_build=False):
    """Rebuild cache files for all sources involved in build_name, as well as 
    the latest merged collection found for that build"""
    if build_name:
        sources = mongo.get_source_fullnames(build_manager.list_sources(build_name))
        target = mongo.get_latest_build(build_name)
    elif sources:
        sources = mongo.get_source_fullnames(sources)
    if not sources and not target:
        raise Exception("No valid sources found")

    def rebuild(col):
        cur = mongo.id_feeder(col,batch_size=10000,logger=config.logger,force_build=force_build)
        [i for i in cur] # just iterate

    @asyncio.coroutine
    def do(srcs,tgt):
        pinfo = {"category" : "cache",
                "source" : None,
                "step" : "rebuild",
                "description" : ""}
        config.logger.info("Rebuild cache for sources: %s, target: %s" % (srcs,tgt))
        for src in srcs:
            # src can be a full name (eg. clinvar.clinvar_hg38) but id_feeder knows only name (clinvar_hg38)
            if "." in src:
                src = src.split(".")[1]
            config.logger.info("Rebuilding cache for source '%s'" % src)
            col = mongo.get_src_db()[src]
            pinfo["source"] = src
            job = yield from job_manager.defer_to_thread(pinfo, partial(rebuild,col))
            yield from job
            config.logger.info("Done rebuilding cache for source '%s'" % src)
        if tgt:
            config.logger.info("Rebuilding cache for target '%s'" % tgt)
            col = mongo.get_target_db()[tgt]
            pinfo["source"] = tgt
            job = job_manager.defer_to_thread(pinfo, partial(rebuild,col))
            yield from job

    task = asyncio.ensure_future(do(sources,target))
    return task


from biothings.utils.hub import schedule, pending, done

COMMANDS = OrderedDict()
# dump commands
COMMANDS["dump"] = dmanager.dump_src
COMMANDS["dump_all"] = dmanager.dump_all
# upload commands
COMMANDS["upload"] = upload_manager.upload_src
COMMANDS["upload_all"] = upload_manager.upload_all
COMMANDS["snpeff"] = snpeff
COMMANDS["rebuild_cache"] = rebuild_cache
# building/merging
COMMANDS["merge"] = build_manager.merge
COMMANDS["premerge"] = partial(build_manager.merge,steps=["merge","metadata"])
COMMANDS["es_sync_hg19_test"] = partial(syncer_manager.sync,"es",target_backend=config.ES_TEST_HG19)
COMMANDS["es_sync_hg38_test"] = partial(syncer_manager.sync,"es",target_backend=config.ES_TEST_HG38)
COMMANDS["es_sync_hg19_prod"] = partial(syncer_manager.sync,"es",target_backend=config.ES_PROD_HG19)
COMMANDS["es_sync_hg38_prod"] = partial(syncer_manager.sync,"es",target_backend=config.ES_PROD_HG38)
COMMANDS["es_prod"] = {"hg19":config.ES_PROD_HG19,"hg38":config.ES_PROD_HG38}
COMMANDS["es_test"] = {"hg19":config.ES_TEST_HG19,"hg38":config.ES_TEST_HG38}
# diff
COMMANDS["diff"] = partial(differ_manager.diff,"jsondiff-selfcontained")
COMMANDS["report"] = differ_manager.diff_report
COMMANDS["release_note"] = differ_manager.release_note
COMMANDS["publish_diff_hg19"] = partial(differ_manager.publish_diff,config.S3_APP_FOLDER % "hg19")
COMMANDS["publish_diff_hg38"] = partial(differ_manager.publish_diff,config.S3_APP_FOLDER % "hg38")
# indexing commands
COMMANDS["index"] = index_manager.index
COMMANDS["snapshot"] = index_manager.snapshot
COMMANDS["publish_snapshot_hg19"] = partial(index_manager.publish_snapshot,config.S3_APP_FOLDER % "hg19")
COMMANDS["publish_snapshot_hg38"] = partial(index_manager.publish_snapshot,config.S3_APP_FOLDER % "hg38")

# admin/advanced
EXTRA_NS = {
        "dm" : dmanager,
        "um" : upload_manager,
        "bm" : build_manager,
        "dim" : differ_manager,
        "sm" : syncer_manager,
        "im" : index_manager,
        "mongo_sync" : partial(syncer_manager.sync,"mongo"),
        "es_sync" : partial(syncer_manager.sync,"es"),
        "loop" : loop,
        "pqueue" : process_queue,
        "tqueue" : thread_queue,
        "g": globals(),
        "sch" : partial(schedule,loop),
        "top" : job_manager.top,
        "pending" : pending,
        "done" : done,
        }

passwords = {
        'guest': '', # guest account with no password
        }

from biothings.utils.hub import start_server

server = start_server(loop,"MyVariant hub",passwords=passwords,
    port=config.HUB_SSH_PORT,commands=COMMANDS,extra_ns=EXTRA_NS)

try:
    loop.run_until_complete(server)
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()

