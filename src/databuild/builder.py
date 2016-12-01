import math
import asyncio
from functools import partial
import datetime, pickle

from biothings.utils.common import iter_n
from biothings.utils.mongo import doc_feeder
import biothings.utils.mongo as mongo
import biothings.databuild.builder as builder
import config

class MyVariantDataBuilder(builder.DataBuilder):

    def merge(self, sources=None, target_name=None, batch_size=50000, job_manager=None, **kwargs):
        # just override default batch_size or it consumes too much mem
        return super(MyVariantDataBuilder,self).merge(sources,
                                target_name, job_manager, batch_size=batch_size, **kwargs)

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
        results = {"missing" : [], "disagreed" : []}
        # grab ids only, so we can get more, let's say 10 times more
        id_batch_size = batch_size * 10
        for big_doc_ids in doc_feeder(self.target_backend.target_collection,
                                  step=id_batch_size, inbatch=True, fields={'_id':1}):
            for doc_ids in iter_n(big_doc_ids,batch_size):
                # faking non-blocking call... (but we all know doc_feeder is a blocking one...)
                yield from asyncio.sleep(0.1)
                cnt += len(doc_ids)
                pinfo = self.get_pinfo()
                pinfo["step"] = "post-merge (chrom)"
                pinfo["description"] = "#%d/%d (%.1f%%)" % (bnum,btotal,(cnt/total*100.))
                self.logger.info("Creating post-merge job #%d/%d to process chrom %d/%d (%.1f%%)" % \
                        (bnum,btotal,cnt,total,(cnt/total*100.)))
                ids = [doc["_id"] for doc in doc_ids]
                job = job_manager.defer_to_process(pinfo,
                        partial(chrom_worker, self.target_backend.target_name, ids))
                def processed(f,results, batch_num):
                    try:
                        fres = f.result()
                        results["missing"].extend(fres["missing"])
                        results["disagreed"].extend(fres["disagreed"])
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
        yield from asyncio.wait(jobs)
        self.logger.info("Found %d missing 'chrom' and %d where resources disagreed" % (len(results["missing"]), len(results["disagreed"])))
        if results["missing"] or results["disagreed"]:
            fn = "chrom_%s_%s.pickle" % (self.target_backend.target_name,datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
            self.logger.info("Pickling 'chrom' discrepancies into %s" % fn)
            pickle.dump(results,open(fn,"wb"))

        return results

    def post_merge(self, source_names, batch_size, job_manager):
        self.validate_merge()
        # we're in a new thread (see biothings.databuild.builder, post_merge
        # is called in defer_to_thread)
        asyncio.set_event_loop(job_manager.loop)
        job = self.set_chrom(batch_size, job_manager)
        job = asyncio.ensure_future(job)


def get_chrom(doc):
    chrom_keys = set()
    this_chrom = {"chrom" : None, "agreed" : False}
    # Get chrom keys here
    for k in doc:
        if type(doc[k]) == dict and 'chrom' in doc[k]:
                chrom_keys.add(str(doc[k]['chrom']))
    if len(chrom_keys) == 1:
        this_chrom["chrom"] = chrom_keys.pop()
        this_chrom["agreed"] = True
    elif doc['_id'].startswith('chr'):
        this_chrom["chrom"] = doc['_id'].split(':')[0][3:]
        this_chrom["agreed"] = False
    return this_chrom

def chrom_worker(col_name, ids):
    tgt = mongo.get_target_db()
    col = tgt[col_name]
    cur = col.find({'_id': {'$in': ids}})
    bob = col.initialize_unordered_bulk_op()  
    disagreed = []
    missing = []
    for doc in cur:
        dchrom = get_chrom(doc)
        if dchrom["chrom"] is None:
            missing.append(doc["_id"])
        elif dchrom["agreed"] == False:
            disagreed.append(doc["_id"])
        chrom = dchrom["chrom"]
        bob.find({"_id": doc["_id"]}).update({"$set": {"chrom" : chrom}})
    bob.execute()
    return {"missing": missing, "disagreed" : disagreed}
