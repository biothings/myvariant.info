from .geno2mp_parser import load_data as _load_data

GENO2MP_INPUT_FILE = '<file_path_to_geno2mp_vcf_file>'

__METADATA__ = {
    "src_name": 'geno2mp',
    "src_url": 'http://geno2mp.gs.washington.edu/download/Geno2MP.variants.vcf.gz',
    "version": '20151214',
    "field": 'HPO_CT'
}


def load_data():
    exac_data = _load_data(GENO2MP_INPUT_FILE)
    return exac_data
