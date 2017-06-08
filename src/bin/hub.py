#!/usr/bin/env python

import asyncio, asyncssh, sys
import concurrent.futures
from functools import partial

import config, biothings
biothings.config_for_app(config)

from biothings.utils.manager import JobManager
loop = asyncio.get_event_loop()
process_queue = concurrent.futures.ProcessPoolExecutor(max_workers=config.HUB_MAX_WORKERS)
thread_queue = concurrent.futures.ThreadPoolExecutor()
loop.set_default_executor(process_queue)
max_mem = type(config.HUB_MAX_MEM_USAGE) == int and config.HUB_MAX_MEM_USAGE * 1024**3 or config.HUB_MAX_MEM_USAGE
job_manager = JobManager(loop,
                      process_queue, thread_queue,
                      max_memory_usage=max_mem,
                      )

import dataload
import biothings.dataload.uploader as uploader
import biothings.dataload.dumper as dumper
import biothings.databuild.builder as builder
import biothings.databuild.differ as differ
import biothings.databuild.syncer as syncer
import biothings.dataindex.indexer as indexer
from databuild.builder import MyVariantDataBuilder
from databuild.mapper import TagObserved
from dataindex.indexer import VariantIndexer

# will check every 10 seconds for sources to upload
upload_manager = uploader.UploaderManager(poll_schedule = '* * * * * */10', job_manager=job_manager)
upload_manager.register_sources(dataload.__sources_dict__)
upload_manager.poll()

dmanager = dumper.DumperManager(job_manager=job_manager)
dmanager.register_sources(dataload.__sources_dict__)
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

pindexer = partial(VariantIndexer,es_host=config.ES_HOST)
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


from biothings.utils.hub import schedule, top, pending, done

COMMANDS = {
        # dump commands
        "dm" : dmanager,
        "dump" : dmanager.dump_src,
        "dump_all" : dmanager.dump_all,
        # upload commands
        "um" : upload_manager,
        "upload" : upload_manager.upload_src,
        "upload_all": upload_manager.upload_all,
        "snpeff": snpeff,
        "rebuild_cache": rebuild_cache,
        # building/merging
        "bm" : build_manager,
        "merge" : build_manager.merge,
        "mongo_sync" : partial(syncer_manager.sync,"mongo"),
        "es_sync" : partial(syncer_manager.sync,"es"),
        "es_sync_hg19_test" : partial(syncer_manager.sync,"es",target_backend=config.ES_TEST_HG19),
        "es_sync_hg38_test" : partial(syncer_manager.sync,"es",target_backend=config.ES_TEST_HG38),
        "es_sync_hg19_prod" : partial(syncer_manager.sync,"es",target_backend=config.ES_PROD_HG19),
        "es_sync_hg38_prod" : partial(syncer_manager.sync,"es",target_backend=config.ES_PROD_HG38),
        "es_prod": {"hg19":config.ES_PROD_HG19,"hg38":config.ES_PROD_HG38},
        "es_test": {"hg19":config.ES_TEST_HG19,"hg38":config.ES_TEST_HG38},
        "sm" : syncer_manager,
        # diff
        "dim" : differ_manager,
        "diff" : partial(differ_manager.diff,"jsondiff"),
        "report": differ_manager.diff_report,
        # indexing commands
        "im" : index_manager,
        "index" : index_manager.index,
        "snapshot" : index_manager.snapshot,
        # admin/advanced
        "loop" : loop,
        "pqueue" : process_queue,
        "tqueue" : thread_queue,
        "g": globals(),
        "sch" : partial(schedule,loop),
        "top" : partial(top,process_queue,thread_queue),
        "pending" : pending,
        "done" : done,
        }

passwords = {
        'guest': '', # guest account with no password
        }

from biothings.utils.hub import start_server

server = start_server(loop,"MyVariant hub",passwords=passwords,port=config.SSH_HUB_PORT,commands=COMMANDS)

try:
    loop.run_until_complete(server)
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()

