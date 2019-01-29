import csv
import glob
from biothings.utils.dataload import list_split, dict_sweep, unlist, value_convert_to_number


VALID_COLUMN_NO = 245

'''this parser is for dbNSFP v3.5a beta2 downloaded from
https://sites.google.com/site/jpopgen/dbNSFP'''

# convert one snp to json
def _map_line_to_json(df, version, include_gnomad, index=0):
    # specific variable treatment
    chrom = df["#chr"]
    if chrom == 'M':
        chrom = 'MT'
    # fields[7] in version 2, represent hg18_pos
    hg18_end = df["hg18_pos(1-based)"]
    if hg18_end == ".":
        hg18_end = "."
    else:
        hg18_end = int(hg18_end)
    # in case of no hg19 position provided, remove the item
    if df["hg19_pos(1-based)"] == '.':
        return None
    else:
        chromStart = int(df["hg19_pos(1-based)"])
        chromEnd = chromStart
    chromStart_38 = int(df["pos(1-based)"])
    ref = df["ref"].upper()
    alt = df["alt"].upper()
    HGVS_19 = "chr%s:g.%d%s>%s" % (chrom, chromStart, ref, alt)
    HGVS_38 = "chr%s:g.%d%s>%s" % (chrom, chromStart_38, ref, alt)
    if version == 'hg19':
        HGVS = HGVS_19
    elif version == 'hg38':
        HGVS = HGVS_38
    siphy_29way_pi = df["SiPhy_29way_pi"]
    if siphy_29way_pi == ".":
        siphy = "."
    else:
        freq = siphy_29way_pi.split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}
    gtex_gene = df["GTEx_V7p_gene"].split('|')
    gtex_tissue = df["GTEx_V7p_tissue"].split('|')
    gtex = map(dict, map(lambda t: zip(('gene', 'tissue'), t), zip(gtex_gene, gtex_tissue)))
    acc = df["Uniprot_acc_Polyphen2"].rstrip().rstrip(';').split(";")
    pos = df["Uniprot_aapos_Polyphen2"].rstrip().rstrip(';').split(";")
    uniprot = map(dict, map(lambda t: zip(('acc', 'pos'), t), zip(acc, pos)))
    provean_score = df["PROVEAN_score"].split(';')
    sift_score = df["SIFT_score"].split(';')
    hdiv_score = df["Polyphen2_HDIV_score"].split(';')
    hvar_score = df["Polyphen2_HVAR_score"].split(';')
    lrt_score = df["LRT_score"].split(';')
    m_cap_score = df["M-CAP_score"].split(';')
    mutationtaster_score = df["MutationTaster_score"].split(';')
    mutationassessor_score = df["MutationAssessor_score"].split(';')
    vest3_score = df["VEST4_score"].split(';')
    metasvm_score = df["MetaSVM_score"].split(';')
    fathmm_score = df["FATHMM_score"].split(';')
    metalr_score = df["MetaLR_score"].split(';')
    revel_score = df["REVEL_score"].split(';')
    '''
    parse mutpred top 5 features
    '''
    def modify_pvalue(pvalue):
        return float(pvalue.strip('P = '))
    mutpred_mechanisms = df["MutPred_Top5features"]
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
                "ac": df["gnomAD_exomes_AC"],
                "an": df["gnomAD_exomes_AN"],
                "af": df["gnomAD_exomes_AF"],                
                "afr_ac": df["gnomAD_exomes_AFR_AC"],
                "afr_af": df["gnomAD_exomes_AFR_AF"],
                "afr_an": df["gnomAD_exomes_AFR_AN"],
                "amr_ac": df["gnomAD_exomes_AMR_AC"],
                "amr_an": df["gnomAD_exomes_AMR_AN"],
                "amr_af": df["gnomAD_exomes_AMR_AF"],
                "asj_ac": df["gnomAD_exomes_ASJ_AC"],
                "asj_an": df["gnomAD_exomes_ASJ_AN"],
                "asj_af": df["gnomAD_exomes_ASJ_AF"],
                "eas_ac": df["gnomAD_exomes_EAS_AC"],
                "eas_af": df["gnomAD_exomes_EAS_AF"],
                "eas_an": df["gnomAD_exomes_EAS_AN"],
                "fin_ac": df["gnomAD_exomes_FIN_AC"],
                "fin_af": df["gnomAD_exomes_FIN_AF"],
                "fin_an": df["gnomAD_exomes_FIN_AN"],
                "nfe_ac": df["gnomAD_exomes_NFE_AC"],
                "nfe_af": df["gnomAD_exomes_NFE_AF"],
                "nfe_an": df["gnomAD_exomes_NFE_AN"],
                "sas_ac": df["gnomAD_exomes_SAS_AC"],
                "sas_af": df["gnomAD_exomes_SAS_AF"],
                "sas_an": df["gnomAD_exomes_SAS_AN"],
                "oth_ac": df["gnomAD_exomes_OTH_AC"],
                "oth_af": df["gnomAD_exomes_OTH_AF"],
                "oth_an": df["gnomAD_exomes_OTH_AN"]
            },
            "gnomad_genomes": {
                "ac": df["gnomAD_genomes_AC"],
                "an": df["gnomAD_genomes_AN"],
                "af": df["gnomAD_genomes_AF"],                
                "afr_ac": df["gnomAD_genomes_AFR_AC"],
                "afr_af": df["gnomAD_genomes_AFR_AF"],
                "afr_an": df["gnomAD_genomes_AFR_AN"],
                "amr_ac": df["gnomAD_genomes_AMR_AC"],
                "amr_an": df["gnomAD_genomes_AMR_AN"],
                "amr_af": df["gnomAD_genomes_AMR_AF"],
                "asj_ac": df["gnomAD_genomes_ASJ_AC"],
                "asj_an": df["gnomAD_genomes_ASJ_AN"],
                "asj_af": df["gnomAD_genomes_ASJ_AF"],
                "eas_ac": df["gnomAD_genomes_EAS_AC"],
                "eas_af": df["gnomAD_genomes_EAS_AF"],
                "eas_an": df["gnomAD_genomes_EAS_AN"],
                "fin_ac": df["gnomAD_genomes_FIN_AC"],
                "fin_af": df["gnomAD_genomes_FIN_AF"],
                "fin_an": df["gnomAD_genomes_FIN_AN"],
                "nfe_ac": df["gnomAD_genomes_NFE_AC"],
                "nfe_af": df["gnomAD_genomes_NFE_AF"],
                "nfe_an": df["gnomAD_genomes_NFE_AN"],
                "oth_ac": df["gnomAD_genomes_OTH_AC"],
                "oth_af": df["gnomAD_genomes_OTH_AF"],
                "oth_an": df["gnomAD_genomes_OTH_AN"]
            }
        }

