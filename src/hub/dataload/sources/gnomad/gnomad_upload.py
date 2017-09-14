import os
import glob
import zipfile

import biothings.hub.dataload.uploader as uploader
import biothings.hub.dataload.storage as storage

from .gnomad_parser_genomes import load_data as load_data_genomes
from .gnomad_parser_exomes import load_data as load_data_exomes
from ...uploader import SnpeffPostUpdateUploader


class GnomadBaseUploader(uploader.IgnoreDuplicatedSourceUploader,SnpeffPostUpdateUploader):

    __metadata__ = {"mapper" : 'observed',
            "assembly" : "hg19",
            "src_meta" : {
                "url" : "",
                "license_url" : "",
                }
            }


class GnomadExomesUploader(GnomadBaseUploader):

    main_source = "gnomad"
    name = "gnomad_exomes"

    def load_data(self,data_folder):
        files = glob.glob(os.path.join(data_folder,"exomes","*.vcf"))
        if len(files) != 1:
            raise uploader.ResourceError("Expecting only one VCF file, got: %s" % files)
        input_file = files.pop()
        assert os.path.exists("%s.gz.tbi" % input_file)
        self.logger.info("Load data from file '%s'" % input_file)
        res = load_data_exomes(input_file)
        return res

    @classmethod
    def get_mapping(klass):
        mapping = {}
        return mapping


class GnomadGenomesUploader(GnomadBaseUploader, uploader.ParallelizedSourceUploader):

    main_source = "gnomad"
    name = "gnomad_genomes"
    GLOB_PATTERN = "gnomad.genomes.*.vcf"

    def jobs(self):
        # tuple(input_file,version), where version is either hg38 or hg19)
        files = [(e,) for e in glob.glob(os.path.join(self.data_folder, "genomes", self.__class__.GLOB_PATTERN))]
        assert len(files) > 23, "Expecting at least 23 VCF files, got: %s" % files
        return files

    def load_data(self, input_file):
        self.logger.info("Load data from file '%s'" % input_file)
        res = load_data_genomes(input_file)
        return res

    @classmethod
    def get_mapping(klass):
        mapping = {}
        return mapping

