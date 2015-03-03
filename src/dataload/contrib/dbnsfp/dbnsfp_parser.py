# -*- coding: utf-8 -*-
import csv
import glob
from utils.dataload import list_split, dict_sweep, unlist, value_convert


VALID_COLUMN_NO = 119


# convert one snp to json
def _map_line_to_json(fields):
    # specific variable treatment
    chrom = fields[0]
    if fields[7] == ".":
        hg18_end = "."
    else:
        hg18_end = int(fields[7])+1
    chromStart = int(fields[1])
    chromEnd = int(fields[1]) + 1
    allele1 = fields[2].upper()
    allele2 = fields[3].upper()
    HGVS = "chr%s:g.%d%s>%s" % (chrom, chromStart, allele1, allele2)

    if fields[77] == ".":
        siphy = "."
    else:
        freq = fields[77].split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}

    acc = fields[11].rstrip().rstrip(';').split(";")
    pos = fields[13].rstrip().rstrip(';').split(";")
    uniprot = map(dict, map(lambda t: zip(('acc', 'pos'), t), zip(acc, pos)))

    # load as json data
    one_snp_json = {

        "_id": HGVS,
        "dbnsfp":
            {
                "chrom": chrom,
                "hg19":
                    {
                        "start": fields[1],
                        "end": chromEnd
                    },
                "hg18":
                    {
                        "start": fields[7],
                        "end": hg18_end
                    },
                "hg38":
                    {
                        "chrom": fields[8],
                        "pos": fields[9]                    
                    },
                "allele1": allele1,
                "allele2": allele2,
                "aa":
                    {
                        "ref": fields[4],
                        "alt": fields[5],
                        "pos": fields[23],
                        "refcodon": fields[16],
                        "codonpos": fields[18],
                        "aapos_sift": fields[24],
                        "aapos_fathmm": fields[25]
                    },
                "genename": fields[10],
                "uniprot": uniprot,
                "interpro_domain": fields[14],
                "cds_strand": fields[15],
                "slr_test_statistic": fields[17],
                "fold-degenerate": fields[19],
                "ancestral_allele": fields[20],
                "ensembl":
                    {
                        "geneid": fields[21],
                        "transcriptid": fields[22]
                    },
                "sift":
                    {
                        "score": fields[26],
                        "converted_rankscore": fields[27],
                        "pred": fields[28]
                    },
                "polyphen2":
                    {
                        "hdiv":
                        {
                            "score": fields[29],
                            "rankscore": fields[30],
                            "pred": fields[31]
                        },
                        "hvar":
                        {
                            "score": fields[32],
                            "rankscore": fields[33],
                            "pred": fields[34]
                        }
                    },
                "lrt":
                    {
                        "score": fields[35],
                        "converted_rankscore": fields[36],
                        "pred": fields[37]
                    },
                "mutationtaster":
                    {
                        "score": fields[38],
                        "converted_rankscore": fields[39],
                        "pred": fields[40]
                    },
                "mutationassessor":
                    {
                        "score": fields[41],
                        "rankscore": fields[42],
                        "pred": fields[43]
                    },
                "fathmm":
                    {
                        "score": fields[44],
                        "rankscore": fields[45],
                        "pred": fields[46]
                    },
                "radialsvm":
                    {
                        "score": fields[47],
                        "rankscore": fields[48],
                        "pred": fields[49]
                    },
                "lr":
                    {
                        "score": fields[50],
                        "rankscore": fields[51],
                        "pred": fields[52]
                    },
                "reliability_index": fields[53],
                "vest3":
                    {
                        "score": fields[54],
                        "rankscore": fields[55]
                    },
                "provean": 
                    {
                        "score": fields[56],
                        "converted_rankscore": fields[57],
                        "pred": fields[58]
                    },
                "cadd":
                    {
                        "raw": fields[59],
                        "raw_rankscore": fields[60],
                        "phred": fields[61]
                    },
                "gerp++":
                    {
                        "nr": fields[62],
                        "rs": fields[63],
                        "rs_rankscore": fields[64]
                    },
                "phylop":
                    {
                        "46way": 
                            {
                                "primate": fields[65],
                                "primate_rankscore": fields[66],
                                "placental": fields[67],
                                "placental_rankscore": fields[68],
                            },
                        "100way":
                            {
                                "vertebrate": fields[69],
                                "vertebrate_rankscore": fields[70]
                            }
                    },
                "phastcons":
                    {
                        "46way": 
                            {
                                "primate": fields[71],
                                "primate_rankscore": fields[72],
                                "placental": fields[73],
                                "placental_rankscore": fields[74],
                            },
                        "100way":
                            {
                                "vertebrate": fields[75],
                                "vertebrate_rankscore": fields[76]
                            }
                    },
                "siphy_29way":
                    {
                        "pi": siphy,
                        "logodds": fields[78],
                        "logodds_rankscore": fields[79]
                    },
                "lrt_omega": fields[80],
                "unisnp_ids": fields[81],
                "1000gp1":
                    {
                        "ac": fields[82],
                        "af": fields[83],
                        "afr_ac": fields[84],
                        "afr_af": fields[85],
                        "eur_ac": fields[86],
                        "eur_af": fields[87],
                        "amr_ac": fields[88],
                        "amr_af": fields[89],
                        "asn_ac": fields[90],
                        "asn_af": fields[91]
                    },
                "esp6500":
                    {
                        "aa_af": fields[92],
                        "ea_af": fields[93]
                    },
                "aric5606":
                    {
                        "aa_ac": fields[94],
                        "aa_af": fields[95],
                        "ea_ac": fields[96],
                        "ea_af": fields[97]
                    },
                "exac":
                    {
                        "ac": fields[98],
                        "af": fields[99],
                        "adj_ac": fields[100],
                        "adj_af": fields[101],
                        "afr_ac": fields[102],
                        "afr_af": fields[103],
                        "amr_ac": fields[104],
                        "amr_af": fields[105],
                        "eas_ac": fields[106],
                        "eas_af": fields[107],
                        "fin_ac": fields[108],
                        "fin_af": fields[109],
                        "nfe_ac": fields[110],
                        "nfe_af": fields[111],
                        "sas_ac": fields[112],
                        "sas_af": fields[113]
                        
                    },
                "clinvar":
                    {
                        "rs": fields[114],
                        "clin_sig": fields[115],
                        "trait": fields[116]
                    }
            }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert(one_snp_json)), vals=["."]), ";")
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"])
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    db_nsfp.next()  # skip header
    previous_row = None
    for row in db_nsfp:
        assert len(row) == VALID_COLUMN_NO
        current_row = _map_line_to_json(row)
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
        print input_file
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json

