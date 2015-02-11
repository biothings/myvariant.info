from __future__ import print_function
from .dbsnp_vcf_parser import parse_vcf


infile = "/opt/myvariant.info/load_archive/dbsnp/00-All.vcf.gz"

def load_data():
    chrom_list = [str(i) for i in range(1, 23)] + ['X', 'Y', 'MT']
    for chrom in chrom_list:
        print("Processing chr{}...".format(chrom))
        snpdoc_iter = parse_vcf(infile, compressed=True, verbose=False, by_id=True, reference=chrom)
        for doc in snpdoc_iter:
            _doc = {'dbsnp': doc}
            _doc['_id'] = doc['_id']
            del doc['_id']
            yield _doc
