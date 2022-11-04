import math
import asyncio
from functools import partial
import datetime
import pickle

from biothings.utils.common import iter_n
from biothings.utils.mongo import id_feeder, get_target_db, Database, Collection
from pymongo import UpdateOne
from biothings.hub.databuild.builder import DataBuilder
from biothings.hub.databuild.backend import ShardedTargetDocMongoBackend
import config


class MyVariantDataBuilder(DataBuilder):
    MAX_CHROM_EX = 100000  # if chrom discrepancies found, max # of examples we keep

    def merge(self, sources=None, target_name=None, batch_size=50000, job_manager=None, **kwargs):
        # just override default batch_size, or it consumes too much mem
        return super(MyVariantDataBuilder, self).merge(sources=sources, target_name=target_name, job_manager=job_manager, batch_size=batch_size, **kwargs)

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
            self.logger.info("OK [total count={} <= sum(total)={}]".format(target_cnt, total))
        else:
            self.logger.warning("Total count of documents {} is greater than what was inserted/updated... {}]".format(target_cnt, total))

    async def set_chrom(self, batch_size, job_manager):
        # divide & conquer... build batches
        jobs = []
        total = self.target_backend.count()
        btotal = math.ceil(total / batch_size)
        bnum = 1
        cnt = 0
        results = {
            "missing": {
                "count": 0,
                "examples": []
            },
            "disagreed": {
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
            for doc_ids in iter_n(big_doc_ids, batch_size):
                cnt += len(doc_ids)
                pinfo = self.get_pinfo()
                pinfo["step"] = "post-merge (chrom)"
                pinfo["description"] = "#%d/%d (%.1f%%)" % (bnum, btotal, (cnt / total * 100.))
                self.logger.info("Creating post-merge job #%d/%d to process chrom %d/%d (%.1f%%)" % \
                                 (bnum, btotal, cnt, total, (cnt / total * 100.)))
                job = await job_manager.defer_to_process(pinfo, partial(chrom_worker, self.target_backend.target_name, doc_ids))

                def processed(f, results, batch_num):
                    try:
                        fres = f.result()
                        for errtype in ("missing", "disagreed"):
                            if fres[errtype]:
                                results[errtype]["count"] += len(fres[errtype])
                                if len(results[errtype]["examples"]) < self.__class__.MAX_CHROM_EX:
                                    results[errtype]["examples"].extend(fres[errtype])
                        # merge root key counts
                        rk = fres["root_keys"]
                        for k in rk:
                            root_keys.setdefault(k, 0)
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
            await asyncio.gather(*jobs)
            self.logger.info("Found %d missing 'chrom' and %d where resources disagreed" % (results["missing"]["count"], results["disagreed"]["count"]))
            if results["missing"]["count"] or results["disagreed"]["count"]:
                fn = "chrom_%s_%s.pickle" % (self.target_backend.target_name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                self.logger.info("Pickling 'chrom' discrepancies into %s" % fn)
                pickle.dump(results, open(fn, "wb"))
            # now store metadata
            root_keys["total"] = root_keys.pop("_id")
            self.logger.info("Root keys: %s" % root_keys)
            src_build = self.source_backend.build
            src_build.update({'_id': self.target_backend.target_name}, {"$set": {"_meta.stats": root_keys}})

        return results

    def post_merge(self, source_names, batch_size, job_manager):
        self.validate_merge()
        # we're in a new thread (see biothings.databuild.builder, post_merge is called in defer_to_thread)
        asyncio.set_event_loop(job_manager.loop)
        job = self.set_chrom(batch_size, job_manager)
        # since we are in a new thread, we cannot use asyncio.create_task() here
        # see https://docs.python.org/3/library/asyncio-dev.html#concurrency-and-multithreading
        task = asyncio.run_coroutine_threadsafe(job, job_manager.loop)
        return task

    def get_stats(self, *args, **kwargs):
        # we overide that one just to make sure existing metadata won't be
        # overwritten by the ones coming from the base class (see root_keys in set_chrom())
        return {}


class MyVariantShardedDataBuilder(MyVariantDataBuilder):
    """
    Data builder using sharded MongoDB cluster
    """

    def __init__(self, build_name, source_backend, target_backend, *args, **kwargs):
        shared_tgt_backend = partial(ShardedTargetDocMongoBackend,
                                     target_db=partial(get_target_db))
        super().__init__(build_name=build_name,
                         source_backend=source_backend,
                         target_backend=shared_tgt_backend,
                         *args, **kwargs)


def inspect_chrom(doc: dict):
    """
    doc is a merged document stored in "<build_name>" collection (e.g. "warm_hg19_20210722_yz5tmmal") of "myvariant" database (e.g. on su09:27017).
    Example:
        {
            "_id": "chrX:g.1337588C>A",
            "cadd": { ... },
            "dbsnp": { ... },
            "observed": true,
            "gnomad_genome": { ... },
            "hg19": { ... },
            "snpeff": { ... },
            "vcf": { ... },
        }
    A purpose of "chrom_worker" is to add a top-level "chrom" field to every such doc, while "inspect_chrom" is to find if all the second-level "chrom" fields
    are in consistency.
    """

    """
    "chrom" is determined in the following order:
    
    1. use the commonly shared second-level chrom value across all datasources, if any
    2. if there are multiple or none second-level chrom values found, infer from the id (like "chrX" from "chrX:g.1337588C>A")
    3. use None, if it's impossible to infer from the id
    
    "agreed" is an indicator of consistency of the second-level "chrom" values. It could be:
    
    1. True, if there exists a commonly shared second-level chrom value
    2. False, if there exist multiple second-level chrom values (and in this case the "chrom" is inferred from the id)
    3. None, if no second-level chrom values exist 
    """
    result = {"chrom": None, "agreed": False}

    # Get second-level chrom values
    chrom_values = set()
    for k in doc:
        # config.CHROM_FIELDS is a dict of <datasource_name: chrom_field_name>. E.g.CHROM_FIELDS = {'cadd': 'chrom', 'clinvar': 'chrom'}.
        if type(doc[k]) == dict and k in config.CHROM_FIELDS and config.CHROM_FIELDS[k] in doc[k]:
            chrom_field_name = config.CHROM_FIELDS[k]
            chrom_values.add(str(doc[k][chrom_field_name]))

    if len(chrom_values) == 1:
        result["chrom"] = chrom_values.pop()
        result["agreed"] = True
        return result

    # if there are multiple or none second-level chrom values, infer from the id
    if doc['_id'].startswith('chr'):
        result["chrom"] = doc['_id'].split(':')[0][3:]
        result["agreed"] = False if chrom_values else None
        return result

    # return the init result = {"chrom": None, "agreed": False}. In this case, the "agreed" value is meaningless.
    return result


def chrom_worker(col_name, ids):
    database: Database = get_target_db()
    collection: Collection = database[col_name]
    cur = collection.find({'_id': {'$in': ids}})
    bulk_operations = []

    docs_with_disagreed_chrom = []
    docs_with_missing_chrom = []
    target_root_keys = set(["_id", "vcf", "total", "hg19", "hg38", "observed"])
    found_root_keys = {}

    for doc in cur:
        chrom_info = inspect_chrom(doc)
        chrom_value = chrom_info["chrom"]
        chrom_agreement = chrom_info["agreed"]

        if chrom_value is None:
            docs_with_missing_chrom.append(doc["_id"])
        else:
            if chrom_agreement is False:
                docs_with_disagreed_chrom.append(doc["_id"])
            bulk_operations.append(UpdateOne(filter={"_id": doc["_id"]}, update={"$set": {"chrom": chrom_value}}, upsert=False))

        # count root keys for later metadata
        for k in doc:
            # other root keys are actual sources and are counted under "src" key while merge_stats
            if k in target_root_keys:
                found_root_keys.setdefault(k, 0)
                found_root_keys[k] += 1

    if bulk_operations:
        collection.bulk_write(bulk_operations, ordered=False)

    return {"missing": docs_with_missing_chrom, "disagreed": docs_with_disagreed_chrom, "root_keys": found_root_keys}
