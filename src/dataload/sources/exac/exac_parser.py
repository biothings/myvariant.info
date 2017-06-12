import vcf

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf


def _map_line_to_json(doc_key, item):
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
        assert len(item.ALT) == len(info['AF']), "Expecting length of item.ALT= length of info.AF, but not for %s" % (HGVS)
        assert len(item.ALT) == len(info['Hom_AFR']), "Expecting length of item.ALT= length of HOM_AFR, but not for %s" % (HGVS)
        one_snp_json = {
            "_id": HGVS,
            doc_key : {
                "chrom": chrom,
                "pos": chromStart,
                "multi-allelic": hgvs_list,
                "ref": ref,
                "alt": alt,
                "alleles": item.ALT,
                "type": var_type,
                "ac": {
                    "ac": info['AC'][i],
                    "ac_afr": info['AC_AFR'][i],
                    "ac_amr": info['AC_AMR'][i],
                    "ac_adj": info['AC_Adj'][i],
                    "ac_eas": info['AC_EAS'][i],
                    "ac_fin": info['AC_FIN'][i],
                    "ac_het": info['AC_Het'][i],
                    "ac_hom": info['AC_Hom'][i],
                    "ac_nfe": info['AC_NFE'][i],
                    "ac_oth": info['AC_OTH'][i],
                    "ac_sas": info['AC_SAS'][i],
                    "ac_male": info['AC_MALE'][i],
                    "ac_female": info['AC_FEMALE'][i]
                },
                "af": info['AF'][i],
                "an": {
                    "an": info['AN'],
                    "an_afr": info['AN_AFR'],
                    "an_amr": info['AN_AMR'],
                    "an_adj": info['AN_Adj'],
                    "an_eas": info['AN_EAS'],
                    "an_fin": info['AN_FIN'],
                    "an_nfe": info['AN_NFE'],
                    "an_oth": info['AN_OTH'],
                    "an_sas": info['AN_SAS'],
                    "an_female": info['AN_FEMALE'],
                    "an_male": info['AN_MALE']

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
        obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json)), [None]))
        yield obj


def load_data(doc_key,input_file):
    vcf_reader = vcf.Reader(open(input_file, 'r'))
    for record in vcf_reader:
        for record_mapped in _map_line_to_json(doc_key,record):
            yield record_mapped
