# -*- coding: utf-8 -*-
import csv
import glob
from itertools import islice


VALID_COLUMN_NO = 31


# remove keys whos values are "."
# and remove empty dictionaries
def dict_sweep(d):
    for key, val in d.items():
        if val == "NA" or \
           val == "none":
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
    return d


def polyphen(field):
    if field.find(":") == 0:
        return field.split(":")
    else:
        return field

def count_dict(field):
    count_list = field.split("/")
    counts = dict(item.split("=") for item in count_list)
    return counts
    
    
# convert one snp to json
def _map_line_to_json(fields):
    chrInfo = fields[0].split(":")  # grch37
    chrom = chrInfo[0]
    chromStart = int(chrInfo[1])

    ma_fin_percent = fields[7].split("/")

    if fields[3]:
        HGVS = "chr%s:g.%d%s" % (chrom, chromStart, fields[3])

    # load as json data
    if HGVS is None:
        return

    one_snp_json = {

        "_id": HGVS,
        "evs":
            {
                "grch37":
                    {
                        "chr": fields[0].split(":")[0],
                        "pos": fields[0].split(":")[1]
                    },
                "grch38":
                    {
                        "chr": fields[30].split(":")[0],
                        "pos": fields[30].split(":")[1]
                    },
                "rs_id": fields[1],
                "db_snp_version": fields[2],
                "allele1": fields[3].split(">")[0],
                "allele2": fields[3].split(">")[1],
                "allele_count":
                    {
                        "european_american": count_dict(fields[4]),
                        "african_american": count_dict(fields[5]),
                        "all": count_dict(fields[6])
                    },
                "ma_fin_percent":
                    {
                        "european_american": ma_fin_percent[0],
                        "african_american": ma_fin_percent[1],
                        "all": ma_fin_percent[2]
                    },
                "genotype_count":
                    {
                        "european_american": count_dict(fields[8]),
                        "african_american": count_dict(fields[9]),
                        "all_genotype": count_dict(fields[10])
                    },
                "avg_sample_read": fields[11],
                "gene":
                    {
                        "id": fields[12],
                        "accession": fields[13]
                    },
                "function_gvs": fields[14],
                "hgvs":
                    {
                        "coding": fields[16],
                        "protein": fields[15]
                    },
                "coding_dna_size": fields[17],
                "conservation":
                    {
                        "phast_cons": fields[18],
                        "gerp": fields[19]
                    },
                "grantham_score": fields[20],
                "polyphen2":
                    {
                        "class": polyphen(fields[21])[0],
                        "score": polyphen(fields[21])[1]
                    },
                "ref_base_ncbi": fields[22],
                "chimp_allele": fields[23],
                "clinical_info": fields[24],
                "filter_status": fields[25],
                "on_illumina_human_exome_chip": fields[26],
                "gwas_pubmed_info": fields[27],
                "estimated_age_kyrs":
                    {
                        "ea": fields[28],
                        "aa": fields[29]
                    }
            }
        }

    return dict_sweep(value_convert(one_snp_json))


# open file, parse, pass to json mapper
def data_generator(input_file):
    open_file = open(input_file)
    evs = csv.reader(open_file, delimiter=" ")
    for row in islice(evs, 8, None):  # skip meta lines
        assert len(row) == VALID_COLUMN_NO
        if row[30] == "":
            continue  # skip variant
        one_snp_json = _map_line_to_json(row)
        if one_snp_json:
            yield one_snp_json
    open_file.close()


# load path and find files, pass to data_generator
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print input_file
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json