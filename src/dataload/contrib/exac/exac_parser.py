import vcf

from utils.dataload import dict_sweep, unlist, value_convert
from utils.hgvs import get_hgvs_from_vcf


def _map_line_to_json(item):
    chrom = item.CHROM
    chromStart = item.POS
    ref = item.REF
    info = item.INFO
    try:
        baseqranksum = info['BaseQRankSum']
    except:
        baseqranksum = None
    try:
        clippingranksum = info['ClippingRankSum']
    except:
        clippingranksum = None
    try:
        mqranksum = info['MQRankSum']
    except:
        mqranksum = None
    try:
        readposranksum = info['ReadPosRankSum']
    except:
        readposranksum = None
    try:
        qd = info['QD']
    except:
        qd = None
    try:
        inbreedingcoeff = info['InbreedingCoeff']
    except:
        inbreedingcoeff = None
    for i in range(0, len(item.ALT)):
        item.ALT[i] = str(item.ALT[i])
    for alt in item.ALT:
        alt = str(alt)
        (HGVS, var_type) = get_hgvs_from_vcf(chrom, chromStart, ref, alt, mutant_type=True)
        if HGVS is None:
            return
        one_snp_json = {
            "_id": HGVS,
            "exac": {
                "chrom": chrom,
                "pos": chromStart,
                "ref": ref,
                "alt": alt,
                "alleles": item.ALT,
                "type": var_type,
                "ac": {
                    "ac": info['AC'],
                    "ac_afr": info['AC_AFR'],
                    "ac_amr": info['AC_AMR'],
                    "ac_adj": info['AC_Adj'],
                    "ac_eas": info['AC_EAS'],
                    "ac_fin": info['AC_FIN'],
                    "ac_het": info['AC_Het'],
                    "ac_hom": info['AC_Hom'],
                    "ac_nfe": info['AC_NFE'],
                    "ac_oth": info['AC_OTH'],
                    "ac_sas": info['AC_SAS']
                },
                "af": info['AF'],
                "an": {
                    "an": info['AN'],
                    "an_afr": info['AN_AFR'],
                    "an_amr": info['AN_AMR'],
                    "an_adj": info['AN_Adj'],
                    "an_eas": info['AN_EAS'],
                    "an_fin": info['AN_FIN'],
                    "an_nfe": info['AN_NFE'],
                    "an_oth": info['AN_OTH'],
                    "an_sas": info['AN_SAS']

                },
                "baseqranksum": baseqranksum,
                "clippingranksum": clippingranksum,
                "fs": info['FS'],
                "het": {
                    "het_afr": info['Het_AFR'],
                    "het_amr": info['Het_AMR'],
                    "het_eas": info['Het_EAS'],
                    "het_fin": info['Het_FIN'],
                    "het_nfe": info['Het_NFE'],
                    "het_oth": info['Het_OTH'],
                    "het_sas": info['Het_SAS']
                },
                "hom": {
                    "hom_afr": info['Hom_AFR'],
                    "hom_amr": info['Hom_AMR'],
                    "hom_eas": info['Hom_EAS'],
                    "hom_fin": info['Hom_FIN'],
                    "hom_nfe": info['Hom_NFE'],
                    "hom_oth": info['Hom_OTH'],
                    "hom_sas": info['Hom_SAS']
                },
                "inbreedingcoeff": inbreedingcoeff,
                "mq": {
                    "mq": info['MQ'],
                    "mq0": info['MQ0'],
                    "mqranksum": mqranksum
                },
                "ncc": info['NCC'],
                "qd": qd,
                "readposranksum": readposranksum,
                "vqslod": info['VQSLOD'],
                "culprit": info['culprit']
            }
        }
        obj = (dict_sweep(unlist(value_convert(one_snp_json)), [None]))
        yield obj


def load_data(input_file):
    vcf_reader = vcf.Reader(open(input_file, 'r'))
    for record in vcf_reader:
        for record_mapped in _map_line_to_json(record):
            yield record_mapped
