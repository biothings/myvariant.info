import csv
import glob
from utils.dataload import list_split, dict_sweep, unlist, value_convert


VALID_COLUMN_NO = 112

'''this parser is for dbNSFP v3.0 beta2 downloaded from
https://sites.google.com/site/jpopgen/dbNSFP'''
# convert one snp to json
def _map_line_to_json(fields, version = 'hg19'):
    # specific variable treatment
    chrom = fields[0]
    if chrom = 'M':
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
    if fields[69] == ".":
        siphy = "."
    else:
        freq = fields[69].split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}

    acc = fields[26].rstrip().rstrip(';').split(";")
    pos = fields[28].rstrip().rstrip(';').split(";")
    uniprot = map(dict, map(lambda t: zip(('acc', 'pos'), t), zip(acc, pos)))

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
            "interpro_domain": fields[111],
            "cds_strand": fields[12],
            "ancestral_allele": fields[16],
            "ensembl": {
                "geneid": fields[19],
                "transcriptid": fields[20]
            },
            "sift": {
                "score": fields[23],
                "converted_rankscore": fields[24],
                "pred": fields[25]
            },
            "polyphen2": {
                "hdiv": {
                    "score": fields[29],
                    "rankscore": fields[30],
                    "pred": fields[31]
                },
                "hvar": {
                    "score": fields[32],
                    "rankscore": fields[33],
                    "pred": fields[34]
                }
            },
            "lrt": {
                "score": fields[35],
                "converted_rankscore": fields[36],
                "pred": fields[37],
                "omega": fields[38]
            },
            "mutationtaster": {
                "score": fields[39],
                "converted_rankscore": fields[40],
                "pred": fields[41],
                "model": fields[42],
                "AAE": fields[43]
            },
            "mutationassessor": {
                "score": fields[46],
                "rankscore": fields[47],
                "pred": fields[48]
            },
            "fathmm": {
                "score": fields[49],
                "rankscore": fields[50],
                "pred": fields[51]
            },
            "provean": {
                "score": fields[52],
                "rankscore": fields[53],
                "pred": fields[54]
            },
            "metasvm": {
                "score": fields[55],
                "rankscore": fields[56],
                "pred": fields[57]
            },
            "lr": {
                "score": fields[58],
                "rankscore": fields[59],
                "pred": fields[60]
            },
            "reliability_index": fields[61],
            "gerp++": {
                "nr": fields[62],
                "rs": fields[63],
                "rs_rankscore": fields[64]
            },
            "phylop_7way": {
                "vertebrate": fields[65],
                "vertebrate_rankscore": fields[66]
            },
            "phastCons_7way": {
                "vertebrate": fields[67],
                "vertebrate_rankscore": fields[68]
            },
            "siphy_29way": {
                "pi": siphy,
                "logodds": fields[70],
                "logodds_rankscore": fields[71]
            },
            "1000gp1": {
                "ac": fields[72],
                "af": fields[73],
                "afr_ac": fields[74],
                "afr_af": fields[75],
                "eur_ac": fields[76],
                "eur_af": fields[77],
                "amr_ac": fields[78],
                "amr_af": fields[79],
                "eas_ac": fields[80],
                "eas_af": fields[81],
                "sas_ac": fields[82],
                "sas_af": fields[83]
            },
            "twinsuk": {
                "ac": fields[84],
                "af": fields[85]
            },
            "alspac": {
                "ac": fields[86],
                "af": fields[87]
            },
            "esp6500": {
                "aa_ac": fields[88],
                "aa_af": fields[89],
                "ea_ac": fields[90],
                "ea_af": fields[91]
            },
            "exac": {
                "ac": fields[92],
                "af": fields[93],
                "adj_ac": fields[94],
                "adj_af": fields[95],
                "afr_ac": fields[96],
                "afr_af": fields[97],
                "amr_ac": fields[98],
                "amr_af": fields[99],
                "eas_ac": fields[100],
                "eas_af": fields[101],
                "fin_ac": fields[102],
                "fin_af": fields[103],
                "nfe_ac": fields[104],
                "nfe_af": fields[105],
                "sas_ac": fields[106],
                "sas_af": fields[107]
            },
            "clinvar": {
                "rs": fields[108],
                "clinsig": fields[109],
                "trait": fields[110]
            }
        }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert(one_snp_json)), vals=["."]), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file, version = 'hg19'):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    db_nsfp.next()  # skip header
    previous_row = None
    for row in db_nsfp:
        assert len(row) == VALID_COLUMN_NO
        current_row = _map_line_to_json(row, version = 'hg19')
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
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print(input_file)
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json
