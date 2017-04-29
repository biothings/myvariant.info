import csv
import glob
from utils.dataload import list_split, dict_sweep, unlist


VALID_COLUMN_NO = 136

'''this parser is for dbNSFP v3.3a beta2 downloaded from
https://sites.google.com/site/jpopgen/dbNSFP'''

# convert one snp to json
def _map_line_to_json(df, version, index=0):
    # specific variable treatment
    chrom = df["#chr"]
    if chrom == 'M':
        chrom = 'MT'
    # fields[7] in version 2, represent hg18_pos
    hg18_end = df["hg18_pos(1-coor)"]
    if hg18_end == ".":
        hg18_end = "."
    else:
        hg18_end = int(hg18_end)
    # in case of no hg19 position provided, remove the item
    if df["pos(1-coor)"] == '.':
        return None
    else:
        chromStart = int(df["pos(1-coor)"])
        chromEnd = chromStart
    chromStart_38 = int(df["hg38_pos"])
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
    acc = df["Uniprot_acc"].rstrip().rstrip(';').split(";")
    pos = df["Uniprot_aapos"].rstrip().rstrip(';').split(";")
    uniprot = map(dict, map(lambda t: zip(('acc', 'pos'), t), zip(acc, pos)))
    provean_score = df["PROVEAN_score"].split(';')
    sift_score = df["SIFT_score"].split(';')
    hdiv_score = df["Polyphen2_HDIV_score"].split(';')
    hvar_score = df["Polyphen2_HVAR_score"].split(';')
    lrt_score = df["LRT_score"].split(';')
    m_cap_score = df["M-CAP_score"].split(';')
    mutationtaster_score = df["MutationTaster_score"].split(';')
    mutationassessor_score = df["MutationAssessor_score"].split(';')
    vest3_score = df["VEST3_score"].split(';')
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

# load as json data
    one_snp_json = {
        "_id": HGVS,
        "dbnsfp": {
            "rsid": df["rs_dbSNP147"],
            #"rsid_dbSNP144": fields[6],
            "chrom": chrom,
            "hg19": {
                "start": chromStart,
                "end": chromEnd
            },
            "hg18": {
                "start": df["hg18_pos(1-coor)"],
                "end": hg18_end
            },
            "hg38": {
                "start": df["hg38_pos"],
                "end": df["hg38_pos"]
            },
            "ref": ref,
            "alt": alt,
            "aa": {
                "ref": df["aaref"],
                "alt": df["aaalt"],
                "pos": df["aapos"],
                "refcodon": df["refcodon"],
                "codonpos": df["codonpos"]
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
                "transcriptid": df["Ensembl_transcriptid"]
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
                "pred": df["MutationTaster_pred"]
            },
            "mutationassessor": {
                "score": mutationassessor_score,
                "rankscore": df["MutationAssessor_rankscore"],
                "pred": df["MutationAssessor_pred"]
            },
            "fathmm": {
                "score": fathmm_score,
                "rankscore": df["FATHMM_rankscore"],
                "pred": df["FATHMM_pred"]
            },
            "provean": {
                "score": provean_score,
                "rankscore": df["PROVEAN_converted_rankscore"],
                "pred": df["PROVEAN_pred"]
            },
            "vest3": {
                "score": vest3_score,
                "rankscore": df["VEST3_rankscore"]
            },
            "eigen": {
                "coding_or_noncoding": df["Eigen_coding_or_noncoding"],
                "raw": df["Eigen-raw"],
                "phred": df["Eigen-phred"]
            },
            "eigen-pc": {
                "raw": df["Eigen-PC-raw"],
                "phred": df["Eigen-PC-phred"],
                "raw_rankscore": df["Eigen-PC-raw_rankscore"]
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
            "gerp++": {
                "nr": df["GERP++_NR"],
                "rs": df["GERP++_RS"],
                "rs_rankscore": df["GERP++_RS_rankscore"]
            },
            "phylo": {
                "p100way": {
                    "vertebrate": df["phyloP100way_vertebrate"],
                    "vertebrate_rankscore": df["phyloP100way_vertebrate_rankscore"]
                },
                "p46way": {
                    "placental": df["phyloP46way_placental"],
                    "placental_rankscore": df["phyloP46way_placental_rankscore"],
                    "primate": df["phyloP46way_primate"],
                    "primate_rankscore": df["phyloP46way_primate_rankscore"]
                }
            },
            "phastcons": {
                "100way": {
                    "vertebrate": df["phastCons100way_vertebrate"],
                    "vertebrate_rankscore": df["phastCons100way_vertebrate_rankscore"]
                },
                "46way": {
                    "placental": df["phastCons46way_placental"],
                    "placental_rankscore": df["phastCons46way_placental_rankscore"],
                    "primate": df["phastCons46way_primate"],
                    "primate_rankscore": df["phastCons46way_primate_rankscore"]
                }
            },
            "siphy_29way": {
                "pi": siphy,
                "logodds": df["SiPhy_29way_logOdds"],
                "logodds_rankscore": df["SiPhy_29way_logOdds_rankscore"]
            },
            "1000gp1": {
                "ac": df["1000Gp1_AC"],
                "af": df["1000Gp1_AF"],
                "afr_ac": df["1000Gp1_AFR_AC"],
                "afr_af": df["1000Gp1_AFR_AF"],
                "eur_ac": df["1000Gp1_EUR_AC"],
                "eur_af": df["1000Gp1_EUR_AF"],
                "amr_ac": df["1000Gp1_AMR_AC"],
                "amr_af": df["1000Gp1_AMR_AF"],
                "asn_ac": df["1000Gp1_ASN_AC"],
                "asn_af": df["1000Gp1_ASN_AF"]
            },
            "esp6500": {
                "aa_af": df["ESP6500_AA_AF"],
                "ea_af": df["ESP6500_EA_AF "]
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
            "aric5606": {
                "aa_ac": df["ARIC5606_AA_AC"],
                "aa_af": df["ARIC5606_AA_AF"],
                "ea_ac": df["ARIC5606_EA_AC"],
                "ea_af": df["ARIC5606_EA_AF"]
            },
            "clinvar": {
                "rs": df["clinvar_rs"],
                "clinsig": list(map(int,[i for i in df["clinvar_clnsig"].split("|") if i != "."])),
                "trait": [i for i in df["clinvar_trait"].split("|") if i != "."],
                "golden_stars": list(map(int,[i for i in df["clinvar_golden_stars"].split("|") if i != "."]))
            }
        }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert_to_number(one_snp_json)), vals=[".", None]), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    index = next(db_nsfp)
    assert len(index) == VALID_COLUMN_NO, "Expecting %s columns, but got %s" % (VALID_COLUMN_NO, len(index))
    previous_row = None
    for row in db_nsfp:
        df = dict(zip(index, row))
        # use transpose matrix to have 1 row with N 187 columns
        current_row = _map_line_to_json(df, version=version)
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


def load_data_file(input_file, version):
    data = data_generator(input_file, version=version)
    for one_snp_json in data:
        yield one_snp_json


# load path and find files, pass to data_generator
def load_data(path_glob, version='hg19'):
    for input_file in sorted(glob.glob(path_glob)):
         for d in load_data_file(input_file, version):
             yield d