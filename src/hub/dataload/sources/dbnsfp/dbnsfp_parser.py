import csv
import glob
from biothings.utils.dataload import list_split, dict_sweep, unlist, value_convert_to_number
from biothings.utils.common import anyfile

# VALID_COLUMN_NO = 367  # for 4.1a
VALID_COLUMN_NO = 642  # for 4.2a


"""
this parser is for dbNSFP v4.2a downloaded from
https://sites.google.com/site/jpopgen/dbNSFP
"""


# convert one snp to json
def _map_row_to_json(row, version, include_gnomad):
    """
    `row` is a pandas Series-like object or a simple `dict` representing the content of one row in a dbNSFP tsv files
    """

    # specific variable treatment
    chrom = row["#chr"]
    if chrom == 'M':
        chrom = 'MT'
    # fields[7] in version 2, represent hg18_pos
    hg18_end = row["hg18_pos(1-based)"]
    if hg18_end == ".":
        hg18_end = "."
    else:
        hg18_end = int(hg18_end)
    # in case of no hg19 position provided, remove the item
    if row["hg19_pos(1-based)"] == '.':
        return None
    else:
        chromStart = int(row["hg19_pos(1-based)"])
        chromEnd = chromStart
    chromStart_38 = int(row["pos(1-based)"])
    ref = row["ref"].upper()
    alt = row["alt"].upper()
    HGVS_19 = "chr%s:g.%d%s>%s" % (chrom, chromStart, ref, alt)
    HGVS_38 = "chr%s:g.%d%s>%s" % (chrom, chromStart_38, ref, alt)
    if version == 'hg19':
        HGVS = HGVS_19
    elif version == 'hg38':
        HGVS = HGVS_38
    siphy_29way_pi = row["SiPhy_29way_pi"]
    if siphy_29way_pi == ".":
        siphy = "."
    else:
        freq = siphy_29way_pi.split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}
    gtex_gene = row["GTEx_V8_gene"].split('|')
    gtex_tissue = row["GTEx_V8_tissue"].split('|')
    gtex = map(dict, map(lambda t: zip(('gene', 'tissue'), t), zip(gtex_gene, gtex_tissue)))
    acc = row["Uniprot_acc"].rstrip().rstrip(';').split(";")
    entry = row["Uniprot_entry"].rstrip().rstrip(';').split(";")
    uniprot = map(dict, map(lambda t: zip(('acc', 'entry'), t), zip(acc, entry)))
    provean_score = row["PROVEAN_score"].split(';')
    sift_score = row["SIFT_score"].split(';')
    sift4g_score = row["SIFT4G_score"].split(';')
    hdiv_score = row["Polyphen2_HDIV_score"].split(';')
    hvar_score = row["Polyphen2_HVAR_score"].split(';')
    lrt_score = row["LRT_score"].split(';')
    m_cap_score = row["M-CAP_score"].split(';')
    mutationtaster_score = row["MutationTaster_score"].split(';')
    mutationassessor_score = row["MutationAssessor_score"].split(';')
    vest3_score = row["VEST4_score"].split(';')
    metasvm_score = row["MetaSVM_score"].split(';')
    fathmm_score = row["FATHMM_score"].split(';')
    metalr_score = row["MetaLR_score"].split(';')
    revel_score = row["REVEL_score"].split(';')
    appris = row["APPRIS"].split(";")
    mpc_score = row["MPC_score"].split(';')
    mvp_score = row["MVP_score"].split(';')
    tsl = row["TSL"].split(';')
    vep_canonical = row["VEP_canonical"].split(';')
    deogen2_score = row["DEOGEN2_score"].split(';')
    '''
    parse mutpred top 5 features
    '''
    def modify_pvalue(pvalue):
        return float(pvalue.strip('P = '))
    mutpred_mechanisms = row["MutPred_Top5features"]
    if mutpred_mechanisms not in ['.', ',', '-']:
        mutpred_mechanisms = mutpred_mechanisms.split(" (") and mutpred_mechanisms.split(";")
        mutpred_mechanisms = [m.rstrip(")") for m in mutpred_mechanisms]
        mutpred_mechanisms = [i.split(" (") for i in mutpred_mechanisms]
        mutpred_mechanisms = sum(mutpred_mechanisms, [])
        mechanisms = [
            {"mechanism": mutpred_mechanisms[0],
             "p_val": modify_pvalue(mutpred_mechanisms[1])},
            {"mechanism": mutpred_mechanisms[2],
             "p_val": modify_pvalue(mutpred_mechanisms[3])},
            {"mechanism": mutpred_mechanisms[4],
             "p_val": modify_pvalue(mutpred_mechanisms[5])},
            {"mechanism": mutpred_mechanisms[6],
             "p_val": modify_pvalue(mutpred_mechanisms[7])},
            {"mechanism": mutpred_mechanisms[8],
             "p_val": modify_pvalue(mutpred_mechanisms[9])}
        ]
    else:
        mechanisms = '.'

    # normalize scores

    def norm(arr):
        return [None if item == '.' else item for item in arr]

    provean_score = norm(provean_score)
    sift_score = norm(sift_score)
    hdiv_score = norm(hdiv_score)
    hvar_score = norm(hvar_score)
    lrt_score = norm(lrt_score)
    m_cap_score = norm(m_cap_score)
    mutationtaster_score = norm(mutationtaster_score)
    mutationassessor_score = norm(mutationassessor_score)
    vest3_score = norm(vest3_score)
    metasvm_score = norm(metasvm_score)
    fathmm_score = norm(fathmm_score)
    metalr_score = norm(metalr_score)
    revel_score = norm(revel_score)

    gnomad = {"gnomad_exomes": {
                "flag": row["gnomAD_exomes_flag"],
                "ac": row["gnomAD_exomes_AC"],
                "an": row["gnomAD_exomes_AN"],
                "af": row["gnomAD_exomes_AF"],
                "nhomalt": row["gnomAD_exomes_nhomalt"],
                "afr_ac": row["gnomAD_exomes_AFR_AC"],
                "afr_af": row["gnomAD_exomes_AFR_AF"],
                "afr_an": row["gnomAD_exomes_AFR_AN"],
                "afr_nhomalt": row["gnomAD_exomes_AFR_nhomalt"],
                "amr_ac": row["gnomAD_exomes_AMR_AC"],
                "amr_an": row["gnomAD_exomes_AMR_AN"],
                "amr_af": row["gnomAD_exomes_AMR_AF"],
                "amr_nhomalt": row["gnomAD_exomes_AMR_nhomalt"],
                "asj_ac": row["gnomAD_exomes_ASJ_AC"],
                "asj_an": row["gnomAD_exomes_ASJ_AN"],
                "asj_af": row["gnomAD_exomes_ASJ_AF"],
                "asj_nhomalt": row["gnomAD_exomes_ASJ_nhomalt"],
                "eas_ac": row["gnomAD_exomes_EAS_AC"],
                "eas_af": row["gnomAD_exomes_EAS_AF"],
                "eas_an": row["gnomAD_exomes_EAS_AN"],
                "eas_nhomalt": row["gnomAD_exomes_EAS_nhomalt"],
                "fin_ac": row["gnomAD_exomes_FIN_AC"],
                "fin_af": row["gnomAD_exomes_FIN_AF"],
                "fin_an": row["gnomAD_exomes_FIN_AN"],
                "fin_nhomalt": row["gnomAD_exomes_FIN_nhomalt"],
                "nfe_ac": row["gnomAD_exomes_NFE_AC"],
                "nfe_af": row["gnomAD_exomes_NFE_AF"],
                "nfe_an": row["gnomAD_exomes_NFE_AN"],
                "nfe_nhomalt": row["gnomAD_exomes_NFE_nhomalt"],
                "sas_ac": row["gnomAD_exomes_SAS_AC"],
                "sas_af": row["gnomAD_exomes_SAS_AF"],
                "sas_an": row["gnomAD_exomes_SAS_AN"],
                "sas_nhomalt": row["gnomAD_exomes_SAS_nhomalt"],
                "popmax_ac": row["gnomAD_exomes_POPMAX_AC"],
                "popmax_af": row["gnomAD_exomes_POPMAX_AF"],
                "popmax_an": row["gnomAD_exomes_POPMAX_AN"],
                "popmax_nhomalt": row["gnomAD_exomes_POPMAX_nhomalt"]
            },
            "gnomad_exomes_controls": {
                "ac": row["gnomAD_exomes_controls_AC"],
                "an": row["gnomAD_exomes_controls_AN"],
                "af": row["gnomAD_exomes_controls_AF"],
                "nhomalt": row["gnomAD_exomes_controls_nhomalt"],
                "afr_ac": row["gnomAD_exomes_controls_AFR_AC"],
                "afr_af": row["gnomAD_exomes_controls_AFR_AF"],
                "afr_an": row["gnomAD_exomes_controls_AFR_AN"],
                "afr_nhomalt": row["gnomAD_exomes_controls_AFR_nhomalt"],
                "amr_ac": row["gnomAD_exomes_controls_AMR_AC"],
                "amr_an": row["gnomAD_exomes_controls_AMR_AN"],
                "amr_af": row["gnomAD_exomes_controls_AMR_AF"],
                "amr_nhomalt": row["gnomAD_exomes_controls_AMR_nhomalt"],
                "asj_ac": row["gnomAD_exomes_controls_ASJ_AC"],
                "asj_an": row["gnomAD_exomes_controls_ASJ_AN"],
                "asj_af": row["gnomAD_exomes_controls_ASJ_AF"],
                "asj_nhomalt": row["gnomAD_exomes_controls_ASJ_nhomalt"],
                "eas_ac": row["gnomAD_exomes_controls_EAS_AC"],
                "eas_af": row["gnomAD_exomes_controls_EAS_AF"],
                "eas_an": row["gnomAD_exomes_controls_EAS_AN"],
                "eas_nhomalt": row["gnomAD_exomes_controls_EAS_nhomalt"],
                "fin_ac": row["gnomAD_exomes_controls_FIN_AC"],
                "fin_af": row["gnomAD_exomes_controls_FIN_AF"],
                "fin_an": row["gnomAD_exomes_controls_FIN_AN"],
                "fin_nhomalt": row["gnomAD_exomes_controls_FIN_nhomalt"],
                "nfe_ac": row["gnomAD_exomes_controls_NFE_AC"],
                "nfe_af": row["gnomAD_exomes_controls_NFE_AF"],
                "nfe_an": row["gnomAD_exomes_controls_NFE_AN"],
                "nfe_nhomalt": row["gnomAD_exomes_controls_NFE_nhomalt"],
                "sas_ac": row["gnomAD_exomes_controls_SAS_AC"],
                "sas_af": row["gnomAD_exomes_controls_SAS_AF"],
                "sas_an": row["gnomAD_exomes_controls_SAS_AN"],
                "sas_nhomalt": row["gnomAD_exomes_controls_SAS_nhomalt"],
                "popmax_ac": row["gnomAD_exomes_controls_POPMAX_AC"],
                "popmax_af": row["gnomAD_exomes_controls_POPMAX_AF"],
                "popmax_an": row["gnomAD_exomes_controls_POPMAX_AN"],
                "popmax_nhomalt": row["gnomAD_exomes_controls_POPMAX_nhomalt"]
            },
            "gnomad_genomes": {
                "flag": row["gnomAD_genomes_flag"],
                "ac": row["gnomAD_genomes_AC"],
                "an": row["gnomAD_genomes_AN"],
                "af": row["gnomAD_genomes_AF"],
                "nhomalt": row["gnomAD_genomes_nhomalt"],
                "afr_ac": row["gnomAD_genomes_AFR_AC"],
                "afr_af": row["gnomAD_genomes_AFR_AF"],
                "afr_an": row["gnomAD_genomes_AFR_AN"],
                "afr_nhomalt": row["gnomAD_genomes_AFR_nhomalt"],
                "ami_ac": row["gnomAD_genomes_AMI_AC"],
                "ami_an": row["gnomAD_genomes_AMI_AN"],
                "ami_af": row["gnomAD_genomes_AMI_AF"],
                "ami_nhomalt": row["gnomAD_genomes_AMI_nhomalt"],
                "amr_ac": row["gnomAD_genomes_AMR_AC"],
                "amr_an": row["gnomAD_genomes_AMR_AN"],
                "amr_af": row["gnomAD_genomes_AMR_AF"],
                "amr_nhomalt": row["gnomAD_genomes_AMR_nhomalt"],
                "asj_ac": row["gnomAD_genomes_ASJ_AC"],
                "asj_an": row["gnomAD_genomes_ASJ_AN"],
                "asj_af": row["gnomAD_genomes_ASJ_AF"],
                "asj_nhomalt": row["gnomAD_genomes_ASJ_nhomalt"],
                "eas_ac": row["gnomAD_genomes_EAS_AC"],
                "eas_af": row["gnomAD_genomes_EAS_AF"],
                "eas_an": row["gnomAD_genomes_EAS_AN"],
                "eas_nhomalt": row["gnomAD_genomes_EAS_nhomalt"],
                "fin_ac": row["gnomAD_genomes_FIN_AC"],
                "fin_af": row["gnomAD_genomes_FIN_AF"],
                "fin_an": row["gnomAD_genomes_FIN_AN"],
                "fin_nhomalt": row["gnomAD_genomes_FIN_nhomalt"],
                "nfe_ac": row["gnomAD_genomes_NFE_AC"],
                "nfe_af": row["gnomAD_genomes_NFE_AF"],
                "nfe_an": row["gnomAD_genomes_NFE_AN"],
                "nfe_nhomalt": row["gnomAD_genomes_NFE_nhomalt"],
                "popmax_ac": row["gnomAD_genomes_POPMAX_AC"],
                "popmax_af": row["gnomAD_genomes_POPMAX_AF"],
                "popmax_an": row["gnomAD_genomes_POPMAX_AN"],
                "popmax_nhomalt": row["gnomAD_genomes_POPMAX_nhomalt"],
                "sas_ac": row["gnomAD_genomes_SAS_AC"],
                "sas_af": row["gnomAD_genomes_SAS_AF"],
                "sas_an": row["gnomAD_genomes_SAS_AN"],
                "sas_nhomalt": row["gnomAD_genomes_SAS_nhomalt"]
            }
        }

    # load as json data
    one_snp_json = {
        "_id": HGVS,
        "dbnsfp": {
            "rsid": row["rs_dbSNP"],  # for 4.2a
            # "rsid": row["rs_dbSNP151"],  # for 4.1a
            "chrom": chrom,
            "hg19": {
                "start": chromStart,
                "end": chromEnd
            },
            "hg18": {
                "start": row["hg18_pos(1-based)"],
                "end": hg18_end
            },
            "hg38": {
                "start": row["pos(1-based)"],
                "end": row["pos(1-based)"]
            },
            "ref": ref,
            "alt": alt,
            "aa": {
                "ref": row["aaref"],
                "alt": row["aaalt"],
                "pos": row["aapos"],
                "refcodon": row["refcodon"],
                "codonpos": row["codonpos"],
                "codon_degeneracy": row["codon_degeneracy"],
            },
            "genename": row["genename"],
            "uniprot": list(uniprot),
            "vindijia_neandertal": [i for i in row["VindijiaNeandertal"].split("/") if i != "."],
            "interpro_domain": row["Interpro_domain"],
            "cds_strand": row["cds_strand"],
            "ancestral_allele": row["Ancestral_allele"],
            "appris": appris,
            "genecode_basic": row["GENCODE_basic"],
            "tsl": tsl,
            "vep_canonical": vep_canonical,
            # "altaineandertal": fields[17],
            # "denisova": fields[18]
            "ensembl": {
                "geneid": row["Ensembl_geneid"],
                "transcriptid": row["Ensembl_transcriptid"],
                "proteinid": row["Ensembl_proteinid"]
            },
            "sift": {
                "score": sift_score,
                "converted_rankscore": row["SIFT_converted_rankscore"],
                "pred": row["SIFT_pred"]
            },
            "sift4g": {
                "score": sift4g_score,
                "pred": row["SIFT4G_score"],
                "converted_rankscore": row["SIFT4G_converted_rankscore"]
            },
            "polyphen2": {
                "hdiv": {
                    "score": hdiv_score,
                    "rankscore": row["Polyphen2_HDIV_rankscore"],
                    "pred": row["Polyphen2_HDIV_pred"]
                },
                "hvar": {
                    "score": hvar_score,
                    "rankscore": row["Polyphen2_HVAR_rankscore"],
                    "pred": row["Polyphen2_HVAR_pred"]
                }
            },
            "lrt": {
                "score": lrt_score,
                "converted_rankscore": row["LRT_converted_rankscore"],
                "pred": row["LRT_pred"],
                "omega": row["LRT_Omega"]
            },
            "mvp": {
                "score": mvp_score,
                "rankscore": row["MVP_rankscore"]
            },
            "mpc": {
                "score": mpc_score,
                "rankscore": row["MPC_rankscore"]
            },
            "bstatistic": {
                "score": row['bStatistic'],
                "converted_rankscore": row["bStatistic_converted_rankscore"]
            },
            "aloft": {
                "fraction_transcripts_affected": row["Aloft_Fraction_transcripts_affected"].split(';'),
                "prob_tolerant": row["Aloft_prob_Tolerant"],
                "prob_recessive": row["Aloft_prob_Recessive"],
                "prob_dominant": row["Aloft_prob_Dominant"],
                "pred": row["Aloft_pred"],
                "confidence": row["Aloft_Confidence"],
            },
            "primateai": {
                "score": row["PrimateAI_score"],
                "rankscore": row["PrimateAI_rankscore"],
                "pred": row["PrimateAI_pred"]
            },
            "mutationtaster": {
                "score": mutationtaster_score,
                "converted_rankscore": row["MutationTaster_converted_rankscore"],
                "pred": row["MutationTaster_pred"],
                "model": row["MutationTaster_model"],
                "AAE": row["MutationTaster_AAE"]
            },
            "mutationassessor": {
                "score": mutationassessor_score,
                "rankscore": row["MutationAssessor_rankscore"],
                "pred": row["MutationAssessor_pred"]
            },
            "fathmm": {
                "score": fathmm_score,
                "rankscore": row["FATHMM_converted_rankscore"],
                "pred": row["FATHMM_pred"]
            },
            "provean": {
                "score": provean_score,
                "rankscore": row["PROVEAN_converted_rankscore"],
                "pred": row["PROVEAN_pred"]
            },
            "vest4": {
                "score": vest3_score,
                "rankscore": row["VEST4_rankscore"]
            },
            "deogen2": {
                "score": deogen2_score,
                "rankscore": row["DEOGEN2_rankscore"],
                "pred": row["DEOGEN2_pred"]
            },
            "fathmm-mkl": {
                "coding_score": row["fathmm-MKL_coding_score"],
                "coding_rankscore": row["fathmm-MKL_coding_rankscore"],
                "coding_pred": row["fathmm-MKL_coding_pred"],
                "coding_group": row["fathmm-MKL_coding_group"]
            },
            "fathmm-xf": {
                "coding_score": row["fathmm-XF_coding_score"],
                "coding_rankscore": row["fathmm-XF_coding_rankscore"],
                "coding_pred": row["fathmm-XF_coding_pred"]
            },
            "eigen": {
                "raw_coding": row["Eigen-raw_coding"],
                "raw_coding_rankscore": row["Eigen-raw_coding_rankscore"],
                "phred_coding": row["Eigen-phred_coding"]
            },
            "eigen-pc": {
                "raw_coding": row["Eigen-PC-raw_coding"],
                "phred_coding": row["Eigen-PC-phred_coding"],
                "raw_rankscore": row["Eigen-PC-raw_coding_rankscore"]
            },
            "genocanyon": {
                "score": row["GenoCanyon_score"],
                "rankscore": row["GenoCanyon_rankscore"]
            },
            "metasvm": {
                "score": metasvm_score,
                "rankscore": row["MetaSVM_rankscore"],
                "pred": row["MetaSVM_pred"]
            },
            "metalr": {
                "score": metalr_score,
                "rankscore": row["MetaLR_rankscore"],
                "pred": row["MetaLR_pred"]
            },
            "reliability_index": row["Reliability_index"],
            "m_cap_score": {
                "score": m_cap_score,
                "rankscore": row["M-CAP_rankscore"],
                "pred": row["M-CAP_pred"]
            },
            "revel": {
                "score": revel_score,
                "rankscore": row["REVEL_rankscore"]
            },
            "mutpred": {
                "score": row["MutPred_score"],
                "rankscore": row["MutPred_rankscore"],
                "accession": row["MutPred_protID"],
                "aa_change": row["MutPred_AAchange"],
                "pred": mechanisms
            },
            "dann": {
                "score": row["DANN_score"],
                "rankscore": row["DANN_rankscore"]
            },
            "gerp++": {
                "nr": row["GERP++_NR"],
                "rs": row["GERP++_RS"],
                "rs_rankscore": row["GERP++_RS_rankscore"]
            },
            "integrated": {
                "fitcons_score": row["integrated_fitCons_score"],
                "fitcons_rankscore": row["integrated_fitCons_rankscore"],
                "confidence_value": row["integrated_confidence_value"]
            },
            "gm12878": {
                "fitcons_score": row["GM12878_fitCons_score"],
                "fitcons_rankscore": row["GM12878_fitCons_rankscore"],
                "confidence_value": row["GM12878_confidence_value"]
            },
            "h1-hesc": {
                "fitcons_score": row["H1-hESC_fitCons_score"],
                "fitcons_rankscore": row["H1-hESC_fitCons_rankscore"],
                "confidence_value": row["H1-hESC_confidence_value"]
            },
            "huvec": {
                "fitcons_score": row["HUVEC_fitCons_score"],
                "fitcons_rankscore": row["HUVEC_fitCons_rankscore"],
                "confidence_value": row["HUVEC_confidence_value"]
            },
            "phylo": {
                "p100way": {
                    "vertebrate": row["phyloP100way_vertebrate"],
                    "vertebrate_rankscore": row["phyloP100way_vertebrate_rankscore"]
                },
                "p30way": {
                    "mammalian": row["phyloP30way_mammalian"],
                    "mammalian_rankscore": row["phyloP30way_mammalian_rankscore"]
                },
                "p17way": {
                    "primate": row["phyloP17way_primate"],
                    "primate_rankscore": row["phyloP17way_primate_rankscore"]
                }
            },
            "phastcons": {
                "100way": {
                    "vertebrate": row["phastCons100way_vertebrate"],
                    "vertebrate_rankscore": row["phastCons100way_vertebrate_rankscore"]
                },
                "30way": {
                    "mammalian": row["phastCons30way_mammalian"],
                    "mammalian_rankscore": row["phastCons30way_mammalian_rankscore"]
                },
                "p17way": {
                    "primate": row["phastCons17way_primate"],
                    "primate_rankscore": row["phastCons17way_primate_rankscore"]
                }
            },
            "siphy_29way": {
                "pi": siphy,
                "logodds": row["SiPhy_29way_logOdds"],
                "logodds_rankscore": row["SiPhy_29way_logOdds_rankscore"]
            },
            "bayesdel": {
                "add_af": {
                    "score": row["BayesDel_addAF_score"],
                    "rankscore": row["BayesDel_addAF_rankscore"],
                    "pred": row["BayesDel_addAF_pred"]
                },
                "no_af": {
                    "score": row["BayesDel_noAF_score"],
                    "rankscore": row["BayesDel_noAF_rankscore"],
                    "pred": row["BayesDel_noAF_pred"]
                }
            },
            "clinpred": {
                "score": row["ClinPred_score"],
                "rankscore": row["ClinPred_rankscore"],
                "pred": row["ClinPred_pred"]
            },
            "list-s2": {
                "score": row["LIST-S2_score"],
                "rankscore": row["LIST-S2_rankscore"],
                "pred": row["LIST-S2_pred"]
            },
            "1000gp3": {
                "ac": row["1000Gp3_AC"],
                "af": row["1000Gp3_AF"],
                "afr_ac": row["1000Gp3_AFR_AC"],
                "afr_af": row["1000Gp3_AFR_AF"],
                "eur_ac": row["1000Gp3_EUR_AC"],
                "eur_af": row["1000Gp3_EUR_AF"],
                "amr_ac": row["1000Gp3_AMR_AC"],
                "amr_af": row["1000Gp3_AMR_AF"],
                "eas_ac": row["1000Gp3_EAS_AC"],
                "eas_af": row["1000Gp3_EAS_AF"],
                "sas_ac": row["1000Gp3_SAS_AC"],
                "sas_af": row["1000Gp3_SAS_AF"]
            },
            "twinsuk": {
                "ac": row["TWINSUK_AC"],
                "af": row["TWINSUK_AF"]
            },
            "alspac": {
                "ac": row["ALSPAC_AC"],
                "af": row["ALSPAC_AF"]
            },
            "esp6500": {
                "aa_ac": row["ESP6500_AA_AC"],
                "aa_af": row["ESP6500_AA_AF"],
                "ea_ac": row["ESP6500_EA_AC"],
                "ea_af": row["ESP6500_EA_AF"]
            },
            "uk10k": {
                "ac": row["UK10K_AC"],
                "af": row["UK10K_AF"]
            },
            "exac": {
                "ac": row["ExAC_AC"],
                "af": row["ExAC_AF"],
                "adj_ac": row["ExAC_Adj_AC"],
                "adj_af": row["ExAC_Adj_AF"],
                "afr_ac": row["ExAC_AFR_AC"],
                "afr_af": row["ExAC_AFR_AF"],
                "amr_ac": row["ExAC_AMR_AC"],
                "amr_af": row["ExAC_AMR_AF"],
                "eas_ac": row["ExAC_EAS_AC"],
                "eas_af": row["ExAC_EAS_AF"],
                "fin_ac": row["ExAC_FIN_AC"],
                "fin_af": row["ExAC_FIN_AF"],
                "nfe_ac": row["ExAC_NFE_AC"],
                "nfe_af": row["ExAC_NFE_AF"],
                "sas_ac": row["ExAC_SAS_AC"],
                "sas_af": row["ExAC_SAS_AF"]
            },
            "exac_nontcga": {
                "ac": row["ExAC_nonTCGA_AC"],
                "af": row["ExAC_nonTCGA_AF"],
                "adj_ac": row["ExAC_nonTCGA_Adj_AC"],
                "adj_af": row["ExAC_nonTCGA_Adj_AF"],
                "afr_ac": row["ExAC_nonTCGA_AFR_AC"],
                "afr_af": row["ExAC_nonTCGA_AFR_AF"],
                "amr_ac": row["ExAC_nonTCGA_AMR_AC"],
                "amr_af": row["ExAC_nonTCGA_AMR_AF"],
                "eas_ac": row["ExAC_nonTCGA_EAS_AC"],
                "eas_af": row["ExAC_nonTCGA_EAS_AF"],
                "fin_ac": row["ExAC_nonTCGA_FIN_AC"],
                "fin_af": row["ExAC_nonTCGA_FIN_AF"],
                "nfe_ac": row["ExAC_nonTCGA_NFE_AC"],
                "nfe_af": row["ExAC_nonTCGA_NFE_AF"],
                "sas_ac": row["ExAC_nonTCGA_SAS_AC"],
                "sas_af": row["ExAC_nonTCGA_SAS_AF"]
            },
            "exac_nonpsych": {
                "ac": row["ExAC_nonpsych_AC"],
                "af": row["ExAC_nonpsych_AF"],
                "adj_ac": row["ExAC_nonpsych_Adj_AC"],
                "adj_af": row["ExAC_nonpsych_Adj_AF"],
                "afr_ac": row["ExAC_nonpsych_AFR_AC"],
                "afr_af": row["ExAC_nonpsych_AFR_AF"],
                "amr_ac": row["ExAC_nonpsych_AMR_AC"],
                "amr_af": row["ExAC_nonpsych_AMR_AF"],
                "eas_ac": row["ExAC_nonpsych_EAS_AC"],
                "eas_af": row["ExAC_nonpsych_EAS_AF"],
                "fin_ac": row["ExAC_nonpsych_FIN_AC"],
                "fin_af": row["ExAC_nonpsych_FIN_AF"],
                "nfe_ac": row["ExAC_nonpsych_NFE_AC"],
                "nfe_af": row["ExAC_nonpsych_NFE_AF"],
                "sas_ac": row["ExAC_nonpsych_SAS_AC"],
                "sas_af": row["ExAC_nonpsych_SAS_AF"]
            },
            "clinvar": {
                "clinvar_id": row["clinvar_id"],
                "clinsig": [i for i in row["clinvar_clnsig"].split("/") if i != "."],
                "trait": [i for i in row["clinvar_trait"].split("|") if i != "."],
                "review": [i for i in row["clinvar_review"].split(",") if i != "."],
                "hgvs": [i for i in row["clinvar_hgvs"].split("|") if i != "."],
                "omim": [i for i in row["clinvar_OMIM_id"].split("|") if i != "."],
                "medgen": [i for i in row["clinvar_MedGen_id"].split("|") if i != "."],
                "orphanet": [i for i in row["clinvar_Orphanet_id"].split("|") if i != "."],
                "var_source": [i for i in row["clinvar_var_source"].split("|") if i != "."]
            },
            "hgvsc": list(set(row["HGVSc_ANNOVAR"].split(';') + row["HGVSc_snpEff"].split(';') + row["HGVSc_VEP"].split(';'))),
            "hgvsp": list(set(row["HGVSp_ANNOVAR"].split(';') + row["HGVSp_snpEff"].split(';') + row["HGVSp_VEP"].split(';'))),
            "gtex": list(gtex),
            "geuvadis_eqtl_target_gene": row["Geuvadis_eQTL_target_gene"]
        }
    }
    if include_gnomad:
        one_snp_json['dbnsfp'].update(gnomad)
    one_snp_json = list_split(dict_sweep(unlist(value_convert_to_number(one_snp_json)), vals=[".", '-', "NA", None], remove_invalid_list=True), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version, include_gnomad):
    with anyfile(input_file) as file:
        file_reader = csv.reader(file, delimiter="\t")

        header = next(file_reader)
        assert len(header) == VALID_COLUMN_NO, "Expecting %s columns, but got %s" % (VALID_COLUMN_NO, len(header))

        previous_row = None
        for row in file_reader:
            row = dict(zip(header, row))

            # use transpose matrix to have 1 line with N 187 columns
            current_row = _map_row_to_json(row, version=version, include_gnomad=include_gnomad)
            if previous_row and current_row:
                if current_row["_id"] == previous_row["_id"]:
                    aa = previous_row["dbnsfp"]["aa"]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(current_row["dbnsfp"]["aa"])
                    previous_row["dbnsfp"]["aa"] = aa
                    if len(previous_row["dbnsfp"]["aa"]) > 1:
                        continue
                else:
                    yield previous_row

            previous_row = current_row

        if previous_row:
            yield previous_row


def load_data_file(input_file, version, include_gnomad=False):
    data = data_generator(input_file, version=version, include_gnomad=include_gnomad)
    for one_snp_json in data:
        yield one_snp_json


# load path and find files, pass to data_generator
def load_data(path_glob, version='hg19', include_gnomad=False):
    for input_file in sorted(glob.glob(path_glob)):
        for d in load_data_file(input_file, version, include_gnomad):
            yield d
