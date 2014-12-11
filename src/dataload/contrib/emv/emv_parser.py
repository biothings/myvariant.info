# -*- coding: utf-8 -*-
#import os
import re
import glob
import csv
from itertools import imap, groupby
import os
from utils.dataload import dict_sweep, value_convert, merge_duplicate_rows

## merge EMV file with genomic ID file
#def file_merge(emv_file, id_file):
#    os.system("cut -f3 genomic_id.txt > genomic_id3.txt")
#    os.system("paste -d"," genomic_id3.txt EmVClass.2014-3.csv > emv.csv")

VALID_COLUMN_NO = 11

    
def id_strip(id_list):
    id_list = id_list.split("|")
    ids = []
    for id in id_list:
        ids.append(id.rstrip().lstrip())
    return ids
        
# convert one snp to json
def _map_line_to_json(fields):
    id = fields[0].split(":")
    HGVS = "chr%s:%s" % (re.search(r'[1-9]+', id[0]).group(), id[1])
        
    # load as json data
    if HGVS is None:
        return

    one_snp_json = {

        "_id": HGVS,
        "emv":
            {
                "gene": fields[2],
                "variant_id": fields[3],
                "exon": fields[4],
                "egl_variant": fields[5],
                "egl_protein": fields[6],
                "egl_classification": fields[7],
                "egl_classification_date": fields[8],
                "variant_aka_list": id_strip(fields[9]),
                "clinvar_rcv": fields[10],
            }
        }

    return dict_sweep(value_convert(one_snp_json), "")


# open file, parse, pass to json mapper
def data_generator(input_file):
    #with open(input_file) as open_file:
    os.system("sort -t$'\t' -k1 -n %s > %s_sorted.csv" % (input_file, input_file))
    open_file = open("%s_sorted.csv" % (input_file))
    emv = csv.reader(open_file, delimiter=",")
    open_file.close()
    # Skip header
    emv.next()
    emv = (row for row in emv if row[0])
    json_rows = imap(_map_line_to_json, emv)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    return (one_snp_json for one_snp_json in merge_duplicate_rows(row_groups, "emv"))


# load path and find files, pass to data_generator
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print input_file
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json
