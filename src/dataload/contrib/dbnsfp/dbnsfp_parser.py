import csv
import glob
from utils.dataload import list_split, dict_sweep, unlist, value_convert


VALID_COLUMN_NO = 132

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
    if fields[89] == ".":
        siphy = "."
    else:
        freq = fields[89].split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}

    acc = fields[26].rstrip().rstrip(';').split(";")
    pos = fields[28].rstrip().rstrip(';').split(";")
    uniprot = map(dict, map(lambda t: zip(('acc', 'pos'), t), zip(acc, pos)))
    provean_score = fields[52].split(';')
    sift_score = fields[23].split(';')
    hdiv_score = fields[29].split(';')
    hvar_score = fields[32].split(';')
    lrt_score = fields[35].split(';')
    mutationtaster_score = fields[39].split(';')
    mutationassessor_score = fields[46].split(';')
    metasvm_score = fields[59].split(';')
    fathmm_score = fields[49].split(';')
    lr_score = fields[62].split(';')
    fathmm_coding_score = fields[55].split(';')
    integrated_fitcons_score = fields[66].split(';')
    gm12878_fitcons_score = fields[69].split(';')
    h1_hesc_fitcons_score = fields[72].split(';')
    huvec_fitcons_score = fields[75].split(';')
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
            "chrom": chrom,
            "hg19": {
                "start": fields[8],
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
            },
            "genename": fields[11],
            "uniprot": uniprot,
            "interpro_domain": fields[131],
            "cds_strand": fields[12],
            "ancestral_allele": fields[16],
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
            "fathmm-mkl": {
                "coding_score": fathmm_coding_score,
                "coding_rankscore": fields[56],
                "coding_pred": fields[57],
                "coding_group": fields[58]
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
            "gerp++": {
                "nr": fields[78],
                "rs": fields[79],
                "rs_rankscore": fields[80]
            },
            "integrated": {
                "fitcons_score": integrated_fitcons_score,
                "fitcons_rankscore": fields[67],
                "confidence_value": fields[68]
            },
            "gm12878": {
                "fitcons_score": gm12878_fitcons_score,
                "fitcons_rankscore": fields[70],
                "confidence_value": fields[71]
            },
            "h1-hesc": {
                "fitcons_score": h1_hesc_fitcons_score,
                "fitcons_rankscore": fields[73],
                "confidence_value": fields[74]
            },
            "huvec": {
                "fitcons_score": huvec_fitcons_score,
                "fitcons_rankscore": fields[76],
                "confidence_value": fields[77]
            },
            "phylo": {
                "p7way": {
                    "vertebrate": fields[81],
                    "vertebrate_rankscore": fields[82]
                },
                "p20way": {
                    "mammalian": fields[83],
                    "mammalian_rankscore": fields[84]
                }
            },
            "phastcons": {
                "7way": {
                    "vertebrate": fields[85],
                    "vertebrate_rankscore": fields[86]
                },
                "20way": {
                    "mammalian": fields[87],
                    "mammalian_rankscore": fields[88]
                }
            },
            "siphy_29way": {
                "pi": siphy,
                "logodds": fields[90],
                "logodds_rankscore": fields[91]
            },
            "1000gp3": {
                "ac": fields[92],
                "af": fields[93],
                "afr_ac": fields[94],
                "afr_af": fields[95],
                "eur_ac": fields[96],
                "eur_af": fields[97],
                "amr_ac": fields[98],
                "amr_af": fields[99],
                "eas_ac": fields[100],
                "eas_af": fields[101],
                "sas_ac": fields[102],
                "sas_af": fields[103]
            },
            "twinsuk": {
                "ac": fields[104],
                "af": fields[105]
            },
            "alspac": {
                "ac": fields[106],
                "af": fields[107]
            },
            "esp6500": {
                "aa_ac": fields[108],
                "aa_af": fields[109],
                "ea_ac": fields[110],
                "ea_af": fields[111]
            },
            "exac": {
                "ac": fields[112],
                "af": fields[113],
                "adj_ac": fields[114],
                "adj_af": fields[115],
                "afr_ac": fields[116],
                "afr_af": fields[117],
                "amr_ac": fields[118],
                "amr_af": fields[119],
                "eas_ac": fields[120],
                "eas_af": fields[121],
                "fin_ac": fields[122],
                "fin_af": fields[123],
                "nfe_ac": fields[124],
                "nfe_af": fields[125],
                "sas_ac": fields[126],
                "sas_af": fields[127]
            },
            "clinvar": {
                "rs": fields[128],
                "clinsig": fields[129],
                "trait": fields[130]
            }
        }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert(one_snp_json)), vals=["."]), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    db_nsfp.next()  # skip header
    previous_row = None
    for row in db_nsfp:
        assert len(row) == VALID_COLUMN_NO
        current_row = _map_line_to_json(row, version=version)
        if previous_row:
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
def load_data(path, version='hg19'):
    for input_file in sorted(glob.glob(path)):
        print(input_file)
        data = data_generator(input_file, version=version)
        for one_snp_json in data:
            yield one_snp_json
