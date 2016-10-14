import os
import csv
import glob
from biothings.utils.dataload import list_split, dict_sweep, unlist, value_convert_to_number


VALID_COLUMN_NO = 183

'''this parser is for dbNSFP v3.0 beta2 downloaded from
https://sites.google.com/site/jpopgen/dbNSFP'''


# convert one snp to json
def _map_line_to_json(fields, version):
    # specific variable treatment
    chrom = fields[0]
    if chrom == 'M':
        chrom = 'MT'
    # fields[7] in version 2, represent hg18_pos
    if fields[10] == ".":
        hg18_end = "."
    else:
        hg18_end = int(fields[10])
    # in case of no hg19 position provided, remove the item
    if fields[8] == '.':
        return None
    else:
        chromStart = int(fields[8])
        chromEnd = int(fields[8])
    chromStart_38 = int(fields[1])
    ref = fields[2].upper()
    alt = fields[3].upper()
    HGVS_19 = "chr%s:g.%d%s>%s" % (chrom, chromStart, ref, alt)
    HGVS_38 = "chr%s:g.%d%s>%s" % (chrom, chromStart_38, ref, alt)
    if version == 'hg19':
        HGVS = HGVS_19
    elif version == 'hg38':
        HGVS = HGVS_38
    if fields[105] == ".":
        siphy = "."
    else:
        freq = fields[105].split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}
    gtex_gene = fields[181].split('|')
    gtex_tissue = fields[182].split('|')
    gtex = list(map(dict, map(lambda t: zip(('gene', 'tissue'), t), zip(gtex_gene, gtex_tissue))))
    acc = fields[26].rstrip().rstrip(';').split(";")
    pos = fields[28].rstrip().rstrip(';').split(";")
    uniprot = list(map(dict, map(lambda t: zip(('acc', 'pos'), t), zip(acc, pos))))
    provean_score = fields[52].split(';')
    sift_score = fields[23].split(';')
    hdiv_score = fields[29].split(';')
    hvar_score = fields[32].split(';')
    lrt_score = fields[35].split(';')
    dann_score = fields[69].split(';')
    mutationtaster_score = fields[39].split(';')
    mutationassessor_score = fields[46].split(';')
    vest3_score = fields[57].split(';')
    metasvm_score = fields[59].split(';')
    fathmm_score = fields[49].split(';')
    lr_score = fields[62].split(';')
    fathmm_coding_score = fields[71].split(';')
    integrated_fitcons_score = fields[82].split(';')
    gm12878_fitcons_score = fields[85].split(';')
    h1_hesc_fitcons_score = fields[88].split(';')
    huvec_fitcons_score = fields[91].split(';')
    if len(provean_score) > 1:
        for i in range(len(provean_score)):
            if provean_score[i] == '.':
                provean_score[i] = None
    if len(sift_score) > 1:
        for i in range(len(sift_score)):
            if sift_score[i] == '.':
                sift_score[i] = None
    if len(hdiv_score) > 1:
        for i in range(len(hdiv_score)):
            if hdiv_score[i] == '.':
                hdiv_score[i] = None
    if len(hvar_score) > 1:
        for i in range(len(hvar_score)):
            if hvar_score[i] == '.':
                hvar_score[i] = None
    if len(lrt_score) > 1:
        for i in range(len(lrt_score)):
            if lrt_score[i] == '.':
                lrt_score[i] = None
    if len(mutationtaster_score) > 1:
        for i in range(len(mutationtaster_score)):
            if mutationtaster_score[i] == '.':
                mutationtaster_score[i] = None
    if len(mutationassessor_score) > 1:
        for i in range(len(mutationassessor_score)):
            if mutationassessor_score[i] == '.':
                mutationassessor_score[i] = None
    if len(metasvm_score) > 1:
        for i in range(len(metasvm_score)):
            if metasvm_score[i] == '.':
                metasvm_score[i] = None
    if len(vest3_score) > 1:
        for i in range(len(vest3_score)):
            if vest3_score[i] == '.':
                vest3_score[i] = None
    if len(fathmm_score) > 1:
        for i in range(len(fathmm_score)):
            if fathmm_score[i] == '.':
                fathmm_score[i] = None
    if len(lr_score) > 1:
        for i in range(len(lr_score)):
            if lr_score[i] == '.':
                lr_score[i] = None
    if len(fathmm_coding_score) > 1:
        for i in range(len(fathmm_coding_score)):
            if fathmm_coding_score[i] == '.':
                fathmm_coding_score[i] = None
    if len(dann_score) > 1:
        for i in range(len(dann_score)):
            if dann_score[i] == '.':
                dann_score[i] = None
    if len(integrated_fitcons_score) > 1:
        for i in range(len(integrated_fitcons_score)):
            if integrated_fitcons_score[i] == '.':
                integrated_fitcons_score[i] = None
    if len(gm12878_fitcons_score) > 1:
        for i in range(len(gm12878_fitcons_score)):
            if gm12878_fitcons_score[i] == '.':
                gm12878_fitcons_score[i] = None
    if len(h1_hesc_fitcons_score) > 1:
        for i in range(len(h1_hesc_fitcons_score)):
            if h1_hesc_fitcons_score[i] == '.':
                h1_hesc_fitcons_score[i] = None
    if len(huvec_fitcons_score) > 1:
        for i in range(len(huvec_fitcons_score)):
            if huvec_fitcons_score[i] == '.':
                huvec_fitcons_score[i] = None
