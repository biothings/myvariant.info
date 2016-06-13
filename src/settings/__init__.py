# -*- coding: utf-8 -*-
from biothings.settings import BiothingSettings

ES_INDEX_BASE = 'myvariant_current'
DEFAULT_ASSEMBLY = 'hg19'
SUPPORTED_ASSEMBLIES = ['hg19', 'hg38']
HG38_FIELDS = ['clinvar.hg38', 'dbnsfp.hg38', 'evs.hg38']
HG19_FIELDS = ['clinvar.hg19', 'cosmic.hg19', 'dbnsfp.hg19', 'dbsnp.hg19', 'docm.hg19', 'evs.hg19', 'grasp.hg19'] #, 'mutdb.hg19', 'wellderly.hg19']
CHROM_FIELDS = ['cadd.chrom', 'clinvar.chrom', 'cosmic.chrom', 'dbnsfp.chrom', 'dbsnp.chrom', 'docm.chrom',
                'evs.chrom', 'exac.chrom']#, 'mutdb.chrom', 'wellderly.chrom']
HG19_INDEX = ''
HG38_INDEX = ''

class MyVariantSettings(BiothingSettings):
    @property
    def es_index_base(self):
        try:
            return self._return_var('ES_INDEX_BASE')
        except:
            return ES_INDEX_BASE

    @property
    def default_assembly(self):
        try:
            return self._return_var('DEFAULT_ASSEMBLY')
        except:
            return DEFAULT_ASSEMBLY
    
    @property
    def supported_assemblies(self):
        try:
            return self._return_var('SUPPORTED_ASSEMBLIES')
        except:
            return SUPPORTED_ASSEMBLIES
    
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
