import os
import os.path
import glob
import sys
import time
import asyncio

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import ManualDumper
from biothings.utils.common import aiogunzipall


class GnomadDumper(ManualDumper):

    SRC_NAME = "gnomad"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)

    def __init__(self, *args, **kwargs):
        super(GnomadDumper,self).__init__(*args,**kwargs)
        self.logger.info("""
Assuming manual download from: http://gnomad.broadinstitute.org/downloads
Under version directory, there should be 2 sub-directories, containing VCF and .tbi files:
- exomes/
- genomes/
""")

    def post_dump(self, *args, **kwargs):
        job_manager = kwargs.get("job_manager")
        if not job_manager:
            raise Exception("No job_manager found")
        asyncio.set_event_loop(job_manager.loop)
        job = self.gunzipall(job_manager)
        task = asyncio.ensure_future(job)
        return task

    @asyncio.coroutine
    def gunzipall(self, job_manager):
        genomes_dir = [os.path.join(self.new_data_folder,"genomes"),"*.vcf.bgz"]
        exomes_dir = [os.path.join(self.new_data_folder,"exomes"),"*.vcf.bgz"]
        # hg38 data is one folder deeper
        genomes_dir_hg38 = [os.path.join(genomes_dir[0],"liftover_grch38"),"*.vcf.gz"]
        exomes_dir_hg38 = [os.path.join(exomes_dir[0],"liftover_grch38"),"*.vcf.gz"]
        jobs = []
        got_error = None
        for fp in [genomes_dir_hg38,exomes_dir_hg38]:#,genomes_dir,exomes_dir]:
            folder,pattern = fp
            pinfo = self.get_pinfo()
            pinfo["step"] = "post-dump (gunzip)"
            self.logger.info("Unzipping files in '%s'" % folder) 
            job = yield from aiogunzipall(folder,pattern,job_manager,pinfo)
            jobs.append(job)
        if jobs:
            yield from asyncio.gather(*jobs)
            if got_error:
                raise got_error
