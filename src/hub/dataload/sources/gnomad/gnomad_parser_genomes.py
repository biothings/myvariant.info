import vcf

from biothings.utils.dataload import dict_sweep, unlist, value_convert_to_number
from utils.hgvs import get_hgvs_from_vcf

def parse_chrX(_info, i):
    json_doc = {
        "ac": {
            "ac": _info['AC'][i],
            "ac_afr": _info['AC_AFR'][i],
            "ac_amr": _info['AC_AMR'][i],
            "ac_eas": _info['AC_EAS'][i],
            "ac_fin": _info['AC_FIN'][i],
            "ac_nfe": _info['AC_NFE'][i],
            "ac_oth": _info['AC_OTH'][i],
            "ac_asj": _info['AC_ASJ'][i],
            "ac_male": _info['AC_Male'][i],
            "ac_female": _info['AC_Female'][i],
            "ac_raw": _info['AC_raw'][i],
            "ac_afr_female": _info['AC_AFR_Female'],
            "ac_afr_male": _info['AC_AFR_Male'],
            "ac_amr_female": _info['AC_AMR_Female'],
            "ac_amr_male": _info['AC_AMR_Male'],
            "ac_asj_female": _info['AC_ASJ_Female'],
            "ac_asj_male": _info['AC_ASJ_Male'],
            "ac_eas_female": _info['AC_EAS_Female'],
            "ac_eas_male": _info['AC_EAS_Male'],
            "ac_fin_female": _info['AC_FIN_Female'],
            "ac_fin_male": _info['AC_FIN_Male'],
            "ac_nfe_female": _info['AC_NFE_Female'],
            "ac_nfe_male": _info['AC_NFE_Male'],
            "ac_oth_female": _info['AC_OTH_Female'],
            "ac_oth_male": _info['AC_OTH_Male']
        },
        "af": {
            "af": _info['AF'][i],
            "af_afr": _info['AF_AFR'][i],
            "af_amr": _info['AF_AMR'][i],
            "af_asj": _info['AF_ASJ'][i],
            "af_eas": _info['AF_EAS'][i],
            "af_fin": _info['AF_FIN'][i],
            "af_nfe": _info['AF_NFE'][i],
            "af_oth": _info['AF_OTH'][i],
            "af_female": _info['AF_Female'][i],
            "af_male": _info['AF_Male'][i],
            "af_raw": _info['AF_raw'][i],
            "af_afr_female": _info['AF_AFR_Female'],
            "af_afr_male": _info['AF_AFR_Male'],
            "af_amr_female": _info['AF_AMR_Female'],
            "af_amr_male": _info['AF_AMR_Male'],
            "af_asj_female": _info['AF_ASJ_Female'],
            "af_asj_male": _info['AF_ASJ_Male'],
            "af_eas_female": _info['AF_EAS_Female'],
            "af_eas_male": _info['AF_EAS_Male'],
            "af_fin_female": _info['AF_FIN_Female'],
            "af_fin_male": _info['AF_FIN_Male'],
            "af_nfe_female": _info['AF_NFE_Female'],
            "af_nfe_male": _info['AF_NFE_Male'],
            "af_oth_female": _info['AF_OTH_Female'],
            "af_oth_male": _info['AF_OTH_Male']
        },
        "an": {
            "an": _info['AN'],
            "an_afr": _info['AN_AFR'],
            "an_amr": _info['AN_AMR'],
            "an_asj": _info['AN_ASJ'],
            "an_eas": _info['AN_EAS'],
            "an_fin": _info['AN_FIN'],
            "an_nfe": _info['AN_NFE'],
            "an_oth": _info['AN_OTH'],
            "an_female": _info['AN_Female'],
            "an_male": _info['AN_Male'],
            "an_raw": _info['AN_raw'],
            "an_afr_female": _info['AN_AFR_Female'],
            "an_afr_male": _info['AN_AFR_Male'],
            "an_amr_female": _info['AN_AMR_Female'],
            "an_amr_male": _info['AN_AMR_Male'],
            "an_asj_female": _info['AN_ASJ_Female'],
            "an_asj_male": _info['AN_ASJ_Male'],
            "an_eas_female": _info['AN_EAS_Female'],
            "an_eas_male": _info['AN_EAS_Male'],
            "an_fin_female": _info['AN_FIN_Female'],
            "an_fin_male": _info['AN_FIN_Male'],
            "an_nfe_female": _info['AN_NFE_Female'],
            "an_nfe_male": _info['AN_NFE_Male'],
            "an_oth_female": _info['AN_OTH_Female'],
            "an_oth_male": _info['AN_OTH_Male']
        },
        "gc": {
            "gc": _info['GC'],
            "gc_female": _info['GC_Female'],
            "gc_male": _info['GC_Male'],
            "gc_raw": _info['GC_raw'],
            "gc_afr_female": _info['GC_AFR_Female'],
            "gc_afr_male": _info['GC_AFR_Male'],
            "gc_amr_female": _info['GC_AMR_Female'],
            "gc_amr_male": _info['GC_AMR_Male'],
            "gc_asj_female": _info['GC_ASJ_Female'],
            "gc_asj_male": _info['GC_ASJ_Male'],
            "gc_eas_female": _info['GC_EAS_Female'],
            "gc_eas_male": _info['GC_EAS_Male'],
            "gc_fin_female": _info['GC_FIN_Female'],
            "gc_fin_male": _info['GC_FIN_Male'],
            "gc_nfe_female": _info['GC_NFE_Female'],
            "gc_nfe_male": _info['GC_NFE_Male'],
            "gc_oth_female": _info['GC_OTH_Female'],
            "gc_oth_male": _info['GC_OTH_Male'],
        },
        "hemi": {
            "hemi": _info['Hemi'],
            "hemi_afr": _info['Hemi_AFR'],
            "hemi_amr": _info['Hemi_AMR'],
            "hemi_asj": _info['Hemi_ASJ'],
            "hemi_eas": _info['Hemi_EAS'],
            "hemi_fin": _info['Hemi_FIN'],
            "hemi_nfe": _info['Hemi_NFE'],
            "hemi_oth": _info['Hemi_OTH'],
            "hemi_raw": _info['Hemi_raw']
        },
        "hom": {
            "hom": _info['Hom'],
            "hom_afr": _info['Hom_AFR'],
            "hom_asj": _info['Hom_ASJ'],
            "hom_amr": _info['Hom_AMR'],
            "hom_eas": _info['Hom_EAS'],
            "hom_fin": _info['Hom_FIN'],
            "hom_nfe": _info['Hom_NFE'],
            "hom_oth": _info['Hom_OTH'],
            "hom_raw": _info['Hom_raw']
        }
    }
    return json_doc

