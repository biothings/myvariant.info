import os
import glob
from typing import Callable

from biothings.hub.dataload.uploader import ResourceError, ParallelizedSourceUploader

from .gnomad_v2_parser import load_genome_data as load_genome_data_v2, load_exome_data as load_exome_data_v2
from .gnomad_v3_parser import load_genome_data as load_genome_data_v3
from .mapping import exomes_mapping_v2, genomes_mapping_v2, genomes_mapping_v3
from hub.dataload.uploader import SnpeffPostUpdateUploader
from hub.dataload.storage import MyVariantIgnoreDuplicatedStorage

"""
Structure of manual upload:

datasources
|-- gnomad
    |-- 20210610 (data_folder)
        |-- 2.1.1
        |   |-- exomes
        |   |   |-- gnomad.exomes.r2.1.1.sites.*.vcf.bgz
        |   |   |-- gnomad.exomes.r2.1.1.sites.*.vcf.bgz.tbi
        |   |   `-- liftover_grch38
        |   |       |-- gnomad.exomes.r2.1.1.sites.*.liftover_grch38.vcf.bgz
        |   |       `-- gnomad.exomes.r2.1.1.sites.*.liftover_grch38.vcf.bgz.tbi
        |   `-- genomes
        |       |-- gnomad.genomes.r2.1.1.sites.*.vcf.bgz
        |       |-- gnomad.genomes.r2.1.1.sites.*.vcf.bgz.tbi
        |       `-- liftover_grch38
        |           |-- gnomad.genomes.r2.1.1.sites.*.liftover_grch38.vcf.bgz
        |           `-- gnomad.genomes.r2.1.1.sites.*.liftover_grch38.vcf.bgz.tbi
        |-- 3.1.1
        |   `-- genomes
        |       |-- gnomad.genomes.v3.1.1.sites.chr*.vcf.bgz
        |       `-- gnomad.genomes.v3.1.1.sites.chr*.vcf.bgz.tbi

Versions of data:

- genomAD_exome_hg19: v2.1.1   =>  2.1.1/exomes
- genomAD_exome_hg38: v2.1.1   =>  2.1.1/exomes/liftover_grch38
- genomAD_genome_hg19: v2.1.1  =>  2.1.1/genomes
- genomAD_genome_hg38: v3.1.1  =>  3.1.1/genomes

N.B.:

- 2.1.1/genomes/liftover_grch38 is discarded
- gnomAD v3 has no exomes data
"""

SRC_META = {
    "url": "http://gnomad.broadinstitute.org",
    "license_url": "http://gnomad.broadinstitute.org/terms",
    "license_url_short": "http://bit.ly/2I1cl1I",
    "license": "ODbL"
}


class GnomadBaseUploader(SnpeffPostUpdateUploader):
    storage_class = MyVariantIgnoreDuplicatedStorage


class GnomadBaseHg19Uploader(GnomadBaseUploader):
    __metadata__ = {
        "mapper": 'observed',
        "assembly": "hg19",
        "src_meta": SRC_META
    }


class GnomadBaseHg38Uploader(GnomadBaseUploader):
    __metadata__ = {
        "mapper": 'observed',
        "assembly": "hg38",
        "src_meta": SRC_META
    }


class GnomadExomesBaseUploader(GnomadBaseUploader):  # TODO also extends ParallelizedSourceUploader?
    # Please override in subclasses
    LOAD_FUNCTION: Callable = None
    GLOB_VCF_PATTERN: str = None
    GLOB_TBI_PATTERN: str = None

    def load_data(self, data_folder):
        vcf_files = glob.glob(os.path.join(data_folder, self.__class__.GLOB_VCF_PATTERN))
        if len(vcf_files) != 1:
            raise ResourceError("Expecting only one VCF file, got: %s" % vcf_files)

        tbi_files = glob.glob(os.path.join(data_folder, self.__class__.GLOB_TBI_PATTERN))
        if len(tbi_files) != 1:
            raise ResourceError("Expecting only one TBI file, got: %s" % tbi_files)

        input_file = vcf_files.pop()

        self.logger.info("Load data from file '%s'" % input_file)
        res = self.__class__.LOAD_FUNCTION(input_file)
        return res


class GnomadExomesHg19Uploader(GnomadBaseHg19Uploader, GnomadExomesBaseUploader):
    main_source = "gnomad"
    name = "gnomad_exomes_hg19"

    GLOB_VCF_PATTERN = "2.1.1/exomes/gnomad.exomes.*.vcf.bgz"
    GLOB_TBI_PATTERN = GLOB_VCF_PATTERN + ".tbi"

    LOAD_FUNCTION = load_exome_data_v2

    @classmethod
    def get_mapping(cls):
        return exomes_mapping_v2


class GnomadExomesHg38Uploader(GnomadBaseHg38Uploader, GnomadExomesBaseUploader):
    main_source = "gnomad"
    name = "gnomad_exomes_hg38"

    GLOB_VCF_PATTERN = "2.1.1/exomes/liftover_grch38/gnomad.exomes.*.vcf.bgz"
    GLOB_TBI_PATTERN = GLOB_VCF_PATTERN + ".tbi"

    LOAD_FUNCTION = load_exome_data_v2

    @classmethod
    def get_mapping(cls):
        return exomes_mapping_v2


class GnomadGenomesBaseUploader(GnomadBaseUploader, ParallelizedSourceUploader):
    # Please override in subclasses
    LOAD_FUNCTION: Callable = None
    GLOB_VCF_PATTERN: str = None
    GLOB_TBI_PATTERN: str = None

    def jobs(self):
        vcf_files = glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_VCF_PATTERN))
        if len(vcf_files) < 23:
            raise ResourceError("Expecting at least 23 VCF files, got: %s" % vcf_files)

        tbi_files = glob.glob(os.path.join(self.data_folder, self.__class__.GLOB_TBI_PATTERN))
        if len(tbi_files) < 23:
            raise ResourceError("Expecting at least 23 TBI files, got: %s" % tbi_files)

        return [(f, ) for f in vcf_files]

    def load_data(self, input_file):
        self.logger.info("Load data from file '%s'" % input_file)
        res = self.__class__.LOAD_FUNCTION(input_file)
        return res


class GnomadGenomesHg19Uploader(GnomadBaseHg19Uploader, GnomadGenomesBaseUploader):
    main_source = "gnomad"
    name = "gnomad_genomes_hg19"

    GLOB_VCF_PATTERN = "2.1.1/genomes/gnomad.genomes.*.vcf.bgz"
    GLOB_TBI_PATTERN = GLOB_VCF_PATTERN + ".tbi"

    LOAD_FUNCTION = load_genome_data_v2

    @classmethod
    def get_mapping(cls):
        return genomes_mapping_v2


class GnomadGenomesHg38Uploader(GnomadBaseHg38Uploader, GnomadGenomesBaseUploader):
    main_source = "gnomad"
    name = "gnomad_genomes_hg38"

    GLOB_VCF_PATTERN = "3.1.1/genomes/gnomad.genomes.*.vcf.bgz"
    GLOB_TBI_PATTERN = GLOB_VCF_PATTERN + ".tbi"

    LOAD_FUNCTION = load_genome_data_v3

    @classmethod
    def get_mapping(cls):
        return genomes_mapping_v3