# load as json data
    one_snp_json = {
        "_id": HGVS,
        "dbnsfp": {
            "rsid": fields[6],
            #"rsid_dbSNP144": fields[6],
            "chrom": chrom,
            "hg19": {
                "start": chromStart,
                "end": chromEnd
            },
            "hg18": {
                "start": fields[10],
                "end": hg18_end
            },
            "hg38": {
                "start": fields[1],
                "end": fields[1]
            },
            "ref": ref,
            "alt": alt,
            "aa": {
                "ref": fields[4],
                "alt": fields[5],
                "pos": fields[22],
                "refcodon": fields[13],
                "codonpos": fields[14],
                "codon_degeneracy": fields[15]
            },
            "genename": fields[11],
            "uniprot": uniprot,
            "interpro_domain": fields[180],
            "cds_strand": fields[12],
            "ancestral_allele": fields[16],
            #"altaineandertal": fields[17],
            #"denisova": fields[18]
            "ensembl": {
                "geneid": fields[19],
                "transcriptid": fields[20],
                "proteinid": fields[21]
            },
            "sift": {
                "score": sift_score,
                "converted_rankscore": fields[24],
                "pred": fields[25]
            },
            "polyphen2": {
                "hdiv": {
                    "score": hdiv_score,
                    "rankscore": fields[30],
                    "pred": fields[31]
                },
                "hvar": {
                    "score": hvar_score,
                    "rankscore": fields[33],
                    "pred": fields[34]
                }
            },
            "lrt": {
                "score": lrt_score,
                "converted_rankscore": fields[36],
                "pred": fields[37],
                "omega": fields[38]
            },
            "mutationtaster": {
                "score": mutationtaster_score,
                "converted_rankscore": fields[40],
                "pred": fields[41],
                "model": fields[42],
                "AAE": fields[43]
            },
            "mutationassessor": {
                "score": mutationassessor_score,
                "rankscore": fields[47],
                "pred": fields[48]
            },
            "fathmm": {
                "score": fathmm_score,
                "rankscore": fields[50],
                "pred": fields[51]
            },
            "provean": {
                "score": provean_score,
                "rankscore": fields[53],
                "pred": fields[54]
            },
            "vest3": {
                "score": vest3_score,
                "rankscore": fields[57],
                "transcriptid": fields[55],
                "transcriptvar": fields[56]
            },
            "fathmm-mkl": {
                "coding_score": fathmm_coding_score,
                "coding_rankscore": fields[72],
                "coding_pred": fields[73],
                "coding_group": fields[74]
            },
            "eigen": {
                "raw": fields[75],
                "phred": fields[76],
                "raw_rankscore": fields[77]
            },
            "eigen-pc": {
                "raw": fields[78],
                "raw_rankscore": fields[79]
            },
            "genocanyon": {
                "score": fields[80],
                "rankscore": fields[81]
            },
            "metasvm": {
                "score": metasvm_score,
                "rankscore": fields[60],
                "pred": fields[61]
            },
            "metalr": {
                "score": lr_score,
                "rankscore": fields[63],
                "pred": fields[64]
            },
            "reliability_index": fields[65],
            "dann": {
                "score": dann_score,
                "rankscore": fields[70]
            },
            "gerp++": {
                "nr": fields[94],
                "rs": fields[95],
                "rs_rankscore": fields[96]
            },
            "integrated": {
                "fitcons_score": integrated_fitcons_score,
                "fitcons_rankscore": fields[83],
                "confidence_value": fields[84]
            },
            "gm12878": {
                "fitcons_score": gm12878_fitcons_score,
                "fitcons_rankscore": fields[86],
                "confidence_value": fields[87]
            },
            "h1-hesc": {
                "fitcons_score": h1_hesc_fitcons_score,
                "fitcons_rankscore": fields[89],
                "confidence_value": fields[90]
            },
            "huvec": {
                "fitcons_score": huvec_fitcons_score,
                "fitcons_rankscore": fields[92],
                "confidence_value": fields[93]
            },
            "phylo": {
                "p100way": {
                    "vertebrate": fields[97],
                    "vertebrate_rankscore": fields[98]
                },
                "p20way": {
                    "mammalian": fields[99],
                    "mammalian_rankscore": fields[100]
                }
            },
            "phastcons": {
                "100way": {
                    "vertebrate": fields[101],
                    "vertebrate_rankscore": fields[102]
                },
                "20way": {
                    "mammalian": fields[103],
                    "mammalian_rankscore": fields[104]
                }
            },
            "siphy_29way": {
                "pi": siphy,
                "logodds": fields[106],
                "logodds_rankscore": fields[107]
            },
            "1000gp3": {
                "ac": fields[108],
                "af": fields[109],
                "afr_ac": fields[110],
                "afr_af": fields[111],
                "eur_ac": fields[112],
                "eur_af": fields[113],
                "amr_ac": fields[114],
                "amr_af": fields[115],
                "eas_ac": fields[116],
                "eas_af": fields[117],
                "sas_ac": fields[118],
                "sas_af": fields[119]
            },
            "twinsuk": {
                "ac": fields[120],
                "af": fields[121]
            },
            "alspac": {
                "ac": fields[122],
                "af": fields[123]
            },
            "esp6500": {
                "aa_ac": fields[124],
                "aa_af": fields[125],
                "ea_ac": fields[126],
                "ea_af": fields[127]
            },
            "exac": {
                "ac": fields[128],
                "af": fields[129],
                "adj_ac": fields[130],
                "adj_af": fields[131],
                "afr_ac": fields[132],
                "afr_af": fields[133],
                "amr_ac": fields[134],
                "amr_af": fields[135],
                "eas_ac": fields[136],
                "eas_af": fields[137],
                "fin_ac": fields[138],
                "fin_af": fields[139],
                "nfe_ac": fields[140],
                "nfe_af": fields[141],
                "sas_ac": fields[142],
                "sas_af": fields[143]
            },
            "exac_nontcga": {
                "ac": fields[144],
                "af": fields[145],
                "adj_ac": fields[146],
                "adj_af": fields[147],
                "afr_ac": fields[148],
                "afr_af": fields[149],
                "amr_ac": fields[150],
                "amr_af": fields[151],
                "eas_ac": fields[152],
                "eas_af": fields[153],
                "fin_ac": fields[154],
                "fin_af": fields[155],
                "nfe_ac": fields[156],
                "nfe_af": fields[157],
                "sas_ac": fields[158],
                "sas_af": fields[159]
            },
            "exac_nonpsych": {
                "ac": fields[160],
                "af": fields[161],
                "adj_ac": fields[162],
                "adj_af": fields[163],
                "afr_ac": fields[164],
                "afr_af": fields[165],
                "amr_ac": fields[166],
                "amr_af": fields[167],
                "eas_ac": fields[168],
                "eas_af": fields[169],
                "fin_ac": fields[170],
                "fin_af": fields[171],
                "nfe_ac": fields[172],
                "nfe_af": fields[173]
            },
            "clinvar": {
                "rs": fields[176],
                "clinsig": fields[177],
                "trait": fields[178],
                "golden_stars": fields[179]
            },
            "gtex": gtex
        }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert_to_number(one_snp_json)), vals=["."]), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    next(db_nsfp)  # skip header
    previous_row = None
    for row in db_nsfp:
        assert len(row) == VALID_COLUMN_NO
        current_row = _map_line_to_json(row, version=version)
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
    open_file.close()


# load path and find files, pass to data_generator
def load_data(path_glob, version='hg19'):
    for input_file in sorted(glob.glob(path_glob)):
        print(input_file)
        data = data_generator(input_file, version=version)
        for one_snp_json in data:
            yield one_snp_json
