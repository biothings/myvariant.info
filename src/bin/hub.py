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
build_manager.sync()

differ_manager = differ.DifferManager(job_manager=job_manager)
differ_manager.sync()

pindexer = partial(VariantIndexer,es_host=config.ES_HOST)
index_manager = indexer.IndexerManager(pindexer=pindexer,
        job_manager=job_manager)
index_manager.sync()

import biothings.utils.mongo as mongo
def snpeff(build_name=None,sources=[]):
    """Shortcut to run snpeff on all sources given a build_name
    or a list of source names
    will process sources one by one"""
    if build_name:
        sources = mongo.get_source_fullnames(build_manager.list_sources(build_name))
    else:
        sources = mongo.get_source_fullnames(sources)
    config.logger.info("Sequentially running snpeff on %s" % repr(sources))
    @asyncio.coroutine
    def do(srcs):
        for src in srcs:
            config.logger.info("Running snpeff on '%s'" % src)
            job = upload_manager.upload_src(src,steps="post")
            yield from asyncio.wait(job)
    task = asyncio.ensure_future(do(sources))
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
        # building/merging
        "bm" : build_manager,
        "merge" : build_manager.merge,
        # diff
        "dim" : differ_manager,
        "diff" : partial(differ_manager.diff,"jsondiff"),
        "report": differ_manager.diff_report,
        # indexing commands
        "im" : index_manager,
        "index" : index_manager.index,
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

server = start_server(loop, "MyVariant hub",passwords=passwords,port=config.SSH_HUB_PORT,commands=COMMANDS)

try:
    loop.run_until_complete(server)
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error starting server: ' + str(exc))

loop.run_forever()