def parse_chr(_info, i):
    json_doc = {
        "ac": {
            "ac": _info['AC'][i],
            "ac_afr": _info['AC_AFR'][i],
            "ac_amr": _info['AC_AMR'][i],
            "ac_eas": _info['AC_EAS'][i],
            "ac_fin": _info['AC_FIN'][i],
            "ac_nfe": _info['AC_NFE'][i],
            "ac_nfe": _info['AC_NFE'][i],
            "ac_oth": _info['AC_OTH'][i],
            "ac_asj": _info['AC_ASJ'][i],
            "ac_male": _info['AC_Male'][i],
            "ac_female": _info['AC_Female'][i],
            "ac_raw": _info['AC_raw'][i]
        },
        "af": {
            "af": _info['AF'][i],
            "af_afr": _info['AF_AFR'][i],
            "af_amr": _info['AF_AMR'][i],
            "af_asj": _info['AF_ASJ'][i],
            "af_eas": _info['AF_EAS'][i],
            "af_fin": _info['AF_FIN'][i],
            "af_nfe": _info['AF_NFE'][i],
            "af_oth": _info['AF_OTH'][i],
            "af_female": _info['AF_Female'][i],
            "af_male": _info['AF_Male'][i],
            "af_raw": _info['AF_raw'][i]
        },
        "an": {
            "an": _info['AN'],
            "an_afr": _info['AN_AFR'],
            "an_amr": _info['AN_AMR'],
            "an_asj": _info['AN_ASJ'],
            "an_eas": _info['AN_EAS'],
            "an_fin": _info['AN_FIN'],
            "an_nfe": _info['AN_NFE'],
            "an_oth": _info['AN_OTH'],
            "an_female": _info['AN_Female'],
            "an_male": _info['AN_Male'],
            "an_raw": _info['AN_raw']
        },
        "gc": {
            "gc": _info['GC'],
            "gc_afr": _info['GC_AFR'],
            "gc_amr": _info['GC_AMR'],
            "gc_asj": _info['GC_ASJ'],
            "gc_eas": _info['GC_EAS'],
            "gc_fin": _info['GC_FIN'],
            "gc_nfe": _info['GC_NFE'],
            "gc_oth": _info['GC_OTH'],
            "gc_female": _info['GC_Female'],
            "gc_male": _info['GC_Male'],
            "gc_raw": _info['GC_raw']
        },
        "hom": {
            "hom": _info['Hom'],
            "hom_afr": _info['Hom_AFR'],
            "hom_asj": _info['Hom_ASJ'],
            "hom_amr": _info['Hom_AMR'],
            "hom_eas": _info['Hom_EAS'],
            "hom_fin": _info['Hom_FIN'],
            "hom_nfe": _info['Hom_NFE'],
            "hom_oth": _info['Hom_OTH'],
            "hom_female": _info['Hom_Female'],
            "hom_male": _info['Hom_Male'],
            "hom_raw": _info['Hom_raw']
        }
    }
    return json_doc

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
            "gnomad_genome": {
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

def 
