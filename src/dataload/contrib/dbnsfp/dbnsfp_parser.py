# -*- coding: utf-8 -*-
import csv
import glob


VALID_COLUMN_NO = 88


# split ";" separated fields into comma separated lists, strip.
def list_split(d):
    for key, val in d.items():
        try:
            if len(val.split(";")) > 1:
                d[key] = val.rstrip().rstrip(';').split(";")
        except (AttributeError):
            pass
        if isinstance(val, dict):
            list_split(val)
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
    if fields[6] == ".":
        hg18_end = "."
    else:
        hg18_end = int(fields[6])+1
    chromEnd = int(fields[1]) + 1
    allele1 = fields[2]
    allele2 = fields[3]
    HGVS = "chr%s:g.%d%s>%s" % (chrom, chromEnd, allele1, allele2)

    if fields[71] == ".":
        siphy = "."
    else:
        freq = fields[71].split(":")
        siphy = {'a': freq[0], 'c': freq[1], 'g': freq[2], 't': freq[3]}

    acc = fields[8].rstrip().rstrip(';').split(";")
    pos = fields[10].rstrip().rstrip(';').split(";")
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
                        "start": fields[6],
                        "end": hg18_end
                    },
                "allele1": allele1,
                "allele2": allele2,
                "aa":
                    {
                        "ref": fields[4],
                        "alt": fields[5]
                    },
                "genename": fields[7],
                "uniprot": uniprot,
                "interpro_domain": fields[11],
                "cds_strand": fields[12],
                "refcodon": fields[13],
                "slr_test_statistic": fields[14],
                "codonpos": fields[15],
                "fold-degenerate": fields[16],
                "ancestral_allele": fields[17],
                "ensembl":
                    {
                        "geneid": fields[18],
                        "transcriptid": fields[19]
                    },
                "aapos": fields[20],
                "aapos_sift": fields[21],
                "aapos_fathmm": fields[22],
                "sift":
                    {
                        "score": fields[23],
                        "converted_rankscore": fields[24],
                        "pred": fields[25]
                    },
                "polyphen2":
                    {
                        "hdiv":
                        {
                            "score": fields[26],
                            "rankscore": fields[27],
                            "pred": fields[28]
                        },
                        "hvar":
                        {
                            "score": fields[29],
                            "rankscore": fields[30],
                            "pred": fields[31]
                        }
                    },
                "lrt":
                    {
                        "score": fields[32],
                        "converted_rankscore": fields[33],
                        "pred": fields[34]
                    },
                "mutationtaster":
                    {
                        "score": fields[35],
                        "converted_rankscore": fields[36],
                        "pred": fields[37]
                    },
                "mutationassessor":
                    {
                        "score": fields[38],
                        "rankscore": fields[39],
                        "pred": fields[40]
                    },
                "fathmm":
                    {
                        "score": fields[41],
                        "rankscore": fields[42],
                        "pred": fields[43]
                    },
                "radialsvm":
                    {
                        "score": fields[44],
                        "rankscore": fields[45],
                        "pred": fields[46]
                    },
                "lr":
                    {
                        "score": fields[47],
                        "rankscore": fields[48],
                        "pred": fields[49]
                    },
                "reliability_index": fields[50],
                "vest3":
                    {
                        "score": fields[51],
                        "rankscore": fields[52]
                    },
                "cadd":
                    {
                        "raw": fields[53],
                        "raw_rankscore": fields[54],
                        "phred": fields[55]
                    },
                "gerp++":
                    {
                        "nr": fields[56],
                        "rs": fields[57],
                        "rs_rankscore": fields[58]
                    },
                "phylop46way":
                    {
                        "primate": fields[59],
                        "primate_rankscore": fields[60],
                        "placental": fields[61],
                        "placental_rankscore": fields[62],
                        "vertebrate": fields[63],
                        "vertebrate_rankscore": fields[64]
                    },
                "phastcons46way":
                    {
                        "primate": fields[65],
                        "primate_rankscore": fields[66],
                        "placental": fields[67],
                        "placental_rankscore": fields[68],
                        "vertebrate": fields[69],
                        "vertebrate_rankscore": fields[70]
                    },
                "siphy_29way_pi": siphy,
                "siphy_29way_pi_logodds": fields[72],
                "siphy_29way_pi_logodds_rankscore": fields[73],
                "lrt_omega": fields[74],
                "unisnp_ids": fields[75],
                "1000gp1":
                    {
                        "ac": fields[76],
                        "af": fields[77],
                        "afr_ac": fields[78],
                        "afr_af": fields[79],
                        "eur_ac": fields[80],
                        "eur_af": fields[81],
                        "amr_ac": fields[82],
                        "amr_af": fields[83],
                        "asn_ac": fields[84],
                        "asn_af": fields[85]
                    },
                "esp6500":
                    {
                        "aa_af": fields[86],
                        "ea_af": fields[87]
                    }
            }
    }

    one_snp_json = dict_sweep(unlist(value_convert(list_split(one_snp_json))))
    one_snp_json["dbnsfp"]["chrom"] = str(one_snp_json["dbnsfp"]["chrom"]) 
    return one_snp_json


# open file, parse, pass to json mapper
def data_generator(input_file):
    open_file = open(input_file)
    db_nsfp = csv.reader(open_file, delimiter="\t")
    db_nsfp.next()  # skip header
    for row in db_nsfp:
        assert len(row) == VALID_COLUMN_NO
        one_snp_json = _map_line_to_json(row)
        yield one_snp_json
    open_file.close()


# load path and find files, pass to data_generator
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print input_file
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json