# load as json data
    one_snp_json = {
        "_id": HGVS,
        "dbnsfp": {
            "rsid": df["rs_dbSNP150"],
            #"rsid_dbSNP144": fields[6],
            "chrom": chrom,
            "hg19": {
                "start": chromStart,
                "end": chromEnd
            },
            "hg18": {
                "start": df["hg18_pos(1-based)"],
                "end": hg18_end
            },
            "hg38": {
                "start": df["pos(1-based)"],
                "end": df["pos(1-based)"]
            },
            "ref": ref,
            "alt": alt,
            "aa": {
                "ref": df["aaref"],
                "alt": df["aaalt"],
                "pos": df["aapos"],
                "refcodon": df["refcodon"],
                "codonpos": df["codonpos"],
                "codon_degeneracy": df["codon_degeneracy"],
            },
            "genename": df["genename"],
            "uniprot": list(uniprot),
            "interpro_domain": df["Interpro_domain"],
            "cds_strand": df["cds_strand"],
            "ancestral_allele": df["Ancestral_allele"],
            #"altaineandertal": fields[17],
            #"denisova": fields[18]
            "ensembl": {
                "geneid": df["Ensembl_geneid"],
                "transcriptid": df["Ensembl_transcriptid"],
                "proteinid": df["Ensembl_proteinid"]
            },
            "sift": {
                "score": sift_score,
                "converted_rankscore": df["SIFT_converted_rankscore"],
                "pred": df["SIFT_pred"]
            },
            "polyphen2": {
                "hdiv": {
                    "score": hdiv_score,
                    "rankscore": df["Polyphen2_HDIV_rankscore"],
                    "pred": df["Polyphen2_HDIV_pred"]
                },
                "hvar": {
                    "score": hvar_score,
                    "rankscore": df["Polyphen2_HVAR_rankscore"],
                    "pred": df["Polyphen2_HVAR_pred"]
                }
            },
            "lrt": {
                "score": lrt_score,
                "converted_rankscore": df["LRT_converted_rankscore"],
                "pred": df["LRT_pred"],
                "omega": df["LRT_Omega"]
            },
            "mutationtaster": {
                "score": mutationtaster_score,
                "converted_rankscore": df["MutationTaster_converted_rankscore"],
                "pred": df["MutationTaster_pred"],
                "model": df["MutationTaster_model"],
                "AAE": df["MutationTaster_AAE"]
            },
            "mutationassessor": {
                "score": mutationassessor_score,
                "rankscore": df["MutationAssessor_rankscore"],
                "pred": df["MutationAssessor_pred"]
            },
            "fathmm": {
                "score": fathmm_score,
                "rankscore": df["FATHMM_converted_rankscore"],
                "pred": df["FATHMM_pred"]
            },
            "provean": {
                "score": provean_score,
                "rankscore": df["PROVEAN_converted_rankscore"],
                "pred": df["PROVEAN_pred"]
            },
            "vest4": {
                "score": vest3_score,
                "rankscore": df["VEST4_rankscore"]
            },
            "fathmm-mkl": {
                "coding_score": df["fathmm-MKL_coding_score"],
                "coding_rankscore": df["fathmm-MKL_coding_rankscore"],
                "coding_pred": df["fathmm-MKL_coding_pred"],
                "coding_group": df["fathmm-MKL_coding_group"]
            },
            "eigen": {
                "coding_or_noncoding": df["Eigen_coding_or_noncoding"],
                "raw_coding": df["Eigen-raw_coding"],
                "phred_coding": df["Eigen-phred_coding"]
            },
            "eigen-pc": {
                "raw_coding": df["Eigen-PC-raw_coding"],
                "phred_coding": df["Eigen-PC-phred_coding"],
                "raw_rankscore": df["Eigen-PC-raw_rankscore"]
            },
            "genocanyon": {
                "score": df["GenoCanyon_score"],
                "rankscore": df["GenoCanyon_rankscore"]
            },
            "metasvm": {
                "score": metasvm_score,
                "rankscore": df["MetaSVM_rankscore"],
                "pred": df["MetaSVM_pred"]
            },
            "metalr": {
                "score": metalr_score,
                "rankscore": df["MetaLR_rankscore"],
                "pred": df["MetaLR_pred"]
            },
            "reliability_index": df["Reliability_index"],
            "m_cap_score": {
                "score": m_cap_score,
                "rankscore": df["M-CAP_rankscore"],
                "pred": df["M-CAP_pred"]
            },
            "revel": {
                "score": revel_score,
                "rankscore": df["REVEL_rankscore"]
            },
            "mutpred": {
                "score": df["MutPred_score"],
                "rankscore": df["MutPred_rankscore"],
                "accession": df["MutPred_protID"],
                "aa_change": df["MutPred_AAchange"],
                "pred": mechanisms
            },
            "dann": {
                "score": df["DANN_score"],
                "rankscore": df["DANN_rankscore"]
            },
            "gerp++": {
                "nr": df["GERP++_NR"],
                "rs": df["GERP++_RS"],
                "rs_rankscore": df["GERP++_RS_rankscore"]
            },
            "integrated": {
                "fitcons_score": df["integrated_fitCons_score"],
                "fitcons_rankscore": df["integrated_fitCons_rankscore"],
                "confidence_value": df["integrated_confidence_value"]
            },
            "gm12878": {
                "fitcons_score": df["GM12878_fitCons_score"],
                "fitcons_rankscore": df["GM12878_fitCons_rankscore"],
                "confidence_value": df["GM12878_confidence_value"]
            },
            "h1-hesc": {
                "fitcons_score": df["H1-hESC_fitCons_score"],
                "fitcons_rankscore": df["H1-hESC_fitCons_rankscore"],
                "confidence_value": df["H1-hESC_confidence_value"]
            },
            "huvec": {
                "fitcons_score": df["HUVEC_fitCons_score"],
                "fitcons_rankscore": df["HUVEC_fitCons_rankscore"],
                "confidence_value": df["HUVEC_confidence_value"]
            },
            "phylo": {
                "p100way": {
                    "vertebrate": df["phyloP100way_vertebrate"],
                    "vertebrate_rankscore": df["phyloP100way_vertebrate_rankscore"]
                },
                "p30way": {
                    "mammalian": df["phyloP30way_mammalian"],
                    "mammalian_rankscore": df["phyloP30way_mammalian_rankscore"]
                }
            },
            "phastcons": {
                "100way": {
                    "vertebrate": df["phastCons100way_vertebrate"],
                    "vertebrate_rankscore": df["phastCons100way_vertebrate_rankscore"]
                },
                "30way": {
                    "mammalian": df["phastCons30way_mammalian"],
                    "mammalian_rankscore": df["phastCons30way_mammalian_rankscore"]
                }
            },
            "siphy_29way": {
                "pi": siphy,
                "logodds": df["SiPhy_29way_logOdds"],
                "logodds_rankscore": df["SiPhy_29way_logOdds_rankscore"]
            },
            "1000gp3": {
                "ac": df["1000Gp3_AC"],
                "af": df["1000Gp3_AF"],
                "afr_ac": df["1000Gp3_AFR_AC"],
                "afr_af": df["1000Gp3_AFR_AF"],
                "eur_ac": df["1000Gp3_EUR_AC"],
                "eur_af": df["1000Gp3_EUR_AF"],
                "amr_ac": df["1000Gp3_AMR_AC"],
                "amr_af": df["1000Gp3_AMR_AF"],
                "eas_ac": df["1000Gp3_EAS_AC"],
                "eas_af": df["1000Gp3_EAS_AF"],
                "sas_ac": df["1000Gp3_SAS_AC"],
                "sas_af": df["1000Gp3_SAS_AF"]
            },
            "twinsuk": {
                "ac": df["TWINSUK_AC"],
                "af": df["TWINSUK_AF"]
            },
            "alspac": {
                "ac": df["ALSPAC_AC"],
                "af": df["ALSPAC_AF"]
            },
            "esp6500": {
                "aa_ac": df["ESP6500_AA_AC"],
                "aa_af": df["ESP6500_AA_AF"],
                "ea_ac": df["ESP6500_EA_AC"],
                "ea_af": df["ESP6500_EA_AF"]
            },
            "exac": {
                "ac": df["ExAC_AC"],
                "af": df["ExAC_AF"],
                "adj_ac": df["ExAC_Adj_AC"],
                "adj_af": df["ExAC_Adj_AF"],
                "afr_ac": df["ExAC_AFR_AC"],
                "afr_af": df["ExAC_AFR_AF"],
                "amr_ac": df["ExAC_AMR_AC"],
                "amr_af": df["ExAC_AMR_AF"],
                "eas_ac": df["ExAC_EAS_AC"],
                "eas_af": df["ExAC_EAS_AF"],
                "fin_ac": df["ExAC_FIN_AC"],
                "fin_af": df["ExAC_FIN_AF"],
                "nfe_ac": df["ExAC_NFE_AC"],
                "nfe_af": df["ExAC_NFE_AF"],
                "sas_ac": df["ExAC_SAS_AC"],
                "sas_af": df["ExAC_SAS_AF"]
            },
            "exac_nontcga": {
                "ac": df["ExAC_nonTCGA_AC"],
                "af": df["ExAC_nonTCGA_AF"],
                "adj_ac": df["ExAC_nonTCGA_Adj_AC"],
                "adj_af": df["ExAC_nonTCGA_Adj_AF"],
                "afr_ac": df["ExAC_nonTCGA_AFR_AC"],
                "afr_af": df["ExAC_nonTCGA_AFR_AF"],
                "amr_ac": df["ExAC_nonTCGA_AMR_AC"],
                "amr_af": df["ExAC_nonTCGA_AMR_AF"],
                "eas_ac": df["ExAC_nonTCGA_EAS_AC"],
                "eas_af": df["ExAC_nonTCGA_EAS_AF"],
                "fin_ac": df["ExAC_nonTCGA_FIN_AC"],
                "fin_af": df["ExAC_nonTCGA_FIN_AF"],
                "nfe_ac": df["ExAC_nonTCGA_NFE_AC"],
                "nfe_af": df["ExAC_nonTCGA_NFE_AF"],
                "sas_ac": df["ExAC_nonTCGA_SAS_AC"],
                "sas_af": df["ExAC_nonTCGA_SAS_AF"]
            },
            "exac_nonpsych": {
                "ac": df["ExAC_nonpsych_AC"],
                "af": df["ExAC_nonpsych_AF"],
                "adj_ac": df["ExAC_nonpsych_Adj_AC"],
                "adj_af": df["ExAC_nonpsych_Adj_AF"],
                "afr_ac": df["ExAC_nonpsych_AFR_AC"],
                "afr_af": df["ExAC_nonpsych_AFR_AF"],
                "amr_ac": df["ExAC_nonpsych_AMR_AC"],
                "amr_af": df["ExAC_nonpsych_AMR_AF"],
                "eas_ac": df["ExAC_nonpsych_EAS_AC"],
                "eas_af": df["ExAC_nonpsych_EAS_AF"],
                "fin_ac": df["ExAC_nonpsych_FIN_AC"],
                "fin_af": df["ExAC_nonpsych_FIN_AF"],
                "nfe_ac": df["ExAC_nonpsych_NFE_AC"],
                "nfe_af": df["ExAC_nonpsych_NFE_AF"],
                "sas_ac": df["ExAC_nonpsych_SAS_AC"],
                "sas_af": df["ExAC_nonpsych_SAS_AF"]
            },
            "clinvar": {
                "rs": df["clinvar_rs"],
                "clinsig": list(map(int,[i for i in df["clinvar_clnsig"].split("|") if i != "."])),
                "trait": [i for i in df["clinvar_trait"].split("|") if i != "."],
                "golden_stars": list(map(int,[i for i in df["clinvar_review"].split("|") if i != "."]))
            },
            "gtex": list(gtex)
        }
    }
    if include_gnomad:
        one_snp_json['dbnsfp'].update(gnomad)
    one_snp_json = list_split(dict_sweep(unlist(value_convert_to_number(one_snp_json)), vals=[".", '-', None]), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version, include_gnomad):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    index = next(db_nsfp)
    assert len(index) == VALID_COLUMN_NO, "Expecting %s columns, but got %s" % (VALID_COLUMN_NO, len(index))
    previous_row = None
    for row in db_nsfp:
        df = dict(zip(index, row))
        # use transpose matrix to have 1 row with N 187 columns
        current_row = _map_line_to_json(df, version=version, include_gnomad=include_gnomad)
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
