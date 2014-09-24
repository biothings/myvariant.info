# -*- coding: utf-8 -*-
import csv
import glob


VALID_COLUMN_NO = 98


# split ";" separated fields into comma separated lists, strip.
def list_split(d):
    for key, val in d.items():
        if isinstance(val, dict):
            list_split(val)
        try:
            if len(val.split(";")) > 1:
                d[key] = val.rstrip().rstrip(';').split(";")
        except (AttributeError):
            pass
    return d


# remove keys whos values are "."
# and remove empty dictionaries
def dict_sweep(d):
    for key, val in d.items():
        if val == ".":
            del d[key]
        elif isinstance(val, list):
            d[key] = [dict_sweep(item) for item in val if isinstance(item, dict)]
            if len(val) == 0:
                del d[key]
        elif isinstance(val, dict):
            dict_sweep(val)
            if len(val) == 0:
                del d[key]
    return d


# convert string numbers into integers or floats
def value_convert(d):
    for key, val in d.items():
        try:
            d[key] = int(val)
        except (ValueError, TypeError):
            try:
                d[key] = float(val)
            except (ValueError, TypeError):
                pass
        if isinstance(val, dict):
            value_convert(val)
        elif isinstance(val, list):
            try:
                d[key] = [int(x) for x in val]
            except (ValueError, TypeError):
                try:
                    d[key] = [float(x) for x in val]
                except (ValueError, TypeError):
                    pass
    return d


# if dict value is a list of length 1, unlist
def unlist(d):
    for key, val in d.items():
            if isinstance(val, list):
                if len(val) == 1:
                    d[key] = val[0]
            elif isinstance(val, dict):
                unlist(val)
    return d


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
    allele1 = fields[2]
    allele2 = fields[3]
    HGVS = "chr%s:g.%d%s>%s" % (chrom, chromStart, allele1, allele2)

    if fields[74] == ".":
        siphy = "."
    else:
        freq = fields[74].split(":")
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
                "cadd":
                    {
                        "raw": fields[56],
                        "raw_rankscore": fields[57],
                        "phred": fields[58]
                    },
                "gerp++":
                    {
                        "nr": fields[59],
                        "rs": fields[60],
                        "rs_rankscore": fields[61]
                    },
                "phylop":
                    {
                        "46way": 
                            {
                                "primate": fields[62],
                                "primate_rankscore": fields[63],
                                "placental": fields[64],
                                "placental_rankscore": fields[65],
                            },
                        "100way":
                            {
                                "vertebrate": fields[66],
                                "vertebrate_rankscore": fields[67]
                            }
                    },
                "phastcons":
                    {
                        "46way": 
                            {
                                "primate": fields[68],
                                "primate_rankscore": fields[69],
                                "placental": fields[70],
                                "placental_rankscore": fields[71],
                            },
                        "100way":
                            {
                                "vertebrate": fields[72],
                                "vertebrate_rankscore": fields[73]
                            }
                    },
                "siphy_29way":
                    {
                        "pi": siphy,
                        "logodds": fields[75],
                        "logodds_rankscore": fields[76]
                    },
                "lrt_omega": fields[77],
                "unisnp_ids": fields[78],
                "1000gp1":
                    {
                        "ac": fields[79],
                        "af": fields[80],
                        "afr_ac": fields[81],
                        "afr_af": fields[82],
                        "eur_ac": fields[83],
                        "eur_af": fields[84],
                        "amr_ac": fields[85],
                        "amr_af": fields[86],
                        "asn_ac": fields[87],
                        "asn_af": fields[88]
                    },
                "esp6500":
                    {
                        "aa_af": fields[89],
                        "ea_af": fields[90]
                    },
                "aric5606":
                    {
                        "aa_ac": fields[91],
                        "aa_af": fields[92],
                        "ea_ac": fields[93],
                        "ea_af": fields[94]
                    },
                "clinvar":
                    {
                        "rs": fields[95],
                        "clin_sig": fields[96],
                        "trait": fields[97]
                    }
            }
    }

    one_snp_json = list_split(dict_sweep(unlist(value_convert(one_snp_json))))
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

i = load_data("/Users/Amark/Documents/Su_Lab/myvariant.info/dbnsfpv2/dbNSFPv2.7/chr4.tsv")
out = list(i)