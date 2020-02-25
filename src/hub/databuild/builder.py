import math
import asyncio
from functools import partial
import datetime, pickle

from biothings.utils.common import iter_n, open_compressed_file
from biothings.utils.mongo import id_feeder
import biothings.utils.mongo as mongo
import biothings.hub.databuild.builder as builder
from biothings.hub.databuild.backend import ShardedTargetDocMongoBackend
import config

class MyVariantDataBuilder(builder.DataBuilder):

    MAX_CHROM_EX = 100000 # if chrom discrepancies found, max # of examples we keep

    def merge(self, sources=None, target_name=None, batch_size=50000, job_manager=None, **kwargs):
        # just override default batch_size or it consumes too much mem
        return super(MyVariantDataBuilder,self).merge(
                sources=sources,
                target_name=target_name,
                job_manager=job_manager,
                batch_size=batch_size,
                **kwargs)

    def validate_merge(self):
        # MyVariant merging either insert or updates. So we can't just count
        # the number of inserted/updated data from single colleciton and compare with
        # the target count.
        total = sum(self.stats.values())
        self.logger.info("Validating...")
        target_cnt = self.target_backend.count()
        if total == 0:
            self.logger.warning("Nothing was inserted in target collection...")
        if target_cnt <= total:
            self.logger.info("OK [total count={} <= sum(total)={}]".format(target_cnt,total))
        else:
            self.logger.warning("Total count of documents {} is greater than what was inserted/updated... {}]".format(target_cnt, total))

    def set_chrom(self, batch_size, job_manager):
        # divide & conquer... build batches
        jobs = []
        total = self.target_backend.count()
        btotal = math.ceil(total/batch_size) 
        bnum = 1
        cnt = 0
        results = {
            "missing" : {
                "count": 0,
                "examples": []
            },
            "disagreed" : {
                "count": 0,
                "examples": []
            }
        }
        root_keys = {}
        # grab ids only, so we can get more and fill queue for each step
        # each round, fill the queue to make sure every cpu slots are always working
        id_batch_size = batch_size * job_manager.process_queue._max_workers * 2
        self.logger.info("Fetch _ids from '%s' with batch_size=%d, and create post-merger job with batch_size=%d" % \
                (self.target_backend.target_collection.name, id_batch_size, batch_size))
        for big_doc_ids in id_feeder(self.target_backend.target_collection, batch_size=id_batch_size, logger=self.logger):
            for doc_ids in iter_n(big_doc_ids,batch_size):
                yield from asyncio.sleep(0.1)
                cnt += len(doc_ids)
                pinfo = self.get_pinfo()
                pinfo["step"] = "post-merge (chrom)"
                pinfo["description"] = "#%d/%d (%.1f%%)" % (bnum,btotal,(cnt/total*100.))
                self.logger.info("Creating post-merge job #%d/%d to process chrom %d/%d (%.1f%%)" % \
                        (bnum,btotal,cnt,total,(cnt/total*100.)))
                job = yield from job_manager.defer_to_process(pinfo,
                        partial(chrom_worker, self.target_backend.target_name, doc_ids))
                def processed(f,results, batch_num):
                    try:
                        fres = f.result()
                        for errtype in ("missing","disagreed"):
                            if fres[errtype]:
                                results[errtype]["count"] += len(fres[errtype])
                                if len(results[errtype]["examples"]) < self.__class__.MAX_CHROM_EX:
                                    results[errtype]["examples"].extend(fres[errtype])
                        # merge root key counts
                        rk = fres["root_keys"]
                        for k in rk:
                            root_keys.setdefault(k,0)
                            root_keys[k] += rk[k]
                        self.logger.info("chrom batch #%d, done" % batch_num)
                    except Exception as e:
                        import traceback
                        self.logger.error("chrom batch #%d, error in processed (set_chrom): %s:\n%s" % \
                                (batch_num, e, traceback.format_exc()))
                        raise
                job.add_done_callback(partial(processed, results=results, batch_num=bnum))
                jobs.append(job)
                bnum += 1
        self.logger.info("%d jobs created for merging step" % len(jobs))
        if jobs:
            yield from asyncio.gather(*jobs)
            self.logger.info("Found %d missing 'chrom' and %d where resources disagreed" % (results["missing"]["count"], results["disagreed"]["count"]))
            if results["missing"]["count"] or results["disagreed"]["count"]:
                fn = "chrom_%s_%s.pickle" % (self.target_backend.target_name,datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                self.logger.info("Pickling 'chrom' discrepancies into %s" % fn)
                pickle.dump(results,open(fn,"wb"))
            # now store metadata
            root_keys["total"] = root_keys.pop("_id")
            self.logger.info("Root keys: %s" % root_keys)
            src_build = self.source_backend.build
            src_build.update({'_id': self.target_backend.target_name},{"$set":{"_meta.stats":root_keys}})

        return results

    def post_merge(self, source_names, batch_size, job_manager):
        self.validate_merge()
        # we're in a new thread (see biothings.databuild.builder, post_merge
        # is called in defer_to_thread)
        asyncio.set_event_loop(job_manager.loop)
        job = self.set_chrom(batch_size, job_manager)
        task = asyncio.ensure_future(job)
        return task

    def get_stats(self,*args,**kwargs):
        # we overide that one just to make sure existing metadata won't be
        # overwritten by the ones coming from the base class (see root_keys in set_chrom())
        return {}

class MyVariantShardedDataBuilder(MyVariantDataBuilder):

    def __init__(self, build_name, source_backend, target_backend, *args, **kwargs):
        shared_tgt_backend = partial(ShardedTargetDocMongoBackend,
                                     target_db=partial(mongo.get_target_db))
        super().__init__(build_name=build_name,
                         source_backend=source_backend,
                         target_backend=shared_tgt_backend,
                         *args,**kwargs)


def get_chrom(doc):
    chrom_keys = set()
    this_chrom = {"chrom" : None, "agreed" : False}
    # Get chrom keys here
    for k in doc:
        if type(doc[k]) == dict and k in config.CHROM_FIELDS and config.CHROM_FIELDS[k] in  doc[k]:
            chrom_field =config.CHROM_FIELDS[k]
            chrom_keys.add(str(doc[k][chrom_field]))
    if len(chrom_keys) == 1:
        this_chrom["chrom"] = chrom_keys.pop()
        this_chrom["agreed"] = True
    elif doc['_id'].startswith('chr'):
        this_chrom["chrom"] = doc['_id'].split(':')[0][3:]
        if chrom_keys:
            this_chrom["agreed"] = False
        else:
            # neither a disagrement or agreement, info is just not there
            # (ie. chrom value could only be determined from _id)
            this_chrom["agreed"] = None
    return this_chrom


def chrom_worker(col_name, ids):
    tgt = mongo.get_target_db()
    col = tgt[col_name]
    cur = col.find({'_id': {'$in': ids}})
    bob = col.initialize_unordered_bulk_op()
    disagreed = []
    missing = []
    root_keys = {}
    at_least_one = False
    for doc in cur:
        dchrom = get_chrom(doc)
        if dchrom["chrom"] is None:
            missing.append(doc["_id"])
        elif dchrom["agreed"] is False:
            disagreed.append(doc["_id"])
        chrom = dchrom["chrom"]
        if chrom:
            bob.find({"_id": doc["_id"]}).update({"$set": {"chrom" : chrom}})
            at_least_one = True
        # count root keys for later metadata
        for k in doc:
            # other root keys are actual sources and
            # are counted under "src" key while merge_stats
            if k in ["_id","vcf","total","hg19","hg38","observed"]:
                root_keys.setdefault(k,0)
                root_keys[k] += 1

    at_least_one and bob.execute()

    return {"missing": missing, "disagreed" : disagreed, "root_keys" : root_keys}

