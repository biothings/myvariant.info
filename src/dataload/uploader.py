import glob, os, math

import biothings.dataload.uploader as uploader
from biothings.dataload.storage import IgnoreDuplicatedStorage
from biothings.utils.mongo import doc_feeder

import dataload.sources.snpeff.snpeff_upload as snpeff_upload
import dataload.sources.snpeff.snpeff_parser as snpeff_parser

class SnpeffPostUpdateUploader(uploader.BaseSourceUploader):

    def post_update_data(self):
        self.logger.info("Updating snpeff information from source '%s' (collection:%s)" % (self.fullname,self.collection_name))
        # select Snpeff uploader to get collection name and src_dump _id
        version = self.__class__.__metadata__["assembly"]
        snpeff_class = getattr(snpeff_upload,"Snpeff%sUploader" % version.capitalize())
        snpeff_main_source = snpeff_class.main_source
        snpeff_doc = self.src_dump.find_one({"_id" : snpeff_main_source})
        assert snpeff_doc, "No snpeff information found, has it been dumped & uploaded ?"
        snpeff_dir = snpeff_doc["data_folder"]
        cmd = "java -Xmx4g -jar %s/snpEff/snpEff.jar %s" % (snpeff_dir,version)
        print(cmd)
        # genome files are in "data_folder"/../data
        genomes = glob.glob(os.path.join(snpeff_dir,"..","data","%s_genome.*" % version))
        assert len(genomes) == 1, "Expected only one genome files for '%s', got: %s" % (version,genomes)
        genome = genomes[0]
        parser = snpeff_parser.VCFConstruct(cmd,genome)
        storage = IgnoreDuplicatedStorage(None,snpeff_class.name,self.logger)
        batch_size = 1000000
        col = self.db[self.collection_name]
        total = math.ceil(col.count()/batch_size)
        cnt = 0
        for doc_ids in doc_feeder(col, step=batch_size, inbatch=True, fields={'_id':1}):
            ids = [d["_id"] for d in doc_ids]
            data = parser.annotate_by_snpeff(ids)
            storage.process(data, batch_size)
            cnt += 1
            self.logger.debug("Processed batch %s/%s [%.1f]" % (cnt,total,(cnt/total*100)))

