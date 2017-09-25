import glob, os, math, asyncio
from functools import partial

import biothings.hub.dataload.uploader as uploader
from biothings.hub.dataload.storage import UpsertStorage
from biothings.utils.mongo import doc_feeder, id_feeder
import biothings.utils.mongo as mongo
from biothings.utils.common import iter_n
from biothings.utils.dataload import dict_attrmerge

import hub.dataload.sources.snpeff.snpeff_upload as snpeff_upload
import hub.dataload.sources.snpeff.snpeff_parser as snpeff_parser
from utils.hgvs import get_pos_start_end
from config import MAX_REF_ALT_LEN

class SnpeffPostUpdateUploader(uploader.BaseSourceUploader):

    keep_archive = 1

    SNPEFF_BATCH_SIZE = 1000000

    def get_pinfo(self):
        pinfo = super(SnpeffPostUpdateUploader,self).get_pinfo()
        # mem depends in the batch size and doc size, but snpeff consumes a lot
        # (here, asumming 1 doc will weigh 1kB)
        pinfo.setdefault("__reqs__",{})["mem"] = (self.__class__.SNPEFF_BATCH_SIZE/100000.) * (1024**3)
        return pinfo

    def do_snpeff(self, batch_size=SNPEFF_BATCH_SIZE, force=False, force_use_cache=False):
        self.logger.info("Updating snpeff information from source '%s' (collection:%s)" % (self.fullname,self.collection_name))
        # select Snpeff uploader to get collection name and src_dump _id
        version = self.__class__.__metadata__["assembly"]
        snpeff_class = getattr(snpeff_upload,"Snpeff%sUploader" % version.capitalize())
        snpeff_main_source = snpeff_class.main_source
        snpeff_doc = self.src_dump.find_one({"_id" : snpeff_main_source})
        assert snpeff_doc, "No snpeff information found, has it been dumped & uploaded ?"
        snpeff_dir = snpeff_doc["data_folder"]
        # -q: when there's an update, there's a message on stderr....
        cmd = "java -Xmx4g -jar %s/snpEff/snpEff.jar -t -noStats -noExpandIUB %s" % (snpeff_dir,version)
        # genome files are in "data_folder"/../data
        genomes = glob.glob(os.path.join(snpeff_dir,"..","data","%s_genome.*" % version))
        assert len(genomes) == 1, "Expected only one genome files for '%s', got: %s" % (version,genomes)
        genome = genomes[0]
        annotator = snpeff_parser.SnpeffAnnotator(cmd,logger=self.logger)
        vcf_builder = snpeff_parser.VCFConstruct(genome,logger=self.logger)
        storage = UpsertStorage(None,snpeff_class.name,self.logger)
        col = self.db[self.collection_name]
        total = math.ceil(col.count()/batch_size)
        cnt = 0
        to_process = []

        def process(ids):
            self.logger.info("%d documents to annotate" % len(ids))
            hgvs_vcfs = vcf_builder.build_vcfs(ids)
            # merge "vcf" and snpeff annotations keys when possible
            # (it no snpeff data, we keep 'vcf' data)
            for annot in annotator.annotate(hgvs_vcfs):
                hgvs_vcfs[annot["_id"]].update(annot)
            # trim if sequence is to big
            for _id in hgvs_vcfs:
                vcf = hgvs_vcfs[_id]
                for k in ["alt","ref"]:
                    if len(vcf["vcf"][k]) > MAX_REF_ALT_LEN:
                        msg = "...(trimmed)"
                        vcf["vcf"][k] = vcf["vcf"][k][:MAX_REF_ALT_LEN - len(msg)] + msg
                hgvs_vcfs[_id] = vcf

            data = annotate_start_end(hgvs_vcfs,version)
            howmany = storage.process(data, batch_size)
            if howmany:
                # we need to update some metadata info about snpeff b/c data has changed
                # so cache could be invalid
                self.logger.debug("Invalidating cache for '%s'" % snpeff_class.name)
                mongo.invalidate_cache(snpeff_class.name)

        for ids in id_feeder(col, batch_size=batch_size, logger=self.logger, force_use=force_use_cache):
            cnt += 1
            self.logger.debug("Processing batch %s/%s [%.1f]" % (cnt,total,(cnt/total*100)))
            # don't re-compute annotations if already there
            if not force:
                for subids in iter_n(ids,10000):
                    cur = storage.temp_collection.find({'_id' : {'$in' : subids}},{'_id':1})
                    already_ids = [d["_id"] for d in list(cur)]
                    newids = list(set(subids).difference(set(already_ids)))
                    if len(subids) != len(newids):
                        self.logger.debug("%d documents already have snpeff annotations, skip them" % \
                                (len(subids) - len(newids)))
                    to_process.extend(newids)
                    self.logger.debug("Batch filled %d out of %d" % (len(to_process),batch_size))
                    if not (len(to_process) >= batch_size):
                        # can fill more...
                        continue
                    process(to_process)
                    to_process = []
            else:
                to_process = ids
        # for potential remainings
        if to_process:
            process(to_process)

    def post_update_data(self, steps, force, batch_size, job_manager, **kwargs):
        # this one will run in current thread, snpeff java prg will
        # multiprocess itself, no need to do more
        force_use_cache = kwargs.get("force_use_cache",False)
        self.do_snpeff(force=force,force_use_cache=force_use_cache)


def annotate_start_end(hgvs_vcfs, assembly):
    for hgvs_id in hgvs_vcfs:
        st,end = None,None
        doc = hgvs_vcfs[hgvs_id]
        if 'vcf' in doc:
            # remove chrom, not needed
            doc['vcf'].pop('chrom',None)
            try:
                st, end = get_pos_start_end(
                                chr=None, # not even used in func
                                pos=doc['vcf']['position'],
                                ref=doc['vcf']['ref'],
                                alt=doc['vcf']['alt'])
                if st and end:
                    doc[assembly] = {"start": st, "end": end}
            except Exception as e:
                pass

        yield doc

