# -*- coding: utf-8 -*-
from biothings.settings import BiothingSettings

HG38_FIELDS = ['clinvar.hg38', 'dbnsfp.hg38', 'evs.hg38']
HG19_FIELDS = ['clinvar.hg19', 'cosmic.hg19', 'dbnsfp.hg19', 'dbsnp.hg19', 'docm.hg19', 'evs.hg19', 'grasp.hg19'] #, 'mutdb.hg19', 'wellderly.hg19']
CHROM_FIELDS = ['cadd.chrom', 'clinvar.chrom', 'cosmic.chrom', 'dbnsfp.chrom', 'dbsnp.chrom', 'docm.chrom',
                'evs.chrom', 'exac.chrom']#, 'mutdb.chrom', 'wellderly.chrom']

class MyVariantSettings(BiothingSettings):
    @property
    def hg38_fields(self):
        try:
            return self._return_var('HG38_FIELDS')
        except:
            return HG38_FIELDS

    @property
    def hg19_fields(self):
        try:
            return self._return_var('HG19_FIELDS')
        except:
            return HG19_FIELDS

    @property
    def chrom_fields(self):
        try:
            return self._return_var('CHROM_FIELDS')
        except:
            return CHROM_FIELDS

    @property
    def jsonld_context_path(self):
        try:
            return self._return_var('JSONLD_CONTEXT_PATH')
        except:
            print("JSONLD_CONTEXT_PATH was not found in your config file.  No context file loaded.")
            return {}
