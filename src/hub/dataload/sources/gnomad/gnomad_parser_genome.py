import vcf

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf


def _map_line_to_json(item):
    chrom = item.CHROM
    # test on chrom 22 only for the momment, need to remove '22' later
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
        assert len(item.ALT) == len(info['AF']), "Expecting length of item.ALT= length of info.AF, but not for %s" % (HGVS)
        assert len(item.ALT) == len(info['Hom_AFR']), "Expecting length of item.ALT= length of HOM_AFR, but not for %s" % (HGVS)
        one_snp_json = {
            "_id": HGVS,
            "gnomad_genome" : {
                "chrom": chrom,
                "pos": chromStart,
                "filter": _filter,
                "multi-allelic": hgvs_list,
                "ref": ref,
                "alt": alt,
                "alleles": item.ALT,
                "type": var_type,
                "rsid": rsid,
                "ac": {
                    "ac": info['AC'][i],
                    "ac_afr": info['AC_AFR'][i],
                    "ac_amr": info['AC_AMR'][i],
                    "ac_asj": info['AC_ASJ'][i],
                    "ac_eas": info['AC_EAS'][i],
                    "ac_fin": info['AC_FIN'][i],
                    "ac_nfe": info['AC_NFE'][i],
                    "ac_oth": info['AC_OTH'][i],
                    "ac_male": info['AC_Male'][i],
                    "ac_female": info['AC_Female'][i],
                    "ac_raw": info['AC_raw'][i]
                },
                "af": {
                    "af": info['AF'][i],
                    "af_afr": info['AF_AFR'][i],
                    "af_amr": info['AF_AMR'][i],
                    "af_asj": info['AF_ASJ'][i],
                    "af_eas": info['AF_EAS'][i],
                    "af_fin": info['AF_FIN'][i],
                    "af_nfe": info['AF_NFE'][i],
                    "af_oth": info['AF_OTH'][i],
                    "af_female": info['AF_Female'][i],
                    "af_male": info['AF_Male'][i],
                    "af_raw": info['AF_raw'][i]
                },
                "an": {
                    "an": info['AN'],
                    "an_afr": info['AN_AFR'],
                    "an_amr": info['AN_AMR'],
                    "an_asj": info['AN_ASJ'],
                    "an_eas": info['AN_EAS'],
                    "an_fin": info['AN_FIN'],
                    "an_nfe": info['AN_NFE'],
                    "an_oth": info['AN_OTH'],
                    "an_female": info['AN_Female'],
                    "an_male": info['AN_Male'],
                    "an_raw": info['AN_raw']
                },
                "gc": {
                    "gc": info['GC'],
                    "gc_afr": info['GC_AFR'],
                    "gc_amr": info['GC_AMR'],
                    "gc_asj": info['GC_ASJ'],
                    "gc_eas": info['GC_EAS'],
                    "gc_fin": info['GC_FIN'],
                    "gc_nfe": info['GC_NFE'],
                    "gc_oth": info['GC_OTH'],
                    "gc_female": info['GC_Female'],
                    "gc_male": info['GC_Male'],
                    "gc_raw": info['GC_raw']
                },
                "baseqranksum": baseqranksum,
                "clippingranksum": clippingranksum,
                "fs": info['FS'],
                "hom": {
                    "hom": info['Hom'],
                    "hom_afr": info['Hom_AFR'],
                    "hom_asj": info['Hom_ASJ'],
                    "hom_amr": info['Hom_AMR'],
                    "hom_eas": info['Hom_EAS'],
                    "hom_fin": info['Hom_FIN'],
                    "hom_nfe": info['Hom_NFE'],
                    "hom_oth": info['Hom_OTH'],
                    "hom_female": info['Hom_Female'],
                    "hom_male": info['Hom_Male'],
                    "hom_raw": info['Hom_raw']
                },
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
        obj = (dict_sweep(unlist(value_convert_to_number(one_snp_json)), [None]))
        yield obj


def load_data(input_file):
    vcf_reader = vcf.Reader(open(input_file, 'r'))
    for record in vcf_reader:
        for record_mapped in _map_line_to_json(record):
            yield record_mapped
