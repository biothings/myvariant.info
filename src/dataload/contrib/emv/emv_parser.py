# -*- coding: utf-8 -*-
#import os
import re
import glob
import csv
from itertools import imap, groupby, ifilter
import os
from utils.dataload import dict_sweep, value_convert, unlist, merge_duplicate_rows

## merge EMV file with genomic ID file
#def file_merge(emv_file, id_file):
#    os.system("cut -f3 genomic_id.txt > genomic_id3.txt")
#    os.system("paste -d"," genomic_id3.txt EmVClass.2014-3.csv > emv.csv")

VALID_COLUMN_NO = 11

        
# convert one snp to json
def _map_line_to_json(fields):
    vid = fields[0].split(":")
    chrom = re.search(r'[1-9]+', vid[0]).group()
    
    if chrom == '23':
        chrom = chrom.replace('23', 'X')
    HGVS = "chr%s:%s" % (chrom, vid[1])
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
                "variant_aka_list": fields[9].split(" | "),
                "clinvar_rcv": fields[10],
            }
        }

    return unlist(dict_sweep(value_convert(one_snp_json), vals=[""]))


# open file, parse, pass to json mapper
def data_generator(input_file):
    sorted = input_file.split(".")[0] 
    os.system("sort -t$'\t' -k1 -n %s > %s_sorted.csv" % (input_file, sorted))
    open_file = open("%s_sorted.csv" % (sorted))
    emv = csv.reader(open_file, delimiter=",")
    # Skip header
    emv.next()
    emv = ifilter(lambda x: x[0], emv)
    json_rows = imap(_map_line_to_json, emv)
    row_groups = (it for (key, it) in groupby(json_rows, lambda row: row["_id"]))
    return (merge_duplicate_rows(rg, "emv") for rg in row_groups )


# load path and find files, pass to data_generator
def load_data(path):
    for input_file in sorted(glob.glob(path)):
        print(input_file)
        data = data_generator(input_file)
        for one_snp_json in data:
            yield one_snp_json
            
