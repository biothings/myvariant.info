# -*- coding: utf-8 -*-
import csv
import glob
from itertools import islice, groupby, imap
import pymongo
from utils.common import timesofar
import time


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
                #"grantham_score": fields[20],
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


def merge_duplicate_rows(rows):
    rows = list(rows)
    first_row = rows[0]
    other_rows = rows[1:]
    for row in other_rows:
        for i in first_row["evs"]:
            if row['evs'][i]:
                if row["evs"][i] != first_row["evs"][i]:
                    aa = first_row["evs"][i]
                    if not isinstance(aa, list):
                        aa = [aa]
                    aa.append(row["evs"][i])
                    first_row["evs"][i] = aa             
    return first_row


# open file, parse, pass to json mapper
def data_generator(input_file):
    with open(input_file) as open_file:
        evs = csv.reader(open_file, delimiter=" ")
        # Skip first 8 meta lines
        evs = islice(evs, 8, None)
        json_rows = imap(_map_line_to_json, evs)
        row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
        for one_snp_json in imap(merge_duplicate_rows, row_groups):
            yield one_snp_json
        
            
# load path and find files, pass to data_generator
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print input_file
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json
    

def load_collection(database, input_file_list, collection_name):
    """
    : param database: mongodb url
    : param input_file_list: variant docs, path to file
    : param collection_name: annotation source name
    """
    conn = pymongo.MongoClient(database)
    db = conn.variantdoc
    posts = db[collection_name]
    t1 = time.time()
    cnt = 0
    for doc in load_data(input_file_list):
        posts.insert(doc, manipulate=False, check_keys=False, w=0)
        cnt += 1
        if cnt % 100000 == 0:
            print cnt, timesofar(t1)
    print "successfully loaded %s into mongodb" % collection_name

#load_collection('mongodb://myvariant_user:Qag1H6V%0vEG@localhost:27017/variantdoc', 
#                    '/opt/myvariant.info/load_archive/evs/ESP6500SI-V2-SSA137.GRCh38-liftover.chr*', 'evs')
load_collection('mongodb://myvariant_user:Qag1H6V%0vEG@su08.scripps.edu:27017/variantdoc',
    '/Users/Amark/Documents/Su_Lab/myvariant.info/evs/evs.txt/ESP6500SI-V2-SSA137.GRCh38-liftover.chr1.*',#ESP6500SI-V2-SSA137.GRCh38-liftover.chr*',
    'evs')