import vcf
from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf

def _map_line_to_json(item):
    chrom = item.CHROM
    chromStart = item.POS
    ref = item.REF
    info = item.INFO
    hpo_count=item.INFO['HPO_CT']
    for alt in item.ALT:
        alt = str(alt)
        (HGVS, var_type) = get_hgvs_from_vcf(chrom, chromStart, ref, alt, mutant_type=True)
        if HGVS is None:
            return
        one_snp_json = {
            "_id": HGVS,
            "geno2mp": {
                "hpo_count": hpo_count,

            }
        }
        obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json)), [None]))
        yield obj


def load_data(input_file):
    vcf_reader = vcf.Reader(open(input_file, 'r'))
    for record in vcf_reader:
#        print(record)
        for record_mapped in _map_line_to_json(record):
            yield record_mapped
