import vcf

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf

CHROM_VALID_VALUES = [str(_chr) for _chr in list(range(1, 23)) + ['X', 'Y', 'MT']]

def _map_line_to_json(item, keys):
    key_start = ["AC", "AF", "AN", "Hom", "GC", "Hemi"]
    chrom = str(item.CHROM)
    if chrom not in CHROM_VALID_VALUES:
        return
    chromStart = item.POS
    ref = item.REF
    info = item.INFO
    _filter = item.FILTER
    rsid = item.ID
    # the following value could be missing in the vcf record
    # check first if the key exists in the vcf record
    # if not, return None
    vqslod = info['VQSLOD'] if 'VQSLOD' in info else None
    vqsr_culprit = info['VQSR_culprit'] if 'VQSR_culprit' in info else None
    baseqranksum = info['BaseQRankSum'] if 'BaseQRankSum' in info else None
    clippingranksum = info['ClippingRankSum'] if 'ClippingRankSum' in info else None
    mqranksum = info['MQRankSum'] if 'MQRankSum' in info else None
    readposranksum = info['ReadPosRankSum'] if 'ReadPosRankSum' in info else None
    qd = info['QD'] if 'QD' in info else None
    inbreedingcoeff = info['InbreedingCoeff'] if 'InbreedingCoeff' in info else None
    # convert vcf object to string
    item.ALT = [str(alt) for alt in item.ALT]
    # if multiallelic, put all variants as a list in multi-allelic field
    hgvs_list = None
    if len(item.ALT) > 1:
        hgvs_list = [get_hgvs_from_vcf(chrom, chromStart, ref, alt, mutant_type=False) for alt in item.ALT]
    for i, alt in enumerate(item.ALT):
        (HGVS, var_type) = get_hgvs_from_vcf(chrom, chromStart, ref, alt, mutant_type=True)
        if HGVS is None:
            return
        assert len(item.ALT) == len(info['AC']), "Expecting length of item.ALT= length of info.AC, but not for %s" % (HGVS)
        # assert len(item.ALT) == len(info['AF']), "Expecting length of item.ALT= length of info.AF, but not for %s" % (HGVS)
        one_snp_json = {
            "_id": HGVS,
            "gnomad_exome": {
                "chrom": chrom,
                "pos": chromStart,
                "filter": _filter,
                "multi-allelic": hgvs_list,
                "ref": ref,
                "alt": alt,
                "alleles": item.ALT,
                "type": var_type,
                "rsid": rsid,
                "baseqranksum": baseqranksum,
                "clippingranksum": clippingranksum,
                "fs": info['FS'],
                "inbreedingcoeff": inbreedingcoeff,
                "mq": {
                    "mq": info['MQ'],
                    "mqranksum": mqranksum
                },
                "qd": qd,
                "readposranksum": readposranksum,
                "vqslod": vqslod,
                "vqsr_culprit": vqsr_culprit
            }
        }
        # create a holder in one_snp_json for each _start, e.g. 'ac', 'af', 'gc'
        for _start in key_start:
            one_snp_json['gnomad_exome'][_start.lower()] = {}
        # loop through each available key
        for _key in keys:
            if _key in info:
                # loop through each prefix
                for _start in key_start:
                    # "ac", "af" value is related to multi-allelic, need to deal with separately
                    if _key.startswith(_start) and _start in ['AC', 'AF', 'Hom', 'Hemi']:
                        one_snp_json['gnomad_exome'][_start.lower()][_key.lower()] = info[_key][i]
                    elif _key.startswith(_start) and _start not in ['AC', 'AF', 'Hom', 'Hemi']:
                        one_snp_json['gnomad_exome'][_start.lower()][_key.lower()] = info[_key]
        obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json, skipped_keys=['chrom'])), [None]))
        yield obj


def load_data(input_file):
    vcf_reader = vcf.Reader(filename=input_file)
    keys = vcf_reader.infos.keys()
    keys = [_key for _key in keys if _key.startswith(("AC", "AF", "AN", "Hom", "GC", "Hemi"))]
    for record in vcf_reader:
        for record_mapped in _map_line_to_json(record, keys):
            yield record_mapped

def test(input_file):
    vcf_reader = vcf.Reader(filename=input_file)
    chrom_li = [str(i) for i in range(1, 23)]
    chrom_li += ['X', 'Y']
    for chrom in chrom_li:
        data = next(vcf_reader.fetch(chrom))
        print(list(_map_line_to_json(data)))

